# progress.md — where solattn is right now

Newest entry first. Every stage states its ETAs **before** the work is armed
(CLAUDE.md standing rule) and re-quotes them from measurement afterward.

---

## Stage A — registration, scaffold, access verification, collectors live — 2026-08-16

### Task 0 — the registration (this commit)

`REGISTRATION.md` is committed **before any collector exists**. At the moment
it was written no collector had been built, no request had been sent to any
attention source, no pool had been enumerated, and no outcome existed. It
registers, in advance and in full:

- **the universe rule** — every new Solana AMM pool observed at birth from
  GeckoTerminal's keyless public `new_pools` feed, birth-ordered, **no
  attention input of any kind in the enumeration**, with venue class recorded
  as a tag from a launch-venue denylist so nothing is discarded at collection
  time and the analysis filter predates the data;
- **the expected daily count** — ~1,330 AMM pools/day and ~9,000 full-feed
  pools/day from solclear's Stage B addendum (measured 2026-08-13, n = 122),
  with a **>2× disagreement reported and never averaged away**;
- **the attention metric ex ante** — `mentions(w)`, `authors(w)` and the five
  registered statistics `v1 / v6 / v24 / ua24 / accel` over trailing 1h / 6h /
  24h windows from pool birth, **mechanical only, no LLM judgment in Stage A**,
  with the within-birth-day quintile construction, its tie-breaks, and the
  degenerate-cohort fallback all fixed now;
- **the matching rules** — mint-address exact match primary; cashtag and name
  secondary; **a cashtag matching more than one active mint is `ambiguous` and
  attributed to nobody**, counted as its own first-class daily output.
  **Ticker collisions are named as the expected failure mode**;
- **horizons and bars** — 1/3/7 days primary, 30 secondary; entry at the
  `d0+2` daily candle so **no return bar overlaps the attention window**;
  solclear's death floor ported (no volume-bearing candle in the trailing 14
  days, or exit below 1% of entry, books −100%, deaths stay in their quintile);
  the 300–600 bps cost band with 450 bps central; **top-quintile return against
  the birth-ordered cohort base rate**, day-clustered bootstrap, **40 trials
  counted and deflated** with `(7d, v24, mint-exact)` designated primary;
- **the kill criteria** — no distinguishable lift (95% interval includes zero)
  **or** lift entirely inside the cost band closes the hypothesis;
- **the survivorship audit as a first-class output** — the death-rate gap
  between birth-ordered and attention-selected subsets reported alongside every
  result, at every horizon, with its n, and a >15-point gap meaning the
  headline rests on the birth-ordered subset alone;
- **hypothesis-family separation** — attention and flow reflexivity, distinct
  from AiTrader's news-drift (information incorporation) family, with its own
  bars, and **neither project's outcome is evidence in the other's family**;
- **channel-selection bias named plainly** — the list fixed at registration by
  an objective rule (top 20 public Solana/memecoin channels by membership from
  a stated directory on a stated date) and **never edited mid-collection**;
- **the ingest filter**, registered with the registration because a filter is
  part of the instrument, and deliberately **shape-dominant** (mint-shaped and
  cashtag-shaped strings) so it cannot privilege particular tokens.

**The registered prior that this finds a tradeable signal is 5 to 8 percent,
and a documented negative is a valid and expected outcome.**

ADRs recorded with the registration: **ADR-001** (birth-ordered enumeration,
attention never touches it), **ADR-002** (venue class as a recorded tag from a
denylist), **ADR-003** (request ledger with daily caps, free APIs included),
**ADR-004** (mechanical attention, no LLM), **ADR-005** (ambiguous matches
attributed to nobody), **ADR-006** (the `d0+2` return anchor), **ADR-007**
(the fixed channel list).

### ETAs for Stage A, stated before the work was armed

Baseline for the estimate: solclear's Stage A ran ~6.5 h across ten tasks and
its Stage B ~1.5 h across six; this stage's document set is larger and its
network work is dominated by rate-limit pacing rather than by thinking.

| task | scope | ETA | what the number rests on |
|---|---|---|---|
| 0 | registration + first commit | 25–35 min | document volume; no network |
| 1 | scaffold (uv, ruff, mypy, pytest, pre-commit, Makefile, env template) | 20–30 min | solclear's scaffold as the template |
| 2 | access verification, measured, per source | 45–70 min | **network-bound**; the spread is driven by how many Farcaster hosts must be probed before one verifies, at ~2 s per probe |
| 3 | enumeration watcher + outcome checkpoints + SOL benchmark leg | 40–60 min | ~6 modules at solclear's observed pace |
| 4 | matching layer + daily counts | 25–35 min | 2 modules + tests |
| 5 | go live and sanity-count | **clock-bound, not effort-bound** | the first-day report needs a full UTC day of collection and completes on the calendar, not on effort |
| 6 | report, lint/typecheck/test, commit, push | 20–30 min | solclear's measured ~15 min for the same three gates plus this repo's larger doc set |

**Total active build ≈ 3–4.5 h.** Task 5's first-day report cannot be
compressed: it completes one full UTC day after the collectors start.

---

## Stage A.3 — the outcome path known-answer tested ahead of its first fire — 2026-08-17

*A verification, not an amendment: the registration, the trial grid, the channel
list, the matching rules, the metric, the horizons, the death floor and the
cost band were not touched, and no trial was added. No cohort outcome was
observed — every KAT pool was born 2023–2024, out of cohort by construction.
Collectors stayed live throughout. ETAs (20–25 / 15–20 / 15–20 / 20–25 min)
held. `make lint`, `make typecheck`, `make test` green (**99 tests**).*

### Task 1 — the known-answer set, with provenance

Resolved from solclear's pre-registered Stage B addendum mints (committed there
before any outcome existed) plus WIF as the known survivor, mint → earliest
pool via the keyless token-pools endpoint, every request through the gated
paced client:

| class | pool | provenance | born | candles served |
|---|---|---|---|---|
| died-in-window | `4g7CkmDQ…` | solclear hard_rug `7CSWFsrB…pump` (documented, in-holdout) | 2024-10-11 | 57 sparse over 517 d |
| alive-past-30d | `EP2ib6dY…` | WIF earliest pool | 2023-11-20 | 181 continuous |
| sparse non-contiguous | `2YLJcB5v…` | solclear honest_candidate `gYgUiBNG…pump` | 2024-07-03 | 18 over 449 d |
| single-candle | `4i53RDoG…` | same mint's 2nd pool | 2024-07-04 | 1 |
| sparse dead | `HHu4yVFW…` | solclear honest_candidate `CP1KFKft…` | 2024-09-25 | 35 over 495 d |
| no-candle (a) | 404 address probe | dead mint address used as pool id | — | `None` (source unavailable) |
| no-candle (b) | empty list → `measure()` | direct | — | 0 |

**Anchor note, stated plainly.** GeckoTerminal's keyless daily OHLCV serves a
trailing window only — the three 2024 pools' first served candle clusters at
2025-03-14/17, WIF's pool serves exactly 181 days, and paging past the window
with `before_timestamp` returns **HTTP 401** (deep history is auth-gated at the
vendor; measured, not inferred). True birth anchors are therefore unreachable
for old pools, so the KAT anchors at `d0_kat = first_served_day − 2` and
verifies the **path's retrieval, parsing, anchoring, death-floor and return
arithmetic on real vendor data** rather than reproducing true birth returns.
The production path is unaffected: cohort fetches happen at T0+10d, far inside
any horizon. A first anchor choice (`d0_kat = first_served_day`) left the death
branches unexercised — four of five pools landed UNMEASURABLE — and was
corrected, because **a KAT whose interesting branches never fire proves nothing
about them**; both runs are recorded.

### Task 2 — expected values, independent route, tolerance stated first

Own fetch, own JSON parse, own arithmetic implementing REGISTRATION.md §4's
text directly (entry = close at d0+2; exit = close at d0+2+h; death iff no
volume-bearing candle in the 14 days ending at exit or exit < 1% of entry;
net = (1+g)(1−0.0225)² −1; deaths net exactly −100%). Only the paced transport
is shared, because the 6 s pacing is a measured limit that binds any client.
**Tolerance, stated before comparing:** dates exact; verdicts exact;
returns |Δ| ≤ 1e-9; candle counts exact with one re-fetch on vendor revision.

### Task 3 — comparison: 0 hard mismatches; one specification gap, surfaced 13 times

40 cells across two runs (5 pools × 4 horizons × 2 anchor rules), plus the two
no-candle probes and the benchmark leg. Every comparable cell **MATCH**:

- **ALIVE returns match to ≤ 1e-9 in all 6 cells** (WIF ×4; hard-rug pool
  h=7: −0.060664, h=30: −0.091383 — both routes identical).
- **Horizon instants land exactly where §4 says in all 40 cells**
  (entry = d0+2, exit = d0+2+h; `dates_ok=True` everywhere).
- **`DEAD:no_volume_in_lookback` fires exactly where the independent §4
  arithmetic fires it** (single-candle pool, h=30), at the registered 14-day
  threshold.
- **The no-candle cases do the right thing, explicitly checked:** a 404
  address returns `None` — *source unavailable*, not marked done, retried by
  the catch-up window; an empty candle list produces
  `measurable=False, gross=None, net=None, reason=no_entry_mark` — **no silent
  zero and no dropped row**, the two failures that would have mattered most.
- **Benchmark leg** (coinbase, independent arithmetic on the path-fetched
  series): SOL +0.011035 (1d) / +0.044017 (3d) / +0.079696 (7d) / +0.101275
  (30d) over the WIF anchors; spans outside the served window are reported as
  outside, never zeroed.
- **Not exercised on real data: `dust_close`.** No KAT cell's exit close fell
  below 1% of entry. The branch is pinned at the registered 1% threshold by
  `tests/test_returns.py::test_dust_close_books_a_total_loss`; stated here so
  the KAT is not read as having reached it.

**The specification gap (13 of 40 cells, and it will bind on the cohort).**
§4's death floor states two conditions: (a) no volume-bearing candle in the 14
days ending at the exit date; (b) exit close below 1% of entry. It is **silent**
on the case the sparse pools hit constantly: **the exit-day candle is missing
while volume exists inside the lookback** (the pool traded recently, then not
on the exit day). The code books this **`DEAD:no_exit_candle` = −100%**, which
follows the registered rationale (a missing daily candle means zero trades that
day; no trades at exit means no exit liquidity, exactly the dust-close logic)
— but the registration does not say it. Per the report-rather-than-choose rule
this is recorded as a gap, not silently ratified: **it needs a one-line
amendment before Stage B reads any outcome — deadline 2026-08-26** — either
adopting the code's conservative reading (recommended; it is the rationale's
own extension) or defining an alternative. Until amended, the code's behaviour
stands unchanged and this entry is the notice of it. Frequency on KAT data: 13
of 20 sparse-pool cells, so on a cohort that solclear's priors say is ~97.5%
dead at 30 days, this case is the **norm, not the edge**.

### Task 4 — one defect found and fixed, in the outcome path only

**Defect: a transient fetch failure at checkpoint time became permanent silent
data loss.** `fetch_daily_candles` returned `[]` for *both* "the source
answered: no candles" and "the source did not answer" (429/5xx/transport), and
`run_checkpoints` then marked the pool done-with-0-candles either way — never
to be refetched. A rate blip on 2026-08-26 would have silently discarded that
pool's outcomes. **Cause:** an error collapsed into a data condition, the exact
shape CLAUDE.md forbids and ADR-012 distinguishes (absent data vs measured
absence). **Fix:** `fetch_daily_candles` returns `None` for
source-unavailable and `[]` only for an answered empty; `run_checkpoints`
marks done only on an answer, counts `unavailable_retrying`, writes an
`error` lifecycle marker, and the 5-day catch-up window retries. Pinned by
three new tests in `tests/test_checkpoints.py` (unavailable → not done +
retried; answered-empty → done with 0; answered-candles → stored + done).

**Verdict: the outcome path is verified ahead of its 2026-08-26 first fire** —
retrieval, parsing, anchoring, horizon instants, the death floor at its
registered thresholds, cost arithmetic and the benchmark leg all reproduce the
independently derived answers within the stated tolerance, with the
`no_exit_candle` specification gap documented above as the one item requiring
a registration decision before any outcome is read.

### Maturity dates — unchanged

**2026-08-27** (7-day analysis), **2026-09-19** (30-day). No analysis before
those dates.

---

## Amendment 2 — per-source attention reporting, registered before maturity — 2026-08-17

*ETA stated before arming (25–35 / 30–40 / 20–25 min); held. `make lint`,
`make typecheck`, `make test` green (**94 tests**). Collectors stayed live and
untouched throughout.*

### Task 1 — mechanical characterisation, proxies stated before computing

P1 = rows ÷ distinct authors. P2 = share of rows from the single most active
author id. P3 = share of sampled messages with ≥ 3 distinct cashtags **or**
(cashtag + mint-address characters) ÷ total characters > 0.30, using the
registered filter's own regexes on a fresh bounded sample (raw text is
deliberately not persisted). P4 = persisted `match_kind` distribution. **No
channel was classified by hand or by judgment.**

| | telegram | bluesky | farcaster |
|---|---|---|---|
| rows (persisted, 2 days) | 65 | 6,725 | 1,174 |
| distinct authors | **4** | **3,077** | 410 |
| P1 rows/author | **16.25** | **2.19** | 2.86 |
| P2 top-author share | 0.308 | 0.050 | 0.273 |
| channels producing rows | 4 of 20 | 1 (firehose) | 1 (hub) |
| P3 dominance share | **0.153** (n = 680) | 0.111 (n = 18) | 0.286 (n = 7) |
| P4 ambiguous | **0.831** | 0.240 | 0.205 |
| P4 unmatched | **0.031** | 0.487 | 0.541 |
| P4 mint-exact | 0.000 | 0.001 | 0.000 |

**P3 is a measurement for Telegram only.** The firehose samples (n = 18 and
n = 7 passing the ingest filter in the sampling window) are too small to
distinguish any share; those figures are recorded for completeness and are
**not** results. A share with n = 7 is not a result.

Two contrasts do not rest on the weak proxy: **16.25 rows/author from 4
authors versus 2.19 from 3,077**, and an unmatched share of **0.031 versus
0.487** — nearly everything Telegram emits matches the token vocabulary, the
signature of a feed that names tokens by construction. This is a factual
description of what each source emits, **not a quality ranking**; no source was
dropped, down-weighted, or preferred in collection because of it.

### Task 2 — Amendment 2, registered before any outcome existed

At writing: attention rows existed for all three sources; **no outcome existed
and none was looked at** (`data/outcomes/` empty, the single checkpoint run
recorded `pools_due 0`, first maturity 2026-08-26). Registered:

- **The primary attention metric is computed and reported per source.**
- **A pooled series is reported as a registered SECONDARY, never primary** —
  reported rather than suppressed, because hiding the comparison would be its
  own distortion.
- **The designated primary trial becomes `(7d, v24, mint-exact, bluesky)`**,
  Bluesky on the mechanical ground that it is the only series aggregating many
  independent emitters (3,077 authors, top-author share 0.050).
- **Trial grid: 4 × 5 × 2 × 4 = 160** (was 40). One primary trial at α = 0.05;
  the other 159 against **Šidák α_adj = 0.000321** (was 0.00128). The grid may
  not grow again without a further amendment and a new cohort.
- **Every Telegram figure ships labelled `alert-feed-dominated`** with its
  characterisation numbers attached.
- **The under-detection direction is registered now**: a narrow
  alert-dominated instrument under-samples community attention, biasing the
  association **toward the null** — so a negative on Telegram or any pooled
  series carries an under-detection caveat, and a positive is not inflated by
  this weakness. Registered before results so it cannot later be produced as a
  rationalisation.

Pinned in the build: `tests/test_registration.py` now asserts the grid size,
the series tuple, the new primary trial, the deflated α, the
`alert-feed-dominated` label, the under-detection sentences, and that
Amendment 2 sits after Amendment 1 in the append-only log.

### Confirmation: nothing collected was altered

**No bar, rule, list or metric was changed.** The channel list remains frozen
under §7's never-edit rule — Telegram has collected since 2026-08-17T04:28Z, so
it stays fixed regardless of what the characterisation showed. Unchanged and
test-pinned: attention windows (1/6/24 h), horizons (1/3/7 + 30), death floor
(14 d, 1%), cost band (450 central, 300/600), channel-list size (20), matching
rules, ingest filter, universe rule. Amendment 2 changes **only** how results
are partitioned for reporting and the trial count that follows.

Collectors were not restarted for this amendment and remained live throughout.

### Maturity dates — unchanged

**2026-08-27** for the 7-day analysis; **2026-09-19** for the 30-day. No
analysis before those dates.

---

## Stage A.1 — the MTProto ledger gap closed, the daily pass scheduled, clean restart — 2026-08-17

*ETAs stated before arming (25–35 / 20 / 25–30 / 20–25 / 20–25 min per task);
all held. `make lint`, `make typecheck`, `make test` green (90 tests). No
registered bar, matching rule, channel-list entry, or attention metric was
touched.*

### Task 1 — outcome collection: it was NOT scheduled, and now is

**Finding first: the daily pass had never run.** No crontab entry, no systemd
unit, no `data/state/checkpoints.jsonl`, zero outcome rows on disk. Not yet a
data hole — the first checkpoint (2026-08-16 cohort at d+10) is due
**2026-08-26** — but nine days from becoming one silently.

Fixed under the same supervision discipline as the watcher: a third supervised
component in `scripts/run_collectors.sh` (pidfile, nohup, `data/state/daily.log`)
runs checkpoint + counts + digest once at start and then daily at ~00:40Z, when
the previous UTC day's final candle exists. **First run: 2026-08-17T06:02:18Z**
— `pools_due 0` (correct: nothing matures before 08-26), benchmark leg fetched
(350 daily SOL closes, coinbase), digest written. Backfill state: nothing to
backfill; no checkpoint was ever due before today. `due_days` also gained a
5-day trailing catch-up window so a missed daily run self-heals: the done-set
makes re-scans idempotent and daily candles are retrospective, so a late fetch
returns identical rows — the §8 checkpoint instants are unchanged.

### Task 2 — Telegram flood behaviour, measured passively

**Nothing has been observed, and that is the report — not an inferred limit.**
Zero flood events in every log before instrumentation (collector.log,
watcher.log, lifecycle), and **zero `flood_wait` markers since**. The read path
now records every `FloodWaitError` with its channel and requested wait as a
first-class lifecycle marker, skips the channel for that cycle, and never
probes toward the wall (deliberately tripping flood control risks the account
and buys a number the measurement does not need). Measured cycle timing, first
instrumented cycle: **20 channels read in 31 s** (~1.6 s/channel at the
50-message read limit). Silence at this cadence is consistent with being far
inside the limit; it is not evidence of where the limit is.

### Task 3 — MTProto reads now pass the ledger (ADR-011)

One charge per channel-history request, priced before sending, refusing with
the standard `RequestCapError` semantics (refusal names the arithmetic, writes
nothing, ends the cycle). The fail-open gap named in the Stage A addendum is
closed: the 50,000/day cap binds through the gate, not through the incidental
read limit. First post-restart cycle wrote **20 telegram ledger rows** —
~5,760 charges/day at current cadence against the 50,000 cap.
`tests/test_ledger.py` pins the refusal.

### Task 4 — restart, with the interruption explained in the log

The running processes predated the new SIGTERM handling, so the supervisor
wrote their stop markers itself before the kill (detail: "supervised restart:
Stage A.1"), and the restarted processes write their own from now on (SIGTERM
now runs the finally blocks in `watch` and `collect`).

| source | gap, marker to marker |
|---|---|
| watcher (enumeration) | stop 06:02:16Z → heartbeat 06:02:17Z = **1 s** |
| collect loop (bluesky, farcaster, telegram) | stop 06:02:16Z → start 06:02:17Z = **1 s** (plus each source's position inside the killed ≤300 s cycle, bounded by that cycle) |

All four sources confirmed collecting after the change, rows before → after
restart (deduplicated reads): telegram **880 → 943**, bluesky **6,481 →
6,570**, farcaster **1,420 → 1,451**, enumeration manifests **24,173 →
24,479**. Daily loop running as a third supervised component.

### Standing maturity dates — unchanged

Earliest Stage B analysis: **2026-08-27** (7-day maturity 08-26 + checkpoint
08-27 for the first full cohort). 30-day horizon: **2026-09-19**. No analysis
happens before these dates; the first checkpoint that fetches pool outcomes
fires 2026-08-26 and the schedule that will run it is now supervised, logged,
and self-healing.

---

## Stage A addendum — Amendment 1, the channel list resolved mechanically, Telegram live — 2026-08-17

*Amendment drafted and the resolver built after the operator delegated approval
and chose the MTProto-search route. At amendment time Telegram had collected
**zero rows** (verified by count), so §9's "edited after collection began" had
not fired. `make lint`, `make typecheck`, `make test` green (89 tests).*

### What changed

**REGISTRATION.md Amendment 1 (2026-08-16, appended per the amendment rule):**
the §7 channel-list source becomes **Telegram's own MTProto search** — the
registered eleven-term ingest vocabulary used verbatim as `contacts.search`
queries, results unioned and deduplicated, two mechanical predicates (public
broadcast channel; registered keyword in title+username via the same code path
as the ingest filter), ranked by Telegram's first-party `participants_count`
descending, §7's username tie-break, top 20. No language filter — Telegram
exposes no language field and substituting one would be judgment. The full
rationale (no free machine-readable directory; TGStat's anonymous gate; the
scouting requests that tripped it; first-party provenance) is in the amendment
itself. **No human or model judgment selected any channel.**

The resolved list is in `docs/CHANNELS.md`, **fixed as of
2026-08-17T04:14Z and never edited mid-collection**: 20 channels, top
`@memecoinx` (30,278), floor `@dexscreenerupdatealerts` (385). 27 eligible
candidates from 11 queries; exclusions counted (35 not-a-public-channel, 6
no-username, 12 no-registered-keyword). The list's small absolute sizes are a
recorded property of the instrument — Telegram search favours on-topic matches
over raw audience size — and every result reads against that statement.

### Telegram collection: live

- **First collection cycle with the fixed list: 2026-08-17T04:26Z.** First
  stored row ingested **04:28:23Z**.
- The session file was created by the operator's own interactive login
  (21:12 local, 2026-08-16); it is untracked, gitignored (`*.session`), and
  verified authorized. No credential, code, or session content appears in any
  log, commit, or this entry.
- MTProto traffic does not pass the HTTP ledger (it is not HTTP); the
  registered 50,000/day telegram cap is therefore currently enforced by the
  per-cycle read limit (50 messages × 20 channels per cycle) rather than by
  the gate. Recorded as a known gap to close, not silently reclassified.

### Per-channel resolution and first-window activity

The resolution table with `participants_count` per channel is
`docs/CHANNELS.md`. Rows stored per channel in the first measured window
(04:28–05:17Z, **49 min**): `@birdeye_trendings` 19, `@BirdeyeTrendingCI` 19,
`@MemeCoinIntelligence` 18, `@birdeye_official` 7 — **4 of 20 channels
produced rows; the other 16 resolved but were quiet in the window**, which is
data, not failure. All 20 stay on the list per §7.

### Four sources, one table (window 2026-08-17T04:28–05:17Z, 49 min, cumulative rows since each source started)

| | telegram | bluesky | farcaster | geckoterminal (enum) |
|---|---|---|---|---|
| live since | 04:26Z today | 2026-08-16 16:29Z | 2026-08-16 16:29Z | 2026-08-16 16:29Z |
| stored rows | 63 | 5,929 | 1,042 | 16,714 pool births (2 days) |
| distinct authors | 4 | 2,751 | 365 | — |
| matched mint | 0 | **5** | 0 | — |
| matched cashtag | 6 | 156 | 105 | — |
| matched name | 1 | 1,455 | 120 | — |
| **ambiguous** | **54** | 1,339 | 216 | — |
| unmatched | 2 | 2,974 | 601 | — |
| requests today (ledger) | 0 (non-HTTP; see gap above) | 0 (websocket) | 4,489 / 20,000 | 544 / 10,000 |

**The project's first mint-exact matches exist: 5, on Bluesky.** And the
registered expected failure mode is now measured at scale: **86% of Telegram's
matched-shape mentions are ambiguous** (54 of 63) — ticker collisions
dominating exactly as §3 predicted, attributed to nobody, counted as their own
class.

### The first complete-day rate check — the disagreement did NOT survive the day

**2026-08-16 closed at 1,863 `amm` births (10,318 total), ratio 1.40 against
the registered ~1,330/day — `disagreement = 0` on the authoritative count
basis.** The 5.5× partial-day rate reported yesterday was measured over the
first 20 minutes of collection; the full day landed inside the registered 2×
band. One caveat carried honestly: the day contained only ~7.5 h of collection
(watcher started 16:29Z), so its count understates a true full day.
Today's live rate basis still reads ~7,000/day at 05:17Z and the saturation
marker still fires; **the first day collected from 00:00Z — 2026-08-17 — is
the number that settles the capacity question**, and ADR-010's operator
decision stays open until it closes.

### Standing state

- No analysis before **2026-08-27** (7-day maturity + checkpoint), **2026-09-19**
  (30-day). Unchanged.
- Collectors: watcher + attention loop running; `daily` pass should be cronned.

---

## Stage A — Tasks 1–6: scaffold, measured access, collectors live, clocks started — 2026-08-16

*Registration (Task 0) committed in `0c32387` before any collector existed.
`make lint`, `make typecheck`, `make test` green (87 tests). Collectors running
since 2026-08-16T16:29Z.*

### Registration summary

Committed first, in full, before a single request was sent to any source: the
birth-ordered universe rule with no attention input in enumeration; the expected
~1,330 AMM pools/day with a >2× disagreement rule; the attention metric ex ante
(`v1 / v6 / v24 / ua24 / accel` over 1h/6h/24h from birth, mechanical, no LLM);
the matching rules with ambiguity attributed to nobody; horizons 1/3/7 primary
and 30 secondary anchored at the `d0+2` candle so no return bar overlaps the
attention window; solclear's death floor and 300–600 bps cost band; the
40-trial grid with `(7d, v24, mint-exact)` designated primary; the kill
criteria; the survivorship audit as a first-class output; family separation from
AiTrader's news-drift experiment; and the fixed channel list. **Registered prior
that this finds a tradeable signal: 5 to 8 percent. A documented negative is a
valid and expected outcome.**

### The access table, measured 2026-08-16 (full detail in `docs/ACCESS.md`)

| source | endpoint | reachable | measured rate | measured limit | cost |
|---|---|---|---|---|---|
| GeckoTerminal | `GET /networks/solana/new_pools` | yes | 20 pools/page in 0.84 s | 6.0 s pacing → 14,400 req/day capacity; cap 10,000 | keyless, free |
| GeckoTerminal | `GET /pools/{pool}/ohlcv/day` | yes | full daily history in **one** call | 2 calls per pool per lifetime | keyless, free |
| Coinbase Exchange | `GET /products/SOL-USD/candles` | yes | 350 daily closes in 0.07 s, span 2025-09-01 → 2026-08-16 | keyless | keyless, free |
| Farcaster | `GET snap.farcaster.xyz:3381/v1/events` (shards 1, 2) | yes | 71 casts per 2 shard pages in 5.0 s; **tip age 5–11 s** | no limit observed at ~12 req/s | keyless, free |
| Bluesky | `wss://jetstream2.us-east.bsky.network/subscribe` | yes | 33.9–41.3 events/s, 32.0–38.7 posts/s (~2.8–3.3 M posts/day) | no documented cap; one connection | keyless, free |
| Telegram | MTProto `help.getNearestDc` | yes | 2.65 s connect + one call; **api_id accepted**, nearest DC 1, country CA | credential validity only | free |
| Telegram | MTProto `channels.getHistory` | **NO** | UNMEASURED | UNMEASURED — flood limits are only observable with an authorized session, and no figure is quoted from documentation | free |

**Telegram is blocked on two independent operator actions, and neither blocks
the stage.** (1) MTProto has no non-interactive user login: an authorized
session needs a phone number and code, once, via
`uv run python scripts/telegram_login.py`. (2) The channel list is **not yet
fixed** — seven public directories were probed and none served a
machine-readable member-count ranking (`docs/CHANNELS.md` records each with its
result). Per ADR-007 the collector therefore stays inactive rather than running
against a provisional list that would get "improved" later. The credential pair
itself is verified valid.

**A source that failed verification and was dropped, with the measured reason.**
`hub.pinata.cloud` answers `GET /v1/info` with HTTP 200 and an 823,527,781-message
db-stats payload — and its newest event is **238 days old**. A
reachability-only check would have accepted it and this project would have
recorded **zero Farcaster attention on every cohort while believing the source
worked**, a failure indistinguishable in the data from "nobody mentioned these
tokens". Freshness is now part of verification (ADR-008), and the hub that
passed both bars, `snap.farcaster.xyz:3381`, measured a tip age of 5 seconds.
Also probed and rejected: `snapchain.pinata.cloud` (connect error),
`hub.merv.fun` (timeout), `hoyt.farcaster.xyz:2281` and
`nemes.farcaster.xyz:2281` (connect error), `hub-api.neynar.com` (HTTP 402 —
paid), `api.farcaster.xyz` (HTTP 404).

### First counts — partial day, 2026-08-16T16:26–16:47Z (20 minutes)

**This is a 20-minute window, not a day.** The registered first-day report is
due after the first complete UTC day (2026-08-17) and is the authoritative
figure; everything here carries its span in the same sentence as its number.

| quantity | measured |
|---|---|
| manifest rows appended | 696 |
| unique pools after dedup | 477 (**31% pager overlap** — the feed's pages shift under the pager, so overlap biases the enumeration *complete*, never sparse) |
| `amm` | 98 (20.5% of the cohort) |
| `launchpad` | 379 |
| messages ingested past the registered filter | 87 (farcaster 49, bluesky 38) |
| Bluesky firehose volume | ~1,863 posts per 60 s, of which 5 passed the filter |
| match outcomes | 85 unmatched, **1 ambiguous**, 1 cashtag, 0 mint-exact |
| requests spent | geckoterminal 42/10,000 · farcaster 379/20,000 · benchmark 2/200 · telegram 0 · bluesky 0 |
| disk | 372 KiB in 22 min → **~24 MiB/day, ~712 MiB/30 days** |
| CPU | 0.0% steady state, 35 MB RSS (the watcher sleeps 120 s between sweeps; the work is I/O-bound) |

**The matching layer's expected failure mode appeared within 20 minutes of
going live**: one ambiguous mention, attributed to no token and counted as its
own category, exactly as ADR-005 registered. Zero mint-exact matches so far is
the expected shape at this stage — the active universe is only the pools born
since the watcher started, and mint-address mentions are rare relative to
cashtags.

### A source behaving differently from its verification — the registered rate check fired

**Observed `amm` birth rate 7,300/day against the registered ~1,330/day — a
5.5× disagreement (measured over a 20-minute span, n = 98 `amm` of 477 unique
pools).** The full-feed rate, ~37,000/day, is 4.1× solclear's ~9,000/day and
2.7× its newest−oldest variant. The `amm` share also moved: **20.5% observed
against solclear's 14.8%** (18 of 122, 2026-08-13).

Per the registration this is **reported as a disagreement and not averaged
away**, with candidate causes named and none picked: a genuine venue-mix and
activity shift in the three days since; a methodological difference (solclear's
headline divided by retrieval-time − oldest, which biases down); or a dex id
missing from the launch-venue denylist. **The denylist is not edited to make
the number agree** — REGISTRATION.md §9 lists that as voiding the registration.
The authoritative check is the first complete UTC day, judged on its count.

**This forces an operator decision, recorded in ADR-010 and not taken here.**
At ~7,300 `amm` births/day the outcome checkpoints need **~14,600 requests/day
against a 14,400/day measured capacity and a 10,000/day registered cap**. The
arithmetic REGISTRATION.md §7 performed at ~1,330/day no longer closes. The
registered saturation rule fired and the watcher recorded it as a lifecycle
marker rather than sampling around it. The options — raise the cap and
re-measure whether a faster pace holds; amend to a narrower registered
sub-cohort; or adopt a stated sampling rule — each start a new cohort except
the first, and **none may be taken silently.**

### Timeline — the registered maturity dates

Collection started **2026-08-16T16:29Z**; the first **complete** UTC day is
**2026-08-17**. For a cohort born on day `d`, entry is the `d+2` candle, exits
are `d+2+h`, and the checkpoint fetches land at `d+10` and `d+33`.

| cohort | entry mark | 1 d | 3 d | 7 d | 30 d | checkpoint 1 | checkpoint 2 |
|---|---|---|---|---|---|---|---|
| partial day 2026-08-16 | 2026-08-18 | 2026-08-19 | 2026-08-21 | 2026-08-25 | 2026-09-17 | 2026-08-26 | 2026-09-18 |
| **first full day 2026-08-17** | 2026-08-19 | 2026-08-20 | 2026-08-22 | **2026-08-26** | 2026-09-18 | **2026-08-27** | **2026-09-19** |

**The earliest date a Stage B analysis is worth running is 2026-08-27** — the
date the first full cohort's 7-day outcomes have both matured (2026-08-26) and
been fetched at checkpoint 1. The ≥ 300 matured `amm` pools condition is not
binding at the observed birth rate; the checkpoint date is. The 30-day
secondary horizon is not analysable before **2026-09-19**.

**No analysis happens before these dates.** Not a partial look, not a
"preliminary" quintile split, not a sanity check on returns. Looking at a
partial cohort is the failure the registration exists to prevent, and the
registration is closed.

### ETAs, re-quoted against what actually happened

| task | ETA | actual | note |
|---|---|---|---|
| 0 | 25–35 min | ~35 min | held |
| 1 | 20–30 min | ~30 min | held |
| 2 | 45–70 min | ~65 min | held; the spread was driven by Farcaster hub probing exactly as predicted — six hubs probed, and the freshness bar cost a second round |
| 3 | 40–60 min | ~50 min | held |
| 4 | 25–35 min | ~30 min | held |
| 5 | clock-bound | started 16:29Z | the full first-day report completes 2026-08-18, one full UTC day after collection began; it cannot be compressed |
| 6 | 20–30 min | ~25 min | held |

### Outstanding at the end of Stage A

1. **Operator decision on the capacity shortfall** (ADR-010). Outcome coverage
   will refuse at the registered cap until it is made. Nothing is silently
   sampled or dropped in the meantime.
2. **Telegram login** — one interactive run of `scripts/telegram_login.py`.
3. **Telegram channel list** — name a directory that publishes member counts,
   or supply the twenty channels with their ranking source and date.
4. **Collector durability** — `scripts/run_collectors.sh start` is running in
   this session's process tree. For a machine that reboots, wrap it in a
   systemd unit or a tmux session: **a gap in a forward-recorded cohort cannot
   be backfilled.** `./scripts/run_collectors.sh daily` should be cronned for
   the checkpoint, counts and digest pass.

---

*Entries for Tasks 1–6 are appended below as each completes.*
