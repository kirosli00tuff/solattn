#!/usr/bin/env bash
# Run the solattn collectors continuously.
#
# Everything here is read-only with respect to the outside world: it retrieves
# public data and writes local files. Nothing places an order, connects to a
# venue, or suggests an entry.
#
#   ./scripts/run_collectors.sh start   # start watcher + attention collectors
#   ./scripts/run_collectors.sh stop    # stop them
#   ./scripts/run_collectors.sh status  # what is running
#   ./scripts/run_collectors.sh daily   # one checkpoint + digest pass (cron this)
#
# Durability is the operator's call. For a machine that reboots, wrap `start`
# in a systemd unit or a tmux session — a gap in a forward-recorded cohort
# cannot be backfilled, which is the whole reason this project records forward.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/state

#: The units that own production (ADR-014). This script is a manual/dev tool.
SYSTEMD_UNITS="solattn-watch.service solattn-collect.service solattn-daily.timer"

# Refuse to start anything while systemd already owns it.
#
# A.4 declared this script non-production but did not stop it, and from
# 2026-08-18T04:20:35Z both ran concurrently: two watchers against one source,
# a doubled request rate, and ~3 s effective spacing against a source measured
# to return HTTP 429 at that rate. The guard exists so the same collision
# cannot recur on the next manual restart (ADR-018).
refuse_if_systemd_active() {
  [ -n "${SOLATTN_ALLOW_ALONGSIDE_SYSTEMD:-}" ] && return 0
  command -v systemctl >/dev/null 2>&1 || return 0
  active=""
  for unit in $SYSTEMD_UNITS; do
    if systemctl --user is-active --quiet "$unit" 2>/dev/null; then
      active="$active $unit"
    fi
  done
  [ -z "$active" ] && return 0
  cat >&2 <<EOF
REFUSED: systemd already owns the collectors. Active:$active

ADR-014 made the systemd user units the production mechanism and this script a
manual/dev tool. Starting it alongside them runs a SECOND watcher against one
source: measured on 2026-08-18, that doubled the request rate and halved the
effective spacing to ~3 s, against a source that returns HTTP 429 at that rate.

Nothing was started and nothing was written.

Stop the units first, deliberately:
    systemctl --user stop$active

Or, for a deliberate side-by-side run:
    SOLATTN_ALLOW_ALONGSIDE_SYSTEMD=1 $0 $1
EOF
  return 1
}
WATCH_PID=data/state/watcher.pid
COLLECT_PID=data/state/collector.pid
DAILY_PID=data/state/daily.pid
LOG=data/state

start() {
  refuse_if_systemd_active start || exit 3
  if [ -f "$WATCH_PID" ] && kill -0 "$(cat "$WATCH_PID")" 2>/dev/null; then
    echo "watcher already running (pid $(cat "$WATCH_PID"))"
  else
    nohup uv run python -m solattn.cli watch >>"$LOG/watcher.log" 2>&1 &
    echo $! >"$WATCH_PID"
    echo "watcher started (pid $(cat "$WATCH_PID"))"
  fi

  if [ -f "$COLLECT_PID" ] && kill -0 "$(cat "$COLLECT_PID")" 2>/dev/null; then
    echo "collector already running (pid $(cat "$COLLECT_PID"))"
  else
    nohup bash -c 'while true; do uv run python -m solattn.cli collect --seconds 300 >>"data/state/collector.log" 2>&1 || sleep 30; done' \
      >>"$LOG/collector.log" 2>&1 &
    echo $! >"$COLLECT_PID"
    echo "collector started (pid $(cat "$COLLECT_PID"))"
  fi

  if [ -f "$DAILY_PID" ] && kill -0 "$(cat "$DAILY_PID")" 2>/dev/null; then
    echo "daily loop already running (pid $(cat "$DAILY_PID"))"
  else
    # The daily pass, under the same supervision discipline as the watcher:
    # run once immediately (a missed day self-heals via the checkpoint
    # catch-up window), then once per UTC day at ~00:40Z, when the previous
    # day's final candle exists. The checkpoint CLI writes its own lifecycle
    # markers, so every run is visible downtime-or-work in the same log.
    nohup bash -c '
      while true; do
        uv run python -m solattn.cli checkpoint >>data/state/daily.log 2>&1
        uv run python -m solattn.cli counts     >>data/state/daily.log 2>&1
        uv run python -m solattn.cli report     >>data/state/daily.log 2>&1
        now=$(date -u +%s)
        next=$(date -u -d "tomorrow 00:40" +%s)
        sleep $(( next - now ))
      done' >>"$LOG/daily.log" 2>&1 &
    echo $! >"$DAILY_PID"
    echo "daily loop started (pid $(cat "$DAILY_PID"))"
  fi
}

stop() {
  for pidfile in "$WATCH_PID" "$COLLECT_PID" "$DAILY_PID"; do
    [ -f "$pidfile" ] || continue
    pid=$(cat "$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      pkill -P "$pid" 2>/dev/null || true
      kill "$pid" 2>/dev/null || true
      echo "stopped $(basename "$pidfile" .pid) (pid $pid)"
    fi
    rm -f "$pidfile"
  done
}

status() {
  # systemd first: it owns production, so reporting only this script's pidfiles
  # would print "not running" while the collectors are in fact running.
  if command -v systemctl >/dev/null 2>&1; then
    echo "systemd (production, ADR-014):"
    for unit in $SYSTEMD_UNITS; do
      printf '  %-28s %s\n' "$unit" "$(systemctl --user is-active "$unit" 2>/dev/null || true)"
    done
  fi
  echo "this script (manual/dev):"
  for pidfile in "$WATCH_PID" "$COLLECT_PID" "$DAILY_PID"; do
    name=$(basename "$pidfile" .pid)
    if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      printf '  %-28s running (pid %s)\n' "$name" "$(cat "$pidfile")"
    else
      printf '  %-28s not running\n' "$name"
    fi
  done
}

daily() {
  refuse_if_systemd_active daily || exit 3
  uv run python -m solattn.cli checkpoint
  uv run python -m solattn.cli counts
  uv run python -m solattn.cli report
}

case "${1:-status}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  daily) daily ;;
  *) echo "usage: $0 {start|stop|status|daily}" >&2; exit 2 ;;
esac
