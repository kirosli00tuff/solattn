"""The registered matching rules, including the collision policy."""

from __future__ import annotations

from datetime import UTC, datetime

from solattn import registry
from solattn.attention import filters
from solattn.matching.rules import ActiveUniverse, UniverseEntry, match_message

BORN = datetime(2026, 8, 16, 12, 0, tzinfo=UTC)
MINT_A = "7CSWFsrB3gPc5o5hxKTJCUbFDq4QyTWpjVG76S1Xpump"
MINT_B = "CP1KFKft4HtvNgNx5PDPrsmZbBs9fDFoVbJAKfiRAUde"


def universe(*entries: UniverseEntry) -> ActiveUniverse:
    return ActiveUniverse(list(entries))


def test_mint_exact_match_is_primary() -> None:
    # Arrange
    active = universe(UniverseEntry(MINT_A, "WIF", "dogwifhat", BORN))
    # Act
    decision = match_message(f"aping {MINT_A} now", active)
    # Assert
    assert decision.kind == registry.MATCH_MINT
    assert decision.mint == MINT_A


def test_cashtag_matching_one_mint_resolves() -> None:
    active = universe(UniverseEntry(MINT_A, "WIF", "dogwifhat", BORN))
    decision = match_message("$WIF looking strong", active)
    assert decision.kind == registry.MATCH_CASHTAG
    assert decision.mint == MINT_A


def test_cashtag_collision_is_ambiguous_and_attributed_to_nobody() -> None:
    """Ticker collisions are the expected failure mode, not an edge case."""
    # Arrange - two active mints share the ticker
    active = universe(
        UniverseEntry(MINT_A, "WIF", "dogwifhat", BORN),
        UniverseEntry(MINT_B, "WIF", "wifout", BORN),
    )
    # Act
    decision = match_message("$WIF to the moon", active)
    # Assert - attributed to NEITHER, and the collision size is recorded
    assert decision.kind == registry.MATCH_AMBIGUOUS
    assert decision.mint is None
    assert decision.candidates == 2


def test_mint_beats_a_conflicting_cashtag_and_records_the_conflict() -> None:
    active = universe(
        UniverseEntry(MINT_A, "WIF", "dogwifhat", BORN),
        UniverseEntry(MINT_B, "BONK", "bonkcoin", BORN),
    )
    decision = match_message(f"{MINT_A} is the real one, not $BONK", active)
    assert decision.kind == registry.MATCH_MINT
    assert decision.mint == MINT_A
    assert decision.conflict is True


def test_name_shorter_than_the_registered_floor_is_not_matchable() -> None:
    active = universe(UniverseEntry(MINT_A, "ZZZ", "abc", BORN))
    assert match_message("abc is everywhere", active).kind == registry.MATCH_UNMATCHED


def test_unmatched_is_kept_as_its_own_class() -> None:
    active = universe(UniverseEntry(MINT_A, "WIF", "dogwifhat", BORN))
    decision = match_message("solana is busy today", active)
    assert decision.kind == registry.MATCH_UNMATCHED
    assert decision.mint is None


def test_unknown_mint_shape_does_not_match_the_universe() -> None:
    active = universe(UniverseEntry(MINT_A, "WIF", "dogwifhat", BORN))
    decision = match_message(f"look at {MINT_B}", active)
    assert decision.kind == registry.MATCH_UNMATCHED


def test_active_universe_excludes_births_outside_the_registered_window() -> None:
    old = datetime(2026, 6, 1, tzinfo=UTC)
    active = universe(
        UniverseEntry(MINT_A, "WIF", "dogwifhat", old),
        UniverseEntry(MINT_B, "BONK", "bonkcoin", BORN),
    ).active_at(BORN)
    assert len(active) == 1
    assert active.has_mint(MINT_B)
    assert not active.has_mint(MINT_A)


def test_filter_is_shape_dominant() -> None:
    """Rules 1 and 2 match a form, not a name, so they cannot favour a token."""
    assert filters.apply(f"{MINT_A}").rule == "1-mint-shape"
    assert filters.apply("$WIF").rule == "2-cashtag-shape"
    assert filters.apply("solana update").rule == "3-keyword"
    assert filters.apply("just a normal sentence").passed is False


def test_short_ambiguous_keywords_are_excluded_by_registration() -> None:
    """ "sol" alone must not admit a message — it collides with ordinary prose."""
    assert filters.apply("el sol brilla hoy").passed is False
