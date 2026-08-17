"""The death floor and net-return arithmetic."""

from __future__ import annotations

from datetime import date

from solattn import registry
from solattn.outcomes.returns import (
    death_rate,
    entry_date,
    exit_date,
    measure,
    net_of_cost,
)
from solattn.records import Candle

BORN = date(2026, 8, 1)
POOL = "PooL1111111111111111111111111111111111111111"
MINT = "Mint1111111111111111111111111111111111111111"


def candle(day: date, close: float, volume: float = 1000.0) -> Candle:
    return Candle(POOL, day.isoformat(), close, close, close, close, volume, "2026-08-16T00:00:00Z")


def series(closes: dict[int, float], volume: float = 1000.0) -> list[Candle]:
    from datetime import timedelta

    return [candle(BORN + timedelta(days=d), c, volume) for d, c in closes.items()]


def test_entry_anchor_is_two_days_after_birth() -> None:
    assert entry_date(BORN) == date(2026, 8, 3)
    assert exit_date(BORN, 7) == date(2026, 8, 10)


def test_gross_and_net_on_a_live_pool() -> None:
    # Arrange - entry at 1.00 on d0+2, exit at 1.50 on d0+9
    outcome = measure(MINT, POOL, BORN, 7, series({2: 1.0, 5: 1.2, 9: 1.5}))
    # Act / Assert
    assert outcome.dead is False
    assert outcome.gross_return == 0.5
    assert outcome.net_return is not None
    # 450 bps round trip charged 225 per leg costs ~4.4% of a 1.5x
    assert 0.42 < outcome.net_return < 0.44


def test_dust_close_books_a_total_loss() -> None:
    outcome = measure(MINT, POOL, BORN, 7, series({2: 1.0, 9: 0.005}))
    assert outcome.dead is True
    assert outcome.death_reason == "dust_close"
    assert outcome.net_return == registry.DEATH_RETURN


def test_no_volume_in_the_lookback_books_a_total_loss() -> None:
    """A pool with candles but no trading in the trailing 14 days is dead."""
    outcome = measure(MINT, POOL, BORN, 7, series({2: 1.0, 9: 1.4}, volume=0.0))
    assert outcome.dead is True
    assert outcome.death_reason == "no_volume_in_lookback"
    assert outcome.net_return == registry.DEATH_RETURN


def test_missing_exit_candle_books_a_total_loss() -> None:
    outcome = measure(MINT, POOL, BORN, 7, series({2: 1.0, 3: 1.1}))
    assert outcome.dead is True
    assert outcome.net_return == registry.DEATH_RETURN


def test_no_entry_mark_is_unmeasurable_not_a_death() -> None:
    """A pool with no entry candle produces no number at all."""
    outcome = measure(MINT, POOL, BORN, 7, series({5: 1.0, 9: 2.0}))
    assert outcome.measurable is False
    assert outcome.dead is False
    assert outcome.net_return is None


def test_cost_cannot_deepen_a_total_loss() -> None:
    for band in registry.COST_BANDS:
        assert net_of_cost(registry.DEATH_RETURN, band) == registry.DEATH_RETURN


def test_cost_band_sensitivity_is_monotone() -> None:
    low = net_of_cost(1.0, registry.COST_BPS_LOW)
    mid = net_of_cost(1.0, registry.COST_BPS_CENTRAL)
    high = net_of_cost(1.0, registry.COST_BPS_HIGH)
    assert low > mid > high


def test_death_rate_reports_its_n() -> None:
    outcomes = [
        measure(MINT, POOL, BORN, 7, series({2: 1.0, 9: 0.001})),
        measure(MINT, POOL, BORN, 7, series({2: 1.0, 9: 1.5})),
        measure(MINT, POOL, BORN, 7, series({5: 1.0})),
    ]
    n, rate = death_rate(outcomes)
    assert n == 2
    assert rate == 0.5


# --- Amendment 3 ------------------------------------------------------------


def test_missing_exit_candle_books_no_exit_candle_distinctly() -> None:
    """The third condition is its own verdict, not folded into the other two."""
    # Arrange - traded on d0+2 and d0+8 (volume in lookback), nothing on d0+9
    outcome = measure(MINT, POOL, BORN, 7, series({2: 1.0, 8: 0.9}))
    # Assert
    assert outcome.dead is True
    assert outcome.death_reason == registry.DEATH_NO_EXIT_CANDLE
    assert outcome.death_reason != registry.DEATH_NO_VOLUME
    assert outcome.death_reason != registry.DEATH_DUST
    assert outcome.net_return == registry.DEATH_RETURN


def test_carry_forward_marks_to_the_last_available_close() -> None:
    """The robustness reading marks to d0+8's close instead of booking -100%."""
    candles = series({2: 1.0, 8: 0.9})
    primary = measure(MINT, POOL, BORN, 7, candles)
    alt = measure(MINT, POOL, BORN, 7, candles, exit_rule=registry.EXIT_RULE_CARRY_FORWARD)
    assert primary.net_return == registry.DEATH_RETURN
    assert alt.dead is False
    assert alt.gross_return is not None
    assert abs(alt.gross_return - (0.9 / 1.0 - 1.0)) < 1e-12


def test_carry_forward_still_honours_the_other_two_conditions() -> None:
    """Amendment 3: (a) and (b) apply unchanged under the alternative."""
    dusty = measure(
        MINT, POOL, BORN, 7, series({2: 1.0, 8: 0.001}), exit_rule=registry.EXIT_RULE_CARRY_FORWARD
    )
    assert dusty.dead is True
    silent = measure(
        MINT,
        POOL,
        BORN,
        7,
        series({2: 1.0, 8: 0.9}, volume=0.0),
        exit_rule=registry.EXIT_RULE_CARRY_FORWARD,
    )
    assert silent.dead is True
    assert silent.death_reason == registry.DEATH_NO_VOLUME


def test_an_unregistered_exit_rule_raises_rather_than_growing_the_grid() -> None:
    import pytest

    with pytest.raises(ValueError, match="not a registered exit rule"):
        measure(MINT, POOL, BORN, 7, series({2: 1.0}), exit_rule="whatever_looks_best")


def test_death_reasons_partition_and_stratum_rate_reports_its_n() -> None:
    from solattn.outcomes.returns import death_reason_rates, no_exit_candle_rate_by_stratum

    q5 = [measure(MINT, POOL, BORN, 7, series({2: 1.0, 9: 1.5}))]  # alive
    q1 = [
        measure(MINT, POOL, BORN, 7, series({2: 1.0, 8: 0.9})),  # no_exit_candle
        measure(MINT, POOL, BORN, 7, series({2: 1.0, 9: 0.001})),
    ]  # dust
    rates = death_reason_rates(q1)
    assert rates[registry.DEATH_NO_EXIT_CANDLE] == 0.5
    assert rates[registry.DEATH_DUST] == 0.5
    per = no_exit_candle_rate_by_stratum({"Q5": q5, "Q1": q1})
    assert per["Q5"]["no_exit_candle_rate"] == 0.0
    assert per["Q1"]["no_exit_candle_rate"] == 0.5
    assert per["Q1"]["n"] == 2.0  # a rate with a hidden n is not a result
