"""Immutable daily birth manifests.

One file per UTC birth day, append-only, sealed with a sha256 sidecar when the
day closes. **A sealed manifest is never rewritten**; a correction is appended
as a new record with its own retrieval time.

Deduplication is by pool address, resolved on READ rather than on write, so two
watcher processes appending concurrently cannot lose a birth to a race.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from solattn import jsonl, registry
from solattn.records import PoolBirth

#: Below these, a rate cannot be measured honestly and the check reports so.
MIN_RATE_SAMPLE = 20
MIN_RATE_SPAN_SECONDS = 600.0


def manifest_path(root: Path, day: str) -> Path:
    return root / f"births-{day}.jsonl"


def append_births(root: Path, births: list[PoolBirth]) -> dict[str, int]:
    """Append births to their birth-day manifests. Returns per-day counts written."""
    written: dict[str, int] = {}
    for birth in births:
        jsonl.append(manifest_path(root, birth.manifest_day), birth.to_row())
        written[birth.manifest_day] = written.get(birth.manifest_day, 0) + 1
    return written


def read_day(root: Path, day: str) -> list[PoolBirth]:
    """Read one day's manifest, deduplicated by pool, ordered by birth time.

    Ordered by the record's own ``pool_created_at``, never by file position:
    two processes appending to one file interleave (standing practice).
    """
    rows = jsonl.read(manifest_path(root, day), order_by="pool_created_at")
    unique: dict[str, PoolBirth] = {}
    for row in rows:
        birth = PoolBirth(**row)
        unique.setdefault(birth.pool, birth)
    return sorted(unique.values(), key=lambda b: (b.pool_created_at, b.pool))


def read_recent(root: Path, days: list[str]) -> list[PoolBirth]:
    """Read several birth days at once (used to build the active match universe)."""
    out: list[PoolBirth] = []
    for day in days:
        out.extend(read_day(root, day))
    return out


def observed_rate_per_day(births: list[PoolBirth]) -> float | None:
    """Births per day, measured over the span the births themselves cover.

    Returns None when the span is too short to extrapolate from. The
    registration compares a **rate** against ~1,330/day and trips saturation on
    a **rate**, so a partial day must be measured as a rate — comparing a
    part-day *count* against a full-day expectation would report a disagreement
    every morning and none of them would mean anything.
    """
    if len(births) < MIN_RATE_SAMPLE:
        return None
    stamps = sorted(b.pool_created_at for b in births)
    from solattn.clock import parse_iso

    span_s = (parse_iso(stamps[-1]) - parse_iso(stamps[0])).total_seconds()
    if span_s < MIN_RATE_SPAN_SECONDS:
        return None
    # n births span n-1 intervals; using n would overstate the rate on small n.
    return (len(births) - 1) / span_s * 86_400


def day_counts(root: Path, day: str, day_is_complete: bool = False) -> dict[str, Any]:
    """Per-venue-class counts for a birth day, plus the registered rate checks.

    ``basis`` records which quantity the disagreement was judged on: the day's
    full ``count`` once the day is closed, or the measured ``rate`` while it is
    still open. A day with too few births to measure a rate reports
    ``basis="insufficient"`` and asserts nothing — an undecidable check must
    say so rather than defaulting to "fine".
    """
    births = read_day(root, day)
    amm_births = [b for b in births if b.venue_class == registry.VENUE_CLASS_AMM]
    amm = len(amm_births)
    expected = registry.EXPECTED_AMM_POOLS_PER_DAY
    rate = observed_rate_per_day(amm_births)

    if day_is_complete:
        basis, measured = "count", float(amm)
    elif rate is not None:
        basis, measured = "rate", rate
    else:
        basis, measured = "insufficient", 0.0

    ratio = (measured / expected) if (expected and basis != "insufficient") else 0.0
    disagreement = basis != "insufficient" and (
        ratio > registry.RATE_DISAGREEMENT_FACTOR or ratio < 1 / registry.RATE_DISAGREEMENT_FACTOR
    )
    saturated = basis != "insufficient" and measured > registry.SATURATION_AMM_PER_DAY

    return {
        "total": len(births),
        "amm": amm,
        "launchpad": len(births) - amm,
        "expected_amm": expected,
        "basis": basis,
        "measured_amm_per_day": round(measured, 1),
        "amm_vs_expected_ratio": round(ratio, 2),
        "disagreement": int(disagreement),
        "saturated": int(saturated),
    }


def seal_day(root: Path, day: str, sealed_at: str) -> jsonl.Seal | None:
    """Seal a closed day's manifest. Returns None when the day has no manifest."""
    path = manifest_path(root, day)
    if not path.is_file():
        return None
    return jsonl.seal(path, sealed_at)
