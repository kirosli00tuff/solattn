"""The request ledger: counted before sending, restart-proof, refuses first."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from solattn.clock import FixedClock
from solattn.ledger import Ledger, RequestCapError

NOW = datetime(2026, 8, 16, 12, 0, tzinfo=UTC)
NEXT_DAY = datetime(2026, 8, 17, 0, 30, tzinfo=UTC)


def build(tmp_path: Path, cap: int, clock: FixedClock | None = None) -> Ledger:
    return Ledger(tmp_path / "requests.jsonl", {"src": cap}, clock or FixedClock(NOW))


def test_charges_accumulate(tmp_path: Path) -> None:
    ledger = build(tmp_path, 5)
    ledger.charge("src")
    ledger.charge("src", 2)
    assert ledger.spent("src") == 3


def test_refusal_writes_nothing_and_names_the_arithmetic(tmp_path: Path) -> None:
    # Arrange
    ledger = build(tmp_path, 3)
    ledger.charge("src", 3)
    # Act / Assert
    with pytest.raises(RequestCapError, match=r"3 already spent .* \+ 1 requested > cap 3"):
        ledger.charge("src")
    assert ledger.spent("src") == 3  # nothing was written by the refusal


def test_cap_survives_a_restart(tmp_path: Path) -> None:
    """A new Ledger over the same file re-reads the cumulative total."""
    build(tmp_path, 4).charge("src", 4)
    restarted = build(tmp_path, 4)
    assert restarted.spent("src") == 4
    with pytest.raises(RequestCapError):
        restarted.charge("src")


def test_the_cap_is_per_day(tmp_path: Path) -> None:
    build(tmp_path, 2).charge("src", 2)
    tomorrow = build(tmp_path, 2, FixedClock(NEXT_DAY))
    assert tomorrow.spent("src") == 0
    tomorrow.charge("src")


def test_a_source_without_a_registered_cap_cannot_send(tmp_path: Path) -> None:
    with pytest.raises(KeyError, match="no registered daily cap"):
        build(tmp_path, 5).charge("unregistered")


def test_report_shows_remaining(tmp_path: Path) -> None:
    ledger = build(tmp_path, 10)
    ledger.charge("src", 4)
    assert ledger.report()["src"] == {"spent": 4, "cap": 10, "remaining": 6}


def test_mtproto_channel_read_refuses_at_the_telegram_cap(tmp_path: Path) -> None:
    """ADR-011: one charge per channels.getHistory; the cap binds via the gate.

    In the pattern of the gate tests above: the third channel read refuses,
    names the arithmetic, and writes nothing - so a cadence change can never
    silently remove the limit, because the limit is the ledger, not the cadence.
    """
    from solattn.attention.collect import charge_channel_read

    ledger = Ledger(tmp_path / "requests.jsonl", {"telegram": 2}, FixedClock(NOW))
    charge_channel_read(ledger, "memecoinx")
    charge_channel_read(ledger, "Raydiumx")
    with pytest.raises(RequestCapError, match=r"2 already spent .* > cap 2"):
        charge_channel_read(ledger, "myroSOL")
    assert ledger.spent("telegram") == 2  # the refusal wrote nothing
