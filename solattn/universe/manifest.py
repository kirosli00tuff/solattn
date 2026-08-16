"""Immutable daily birth manifests.

One file per UTC birth day, append-only, sealed with a sha256 sidecar when the
day closes. **A sealed manifest is never rewritten**; a correction is appended
as a new record with its own retrieval time.

Deduplication is by pool address, resolved on READ rather than on write, so two
watcher processes appending concurrently cannot lose a birth to a race.
"""

from __future__ import annotations

from pathlib import Path

from solattn import jsonl, registry
from solattn.records import PoolBirth


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


def day_counts(root: Path, day: str) -> dict[str, int]:
    """Per-venue-class counts for a birth day, plus the registered rate check."""
    births = read_day(root, day)
    amm = sum(1 for b in births if b.venue_class == registry.VENUE_CLASS_AMM)
    launchpad = len(births) - amm
    expected = registry.EXPECTED_AMM_POOLS_PER_DAY
    ratio = (amm / expected) if expected else 0.0
    return {
        "total": len(births),
        "amm": amm,
        "launchpad": launchpad,
        "expected_amm": expected,
        "amm_vs_expected_pct": int(ratio * 100),
        "disagreement": int(
            ratio > registry.RATE_DISAGREEMENT_FACTOR
            or ratio < 1 / registry.RATE_DISAGREEMENT_FACTOR
        ),
        "saturated": int(amm > registry.SATURATION_AMM_PER_DAY),
    }


def seal_day(root: Path, day: str, sealed_at: str) -> jsonl.Seal | None:
    """Seal a closed day's manifest. Returns None when the day has no manifest."""
    path = manifest_path(root, day)
    if not path.is_file():
        return None
    return jsonl.seal(path, sealed_at)
