"""Append-only storage: clock-ordered reads and immutable sealing."""

from __future__ import annotations

from pathlib import Path

import pytest

from solattn import jsonl


def test_reads_are_ordered_by_the_clock_not_by_file_position(tmp_path: Path) -> None:
    """Two processes appending interleave; file order is not time order."""
    # Arrange - written out of chronological order, as concurrent writers would
    path = tmp_path / "rows.jsonl"
    jsonl.append(path, {"at": "2026-08-16T12:00:00Z", "v": "second"})
    jsonl.append(path, {"at": "2026-08-16T09:00:00Z", "v": "first"})
    # Act
    rows = jsonl.read(path, order_by="at")
    # Assert
    assert [r["v"] for r in rows] == ["first", "second"]


def test_missing_order_field_raises_rather_than_sorting_arbitrarily(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    jsonl.append(path, {"v": 1})
    with pytest.raises(ValueError, match="has no 'at' field to order by"):
        jsonl.read(path, order_by="at")


def test_absent_file_reads_empty(tmp_path: Path) -> None:
    assert jsonl.read(tmp_path / "nope.jsonl") == []


def test_seal_records_the_digest_and_row_count(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    jsonl.append_many(path, [{"v": 1}, {"v": 2}])
    sealed = jsonl.seal(path, "2026-08-16T00:00:00Z")
    assert sealed.rows == 2
    assert jsonl.verify_seal(path) is True


def test_rewriting_a_sealed_file_raises(tmp_path: Path) -> None:
    """Manifests are immutable: a correction is appended, never edited in."""
    path = tmp_path / "rows.jsonl"
    jsonl.append(path, {"v": 1})
    jsonl.seal(path, "2026-08-16T00:00:00Z")
    jsonl.append(path, {"v": 2})
    assert jsonl.verify_seal(path) is False
    with pytest.raises(jsonl.SealMismatchError, match="Manifests are immutable"):
        jsonl.seal(path, "2026-08-16T01:00:00Z")


def test_malformed_line_raises_with_its_line_number(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text('{"v": 1}\nnot json\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"rows\.jsonl:2 is not valid JSON"):
        jsonl.read(path)
