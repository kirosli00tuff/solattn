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


def test_trial_grid_is_counted_and_includes_the_series_dimension() -> None:
    """Amendment 2 grew the grid by the series dimension; it may not grow again."""
    assert registry.TRIAL_GRID_SIZE == 160
    assert len(registry.HORIZONS) == 4
    assert len(registry.STATISTICS) == 5
    assert len(registry.MATCH_SETS) == 2
    assert len(registry.ATTENTION_SERIES) == 4
    assert "4 × 5 × 2 × 4 = 160 trials" in DOC


def test_series_are_per_source_plus_a_secondary_pooled() -> None:
    assert registry.ATTENTION_SERIES == ("bluesky", "farcaster", "telegram", "pooled")
    assert registry.SERIES_POOLED == "pooled"
    assert "as a registered SECONDARY, never primary" in DOC


def test_under_detection_direction_is_registered_before_results() -> None:
    """The caveat must exist in the registration, not appear later in discussion."""
    assert "biases the measured association toward the null" in DOC
    assert "a positive result is not inflated by this weakness" in DOC


def test_telegram_construct_description_is_pinned() -> None:
    assert "alert-feed-dominated" in DOC


def test_primary_trial_is_designated_with_its_series() -> None:
    assert registry.PRIMARY_TRIAL == (7, "v24", "mint-exact", "bluesky")
    assert "series = bluesky" in DOC


def test_sidak_alpha_matches_the_registered_figure() -> None:
    assert round(registry.SIDAK_ALPHA, 6) == 0.000321
    assert "0.000321" in DOC


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


def test_amendment_2_did_not_touch_the_collected_instruments() -> None:
    """Amendment 2 changes reporting partition only - not any collected rule."""
    assert registry.ATTENTION_SUBWINDOW_HOURS == (1, 6, 24)
    assert registry.HORIZONS_PRIMARY == (1, 3, 7)
    assert registry.DEATH_LOOKBACK_DAYS == 14
    assert registry.COST_BPS_CENTRAL == 450
    assert registry.CHANNEL_LIST_SIZE == 20
    assert DOC.index("Amendment 2") > DOC.index("Amendment 1")


# --- Amendment 3: the death floor's third condition -------------------------


def test_amendment_3_registers_no_exit_candle_as_its_own_verdict() -> None:
    assert registry.DEATH_NO_EXIT_CANDLE == "no_exit_candle"
    assert registry.DEATH_REASONS == (
        "no_volume_in_lookback",
        "dust_close",
        "no_exit_candle",
    )
    assert len(set(registry.DEATH_REASONS)) == 3  # distinct, so deaths partition
    assert "(c) `no_exit_candle` — the exit-day candle is absent." in DOC


def test_amendment_3_records_that_it_did_not_silently_ratify() -> None:
    assert "That behaviour predated any registration text authorising" in DOC
    assert "13 of 20 sparse-pool cells" in DOC
    assert "as a registration decision" in DOC


def test_amendment_3_registers_the_bias_direction_toward_the_hypothesis() -> None:
    """The unfavourable direction must be in the registration, not the discussion."""
    assert "biases the measured association toward the hypothesis" in DOC
    assert "opposite direction from the under-detection caveat registered in" in DOC
    # Amendment 2's opposite-direction caveat still stands alongside it
    assert "biases the measured association toward the null" in DOC


def test_amendment_3_registers_the_per_stratum_mitigation() -> None:
    assert "must be reported per attention stratum as a first-class Stage B output" in DOC
    assert "is itself a finding about the instrument" in DOC


def test_carry_forward_is_a_robustness_report_not_a_selectable_trial() -> None:
    assert registry.EXIT_RULES == ("primary", "carry_forward")
    assert "may never become the headline" in DOC
    assert "It adds no cells to the trial grid" in DOC


def test_amendment_3_did_not_move_the_grid_or_any_other_bar() -> None:
    """The whole point: a specification gap closed without touching a bar."""
    assert registry.TRIAL_GRID_SIZE == 160
    assert round(registry.SIDAK_ALPHA, 6) == 0.000321
    assert registry.PRIMARY_TRIAL == (7, "v24", "mint-exact", "bluesky")
    assert registry.DEATH_LOOKBACK_DAYS == 14
    assert registry.DEATH_DUST_FRACTION == 0.01
    assert registry.ENTRY_OFFSET_DAYS == 2
    assert registry.COST_BPS_CENTRAL == 450
    assert DOC.index("Amendment 3") > DOC.index("Amendment 2")


# --- Amendment 5: the enumeration miss --------------------------------------


def test_amendment_5_registers_the_measured_miss_with_both_routes() -> None:
    assert registry.ENUMERATION_MISS_LOW == 0.278
    assert registry.ENUMERATION_MISS_HIGH == 0.347
    assert registry.ENUMERATION_COVERAGE == 0.704
    assert "a miss rate of 28 to 35 percent" in DOC
    assert "The two routes agree within 10.6%" in DOC
    assert "**401 of 884 = 45.4%**" in DOC


def test_amendment_5_registers_the_estimate_as_a_lower_bound() -> None:
    """A bound quoted bare as a point estimate is the failure this prevents."""
    assert "LOWER BOUND on both routes" in DOC
    assert "Both routes therefore err in the same direction, toward **under**-stating" in DOC


def test_amendment_5_registers_the_non_uniformity() -> None:
    """Uniform thinning costs power; non-uniform thinning damages the claim."""
    assert registry.MISS_RATE_QUIETEST_HOUR == 0.087
    assert registry.MISS_RATE_BUSIEST_HOUR == 0.650
    assert registry.MISS_BURST_QUINTILE_RATIO == 8.3
    assert "8.7% at 07:00 UTC to 65.0% at 16:00 UTC" in DOC
    assert "8.3× the missed births of the slowest" in DOC


def test_amendment_5_registers_where_the_miss_falls() -> None:
    """The within-sweep share bounds what a cadence change can fix."""
    assert registry.MISS_SHARE_BETWEEN_SWEEPS == 0.754
    assert registry.MISS_SHARE_WITHIN_SWEEP == 0.246
    assert round(registry.MISS_SHARE_BETWEEN_SWEEPS + registry.MISS_SHARE_WITHIN_SWEEP, 3) == 1.0
    assert "skips across pages as well as duplicating" in DOC


def test_amendment_5_registers_the_bias_direction_toward_the_null() -> None:
    """Registered before any outcome, so it cannot be produced afterwards."""
    assert "Pools born during bursts are systematically less likely to be enumerated" in DOC
    assert "biases the measured association toward the null" in DOC
    assert "a positive result is not inflated by this weakness" in DOC
    # It must NOT be mistaken for attention-driven selection.
    assert "this is not attention-driven selection" in DOC


def test_amendment_5_registers_the_per_result_reporting_requirement() -> None:
    assert "A result that omits these is not reportable" in DOC
    assert "alongside the survivorship audit §5 already requires" in DOC


def test_amendment_5_did_not_move_the_grid_or_any_other_bar() -> None:
    """The whole point: the instrument described honestly without touching a bar."""
    assert registry.TRIAL_GRID_SIZE == 160
    assert round(registry.SIDAK_ALPHA, 6) == 0.000321
    assert registry.PRIMARY_TRIAL == (7, "v24", "mint-exact", "bluesky")
    assert registry.DEATH_LOOKBACK_DAYS == 14
    assert registry.COST_BPS_CENTRAL == 450
    assert registry.ENTRY_OFFSET_DAYS == 2
    assert registry.CHANNEL_LIST_SIZE == 20
    assert len(registry.LAUNCHPAD_DEXES) == 16  # meteora-dbc was NOT added
    assert "this amendment adds no trial" in DOC
    assert DOC.index("Amendment 5") > DOC.index("Amendment 4")
