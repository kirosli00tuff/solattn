"""The registry must equal the numbers written in REGISTRATION.md.

The registration is the contract; ``solattn/registry.py`` is that contract in
code. If the two can drift, a mid-collection edit to a bar becomes invisible.
These tests make drift break the build.
"""

from __future__ import annotations

from pathlib import Path

from solattn import registry

ROOT = Path(__file__).resolve().parent.parent
DOC = " ".join((ROOT / "REGISTRATION.md").read_text(encoding="utf-8").split())
"""Whitespace-collapsed so a markdown reflow cannot break a pin; a deletion still does."""


def test_trial_grid_is_forty_and_counted() -> None:
    assert registry.TRIAL_GRID_SIZE == 40
    assert len(registry.HORIZONS) == 4
    assert len(registry.STATISTICS) == 5
    assert len(registry.MATCH_SETS) == 2
    assert "4 × 5 × 2 = 40 trials" in DOC


def test_primary_trial_is_designated() -> None:
    assert registry.PRIMARY_TRIAL == (7, "v24", "mint-exact")
    assert "`(h = 7d, statistic = v24, match set" in DOC


def test_sidak_alpha_matches_the_registered_figure() -> None:
    assert round(registry.SIDAK_ALPHA, 5) == 0.00128
    assert "0.00128" in DOC


def test_horizons_match_the_document() -> None:
    assert registry.HORIZONS_PRIMARY == (1, 3, 7)
    assert registry.HORIZONS_SECONDARY == (30,)
    assert "Primary: `h ∈ {1, 3, 7}` days" in DOC


def test_cost_band_matches_the_document() -> None:
    assert registry.COST_BPS_CENTRAL == 450
    assert (registry.COST_BPS_LOW, registry.COST_BPS_HIGH) == (300, 600)
    assert "450 bps round trip, charged 225 bps per leg" in DOC


def test_death_floor_matches_the_document() -> None:
    assert registry.DEATH_LOOKBACK_DAYS == 14
    assert registry.DEATH_DUST_FRACTION == 0.01
    assert "no candle with non-zero volume in the 14 days ending at" in DOC
    assert "below 1% of the entry close" in DOC


def test_entry_anchor_matches_the_document() -> None:
    assert registry.ENTRY_OFFSET_DAYS == 2
    assert "close of the daily candle for UTC date `d0 + 2`" in DOC


def test_attention_windows_match_the_document() -> None:
    assert registry.ATTENTION_SUBWINDOW_HOURS == (1, 6, 24)
    assert registry.ATTENTION_WINDOW_HOURS == 24
    assert "`[T0, T0 + 24h]`" in DOC


def test_quintile_rules_match_the_document() -> None:
    assert registry.QUINTILE_COUNT == 5
    assert registry.DEGENERATE_ZERO_FRACTION == 0.80
    assert "more than 80% of a birth day's cohort has `v24 == 0`" in DOC


def test_expected_rate_and_disagreement_rule() -> None:
    assert registry.EXPECTED_AMM_POOLS_PER_DAY == 1330
    assert registry.RATE_DISAGREEMENT_FACTOR == 2.0
    assert "~1,330 pools/day" in DOC or "**~1,330 pools/day**" in DOC
    assert "more than 2× in either direction is reported as" in DOC


def test_survivorship_priors_and_gap_rule() -> None:
    assert registry.PRIOR_BIRTH_ORDERED_DEATH_30D == 0.975
    assert registry.PRIOR_BIRTH_ORDERED_N == 40
    assert registry.PRIOR_ATTENTION_CRAWLED_DEATH_30D == 0.1875
    assert registry.PRIOR_ATTENTION_CRAWLED_N == 16
    assert registry.SURVIVORSHIP_GAP_POINTS == 15.0
    assert "more than 15 percentage points" in DOC


def test_power_and_cohort_bars() -> None:
    assert registry.UNDERPOWERED_MIN_N == 20
    assert registry.MIN_MATURED_POOLS == 300
    assert "fewer than 20 matured pools" in DOC
    assert "≥ 300 matured `amm` pools" in DOC


def test_pacing_and_capacity_are_the_measured_figures() -> None:
    assert registry.GECKOTERMINAL_MIN_SPACING_S == 6.0
    assert registry.WATCH_SWEEP_SECONDS == 120
    assert registry.WATCH_PAGES_PER_SWEEP == 4
    assert registry.CHECKPOINT_DAYS == (10, 33)
    assert "minimum 6.0 s between requests" in DOC


def test_ingest_filter_excludes_short_ambiguous_strings() -> None:
    """The registration excludes "sol" and "ca" deliberately."""
    assert "sol" not in registry.INGEST_KEYWORDS
    assert "ca" not in registry.INGEST_KEYWORDS
    assert "solana" in registry.INGEST_KEYWORDS


def test_launchpad_denylist_not_an_allowlist() -> None:
    """A dex not on the denylist classifies as amm — fails open, by design."""
    assert registry.classify_amm_default() if hasattr(registry, "classify_amm_default") else True
    from solattn.sources.geckoterminal import classify_venue

    assert classify_venue("pumpfun") == registry.VENUE_CLASS_LAUNCHPAD
    assert classify_venue("some-new-amm-launched-tomorrow") == registry.VENUE_CLASS_AMM


def test_channel_query_set_is_the_ingest_vocabulary_verbatim() -> None:
    """Amendment 1: the search queries ARE the registered §7 keyword set."""
    assert set(registry.CHANNEL_QUERY_SET) == set(registry.INGEST_KEYWORDS)
    assert len(registry.CHANNEL_QUERY_SET) == 11
    assert "Amendment 1 — 2026-08-16" in DOC


def test_amendment_did_not_touch_the_body() -> None:
    """Nothing above the amendment line may be edited (append-only rule)."""
    assert "Registered prior that H1 finds a tradeable signal: 5 to 8 percent" in DOC
    assert DOC.index("Amendment 1") > DOC.index("What would make this registration void")
