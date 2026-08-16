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
