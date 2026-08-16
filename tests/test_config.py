"""Settings: absent-or-blank secrets fail fast, naming the variable."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from solattn.config import MissingSecretError, Settings, load_settings


def clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.startswith("SOLATTN_"):
            monkeypatch.delenv(name, raising=False)


def test_blank_value_counts_as_absent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Arrange - the shape produced by copying .env.example without filling it in
    clear_env(monkeypatch)
    env = tmp_path / ".env"
    env.write_text("SOLATTN_TELEGRAM_API_ID=\nSOLATTN_TELEGRAM_API_HASH=   \n")
    # Act
    settings = load_settings(env)
    # Assert - absent, not a blank credential
    assert settings.has_telegram is False
    with pytest.raises(MissingSecretError, match="SOLATTN_TELEGRAM_API_ID"):
        settings.require_telegram()


def test_present_values_resolve(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    clear_env(monkeypatch)
    env = tmp_path / ".env"
    env.write_text("SOLATTN_TELEGRAM_API_ID=1234\nSOLATTN_TELEGRAM_API_HASH=abc\n")
    settings = load_settings(env)
    assert settings.require_telegram() == (1234, "abc")


def test_non_integer_api_id_raises_rather_than_guessing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_env(monkeypatch)
    env = tmp_path / ".env"
    env.write_text("SOLATTN_TELEGRAM_API_ID=not-a-number\n")
    with pytest.raises(ValueError, match="refusing to guess"):
        load_settings(env)


def test_malformed_env_line_raises_with_its_line_number(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clear_env(monkeypatch)
    env = tmp_path / ".env"
    env.write_text("# comment\nJUST_A_KEY\n")
    with pytest.raises(ValueError, match=r"\.env:2 is not a KEY=VALUE line"):
        load_settings(env)


def test_data_directories_hang_off_the_root() -> None:
    settings = Settings(Path("d"), None, None, "s", {})
    assert settings.manifests_dir() == Path("d/manifests")
    assert settings.vendor_dir() == Path("d/vendor")
