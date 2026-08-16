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


def test_rate_disagreement_is_flagged_not_averaged(tmp_path: Path) -> None:
    # Arrange - one amm birth against a registered expectation of ~1,330
    manifest.append_births(tmp_path, parse_new_pools(FEED, "u", "2026-08-16T12:00:00Z"))
    # Act
    counts = manifest.day_counts(tmp_path, "2026-08-16")
    # Assert
    assert counts["amm"] == 1
    assert counts["launchpad"] == 1
    assert counts["disagreement"] == 1
    assert counts["expected_amm"] == registry.EXPECTED_AMM_POOLS_PER_DAY


def test_saturation_flag_fires_above_the_registered_threshold(tmp_path: Path) -> None:
    births = [
        PoolBirth(
            f"Mint{i}",
            f"Pool{i}",
            "pumpswap",
            registry.VENUE_CLASS_AMM,
            "X",
            "Xx",
            "2026-08-16T10:00:00Z",
            "2026-08-16",
            "geckoterminal",
            "u",
            "2026-08-16T12:00:00Z",
        )
        for i in range(registry.SATURATION_AMM_PER_DAY + 1)
    ]
    manifest.append_births(tmp_path, births)
    assert manifest.day_counts(tmp_path, "2026-08-16")["saturated"] == 1
