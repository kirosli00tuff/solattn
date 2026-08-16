# CLAUDE.md — solattn operating manual

Read this file at the start of every coding session. It is the contract for how
work happens in this repository.

## What this project is (permanent, stated from the first commit)

> **solattn is an evaluation-only measurement of whether social attention
> velocity predicts forward outcomes on an independently enumerated,
> birth-ordered Solana token universe.**
>
> **It does not trade. It does not suggest entries. It has no execution path in
> any stage.** There is no wallet, no signer, no order, no venue connection, no
> position, and no stage in which one is planned. The output is a measurement
> and a documented verdict.
>
> **The prior evidence travels with it.** solclear measured **97.5% 30-day
> death on birth-ordered pools (n = 40) against 18.75% on attention-crawled
> ones (n = 16)** — a 60-point gap produced by nothing but which pages a
> crawler chose to archive. **Attention sampling manufactures survivorship.**
> Peer-reviewed post-promotion return paths are negative within days.
>
> **The registered prior that this finds a tradeable signal is 5 to 8 percent.**
> The product is the bias-controlled measurement either way, and **a documented
> negative is a valid and expected outcome.**

The scope is encoded in the build, not only in prose: `tests/test_honesty.py`
scans the package for execution-shaped names and pins the statements above in
`README.md`, `CLAUDE.md`, and `REGISTRATION.md`. Deleting one breaks the build.
That is the intent, not an obstacle to route around.

## Give a measured ETA for every task (standing rule)

**Every prompt gets an ETA per task, up front, before any work is armed.** The
ETA must be **measured, not guessed**: run a small probe, read the actual pace
(requests/second, pools/day, messages/second, pages/token), and derive the
estimate from it — the C.1 rule that measured beats documented, applied to
time. State the assumption the number rests on ("at the probe's 0.17 req/s") so
a wrong ETA is debuggable rather than mysterious. When pace is high-variance,
give a range and say what drives the spread. Re-quote an ETA from the ledger or
the log, never from the original guess.

A task whose duration is set by the calendar rather than by effort (a maturing
horizon, a 24-hour collection day) states the **clock date** it completes, not
an effort estimate, and says plainly that it cannot be compressed.

## Non-negotiable rules

1. **The scope statement above.** No function, doc, artifact, or release may
   place an order, size a position, suggest an entry, or describe an execution
   path. Pinned by `tests/test_honesty.py`.
2. **Pre-register before results.** Decide the universe, the metric, the
   windows, the horizons, the bars, the trial count, and the kill criteria
   before the data is seen. A result read against a bar chosen afterward is not
   a result. `REGISTRATION.md` is the registration; it is append-only, and an
   amendment is dated, reasoned, and states what data existed when it was made.
3. **Secrets never enter the repo.** No API keys, hashes, tokens, or passwords
   in source, config, fixtures, or history. Secrets come only from environment
   variables (see `.env.example`); `solattn/config.py` raises naming the
   missing variable. `tests/test_honesty.py` scans every tracked file for
   credential-shaped strings, so a leak breaks the build rather than shipping.
4. **A request ledger with caps, even for free APIs.** Free tiers have limits,
   and a gate that never fires is still a gate. Every outbound request is
   counted against a per-source daily cap before it is sent; the ledger is
   append-only on disk and re-read on start, so a restart cannot walk past the
   cap. A refusal names the arithmetic and writes nothing.
5. **The daily manifests are immutable.** A manifest, once closed and hashed,
   is never rewritten. Corrections are appended as new records with their own
   retrieval time, never edits in place.

## Standing practices (ported from MLCryptoEngine and solclear, defect-earned)

- **Measured behaviour beats documentation.** A published rate limit, a
  documented page size, a claimed endpoint — none of these is believed until a
  probe measures it. solclear's GeckoTerminal probe 429'd at the documented
  30/min and held only at 6 s spacing; the registered pacing here comes from
  that measurement, not from the docs.
- **Union time intervals before summing.** Never add durations from a list of
  windows that might overlap — merge first (`solattn/intervals.py`), and any
  new interval arithmetic carries a test with at least one overlapping pair.
  Three separate parent-project defects came from exactly that shape: a list, a
  `sum()`, no union. It never raises; it silently returns a number too large.
- **Never trust append order across processes.** Two processes appending to one
  file interleave. Order by the recorded clock, never by file position. Every
  reader in `solattn/jsonl.py` sorts by the record's own timestamp.
- **Refusals fail closed.** A source that cannot be verified is reported and
  dropped, not worked around. A pool whose retrieval was incomplete is not
  scored. An ambiguous match is attributed to nobody. In every case the
  refusal is a first-class recorded outcome with a reason, never a silent skip
  and never a plausible-looking default.
- **Known-answer tests before trusting a pipeline.** A new retrieval or metric
  path reproduces a previously measured answer before its output is believed.
- **A negative with a hidden n is not a result.** Every claim in this
  repository carries its sample size in the same sentence as its number.

## Directory map

```
solattn/
  registry.py        Every registered constant, in one place — the registration in code
  config.py          Env-backed settings; secrets fail fast, naming the variable
  clock.py           The only source of wall-clock time; UTC, injectable for tests
  intervals.py       merge_windows — union before summing
  ledger.py          Per-source request ledger with daily caps; append-only, restart-proof
  http.py            Paced keyless HTTP client, ledger-gated (unmetered calls unavailable)
  jsonl.py           Append-only JSONL store; clock-ordered reads; sha256 manifest sealing
  lifecycle.py       Lifecycle markers and restart-proof cursor state
  records.py         Frozen record types (PoolBirth, Mention, Candle, MatchCounts, ...)
  sources/           One module per external source; each verifies itself
  universe/          Birth-ordered watcher; immutable daily manifests
  attention/         Registered ingest filter; window/velocity/quintile metrics
  matching/          The registered matching rules; matched / ambiguous / unmatched
  outcomes/          Horizon checkpoints, death floor, net return, SOL benchmark leg
  cli.py             Entry points: verify, watch, collect, checkpoint, counts, report
data/manifests/      Immutable daily birth manifests (machine-local, gitignored)
data/attention/      Append-only mention records (machine-local, gitignored)
data/outcomes/       Fetched candles and computed outcomes (machine-local, gitignored)
data/vendor/         Request ledger (machine-local, append-only, gitignored)
docs/digests/        Committed daily digests: counts and manifest sha256, not raw rows
tests/               Pytest suite; test_honesty.py and test_registration.py are load-bearing
```

## Coding standards

- Python 3.12+; type hints on all function signatures; `ruff format`,
  `ruff check`, and `mypy --strict` must pass clean.
- Anything with logic gets a pytest test. Real tests, not smoke tests.
- Errors are handled explicitly; never silently swallow an exception. An error
  must never quietly become a data condition.
- Immutable data patterns: frozen dataclasses, pure functions over records.
- Many small focused modules over few large ones; 200–400 lines typical.

## Git commit conventions

Conventional commits: `<type>: <description>` with type in
`feat, fix, refactor, docs, test, chore, perf, ci`. Imperative mood, lower
case, no trailing period. One deliverable or coherent change per commit.

## Read these first

- `REGISTRATION.md` — the pre-registration. Read before proposing any analysis.
  Nothing in it may be revised to fit a result.
- `README.md` — what this measures and what it does not.
- `DECISIONS.md` — append-only ADR log; read before revisiting a settled
  question.
- `progress.md` — where the project is right now (newest stage first).
- `docs/ACCESS.md` — the measured access table per source, with dates.
