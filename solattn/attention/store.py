"""Append-only mention storage, one file per UTC day.

Every ingested message is stored with its registered match attribution,
including ``ambiguous`` and ``unmatched`` — nothing that passed the filter is
discarded, because the ambiguous and unmatched counts are themselves reported
outputs (ADR-005).
"""

from __future__ import annotations

from pathlib import Path

from solattn import jsonl
from solattn.records import Mention


def mentions_path(root: Path, day: str) -> Path:
    return root / f"mentions-{day}.jsonl"


def append_mention(root: Path, day: str, mention: Mention) -> None:
    jsonl.append(mentions_path(root, day), mention.to_row())


def read_day(root: Path, day: str) -> list[Mention]:
    """Read one day's mentions, ordered by the record's own posted_at."""
    rows = jsonl.read(mentions_path(root, day), order_by="posted_at")
    seen: dict[tuple[str, str, str], Mention] = {}
    for row in rows:
        mention = Mention(**row)
        seen.setdefault((mention.source, mention.channel, mention.message_id), mention)
    return sorted(seen.values(), key=lambda m: (m.posted_at, m.message_id))
