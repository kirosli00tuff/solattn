"""The fixed Telegram channel list (ADR-007, REGISTRATION.md 7).

The list is resolved ONCE by the registered objective rule — top 20 public
Solana/memecoin channels by member count, from a single stated directory, read
on a single stated date — and is thereafter **never edited mid-collection**.

The resolved list lives in ``docs/CHANNELS.md``, which this module parses. It
is deliberately data, not code: a channel list embedded in source invites an
"improvement" during a refactor, and any change to it starts a new cohort.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CHANNELS_DOC = Path("docs/CHANNELS.md")
#: | rank | @username | members | note |
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*@([A-Za-z0-9_]+)\s*\|\s*([\d,]+)\s*\|(.*)\|\s*$")


@dataclass(frozen=True)
class Channel:
    rank: int
    username: str
    members: int
    note: str


def parse_channels(text: str) -> list[Channel]:
    """Parse the resolved list out of the registration document."""
    channels: list[Channel] = []
    for line in text.splitlines():
        match = ROW_RE.match(line.strip())
        if match is None:
            continue
        channels.append(
            Channel(
                rank=int(match.group(1)),
                username=match.group(2),
                members=int(match.group(3).replace(",", "")),
                note=match.group(4).strip(),
            )
        )
    return sorted(channels, key=lambda c: (c.rank, c.username))


def load_channels(path: Path | None = None) -> list[Channel]:
    """Load the fixed list. An absent document means the list is not yet fixed.

    Returning an empty list is the correct behaviour: the Telegram collector
    stays inactive until the list is fixed, because a provisional list that
    gets improved later is worse than a late start (ADR-007).
    """
    target = path if path is not None else CHANNELS_DOC
    if not target.is_file():
        return []
    return parse_channels(target.read_text(encoding="utf-8"))
