"""Command-line entry points.

Every command is read-only with respect to the outside world: it retrieves
public data and writes local files. **Nothing here places an order, sizes a
position, connects to a venue, or suggests an entry**, and no stage adds one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from solattn import registry, verify
from solattn.attention.channels import load_channels
from solattn.attention.collect import collect_all
from solattn.clock import SystemClock, day_str, utc_date
from solattn.config import load_settings
from solattn.http import PacedClient
from solattn.ledger import Ledger
from solattn.matching.daily import daily_counts, render_counts
from solattn.outcomes.checkpoints import run_checkpoints
from solattn.reporting import write_digest
from solattn.universe.watcher import sweep_once, watch_forever


def _client(settings: object, clock: SystemClock) -> tuple[PacedClient, Ledger]:
    from solattn.config import Settings

    assert isinstance(settings, Settings)
    ledger = Ledger(settings.vendor_dir() / "requests.jsonl", settings.daily_caps, clock)
    return PacedClient(ledger), ledger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="solattn",
        description=(
            "Evaluation-only measurement of social attention velocity against "
            "forward outcomes on a birth-ordered Solana pool universe. "
            "Does not trade; no execution path."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_verify = sub.add_parser("verify", help="measured access verification per source")
    p_verify.add_argument("--firehose-seconds", type=float, default=10.0)

    p_watch = sub.add_parser("watch", help="birth-ordered universe watcher")
    p_watch.add_argument("--once", action="store_true", help="one sweep, then exit")
    p_watch.add_argument("--minutes", type=float, default=0.0, help="run for N minutes")

    p_collect = sub.add_parser("collect", help="attention collectors")
    p_collect.add_argument("--seconds", type=float, default=60.0)

    sub.add_parser("checkpoint", help="outcome candle fetch at horizon checkpoints")

    p_counts = sub.add_parser("counts", help="daily sanity counts")
    p_counts.add_argument("--day", default="")

    p_report = sub.add_parser("report", help="write the committed daily digest")
    p_report.add_argument("--day", default="")

    args = parser.parse_args(argv)
    clock = SystemClock()
    settings = load_settings()
    for directory in (
        settings.manifests_dir(),
        settings.attention_dir(),
        settings.outcomes_dir(),
        settings.vendor_dir(),
        settings.state_dir(),
    ):
        directory.mkdir(parents=True, exist_ok=True)

    if args.command == "verify":
        client, _ = _client(settings, clock)
        with client:
            channels = [c.username for c in load_channels()]
            results = verify.run_all(client, clock, settings, channels, args.firehose_seconds)
        path = verify.write_table(results, clock, Path("docs/ACCESS.md"))
        for row in results:
            print(f"{'OK  ' if row.reachable else 'DROP'} {row.source:14} {row.measured_rate}")
        print(f"\nwrote {path}")
        return 0

    if args.command == "watch":
        client, _ledger = _client(settings, clock)
        with client:
            if args.once:
                found = sweep_once(client, clock, settings)
                print(json.dumps(found, indent=2, sort_keys=True))
            else:
                watch_forever(client, clock, settings, minutes=args.minutes or None)
        return 0

    if args.command == "collect":
        counts = collect_all(clock, settings, seconds=args.seconds)
        print(json.dumps(counts, indent=2, sort_keys=True))
        return 0

    if args.command == "checkpoint":
        client, _ = _client(settings, clock)
        with client:
            summary = run_checkpoints(client, clock, settings)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "counts":
        day = args.day or day_str(utc_date(clock.now()))
        print(render_counts(daily_counts(settings, day), day))
        return 0

    if args.command == "report":
        day = args.day or day_str(utc_date(clock.now()))
        path = write_digest(settings, clock, day)
        print(f"wrote {path}")
        return 0

    parser.error(f"unknown command {args.command}")
    raise SystemExit(2)  # parser.error already exits; this satisfies the type


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main", "registry"]
