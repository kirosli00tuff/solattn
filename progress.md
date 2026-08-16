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

*Entries for Tasks 1–6 are appended below as each completes.*
