"""Checkpoint semantics: an unanswered fetch is retried, never marked done.

The A.3 known-answer test found that a transient 429 at checkpoint time was
recorded as "0 candles, done" and never refetched — permanent silent loss of
that pool's outcomes. These tests pin the fix.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from solattn import jsonl, registry
from solattn.clock import FixedClock
from solattn.config import Settings
from solattn.http import Response
from solattn.outcomes import checkpoints
from solattn.records import Candle, PoolBirth
from solattn.sources import geckoterminal
from solattn.universe import manifest


class StubClient:
    """Returns a scripted Response; records what was requested."""

    def __init__(self, response: Response) -> None:
        self.response = response
        self.calls: list[str] = []

    def get(self, source: str, url: str, params: Any = None, note: str = "") -> Response:
        self.calls.append(url)
        return self.response


def response(status: int, body: Any) -> Response:
    return Response(status=status, elapsed_s=0.1, url="u", json_body=body, text="")


def test_fetch_returns_none_when_the_source_is_unavailable() -> None:
    """429/5xx/transport is NOT an answer — it must not read as no-candles."""
    from datetime import UTC, datetime

    clock = FixedClock(datetime(2026, 8, 17, tzinfo=UTC))
    for status in (429, 500, 0):
        client = StubClient(response(status, None))
        assert geckoterminal.fetch_daily_candles(client, clock, "Pool") is None  # type: ignore[arg-type]


def test_fetch_returns_empty_list_on_a_2xx_with_no_candles() -> None:
    """A 200 with an empty list IS an answer: measured absence, not failure."""
    from datetime import UTC, datetime

    clock = FixedClock(datetime(2026, 8, 17, tzinfo=UTC))
    client = StubClient(response(200, {"data": {"attributes": {"ohlcv_list": []}}}))
    assert geckoterminal.fetch_daily_candles(client, clock, "Pool") == []  # type: ignore[arg-type]


@pytest.fixture
def env(tmp_path: Path) -> Settings:
    settings = Settings(tmp_path, None, None, "s", dict(registry.DAILY_CAPS))
    for d in (
        settings.manifests_dir(),
        settings.outcomes_dir(),
        settings.vendor_dir(),
        settings.state_dir(),
    ):
        d.mkdir(parents=True, exist_ok=True)
    return settings


def birth(day: str) -> PoolBirth:
    return PoolBirth(
        mint="Mint1",
        pool="Pool1",
        dex="pumpswap",
        venue_class=registry.VENUE_CLASS_AMM,
        symbol="X",
        name="Xxxx",
        pool_created_at=f"{day}T10:00:00Z",
        manifest_day=day,
        source="geckoterminal",
        source_url="u",
        retrieved_at=f"{day}T10:05:00Z",
    )


def run(env: Settings, monkeypatch: pytest.MonkeyPatch, fetched: Any) -> dict[str, Any]:
    from datetime import UTC, datetime

    clock = FixedClock(datetime(2026, 8, 17, 12, 0, tzinfo=UTC))
    # birth 10 days before "today" - due at checkpoint 10
    manifest.append_births(env.manifests_dir(), [birth("2026-08-07")])
    from solattn.sources import geckoterminal as gt_module
    from solattn.sources import solbench as bench_module

    monkeypatch.setattr(
        gt_module, "fetch_daily_candles", lambda client, clock, pool, limit=100: fetched
    )
    monkeypatch.setattr(bench_module, "fetch", lambda client, clock: ("", []))
    return checkpoints.run_checkpoints(None, clock, env)  # type: ignore[arg-type]


def test_unavailable_fetch_is_not_marked_done_and_retries(
    env: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange / Act - the source answers nothing (None)
    summary = run(env, monkeypatch, None)
    # Assert - NOT done, counted as retrying; a later pass will pick it up
    assert summary["unavailable_retrying"] == 1
    assert summary["pools_fetched"] == 0
    assert jsonl.read(env.state_dir() / "checkpoints.jsonl") == []


def test_answered_empty_is_marked_done_with_zero_candles(
    env: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = run(env, monkeypatch, [])
    done = jsonl.read(env.state_dir() / "checkpoints.jsonl")
    assert summary["unavailable_retrying"] == 0
    # only checkpoint 10 is due for a 10-day-old pool; checkpoint 33 comes later
    assert [d["candles"] for d in done] == [0]


def test_answered_candles_are_stored_and_marked_done(
    env: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    candle = Candle("Pool1", "2026-08-09", 1, 1, 1, 1.0, 10.0, "2026-08-17T12:00:00Z")
    summary = run(env, monkeypatch, [candle])
    assert summary["pools_fetched"] == 1
    stored = jsonl.read(checkpoints.candles_path(env, "Pool1"))
    assert len(stored) == 1
