"""A rate-limited page must refuse loudly, never read as the end of the feed.

`fetch_new_pools` returned `[]` on any non-2xx, and `sweep_once` treated a
falsy page as end-of-feed, so a 429 truncated the sweep with no refusal and no
error marker — the same absent-data versus measured-absence shape ADR-012 fixed
on the OHLCV path, still live on enumeration (ADR-017).

A.5 measured the cost of the blindness rather than of the bug itself: 887 of
887 collected sweeps read all four pages, so the defect never fired, but the
ledger recorded 429s and 200s identically and could not have shown it if it
had.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from solattn import jsonl, registry
from solattn.clock import FixedClock
from solattn.config import Settings
from solattn.http import Response
from solattn.ledger import KIND_SETTLE, Ledger
from solattn.sources import geckoterminal
from solattn.universe import manifest, watcher

NOW = datetime(2026, 8, 18, 12, 0, tzinfo=UTC)


def page(pool_suffix: str, created: str) -> dict[str, Any]:
    return {
        "attributes": {"address": f"Pool{pool_suffix}", "pool_created_at": created},
        "relationships": {
            "base_token": {"data": {"id": f"solana_Mint{pool_suffix}"}},
            "dex": {"data": {"id": "pumpswap"}},
        },
    }


def response(status: int, body: Any) -> Response:
    return Response(status=status, elapsed_s=0.01, url="u", json_body=body, text="rate limited")


class ScriptedClient:
    """Answers each successive page from a script of Responses."""

    def __init__(self, script: list[Response]) -> None:
        self.script = script
        self.calls = 0

    def get(self, source: str, url: str, params: Any = None, note: str = "") -> Response:
        answer = self.script[min(self.calls, len(self.script) - 1)]
        self.calls += 1
        return answer


@pytest.fixture
def env(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path, None, None, "s", dict(registry.DAILY_CAPS))
    for directory in (
        settings.manifests_dir(),
        settings.outcomes_dir(),
        settings.vendor_dir(),
        settings.state_dir(),
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return settings


def markers(settings: Settings, marker: str) -> list[dict[str, Any]]:
    rows = jsonl.read(settings.state_dir() / "lifecycle.jsonl")
    return [r for r in rows if r.get("marker") == marker]


# --- the fetch layer: unavailable is not empty -------------------------------


def test_a_rate_limited_page_is_unavailable_not_empty() -> None:
    """429/5xx/transport is NOT an answer, so it cannot mean 'no pools'."""
    clock = FixedClock(NOW)
    for status in (429, 500, 503, 0):
        client = ScriptedClient([response(status, None)])
        assert geckoterminal.fetch_new_pools(client, clock, 1) is None  # type: ignore[arg-type]


def test_a_2xx_page_with_no_rows_is_an_answer() -> None:
    """A served empty page IS the end of the feed: measured absence."""
    clock = FixedClock(NOW)
    client = ScriptedClient([response(200, {"data": []})])
    assert geckoterminal.fetch_new_pools(client, clock, 1) == []  # type: ignore[arg-type]


# --- the sweep layer: truncation is counted, not absorbed --------------------


def test_429_during_paging_does_not_read_as_end_of_feed(env: Settings) -> None:
    """The distinguishing test: same falsy page, two different meanings."""
    # Arrange: page 1 serves two births, page 2 is rate limited.
    clock = FixedClock(NOW)
    client = ScriptedClient(
        [
            response(200, {"data": [page("AAA", "2026-08-18T10:00:00Z")]}),
            response(429, None),
        ]
    )

    # Act
    summary = watcher.sweep_once(client, clock, env)  # type: ignore[arg-type]

    # Assert: the sweep stopped short and SAYS so.
    assert summary["truncated"] == 1
    assert summary["pages_unavailable"] == 1
    assert summary["pages_read"] == 1  # the 429 page was never read
    assert summary["pools_seen"] == 1

    errors = markers(env, "error")
    assert len(errors) == 1
    assert "TRUNCATED" in errors[0]["detail"]
    assert "not end-of-feed" in errors[0]["detail"]
    assert errors[0]["page"] == 2


def test_an_answered_empty_page_reads_as_end_of_feed(env: Settings) -> None:
    """The other branch: a served empty page ends the sweep with NO error."""
    clock = FixedClock(NOW)
    client = ScriptedClient(
        [
            response(200, {"data": [page("AAA", "2026-08-18T10:00:00Z")]}),
            response(200, {"data": []}),
        ]
    )

    summary = watcher.sweep_once(client, clock, env)  # type: ignore[arg-type]

    assert summary["truncated"] == 0
    assert summary["pages_unavailable"] == 0
    assert summary["pages_read"] == 2  # the empty page WAS read; it just had nothing
    assert summary["pools_seen"] == 1
    assert markers(env, "error") == []


def test_a_truncated_sweep_is_visible_in_the_lifecycle_log(env: Settings) -> None:
    """A retrospective must be able to find truncated sweeps without a re-probe."""
    clock = FixedClock(NOW)
    client = ScriptedClient([response(429, None)])
    watcher.sweep_once(client, clock, env)  # type: ignore[arg-type]

    beats = markers(env, "heartbeat")
    assert len(beats) == 1
    assert beats[0]["truncated"] == 1
    assert beats[0]["pages_read"] == 0
    assert beats[0]["pools_seen"] == 0
    assert markers(env, "error")[0]["page"] == 1


def test_a_truncated_sweep_still_writes_what_it_did_read(env: Settings) -> None:
    """Refusing loudly must not throw away the pages that WERE served."""
    clock = FixedClock(NOW)
    client = ScriptedClient(
        [
            response(200, {"data": [page("AAA", "2026-08-18T10:00:00Z")]}),
            response(429, None),
        ]
    )
    watcher.sweep_once(client, clock, env)  # type: ignore[arg-type]

    births = manifest.read_day(env.manifests_dir(), "2026-08-18")
    assert [b.pool for b in births] == ["PoolAAA"]


# --- the ledger: a served request is distinguishable from a refused one ------


def test_the_ledger_records_the_status_without_moving_the_cap(tmp_path: Path) -> None:
    """Settle rows carry count 0, so recording a status can never move a cap."""
    ledger = Ledger(tmp_path / "requests.jsonl", {"geckoterminal": 10}, FixedClock(NOW))
    ledger.charge("geckoterminal", 1, "page=1")
    ledger.settle("geckoterminal", 200, "page=1")
    ledger.charge("geckoterminal", 1, "page=2")
    ledger.settle("geckoterminal", 429, "page=2")

    assert ledger.spent("geckoterminal") == 2  # settles did NOT inflate the count
    assert ledger.report()["geckoterminal"] == {"spent": 2, "cap": 10, "remaining": 8}
    assert dict(ledger.statuses()["geckoterminal"]) == {200: 1, 429: 1}


def test_settle_rows_are_appended_never_edited(tmp_path: Path) -> None:
    """Append-only: the charge row is untouched and the status is a new row."""
    ledger = Ledger(tmp_path / "requests.jsonl", {"geckoterminal": 10}, FixedClock(NOW))
    ledger.charge("geckoterminal", 1, "page=1")
    ledger.settle("geckoterminal", 429, "page=1")

    rows = jsonl.read(tmp_path / "requests.jsonl")
    assert len(rows) == 2
    assert rows[0]["count"] == 1 and "status" not in rows[0]
    assert rows[1]["kind"] == KIND_SETTLE and rows[1]["status"] == 429 and rows[1]["ok"] == 0


def test_rows_written_before_the_status_change_still_count(tmp_path: Path) -> None:
    """A pre-ADR-017 row has no `kind`; it must still price against the cap."""
    path = tmp_path / "requests.jsonl"
    jsonl.append(
        path,
        {
            "at": "2026-08-18T00:00:00Z",
            "day": "2026-08-18",
            "source": "geckoterminal",
            "count": 3,
            "note": "legacy",
        },
    )
    ledger = Ledger(path, {"geckoterminal": 10}, FixedClock(NOW))
    assert ledger.spent("geckoterminal") == 3
    assert ledger.statuses() == {}  # a legacy row asserts nothing about status
