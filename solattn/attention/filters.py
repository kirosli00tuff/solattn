"""The registered ingest filter (REGISTRATION.md 7).

A filter is part of the instrument, so it is registered with the registration
and never edited mid-collection.

Rules 1 and 2 are **shape** filters — they match a *form* (a Solana mint
address, a cashtag) rather than a name, so they cannot privilege particular
tokens. That is load-bearing: it is what keeps the ingest filter from becoming
an attention-selection instrument in its own right. Rule 3's keyword set is
small, fixed, and excludes short ambiguous strings ("sol", "ca") that collide
with ordinary prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from solattn import registry

#: Base58 excludes 0, O, I and l. A Solana mint is 32-44 of these characters.
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
MINT_RE = re.compile(
    rf"(?<![{BASE58_ALPHABET}])[{BASE58_ALPHABET}]{{{registry.BASE58_MIN_LEN},{registry.BASE58_MAX_LEN}}}"
    rf"(?![{BASE58_ALPHABET}])"
)
CASHTAG_RE = re.compile(
    rf"\$([A-Za-z0-9]{{{registry.CASHTAG_MIN_LEN},{registry.CASHTAG_MAX_LEN}}})\b"
)


@dataclass(frozen=True)
class FilterHit:
    """What the registered filter found in one message."""

    passed: bool
    mints: tuple[str, ...]
    cashtags: tuple[str, ...]
    keywords: tuple[str, ...]

    @property
    def rule(self) -> str:
        """Which registered rule admitted the message (1 mint, 2 cashtag, 3 keyword)."""
        if self.mints:
            return "1-mint-shape"
        if self.cashtags:
            return "2-cashtag-shape"
        if self.keywords:
            return "3-keyword"
        return "none"


def find_mints(text: str) -> tuple[str, ...]:
    """Every mint-shaped base58 string, in order, deduplicated."""
    seen: dict[str, None] = {}
    for match in MINT_RE.finditer(text):
        seen.setdefault(match.group(0), None)
    return tuple(seen)


def find_cashtags(text: str) -> tuple[str, ...]:
    """Every cashtag, upper-cased and deduplicated. Case-insensitive by registration."""
    seen: dict[str, None] = {}
    for match in CASHTAG_RE.finditer(text):
        seen.setdefault(match.group(1).upper(), None)
    return tuple(seen)


def find_keywords(text: str) -> tuple[str, ...]:
    """Registered keywords present, matched case-insensitively at word boundaries."""
    lowered = text.lower()
    hits: list[str] = []
    for keyword in sorted(registry.INGEST_KEYWORDS):
        pattern = re.compile(rf"(?<!\w){re.escape(keyword)}(?!\w)")
        if pattern.search(lowered):
            hits.append(keyword)
    return tuple(hits)


def apply(text: str) -> FilterHit:
    """Apply the registered ingest filter to one message."""
    mints = find_mints(text)
    cashtags = find_cashtags(text)
    keywords = find_keywords(text)
    return FilterHit(
        passed=bool(mints or cashtags or keywords),
        mints=mints,
        cashtags=cashtags,
        keywords=keywords,
    )
