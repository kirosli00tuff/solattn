"""The registered attention statistics and quintile construction.

Mechanical only — **no LLM judgment produces any figure here** (ADR-004). Every
window, statistic, tie-break and fallback was fixed in REGISTRATION.md 2 before
any message was collected.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from solattn import registry
from solattn.clock import parse_iso
from solattn.records import Mention


@dataclass(frozen=True)
class AttentionStats:
    """The five registered statistics for one pool, over its birth window."""

    mint: str
    mentions_1h: int
    mentions_6h: int
    mentions_24h: int
    authors_24h: int

    @property
    def v1(self) -> float:
        return self.mentions_1h / 1.0

    @property
    def v6(self) -> float:
        return self.mentions_6h / 6.0

    @property
    def v24(self) -> float:
        return self.mentions_24h / 24.0

    @property
    def ua24(self) -> float:
        return self.authors_24h / 24.0

    @property
    def accel(self) -> float:
        """v1 / max(v24, 1/24); defined as 0.0 for a pool with no mentions."""
        if self.mentions_24h == 0:
            return 0.0
        return self.v1 / max(self.v24, registry.ACCEL_FLOOR)

    def statistic(self, name: str) -> float:
        if name not in registry.STATISTICS:
            raise KeyError(
                f"{name!r} is not a registered statistic. The trial grid may not grow; "
                f"registered statistics are {registry.STATISTICS}."
            )
        return float(getattr(self, name))


def compute_stats(
    mint: str,
    born_at: datetime,
    mentions: list[Mention],
    match_set: str = registry.MATCH_SET_PRIMARY,
) -> AttentionStats:
    """Count mentions and distinct authors in the registered windows from T0.

    ``match_set`` selects the registered match kinds: the primary set is
    mint-exact only; the secondary set adds cashtag matches.
    """
    kinds = (
        {registry.MATCH_MINT}
        if match_set == registry.MATCH_SET_PRIMARY
        else {registry.MATCH_MINT, registry.MATCH_CASHTAG}
    )
    counts = dict.fromkeys(registry.ATTENTION_SUBWINDOW_HOURS, 0)
    authors: set[str] = set()
    for mention in mentions:
        if mention.matched_mint != mint or mention.match_kind not in kinds:
            continue
        posted = parse_iso(mention.posted_at)
        offset = posted - born_at
        if offset < timedelta(0):
            continue
        for hours in registry.ATTENTION_SUBWINDOW_HOURS:
            if offset <= timedelta(hours=hours):
                counts[hours] += 1
        if offset <= timedelta(hours=registry.ATTENTION_WINDOW_HOURS):
            authors.add(f"{mention.source}:{mention.author_id}")
    return AttentionStats(
        mint=mint,
        mentions_1h=counts[1],
        mentions_6h=counts[6],
        mentions_24h=counts[24],
        authors_24h=len(authors),
    )


def rank_within_day(stats: list[AttentionStats], statistic: str) -> list[AttentionStats]:
    """Rank a birth-day cohort by the statistic, descending, with registered tie-breaks.

    Ties break by ``authors(24h)`` descending, then by mint address ascending.
    Neither tie-break is outcome-dependent — both were fixed at registration.
    """
    return sorted(stats, key=lambda s: (-s.statistic(statistic), -s.authors_24h, s.mint))


def assign_quintiles(stats: list[AttentionStats], statistic: str) -> dict[str, int]:
    """Split a birth-day cohort into five equal-count buckets, Q1 low .. Q5 high.

    When the cohort size is not divisible by 5 the **remainder goes to the
    lowest buckets**, so Q5 is never inflated by rounding.
    """
    ranked = rank_within_day(stats, statistic)
    total = len(ranked)
    if total == 0:
        return {}
    base, remainder = divmod(total, registry.QUINTILE_COUNT)
    sizes = [base] * registry.QUINTILE_COUNT
    # ``sizes`` runs Q5 (index 0) down to Q1 (index -1), so the remainder is
    # added from the END: the LOWEST buckets absorb it and Q5 is never inflated
    # by rounding, as REGISTRATION.md section 2 requires.
    for index in range(remainder):
        sizes[-(index + 1)] += 1

    assignment: dict[str, int] = {}
    position = 0
    for offset, size in enumerate(sizes):
        quintile = registry.QUINTILE_COUNT - offset
        for entry in ranked[position : position + size]:
            assignment[entry.mint] = quintile
        position += size
    return assignment


def is_degenerate(stats: list[AttentionStats]) -> bool:
    """True when the zero-attention share exceeds the registered threshold.

    Registered in advance **because it is expected to fire**: most births will
    have zero mentions, and a quintile split over an all-zero cohort orders by
    the tie-break rather than by attention.
    """
    if not stats:
        return True
    zeros = sum(1 for s in stats if s.mentions_24h == 0)
    return (zeros / len(stats)) > registry.DEGENERATE_ZERO_FRACTION


def binary_split(stats: list[AttentionStats]) -> dict[str, str]:
    """The registered fallback: any-mention versus zero-mention.

    Reported alongside — never instead of — the quintile result, for every day,
    so the choice cannot be made after seeing outcomes.
    """
    return {s.mint: ("any_mention" if s.mentions_24h > 0 else "zero_mention") for s in stats}
