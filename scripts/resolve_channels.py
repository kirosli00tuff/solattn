"""Run the registered channel resolution ONCE against the live session.

Implements REGISTRATION.md Amendment 1 (2026-08-16). Refuses to run if
docs/CHANNELS.md already carries a resolved list, because the amendment fixes
the list at first resolution and forbids re-resolving for this cohort.

    uv run python scripts/resolve_channels.py

Prints only channel usernames, titles and participant counts. No credential,
no session content, no account identity is read or printed.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from solattn import registry
from solattn.attention.channels import load_channels
from solattn.attention.resolve_channels import (
    Candidate,
    is_eligible,
    is_relevant,
    matched_keywords,
    rank_and_cut,
)
from solattn.clock import SystemClock, iso
from solattn.config import load_settings

RAW_OUT = Path("data/state/channel_resolution_raw.json")


async def main() -> int:
    clock = SystemClock()
    settings = load_settings()

    if load_channels():
        print("docs/CHANNELS.md already carries a resolved list. Amendment 1 fixes the")
        print("list at first resolution; re-resolving is not permitted for this cohort.")
        return 1

    api_id, api_hash = settings.require_telegram()

    from telethon import TelegramClient, functions
    from telethon.errors import FloodWaitError
    from telethon.tl.types import Channel

    client = TelegramClient(settings.telegram_session, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print("session is not authorized; run scripts/telegram_login.py first")
        await client.disconnect()
        return 1

    candidates: dict[int, Candidate] = {}
    per_query: dict[str, int] = {}
    excluded_not_public = 0
    excluded_not_channel = 0
    excluded_irrelevant = 0

    try:
        # --- steps 1-4: search, union, dedupe, apply the mechanical predicates
        for query in registry.CHANNEL_QUERY_SET:
            try:
                result = await client(
                    functions.contacts.SearchRequest(q=query, limit=registry.CHANNEL_SEARCH_LIMIT)
                )
            except FloodWaitError as flood:
                print(f"FloodWaitError on query {query!r}: wait {flood.seconds}s - stopping")
                return 2
            hits = 0
            for chat in list(result.chats):
                if not isinstance(chat, Channel):
                    excluded_not_channel += 1
                    continue
                username = getattr(chat, "username", None)
                if not is_eligible(
                    bool(getattr(chat, "broadcast", False)),
                    bool(getattr(chat, "megagroup", False)),
                    username,
                ):
                    if getattr(chat, "broadcast", False) and not username:
                        excluded_not_public += 1
                    else:
                        excluded_not_channel += 1
                    continue
                title = str(getattr(chat, "title", "") or "")
                if not is_relevant(title, str(username)):
                    excluded_irrelevant += 1
                    continue
                hits += 1
                candidates.setdefault(
                    int(chat.id),
                    Candidate(
                        channel_id=int(chat.id),
                        username=str(username),
                        title=title,
                        matched_queries=matched_keywords(title, str(username)),
                    ),
                )
            per_query[query] = hits
            await asyncio.sleep(1.0)

        print(f"eligible+relevant unique candidates: {len(candidates)}")
        print(f"per-query hits: {json.dumps(per_query)}")
        print(
            f"excluded: not-a-public-channel {excluded_not_channel}, "
            f"no-username {excluded_not_public}, no-keyword {excluded_irrelevant}"
        )

        # --- step 5: participants_count per eligible channel, first-party
        counted: list[tuple[Candidate, int]] = []
        for candidate in candidates.values():
            try:
                full = await client(
                    functions.channels.GetFullChannelRequest(channel=candidate.username)
                )
            except FloodWaitError as flood:
                print(f"FloodWaitError on getFullChannel: wait {flood.seconds}s - stopping")
                return 2
            except Exception as exc:
                print(f"  unresolved @{candidate.username}: {type(exc).__name__}")
                continue
            count = int(getattr(full.full_chat, "participants_count", 0) or 0)
            counted.append((candidate, count))
            await asyncio.sleep(0.4)
    finally:
        await client.disconnect()

    resolved = rank_and_cut(counted, iso(clock.now()))
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    RAW_OUT.write_text(
        json.dumps(
            {
                "resolved_at": iso(clock.now()),
                "query_set": list(registry.CHANNEL_QUERY_SET),
                "search_limit": registry.CHANNEL_SEARCH_LIMIT,
                "candidates_considered": len(candidates),
                "counted": len(counted),
                "per_query_hits": per_query,
                "excluded": {
                    "not_a_public_channel": excluded_not_channel,
                    "no_username": excluded_not_public,
                    "no_registered_keyword": excluded_irrelevant,
                },
                "ranked": [r.to_row() for r in resolved],
                "all_counted": [
                    {"username": c.username, "title": c.title, "participants_count": n}
                    for c, n in sorted(counted, key=lambda p: -p[1])
                ],
            },
            indent=1,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nranked top {len(resolved)} (by Telegram participants_count):")
    for row in resolved:
        print(
            f"  {row.rank:>2}. @{row.username:<28} {row.participants_count:>10,}  {row.title[:38]}"
        )
    print(f"\nraw resolution written to {RAW_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
