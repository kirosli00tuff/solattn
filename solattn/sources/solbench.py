"""The SOL benchmark leg, from a keyless daily source.

Every outcome figure is reported against holding SOL over the identical span
(REGISTRATION.md 4). The benchmark carries no memecoin execution cost.

Candidate sources are PROBED in order; the first that serves daily closes over
the required span is used, and its identity is recorded with every figure it
produces. Nothing is assumed reachable.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from solattn import registry
from solattn.clock import Clock, day_str, iso
from solattn.http import PacedClient
from solattn.records import AccessResult, Candle

SOURCE = registry.SOURCE_BENCHMARK
BENCH_POOL = "SOL-USD"


def _from_coinbase(body: Any, retrieved_at: str) -> list[Candle]:
    """Coinbase Exchange public candles: [time, low, high, open, close, volume]."""
    if not isinstance(body, list):
        return []
    candles: list[Candle] = []
    for row in body:
        if not isinstance(row, list) or len(row) < 6:
            continue
        stamp, low, high, opened, close, volume = row[:6]
        candles.append(
            Candle(
                pool=BENCH_POOL,
                day=day_str(datetime.fromtimestamp(int(stamp), UTC).date()),
                open=float(opened),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=float(volume),
                retrieved_at=retrieved_at,
            )
        )
    return sorted(candles, key=lambda c: c.day)


def _from_coingecko(body: Any, retrieved_at: str) -> list[Candle]:
    """CoinGecko market_chart: {"prices": [[ms, price], ...]} — close only."""
    if not isinstance(body, dict):
        return []
    prices = body.get("prices")
    if not isinstance(prices, list):
        return []
    by_day: dict[str, float] = {}
    for row in prices:
        if not isinstance(row, list) or len(row) < 2:
            continue
        day = day_str(datetime.fromtimestamp(int(row[0]) / 1000, UTC).date())
        by_day[day] = float(row[1])
    return [
        Candle(
            pool=BENCH_POOL,
            day=day,
            open=price,
            high=price,
            low=price,
            close=price,
            volume=0.0,
            retrieved_at=retrieved_at,
        )
        for day, price in sorted(by_day.items())
    ]


#: (label, url, params, parser) probed in order.
CANDIDATES: tuple[tuple[str, str, dict[str, Any], str], ...] = (
    (
        "coinbase",
        "https://api.exchange.coinbase.com/products/SOL-USD/candles",
        {"granularity": 86400},
        "coinbase",
    ),
    (
        "coingecko",
        "https://api.coingecko.com/api/v3/coins/solana/market_chart",
        {"vs_currency": "usd", "days": 90, "interval": "daily"},
        "coingecko",
    ),
)


def fetch(client: PacedClient, clock: Clock) -> tuple[str, list[Candle]]:
    """Fetch the SOL daily series from the first candidate that serves it."""
    retrieved_at = iso(clock.now())
    for label, url, params, parser in CANDIDATES:
        response = client.get(SOURCE, url, params=params, note=f"sol benchmark {label}")
        if not response.ok:
            continue
        candles = (
            _from_coinbase(response.json_body, retrieved_at)
            if parser == "coinbase"
            else _from_coingecko(response.json_body, retrieved_at)
        )
        if candles:
            return (label, candles)
    return ("", [])


def verify(client: PacedClient, clock: Clock) -> list[AccessResult]:
    """Measure which keyless daily SOL source is actually serving today."""
    results: list[AccessResult] = []
    for label, url, params, parser in CANDIDATES:
        response = client.get(SOURCE, url, params=params, note=f"verify {label}")
        candles = (
            (
                _from_coinbase(response.json_body, iso(clock.now()))
                if parser == "coinbase"
                else _from_coingecko(response.json_body, iso(clock.now()))
            )
            if response.ok
            else []
        )
        span = f"{candles[0].day} .. {candles[-1].day}" if candles else "none"
        results.append(
            AccessResult(
                source=SOURCE,
                endpoint=f"{label}: GET {url.split('//', 1)[1].split('/', 1)[1]}",
                reachable=bool(candles),
                measured_rate=f"{len(candles)} daily closes in {response.elapsed_s:.2f}s",
                measured_limit=f"keyless; self-imposed cap {registry.DAILY_CAPS[SOURCE]}/day",
                cost="keyless, free",
                detail=f"HTTP {response.status}; span {span}",
                measured_at=iso(clock.now()),
            )
        )
        if candles:
            break
    return results
