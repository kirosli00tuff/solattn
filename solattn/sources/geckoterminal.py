"""GeckoTerminal: the keyless new-pools feed and the daily OHLCV endpoint.

This is the enumeration source (REGISTRATION.md 1) and the outcome source
(REGISTRATION.md 4). It carries **no attention input of any kind**: the feed is
ordered by pool creation, and membership is decided by birth and nothing else.

Pacing is measured, not documented (ADR-003).
"""

from __future__ import annotations

from typing import Any

from solattn import registry
from solattn.clock import Clock, day_str, iso, parse_iso, utc_date
from solattn.http import PacedClient
from solattn.records import AccessResult, Candle, PoolBirth

SOURCE = registry.SOURCE_GECKOTERMINAL


def classify_venue(dex_id: str) -> str:
    """Tag a pool's venue class from the registered launch-venue denylist.

    A denylist, not an allowlist (ADR-002): an AMM appearing mid-collection is
    included automatically, where an allowlist would silently drop it.
    """
    return (
        registry.VENUE_CLASS_LAUNCHPAD
        if dex_id.lower() in registry.LAUNCHPAD_DEXES
        else registry.VENUE_CLASS_AMM
    )


def _token_index(included: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item.get("attributes", {}) for item in included if item.get("type") == "token"
    }


def parse_new_pools(body: Any, source_url: str, retrieved_at: str) -> list[PoolBirth]:
    """Parse a new-pools page into birth records.

    A row missing the fields the registration depends on (pool address, base
    mint, creation time) is DROPPED and the drop is visible in the count — it
    is never patched with a guess, and never given a fabricated timestamp.
    """
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    if not isinstance(data, list):
        return []
    tokens = _token_index(body.get("included") or [])

    births: list[PoolBirth] = []
    for row in data:
        attributes = row.get("attributes") or {}
        relationships = row.get("relationships") or {}
        pool = attributes.get("address")
        created = attributes.get("pool_created_at")
        base = ((relationships.get("base_token") or {}).get("data") or {}).get("id")
        dex = ((relationships.get("dex") or {}).get("data") or {}).get("id")
        if not (pool and created and base and dex):
            continue
        mint = base.split("_", 1)[1] if "_" in base else base
        token_attributes = tokens.get(base, {})
        births.append(
            PoolBirth(
                mint=mint,
                pool=str(pool),
                dex=str(dex),
                venue_class=classify_venue(str(dex)),
                symbol=str(token_attributes.get("symbol") or ""),
                name=str(token_attributes.get("name") or attributes.get("name") or ""),
                pool_created_at=iso(parse_iso(str(created))),
                manifest_day=day_str(utc_date(parse_iso(str(created)))),
                source=SOURCE,
                source_url=source_url,
                retrieved_at=retrieved_at,
            )
        )
    return births


def fetch_new_pools(client: PacedClient, clock: Clock, page: int = 1) -> list[PoolBirth] | None:
    """Fetch one page of the birth-ordered new-pools feed.

    Returns ``None`` when the source was unavailable (non-2xx or transport
    error) and ``[]`` when it answered 2xx with no rows. **The two are
    different facts** and the caller must not conflate them: an empty list is
    the end of the feed, whereas ``None`` is no answer at all.

    This is ADR-012's absent-data versus measured-absence split, applied to the
    enumeration path. Returning ``[]`` on a 429 let the rate limiter read as
    "the feed ends here", which truncated a sweep silently — no refusal marker,
    no error marker, and a shorter read recorded as a complete one (ADR-017).
    """
    url = registry.GECKOTERMINAL_BASE + registry.NEW_POOLS_PATH
    response = client.get(
        SOURCE,
        url,
        params={"include": "base_token,dex", "page": page},
        note=f"new_pools page={page}",
    )
    if not response.ok:
        return None
    return parse_new_pools(response.json_body, response.url, iso(clock.now()))


def parse_ohlcv(body: Any, pool: str, retrieved_at: str) -> list[Candle]:
    """Parse the daily OHLCV payload into candles, one per UTC day."""
    if not isinstance(body, dict):
        return []
    attributes = ((body.get("data") or {}).get("attributes")) or {}
    rows = attributes.get("ohlcv_list")
    if not isinstance(rows, list):
        return []
    candles: list[Candle] = []
    from datetime import UTC, datetime

    for row in rows:
        if not isinstance(row, list) or len(row) < 6:
            continue
        stamp, opened, high, low, close, volume = row[:6]
        candles.append(
            Candle(
                pool=pool,
                day=day_str(datetime.fromtimestamp(int(stamp), UTC).date()),
                open=float(opened or 0.0),
                high=float(high or 0.0),
                low=float(low or 0.0),
                close=float(close or 0.0),
                volume=float(volume or 0.0),
                retrieved_at=retrieved_at,
            )
        )
    return candles


def fetch_daily_candles(
    client: PacedClient, clock: Clock, pool: str, limit: int = 100
) -> list[Candle] | None:
    """Fetch daily candles for one pool at a horizon checkpoint.

    One call returns a long history, which is why a pool needs only two calls
    across its whole life (REGISTRATION.md 7).

    Returns ``None`` when the source was unavailable (non-2xx or transport
    error) and ``[]`` when the source answered 2xx with no candles. The two are
    different facts — ADR-012's absent-data versus measured-absence split — and
    conflating them let a transient 429 at checkpoint time read as "this pool
    has no candles", which the checkpoint would then have recorded as done and
    never retried (the A.3 KAT finding).
    """
    url = registry.GECKOTERMINAL_BASE + registry.OHLCV_PATH_TEMPLATE.format(pool=pool)
    response = client.get(
        SOURCE, url, params={"aggregate": 1, "limit": limit}, note=f"ohlcv {pool}"
    )
    if not response.ok:
        return None
    return parse_ohlcv(response.json_body, pool, iso(clock.now()))


def verify(client: PacedClient, clock: Clock) -> list[AccessResult]:
    """Measure reachability, cadence, and limits. Measured, not documented."""
    results: list[AccessResult] = []
    url = registry.GECKOTERMINAL_BASE + registry.NEW_POOLS_PATH

    response = client.get(SOURCE, url, params={"include": "base_token,dex"}, note="verify")
    births = (
        parse_new_pools(response.json_body, response.url, iso(clock.now())) if response.ok else []
    )
    amm = [b for b in births if b.venue_class == registry.VENUE_CLASS_AMM]
    results.append(
        AccessResult(
            source=SOURCE,
            endpoint="GET /networks/solana/new_pools",
            reachable=response.ok,
            measured_rate=f"{len(births)} pools/page in {response.elapsed_s:.2f}s",
            measured_limit=(
                f"paced at {registry.GECKOTERMINAL_MIN_SPACING_S:.1f}s; "
                f"daily cap {registry.GECKOTERMINAL_DAILY_CAP}"
            ),
            cost="keyless, free",
            detail=(
                f"HTTP {response.status}; {len(amm)} of {len(births)} tagged amm"
                if response.ok
                else f"HTTP {response.status}: {response.text[:200]}"
            ),
            measured_at=iso(clock.now()),
        )
    )

    if births:
        probe = births[0]
        candles = fetch_daily_candles(client, clock, probe.pool, limit=10) or []
        results.append(
            AccessResult(
                source=SOURCE,
                endpoint="GET /networks/solana/pools/{pool}/ohlcv/day",
                reachable=bool(candles),
                measured_rate=f"{len(candles)} daily candles in one call",
                measured_limit="one call per pool per checkpoint; 2 calls per pool lifetime",
                cost="keyless, free",
                detail=f"probed pool {probe.pool[:12]}... ({probe.venue_class})",
                measured_at=iso(clock.now()),
            )
        )
    return results
