"""The single source of wall-clock time.

Nothing in this package calls ``datetime.now()`` directly. Time enters through
a ``Clock``, which tests replace with a fixed one, so a measurement that
depends on "now" is reproducible rather than dependent on when the suite ran.

All times are UTC. All serialized timestamps are ISO-8601 with a ``Z`` suffix.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    """Supplies the current instant. The only permitted source of "now"."""

    def now(self) -> datetime:  # pragma: no cover - protocol
        ...


class SystemClock:
    """The real clock. UTC, always."""

    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True)
class FixedClock:
    """A clock pinned to one instant, for tests."""

    instant: datetime

    def now(self) -> datetime:
        return self.instant


def iso(moment: datetime) -> str:
    """Serialize to ISO-8601 UTC with a ``Z`` suffix.

    Raises on a naive datetime rather than assuming a timezone: a silent
    assumption about timezone is how an off-by-hours error survives review.
    """
    if moment.tzinfo is None:
        raise ValueError("refusing to serialize a naive datetime; attach UTC explicitly")
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(text: str) -> datetime:
    """Parse an ISO-8601 timestamp, normalizing to UTC.

    Accepts the ``Z`` suffix and explicit offsets. A timestamp with no offset
    is rejected, for the same reason ``iso`` rejects a naive datetime.
    """
    normalized = text.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp carries no timezone: {text!r}")
    return parsed.astimezone(UTC)


def utc_date(moment: datetime) -> date:
    """The UTC calendar date of an instant."""
    return moment.astimezone(UTC).date()


def day_str(day: date) -> str:
    """The registered calendar-date form, ``YYYY-MM-DD``."""
    return day.isoformat()


def add_days(day: date, count: int) -> date:
    """Calendar-date arithmetic, isolated so the horizon rules read plainly."""
    return day + timedelta(days=count)
