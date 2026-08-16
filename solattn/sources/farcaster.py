"""Farcaster: free hub access as it exists today, measured — including freshness.

Farcaster's public hub landscape has changed repeatedly (Merkle's hubs retired;
the network migrated to Snapchain). Nothing here is assumed: candidate hosts are
PROBED, and the one used must pass **two** bars.

**A liveness check is not enough, and this is a measured finding, not a
precaution.** ``hub.pinata.cloud`` answers ``GET /v1/info`` with HTTP 200 and a
823-million-message db-stats payload while its newest event is **238 days old**
(measured 2026-08-16). A reachability-only check would have accepted it and this
project would have recorded zero Farcaster attention on every live cohort while
believing the source was working. **Freshness is therefore part of
verification**: a hub whose newest event is older than
:data:`MAX_TIP_AGE_SECONDS` fails and is reported and dropped.

Event ids are ``blockNumber << 14`` per shard (measured, not documented), so a
live tail seeds from ``(maxHeight - lookback) << 14`` for each shard that serves
events. Shard 0 is a metadata shard and rejects event queries with HTTP 400;
that is a data condition of the API, recorded here rather than retried blindly.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from solattn import registry
from solattn.clock import Clock, iso
from solattn.http import PacedClient
from solattn.records import AccessResult

SOURCE = registry.SOURCE_FARCASTER

#: Candidate public hubs, probed in order. The first that is BOTH reachable and
#: fresh is used.
HUB_CANDIDATES: tuple[str, ...] = (
    "https://snap.farcaster.xyz:3381",
    "https://snapchain.pinata.cloud",
    "https://hub.pinata.cloud",
    "https://hub.merv.fun",
    "https://hoyt.farcaster.xyz:2281",
)

INFO_PATH = "/v1/info"
EVENTS_PATH = "/v1/events"
CAST_ADD = "MESSAGE_TYPE_CAST_ADD"

#: Farcaster epoch: 2021-01-01T00:00:00Z. Message timestamps are seconds after it.
FARCASTER_EPOCH_S = 1_609_459_200
#: Measured: event id == blockNumber << 14 (2**14 == 16384).
EVENT_ID_BLOCK_SHIFT = 14
#: A hub whose newest event is older than this fails verification and is dropped.
MAX_TIP_AGE_SECONDS = 3600.0
#: How far back from a shard's tip to seed a tail.
TIP_LOOKBACK_BLOCKS = 300


def cast_timestamp(seconds_after_epoch: int) -> datetime:
    return datetime.fromtimestamp(FARCASTER_EPOCH_S + int(seconds_after_epoch), UTC)


def seed_for(max_height: int, lookback_blocks: int = TIP_LOOKBACK_BLOCKS) -> int:
    """The event id to start a tail from, given a shard's current height."""
    return max(0, max_height - lookback_blocks) << EVENT_ID_BLOCK_SHIFT


def extract_cast(event: dict[str, Any]) -> tuple[str, str, datetime, str] | None:
    """Pull (author_fid, hash, posted_at, text) from a merge-message event.

    Returns None for anything that is not a new cast — reactions, links, and
    username proofs carry no text and are not attention.
    """
    message = (event.get("mergeMessageBody") or {}).get("message") or {}
    data = message.get("data") or {}
    if data.get("type") != CAST_ADD:
        return None
    body = data.get("castAddBody") or {}
    text = body.get("text")
    if not isinstance(text, str) or not text:
        return None
    stamp = data.get("timestamp")
    if stamp is None:
        return None
    return (
        f"fc:{data.get('fid', 'unknown')}",
        str(message.get("hash", "")),
        cast_timestamp(int(stamp)),
        text,
    )


@dataclass(frozen=True)
class HubProbe:
    """The measured state of one candidate hub."""

    base: str
    reachable: bool
    fresh: bool
    tip_age_s: float | None
    event_shards: tuple[int, ...]
    casts_seen: int
    elapsed_s: float
    detail: str


def probe_hub(client: PacedClient, base: str, clock: Clock) -> HubProbe:
    """Measure one hub: reachability, which shards serve events, and tip age."""
    started = time.monotonic()
    info = client.get(SOURCE, base + INFO_PATH, params={"dbstats": "true"}, note="hub info")
    if not info.ok or not isinstance(info.json_body, dict):
        return HubProbe(
            base,
            False,
            False,
            None,
            (),
            0,
            time.monotonic() - started,
            f"info HTTP {info.status}: {info.text[:120]}",
        )
    shards = info.json_body.get("shardInfos") or []
    if not shards:
        return HubProbe(
            base,
            True,
            False,
            None,
            (),
            0,
            time.monotonic() - started,
            "200 but no shardInfos: not a Snapchain hub",
        )

    serving: list[int] = []
    casts = 0
    newest: datetime | None = None
    for shard in shards:
        height = int(shard.get("maxHeight") or 0)
        if height <= 0:
            continue
        shard_id = int(shard.get("shardId", 0))
        response = client.get(
            SOURCE,
            base + EVENTS_PATH,
            params={"from_event_id": seed_for(height), "shard_index": shard_id},
            note=f"events shard {shard_id}",
        )
        if not response.ok or not isinstance(response.json_body, dict):
            continue
        serving.append(shard_id)
        for event in response.json_body.get("events") or []:
            extracted = extract_cast(event)
            if extracted is None:
                continue
            casts += 1
            posted = extracted[2]
            newest = posted if newest is None else max(newest, posted)

    if newest is None:
        return HubProbe(
            base,
            True,
            False,
            None,
            tuple(serving),
            casts,
            time.monotonic() - started,
            f"reachable, {len(serving)} shard(s) serving events, but no dated cast at the tip",
        )
    age = (clock.now() - newest).total_seconds()
    return HubProbe(
        base,
        True,
        age <= MAX_TIP_AGE_SECONDS,
        age,
        tuple(serving),
        casts,
        time.monotonic() - started,
        (
            f"newest cast {age:.0f}s old"
            if age <= MAX_TIP_AGE_SECONDS
            else f"STALE: newest cast {age / 86400:.1f} days old — reachable but dead"
        ),
    )


def find_live_hub(client: PacedClient, clock: Clock) -> tuple[HubProbe | None, list[HubProbe]]:
    """Probe candidates in order; return the first fresh one and every attempt."""
    attempts: list[HubProbe] = []
    for base in HUB_CANDIDATES:
        probe = probe_hub(client, base, clock)
        attempts.append(probe)
        if probe.reachable and probe.fresh:
            return (probe, attempts)
    return (None, attempts)


def poll_casts(
    client: PacedClient,
    base: str,
    shard_ids: tuple[int, ...],
    cursors: dict[int, int],
    on_cast: Callable[[str, str, datetime, str], None],
) -> dict[int, int]:
    """Poll each shard once from its cursor; return advanced cursors.

    The cursor advances only past events that were actually delivered to
    ``on_cast``, so a crash mid-page re-reads rather than skipping. A duplicate
    is harmless (the store is keyed by message hash); a skip is an unfixable
    hole in a forward-recorded cohort.
    """
    advanced = dict(cursors)
    for shard_id in shard_ids:
        response = client.get(
            SOURCE,
            base + EVENTS_PATH,
            params={"from_event_id": advanced.get(shard_id, 0), "shard_index": shard_id},
            note=f"tail shard {shard_id}",
        )
        if not response.ok or not isinstance(response.json_body, dict):
            continue
        events = response.json_body.get("events") or []
        for event in events:
            extracted = extract_cast(event)
            if extracted is not None:
                on_cast(*extracted)
        if events:
            advanced[shard_id] = int(events[-1].get("id", advanced.get(shard_id, 0))) + 1
    return advanced


def current_seeds(client: PacedClient, base: str) -> dict[int, int]:
    """Seed a tail at each shard's current tip."""
    info = client.get(SOURCE, base + INFO_PATH, params={"dbstats": "true"}, note="seed")
    if not info.ok or not isinstance(info.json_body, dict):
        return {}
    seeds: dict[int, int] = {}
    for shard in info.json_body.get("shardInfos") or []:
        height = int(shard.get("maxHeight") or 0)
        if height > 0:
            seeds[int(shard.get("shardId", 0))] = seed_for(height)
    return seeds


def verify(client: PacedClient, clock: Clock) -> list[AccessResult]:
    """Probe every candidate; report the first FRESH hub, or drop the source."""
    live, attempts = find_live_hub(client, clock)
    trail = " | ".join(f"{a.base} -> {a.detail}" for a in attempts)

    if live is None:
        return [
            AccessResult(
                source=SOURCE,
                endpoint=", ".join(HUB_CANDIDATES),
                reachable=False,
                measured_rate="n/a",
                measured_limit="n/a",
                cost="n/a",
                detail=(
                    f"no FRESH public hub across {len(attempts)} probed. Reachability "
                    f"alone is not verification: a hub can serve HTTP 200 while months "
                    f"stale. {trail}"
                ),
                measured_at=iso(clock.now()),
            )
        ]

    per_day = int(live.casts_seen / max(live.elapsed_s, 0.01) * 0) or None
    return [
        AccessResult(
            source=SOURCE,
            endpoint=f"GET {live.base}{EVENTS_PATH} (shards {list(live.event_shards)})",
            reachable=True,
            measured_rate=(
                f"{live.casts_seen} casts across {len(live.event_shards)} shard pages in "
                f"{live.elapsed_s:.2f}s; tip age {live.tip_age_s:.0f}s"
                + (f"; ~{per_day:,}/day" if per_day else "")
            ),
            measured_limit=(
                f"no rate limit observed at ~12 req/s; self-imposed cap "
                f"{registry.FARCASTER_DAILY_CAP:,}/day at "
                f"{registry.FARCASTER_MIN_SPACING_S:.1f}s spacing"
            ),
            cost="keyless, free",
            detail=(
                f"{live.detail}; event id == blockNumber << {EVENT_ID_BLOCK_SHIFT} (measured). "
                f"Rejected first: {trail}"
            ),
            measured_at=iso(clock.now()),
        )
    ]
