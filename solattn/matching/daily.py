"""First-class daily match counts (REGISTRATION.md 3).

``matched``, ``ambiguous`` and ``unmatched`` are emitted per day and per source
every day. **Ambiguous is never folded into either of the others** — it is the
count that quantifies the study's expected failure mode.
"""

from __future__ import annotations

from solattn import registry
from solattn.attention import store
from solattn.config import Settings
from solattn.records import MatchCounts


def daily_counts(settings: Settings, day: str) -> list[MatchCounts]:
    """Per-source match tallies for one UTC day, plus an ALL row."""
    mentions = store.read_day(settings.attention_dir(), day)
    sources = sorted({m.source for m in mentions})
    tallies: list[MatchCounts] = []
    for source in [*sources, "ALL"]:
        subset = mentions if source == "ALL" else [m for m in mentions if m.source == source]
        tallies.append(
            MatchCounts(
                day=day,
                source=source,
                ingested=len(subset),
                matched_mint=sum(1 for m in subset if m.match_kind == registry.MATCH_MINT),
                matched_cashtag=sum(1 for m in subset if m.match_kind == registry.MATCH_CASHTAG),
                matched_name=sum(1 for m in subset if m.match_kind == registry.MATCH_NAME),
                ambiguous=sum(1 for m in subset if m.match_kind == registry.MATCH_AMBIGUOUS),
                unmatched=sum(1 for m in subset if m.match_kind == registry.MATCH_UNMATCHED),
                conflicts=sum(1 for m in subset if m.conflict),
            )
        )
    return tallies


def render_counts(tallies: list[MatchCounts], day: str) -> str:
    """Render the daily counts table."""
    lines = [
        f"# match counts — {day}",
        "",
        "| source | ingested | mint | cashtag | name | **ambiguous** | unmatched | conflicts |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in tallies:
        lines.append(
            f"| {row.source} | {row.ingested} | {row.matched_mint} | {row.matched_cashtag} | "
            f"{row.matched_name} | **{row.ambiguous}** | {row.unmatched} | {row.conflicts} |"
        )
    if not tallies:
        lines.append("| (no mentions recorded) | 0 | 0 | 0 | 0 | **0** | 0 | 0 |")
    lines.extend(
        [
            "",
            "Ambiguous mentions are attributed to **no token** and are counted here as a "
            "first-class category — ticker collisions are the expected failure mode of this "
            "study, not an edge case (ADR-005).",
        ]
    )
    return "\n".join(lines) + "\n"
