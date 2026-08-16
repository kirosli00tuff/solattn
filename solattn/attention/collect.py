"""Attention collectors: run every source that verified, filter at ingest, match.

The registered ingest filter is applied at the edge so firehose volume stays
sane (REGISTRATION.md 7); the registered matching rules are applied immediately
so ``ambiguous`` and ``unmatched`` are counted rather than discarded.

A source that did not verify is simply not started — reported and dropped, not
worked around silently.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from solattn import registry
from solattn.attention import filters, store
from solattn.attention.channels import load_channels
from solattn.clock import Clock, day_str, iso, parse_iso, utc_date
from solattn.config import Settings
from solattn.http import PacedClient
from solattn.ledger import Ledger, RequestCapError
from solattn.lifecycle import Lifecycle
from solattn.matching.rules import ActiveUniverse, match_message
from solattn.records import Mention
from solattn.sources import bluesky, farcaster, telegram
from solattn.universe import manifest


def build_active_universe(settings: Settings, clock: Clock) -> ActiveUniverse:
    """The active matching universe: births in the trailing registered window.

    Built from the birth manifests only — **never from any attention-ranked
    surface** (ADR-001).
    """
    now = clock.now()
    days = [
        day_str((now - timedelta(days=offset)).date())
        for offset in range(registry.ACTIVE_UNIVERSE_DAYS + 1)
    ]
    births = manifest.read_recent(settings.manifests_dir(), days)
    return ActiveUniverse.from_births(births).active_at(now)


def _record(
    settings: Settings,
    clock: Clock,
    universe: ActiveUniverse,
    source: str,
    channel: str,
    message_id: str,
    author_id: str,
    posted_at: datetime,
    text: str,
) -> str:
    """Filter, match, and store one message. Returns the match kind."""
    if not filters.apply(text).passed:
        return "filtered_out"
    decision = match_message(text, universe)
    mention = Mention(
        source=source,
        channel=channel,
        message_id=message_id,
        author_id=author_id,
        posted_at=iso(posted_at),
        match_kind=decision.kind,
        matched_mint=decision.mint,
        candidates=decision.candidates,
        conflict=decision.conflict,
        ingested_at=iso(clock.now()),
    )
    store.append_mention(settings.attention_dir(), day_str(utc_date(posted_at)), mention)
    return decision.kind


def collect_bluesky(
    settings: Settings, clock: Clock, universe: ActiveUniverse, seconds: float
) -> dict[str, int]:
    counts: dict[str, int] = {"events": 0, "stored": 0}

    def on_post(author_did: str, rkey: str, text: str) -> None:
        counts["events"] += 1
        kind = _record(
            settings,
            clock,
            universe,
            registry.SOURCE_BLUESKY,
            "jetstream",
            rkey,
            f"bsky:{author_did}",
            clock.now(),
            text,
        )
        if kind != "filtered_out":
            counts["stored"] += 1
            counts[kind] = counts.get(kind, 0) + 1

    for host in bluesky.JETSTREAM_HOSTS:
        try:
            asyncio.run(bluesky.consume(host, on_post, stop_after_s=seconds))
            return counts
        except Exception:
            continue
    return counts


def collect_farcaster(
    client: PacedClient, settings: Settings, clock: Clock, universe: ActiveUniverse, rounds: int
) -> dict[str, int]:
    counts: dict[str, int] = {"casts": 0, "stored": 0}
    live, _ = farcaster.find_live_hub(client, clock)
    if live is None:
        counts["hub"] = 0
        return counts
    cursors = farcaster.current_seeds(client, live.base)

    def on_cast(author: str, cast_hash: str, posted_at: datetime, text: str) -> None:
        counts["casts"] += 1
        kind = _record(
            settings,
            clock,
            universe,
            registry.SOURCE_FARCASTER,
            live.base,
            cast_hash,
            author,
            posted_at,
            text,
        )
        if kind != "filtered_out":
            counts["stored"] += 1
            counts[kind] = counts.get(kind, 0) + 1

    for _ in range(rounds):
        try:
            cursors = farcaster.poll_casts(client, live.base, tuple(cursors), cursors, on_cast)
        except RequestCapError:
            break
    return counts


def collect_telegram(
    settings: Settings, clock: Clock, universe: ActiveUniverse, per_channel: int
) -> dict[str, int]:
    """Read the fixed channel list. Inactive without a session or without a list."""
    counts: dict[str, int] = {"messages": 0, "stored": 0}
    channels = [c.username for c in load_channels()]
    if not settings.has_telegram:
        counts["inactive_reason_credential"] = 1
        return counts
    if not channels:
        counts["inactive_reason_no_fixed_channel_list"] = 1
        return counts
    if not telegram.session_exists(settings.telegram_session):
        counts["inactive_reason_no_session"] = 1
        return counts

    api_id, api_hash = settings.require_telegram()

    def on_message(
        channel: str, message_id: str, author_id: str, posted_at: str, text: str
    ) -> None:
        counts["messages"] += 1
        when = parse_iso(posted_at) if posted_at else clock.now()
        kind = _record(
            settings,
            clock,
            universe,
            registry.SOURCE_TELEGRAM,
            channel,
            message_id,
            author_id,
            when,
            text,
        )
        if kind != "filtered_out":
            counts["stored"] += 1
            counts[kind] = counts.get(kind, 0) + 1

    asyncio.run(
        telegram.consume(
            api_id, api_hash, settings.telegram_session, channels, on_message, per_channel
        )
    )
    return counts


def collect_all(clock: Clock, settings: Settings, seconds: float = 60.0) -> dict[str, Any]:
    """Run every verified collector for a bounded span."""
    life = Lifecycle(settings.state_dir() / "lifecycle.jsonl", "collect", clock)
    life.started(f"{seconds:.0f}s per firehose")
    universe = build_active_universe(settings, clock)
    ledger = Ledger(settings.vendor_dir() / "requests.jsonl", settings.daily_caps, clock)

    result: dict[str, Any] = {"active_universe": len(universe), "at": iso(clock.now())}
    with PacedClient(ledger) as client:
        result[registry.SOURCE_FARCASTER] = collect_farcaster(
            client, settings, clock, universe, rounds=max(1, int(seconds // 10))
        )
    result[registry.SOURCE_BLUESKY] = collect_bluesky(settings, clock, universe, seconds)
    result[registry.SOURCE_TELEGRAM] = collect_telegram(settings, clock, universe, 50)
    life.stopped("collect", **{k: str(v) for k, v in result.items()})
    return result
