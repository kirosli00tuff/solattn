"""The birth-ordered universe watcher.

Sweeps the keyless new-pools feed on the registered cadence and writes every
observed birth to its immutable daily manifest. **No attention input of any
kind participates**: the feed is ordered by pool creation and membership is
decided by birth and nothing else (ADR-001).

Restart-proof: the cursor records the newest ``pool_created_at`` already
durably written, and is advanced only AFTER the manifest write. A cursor ahead
of the data is an invisible hole in a forward-recorded cohort, and a forward
hole cannot be backfilled.
"""

from __future__ import annotations

import time
from typing import Any

from solattn import registry
from solattn.clock import Clock, day_str, iso, utc_date
from solattn.config import Settings
from solattn.http import PacedClient
from solattn.ledger import RequestCapError
from solattn.lifecycle import Cursor, Lifecycle
from solattn.sources import geckoterminal
from solattn.universe import manifest


def _lifecycle(settings: Settings, clock: Clock) -> Lifecycle:
    return Lifecycle(settings.state_dir() / "lifecycle.jsonl", "watcher", clock)


def sweep_once(client: PacedClient, clock: Clock, settings: Settings) -> dict[str, Any]:
    """One sweep of the registered page count. Returns what was observed."""
    life = _lifecycle(settings, clock)
    cursor = Cursor(settings.state_dir() / "watcher.json")
    seen_before = str(cursor.get("newest_pool_created_at", ""))

    collected = []
    pages_read = 0
    pages_unavailable = 0
    truncated = False
    for page in range(1, registry.WATCH_PAGES_PER_SWEEP + 1):
        try:
            births = geckoterminal.fetch_new_pools(client, clock, page)
        except RequestCapError as refusal:
            life.refused(str(refusal), page=page, pages_read=pages_read)
            truncated = True
            break
        if births is None:
            # The source did not answer (429/5xx/transport). That is NOT the
            # end of the feed, and it must never be recorded as one: the sweep
            # stops short, says so, and is counted as truncated (ADR-017).
            life.errored(
                "new_pools unavailable (non-2xx or transport); sweep TRUNCATED, "
                "not end-of-feed. Pages after this one were not read.",
                page=page,
                pages_read=pages_read,
            )
            pages_unavailable += 1
            truncated = True
            break
        pages_read += 1
        if not births:
            # A 2xx answer with no rows IS the end of the feed: measured
            # absence, not absent data.
            break
        collected.extend(births)

    fresh = [b for b in collected if b.pool_created_at > seen_before] if seen_before else collected
    written = manifest.append_births(settings.manifests_dir(), fresh)

    newest = max((b.pool_created_at for b in collected), default=seen_before)
    if newest:
        cursor.write(
            newest_pool_created_at=newest,
            updated_at=iso(clock.now()),
            schema=registry.SCHEMA_VERSION,
        )

    amm = sum(1 for b in fresh if b.venue_class == registry.VENUE_CLASS_AMM)
    summary: dict[str, Any] = {
        "pages_read": pages_read,
        "pages_unavailable": pages_unavailable,
        "truncated": int(truncated),
        "pools_seen": len(collected),
        "new_births": len(fresh),
        "new_amm": amm,
        "new_launchpad": len(fresh) - amm,
        "days_written": written,
        "newest_pool_created_at": newest,
        "at": iso(clock.now()),
    }
    life.heartbeat("sweep", **{k: v for k, v in summary.items() if k != "days_written"})

    today = day_str(utc_date(clock.now()))
    counts = manifest.day_counts(settings.manifests_dir(), today)
    if counts["saturated"]:
        life.mark(
            "saturation",
            f"observed {counts['amm']} amm births on {today} against the registered "
            f"saturation threshold {registry.SATURATION_AMM_PER_DAY}; outcome-checkpoint "
            f"capacity is at risk. Reporting rather than sampling.",
            **counts,
        )
    return summary


def watch_forever(
    client: PacedClient,
    clock: Clock,
    settings: Settings,
    minutes: float | None = None,
) -> int:
    """Sweep on the registered cadence until stopped or ``minutes`` elapses."""
    life = _lifecycle(settings, clock)
    life.started(
        f"sweeping every {registry.WATCH_SWEEP_SECONDS}s, "
        f"{registry.WATCH_PAGES_PER_SWEEP} pages per sweep"
    )
    deadline = None if minutes is None else time.monotonic() + minutes * 60
    sweeps = 0
    try:
        while True:
            if deadline is not None and time.monotonic() >= deadline:
                return sweeps
            sweep_once(client, clock, settings)
            sweeps += 1
            if deadline is not None and time.monotonic() >= deadline:
                return sweeps
            time.sleep(registry.WATCH_SWEEP_SECONDS)
    except KeyboardInterrupt:
        return sweeps
    finally:
        life.stopped(f"{sweeps} sweeps")
