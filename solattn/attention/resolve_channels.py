"""Resolve the fixed channel list from Telegram's own MTProto search.

Implements REGISTRATION.md Amendment 1 (2026-08-16) exactly. **No human or
model judgment selects a channel.** The rule is: search the registered query
set, union and deduplicate, apply two mechanical predicates, rank by Telegram's
own ``participants_count``, break ties by username ascending, take the top 20.

The relevance predicate deliberately reuses ``attention.filters.find_keywords``
- the same word-boundary matcher the §7 ingest filter uses - so the two cannot
drift apart.

This runs **once**. Re-running later would produce a different list, which the
amendment forbids for this cohort.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from solattn import registry
from solattn.attention import filters


@dataclass(frozen=True, slots=True)
class Candidate:
    """A search hit, before ranking."""

    channel_id: int
    username: str
    title: str
    matched_queries: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ResolvedChannel:
    """One channel on the resolved list, with the field it was ranked by."""

    rank: int
    username: str
    title: str
    participants_count: int
    matched_queries: tuple[str, ...]
    resolved_at: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


def is_eligible(broadcast: bool, megagroup: bool, username: str | None) -> bool:
    """Amendment step 3: a public broadcast channel, not a group.

    A channel without a username is not public and is excluded - the only
    surviving half of §7's exclusion clause.
    """
    return bool(broadcast) and not bool(megagroup) and bool(username)


def is_relevant(title: str, username: str) -> bool:
    """Amendment step 4: title + username contains a registered keyword.

    Word-boundary, case-insensitive, through the same code path as the §7
    ingest filter. ``about`` is deliberately not consulted - it would require a
    getFullChannel on every search hit, and the predicate must be decidable
    before that cost is paid.
    """
    return bool(filters.find_keywords(f"{title} {username}"))


def matched_keywords(title: str, username: str) -> tuple[str, ...]:
    """Which registered keywords the channel matched, for the audit trail."""
    return filters.find_keywords(f"{title} {username}")


def rank_and_cut(
    counted: list[tuple[Candidate, int]], resolved_at: str, size: int = registry.CHANNEL_LIST_SIZE
) -> list[ResolvedChannel]:
    """Amendment steps 5-7: rank by participants_count desc, tie-break username asc, top N.

    The tie-break is §7's own and is not outcome-dependent; usernames are
    unique, so no second-order tie-break is needed.
    """
    ordered = sorted(counted, key=lambda pair: (-pair[1], pair[0].username.lower()))
    return [
        ResolvedChannel(
            rank=index,
            username=candidate.username,
            title=candidate.title,
            participants_count=count,
            matched_queries=candidate.matched_queries,
            resolved_at=resolved_at,
        )
        for index, (candidate, count) in enumerate(ordered[:size], start=1)
    ]
