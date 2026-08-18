"""The request ledger: every outbound request counted before it is sent.

ADR-003. Every source this project touches is free or keyless, which is exactly
the condition under which metering gets skipped. **A free tier still has limits,
and a gate that never fires is still a gate** — its value is that it cannot be
walked past, not that it is frequently hit.

Three properties, ported from solclear:

* **Counted before sending.** :meth:`Ledger.charge` runs the cap arithmetic
  first and raises before the caller can issue the request.
* **Append-only on disk, re-read on start.** A restart cannot walk past the cap,
  and many small requests cannot accumulate past it either.
* **A refusal names the arithmetic and writes nothing.**
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Final

from solattn import jsonl
from solattn.clock import Clock, day_str, iso, utc_date

#: Ledger row kinds. A charge is priced before sending and carries the count
#: the cap arithmetic uses; a settle records what came back and carries
#: ``count = 0``, so adding it can never move a cap. Rows written before
#: ADR-017 have no ``kind`` and read as charges, which is what they were.
KIND_CHARGE: Final = "charge"
KIND_SETTLE: Final = "settle"


class RequestCapError(RuntimeError):
    """Raised before a request is sent, when it would exceed the daily cap."""

    def __init__(self, source: str, spent: int, cap: int, requested: int, day: date) -> None:
        super().__init__(
            f"{source} daily cap refused: {spent} already spent on {day_str(day)} "
            f"+ {requested} requested > cap {cap}. Nothing was sent and nothing was "
            f"written. Raise the cap deliberately before a run, never mid-run."
        )
        self.source = source
        self.spent = spent
        self.cap = cap


class Ledger:
    """Append-only per-source daily request ledger."""

    def __init__(self, path: Path, caps: dict[str, int], clock: Clock) -> None:
        self._path = path
        self._caps = dict(caps)
        self._clock = clock

    def cap_for(self, source: str) -> int:
        if source not in self._caps:
            raise KeyError(
                f"{source!r} has no registered daily cap. Every source needs one "
                f"before it may send a request; add it to registry.DAILY_CAPS."
            )
        return self._caps[source]

    def spent(self, source: str, day: date | None = None) -> int:
        """Re-read the ledger from disk and total the day's requests.

        Re-reads rather than caching so a second process's requests are seen,
        and sums rather than assuming append order (two processes appending to
        one file interleave).
        """
        target = day_str(day if day is not None else utc_date(self._clock.now()))
        totals: Counter[str] = Counter()
        for row in jsonl.read(self._path):
            if row.get("day") == target:
                totals[str(row.get("source"))] += int(row.get("count", 0))
        return totals[source]

    def charge(self, source: str, count: int = 1, note: str = "") -> None:
        """Price the request BEFORE it is sent; raise if it would exceed the cap.

        A refusal writes nothing at all — no partial charge, no attempt record.
        """
        if count <= 0:
            raise ValueError("a request charge must be positive")
        cap = self.cap_for(source)
        now = self._clock.now()
        day = utc_date(now)
        already = self.spent(source, day)
        if already + count > cap:
            raise RequestCapError(source, already, cap, count, day)
        jsonl.append(
            self._path,
            {
                "at": iso(now),
                "day": day_str(day),
                "source": source,
                "count": count,
                "kind": KIND_CHARGE,
                "note": note,
            },
        )

    def settle(self, source: str, status: int, note: str = "") -> None:
        """Record what the charged request actually returned.

        The charge is priced BEFORE the request is sent, so the status cannot
        be on the charge row, and the ledger is append-only so the charge row
        cannot be edited. The status is therefore a SECOND row, carrying
        ``count = 0`` so it can never affect the cap arithmetic.

        Without this a retrospective cannot tell a served request from a
        refused one: the ledger recorded 429s and 200s identically, which is
        why A.5 had to re-probe the source to discover that the rate limiter
        was firing at all (ADR-017). ``status = 0`` means a transport error.
        """
        now = self._clock.now()
        jsonl.append(
            self._path,
            {
                "at": iso(now),
                "day": day_str(utc_date(now)),
                "source": source,
                "count": 0,
                "kind": KIND_SETTLE,
                "status": int(status),
                "ok": int(200 <= status < 300),
                "note": note,
            },
        )

    def statuses(self, day: date | None = None) -> dict[str, Counter[int]]:
        """Per-source HTTP status tallies for a day, from the settle rows."""
        target = day_str(day if day is not None else utc_date(self._clock.now()))
        out: dict[str, Counter[int]] = {}
        for row in jsonl.read(self._path):
            if row.get("day") != target or row.get("kind") != KIND_SETTLE:
                continue
            out.setdefault(str(row.get("source")), Counter())[int(row.get("status", 0))] += 1
        return out

    def report(self, day: date | None = None) -> dict[str, dict[str, int]]:
        """Per-source spent / cap / remaining for a day."""
        target = day if day is not None else utc_date(self._clock.now())
        out: dict[str, dict[str, int]] = {}
        for source, cap in sorted(self._caps.items()):
            used = self.spent(source, target)
            out[source] = {"spent": used, "cap": cap, "remaining": cap - used}
        return out
