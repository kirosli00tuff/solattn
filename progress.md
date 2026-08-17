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
