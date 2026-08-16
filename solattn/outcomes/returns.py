"""The death floor and net-return arithmetic (REGISTRATION.md 4).

Ported from solclear ADR-013 and ADR-014. **A dust close has no exit liquidity,
and marking to it manufactures an unrealizable recovery**, so a death books
exactly -100% and dead pools stay in their cohort.

The cost band is applied to a hypothetical, to ask whether a measured lift
would survive costs. **Nothing in this repository executes anything.**
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from solattn import registry
from solattn.clock import add_days, day_str
from solattn.records import Candle


@dataclass(frozen=True)
class Outcome:
    """One pool's measured outcome at one horizon."""

    mint: str
    pool: str
    horizon_days: int
    entry_day: str
    exit_day: str
    entry_close: float | None
    exit_close: float | None
    dead: bool
    death_reason: str
    gross_return: float | None
    net_return: float | None

    @property
    def measurable(self) -> bool:
        """False when no entry mark exists — the pool cannot be measured at all."""
        return self.entry_close is not None


def entry_date(born_on: date) -> date:
    """d0 + 2, the first daily candle opening strictly after the attention window."""
    return add_days(born_on, registry.ENTRY_OFFSET_DAYS)


def exit_date(born_on: date, horizon_days: int) -> date:
    return add_days(born_on, registry.ENTRY_OFFSET_DAYS + horizon_days)


def _by_day(candles: list[Candle]) -> dict[str, Candle]:
    return {c.day: c for c in candles}


def has_volume_in_lookback(candles: list[Candle], exit_on: date) -> bool:
    """True when any candle in the 14 days ending at the exit date traded."""
    floor = exit_on - timedelta(days=registry.DEATH_LOOKBACK_DAYS)
    for candle in candles:
        if floor <= date.fromisoformat(candle.day) <= exit_on and candle.volume > 0:
            return True
    return False


def net_of_cost(gross: float, cost_bps: int) -> float:
    """Charge half the round trip on each leg. A death nets exactly -100%."""
    if gross <= registry.DEATH_RETURN:
        return registry.DEATH_RETURN
    leg = (cost_bps / 2) / 10_000.0
    net = (1.0 + gross) * (1.0 - leg) * (1.0 - leg) - 1.0
    return max(net, registry.DEATH_RETURN)


def measure(
    mint: str,
    pool: str,
    born_on: date,
    horizon_days: int,
    candles: list[Candle],
    cost_bps: int = registry.COST_BPS_CENTRAL,
) -> Outcome:
    """Measure one pool at one horizon under the registered rules."""
    entry_on = entry_date(born_on)
    exit_on = exit_date(born_on, horizon_days)
    indexed = _by_day(candles)
    entry = indexed.get(day_str(entry_on))
    exit_candle = indexed.get(day_str(exit_on))

    if entry is None or entry.close <= 0:
        return Outcome(
            mint,
            pool,
            horizon_days,
            day_str(entry_on),
            day_str(exit_on),
            None,
            None,
            False,
            "no_entry_mark",
            None,
            None,
        )

    if not has_volume_in_lookback(candles, exit_on):
        return Outcome(
            mint,
            pool,
            horizon_days,
            day_str(entry_on),
            day_str(exit_on),
            entry.close,
            exit_candle.close if exit_candle else None,
            True,
            "no_volume_in_lookback",
            registry.DEATH_RETURN,
            registry.DEATH_RETURN,
        )

    if exit_candle is None:
        return Outcome(
            mint,
            pool,
            horizon_days,
            day_str(entry_on),
            day_str(exit_on),
            entry.close,
            None,
            True,
            "no_exit_candle",
            registry.DEATH_RETURN,
            registry.DEATH_RETURN,
        )

    if exit_candle.close < entry.close * registry.DEATH_DUST_FRACTION:
        return Outcome(
            mint,
            pool,
            horizon_days,
            day_str(entry_on),
            day_str(exit_on),
            entry.close,
            exit_candle.close,
            True,
            "dust_close",
            registry.DEATH_RETURN,
            registry.DEATH_RETURN,
        )

    gross = (exit_candle.close / entry.close) - 1.0
    return Outcome(
        mint,
        pool,
        horizon_days,
        day_str(entry_on),
        day_str(exit_on),
        entry.close,
        exit_candle.close,
        False,
        "",
        gross,
        net_of_cost(gross, cost_bps),
    )


def death_rate(outcomes: list[Outcome]) -> tuple[int, float]:
    """(n measurable, death share). A rate with a hidden n is not a result."""
    measurable = [o for o in outcomes if o.measurable]
    if not measurable:
        return (0, 0.0)
    return (len(measurable), sum(1 for o in measurable if o.dead) / len(measurable))
