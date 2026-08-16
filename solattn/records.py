"""Frozen record types. Every persisted row has a type here.

Timestamps serialize as ISO-8601 UTC with a ``Z`` suffix; calendar dates as
``YYYY-MM-DD``. Both forms are fixed by REGISTRATION.md and by clock.py.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PoolBirth:
    """One pool observed at birth from the keyless new-pools feed.

    ``venue_class`` is the registered tag from the launch-venue denylist
    (ADR-002). Nothing is discarded at collection time; the analysis filter is
    applied to this tag, whose rule predates the data.
    """

    mint: str
    pool: str
    dex: str
    venue_class: str
    symbol: str
    name: str
    pool_created_at: str
    manifest_day: str
    source: str
    source_url: str
    retrieved_at: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Mention:
    """One ingested message, with its registered match attribution.

    ``matched_mint`` is None for ``ambiguous`` and ``unmatched`` — an ambiguous
    mention is attributed to NOBODY (ADR-005), never split and never assigned.
    """

    source: str
    channel: str
    message_id: str
    author_id: str
    posted_at: str
    match_kind: str
    matched_mint: str | None
    candidates: int
    conflict: bool
    ingested_at: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Candle:
    """One daily OHLCV bar for a pool."""

    pool: str
    day: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    retrieved_at: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MatchCounts:
    """The per-day, per-source first-class match tally.

    ``ambiguous`` is a first-class category with its own count, reported
    alongside matched and unmatched every day — never folded into either.
    """

    day: str
    source: str
    ingested: int
    matched_mint: int
    matched_cashtag: int
    matched_name: int
    ambiguous: int
    unmatched: int
    conflicts: int

    @property
    def matched_total(self) -> int:
        return self.matched_mint + self.matched_cashtag + self.matched_name

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["matched_total"] = self.matched_total
        return row


@dataclass(frozen=True, slots=True)
class AccessResult:
    """The measured verification outcome for one source.

    A source that fails verification is REPORTED and DROPPED, not worked around
    silently — ``reachable=False`` with a stated reason is a first-class result.
    """

    source: str
    endpoint: str
    reachable: bool
    measured_rate: str
    measured_limit: str
    cost: str
    detail: str
    measured_at: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)
