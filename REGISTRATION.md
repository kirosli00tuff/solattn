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

### Amendment 1 — 2026-08-16 — the channel-list source becomes Telegram's own MTProto search

**What data existed when this amendment was made.** **Telegram had collected
zero rows.** `data/attention/mentions-*.jsonl` contained 0 records with
`source == "telegram"` at the moment this was written, verified by count. No
Telegram message had ever been ingested, matched, or counted. §9's voiding
condition — *"the channel list was edited after collection began"* — **has not
fired**, because collection on this source had not begun. The Bluesky,
Farcaster and enumeration legs were already running and are **untouched by this
amendment**: their cohort, their bars, and their maturity dates are unchanged.

**Why the original rule could not be executed.** §7 required the top 20 public
Solana/memecoin channels by member count **from a single stated public
directory**. Nineteen candidate directories were probed on 2026-08-16 and **none
publishes a Solana/memecoin ranking by member count that is readable without an
account**:

- The only freely machine-readable, member-count-ranked source found was
  `tgstat.com/en/ratings/channels/crypto` (server-rendered, keyless, 100 rows,
  verified strictly descending by subscribers). Its **narrowest category slug is
  `/crypto`** — `/solana`, `/memecoin`, `/memecoins`, `/bitcoin`, `/nft`,
  `/blockchain` and `/cryptocurrencies` all return HTTP 404 — and its top 20
  contained **zero Solana or memecoin channels** (it is TON tap-games, TON
  wallets, and exchange announcement feeds). It could not satisfy the rule.
- TGStat's Solana-specific search renders results client-side, and during the
  scout TGStat began returning **HTTP 429 "Authentication Required — Please log
  in"** to anonymous clients IP-wide, including the ratings pages that had
  worked earlier the same day. The scouting requests caused that gate. It is
  recorded here as a fact about the source's availability, not routed around.
- Every other directory probed (Telemetr, telegramchannels.me,
  telegram-store.com, telega.io, lyzem, Combot, tlgrm.eu, tgdr.io,
  tgchannels.org, telegramic.org) either published no member counts, rendered
  its catalogue client-side, or returned 404/DNS failure.

**Why Telegram's own search is the better instrument, not merely the available
one.** `participants_count` obtained from `channels.getFullChannel` is
**first-party**: it is the platform's own count, read directly from the source
of truth, rather than a third party's cached copy of it. A directory's figure
can be stale, sampled, or editorially curated; Telegram's cannot. The
substitution therefore improves provenance rather than degrading it, and it
removes the third-party availability risk that just materialised.

**The amended rule.** The channel list is resolved **mechanically, by
Telegram's own MTProto search**, with no human or model judgment selecting
channels. Every step below is fixed by this amendment and is reproducible from
the recorded query set and date:

1. **Query set — the registered §7 ingest keyword vocabulary, used verbatim.**
   All eleven terms, no additions, no removals, no reordering:
   `solana`, `pumpfun`, `pump.fun`, `memecoin`, `raydium`, `meteora`,
   `jupiter`, `dexscreener`, `birdeye`, `contract address`, `spl-token`.
   Deriving the queries from the vocabulary already registered in §7 is what
   makes the query set principled rather than ad hoc; a term is not dropped
   because it looks unproductive, because dropping it would be a judgment.
2. **Retrieval.** `contacts.search(q=<term>, limit=50)` for each term, in the
   order listed. Results are unioned and deduplicated by channel id.
3. **Eligibility predicate, mechanical.** A result is eligible iff it is a
   `Channel` with `broadcast = True`, `megagroup = False` (a channel, not a
   group, per §7's wording), and a **public `username`** (a channel without one
   is not public and is excluded, with the exclusion counted).
4. **Relevance predicate, mechanical.** The concatenation of the channel's
   `title` and `username`, lowercased, must contain at least one registered
   keyword from the query set, matched **case-insensitively at word
   boundaries** — the identical matching rule §7's ingest filter rule 3 already
   uses, applied through the same code path (`attention.filters.find_keywords`),
   so the two cannot drift. `title` and `username` are used because both are
   present on the search result itself; `about` is not used, because reading it
   would require a per-candidate `getFullChannel` on every search hit and the
   predicate must be decidable before that cost is paid.
5. **Ranking field.** Telegram's own **`participants_count`**, read per
   eligible channel via `channels.getFullChannel`, descending.
6. **Tie-break.** Ties in `participants_count` are broken by **channel username
   ascending**, which is the tie-break §7 already registered. No second-order
   tie-break is needed, since usernames are unique.
7. **Cutoff.** The **top 20**. Unchanged from §7.
8. **No language filter is applied.** §7 permitted excluding channels *"the
   directory itself marks as non-public or non-English"*. Telegram exposes no
   language field, so the non-English clause is **inapplicable and is not
   substituted for** — filtering by apparent language would be exactly the
   judgment this amendment exists to avoid. Only the non-public clause survives,
   implemented as the missing-username exclusion in step 3.
9. **Recorded once, then frozen.** The resolved list, the query set, the
   per-channel `participants_count`, and the UTC date and time of the read are
   written to `docs/CHANNELS.md`. **From that moment the list is fixed and is
   never edited mid-collection**, exactly as §7 requires. A channel that goes
   quiet, gets renamed, or is deleted stays on the list with that status
   recorded — that is data. Re-running the resolver later would produce a
   different list and is **not** permitted for this cohort.

**What is unchanged.** Everything else in this registration. The universe rule,
the attention metric, the matching rules, the horizons, the death floor, the
cost band, the 40-trial grid, the primary trial, the kill criteria, the
survivorship audit, and the family separation are all untouched. This amendment
changes **only** how the twenty channels in §7 are selected, and it does so
before a single Telegram message has been recorded.

**The residual bias, stated plainly and not solved.** Substituting Telegram's
search for a directory does not remove channel-selection bias — it relocates
it. The instrument is now "what Telegram's search ranks highly for these eleven
terms", which is a different bias from "what a directory chose to list", not an
absence of one. What the amendment buys is that the bias is **fixed in advance,
mechanically reproducible from a recorded query set and date, and immune to
being adjusted once results are visible.** That was always the property §7 was
protecting, and it is preserved.

### Amendment 2 — 2026-08-17 — the attention metric is computed and reported PER SOURCE

**What data existed when this amendment was made.** Attention rows existed for
all three sources (telegram 65, bluesky 6,725, farcaster 1,174 persisted at the
time of writing) and are characterised below. **No outcome existed and none was
looked at.** The first cohort matures 2026-08-26 and the first outcome
checkpoint fires the same day; `data/outcomes/` was empty and
`data/state/checkpoints.jsonl` recorded `pools_due 0` at its only run. This
amendment therefore fixes an open **analysis** choice strictly before any
forward return could inform it, which is the ordering §4 exists to protect.

**Nothing collected changes.** The channel list stays fixed under §7's
never-edit rule — Telegram has collected since 2026-08-17T04:28Z, so the list
is frozen regardless of what the characterisation below shows. The matching
rules, the attention metric definitions, the windows, the horizons, the death
floor, the cost band and the kill criteria are all untouched. **This amendment
changes only how the metric is partitioned for reporting, and the trial count
that follows from it.**

**The characterisation, mechanical, proxies stated before computing.** No
channel was classified by hand or by judgment. P1 = rows ÷ distinct authors;
P2 = share of a source's rows from its single most active author id; P3 = share
of sampled messages with ≥ 3 distinct cashtags **or** with
(cashtag + mint-address characters) ÷ total characters > 0.30, computed with the
registered filter's own regexes on a fresh bounded sample (raw text is
deliberately not persisted); P4 = persisted `match_kind` distribution.

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

**P3 is reported only for Telegram.** The Bluesky and Farcaster samples (n = 18
and n = 7 messages passing the ingest filter in the sampling window) are too
small to distinguish any share, and their figures above are recorded for
completeness, **not** as measurements. A share with n = 7 is not a result.

**What the numbers say, descriptively.** Two contrasts do not depend on the
weak proxy. **Telegram emits 16.25 rows per author from 4 distinct authors,
against Bluesky's 2.19 from 3,077** — a source whose metric aggregates a
handful of emitters versus one aggregating thousands. And **Telegram's
unmatched share is 0.031 against Bluesky's 0.487**: almost everything Telegram
emits matches the token vocabulary, which is the signature of a feed that emits
token names by construction rather than of people who sometimes mention them.
This is a factual description of what each source emits. It is **not** a
quality ranking, and no source is dropped, down-weighted, or preferred in
collection because of it.

**The decision.**

1. **The primary attention metric is computed per source and reported per
   source.** A pooled figure treats three structurally different constructs as
   one; the counts above are what "structurally different" means concretely.
2. **A pooled series IS reported, as a registered SECONDARY, never primary.**
   Suppressing it would hide a comparison a reader will reasonably want, and
   the cost of carrying it is one more series in a grid that is counted and
   deflated anyway. It is labelled `pooled` and may never be quoted as the
   headline.
3. **The designated primary trial becomes
   `(h = 7d, statistic = v24, match set = mint-exact, series = bluesky)`.**
   Bluesky carries it on the mechanical ground recorded above: it is the only
   series whose metric aggregates many independent emitters rather than a few
   (3,077 authors at 2.19 rows each; top-author share 0.050). This designation
   is made **before any outcome was observed** and is fixed from here.
4. **The trial grid grows and the deflation grows with it.**
   **horizons {1, 3, 7, 30} × statistics {v24, v1, v6, ua24, accel} ×
   match sets {mint-exact, mint+cashtag} × series {bluesky, farcaster,
   telegram, pooled} = 4 × 5 × 2 × 4 = 160 trials.** All 160 are reported. The
   one primary trial is read at α = 0.05; the other 159 are judged against the
   Šidák-adjusted level **α_adj = 1 − (1 − 0.05)^(1/160) = 0.000321**. The grid
   **may not grow further** — a series, statistic, horizon or match set not
   listed here requires another amendment and a new cohort.

**The Telegram construct is described in every result.** Any table, figure or
sentence reporting a Telegram attention number carries the description
**"alert-feed-dominated"** with the Task 1 numbers attached (4 distinct
authors, 16.25 rows/author, 0.831 ambiguous, 4 of 20 channels producing). No
reader may mistake it for community attention, and no result may quote a
Telegram figure bare.

**The under-detection direction, stated now rather than in the discussion
later.** The Telegram instrument is narrow and alert-feed-dominated: a fixed
20-channel list of which 4 produced rows, 4 distinct authors, and a message mix
that names tokens by construction. Such an instrument **under-samples genuine
community attention**, and under-sampling the predictor **biases the measured
association toward the null**. Therefore: **a negative result on the Telegram
series — and on any pooled series containing it — carries an under-detection
caveat and must not be read as evidence that attention does not predict
outcomes; and a positive result is not inflated by this weakness, since the
bias runs the other way.** This sentence is registered here, before any
outcome, so it cannot be produced afterwards as a rationalisation of whichever
result appears.

### Amendment 3 — 2026-08-17 — the death floor gains an explicit third condition: `no_exit_candle`

**What data existed when this amendment was made.** **No cohort outcome
existed, and none was read, fetched, or inspected while drafting.** Stated
precisely rather than loosely: `data/outcomes/` contained **exactly one file,
`benchmark-sol.jsonl`** — the SOL benchmark leg, a price series for SOL that
contains no cohort pool and cannot inform this rule — and **zero
`candles-*.jsonl`**; `data/state/checkpoints.jsonl` was **absent**, so no
checkpoint has ever recorded a pool. The first checkpoint fires **2026-08-26**,
nine days after this amendment. Out-of-cohort candles from the A.3
known-answer test (pools born 2023–2024, not cohort members) exist at
`data/state/kat_raw_candles.json` and were seen during A.3; they are disclosed
here for completeness and are the *evidence* for this amendment, not a cohort
outcome.

**How this amendment is written, given the append-only rule.** §4 is not edited
in place — this registration's own header forbids editing anything above an
amendment line. The amended death floor is therefore reproduced **in full,
here**, and this text governs. §4's original two-condition text remains as
written and is superseded by what follows.

**The gap, and that the code predated the text.** §4's death floor stated two
conditions: (a) no volume-bearing candle in the 14 days ending at the exit
date; (b) exit close below 1% of the entry close. It was **silent** on a third
case: **the exit-day candle is missing while volume exists inside the
lookback** — a pool that traded recently but not on the exit day. The
implementation has always booked this as a total loss with the reason
`no_exit_candle`. **That behaviour predated any registration text authorising
it.** The Stage A.3 known-answer test surfaced the gap on 2026-08-17 by
comparing the path against independently derived expected values, where the
case fired in **13 of 20 sparse-pool cells**. A.3 recorded it as a
specification gap and deliberately did **not** ratify it silently. **This
amendment adopts the code's reading, consciously, as a registration decision
made before any outcome exists** — not as a description of what the code
happens to do.

**The amended death floor, in full.** At horizon `h`, a position **books
exactly −100%** if any of the following holds:

- **(a) `no_volume_in_lookback`** — there is no candle with non-zero volume in
  the 14 days ending at the exit date.
- **(b) `dust_close`** — the exit close is below 1% of the entry close.
- **(c) `no_exit_candle` — the exit-day candle is absent.** A missing daily
  candle means **no trades occurred that day**; no trades at exit means **no
  exit liquidity**; and marking a position that cannot be exited to any price
  manufactures an unrealizable recovery. This is the same rationale that
  produced (b), applied to the case where the mark is missing rather than dust.

**Each condition is its own named verdict** — `no_volume_in_lookback`,
`dust_close`, `no_exit_candle` — and **every result partitions deaths by which
condition fired**. Dead pools stay in their quintile, unchanged. Conditions
(a) and (b), the 14-day lookback, the 1% dust fraction, the entry/exit anchors,
the cost band and every other bar are **unchanged**.

**The bias direction, registered before any outcome — and it runs toward the
hypothesis.** If pools with higher attention trade more frequently, they will
have missing exit-day candles **less often**, so condition (c) fires
disproportionately on the **lower-attention comparison group**. Booking those
as −100% depresses the base rate against which the top attention quintile is
measured, which **biases the measured association toward the hypothesis**.
**This is the opposite direction from the under-detection caveat registered in
Amendment 2**, and both now stand together in this registration: Amendment 2's
narrow alert-dominated Telegram instrument biases **toward the null**;
Amendment 3's death rule biases **toward H1**. Neither cancels the other, they
act on different parts of the measurement, and **both are stated here before any
outcome so neither can be produced afterwards as a rationalisation.**

**The registered mitigation, because the direction is unfavourable.** The rate
at which `no_exit_candle` fires **must be reported per attention stratum as a
first-class Stage B output**, with its n, alongside the returns — never folded
into them. Concretely: for each quintile (and for the registered binary
fallback split), report the share of measurable outcomes booked by each of the
three death conditions. **A large differential in `no_exit_candle` firing
across strata is itself a finding about the instrument** and is reported as
such, whatever it does to the headline. If the differential is large, the
headline is read against it rather than in front of it.

**The alternative reading, registered as a ROBUSTNESS REPORT and explicitly not
a trial.** One alternative is registered: **`carry_forward` — mark the exit to
the last available close at or before the exit date**, instead of booking
−100%. Conditions (a) and (b) still apply unchanged under it. It is computed
and reported alongside the primary at Stage B.

**The constraint, stated so a future session cannot read the pair as a
choice:** the **primary rule is fixed by this amendment**. `carry_forward` is a
**robustness report only**. It **may never become the headline**, may not be
substituted for the primary in any table presented as the result, and may not
be selected on the basis of which produces a more favourable number. **It adds
no cells to the trial grid: the grid remains at 160 and the Šidák level remains
α_adj = 0.000321**, exactly as Amendment 2 registered them. Reporting the two
side by side is a statement about sensitivity to a specification choice, not a
menu. A future session that reports `carry_forward` as the result has violated
this registration, and `tests/test_registration.py` pins the grid size, the
Šidák level and this constraint's text against exactly that.

### Amendment 4 — 2026-08-18 — pre-collection rows are excluded from the attention metric

**What data existed when this amendment was made.** **No cohort outcome
existed and none was read, fetched or inspected.** `data/outcomes/` held
exactly one file, `benchmark-sol.jsonl` (the SOL benchmark leg — no cohort
pool), and zero `candles-*.jsonl`; the first checkpoint fires **2026-08-26**,
eight days out. Attention rows existed and were counted for this amendment:
**150,591 stored mentions** (telegram 127,286 · bluesky 19,878 · farcaster
3,427). Enumeration data was read (37,333 cohort mints with a birth
timestamp). No return, price or outcome informed this text.

**The fact that prompted it.** Telegram's first MTProto connect **backfilled
123,225 rows posted before collection began**, the oldest dating to
**2022-01-06**. MTProto serves channel *history* on connect; the firehoses do
not. Bluesky contributed **0** pre-collection rows and Farcaster **14**.

**What was measured, before deciding anything.** The attention windows use
**`posted_at`**, read from the code rather than assumed
(`attention/metrics.py`: `posted = parse_iso(mention.posted_at)`;
`offset = posted - born_at`; `if offset < timedelta(0): continue`). The
contamination surface was then measured directly by applying the registered
window rule to every stored row against its matched mint's manifest birth:

| | rows |
|---|---|
| pre-collection rows attributed to a cohort pool | **27,577** (mint 945 · cashtag 11,251 · name 15,381) |
| of those, landing inside a registered `[T0, T0+24h]` window | **0** |
| live-collected rows landing inside a window (for scale) | 7,672 |

**The metric was never contaminated.** Every pre-collection row predates the
`T0` of every pool it matched, so the existing `offset < 0` guard already
excluded all of them. The 945 mint-exact pre-collection matches are not an
anomaly: a token's **mint predates its AMM pool**, so a genuine mention of the
token can precede the pool birth this registration anchors on.

**The rule, registered anyway and deliberately.** Per this registration's own
discipline — an implementation accident is not a rule — **a mention whose
`posted_at` precedes its source's collection start is excluded from the
attention metric**, explicitly, whether or not the window arithmetic would have
excluded it. The registered ground: **the construct is forward attention
velocity during the launch window.** A message retrieved from history was not
*observed as it happened*; it is a different instrument, available deeply for
Telegram, not at all for the firehoses, and therefore available unevenly across
sources and across pools. Uniform exclusion keeps every pool measured by the
same instrument.

**The registered collection starts, measured** (first `ingested_at` per source):

| source | collection start | pre-collection rows excluded |
|---|---|---|
| telegram | `2026-08-17T04:28:21Z` | **123,225** |
| bluesky | `2026-08-16T16:30:23Z` | **0** |
| farcaster | `2026-08-16T16:29:50Z` | **14** |

A source with **no** registered start excludes nothing, so adding a source
later cannot silently drop its rows.

**The registered consequence, stated rather than hidden.** A pool whose
`[T0, T0+24h]` window **opens before a source's collection start** receives
only partial coverage from that source. This affects pools born in the first
minutes of the cohort and, for Telegram, pools born before
`2026-08-17T04:28:21Z`. The gap is **left visible rather than filled from
backfill**, because filling it would measure those pools with the historical
instrument and every later pool with the live one. Its direction is toward the
null for the affected pools (attention undercounted), consistent with
Amendment 2's under-detection caveat.

**No bar moves.** The grid stays at **160** cells with **α_adj = 0.000321**,
the horizons, death floor, cost band, matching rules, channel list and
statistics are untouched, and this amendment adds no trial.

### Amendment 5 — 2026-08-18 — the enumeration is incomplete, and the incompleteness is not random

**What data existed when this amendment was made.** **No cohort outcome
existed, and none was read, fetched, or inspected while drafting.**
`data/outcomes/` contained exactly one file, `benchmark-sol.jsonl`, the SOL
benchmark leg; no `candles-*.jsonl` existed for any pool; the first outcome
checkpoint fires **2026-08-26**. What existed was **enumeration telemetry
only**: 55,715 birth rows across three daily manifests, 2,459 lifecycle rows,
and 38,742 ledger rows, frozen as a snapshot at **2026-08-18T04:49:43Z** and
measured in Stage A.5. This amendment therefore describes the **instrument**,
strictly before any forward return could inform the description — which is the
ordering §4 exists to protect.

**Why this is an amendment and not a discussion note.** §1 states that
membership "is decided by birth and by nothing else." **The selection rule is
unchanged and remains true: no mention count, engagement figure, listing,
trending page, archive or "top coins" surface participates in enumeration, and
none ever did.** What A.5 measured is that the *realised* cohort is additionally
thinned by an instrument artefact — a paced reader that cannot keep up with the
feed — and that the thinning is **correlated with birth rate**. A reader of §1
would otherwise take the enumerated cohort to be the birth-ordered population.
It is a **non-uniform sample** of it. That belongs in the registration, before
any result is read, rather than in the discussion afterward.

**The measured miss.** Measured mechanically from the feed's own ordering: the
watcher keeps a cursor at the newest `pool_created_at` already written and
treats as fresh only what is strictly newer, so a sweep reporting
`new_births == pools_seen` **proves** that every slot it read was created after
the previous sweep's newest — that the two reads did not overlap, and that the
interval between them was never read.

| quantity | measured |
|---|---|
| consecutive sweep pairs with **zero overlap** | **401 of 884 = 45.4%** |
| feed time elapsed inside continuous watcher runs | 34.50 h |
| feed time actually read (union of per-page windows) | 24.28 h |
| **coverage** | **70.4%** |
| **feed time never read** | **29.6%**, in 1,290 proven-uncovered gaps |
| gap length p10 / p50 / p90 / max | 2 s / 10 s / 65 s / 667 s |

**The miss rate, bounded by two independent routes:**

| route | implied true full-feed rate | miss rate |
|---|---|---|
| **A** — integrate each proven gap at the feed rate measured locally in the page windows bracketing it | 43,497/day | **34.7%** |
| **B** — the feed's own in-window birth rate, time-weighted, independent of any gap model | 39,326/day | **27.8%** |
| enumerated, for comparison | 28,385/day | — |

**The two routes agree within 10.6%. The registered figure is a miss rate of
28 to 35 percent**, ≈ 21,700 births never enumerated over 34.5 h, of which
≈ 4,000 were `amm`.

**The estimate is a LOWER BOUND on both routes, and the reason is registered
here so it is not discovered later as a convenience.** Route B measures the
birth rate only during *covered* time, and covered time is biased toward quiet
periods (see the concentration below), so it understates the true rate and
therefore the miss. Route A prices each gap at the rate of the page windows
that bracket it, and those windows are by construction slower than the gaps
they surround — a gap opens precisely because the feed outran the reader. Both
routes therefore err in the same direction, toward **under**-stating the miss.
Neither is a point estimate to be quoted bare.

**Where the miss falls.** **75.4% in gaps between sweeps, 24.6% in holes
between pages of a single sweep.** The second figure is registered because it
bounds what a cadence change can fix: even an infinitely fast sweep cadence
leaves roughly a quarter of the miss in place. A live probe measured a
13-second hole between page 2 and page 3 of a single 4-page walk, so the feed
**skips across pages as well as duplicating**; coverage is therefore computed
from per-page windows, never per-sweep windows.

**The miss is NOT uniform thinning, which is the part that matters.**

By time of day, the miss rate spans **8.7% at 07:00 UTC to 65.0% at 16:00 UTC
— a 56-point spread and a 7.4× ratio**. By burst intensity, with the
proven-uncovered gaps split into quintiles by the feed rate measured at the
gap:

| quintile of feed rate at the gap | gaps | feed rate | share of all missed births |
|---|---|---|---|
| Q1 slowest | 259 | 29,077/day | 5.4% |
| Q2 | 258 | 37,023/day | 9.6% |
| Q3 | 257 | 44,941/day | 17.7% |
| Q4 | 258 | 51,967/day | 22.1% |
| **Q5 fastest** | 258 | 62,666/day | **45.2%** |

**The fastest birth-rate quintile carries 8.3× the missed births of the
slowest, on the same number of gaps.**

**The direction, stated now rather than in the discussion later**, in the
pattern of Amendments 2 and 3. **Pools born during bursts are systematically
less likely to be enumerated.** Bursts in pool creation are periods of elevated
market-wide activity, which is the same latent condition under which social
attention is heaviest. The cohort therefore **under-samples exactly the periods
where the predictor has its largest values and its largest variance**, and
under-sampling the high end of the predictor **biases the measured association
toward the null**. Therefore: **a negative result carries a declared
under-detection caveat and must not be read as evidence that attention does not
predict outcomes; and a positive result is not inflated by this weakness, since
the bias runs the other way.** This runs in the **same** direction as
Amendment 2's under-detection caveat and the **opposite** direction from
Amendment 3's `no_exit_candle` caveat; all three stand, and none cancels
another.

**Stated precisely, because the distinction is load-bearing: this is not
attention-driven selection.** No attention surface touches enumeration. It is
selection on a variable *correlated* with attention, which is a weaker but real
threat, and it is exactly the mechanism §5's survivorship audit exists to
expose. It does not void the registration under §9 — the enumeration source,
ordering rule and denylist are unchanged — but it is a permanent, declared
property of this cohort.

**The reporting requirement, registered as a first-class output and not a
footnote.** Every result in this repository, **at every horizon**, reports
alongside the survivorship audit §5 already requires:

1. the **enumeration miss rate** with its 28–35% bound, both routes, and the
   statement that it is a lower bound;
2. its **non-uniformity** — the 8.7%/65.0% time-of-day spread and the 8.3×
   burst-quintile concentration — because a uniform 30% thinning would cost
   power and nothing else, and this is not uniform;
3. the **n** of the cohort the result rests on, in the same sentence as the
   number, per the standing rule that a negative with a hidden n is not a
   result.

A result that omits these is not reportable. No table, figure or sentence
carrying a cohort return may appear without them.

**The operator's chosen response is option D — accept documented incomplete
enumeration on the free tier.** A.5 priced complete enumeration at
9,500–14,100 watcher requests/day and the combined budget at 26,330/day, which
only the Lite tier ($499/mo) clears; Analyst at 16,438/day is 61% short. Option
D fits the measured 14,400/day pacing capacity with a 1% margin. **The
documentation this option requires is this amendment.**

**No bar moves.** The grid stays at **160** cells with **α_adj = 0.000321**,
and **this amendment adds no trial**. The universe rule, source, ordering,
launch-venue denylist, horizons, death floor, cost band, matching rules,
channel list, attention windows and statistics are all untouched. Nothing
collected changes, and nothing already collected is discarded or reweighted.
