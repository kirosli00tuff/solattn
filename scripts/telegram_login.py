"""One-time interactive Telegram login.

MTProto has **no non-interactive user login**: authorizing a session requires a
phone number and the code Telegram sends to it, and only the operator can
complete that. This script exists so the step is explicit and performed once.

    uv run python scripts/telegram_login.py

It writes a Telethon session file (gitignored via ``*.session``). The collector
activates the moment the session exists; until then it reports exactly what is
missing and every other source keeps collecting.

No credential handled here has any capability beyond reading public data.
"""

from __future__ import annotations

import asyncio
import sys

from solattn.config import load_settings


async def main() -> int:
    settings = load_settings()
    try:
        api_id, api_hash = settings.require_telegram()
    except Exception as exc:
        print(exc)
        return 1

    from telethon import TelegramClient

    client = TelegramClient(settings.telegram_session, api_id, api_hash)
    await client.start()  # type: ignore[func-returns-value]
    try:
        me = await client.get_me()
        username = getattr(me, "username", None) or getattr(me, "id", "?")
        print(f"authorized as {username}; session written to {settings.telegram_session}.session")
    finally:
        await client.disconnect()  # type: ignore[misc]
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
