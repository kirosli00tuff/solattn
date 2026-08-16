"""Union before summing — with at least one overlapping pair, always.

A test that only uses disjoint windows does not exercise the bug this rule
exists to prevent (three parent-project defects came from exactly that shape).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from solattn.intervals import clamp, covered_duration, merge_windows


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 8, 16, hour, minute, tzinfo=UTC)


def test_overlapping_windows_are_counted_once() -> None:
    # Arrange - two windows overlapping by 30 minutes
    windows = [(at(1), at(3)), (at(2, 30), at(4))]
    # Act
    total = covered_duration(windows)
    # Assert - 3 hours of coverage, not the naive 3.5
    assert total == timedelta(hours=3)


def test_abutting_windows_merge() -> None:
    assert merge_windows([(at(1), at(2)), (at(2), at(3))]) == [(at(1), at(3))]


def test_disjoint_windows_stay_separate() -> None:
    windows = [(at(5), at(6)), (at(1), at(2))]
    assert merge_windows(windows) == [(at(1), at(2)), (at(5), at(6))]
    assert covered_duration(windows) == timedelta(hours=2)


def test_fully_contained_window_adds_nothing() -> None:
    assert covered_duration([(at(1), at(5)), (at(2), at(3))]) == timedelta(hours=4)


def test_empty_is_zero() -> None:
    assert merge_windows([]) == []
    assert covered_duration([]) == timedelta()


def test_backwards_window_raises_rather_than_reordering() -> None:
    with pytest.raises(ValueError, match="ends before it starts"):
        merge_windows([(at(3), at(1))])


def test_clamp_restricts_to_bounds() -> None:
    assert clamp((at(1), at(5)), (at(2), at(4))) == (at(2), at(4))
    assert clamp((at(1), at(2)), (at(3), at(4))) is None
