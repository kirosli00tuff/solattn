"""The paced, ledger-gated HTTP transport.

This is the ONLY way this package reaches the network over HTTP. An unmetered
call is structurally unavailable rather than merely discouraged (ADR-003): the
client owns the ledger, charges before sending, and enforces the registered
minimum spacing per source.

Pacing comes from measurement, never from a published figure — solclear
recorded HTTP 429 from GeckoTerminal at 2.5 s spacing against a documented
30/min limit, and 6 s held.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

from solattn import registry
from solattn.ledger import Ledger


@dataclass(frozen=True)
class Response:
    """A measured HTTP response: status, body, and how long it took."""

    status: int
    elapsed_s: float
    url: str
    json_body: Any | None
    text: str

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


class PacedClient:
    """Ledger-gated HTTP client with per-source minimum spacing.

    Every request is charged to the ledger BEFORE it is sent. A refusal
    (``RequestCapError``) propagates to the caller and nothing is sent.
    """

    def __init__(self, ledger: Ledger, timeout_s: float = 30.0) -> None:
        self._ledger = ledger
        self._client = httpx.Client(
            timeout=timeout_s,
            headers={"User-Agent": "solattn/0.1 (research measurement; no execution path)"},
            follow_redirects=True,
        )
        self._last_sent: dict[str, float] = {}

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> PacedClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _pace(self, source: str) -> float:
        """Sleep until the registered minimum spacing has elapsed. Returns waited seconds."""
        spacing = registry.MIN_SPACING_S.get(source, 1.0)
        last = self._last_sent.get(source)
        if last is None:
            return 0.0
        waited = spacing - (time.monotonic() - last)
        if waited > 0:
            time.sleep(waited)
            return waited
        return 0.0

    def get(
        self,
        source: str,
        url: str,
        params: dict[str, Any] | None = None,
        note: str = "",
    ) -> Response:
        """Charge, pace, send, and return a measured response.

        A non-2xx status is returned rather than raised: the caller decides
        whether a 404 is a data condition or a failure. What is never allowed
        is an error quietly becoming a data condition, so the status is always
        on the returned object.
        """
        self._ledger.charge(source, 1, note or url)
        self._pace(source)
        started = time.monotonic()
        try:
            raw = self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            self._last_sent[source] = time.monotonic()
            return Response(
                status=0,
                elapsed_s=time.monotonic() - started,
                url=url,
                json_body=None,
                text=f"{type(exc).__name__}: {exc}",
            )
        self._last_sent[source] = time.monotonic()
        elapsed = time.monotonic() - started
        body: Any | None
        try:
            body = raw.json()
        except ValueError:
            body = None
        return Response(
            status=raw.status_code,
            elapsed_s=elapsed,
            url=str(raw.url),
            json_body=body,
            text=raw.text[:2000],
        )
