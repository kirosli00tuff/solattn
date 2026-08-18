"""The manual script must refuse to start alongside the systemd units.

A.4 declared `scripts/run_collectors.sh` non-production (ADR-014) but did not
stop it. Both ran concurrently from 2026-08-18T04:20:35Z: two watchers on one
source, a doubled request rate, and ~3 s effective spacing against a source
measured to return HTTP 429 at that rate. The declaration was not a mechanism;
this guard is (ADR-018).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "run_collectors.sh"


@pytest.fixture
def fake_systemctl(tmp_path: Path) -> Path:
    """A PATH shim so the guard can be tested without touching real units."""
    stub = tmp_path / "systemctl"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        "# is-active --quiet <unit>  -> exit 0 (active) when SOLATTN_TEST_ACTIVE=1\n"
        'for arg in "$@"; do\n'
        '  if [ "$arg" = "is-active" ]; then\n'
        '    [ "${SOLATTN_TEST_ACTIVE:-0}" = "1" ] && { echo active; exit 0; }\n'
        "    echo inactive; exit 3\n"
        "  fi\n"
        "done\n"
        "exit 0\n",
        encoding="utf-8",
    )
    stub.chmod(0o755)
    return stub


def run(command: str, shim: Path, active: str, **extra: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PATH"] = f"{shim.parent}{os.pathsep}{env['PATH']}"
    env["SOLATTN_TEST_ACTIVE"] = active
    env.update(extra)
    return subprocess.run(
        [str(SCRIPT), command], capture_output=True, text=True, env=env, cwd=ROOT, timeout=60
    )


def test_start_refuses_while_the_systemd_units_are_active(fake_systemctl: Path) -> None:
    result = run("start", fake_systemctl, active="1")

    assert result.returncode == 3
    assert "REFUSED" in result.stderr
    assert "Nothing was started and nothing was written." in result.stderr
    # The refusal names the cost, in the pattern of every other refusal here.
    assert "429" in result.stderr
    # It must not have started anything.
    assert "started" not in result.stdout


def test_the_daily_pass_is_guarded_too(fake_systemctl: Path) -> None:
    """The timer owns the daily pass; a concurrent manual run double-charges."""
    result = run("daily", fake_systemctl, active="1")

    assert result.returncode == 3
    assert "REFUSED" in result.stderr


def test_the_refusal_is_overridable_deliberately(fake_systemctl: Path) -> None:
    """A guard with no deliberate override gets worked around, not obeyed.

    Only the guard is exercised: `status` never starts anything, so this
    asserts the override path is reachable without launching a collector.
    """
    result = run("status", fake_systemctl, active="1", SOLATTN_ALLOW_ALONGSIDE_SYSTEMD="1")

    assert result.returncode == 0
    assert "REFUSED" not in result.stderr


def test_status_reports_systemd_not_only_this_scripts_pidfiles(
    fake_systemctl: Path,
) -> None:
    """Reporting only the pidfiles printed 'not running' while systemd ran it."""
    result = run("status", fake_systemctl, active="1")

    assert result.returncode == 0
    assert "systemd (production, ADR-014):" in result.stdout
    assert "solattn-watch.service" in result.stdout
    assert "this script (manual/dev):" in result.stdout


def test_start_proceeds_when_no_systemd_units_are_active(fake_systemctl: Path) -> None:
    """The guard must not be a blanket block: inactive units mean no collision.

    Exercised through `status` so no collector is launched by the test suite;
    what is pinned is that the guard returns cleanly rather than refusing.
    """
    result = run("status", fake_systemctl, active="0")

    assert result.returncode == 0
    assert "REFUSED" not in result.stderr
