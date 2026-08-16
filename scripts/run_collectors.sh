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
WATCH_PID=data/state/watcher.pid
COLLECT_PID=data/state/collector.pid
LOG=data/state

start() {
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
}

stop() {
  for pidfile in "$WATCH_PID" "$COLLECT_PID"; do
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
  for pidfile in "$WATCH_PID" "$COLLECT_PID"; do
    name=$(basename "$pidfile" .pid)
    if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      echo "$name: running (pid $(cat "$pidfile"))"
    else
      echo "$name: not running"
    fi
  done
}

daily() {
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
