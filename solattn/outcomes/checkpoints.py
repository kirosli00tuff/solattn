"""Horizon checkpoints: fetch candles per pool at the registered instants.

Outcome collection fetches at CHECKPOINTS rather than continuously, to stay
inside the measured rate limit: the daily-OHLCV endpoint returns a long history
in one call, so each pool needs exactly two calls across its whole life —
T0+10d (entry mark plus the 1/3/7-day exits and their death lookbacks) and
T0+33d (the 30-day exit).

Restart-proof: a checkpoint is recorded as done only AFTER its candles are
durably written.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from solattn import jsonl, registry
from solattn.clock import Clock, day_str, iso, utc_date
from solattn.config import Settings
from solattn.http import PacedClient
from solattn.ledger import RequestCapError
from solattn.lifecycle import Lifecycle
from solattn.sources import geckoterminal, solbench
from solattn.universe import manifest


def candles_path(settings: Settings, pool: str) -> Any:
    return settings.outcomes_dir() / f"candles-{pool}.jsonl"


def due_days(today: date, checkpoint: int, catch_up_days: int = 5) -> list[str]:
    """Birth days due at this checkpoint today, plus a trailing catch-up window.

    The window self-heals a missed daily run: the done-set makes re-scans
    idempotent, and daily candles are retrospective, so a fetch a few days late
    returns the identical rows the on-time fetch would have. No registered bar
    moves — the checkpoint instants of REGISTRATION.md §8 are unchanged; this
    only stops a skipped day from becoming a permanent hole.
    """
    from datetime import timedelta

    return [day_str(today - timedelta(days=checkpoint + back)) for back in range(catch_up_days)]


def _done_path(settings: Settings) -> Any:
    return settings.state_dir() / "checkpoints.jsonl"


def _already_done(settings: Settings) -> set[tuple[str, int]]:
    return {(str(row["pool"]), int(row["checkpoint"])) for row in jsonl.read(_done_path(settings))}


def run_checkpoints(client: PacedClient, clock: Clock, settings: Settings) -> dict[str, Any]:
    """Fetch every pool due at a registered checkpoint today.

    Only the primary universe (``amm``) is outcome-fetched: adding the
    launchpad subset would need ~14,900 calls/day against a 14,400/day capacity
    (REGISTRATION.md 7). The arithmetic is registered, not discovered here.
    """
    life = Lifecycle(settings.state_dir() / "lifecycle.jsonl", "checkpoints", clock)
    life.started()
    today = utc_date(clock.now())
    done = _already_done(settings)
    fetched = 0
    refused = 0
    skipped_launchpad = 0
    pools_due = 0

    for checkpoint in registry.CHECKPOINT_DAYS:
        for day in due_days(today, checkpoint):
            for birth in manifest.read_day(settings.manifests_dir(), day):
                if birth.venue_class != registry.PRIMARY_VENUE_CLASS:
                    skipped_launchpad += 1
                    continue
                pools_due += 1
                if (birth.pool, checkpoint) in done:
                    continue
                try:
                    candles = geckoterminal.fetch_daily_candles(
                        client, clock, birth.pool, limit=checkpoint + 5
                    )
                except RequestCapError as refusal:
                    life.refused(str(refusal), pool=birth.pool, checkpoint=checkpoint)
                    refused += 1
                    break
                if candles:
                    jsonl.append_many(
                        candles_path(settings, birth.pool), [c.to_row() for c in candles]
                    )
                    fetched += 1
                jsonl.append(
                    _done_path(settings),
                    {
                        "at": iso(clock.now()),
                        "pool": birth.pool,
                        "mint": birth.mint,
                        "checkpoint": checkpoint,
                        "candles": len(candles),
                        "birth_day": day,
                    },
                )

    label, bench = solbench.fetch(client, clock)
    if bench:
        jsonl.append_many(
            settings.outcomes_dir() / "benchmark-sol.jsonl", [c.to_row() for c in bench]
        )

    summary = {
        "checkpoints": list(registry.CHECKPOINT_DAYS),
        "pools_due": pools_due,
        "pools_fetched": fetched,
        "refusals": refused,
        "launchpad_skipped": skipped_launchpad,
        "benchmark_source": label or "NONE",
        "benchmark_candles": len(bench),
        "at": iso(clock.now()),
    }
    life.stopped("checkpoints", **summary)
    return summary
