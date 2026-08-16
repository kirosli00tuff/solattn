"""Interval arithmetic: union before summing.

Standing practice, ported from MLCryptoEngine where three separate defects came
from exactly one shape — a list of possibly-overlapping windows, a ``sum()``,
and no union. It never raises. It silently returns a number that is too large.

Any interval computation in this package calls :func:`merge_windows` first.
Do not hand-roll a "sort and add" that looks equivalent.
"""

from __future__ import annotations

from datetime import datetime, timedelta

Window = tuple[datetime, datetime]


def merge_windows(windows: list[Window]) -> list[Window]:
    """Union a list of windows into disjoint, ascending, non-touching spans.

    Windows that overlap OR abut are merged. A window whose end precedes its
    start is a caller error and raises rather than being silently reordered.
    """
    for start, end in windows:
        if end < start:
            raise ValueError(f"window ends before it starts: {start} -> {end}")
    if not windows:
        return []

    ordered = sorted(windows, key=lambda w: (w[0], w[1]))
    merged: list[Window] = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def covered_duration(windows: list[Window]) -> timedelta:
    """Total time covered by a list of windows, counting overlap once."""
    return sum((end - start for start, end in merge_windows(windows)), timedelta())


def clamp(window: Window, bounds: Window) -> Window | None:
    """Intersect a window with bounds; ``None`` when they do not overlap.

    Used wherever a recorded span must be restricted to a measurement window
    before its duration is counted — the Stage 1.6 defect shape.
    """
    start = max(window[0], bounds[0])
    end = min(window[1], bounds[1])
    if end <= start:
        return None
    return (start, end)
