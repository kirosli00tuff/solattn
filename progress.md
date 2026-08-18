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

## Amendment 5 — the enumeration miss registered, the 429 path made loud — 2026-08-18

*ETAs (30–40 / 35–45 / 10–15 / 20–25 min) held. `make lint`, `make typecheck`,
`make test` green: **135 tests**, up from 114, all three gates in **1.11 s**.
**No cohort outcome was read, fetched or inspected**: `data/outcomes/` still
holds only `benchmark-sol.jsonl`, no `candles-*.jsonl` exists for any pool, and
the first checkpoint fires **2026-08-26**. This lands 8 days ahead of it.*

### Task 1 — the instrument registered as it actually is

**Amendment 5** is appended to `REGISTRATION.md`, with **ADR-016**. §1's claim
that membership "is decided by birth and by nothing else" is now qualified in
the registration itself rather than in a discussion section written after a
result is read.

**The distinction the amendment turns on, stated precisely: the selection rule
is unchanged and remains true.** No mention count, engagement figure, listing,
trending page, archive or "top coins" surface participates in enumeration, and
none ever did. What A.5 measured is that the **realised** cohort is additionally
thinned by an instrument artefact — a paced reader that cannot keep up with the
feed — and that the thinning is **correlated with birth rate**. A reader of §1
would otherwise take the enumerated cohort to be the birth-ordered population.
It is a **non-uniform sample** of it.

Registered, with its figures: the **28–35%** miss bound; both routes (gap
integration 34.7%, the feed's own in-window rate 27.8%) and their **10.6%**
agreement; **401 of 884** sweep pairs with zero overlap; **70.4%** coverage;
the **8.7% / 65.0%** time-of-day spread; the **8.3×** burst-quintile
concentration; and the **75.4% between-sweep / 24.6% within-sweep** split,
which bounds what a cadence change can fix.

**Registered as a lower bound on both routes, with the reason**, so it cannot
later be quoted bare as a point estimate: route B measures the birth rate only
during *covered* time, and covered time is biased toward quiet periods, so it
understates the rate; route A prices each gap from the page windows bracketing
it, and those are by construction slower than the gap, which opened precisely
because the feed outran the reader. **Both routes err in the same direction,
toward under-stating the miss.**

**The direction, registered in the Amendment 2 and 3 pattern.** Pools born
during bursts are systematically less likely to be enumerated. Bursts in pool
creation are periods of elevated market-wide activity — the same latent
condition under which social attention is heaviest — so the cohort
**under-samples exactly the periods where the predictor has its largest values
and its largest variance**. Under-sampling the high end of the predictor
**biases the measured association toward the null**. Therefore **a negative
carries a declared under-detection caveat and must not be read as evidence that
attention does not predict outcomes, and a positive is not inflated by this
weakness.** Same direction as Amendment 2's caveat, opposite to Amendment 3's;
all three stand and none cancels another.

**Not attention-driven selection, and the amendment says so.** No attention
surface touches enumeration. This is selection on a variable *correlated* with
attention — a weaker but real threat, and exactly what §5's survivorship audit
exists to expose. It does not void the registration under §9: source, ordering
rule and denylist are unchanged.

**The reporting requirement, first-class and not a footnote.** Every result, at
every horizon, carries the miss rate with its bound and its lower-bound status,
its non-uniformity, and its n — alongside the survivorship audit §5 already
requires. **A result that omits these is not reportable.**

Seven new pins in `tests/test_registration.py` make deleting any of it break
the build, including that `len(LAUNCHPAD_DEXES) == 16` — **`meteora-dbc` was
NOT added**, since that choice was not made.

### Task 2 — the rate-limit path now refuses instead of ending quietly

**The defect (ADR-017).** `fetch_new_pools` returned `[]` on any non-2xx and
`sweep_once` read a falsy page as end-of-feed, so a 429 truncated the sweep with
**no refusal marker and no error marker**, recording a short read as a complete
one. Same absent-data versus measured-absence shape ADR-012 fixed on the OHLCV
path in A.3, left live on enumeration. The ledger could not have surfaced it
either: it charges *before* sending and never recorded the status, which is why
A.5 had to re-probe the live source to learn the limiter fires at all.

**Stated precisely, because it changes what this fix is: the defect never
fired.** All **887 of 887** collected sweeps recorded `pages_read = 4` and
`pools_seen = 80` — zero truncated sweeps, zero pool-slots lost. The 429s were
provoked by a probe adding a third client alongside the two watchers of Task 3.
**This closes a latent defect; it does not repair lost data, and no collected
figure changes.**

**The fix.** `fetch_new_pools` returns `None` when the source did not answer and
`[]` when it answered with no rows. `sweep_once` branches on the difference:

| page outcome | meaning | what the sweep does |
|---|---|---|
| `None` (429 / 5xx / transport) | **no answer** | writes an **error** marker naming the page, counts `pages_unavailable`, sets `truncated`, stops — explicitly *not* end-of-feed |
| `[]` (2xx, no rows) | **measured absence** | ends the sweep, no marker — a served empty page really is the end |
| rows | data | continues |

`truncated` and `pages_unavailable` ride on every heartbeat, so a retrospective
finds truncated sweeps in the log without re-probing the source. **A truncated
sweep still writes the pages that were served** — refusing loudly must not
discard good data.

**The ledger records the status**, as an append-only **settle row** carrying
`count = 0`. The charge is priced before the request is sent and the ledger is
append-only, so the status cannot go on the charge row and the charge row
cannot be edited; `count = 0` means recording a status can never move a cap.
Pre-ADR-017 rows carry no `kind` and read as charges, which is what they were.
`Ledger.statuses()` reports per-source, per-day status tallies. Cost, stated:
the ledger roughly doubles in rows and `spent()` reads the whole file per
charge, so that read cost roughly doubles — measured well inside the 6.0 s
pacing interval.

**Nine tests**, one per branch: a 429 is not end-of-feed; a served empty page
is; a truncated sweep is visible in the lifecycle log; a truncated sweep still
writes what it read; a settle row never inflates the cap; a settle row is
appended and never edited; and a legacy row with no `kind` still prices against
the cap.

**The fix is live, not merely committed.** A fix sitting in git while the old
code runs is the exact error ADR-014 and ADR-018 record, so the units were
restarted and the new schema verified in production:

```
{"at":"2026-08-18T06:03:03Z","marker":"heartbeat","pages_read":4,
 "pages_unavailable":0,"truncated":0,"pools_seen":80,...}
ledger row kinds: {legacy(no kind): 40351, charge: 19, settle: 18}
settled statuses: {geckoterminal HTTP 200: 4, farcaster HTTP 200: 10, farcaster HTTP 400: 4}
```

### Task 3 — one watcher, one collector, and a guard so it stays that way

**Confirmed after restart at 2026-08-18T06:02:44Z:**

| | pid | unit | state |
|---|---|---|---|
| watcher | **298813** | `solattn-watch.service` | active (MainPID 298803) |
| collector | **298836** | `solattn-collect.service` | active |
| daily pass | — | `solattn-daily.timer` | active, waiting, next 2026-08-19 00:40 UTC |

**No shell-loop process remains**, and this script's three `.pid` files are
gone. Exactly one process per role.

**What A.4 got wrong, recorded plainly (ADR-018).** ADR-014 declared
`scripts/run_collectors.sh` "a manual/dev tool ... no longer the production
mechanism" — **and did not stop it. A declaration is not a mechanism.** Both
ran concurrently from **2026-08-18T04:20:35Z** (two `start` markers four seconds
apart) until stopped. The cost: **a doubled request rate**, and **~3 s effective
spacing** against a source measured to return HTTP 429 at that spacing — which
is what made the ADR-017 defect likely to fire. The cohort survived it:
manifests deduplicate by pool on read, so no birth was double-counted and no
sweep was truncated. It was found only because the lifecycle log carried 12
byte-identical duplicate heartbeats.

**The guard.** The script now refuses to `start` or run `daily` while any of the
three units is active. It names the arithmetic and the measured cost, states
that nothing was started and nothing was written, prints the exact stop command,
and exits 3 — the same refusal discipline the ledger uses. It is overridable by
`SOLATTN_ALLOW_ALONGSIDE_SYSTEMD=1`, deliberately: a guard with no explicit
override gets worked around rather than obeyed. **Verified against the real
live units**, which refused and started nothing.

`status` now reports the systemd units *first*. Reporting only this script's
pidfiles printed "not running" while the collectors were in fact running under
systemd — the misreading that let the collision persist unnoticed.

Five tests pin the guard against a PATH-shimmed `systemctl`; the non-refusing
paths are exercised through `status`, so the test suite can never launch a real
collector.

### Two things the new instrumentation surfaced immediately

Both are **recorded, not fixed** — neither is a registered rule and neither was
in this stage's scope.

1. **The feed head has been frozen since `2026-08-18T04:46:53Z` — 61.7 minutes
   across 29 sweeps**, `new_births = 0`, `pools_seen = 80`, HTTP **200**
   throughout. This is the vendor serving valid but stale pages: a **third**
   absence shape, distinct from both a 429 and a served-empty page, and one the
   new branch handles correctly (no truncation, no false end-of-feed). It is a
   live enumeration gap and is **not** the miss shape Amendment 5 registers —
   that one is a reader too slow for the feed, this one is a feed that stopped.
   73 of 920 sweeps have `new_births == 0` overall.
2. **Farcaster returns HTTP 400 on `tail shard 0`**, repeatedly. Previously
   invisible — the ledger recorded 400s and 200s identically. Farcaster is
   still collecting (95 rows in the 05:00Z hour, 11 by 06:03Z), so these are
   partial failures inside a working collector, not an outage.

### The trial grid is unchanged, and this amendment adds no trial

**160 cells** — horizons {1,3,7,30} × statistics {v24,v1,v6,ua24,accel} ×
match sets {mint-exact, mint+cashtag} × series {bluesky, farcaster, telegram,
pooled} — with **Šidák α_adj = 1 − (1 − 0.05)^(1/160) = 0.000321**, and the
primary trial still `(h = 7d, v24, mint-exact, bluesky)` read at α = 0.05.
Pinned in `tests/test_registration.py` alongside the death floor, cost band,
entry anchor, channel-list size and the 16-member launch-venue denylist, so
none of them can drift.

### Maturity dates — unchanged

**2026-08-27** (7-day analysis), **2026-09-19** (30-day).

---

## Stage A.5 — the enumeration miss rate measured, the real choice sized — 2026-08-18

*ETAs (30–40 / 10–15 / 20–30 / 20–30 min) held; Task 4 was re-quoted down to
15–20 min once the gates were measured at **0.54 s** for all three rather than
guessed. `make lint`, `make typecheck`, `make test` green (**114 tests**). **No
cohort outcome was read, fetched or inspected**: `data/outcomes/` still holds
only `benchmark-sol.jsonl`, and the first checkpoint fires 2026-08-26.*

**Nothing registered changed in this stage.** No rule was edited, no denylist
member added, no cap moved, no ADR appended. This stage measures and reports;
the amendment follows separately, once the operator chooses.

All figures below come from **one frozen snapshot taken 2026-08-18T04:49:43Z**
(55,715 birth rows, 2,459 lifecycle rows, 38,742 ledger rows), because the
manifests are being appended to live and two reads minutes apart do not agree.

### The inputs in the prompt, corrected against the data

Three of the figures this stage was handed are raw line counts rather than
births, and the difference changes the capacity arithmetic.

| quantity | as stated | measured, deduplicated | why |
|---|---|---|---|
| births manifested 2026-08-17 | 36,049 | **27,106** | 8,943 rows are duplicates |
| launchpad | 28,260 | **21,199** | |
| **amm — the rate that binds capacity** | 7,789/day | **5,907/day** | |
| watcher heartbeats | 890 | **887 unique** (898 raw) | |
| sweeps with `new_births == pools_seen` | 405 | **401 of 884** usable pairs = **45.4%** | restart-spanning pairs excluded |

`manifest.read_day` deduplicates by pool on read, so **no analysis path was
ever affected** — `day_counts`, the saturation check and the matching universe
have always seen 27,106, not 36,049. Only a raw `wc -l` sees the larger number.

**Where the duplicate rows come from, measured:** all 14,773 of them separate
by **1–30 s**, never by a sweep interval. They are not repeat sightings across
sweeps. They are the same pool returned on two adjacent pages of **one** walk,
because the feed advances during the 18 s it takes to read 4 pages at the
registered 6.0 s spacing. This is a property of paging a newest-first feed, and
it is the reason a 4-page sweep does not read 80 pools.

### Task 1 — the enumeration miss rate

**The overlap test, run mechanically on the feed's own ordering.** `sweep_once`
keeps a cursor at the newest `pool_created_at` already written and treats as
fresh only what is strictly newer. So `new_births == pools_seen` is a
*proof*, not an inference, that every slot read was created after the previous
sweep's newest — that the two reads did not overlap, and that the interval
between them was never read.

| overlap (pools of 80 re-seen from the previous sweep) | sweeps | share |
|---|---:|---:|
| **0 — no overlap, window advanced past the read** | **401** | **45.4%** |
| 1–4 | 35 | 4.0% |
| 5–9 | 40 | 4.5% |
| 10–19 | 84 | 9.5% |
| 20–39 | 163 | 18.4% |
| 40–59 | 92 | 10.4% |
| 60–79 | 23 | 2.6% |
| 80 — feed did not advance at all | 46 | 5.2% |

n = 884 consecutive sweep pairs; measured sweep interval **median 141 s**
(min 44, p90 144, max 152), against the registered 120 s sleep plus ~21 s of
paced work.

**A live probe refuted the assumption the estimate was about to rest on.** The
natural claim is that paging a newest-first feed can only *duplicate* across
pages, never *skip*, because new rows are inserted at the head and push
everything back. Measured instead (2026-08-18T04:50Z, 4 ledgered requests):
pages 1–2 shared 16 pools, but **page 2 → page 3 left a 13-second hole**. The
feed skips across pages as well as duplicating. Coverage is therefore computed
from **per-page** windows, not per-sweep windows — a per-sweep window would
have spanned that hole silently and understated the miss.

**Coverage, unioning the read windows before summing** (`intervals.merge_windows`,
the standing practice — 3,009 page-reads across 5 continuous watcher runs):

| | |
|---|---|
| feed time elapsed inside the runs | **34.50 h** |
| feed time actually read (union) | **24.28 h** |
| **coverage** | **70.4%** |
| **never read** | **29.6%** (10.21 h, in 1,290 proven-uncovered gaps) |

Gap lengths: p10 2 s, **p50 10 s**, p90 65 s, max 667 s.

**Births never enumerated — bounded by two independent routes.** The rate
inside each gap is estimated from the feed's own measured rate in the page
windows that bracket it, at that moment; never from a daily average.

| route | true full-feed rate | miss rate |
|---|---:|---:|
| **A** — integrate each proven gap at the locally measured rate | 43,497/day | **34.7%** |
| **B** — the feed's own in-window rate, time-weighted (independent of any gap model) | 39,326/day | **27.8%** |
| enumerated, for comparison | 28,385/day | — |

The two routes agree within **10.6%**. **The miss rate is 28–35%**, and it is a
**lower bound on both routes**: route B measures the rate only during covered
time, and covered time is biased toward quiet periods (see below), so it
understates the true rate; route A prices gaps from adjacent windows, which are
by construction slower than the gaps themselves.

**≈ 21,700 births were never enumerated over 34.5 h, of which ≈ 4,000 were
`amm`.** Of the missed births, **75.4% fall in gaps between sweeps and 24.6%
in holes between pages of a single sweep** — so even an infinitely fast sweep
cadence would leave a quarter of the miss in place.

#### The misses are not uniform thinning, and that is the damaging part

**By time of day** — the miss rate spans **8.7% at 07:00 UTC to 65.0% at
16:00 UTC, a 56-point spread and a 7.4× ratio**:

| UTC h | enumerated | est. missed | miss rate |
|---:|---:|---:|---:|
| 07 | 952 | 91 | **8.7%** ← quietest |
| 12 | 1,156 | 699 | 37.7% |
| 15 | 1,153 | 1,319 | 53.4% |
| **16** | 1,445 | 2,684 | **65.0%** ← busiest |
| 21 | 2,126 | 2,236 | 51.3% |
| 00 | 2,255 | 1,069 | 32.2% |

**By burst intensity** — gaps split into quintiles by the feed rate measured at
the gap:

| quintile | gaps | feed rate | est. missed | share of all misses |
|---|---:|---:|---:|---:|
| Q1 slowest | 259 | 29,077/day | 1,182 | 5.4% |
| Q2 | 258 | 37,023/day | 2,087 | 9.6% |
| Q3 | 257 | 44,941/day | 3,841 | 17.7% |
| Q4 | 258 | 51,967/day | 4,794 | 22.1% |
| **Q5 fastest** | 258 | 62,666/day | **9,817** | **45.2%** |

**The fastest quintile carries 8.3× the missed births of the slowest, on the
same number of gaps.** A pool born during a burst is systematically less likely
to be enumerated than one born in a lull.

**This is the exact shape solclear measured the cost of.** The registration's
central claim is that membership is decided by birth and by nothing else, and
that attention never touches enumeration. A 28–35% miss that concentrates
8.3× in high-birth-rate periods is not attention-driven selection, but it is
*correlated with the same latent variable attention is* — market-wide activity
bursts. Uniform 30% thinning would cost power and nothing else. This is not
uniform, and it damages the birth-ordered claim in a way that has to be
reported with every result rather than discovered afterward.

#### The duplicate heartbeat entries

**12 duplicated rows, all at or after 2026-08-18T04:20:58Z** — 898 raw
heartbeats, 887 distinct, each duplicate appearing exactly twice with a zero
interval and byte-identical payload. **It is not a logging bug. Two watcher
processes are running.** The lifecycle log carries two `start` markers four
seconds apart (04:20:35Z and 04:20:39Z), and the process table confirms it:

- `solattn-watch.service` (PID 82464) — the systemd unit ADR-014 installed
- `uv run python -m solattn.cli watch` (PID 82127) — the legacy
  `scripts/run_collectors.sh` shell loop, which A.4 recorded as "no longer the
  production mechanism" but never stopped

Two `collect` loops are running for the same reason. The ledger shows the
doubling directly: paired page=1/page=2 requests at identical seconds.

**Scope of the double-counting, stated precisely: it affects the last 12
sweeps only, not the whole log.** Every per-sweep statistic in this entry was
computed on the 887 *distinct* heartbeats. Manifest counts are unaffected —
`read_day` deduplicates by pool. The real costs are that the watcher now spends
**2× its request budget** and that the effective spacing against the source has
halved to ~3 s.

#### A latent defect the probe exposed, which has not yet fired

At ~3 s effective spacing the source returns **HTTP 429** (measured: 2 of 10
requests, `"You've exceeded the Rate Limit"`). `geckoterminal.fetch_new_pools`
returns `[]` on any non-2xx, and `sweep_once` reads `if not births: break` —
so **a 429 becomes "the feed ended here" and the sweep silently stops early,
with no refusal marker and no error marker.** That is the same absent-data
versus measured-absence shape ADR-012 fixed on the OHLCV path in A.3, still
live on the enumeration path. The ledger cannot detect it either: it charges
before sending and never records the status.

**It has not fired in the collected data.** All **887 of 887** sweeps recorded
`pages_read = 4` and `pools_seen = 80`; zero truncated sweeps, zero pool-slots
lost. The 429s were provoked by the probe adding a third client. The defect is
latent, and the duplicate watcher is what makes it likely to fire.

#### Two further measured facts

- **The feed lags wall clock, and the lag is growing**: median **1.2 min**
  (2026-08-16) → **1.6 min** (08-17) → **6.8 min** (08-18), with the last sweep
  at **10.3 min**. Nothing registered depends on this, but a lag that grows
  toward the 14-day death-floor lookback would.
- **The feed refreshes in batches**: page 1 was byte-identical across **51 s**
  of 6 s polling, then advanced by 10 pools at once. Measured once only
  (**n = 1 change in 103 s**) — thin, and it is the single largest source of
  spread in Task 2.

### Task 2 — what complete enumeration would cost

**Packing efficiency, measured by page depth** on the 410 zero-overlap sweeps
(where all 80 slots were written, so the cursor truncated nothing):

| pages/sweep | slots | distinct pools | efficiency | **pools per request** |
|---:|---:|---:|---:|---:|
| 1 | 20 | 20.0 | 100% | **20.04** |
| 2 | 40 | 34.7 | 86.8% | 17.37 |
| 3 | 60 | 46.0 | 76.7% | 15.35 |
| **4 — as registered** | 80 | **57.4** | **71.8%** | **14.35** |

**The registered 4-page sweep spends 28% of its requests on pools it has
already read in the same sweep.** Depth is bought at a falling rate: each page
past the first adds only ~11.4 new pools, not 20.

**Measured full-feed birth rate** (from each sweep's own window, n = 840):
p50 0.424/s (36,610/day), p95 0.717/s (61,947/day), **p99 0.952/s
(82,286/day)**, max 1.800/s. Busiest UTC hour h16 sustains 0.586/s
(50,654/day); quietest h07 0.272/s.

**The condition for guaranteed overlap.** With `P` pages, cycle `C` seconds,
efficiency `η(P)`, peak rate `R` and safety margin `M`:

```
20·P·η(P)  ≥  M · R · C          and     C ≥ 6.0·P   (the measured pacing floor)
⇒  requests/day = 86400·M·R / (20·η(P))     — independent of P at the boundary
```

At **M = 2.0** and **R = p99 = 0.952 pools/s**:

| pages P | η(P) | sweep interval C | C ≥ 6P? | **requests/day** | vs 14,400 pacing |
|---:|---:|---:|---|---:|---:|
| 1 | 100% | 10.5 s | yes | **8,211** | 57% |
| **2** | 86.8% | **18.2 s** | yes | **9,477** | 66% |
| 4 (as registered) | 71.8% | 30.1 s | yes | 11,466 | 80% |

**Registered budget for complete enumeration: 2 pages per sweep every 18 s →
9,477 requests/day**, at a 2.0× margin over the p99 instantaneous birth rate.
P = 1 at 8,211/day is the theoretical floor but leaves no depth margin against
a single dropped page.

**The batching caveat, stated because it drives the spread.** If the feed
really does publish in ~55 s batches, then the page-set must be deep enough to
hold one whole batch no matter how often it is polled: `M·R·T_refresh` =
2 × 0.952 × 55 ≈ **105 pools**, which needs ~9 pages (extrapolating the
measured +11.4 pools/page), i.e. **14,138 requests/day**. The refresh
measurement is one observation. **Before committing to a cadence, run a longer
refresh probe** — that single number moves the watcher budget from 9,477 to
14,138/day.

**So complete enumeration costs 9,500–14,100 watcher requests/day**, against
2,434/day measured today.

### Task 3 — the alternatives, priced, not chosen

**GeckoTerminal / CoinGecko tiers, retrieved 2026-08-18** from
`coingecko.com/en/api/pricing` and `docs.coingecko.com/reference/endpoint-overview`:

| tier | price | credits | per day / rate limit | pool OHLCV? |
|---|---|---|---|---|
| Public keyless GeckoTerminal | $0 | — | **14,400/day** @ 6.0 s *measured* (docs say 30/min; the marketing page says 10/min) | yes |
| Demo (keyed) | $0 | 10k/mo | 329/day, 100/min | yes |
| Basic | $35/mo ($29 yearly) | 100k/mo | 3,288/day, 300/min | **NO** |
| Analyst | $129/mo ($103.20 yearly) | 500k/mo | 16,438/day, 500/min | yes |
| **Lite** | **$499/mo ($399.20 yearly)** | 2m/mo | **65,753/day**, 500/min | yes |
| Enterprise | custom | custom | custom | yes |

**Basic carries `/onchain/networks/{network}/new_pools` but not the pool OHLCV
endpoint** (Analyst and above), so it cannot serve the outcome path at any
volume — it is not a candidate regardless of price.

**Completing enumeration raises the checkpoint load, because it exposes the
births that were being missed.** At the 28–35% miss rate the true `amm` rate is
**8,181–8,671/day** (central 8,426) against 5,907/day enumerated.

| option | watcher | checkpoints | **total/day** | vs 14,400 pacing | vs 10,000 cap |
|---|---:|---:|---:|---|---|
| **A. pay for a tier** — universe unchanged | 9,477 | 16,853 | **26,330** | over by 11,930 | over by 16,330 |
| A′. …if the feed batches (~55 s) | 14,138 | 16,853 | **30,991** | over by 16,591 | over by 20,991 |
| **B. + `meteora-dbc` → launchpad denylist** | 9,477 | 12,867 | **22,344** | over by 7,944 | over by 12,344 |
| **C. restrict universe** (pumpswap only) | 9,477 | 6,040 | **15,517** | over by 1,117 | over by 5,517 |
| **D. accept incomplete enumeration** (today's watcher) | 2,434 | 11,814 | **14,248** | **fits**, 1% margin | over by 4,248 |
| D′. …as actually running now, two watchers | 4,868 | 11,814 | **16,682** | over by 2,282 | over by 6,682 |
| B′. D + `meteora-dbc` reclassified | 2,434 | 9,020 | **11,454** | **fits** | over by 1,454 |
| C′. D + pumpswap only | 2,434 | 4,234 | **6,668** | **fits** | **fits** |

**Which tiers clear the combined budget:** against option A's **26,330/day**,
only **Lite ($499/mo, $399.20 billed yearly)** clears it, with 60% headroom.
**Analyst at 16,438/day does not** — it is 61% short, and it does not clear
option B (22,344) either. Analyst does clear **C** (15,517) and every
D-variant. The 500/min rate limit is not binding at any of these volumes.

**What each option costs methodologically:**

- **A — pay.** Methodological cost **zero**: no registered rule moves, the
  universe is unchanged, and it is the only option that removes the
  non-random miss rather than documenting it. Cost is $499/mo and real
  engineering: a keyed base URL (`pro-api.coingecko.com/api/v3/onchain/…`), a
  new secret in `.env`, a re-run of `docs/ACCESS.md` verification, and a
  known-answer test that the paid path reproduces the keyless path's answers
  before its output is believed.
- **B — reclassify `meteora-dbc`.** Removes 1,397/day (23.6%) from the primary
  universe. Does not fit anything by itself, and does not address the miss.
- **C — restrict the universe.** Fits, and is the only option that fits the
  registered cap without payment — but it discards 64% of the primary universe
  and starts a new cohort. A *liquidity* rule rather than a venue rule is worse
  on capacity, not better: `PoolBirth` stores no reserve figure, so a liquidity
  floor needs an extra call per pool at birth (+8,400/day) before it can filter
  anything.
- **D — accept documented incomplete enumeration.** Costs nothing and fits
  pacing with a 1% margin, but the documentation it requires is the finding
  above: *28–35% of births are never enumerated, and the miss is 7.4× heavier
  at 16:00 UTC than at 07:00 and 8.3× heavier in the fastest birth-rate
  quintile than in the slowest.* Every result would carry that, at every
  horizon, alongside the survivorship audit §5 already requires. **Note that D
  as currently running (D′) does not fit** — the duplicate watcher must be
  stopped for D to be the option it claims to be.

**None of A, A′, B or C fits the registered 10,000/day ledger cap.** Only C′
does. The cap binds before pacing does in every complete-enumeration option.

#### `meteora-dbc`: correction, or change to the registered rule?

**Stated plainly: adding `meteora-dbc` to Section 1's denylist is a change to
the registered rule, and it applies the registered intent. Both are true, and
the registration already decided which governs.**

- **As written, it is a change.** Section 1 defines `launchpad` as membership
  in an *enumerated set* of 16 dex ids. `meteora-dbc` is not among them. The
  rule is the literal list, and adding a member alters it.
- **As intended, it is a correction.** Section 1 says the set is "a **denylist
  of bonding-curve venues**, not an allowlist of AMMs". `meteora-dbc` is
  Meteora's Dynamic Bonding Curve — a bonding-curve launch venue, squarely the
  class the denylist names. It is absent because it was not observed when the
  registration was written on 2026-08-16, not because it was considered and
  excluded.
- **The registration pre-decided the conflict.** Section 1's check rule: "A
  disagreement does not authorize editing the denylist mid-collection; it
  authorizes an **amendment that starts a new cohort**." So it goes through a
  dated amendment, not a quiet edit — which is the whole point of rule 2.

**And the amendment costs no data, in either direction.** The tag is applied
**at analysis, not at collection**: every `PoolBirth` stores its raw `dex`
string, and `classify_venue` is a pure function over it. Both classifications
remain computable for every pool already enumerated and every pool enumerated
hereafter. The choice decides **which tag is the pre-registered primary**, not
what is kept. A reclassification can therefore also be reported as a
*robustness split* — the result both ways, with its n — exactly as Amendment 3
handled the death-floor alternative, without any cohort being restarted.

For scale, the complete-day `amm` venue mix (2026-08-17, n = 5,907):
pumpswap 2,117 (35.8%), meteora-damm-v2 1,667 (28.2%), **meteora-dbc 1,397
(23.6%)**, orca 325 (5.5%), meteora 106, fluxbeam 105, bags-fm 85, raydium 59,
raydium-clmm 40, then a tail of 6. For contrast the `launchpad` subset is
99.4% pump-fun.

### The registered rules stand unchanged, and the choice is the operator's

No rule was edited in this stage. Section 1's denylist is as registered,
Section 7's caps and pacing are as registered, and the watcher still reports
saturation rather than sampling. No ADR was appended, because no decision was
taken.

**Four things are the operator's to decide**, and only the first is urgent:

1. **Stop the duplicate watcher and collect loops** — `scripts/run_collectors.sh`
   is running alongside the systemd units, doubling the request budget and
   halving the effective spacing against the source. Not a registered rule;
   ADR-014 already made systemd the production mechanism. *Not done here
   because this stage was scoped to measure and report.*
2. **Whether to pay, reclassify, restrict, or document** — the table above.
3. **Whether to fix the 429-swallowing path** in `fetch_new_pools` /
   `sweep_once`, which is a defect and not a rule.
4. **Whether to run a longer feed-refresh probe** before fixing a cadence, since
   that one measurement moves the watcher budget by 4,700 requests/day.

**The deadline is the 2026-08-26 first checkpoint.** It is set by the calendar,
not by effort, and cannot be compressed: it is `T0 + 10 d` for the first
birth-day cohort. Whatever is chosen has to be in place before the outcome path
starts drawing on the same budget, because from that date the checkpoint load
(11,814/day at today's enumerated rate, 16,853/day at the true rate) lands on
top of the watcher's.

### Maturity dates — unchanged

**2026-08-27** (7-day analysis), **2026-09-19** (30-day).

---

## Stage A.4 — persistence, the backfill resolved, the saturation sized — 2026-08-18

*ETAs (25–35 / 35–45 / 10–15 / 20–25 min) held. `make lint`, `make typecheck`,
`make test` green (**114 tests**). No cohort outcome was read, fetched or
inspected: `data/outcomes/` still holds only `benchmark-sol.jsonl`, and the
first checkpoint fires 2026-08-26.*

### Task 1 — the downtime, and the defect A.1 recorded as fixed when it was not

**The collectors stopped and nothing restarted them.** Measured from the
lifecycle log, marker to restart:

| component | last marker | gap |
|---|---|---|
| collect (bluesky, farcaster, telegram) | 2026-08-18T02:43:03Z stop | **1h 37m** |
| watcher (enumeration) | 2026-08-18T02:44:29Z stop | **1h 35m** |
| checkpoints (daily pass) | 2026-08-18T00:40:00Z stop | **3h 40m** (its next run was due 00:40Z) |

A `downtime` lifecycle marker was written per component before restarting, so
the interruption reads as explained downtime with its cause rather than an
unlogged hole.

**Stated plainly, because it is the defect being fixed: Stage A.1 recorded the
daily pass as "scheduled" and described it as a "third supervised component",
and that was wrong.** What existed was a `nohup`'d `while true` loop owned by a
shell whose parent was a session — **no crontab entry, no systemd unit,
nothing that survives a logout, a reboot, or the parent exiting.** The stop
markers were clean, which is precisely why the failure was quiet: every
component shut down politely and simply never came back.

**Persistence installed** as systemd user units, verified:

| unit | state | schedule |
|---|---|---|
| `solattn-watch.service` | enabled, active | `Restart=on-failure`, boot-start |
| `solattn-collect.service` | enabled, active | `Restart=always` — `collect` exits after each bounded cycle, so systemd *is* the loop |
| `solattn-daily.timer` | enabled, active | `OnCalendar=*-*-* 00:40:00 UTC`, `Persistent=true`; next fire **2026-08-19 00:40 UTC** |
| `solattn-daily.service` | static (timer-driven) | checkpoint → counts → report |

`Linger=yes`, so the units survive logout and start at boot. **`Persistent=true`
proved itself on installation**: enabling the timer immediately fired the
missed 00:40Z pass, self-healing a run the shell loop had simply lost.
`scripts/run_collectors.sh` remains a manual/dev tool and is no longer the
production mechanism. Recorded as **ADR-014**.

### Task 2 — the backfill: measured first, then registered

**Which timestamp the windows use, read from the code rather than assumed:**
`attention/metrics.py` computes `posted = parse_iso(mention.posted_at)`, then
`offset = posted - born_at`, then `if offset < timedelta(0): continue`. The
windows use **`posted_at`**, and mentions predating `T0` are already skipped.

**The contamination surface, measured** by applying the registered window rule
to every stored row against its matched mint's manifest birth:

| | rows |
|---|---|
| telegram rows total | 127,286 |
| posted before telegram collection started | **123,225** (oldest **2022-01-06**) |
| pre-collection rows attributed to a cohort pool | **27,577** — mint **945**, cashtag **11,251**, name **15,381** |
| **of those, landing inside a registered `[T0, T0+24h]` window** | **0** |
| live-collected rows landing inside a window, for scale | 7,672 |

**The metric was never contaminated.** Every pre-collection row predates the
`T0` of every pool it matched. The 945 mint-exact pre-collection matches are
not an anomaly and are worth understanding: **a token's mint predates its AMM
pool**, so a genuine mention of the token can precede the pool birth this
registration anchors on.

**Registered anyway, as an explicit rule** (Amendment 4, ADR-015): a mention
whose `posted_at` precedes its **source's registered collection start** is
excluded from the attention metric, because the registered construct is
*forward* attention velocity and a message retrieved from history was not
observed as it happened. The immunity was a property of the window arithmetic,
not a stated rule — and this project's discipline is that **an implementation
accident is not a rule**.

**Rows each source loses from the metric** (excluded at computation; nothing is
deleted from disk): **telegram 123,225** (96.8% of its rows) · **bluesky 0** ·
**farcaster 14**. **No counted figure changes**, because none were counted.

Registered consequence: a pool whose window opens before a source's collection
start now gets **visibly partial** coverage from that source rather than
backfill-filled coverage — direction toward the null for those pools.

**Two pre-existing tests failed when the rule landed, and that was the rule
working**: their fixture birth date predated Bluesky's real collection start.
The fixtures were corrected and the straddling-window edge is now pinned by its
own test.

### Task 3 — the saturation, sized against outcome-path capacity

The watcher's saturation marker fired at **6,114.9 measured AMM births/day**
against the registered 1,330 expectation — **4.60× the expectation** (report
threshold 2.0×) and **2.55×** the registered 2,400/day saturation threshold.
The 40,328 figure is the *30-day active matching universe*, not a daily rate;
the daily rate is what binds capacity.

Arithmetic, at the registered 2 calls per pool (T0+10d covers 1/3/7d, T0+33d
covers 30d) and the measured 6.0 s pacing:

| | registered expectation (1,330/day) | **measured (6,114.9/day)** |
|---|---|---|
| outcome checkpoint requests | 2,660/day | **12,230/day** |
| + watcher sweeps | 2,880/day | 2,880/day |
| **= total** | **5,540/day** | **15,110/day** |
| vs pacing capacity 14,400/day | fits, 61.5% margin | **does not fit — short by 710/day (4.9% over)** |
| vs registered ledger cap 10,000/day | fits | **exceeds by 5,110/day (151% of cap)** |

**It does not fit.** The shortfall is 710 requests/day against raw pacing
capacity, and 5,110/day against the self-imposed cap that binds first.

**The options, reported without choosing one**, because any universe
restriction is a registration change and belongs in an amendment rather than an
implementation: (a) raise the ledger cap toward the 14,400 pacing ceiling — the
smallest change, and still 710/day short at the measured rate; (b) reduce
pacing below 6.0 s — but 6.0 s is a *measured* limit (solclear recorded HTTP
429 at 2.5 s) and lowering it needs new measurement, not assumption; (c)
restrict the universe (a venue subset, a liquidity floor, a sampling rule) —
each starts a new cohort; (d) reduce checkpoints per pool — but both are load
bearing for registered horizons.

**The registered rule is to report rather than sample, and it stands until
amended.** The watcher continues to report saturation and the checkpointer will
refuse at the cap rather than silently sampling or dropping. Nothing was
changed here.

### Maturity dates — unchanged

**2026-08-27** (7-day analysis), **2026-09-19** (30-day).

---

## Amendment 3 — the death-floor specification gap closed — 2026-08-17

*ETAs (25–30 / 10–15 / 10–15 / 30–40 / 20–25 min) held. `make lint`,
`make typecheck`, `make test` green (**110 tests**). Collectors stayed live and
untouched. No bar, grid, list, matching rule, metric or horizon moved.*

### No outcome existed — stated precisely, not loosely

The prompt asked me to confirm `data/outcomes/` was empty. **It was not, and
the precise statement is the one that matters:** the directory held **exactly
one file, `benchmark-sol.jsonl`** — the SOL benchmark leg fetched by the daily
pass, a SOL price series containing no cohort pool and incapable of informing a
death rule — and **zero `candles-*.jsonl`**. `data/state/checkpoints.jsonl` was
**absent**: no checkpoint has ever recorded a pool. **No cohort outcome existed,
and none was read, fetched or inspected during this stage.** Disclosed for
completeness: out-of-cohort KAT candles from A.3 (pools born 2023–2024) sit at
`data/state/kat_raw_candles.json` and were seen during A.3 — they are the
evidence *for* this amendment, not a cohort outcome. First checkpoint fires
**2026-08-26**, nine days out.

### Task 1 — the rule, registered and not silently ratified

Amendment 3 adds condition **(c) `no_exit_candle`**: a missing exit-day candle
books −100%, on the registered ground that a missing daily candle means no
trades that day, no trades at exit means no exit liquidity, and marking a
position that cannot be exited manufactures an unrealizable recovery — the
dust-close rationale applied where the mark is *missing* rather than tiny.
Each condition is now its own **named verdict** so deaths partition by cause.

The amendment records explicitly that **A.3 surfaced the gap**, that **the
code's behaviour predated the registration text**, and that the amendment
**adopts it as a decision** rather than describing what the code happens to do.

**A method note.** The prompt asked me to write the rule into §4. The
registration's own header forbids editing anything above an amendment line, so
I did **not** edit §4 in place — the amendment reproduces the death floor **in
full, as amended**, and states that it governs. That honours both instructions;
had I edited §4 directly I would have broken the append-only property that
makes the registration trustworthy.

### Task 2 — the bias direction, registered before any outcome

**This rule biases toward the hypothesis, and that is now in the
registration.** If higher-attention pools trade more frequently they miss
exit-day candles less often, so (c) fires disproportionately on the
**lower-attention comparison group**, depressing the base rate the top quintile
is measured against.

**This is the opposite direction from Amendment 2's under-detection caveat**,
which biases toward the null. Both now stand in the registration together, act
on different parts of the measurement, and neither cancels the other.

**Registered mitigation, because the direction is unfavourable:** the
**per-attention-stratum firing rate of `no_exit_candle` is a first-class Stage B
output**, reported with its n alongside the returns and never folded into them,
for every quintile and for the registered binary fallback split. **A large
differential is itself a finding about the instrument**, reported as such
whatever it does to the headline.

### Task 3 — the alternative is a robustness report, not a trial

`carry_forward` (mark to the last available close at or before the exit date;
conditions (a) and (b) still apply) is registered as a **robustness report
computed and reported alongside the primary**. The registration states in text
that the primary is fixed, that `carry_forward` **may never become the
headline**, may not be substituted into any table presented as the result, may
not be chosen for producing a nicer number, and **adds no cells to the grid**.

**The grid is unchanged: 160 cells, Šidák α_adj = 0.000321**, exactly as
Amendment 2 left them — pinned by
`test_amendment_3_did_not_move_the_grid_or_any_other_bar`.

### Task 4 — implemented and pinned

`measure()` takes a registered `exit_rule`; an unregistered value **raises**
rather than silently widening the grid. The three death reasons are registry
constants and emitted distinctly. `death_reason_rates()` and
`no_exit_candle_rate_by_stratum()` implement the mitigation, the latter
returning `n` alongside every rate. Eleven new tests pin the registered text,
verdict distinctness, grid invariance, the robustness semantics, and that
`carry_forward` still honours conditions (a) and (b).

**A defect in my own patching, caught by a test and worth recording.** Two
`str.replace` calls silently no-opped because `ruff format` had already
exploded the target call sites onto one argument per line, so the death-reason
constants and the carry-forward branch were never inserted — and the file
still *looked* correct. A behavioural test failed and exposed it. The fix
asserts every replacement before applying it. The general lesson, already in
CLAUDE.md's spirit: **an unasserted string replacement is a silent no-op
waiting to happen**, and only a test that exercises the branch will notice.

### Maturity dates — unchanged

**2026-08-27** (7-day analysis), **2026-09-19** (30-day). No analysis before
those dates.

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
