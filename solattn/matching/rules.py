"""The registered matching rules, with the collision policy fixed in advance.

**Ticker collisions are the expected failure mode of this study, not an edge
case** (ADR-005). A cashtag or name matching more than one active mint is
recorded as ``ambiguous`` and attributed to **none of them** — never split
fractionally, never assigned to the most recent, most liquid, or most mentioned.
Ambiguity is a first-class category with its own daily count.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from solattn import registry
from solattn.attention import filters
from solattn.records import PoolBirth


@dataclass(frozen=True)
class UniverseEntry:
    """One token in the active matching universe."""

    mint: str
    symbol: str
    name: str
    born_at: datetime


class ActiveUniverse:
    """The tokens a message may be attributed to at a given instant.

    Active = born within the registered trailing window (30 days). Built from
    the birth manifests only — **never from any attention-ranked surface.**
    """

    def __init__(self, entries: list[UniverseEntry]) -> None:
        self._entries = entries
        self._by_mint = {e.mint: e for e in entries}
        self._by_symbol: dict[str, list[UniverseEntry]] = {}
        self._by_name: dict[str, list[UniverseEntry]] = {}
        for entry in entries:
            if entry.symbol:
                self._by_symbol.setdefault(entry.symbol.upper(), []).append(entry)
            if len(entry.name) >= registry.MIN_NAME_MATCH_LEN:
                self._by_name.setdefault(entry.name.lower(), []).append(entry)

    @classmethod
    def from_births(cls, births: list[PoolBirth]) -> ActiveUniverse:
        from solattn.clock import parse_iso

        return cls(
            [
                UniverseEntry(
                    mint=b.mint,
                    symbol=b.symbol,
                    name=b.name,
                    born_at=parse_iso(b.pool_created_at),
                )
                for b in births
            ]
        )

    def active_at(self, moment: datetime) -> ActiveUniverse:
        """Restrict to tokens born inside the registered trailing window."""
        floor = moment - timedelta(days=registry.ACTIVE_UNIVERSE_DAYS)
        return ActiveUniverse([e for e in self._entries if floor <= e.born_at <= moment])

    def __len__(self) -> int:
        return len(self._entries)

    def has_mint(self, mint: str) -> bool:
        return mint in self._by_mint

    def by_symbol(self, symbol: str) -> list[UniverseEntry]:
        return self._by_symbol.get(symbol.upper(), [])

    def names(self) -> list[str]:
        return list(self._by_name)

    def by_name(self, name: str) -> list[UniverseEntry]:
        return self._by_name.get(name.lower(), [])


@dataclass(frozen=True)
class Match:
    """The attribution decision for one message.

    ``mint`` is None for ``ambiguous`` and ``unmatched``. ``candidates`` records
    how many active mints a secondary match collided with, so the ambiguity is
    quantified rather than merely flagged.
    """

    kind: str
    mint: str | None
    candidates: int
    conflict: bool


def match_message(text: str, universe: ActiveUniverse) -> Match:
    """Attribute one message under the registered rules, in priority order."""
    hit = filters.apply(text)

    # Rule 1 (primary): mint address exact match. Deterministic, collision-free.
    known_mints = [m for m in hit.mints if universe.has_mint(m)]
    if known_mints:
        chosen = known_mints[0]
        conflict = _secondary_points_elsewhere(hit, universe, chosen)
        return Match(registry.MATCH_MINT, chosen, len(known_mints), conflict)

    # Rule 2 (secondary): cashtag.
    for cashtag in hit.cashtags:
        candidates = universe.by_symbol(cashtag)
        if len(candidates) == 1:
            return Match(registry.MATCH_CASHTAG, candidates[0].mint, 1, False)
        if len(candidates) > 1:
            return Match(registry.MATCH_AMBIGUOUS, None, len(candidates), False)

    # Rule 3 (secondary): full-name exact match at word boundaries.
    lowered = text.lower()
    for name in universe.names():
        if re.search(rf"(?<!\w){re.escape(name)}(?!\w)", lowered):
            candidates = universe.by_name(name)
            if len(candidates) == 1:
                return Match(registry.MATCH_NAME, candidates[0].mint, 1, False)
            return Match(registry.MATCH_AMBIGUOUS, None, len(candidates), False)

    return Match(registry.MATCH_UNMATCHED, None, 0, False)


def _secondary_points_elsewhere(
    hit: filters.FilterHit, universe: ActiveUniverse, chosen: str
) -> bool:
    """True when a cashtag in the same message points at a different token.

    The mint address wins (registered priority), and the conflict is recorded
    and counted rather than discarded.
    """
    for cashtag in hit.cashtags:
        for candidate in universe.by_symbol(cashtag):
            if candidate.mint != chosen:
                return True
    return False
