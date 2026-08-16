# REGISTRATION.md — the pre-registration

> **STATUS: REGISTERED 2026-08-16, BEFORE ANY COLLECTOR EXISTED.**
>
> This document is the first commit of this repository. At the moment it was
> written **no collector had been built, no request had been sent to any
> attention source, no pool had been enumerated, and no outcome existed.** That
> ordering is what makes this a pre-registration rather than a description.
>
> **From this point the specification is closed.** A later session implements
> it and does not revise it. Where the specification and reality disagree, the
> session **reports and stops** rather than choosing: a specification that gets
> quietly adjusted during implementation is not a pre-registration, and the
> adjustment is always in the direction that makes the work easier.
>
> Changing anything here requires a **new dated amendment** appended at the
> bottom, with its reason and a statement of exactly what data existed at the
> time it was made. Nothing above an amendment line is ever edited.
>
> **Disclosure.** solclear's and MLCryptoEngine's repositories, findings, and
> decision logs were read before this was written, and their measured figures
> are cited below as priors. No solattn data of any kind existed.

---

## 0. The hypothesis, and the prior on it

**Hypothesis (H1).** On an independently enumerated, birth-ordered Solana AMM
pool universe, the top quintile of post-birth social attention *velocity* earns
a forward return distinguishably better than the cohort's own base rate, by a
margin larger than a registered execution-cost band.

**Registered prior that H1 finds a tradeable signal: 5 to 8 percent.**

The prior is low for reasons that are already measured, not for pessimism:

- solclear Stage E measured **97.5% 30-day death on a birth-ordered cohort
  (n = 40)** against **18.75% on an attention-crawled cohort (n = 16)** from
  the same chain over the same months — a **60-point gap at 30 days and a
  79-point gap at 90 days** produced by nothing but which pages a crawler chose
  to archive. Attention sampling manufactures survivorship. Any study that
  builds its cohort from attention will find "attention predicts survival"
  because it selected on survival.
- Published post-promotion return paths in this asset class are negative within
  days. The direction H1 proposes to find is the direction the literature
  reports as already priced or worse.
- solclear Stage E's cleared basket realized **−100% at 30 days on 18 of 18
  pools**, and the mechanism was population, not model: a birth-ordered feed is
  dominated by pre-graduation curves that die regardless of any launch-window
  score.

**The product of this project is the bias-controlled measurement either way.**
A documented negative is a valid and expected outcome, is the modal outcome
under the registered prior, and closes the hypothesis rather than motivating a
retune.

---

## 1. The universe rule

**Every new Solana AMM pool observed at birth from a keyless public new-pools
feed, birth-ordered, with no attention input of any kind in the enumeration.**

- **Source:** GeckoTerminal's keyless public new-pools feed for the `solana`
  network, `GET https://api.geckoterminal.com/api/v2/networks/solana/new_pools`
  (paged). No API key, no account, no attention-derived ranking. The feed is
  ordered by pool creation, newest first.
- **Ordering:** strictly by the feed's `pool_created_at`. Membership is decided
  by birth and by nothing else. **No mention count, engagement figure, listing,
  trending page, archive, or "top coins" surface participates in enumeration.**
  This is the single most important property of the study and the one solclear
  measured the cost of violating.
- **Venue classification, fixed now.** Every enumerated pool is tagged
  `venue_class ∈ {launchpad, amm}` by its `dex` id:
  - `launchpad` iff the dex id is in the registered launch-venue set
    `{pumpfun, pump-fun, pumpdotfun, launchlab, moonshot, moonit, boop-fun,
    believe, bonkfun, letsbonk-fun, heaven-dex, raydium-launchlab, virtuals,
    daos-fun, sunpump, four-meme}`.
  - `amm` otherwise.
  The rule is a **denylist of bonding-curve venues, not an allowlist of AMMs**,
  deliberately: a new AMM that appears mid-collection is included
  automatically, whereas an allowlist would silently drop it and bias the
  cohort toward venues that existed on registration day.
- **Nothing is discarded at collection time.** Both classes are written to the
  daily manifest with their tag. The registration fixes which tag is the
  primary universe; filtering happens at analysis, from a tag whose rule was
  written before any data existed.
- **The primary universe is the `amm` subset.** The `launchpad` subset is
  enumerated, manifested, and reported, but is not outcome-fetched in Stage A
  (see §7 — request capacity binds, and the arithmetic is stated there rather
  than discovered later).

### Expected daily count, registered so the observed rate can be checked

From solclear's Stage B addendum, measured 2026-08-13 on 122 unique pools:

| cohort | measured rate | basis |
|---|---|---|
| full new-pools feed | **~9,000 pools/day** | 122 pools over a 12.5 min span; the newest−oldest variant gives ~14,000 |
| `amm` subset (the primary universe) | **~1,330 pools/day** | 18 of 122 (pumpswap 9, meteora-damm-v2 6, meteora 1, raydium 1, fluxbeam 1) |
| pumpswap only (graduation proxy) | ~665/day | 9 of 122; Poisson 95% CI ≈ [300, 1,260] |
| `launchpad` subset | ~7,450/day | 101 of 122 were pump.fun bonding curves |

**Check rule, fixed now.** The observed `amm` birth rate is compared against
~1,330/day. **A disagreement of more than 2× in either direction is reported as
a disagreement and never averaged away**, and its likely cause (venue mix
shift, feed pagination behaviour, a dex id not in the registered denylist) is
named. A disagreement does not authorize editing the denylist mid-collection;
it authorizes an amendment that starts a new cohort.

---

## 2. The attention metric, registered ex ante

**Stage A is mechanical. No LLM judgment participates in any attention figure
in this stage** — no sentiment, no relevance scoring, no summarization, no
model-derived weighting. The metric is counting.

### Per token, per source, the counted quantities

- `mentions(w)` — number of ingested messages in trailing window `w` whose
  registered match rules (§3) attribute them to the token.
- `authors(w)` — number of **distinct** author identifiers among those
  messages.

### The registered windows

Attention is accumulated over a **fixed post-birth window** so that every pool
is measured over the same span of its own life, and so that the measurement
closes strictly before the return measurement opens.

- **Attention window: `[T0, T0 + 24h]`**, where `T0` is the pool's
  `pool_created_at` from the enumeration feed.
- **Trailing sub-windows, registered: `w ∈ {1h, 6h, 24h}`**, each measured from
  `T0`. `w = 1h` means `[T0, T0+1h]`.

### The registered statistics

| id | definition | unit |
|---|---|---|
| `v1` | `mentions(1h) / 1` | mentions per hour |
| `v6` | `mentions(6h) / 6` | mentions per hour |
| `v24` | `mentions(24h) / 24` | mentions per hour |
| `ua24` | `authors(24h) / 24` | distinct authors per hour |
| `accel` | `v1 / max(v24, 1/24)` | dimensionless |

The `1/24` floor in `accel` is registered explicitly: it is one mention per
day, the smallest non-zero `v24` the metric can produce, so `accel` is finite
for every pool with at least one mention and is defined as `0.0` for a pool
with none.

**Cross-source aggregation:** the primary statistics sum `mentions` and take
the union of author identifiers **across sources** (author identifiers are
namespaced by source, so a person active on two sources counts twice — this is
registered as a known and accepted property, not corrected for). Per-source
figures are also emitted, always.

### The registered quintile construction

1. Pools are grouped into **birth-day cohorts** by the UTC calendar date of
   `T0`. Quintiles are formed **within a birth day**, never pooled across days,
   because attention volume has a strong day-of-week and regime component and
   pooling would compare a quiet Tuesday's top quintile against a loud
   Saturday's median.
2. Within a birth day, pools are ranked by the statistic under test,
   descending. **Ties are broken by `authors(24h)` descending, then by mint
   address ascending (base58 lexicographic).** Both tie-breaks are fixed now
   and neither is outcome-dependent.
3. The ranked list is split into **five equal-count buckets**, `Q1` (lowest
   attention) … `Q5` (highest). When the cohort size is not divisible by 5, the
   **remainder is assigned to the lowest buckets**, so `Q5` is never inflated
   by rounding.
4. **The degenerate-cohort rule, registered now because it is expected to
   fire.** Most births will have zero mentions. If **more than 80% of a birth
   day's cohort has `v24 == 0`**, the quintile split is meaningless (three or
   four buckets are all-zero and the ordering inside them is the tie-break, not
   attention). Such a day is flagged **`degenerate_quintiles`** and enters the
   registered fallback: a **binary split of any-mention (≥ 1 mention in the
   window) versus zero-mention**, analysed and reported alongside — never
   instead of — the quintile result. Both are reported for every day regardless
   of which fired, so the choice cannot be made after seeing outcomes.

---

## 3. The matching rules, with the collision policy stated in advance

A message is attributed to at most one token. **Ticker collisions are the
expected failure mode of this study**, not an edge case, and the registration
says so: memecoin symbols are reused constantly, several hundred new tokens
share a popular ticker within any given week, and any scheme that resolves a
collision by picking the "most likely" token is manufacturing attention data.

### The rules, in priority order

1. **Primary — mint address exact match.** A base58 string of length 32–44 in
   the message that is byte-equal to a mint in the active universe. Exact,
   deterministic, collision-free. This is the only match kind used in the
   **primary** analysis.
2. **Secondary — cashtag exact match.** A `$TICKER` token (2–10 characters,
   `A–Z0–9`, case-insensitive) equal to the pool's base-token symbol.
3. **Secondary — name exact match.** The token's full name matched
   case-insensitively at word boundaries. A name shorter than 4 characters is
   **not** name-matchable (registered: it produces noise, not signal).

**Active universe** for matching = pools whose `T0` falls in the trailing
**30 days** at the time the message was posted. Fixed now; a wider window
raises collisions, a narrower one drops late mentions.

### The collision policy, fixed before any message was read

- If a cashtag or name matches **exactly one** active mint → `matched_cashtag`
  or `matched_name`.
- If a cashtag or name matches **more than one** active mint → the mention is
  recorded as **`ambiguous`** and is **attributed to none of them.** It is
  never split fractionally, never assigned to the most recent, most liquid,
  most mentioned, or most anything. Ambiguity is a **first-class category with
  its own daily count**, reported alongside matched and unmatched every day.
- If a message contains **both** a mint address and a cashtag or name pointing
  at a different token, the **mint address wins** and the record carries a
  `conflict=true` flag. The conflict count is reported.
- A message that passed the ingest filter and matched nothing is
  **`unmatched`**, counted, and kept.

### The registered analysis consequence

**The primary analysis uses `matched_mint` only.** Cashtag and name matches
form a registered **secondary** match set (`mint+cashtag`) reported separately.
This is the conservative choice and it is fixed now, before anyone knows
whether the mint-only sample is large enough to be interesting.

---

## 4. Horizons, bars, and the return construction

### Anchors, chosen so the measurement cannot leak

- `T0` = pool `pool_created_at` (UTC).
- `d0` = the UTC calendar date of `T0`.
- Attention window closes at `T0 + 24h`, which is at the latest the end of
  `d0 + 1`.
- **Entry mark = the close of the daily candle for UTC date `d0 + 2`.** That
  candle opens at `00:00Z` on `d0 + 2`, which is strictly after the attention
  window closed, for every possible time-of-day of `T0`. **No candle used in
  any return overlaps the attention window.**
- **Exit mark at horizon `h` = the close of the daily candle for UTC date
  `d0 + 2 + h`.**

Registered consequence, stated so it is not later mistaken for a defect: the
entry mark sits **24 to 48 hours after birth** depending on the time of day the
pool was born. That spread is a fixed property of a deterministic rule, not a
choice made per pool.

### Horizons

- **Primary: `h ∈ {1, 3, 7}` days** — these mature inside the operator's
  working window.
- **Secondary: `h = 30` days** — matures later, reported when it matures.

### The death floor (ported from solclear ADR-013, Stage E)

At horizon `h`, a position **books exactly −100%** if either:

- **(a)** there is **no candle with non-zero volume in the 14 days ending at
  the exit date**, or
- **(b)** the exit close is **below 1% of the entry close**.

Rationale, carried over unchanged: a dust close has no exit liquidity, and
marking to it manufactures an unrealizable recovery. **Dead pools stay in their
quintile.** They are never dropped, and a quintile's return is computed over
its full membership including its deaths.

**Graduation stitching (ADR-013 v2), registered now.** A `launchpad` position
that graduates moves liquidity to a new pool address and would read as death
under rule (a). Any analysis that includes `launchpad` pools must stitch the
price series across graduation (curve candles, then AMM-pool candles) **before**
applying the death floor. The Stage A primary universe is `amm`-only, so the
rule does not bind on the primary result; it is registered because a later
cohort may include launch venues.

### The execution-cost band (ported from solclear ADR-014)

- **Registered central figure: 450 bps round trip, charged 225 bps per leg.**
- **Sensitivity bounds: 300 bps and 600 bps round trip.**
- Gross and net are **always reported side by side**.
- A death position nets exactly **−100%** — cost cannot deepen a total loss
  beyond the stake.
- The SOL benchmark leg carries **no** memecoin execution cost.

This is a cost band applied to a hypothetical, for the purpose of asking
whether a measured lift would survive costs. **It is not a trading plan, and
nothing in this repository executes anything.**

### The primary comparison

**Top-attention-quintile (`Q5`) forward return versus the birth-ordered
cohort's own base rate**, over the same birth days, at each horizon, **net of
the registered cost band**.

Base rate = the equal-weighted mean net return of the **entire** birth-ordered
`amm` cohort for those birth days, deaths included. The comparison statistic is
`lift = mean_net(Q5) − mean_net(cohort)`. The **median** of each is reported in
the same table, always, because solclear Stage E measured how badly a fat-tailed
mean misleads here: a +84.1% mean sat over a −100% median (n = 35).

### Inference

- **Day-clustered bootstrap.** Resample **birth days** with replacement (not
  pools), 10,000 draws, recomputing `lift` on each resample. Report the point
  estimate, the 95% percentile interval, and `p_raw`. Days are the cluster unit
  because pools born the same day share venue-mix, regime, and attention-volume
  shocks, and pool-level resampling would understate the interval.
- **The trial grid is counted now and deflated.**
  **horizons {1, 3, 7, 30} × statistics {v24, v1, v6, ua24, accel} ×
  match sets {mint-exact, mint+cashtag} = 4 × 5 × 2 = 40 trials.**
  - **The primary trial is designated now: `(h = 7d, statistic = v24, match set
    = mint-exact)`.** It is one trial and is reported at α = 0.05.
  - All 40 are reported. The other 39 are secondary and are judged against the
    Šidák-adjusted level **α_adj = 1 − (1 − 0.05)^(1/40) = 0.00128**.
  - **The grid may not grow.** A statistic, horizon, or match set not listed
    above cannot be added to this cohort's analysis; it requires an amendment
    and a new cohort.

### The kill criteria

**The hypothesis is closed — a documented negative — if either fires:**

- **(K1) No distinguishable lift.** The primary trial's 95% day-clustered
  bootstrap interval for `lift` **includes zero**.
- **(K2) Lift entirely inside the cost band.** The point estimate of `lift`
  satisfies **|lift| ≤ 600 bps** (the upper sensitivity bound), i.e. any
  apparent edge is no larger than the cost of acting on it.

Either firing closes the hypothesis. **Neither is reopened by retuning a
threshold, adding a statistic, changing the quintile count, or swapping the
attention source** — solclear ADR-015's reopening rule is inherited verbatim in
spirit: the question reopens on a **genuinely different population**, not on a
different metric.

### The underpowered rule (ported from solclear Stage E)

If the `Q5` cell contains **fewer than 20 matured pools** at a horizon, **no
significance is claimed in either direction** at that horizon. The direction is
reported; the inference is withheld and labelled `underpowered`.

### The minimum cohort before any analysis runs

**No Stage B analysis runs before ≥ 300 matured `amm` pools exist at the
primary (7-day) horizon**, and no analysis of any horizon runs before that
horizon's first cohort has matured (§8). Looking at a partial cohort is the
failure this whole document exists to prevent.

---

## 5. The survivorship audit — a first-class output, not a caveat

**The death-rate gap between birth-ordered and attention-selected subsets is
reported alongside every result**, at every horizon, with its n. This project
exists in part to measure that gap forward, prospectively, on a cohort whose
enumeration is known to be unbiased — where solclear could only measure it
retrospectively against an archive.

Reported every time, at every horizon:

| subset | definition |
|---|---|
| birth-ordered cohort | every `amm` pool enumerated at birth |
| any-mention subset | pools with ≥ 1 mint-exact mention in `[T0, T0+24h]` |
| `Q5` subset | the top attention quintile |

with, for each: `n`, death rate under the §4 death floor, median net return,
and the **gap in percentage points** against the birth-ordered cohort.

**Registered priors for this gap** (solclear Stage E, 2026-08-14): 97.5%
30-day death birth-ordered (n = 40) versus 18.75% attention-crawled (n = 16).

**Registered rule, ported from Stage E:** a gap of **more than 15 percentage
points** between the birth-ordered cohort and any attention-selected subset
means **the headline rests on the birth-ordered subset alone**, and every
attention-subset figure is reported carrying that statement.

---

## 6. Hypothesis-family separation from the AiTrader news-drift experiment

This is registered as a **separate hypothesis family** from the news-drift
experiment running in the operator's AiTrader project (`AiTrader/EXPERIMENT.md`,
accepted 2026-07-28, binding and closed).

| | AiTrader news-drift | solattn (this project) |
|---|---|---|
| family | **information incorporation** — does a priced asset drift after news is published | **attention and flow reflexivity** — does crowd attention move a forward outcome |
| universe | US equities, liquidity-stratified | Solana AMM pools enumerated at birth |
| bars | that project's own, registered in its own document | §4 of this document |
| trial grid | its own, counted there | 40, counted here |

**Neither project's outcome is evidence in the other's family.** A positive
news-drift result does not raise this project's prior, and a negative result
here does not lower that project's. They share an operator, a standard of
evidence, and nothing else. Neither may cite the other's number as support, and
no combined or pooled inference across the two is permitted.

---

## 7. Channel-selection bias, named plainly, and the fixed channel list

**Which Telegram channels are watched shapes which attention is visible.** A
channel list assembled by browsing, by relevance, or by "the ones that seem
active" is an attention-selected instrument measuring attention — the same
circularity solclear measured at 60 points, moved one level up. There is no way
to remove this bias; there is only fixing the instrument before it is pointed at
anything and never adjusting it while it collects.

**The registered rule for the channel list:**

- **The top 20 public Solana / memecoin Telegram channels by member count**,
- **from a single stated public directory**, named with its URL,
- **read on a single stated date**, recorded with the retrieval timestamp,
- ranked by the directory's own member-count field, ties broken by channel
  username ascending,
- excluding only channels the directory itself marks as non-public or
  non-English, with each exclusion recorded by name and reason.

**The list is fixed at registration and never edited mid-collection.** Adding a
channel because it looks interesting, dropping one because it is noisy, or
replacing one that goes quiet all change what attention is visible, and each
would require an amendment that **starts a new cohort** rather than continuing
this one. A channel that dies mid-collection stays on the list with zero
messages recorded — that is data, not a gap to patch.

**The resolved list, its directory, and its retrieval date are recorded in
`docs/CHANNELS.md`**, which is written once and thereafter append-only.

### Request capacity, registered with its arithmetic

Both the universe watcher and the outcome checkpointer draw on one keyless
GeckoTerminal budget, through one paced queue.

- **Pacing: minimum 6.0 s between requests.** Measured, not documented:
  solclear's addendum recorded a 429 at 2.5 s spacing against a documented
  30/min limit, and 6 s held. → capacity **14,400 requests/day**.
- **Universe watcher:** a sweep every **120 s**, **4 pages** per sweep →
  **2,880 requests/day**. At ~9,000 births/day the feed produces ~12.5 new
  pools per 2 min against 80 pool-slots fetched — **6.4× headroom** against
  missing a birth.
- **Outcome checkpointer:** the daily-OHLCV endpoint returns a long history in
  one call, so each pool needs **2 calls total**: one at `T0 + 10 d` (covering
  the entry mark and the 1/3/7-day exits and their 14-day death lookbacks) and
  one at `T0 + 33 d` (covering the 30-day exit). At ~1,330 `amm` births/day →
  **~2,660 requests/day**.
- **Total ~5,540 of 14,400 = 38% utilization.** Registered daily ledger cap for
  this source: **10,000 requests/day**.
- **This is why `launchpad` pools are enumerated but not outcome-fetched in
  Stage A.** Adding them would require ~14,900 outcome calls/day against a
  14,400/day capacity — it does not fit, and the arithmetic is stated here
  rather than discovered as a silent shortfall later.
- **Saturation rule:** if the measured `amm` birth rate exceeds **2,400/day**
  (pushing outcome calls past ~60% of capacity), the watcher **reports the
  saturation** and the operator decides. It does not silently sample, and it
  does not silently drop.

### The registered ingest filter

Firehose sources are filtered **at ingest** so volume stays sane. The filter is
registered here, with the registration, because a filter is part of the
instrument.

A message is ingested iff it contains at least one of:

1. **a base58 string of length 32–44** (the Solana mint-address shape), or
2. **a `$CASHTAG`** of 2–10 characters `A–Z0–9`, or
3. a case-insensitive word-boundary match against the **fixed keyword set**
   `{solana, pumpfun, pump.fun, memecoin, raydium, meteora, jupiter,
   dexscreener, birdeye, "contract address", spl-token}`.

**Rules 1 and 2 are shape filters, not content filters** — they cannot
privilege particular tokens, because they match a *form* rather than a name.
That is deliberate and load-bearing: it is what keeps the ingest filter from
being an attention-selection instrument in its own right. The keyword set in
rule 3 is small, fixed, and never extended mid-collection. Short, ambiguous
strings (`sol`, `ca`) are deliberately **excluded** — they collide with ordinary
English and Spanish text and would flood the store with noise while adding no
token-level resolution.

---

## 8. Timeline and maturity dates

**No analysis happens before the registered maturity dates.** They are
calendar facts and cannot be compressed.

Let `D` = the first full UTC day of collection. For a pool born on day `d`:

- entry mark is the daily candle for `d + 2`,
- the 1-day exit is `d + 3`, the 3-day exit is `d + 5`, the 7-day exit is
  `d + 9`, the 30-day exit is `d + 32`,
- the checkpoint fetches occur at `d + 10` and `d + 33` (one day of slack for
  the venue to publish the final candle).

The concrete dates for this cohort are recorded in `progress.md` when `D` is
known, and the earliest date a Stage B analysis is worth running is the later
of the 7-day maturity date and the date the ≥ 300 matured `amm` pools condition
in §4 is met.

---

## 9. What would make this registration void

Stated now so it cannot be argued about later. This registration does not cover,
and its results may not be reported under it, if any of the following happened:

- the channel list was edited after collection began (§7),
- the venue denylist was edited after collection began (§1),
- the ingest filter was edited after collection began (§7),
- the trial grid grew beyond 40 (§4),
- any quantity was computed from a candle overlapping the attention window (§4),
- an ambiguous match was attributed to a token (§3),
- an LLM produced any attention figure in this stage (§2),
- a cohort was assembled from any surface that ranks by attention (§1).

Any of these requires an amendment and a **new cohort**, not a footnote.

---

## Amendments

*None. The registration is as written on 2026-08-16.*
