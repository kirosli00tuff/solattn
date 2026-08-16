"""Committed daily digests: counts and manifest hashes, never raw rows.

Raw collected rows are machine-local and large; the committed artifact is a
digest carrying the counts, the manifest sha256, and the registered rate check.
That keeps the repository small while making every reported number traceable to
a sealed file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from solattn import jsonl, registry
from solattn.clock import Clock, iso
from solattn.config import Settings
from solattn.matching.daily import daily_counts
from solattn.universe import manifest

DIGEST_DIR = Path("docs/digests")


def build_digest(settings: Settings, clock: Clock, day: str) -> dict[str, Any]:
    """Assemble one UTC day's digest."""
    counts = manifest.day_counts(settings.manifests_dir(), day)
    seal = manifest.seal_day(settings.manifests_dir(), day, iso(clock.now()))
    tallies = [t.to_row() for t in daily_counts(settings, day)]
    ledger_rows = jsonl.read(settings.vendor_dir() / "requests.jsonl")
    requests_today = sum(int(r.get("count", 0)) for r in ledger_rows if r.get("day") == day)
    return {
        "day": day,
        "schema": registry.SCHEMA_VERSION,
        "generated_at": iso(clock.now()),
        "enumeration": counts,
        "expected_amm_per_day": registry.EXPECTED_AMM_POOLS_PER_DAY,
        "rate_disagreement_factor": registry.RATE_DISAGREEMENT_FACTOR,
        "manifest_sha256": seal.sha256 if seal else None,
        "manifest_rows": seal.rows if seal else 0,
        "match_counts": tallies,
        "requests_today": requests_today,
        "note": (
            "Counts only. No analysis is performed or implied here; the registered "
            "maturity dates in REGISTRATION.md section 8 gate every analysis."
        ),
    }


def write_digest(settings: Settings, clock: Clock, day: str) -> Path:
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    path = DIGEST_DIR / f"{day}.json"
    path.write_text(
        json.dumps(build_digest(settings, clock, day), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
