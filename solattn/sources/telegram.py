"""Telegram over MTProto: public channel reads.

Two facts about MTProto shape this module, and both are measured rather than
assumed:

1. **The api_id / api_hash pair can be validated without an account.** An
   unauthenticated ``help.getNearestDc`` still travels inside
   ``initConnection(api_id=...)``, so an invalid api_id raises
   ``ApiIdInvalidError``. That makes credential validity a MEASURED fact.
2. **Reading channels needs an authorized user session, and MTProto has no
   non-interactive user login.** The phone-code step can only be performed by
   the operator. Absent a session the collector reports exactly what is needed
   and stays inactive — **it does not block the stage**, and every other source
   keeps collecting.

Flood limits on public channel reads are measurable only once a session exists;
until then the module reports them as unmeasured rather than quoting a number
from documentation.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from solattn import registry
from solattn.clock import Clock, iso
from solattn.records import AccessResult

SOURCE = registry.SOURCE_TELEGRAM


@dataclass(frozen=True)
class CredentialProbe:
    """The measured outcome of validating an api_id / api_hash pair."""

    accepted: bool
    elapsed_s: float
    nearest_dc: int | None
    detail: str


async def _probe_credentials(api_id: int, api_hash: str) -> CredentialProbe:
    """Connect unauthenticated and validate the credential pair by measurement."""
    from telethon import TelegramClient, functions
    from telethon.sessions import MemorySession

    client = TelegramClient(MemorySession(), api_id, api_hash)
    started = time.monotonic()
    try:
        await client.connect()
        result: Any = await client(functions.help.GetNearestDcRequest())
        elapsed = time.monotonic() - started
        return CredentialProbe(
            accepted=True,
            elapsed_s=elapsed,
            nearest_dc=int(getattr(result, "nearest_dc", 0)) or None,
            detail=f"help.getNearestDc accepted the api_id; country={getattr(result, 'country', '?')}",
        )
    except Exception as exc:
        return CredentialProbe(
            accepted=False,
            elapsed_s=time.monotonic() - started,
            nearest_dc=None,
            detail=f"{type(exc).__name__}: {exc}",
        )
    finally:
        await client.disconnect()


def session_exists(session_name: str) -> bool:
    """True when an authorized Telethon session file is already on disk."""
    return Path(f"{session_name}.session").is_file()


async def _probe_channel_reads(
    api_id: int, api_hash: str, session_name: str, channels: list[str], per_channel: int
) -> tuple[bool, int, float, str]:
    """Measure real public-channel reads and any flood wait, with a session.

    Returns (authorized, messages_read, elapsed_s, detail). A ``FloodWaitError``
    is CAUGHT AND REPORTED with its wait seconds — that is the measurement this
    probe exists to take, not a failure.
    """
    from telethon import TelegramClient
    from telethon.errors import FloodWaitError

    client = TelegramClient(session_name, api_id, api_hash)
    read = 0
    started = time.monotonic()
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return (False, 0, time.monotonic() - started, "session exists but is not authorized")
        for channel in channels:
            try:
                async for _ in client.iter_messages(channel, limit=per_channel):
                    read += 1
            except FloodWaitError as flood:
                return (
                    True,
                    read,
                    time.monotonic() - started,
                    f"FloodWaitError after {read} messages: wait {flood.seconds}s",
                )
            except Exception as exc:
                return (True, read, time.monotonic() - started, f"{type(exc).__name__}: {exc}")
        elapsed = time.monotonic() - started
        return (True, read, elapsed, f"no flood limit hit reading {read} messages")
    finally:
        await client.disconnect()


async def consume(
    api_id: int,
    api_hash: str,
    session_name: str,
    channels: list[str],
    on_message: Callable[[str, str, str, str, str], None],
    limit_per_channel: int,
    charge: Callable[[str], None] | None = None,
    on_flood: Callable[[str, int], None] | None = None,
) -> int:
    """Read recent messages from the fixed channel list.

    ``on_message(channel, message_id, author_id, posted_at, text)``. The channel
    list is the REGISTERED one (ADR-007) and is passed in rather than chosen
    here, so it cannot be edited by this module mid-collection.

    ``charge`` is called once per channel BEFORE its history is requested — the
    ledger hook (ADR-011). A refusal raises before anything is read and
    propagates to the caller; nothing is fetched past the cap.

    ``on_flood`` records a ``FloodWaitError`` passively: the channel is skipped
    for this cycle and the wait is REPORTED, never slept toward or retried —
    deliberately tripping flood control risks the account and buys a number the
    measurement does not need.
    """
    from telethon import TelegramClient

    client = TelegramClient(session_name, api_id, api_hash)
    seen = 0
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise RuntimeError(
                "Telegram session is not authorized. Run the one-time interactive "
                "login (scripts/telegram_login.py); MTProto has no non-interactive "
                "user login and only the operator can complete it."
            )
        from telethon.errors import FloodWaitError

        for channel in channels:
            if charge is not None:
                charge(channel)  # a RequestCapError here propagates: refused, nothing read
            try:
                async for message in client.iter_messages(channel, limit=limit_per_channel):
                    text = getattr(message, "message", None)
                    if not text:
                        continue
                    sender = getattr(message, "sender_id", None)
                    on_message(
                        channel,
                        str(getattr(message, "id", "")),
                        f"tg:{sender}" if sender is not None else "tg:unknown",
                        iso(message.date) if getattr(message, "date", None) else "",
                        str(text),
                    )
                    seen += 1
            except FloodWaitError as flood:
                if on_flood is not None:
                    on_flood(channel, int(flood.seconds))
                continue
    finally:
        await client.disconnect()
    return seen


def verify(
    clock: Clock,
    api_id: int | None,
    api_hash: str | None,
    session_name: str,
    channels: list[str] | None = None,
) -> list[AccessResult]:
    """Measure what is actually reachable over MTProto right now."""
    if api_id is None or api_hash is None:
        missing = []
        if api_id is None:
            missing.append("SOLATTN_TELEGRAM_API_ID")
        if api_hash is None:
            missing.append("SOLATTN_TELEGRAM_API_HASH")
        return [
            AccessResult(
                source=SOURCE,
                endpoint="MTProto",
                reachable=False,
                measured_rate="n/a",
                measured_limit="n/a",
                cost="n/a",
                detail=(
                    f"credential absent: {', '.join(missing)}. The operator must create "
                    f"an api_id and api_hash at https://my.telegram.org and put them in "
                    f".env. The collector is built and activates when they appear; the "
                    f"stage is not blocked."
                ),
                measured_at=iso(clock.now()),
            )
        ]

    probe = asyncio.run(_probe_credentials(api_id, api_hash))
    results = [
        AccessResult(
            source=SOURCE,
            endpoint="MTProto help.getNearestDc (unauthenticated)",
            reachable=probe.accepted,
            measured_rate=f"{probe.elapsed_s:.2f}s for connect + one call",
            measured_limit="credential validity only; channel-read limits need a session",
            cost="keyless beyond the api_id pair; free",
            detail=probe.detail + (f"; nearest DC {probe.nearest_dc}" if probe.nearest_dc else ""),
            measured_at=iso(clock.now()),
        )
    ]

    if not probe.accepted:
        return results

    if not session_exists(session_name):
        results.append(
            AccessResult(
                source=SOURCE,
                endpoint="MTProto channels.getHistory (public channels)",
                reachable=False,
                measured_rate="UNMEASURED",
                measured_limit=(
                    "UNMEASURED - flood limits are only observable with an authorized "
                    "session, and no figure is quoted from documentation"
                ),
                cost="free",
                detail=(
                    f"no authorized session at {session_name}.session. MTProto has no "
                    f"non-interactive user login: the operator runs "
                    f"`uv run python scripts/telegram_login.py` once (phone number + "
                    f"code). The collector activates the moment the session exists."
                ),
                measured_at=iso(clock.now()),
            )
        )
        return results

    authorized, read, elapsed, detail = asyncio.run(
        _probe_channel_reads(api_id, api_hash, session_name, channels or [], 20)
    )
    results.append(
        AccessResult(
            source=SOURCE,
            endpoint="MTProto channels.getHistory (public channels)",
            reachable=authorized and read > 0,
            measured_rate=f"{read} messages in {elapsed:.2f}s ({read / max(elapsed, 0.01):.1f}/s)",
            measured_limit=detail,
            cost="free",
            detail=f"probed {len(channels or [])} registered channels",
            measured_at=iso(clock.now()),
        )
    )
    return results
