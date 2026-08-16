"""Append-only JSONL storage with clock-ordered reads and sha256 sealing.

Two standing practices live here:

* **Never trust append order across processes.** Two processes appending to one
  file interleave. Every reader sorts by the record's own recorded clock field,
  never by file position.
* **The manifests are immutable.** ``seal`` writes a sidecar carrying the
  sha256 of the closed file and its row count. Re-sealing a file whose hash has
  changed raises: a corrected row is APPENDED as a new record with its own
  retrieval time, never edited in place.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Row = dict[str, Any]


class SealMismatchError(RuntimeError):
    """Raised when a sealed file no longer matches its recorded digest."""


def append(path: Path, row: Row) -> None:
    """Append one JSON row atomically enough for concurrent writers.

    A single ``write`` of a line shorter than PIPE_BUF is not torn by the OS
    when the file is opened in append mode, which is why each row is
    serialized fully before the write rather than streamed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def append_many(path: Path, rows: list[Row]) -> int:
    """Append many rows; returns the count written."""
    for row in rows:
        append(path, row)
    return len(rows)


def read(path: Path, order_by: str | None = None) -> list[Row]:
    """Read every row, ordered by ``order_by`` when given.

    Ordering is by the record's own clock field, never by file position — two
    processes appending to one file interleave, and file order is not time
    order. A row missing the ordering field raises rather than sorting to an
    arbitrary position.
    """
    if not path.is_file():
        return []
    rows: list[Row] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno} is not valid JSON: {exc}") from exc
        rows.append(parsed)
    if order_by is None:
        return rows
    for index, row in enumerate(rows):
        if order_by not in row:
            raise ValueError(f"{path} row {index} has no {order_by!r} field to order by")
    return sorted(rows, key=lambda r: str(r[order_by]))


def digest(path: Path) -> str:
    """sha256 of a file's bytes."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass(frozen=True)
class Seal:
    """The immutability record for a closed file."""

    path: str
    sha256: str
    rows: int
    sealed_at: str


def seal(path: Path, sealed_at: str) -> Seal:
    """Close a file: record its sha256 and row count in a sidecar.

    Sealing a file that already carries a seal with a DIFFERENT digest raises —
    that is a rewritten manifest, which the immutability rule forbids.
    """
    sidecar = path.with_suffix(path.suffix + ".seal.json")
    current = Seal(
        path=path.name,
        sha256=digest(path),
        rows=len(read(path)),
        sealed_at=sealed_at,
    )
    if sidecar.is_file():
        previous = json.loads(sidecar.read_text(encoding="utf-8"))
        if previous["sha256"] != current.sha256:
            raise SealMismatchError(
                f"{path} was modified after sealing: recorded {previous['sha256'][:12]}, "
                f"now {current.sha256[:12]}. Manifests are immutable; append a correction "
                f"as a new record instead of editing one."
            )
        return current
    sidecar.write_text(
        json.dumps(current.__dict__, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return current


def verify_seal(path: Path) -> bool:
    """True when a sealed file still matches its recorded digest."""
    sidecar = path.with_suffix(path.suffix + ".seal.json")
    if not sidecar.is_file():
        return False
    recorded = json.loads(sidecar.read_text(encoding="utf-8"))
    return bool(recorded["sha256"] == digest(path))
