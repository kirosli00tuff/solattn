"""The registered attention statistics and quintile construction."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from solattn import registry
from solattn.attention.metrics import (
    AttentionStats,
    assign_quintiles,
    binary_split,
    compute_stats,
    is_degenerate,
    rank_within_day,
)
from solattn.clock import iso
from solattn.records import Mention

BORN = datetime(2026, 8, 16, 0, 0, tzinfo=UTC)
MINT = "Mint1111111111111111111111111111111111111111"


def mention(
    offset_h: float, author: str, mint: str = MINT, kind: str = registry.MATCH_MINT
) -> Mention:
    return Mention(
        source="bluesky",
        channel="jetstream",
        message_id=f"m{offset_h}-{author}",
        author_id=author,
        posted_at=iso(BORN + timedelta(hours=offset_h)),
        match_kind=kind,
        matched_mint=mint,
        candidates=1,
        conflict=False,
        ingested_at=iso(BORN),
    )


def test_windows_are_nested_and_counted_from_birth() -> None:
    # Arrange - one mention in hour 0, one at hour 3, one at hour 20, one after the window
    mentions = [mention(0.5, "a"), mention(3, "b"), mention(20, "c"), mention(30, "d")]
    # Act
    stats = compute_stats(MINT, BORN, mentions)
    # Assert
    assert (stats.mentions_1h, stats.mentions_6h, stats.mentions_24h) == (1, 2, 3)
    assert stats.authors_24h == 3


def test_velocities_are_per_hour() -> None:
    stats = compute_stats(MINT, BORN, [mention(0.5, "a"), mention(3, "b")])
    assert stats.v1 == 1.0
    assert stats.v6 == 2 / 6
    assert stats.v24 == 2 / 24


def test_accel_is_zero_without_mentions_and_finite_with_one() -> None:
    assert compute_stats(MINT, BORN, []).accel == 0.0
    single = compute_stats(MINT, BORN, [mention(0.1, "a")])
    assert single.accel == 1.0 / max(1 / 24, registry.ACCEL_FLOOR)


def test_mentions_before_birth_are_ignored() -> None:
    stats = compute_stats(MINT, BORN, [mention(-2, "a"), mention(1, "b")])
    assert stats.mentions_24h == 1


def test_primary_match_set_excludes_cashtag_matches() -> None:
    mentions = [mention(1, "a"), mention(2, "b", kind=registry.MATCH_CASHTAG)]
    primary = compute_stats(MINT, BORN, mentions, registry.MATCH_SET_PRIMARY)
    secondary = compute_stats(MINT, BORN, mentions, registry.MATCH_SET_SECONDARY)
    assert primary.mentions_24h == 1
    assert secondary.mentions_24h == 2


def stat(mint: str, m24: int, authors: int = 1) -> AttentionStats:
    return AttentionStats(mint, 0, 0, m24, authors)


def test_quintiles_put_the_remainder_in_the_lowest_buckets() -> None:
    """Q5 is never inflated by rounding."""
    # Arrange - 7 pools across 5 buckets: sizes 2,2,1,1,1 from the bottom up
    cohort = [stat(f"m{i}", 100 - i) for i in range(7)]
    # Act
    assignment = assign_quintiles(cohort, "v24")
    # Assert - the top quintile holds the smaller share
    sizes = {q: sum(1 for v in assignment.values() if v == q) for q in range(1, 6)}
    assert sizes[5] == 1
    assert sizes[1] + sizes[2] == 4
    assert sum(sizes.values()) == 7


def test_highest_attention_lands_in_the_top_quintile() -> None:
    cohort = [stat(f"m{i}", i) for i in range(10)]
    assignment = assign_quintiles(cohort, "v24")
    assert assignment["m9"] == registry.TOP_QUINTILE
    assert assignment["m0"] == 1


def test_ties_break_by_authors_then_mint_and_never_by_outcome() -> None:
    cohort = [stat("bbb", 5, authors=1), stat("aaa", 5, authors=9), stat("ccc", 5, authors=1)]
    ranked = [s.mint for s in rank_within_day(cohort, "v24")]
    assert ranked == ["aaa", "bbb", "ccc"]


def test_degenerate_rule_fires_on_a_mostly_silent_cohort() -> None:
    cohort = [stat(f"m{i}", 0) for i in range(9)] + [stat("loud", 50)]
    assert is_degenerate(cohort) is True
    split = binary_split(cohort)
    assert split["loud"] == "any_mention"
    assert split["m0"] == "zero_mention"


def test_degenerate_rule_does_not_fire_on_an_active_cohort() -> None:
    assert is_degenerate([stat(f"m{i}", i) for i in range(1, 11)]) is False


def test_unregistered_statistic_raises_rather_than_silently_growing_the_grid() -> None:
    import pytest

    with pytest.raises(KeyError, match="trial grid may not grow"):
        stat("m", 1).statistic("v12")
