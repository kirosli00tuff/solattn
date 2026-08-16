"""Environment-backed settings. Secrets fail fast, naming the variable.

An empty or whitespace-only value is treated as ABSENT, not as a blank
credential: copying .env.example without filling it in must fail loudly rather
than send unauthenticated requests. This is the fix solclear made in its
Stage F after the opposite behaviour shipped.

No credential in this project has any capability beyond reading public data.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from solattn import registry


class MissingSecretError(RuntimeError):
    """Raised when a required credential is absent, naming the variable."""

    def __init__(self, variable: str, purpose: str) -> None:
        super().__init__(
            f"{variable} is absent or empty. It is required to {purpose}. "
            f"Set it in .env (see .env.example); it is never read from anywhere else."
        )
        self.variable = variable


def _clean(raw: str | None) -> str | None:
    """Whitespace-only counts as absent."""
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped or None


def _load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines from .env into the process environment.

    Existing environment variables win, so an explicit export always overrides
    the file. Malformed lines raise rather than being skipped silently.
    """
    if not path.is_file():
        return
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError(f"{path}:{lineno} is not a KEY=VALUE line")
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    """Resolved configuration. Constructed once, at the edge, never mutated."""

    data_root: Path
    telegram_api_id: int | None
    telegram_api_hash: str | None
    telegram_session: str
    daily_caps: dict[str, int]

    @property
    def has_telegram(self) -> bool:
        return self.telegram_api_id is not None and self.telegram_api_hash is not None

    def require_telegram(self) -> tuple[int, str]:
        """Return the MTProto credential pair, or raise naming what is missing."""
        if self.telegram_api_id is None:
            raise MissingSecretError(
                "SOLATTN_TELEGRAM_API_ID", "read public Telegram channels over MTProto"
            )
        if self.telegram_api_hash is None:
            raise MissingSecretError(
                "SOLATTN_TELEGRAM_API_HASH", "read public Telegram channels over MTProto"
            )
        return self.telegram_api_id, self.telegram_api_hash

    def manifests_dir(self) -> Path:
        return self.data_root / "manifests"

    def attention_dir(self) -> Path:
        return self.data_root / "attention"

    def outcomes_dir(self) -> Path:
        return self.data_root / "outcomes"

    def vendor_dir(self) -> Path:
        return self.data_root / "vendor"

    def state_dir(self) -> Path:
        return self.data_root / "state"


def load_settings(env_file: Path | None = None) -> Settings:
    """Resolve settings from .env plus the process environment."""
    _load_dotenv(env_file if env_file is not None else Path(".env"))

    raw_id = _clean(os.environ.get("SOLATTN_TELEGRAM_API_ID"))
    api_id: int | None = None
    if raw_id is not None:
        try:
            api_id = int(raw_id)
        except ValueError as exc:
            raise ValueError(
                "SOLATTN_TELEGRAM_API_ID must be an integer; refusing to guess"
            ) from exc

    caps = dict(registry.DAILY_CAPS)
    for source in caps:
        override = _clean(os.environ.get(f"SOLATTN_{source.upper()}_DAILY_CAP"))
        if override is not None:
            caps[source] = int(override)

    return Settings(
        data_root=Path(_clean(os.environ.get("SOLATTN_DATA_ROOT")) or "data"),
        telegram_api_id=api_id,
        telegram_api_hash=_clean(os.environ.get("SOLATTN_TELEGRAM_API_HASH")),
        telegram_session=_clean(os.environ.get("SOLATTN_TELEGRAM_SESSION")) or "solattn",
        daily_caps=caps,
    )
