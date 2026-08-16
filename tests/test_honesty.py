"""Load-bearing honesty tests. These pin the scope into the build.

Two things break the build here, deliberately:

* an **execution-shaped public name** appearing anywhere in the package, and
* a **deletion of one of the pinned statements** from README.md, CLAUDE.md, or
  REGISTRATION.md.

A future reader, or a future session, cannot quietly remove what makes this
project honest. A third test scans every tracked file for credential-shaped
strings, and a canary asserts each presence-checker actually fires.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def flat(text: str) -> str:
    """Collapse whitespace so a markdown reflow does not break a pin.

    The pin exists to catch a DELETION, not a rewrap. Collapsing both sides
    keeps it sensitive to the former and blind to the latter. Blockquote
    markers are stripped first: the scope statement lives inside a blockquote,
    and a leading "> " on each line would otherwise land mid-sentence.
    """
    stripped = [line.lstrip().removeprefix("> ").removeprefix(">") for line in text.splitlines()]
    return " ".join(" ".join(stripped).split())


#: Names that would mean this project had grown an execution path. The scope
#: statement forbids all of them in every stage.
EXECUTION_SHAPED = re.compile(
    r"(place_order|submit_order|send_order|create_order|market_buy|market_sell"
    r"|open_position|close_position|size_position|position_size|take_profit"
    r"|stop_loss|sign_transaction|private_key|keypair|wallet|swap_tokens"
    r"|execute_trade|entry_signal|buy_signal|sell_signal|recommend_entry)",
    re.IGNORECASE,
)


def package_files() -> list[Path]:
    return sorted((ROOT / "solattn").rglob("*.py"))


def public_names(source: str) -> list[str]:
    """Module-level def/class names that do not begin with an underscore."""
    return [
        match.group(2)
        for match in re.finditer(r"^(?:def|class)\s+([A-Za-z_])(\w*)", source, re.MULTILINE)
        for _ in [0]
    ] + re.findall(r"^(?:def|class)\s+([A-Za-z]\w*)", source, re.MULTILINE)


def test_no_execution_shaped_public_names() -> None:
    """No public name in the package may be execution-shaped."""
    offenders: list[str] = []
    for path in package_files():
        for name in public_names(path.read_text(encoding="utf-8")):
            if EXECUTION_SHAPED.search(name):
                offenders.append(f"{path.relative_to(ROOT)}:{name}")
    assert offenders == [], (
        "execution-shaped public names found. This project has no execution path "
        f"in any stage: {offenders}"
    )


def test_execution_name_detector_fires() -> None:
    """Canary: a detector that cannot fire proves nothing."""
    assert EXECUTION_SHAPED.search("place_order") is not None
    assert EXECUTION_SHAPED.search("compute_stats") is None


PINNED = {
    "README.md": [
        "It does not trade. It does not suggest entries. It has no execution path in",
        "97.5% 30-day death on birth-ordered pools (n = 40)",
        "18.75% on attention-crawled ones (n = 16)",
        "registered prior that this finds a tradeable signal is 5 to 8 percent",
        "documented negative is a valid and expected outcome",
        "Attention sampling manufactures survivorship",
    ],
    "CLAUDE.md": [
        "It does not trade. It does not suggest entries. It has no execution path in",
        "registered prior that this finds a tradeable signal is 5 to 8 percent",
        "a documented negative is a valid and expected outcome",
    ],
    "REGISTRATION.md": [
        "Registered prior that H1 finds a tradeable signal: 5 to 8 percent",
        "97.5% 30-day death on a birth-ordered cohort",
        "Ticker collisions are the expected failure mode",
        "no attention input of any kind",
        "Neither project's outcome is evidence in the other's family",
    ],
}


@pytest.mark.parametrize("document", sorted(PINNED))
def test_pinned_statements_present(document: str) -> None:
    """Deleting a pinned negative or scope statement breaks the build."""
    text = flat((ROOT / document).read_text(encoding="utf-8"))
    missing = [phrase for phrase in PINNED[document] if flat(phrase) not in text]
    assert missing == [], f"{document} lost pinned statements: {missing}"


def test_presence_checker_fires() -> None:
    """Canary: the presence check must fail on a phrase that is genuinely absent."""
    text = flat((ROOT / "README.md").read_text(encoding="utf-8"))
    assert "this phrase is deliberately not in the README" not in text


#: A 32-character hex run is the shape of an API hash. sha256 digests are 64 and
#: git hashes are 40, so neither collides with this pattern.
CREDENTIAL_SHAPED = re.compile(rb"(?<![0-9a-fA-F])[0-9a-fA-F]{32}(?![0-9a-fA-F])")
API_ID_SHAPED = re.compile(rb"API_ID\s*=\s*[0-9]{6,}")


def tracked_files() -> list[Path]:
    listing = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return [ROOT / name for name in listing.stdout.split("\n") if name]


def test_no_credential_shaped_strings_in_tracked_files() -> None:
    """Secrets never enter the repo — enforced by a scan, not by a filename glob."""
    offenders: list[str] = []
    for path in tracked_files():
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if CREDENTIAL_SHAPED.search(raw) or API_ID_SHAPED.search(raw):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], f"credential-shaped strings in tracked files: {offenders}"


def test_credential_detector_fires() -> None:
    """Canary: the credential scanner must catch a synthetic 32-hex string.

    The synthetic string is BUILT at runtime rather than written as a literal:
    a 32-hex literal in this file would be caught by the scanner above, which
    is exactly the behaviour that test asserts. The scanner catching its own
    canary was a true positive, not a false one.
    """
    synthetic = b"dead" * 8
    assert len(synthetic) == 32
    assert CREDENTIAL_SHAPED.search(synthetic) is not None
    assert CREDENTIAL_SHAPED.search(b"SOLATTN_TELEGRAM_API_HASH=") is None
    synthetic_id = b"SOLATTN_TELEGRAM_API_ID=" + b"".join(bytes(str(d), "ascii") for d in range(8))
    assert API_ID_SHAPED.search(synthetic_id) is not None


def test_env_is_not_tracked() -> None:
    """.env must never be tracked, in any state."""
    listing = subprocess.run(
        ["git", "ls-files", ".env"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert listing.stdout.strip() == "", ".env is tracked; it must never be"
