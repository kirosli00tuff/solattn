"""Enumeration: venue tagging, manifests, and the registered rate check."""

from __future__ import annotations

from pathlib import Path

from solattn import registry
from solattn.records import PoolBirth
from solattn.sources.geckoterminal import classify_venue, parse_new_pools
from solattn.universe import manifest

FEED = {
    "data": [
        {
            "attributes": {
                "address": "PoolAAA",
                "pool_created_at": "2026-08-16T10:00:00Z",
                "name": "AAA / SOL",
            },
            "relationships": {
                "base_token": {"data": {"id": "solana_MintAAA"}},
                "dex": {"data": {"id": "pumpswap"}},
            },
        },
        {
            "attributes": {
                "address": "PoolBBB",
                "pool_created_at": "2026-08-16T11:00:00Z",
                "name": "BBB / SOL",
            },
            "relationships": {
                "base_token": {"data": {"id": "solana_MintBBB"}},
                "dex": {"data": {"id": "pumpfun"}},
            },
        },
        {"attributes": {"address": "PoolCCC"}, "relationships": {}},
    ],
    "included": [
        {"id": "solana_MintAAA", "type": "token", "attributes": {"symbol": "AAA", "name": "Alpha"}}
    ],
}


def test_denylist_fails_open_for_a_new_amm() -> None:
    """An unknown dex classifies as amm, so a new venue is never silently dropped."""
    assert classify_venue("pumpfun") == registry.VENUE_CLASS_LAUNCHPAD
    assert classify_venue("PumpFun") == registry.VENUE_CLASS_LAUNCHPAD
    assert classify_venue("brand-new-amm") == registry.VENUE_CLASS_AMM


def test_parse_tags_venue_and_drops_incomplete_rows_visibly() -> None:
    births = parse_new_pools(FEED, "http://example/feed", "2026-08-16T12:00:00Z")
    assert len(births) == 2  # the third row lacks the registered fields
    assert births[0].venue_class == registry.VENUE_CLASS_AMM
    assert births[0].symbol == "AAA"
    assert births[1].venue_class == registry.VENUE_CLASS_LAUNCHPAD
    assert births[0].manifest_day == "2026-08-16"


def test_nothing_is_discarded_at_collection_time(tmp_path: Path) -> None:
    """Both venue classes reach the manifest; filtering happens at analysis."""
    births = parse_new_pools(FEED, "u", "2026-08-16T12:00:00Z")
    manifest.append_births(tmp_path, births)
    stored = manifest.read_day(tmp_path, "2026-08-16")
    assert {b.venue_class for b in stored} == {
        registry.VENUE_CLASS_AMM,
        registry.VENUE_CLASS_LAUNCHPAD,
    }


def test_manifest_dedupes_by_pool_on_read(tmp_path: Path) -> None:
    """Concurrent watchers can double-append; the read resolves it."""
    births = parse_new_pools(FEED, "u", "2026-08-16T12:00:00Z")
    manifest.append_births(tmp_path, births)
    manifest.append_births(tmp_path, births)
    assert len(manifest.read_day(tmp_path, "2026-08-16")) == 2


def test_rate_check_reports_insufficient_rather_than_defaulting_to_fine(tmp_path: Path) -> None:
    """An undecidable check must say so, not silently read as agreement."""
    manifest.append_births(tmp_path, parse_new_pools(FEED, "u", "2026-08-16T12:00:00Z"))
    counts = manifest.day_counts(tmp_path, "2026-08-16")
    assert counts["amm"] == 1
    assert counts["launchpad"] == 1
    assert counts["basis"] == "insufficient"
    assert counts["disagreement"] == 0
    assert counts["saturated"] == 0


def amm_births(count: int, span_minutes: int) -> list[PoolBirth]:
    from datetime import UTC, datetime, timedelta

    start = datetime(2026, 8, 16, 0, 0, tzinfo=UTC)
    step = timedelta(minutes=span_minutes) / max(count - 1, 1)
    return [
        PoolBirth(
            f"Mint{i}",
            f"Pool{i}",
            "pumpswap",
            registry.VENUE_CLASS_AMM,
            "X",
            "Xxxx",
            (start + step * i).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "2026-08-16",
            "geckoterminal",
            "u",
            "2026-08-16T12:00:00Z",
        )
        for i in range(count)
    ]


def test_partial_day_is_judged_on_rate_not_on_a_part_day_count(tmp_path: Path) -> None:
    """40 births in 30 minutes is ~1,872/day - agreement, though the count is 40."""
    manifest.append_births(tmp_path, amm_births(40, 30))
    counts = manifest.day_counts(tmp_path, "2026-08-16")
    assert counts["basis"] == "rate"
    assert 1_700 < counts["measured_amm_per_day"] < 2_000
    assert counts["disagreement"] == 0


def test_rate_disagreement_is_flagged_not_averaged(tmp_path: Path) -> None:
    # Arrange - 300 births in 30 minutes is ~14,000/day against a registered ~1,330
    manifest.append_births(tmp_path, amm_births(300, 30))
    # Act
    counts = manifest.day_counts(tmp_path, "2026-08-16")
    # Assert
    assert counts["basis"] == "rate"
    assert counts["amm_vs_expected_ratio"] > registry.RATE_DISAGREEMENT_FACTOR
    assert counts["disagreement"] == 1


def test_saturation_fires_on_the_measured_rate(tmp_path: Path) -> None:
    """The registered threshold is a rate, so it can trip before the day closes."""
    manifest.append_births(tmp_path, amm_births(300, 30))
    assert manifest.day_counts(tmp_path, "2026-08-16")["saturated"] == 1


def test_closed_day_is_judged_on_its_count(tmp_path: Path) -> None:
    manifest.append_births(tmp_path, amm_births(40, 30))
    counts = manifest.day_counts(tmp_path, "2026-08-16", day_is_complete=True)
    assert counts["basis"] == "count"
    assert counts["measured_amm_per_day"] == 40.0
    assert counts["disagreement"] == 1  # 40 against a registered ~1,330 is a real gap
