"""Lifecycle markers and restart-proof cursor state.

The recorder discipline, ported from MLCryptoEngine: a long-running collector
records what it did, when it started and stopped, and where it got to, so a
restart resumes rather than re-reads or silently skips.

A cursor is written AFTER the work it describes is durably stored, never
before — a cursor ahead of the data is an invisible gap in a forward-recorded
cohort, and a forward gap cannot be backfilled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from solattn import jsonl
from solattn.clock import Clock, iso

MARKER_START = "start"
MARKER_STOP = "stop"
MARKER_ERROR = "error"
MARKER_REFUSAL = "refusal"
MARKER_SATURATION = "saturation"
MARKER_HEARTBEAT = "heartbeat"


@dataclass(frozen=True)
class Lifecycle:
    """Append-only lifecycle log for one named component."""

    path: Path
    component: str
    clock: Clock

    def mark(self, marker: str, detail: str = "", **fields: Any) -> None:
        row: dict[str, Any] = {
            "at": iso(self.clock.now()),
            "component": self.component,
            "marker": marker,
            "detail": detail,
        }
        row.update(fields)
        jsonl.append(self.path, row)

    def started(self, detail: str = "", **fields: Any) -> None:
        self.mark(MARKER_START, detail, **fields)

    def stopped(self, detail: str = "", **fields: Any) -> None:
        self.mark(MARKER_STOP, detail, **fields)

    def errored(self, detail: str, **fields: Any) -> None:
        self.mark(MARKER_ERROR, detail, **fields)

    def refused(self, detail: str, **fields: Any) -> None:
        """A refusal is a first-class recorded outcome, never a silent skip."""
        self.mark(MARKER_REFUSAL, detail, **fields)

    def heartbeat(self, detail: str = "", **fields: Any) -> None:
        self.mark(MARKER_HEARTBEAT, detail, **fields)


class Cursor:
    """A restart-proof position marker, written after the work it describes."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def read(self) -> dict[str, Any]:
        if not self._path.is_file():
            return {}
        loaded: dict[str, Any] = json.loads(self._path.read_text(encoding="utf-8"))
        return loaded

    def write(self, **fields: Any) -> None:
        """Write atomically: a torn cursor file is worse than an old one."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(json.dumps(fields, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(self._path)

    def get(self, key: str, default: Any = None) -> Any:
        return self.read().get(key, default)
