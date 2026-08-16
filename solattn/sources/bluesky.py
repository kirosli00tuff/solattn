"""Bluesky Jetstream: the keyless websocket firehose.

Jetstream serves a filtered, JSON-decoded view of the AT Protocol firehose. It
needs no key and no account. Volume is controlled at ingest by the REGISTERED
filter (REGISTRATION.md 7), never by an unregistered sampling rule.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable
from typing import Any

from solattn import registry
from solattn.clock import Clock, iso
from solattn.records import AccessResult

SOURCE = registry.SOURCE_BLUESKY

#: Public Jetstream instances, in probe order. The first that connects is used.
JETSTREAM_HOSTS: tuple[str, ...] = (
    "wss://jetstream2.us-east.bsky.network/subscribe",
    "wss://jetstream1.us-east.bsky.network/subscribe",
    "wss://jetstream2.us-west.bsky.network/subscribe",
    "wss://jetstream1.us-west.bsky.network/subscribe",
)
WANTED_COLLECTION = "app.bsky.feed.post"


def stream_url(host: str) -> str:
    return f"{host}?wantedCollections={WANTED_COLLECTION}"


def extract_post(event: dict[str, Any]) -> tuple[str, str, str] | None:
    """Pull (author_did, record_key, text) out of a Jetstream commit event.

    Returns None for anything that is not a new post — deletes, identity
    updates, and account events carry no text and are not attention.
    """
    if event.get("kind") != "commit":
        return None
    commit = event.get("commit") or {}
    if commit.get("operation") not in {"create", "update"}:
        return None
    if commit.get("collection") != WANTED_COLLECTION:
        return None
    record = commit.get("record") or {}
    text = record.get("text")
    if not isinstance(text, str):
        return None
    return (str(event.get("did", "")), str(commit.get("rkey", "")), text)


async def _measure(host: str, seconds: float) -> tuple[bool, int, int, str]:
    """Connect and count events for a fixed span. Returns (ok, events, posts, detail)."""
    import websockets

    events = 0
    posts = 0
    try:
        async with websockets.connect(stream_url(host), open_timeout=15) as socket:
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    raw = await asyncio.wait_for(socket.recv(), timeout=remaining)
                except TimeoutError:
                    break
                events += 1
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if extract_post(parsed) is not None:
                    posts += 1
    except Exception as exc:
        return (False, events, posts, f"{type(exc).__name__}: {exc}")
    return (True, events, posts, "connected")


async def consume(
    host: str,
    on_post: Callable[[str, str, str], None],
    stop_after_s: float | None = None,
) -> int:
    """Consume the firehose, calling ``on_post(author_did, rkey, text)``.

    Runs until ``stop_after_s`` elapses, or forever when it is None. The caller
    supplies the registered ingest filter; this function does no filtering of
    its own, so the filter stays in one registered place.
    """
    import websockets

    seen = 0
    deadline = None if stop_after_s is None else time.monotonic() + stop_after_s
    async with websockets.connect(stream_url(host), open_timeout=15) as socket:
        while True:
            if deadline is not None and time.monotonic() >= deadline:
                return seen
            timeout = None if deadline is None else max(0.1, deadline - time.monotonic())
            try:
                raw = await asyncio.wait_for(socket.recv(), timeout=timeout)
            except TimeoutError:
                return seen
            seen += 1
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                continue
            post = extract_post(parsed)
            if post is not None:
                on_post(*post)


def verify(clock: Clock, seconds: float = 10.0) -> list[AccessResult]:
    """Measure the firehose: which host connects, and at what event rate."""
    for host in JETSTREAM_HOSTS:
        ok, events, posts, detail = asyncio.run(_measure(host, seconds))
        if ok:
            return [
                AccessResult(
                    source=SOURCE,
                    endpoint=stream_url(host),
                    reachable=True,
                    measured_rate=(
                        f"{events / seconds:.1f} events/s, {posts / seconds:.1f} posts/s "
                        f"over {seconds:.0f}s (~{int(posts / seconds * 86400):,} posts/day)"
                    ),
                    measured_limit="no documented cap; one persistent connection",
                    cost="keyless, free",
                    detail=f"{detail}; wantedCollections={WANTED_COLLECTION}",
                    measured_at=iso(clock.now()),
                )
            ]
    return [
        AccessResult(
            source=SOURCE,
            endpoint=", ".join(JETSTREAM_HOSTS),
            reachable=False,
            measured_rate="n/a",
            measured_limit="n/a",
            cost="n/a",
            detail=f"no Jetstream host connected across {len(JETSTREAM_HOSTS)} probed",
            measured_at=iso(clock.now()),
        )
    ]
