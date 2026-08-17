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


def last_close_at_or_before(candles: list[Candle], day: date) -> Candle | None:
    """The most recent candle at or before ``day``.

    Used only by the ``carry_forward`` ROBUSTNESS reading (Amendment 3). It is
    never consulted by the primary rule.
    """
    eligible = [c for c in candles if date.fromisoformat(c.day) <= day]
    if not eligible:
        return None
    return max(eligible, key=lambda c: c.day)


def measure(
    mint: str,
    pool: str,
    born_on: date,
    horizon_days: int,
    candles: list[Candle],
    cost_bps: int = registry.COST_BPS_CENTRAL,
    exit_rule: str = registry.EXIT_RULE_PRIMARY,
) -> Outcome:
    """Measure one pool at one horizon under the registered rules.

    ``exit_rule`` selects the exit-mark reading. ``primary`` is the registered
    rule and the only one any headline may use: a missing exit-day candle books
    a total loss (``DEAD:no_exit_candle``), because a missing daily candle means
    no trades that day and no trades at exit means no exit liquidity.
    ``carry_forward`` is the registered ROBUSTNESS reading - it marks to the
    last available close instead - and is reported alongside, never selected
    over, the primary (Amendment 3).
    """
    if exit_rule not in registry.EXIT_RULES:
        raise ValueError(
            f"{exit_rule!r} is not a registered exit rule; Amendment 3 fixes "
            f"{registry.EXIT_RULES} and the grid may not grow."
        )
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
            registry.DEATH_NO_VOLUME,
            registry.DEATH_RETURN,
            registry.DEATH_RETURN,
        )

    if exit_candle is None:
        # Amendment 3, registered: a missing exit-day candle means no trades on
        # the exit day, therefore no exit liquidity, therefore a total loss.
        # Named distinctly so results partition by which condition fired.
        if exit_rule == registry.EXIT_RULE_CARRY_FORWARD:
            carried = last_close_at_or_before(candles, exit_on)
            if carried is not None and carried.close >= entry.close * registry.DEATH_DUST_FRACTION:
                gross = (carried.close / entry.close) - 1.0
                return Outcome(
                    mint,
                    pool,
                    horizon_days,
                    day_str(entry_on),
                    day_str(exit_on),
                    entry.close,
                    carried.close,
                    False,
                    "",
                    gross,
                    net_of_cost(gross, cost_bps),
                )
        return Outcome(
            mint,
            pool,
            horizon_days,
            day_str(entry_on),
            day_str(exit_on),
            entry.close,
            None,
            True,
            registry.DEATH_NO_EXIT_CANDLE,
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
            registry.DEATH_DUST,
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


def death_reason_rates(outcomes: list[Outcome]) -> dict[str, float]:
    """Share of measurable outcomes booked by each registered death condition.

    Partitioning deaths by condition is what makes the Amendment 3 mitigation
    checkable: ``no_exit_candle`` firing at different rates across attention
    strata would bias the comparison, so the rate is reported rather than
    absorbed into the returns.
    """
    measurable = [o for o in outcomes if o.measurable]
    if not measurable:
        return dict.fromkeys(registry.DEATH_REASONS, 0.0)
    return {
        reason: sum(1 for o in measurable if o.death_reason == reason) / len(measurable)
        for reason in registry.DEATH_REASONS
    }


def no_exit_candle_rate_by_stratum(
    outcomes_by_stratum: dict[str, list[Outcome]],
) -> dict[str, dict[str, float]]:
    """Per-attention-stratum ``no_exit_candle`` firing rate — a Stage B output.

    REQUIRED by Amendment 3 as a first-class result, not a diagnostic: the rule
    biases toward the hypothesis if higher-attention pools trade more often and
    so hit it less, and **a large differential is itself a finding about the
    instrument**. Reported with its n, because a rate with a hidden n is not a
    result.
    """
    out: dict[str, dict[str, float]] = {}
    for stratum, outcomes in outcomes_by_stratum.items():
        measurable = [o for o in outcomes if o.measurable]
        fired = sum(1 for o in measurable if o.death_reason == registry.DEATH_NO_EXIT_CANDLE)
        out[stratum] = {
            "n": float(len(measurable)),
            "no_exit_candle_rate": (fired / len(measurable)) if measurable else 0.0,
        }
    return out
