# DECISIONS.md — architecture decision records

Append-only. Read before revisiting any settled question. Decisions inherited
from solclear or MLCryptoEngine cite their ADR numbers.

## ADR-001: Enumeration is birth-ordered from a keyless feed, and attention never touches it

**Date:** 2026-08-16 · **Status:** accepted · inherits solclear ADR-015

**Context.** solclear Stage E measured a **60-point 30-day death-rate gap
(97.5% on 40 birth-ordered pools vs 18.75% on 16 attention-crawled ones)**
produced by nothing but which pages a crawler chose to archive. A study of
whether attention predicts outcomes is uniquely vulnerable to this: if the
cohort is drawn from any surface that ranks, lists, trends, or archives by
attention, then "attention predicts survival" is guaranteed by construction,
because the sample was selected on survival by an attention proxy upstream of
any analysis. The bias leaves no trace in the data itself.

**Decision.** The universe is enumerated **only** from a keyless public
new-pools feed, ordered strictly by `pool_created_at`, with **no attention
input of any kind** in the enumeration. No trending page, listing site,
archive, "top coins" surface, mention count, or engagement figure participates
in deciding membership. Attention is measured **on** the cohort, never used to
**form** it. The measured death-rate gap between the birth-ordered cohort and
every attention-selected subset is a first-class reported output at every
horizon (REGISTRATION.md §5), not a caveat in a footnote.

**Consequences.** The cohort will be dominated by tokens nobody ever mentioned,
most of which die, and the study's statistical power comes from the small
matched subset rather than from the cohort size. That is the correct shape: the
alternative is a larger sample that answers a different question. Any successor
that cannot enumerate births unbiased should not run this study at all.

## ADR-002: Venue class is a recorded tag from a launch-venue denylist, and filtering happens at analysis

**Date:** 2026-08-16 · **Status:** accepted

**Context.** The new-pools feed mixes bonding-curve launch venues with AMM
pools; solclear measured **101 of 122** sampled pools as pump.fun curves. The
two populations behave differently enough that pooling them would dominate any
result (solclear Stage E: a birth-ordered curve feed dies at ~97.5% regardless
of any launch-window score). A filter is therefore required — but *how* it is
implemented decides whether the cohort can be quietly reshaped later.

**Decision.** Every enumerated pool is **written to the manifest with a
`venue_class` tag**; nothing is discarded at collection time. The tag comes
from a **denylist of known launch venues** (`launchpad`), everything else being
`amm`. A denylist rather than an allowlist, deliberately: an AMM that appears
mid-collection is included automatically, where an allowlist would silently
drop it and bias the cohort toward venues that happened to exist on
registration day. The registration fixes the `amm` subset as the primary
universe, so the analysis filter is applied to a tag whose rule predates the
data.

**Consequences.** A dex id missing from the denylist misclassifies a launch
venue as an AMM — a real risk, mitigated by the >2× rate-disagreement check
(REGISTRATION.md §1) which would surface it as an implausible `amm` rate. The
correction is an amendment starting a new cohort, never a mid-collection edit.

## ADR-003: Every outbound request passes a per-source, daily-capped, append-only ledger — free APIs included

**Date:** 2026-08-16 · **Status:** accepted · inherits solclear ADR-003

**Context.** Every source this project touches is free or keyless, which is
exactly the condition under which metering gets skipped. The failure mode is
not one big request but many small ones that individually look free: solclear
measured GeckoTerminal returning HTTP 429 at 2.5 s spacing despite a documented
30/min limit, and its parent project's gate fired correctly twice in production.
**A free tier still has limits, and a gate that never fires is still a gate** —
its value is that it *cannot* be walked past, not that it is frequently hit.

**Decision.** Port the gate in shape. Every request is **counted before it is
sent** against a per-source daily cap; the ledger is **append-only on disk** and
re-read on start, so a restart cannot walk past the cap; **a refusal names the
arithmetic and writes nothing**; and the paced client is the only transport, so
an unmetered call is structurally unavailable rather than merely discouraged.
Pacing is set from measurement (6.0 s for GeckoTerminal), never from the
published figure. Caps are self-imposed; raising one is a deliberate decision
made before a run, never mid-run.

**Consequences.** A runaway loop, a mis-paced sweep, or a restart cannot get the
project rate-limited into a collection gap it cannot recover — a gap in a
forward-recorded cohort is unfixable, unlike a gap in a retrospective one.
The cost is friction in tests, which must construct a ledger.

## ADR-004: Stage A attention is mechanical; no LLM judgment produces any attention figure

**Date:** 2026-08-16 · **Status:** accepted · inherits MLCryptoEngine rule 4

**Context.** An LLM-scored relevance or sentiment weight is attractive here and
would be a registration hazard: its behaviour is not stable across model
versions, its output cannot be reproduced exactly at a later date, and its
judgments would be impossible to pre-register in a way a later session could
verify was honoured.

**Decision.** Stage A attention figures are **counts and their velocities**:
`mentions(w)`, `authors(w)`, and the five registered statistics. No sentiment,
no relevance score, no summarization, no model-derived weighting participates
in any attention number in this stage. The registration fixes the windows and
the quintile construction ex ante (REGISTRATION.md §2), so the whole metric is
reproducible from the raw store by arithmetic alone.

**Consequences.** The metric is blunt — a mention is a mention whether it is
enthusiasm or a scam warning. That bluntness is the price of a figure that can
be pre-registered and reproduced, and any later LLM-weighted variant is a new
hypothesis in the same family, registered separately, not a refinement of this
one.

## ADR-005: An ambiguous match is attributed to nobody and counted as its own first-class class

**Date:** 2026-08-16 · **Status:** accepted

**Context.** Memecoin tickers are reused constantly; a popular cashtag will
match several hundred distinct mints within any 30-day active window. **Ticker
collisions are the expected failure mode of this study, not an edge case.** Any
scheme that resolves a collision — most recent, most liquid, most mentioned,
fractional split — is manufacturing attention data, and it manufactures it in
the direction that inflates the apparent attention of whichever token the
resolver favours. Since the favoured token is typically the one that is already
doing something, the resolver would reintroduce exactly the survivorship
selection ADR-001 exists to keep out.

**Decision.** A cashtag or name matching **more than one** mint in the active
universe is recorded as **`ambiguous`** and attributed to **none of them**.
Ambiguous is a first-class category with its own daily count, reported
alongside matched and unmatched. Mint-address exact match beats a conflicting
cashtag, with the conflict recorded and counted. The **primary analysis uses
mint-exact matches only**; cashtag and name form a registered secondary match
set reported separately.

**Consequences.** The mint-exact sample will be much smaller than the total
message volume, and the ambiguous count is expected to be large — that count is
a measurement this project reports rather than a loss it minimizes. If the
mint-exact sample proves too small to be informative, that is a finding about
how Solana attention is actually expressed, reported as such.

## ADR-006: The return anchor is the `d0+2` daily candle, so no return bar overlaps the attention window

**Date:** 2026-08-16 · **Status:** accepted

**Context.** Attention is accumulated over `[T0, T0+24h]`. Any return bar
overlapping that window leaks the outcome into the predictor: a token whose
price moved during hour 20 both attracted mentions and generated return, and a
bar containing hour 20 would credit the attention with a move it co-occurred
with. Because `T0` can fall at any time of day, an anchor defined as "the next
daily candle" overlaps the window for late-day births.

**Decision.** With `d0` the UTC date of `T0`: **entry mark is the close of the
daily candle for `d0 + 2`**, exit at horizon `h` is the close for `d0 + 2 + h`.
The `d0+2` candle opens at `00:00Z` on `d0+2`, which is strictly after
`T0 + 24h` for **every** time-of-day of `T0`. The consequence — entry sits 24
to 48 hours after birth depending on birth hour — is registered explicitly as a
fixed property of a deterministic rule, not a per-pool choice.

**Consequences.** The study measures a lagged forward return rather than an
immediately-actionable one, which is the honest thing to measure given the
attention window it registered. It also costs power: a day of the most volatile
part of a memecoin's life is excluded from the measured return by construction.
Both are accepted; a leak-free small effect is worth more than a contaminated
large one.

## ADR-007: The channel list is fixed by an objective rule at registration and never edited mid-collection

**Date:** 2026-08-16 · **Status:** accepted

**Context.** Which channels are watched decides which attention exists as far
as this instrument is concerned. A list built by browsing, by relevance, or by
"the ones that seem active" is an attention-selected instrument measuring
attention — solclear's circularity moved one level up, and it would be
invisible in the data. It cannot be removed, only fixed in advance.

**Decision.** The list is **the top 20 public Solana/memecoin Telegram channels
by member count, from a single stated public directory, read on a single stated
date**, ranked by the directory's own member-count field, ties broken by
username ascending, with every exclusion recorded by name and reason. It is
**never edited mid-collection.** A channel that goes quiet stays on the list
with zero messages — that is data. Adding, dropping, or replacing a channel
requires an amendment that **starts a new cohort**.

**Consequences.** The instrument will miss attention that lives in channels
outside the top 20, in DMs, in private groups, and on platforms not sampled —
so this measures *visible* attention on a fixed instrument, which is exactly
what it claims. If the directory is unreachable on the registration date, the
Telegram source does not start collecting until the list is fixed; a
provisional list that gets "improved" later is worse than a late start.

## ADR-008: Source verification includes a freshness bar, because reachability is not liveness

**Date:** 2026-08-16 · **Status:** accepted · measured in Task 2

**Context.** The Task 2 verification of Farcaster probed six public hubs. One,
`hub.pinata.cloud`, answered `GET /v1/info` with **HTTP 200 and an
823,527,781-message db-stats payload** — every signal a reachability check
looks for. Its newest event was **238 days old**. A reachability-only check
would have accepted it, the collector would have polled a dead hub forever, and
this project would have recorded **zero Farcaster attention on every cohort
while believing the source was working**. That failure is silent, permanent in
a forward-recorded cohort, and indistinguishable in the data from "nobody
mentioned these tokens on Farcaster" — which is a *result* this study might
otherwise have reported.

**Decision.** A source verifies only if it is **reachable AND fresh**. For
Farcaster, freshness is measured directly: seed each shard at
`(maxHeight − 300) << 14` (the event-id encoding, measured not documented),
read the newest dated cast, and fail the hub if its tip is older than
`MAX_TIP_AGE_SECONDS` (3600). The probe order runs until a hub passes **both**
bars; every rejected candidate is recorded with its measured reason in
`docs/ACCESS.md`. The hub that passed, `snap.farcaster.xyz:3381`, measured a
tip age of 5–11 seconds.

**Consequences.** Verification costs more requests than a liveness ping, which
is the correct trade for a project whose whole output is a measurement. The
principle generalizes past Farcaster and is now the standard for any source
added later: **a source that returns data is not thereby serving current data**,
and for a forward-recorded study only current data exists.

## ADR-009: The registered rate and saturation checks are judged on a measured rate, and an undecidable check says so

**Date:** 2026-08-16 · **Status:** accepted · corrects an implementation, not the registration

**Context.** REGISTRATION.md 1 compares "the observed `amm` birth rate" against
~1,330/day, and section 7 trips saturation when "the measured `amm` birth rate
exceeds 2,400/day". Both are **rates**. The first implementation compared the
day's count-so-far against a full-day expectation, which would have reported a
disagreement every morning (a partial day always undershoots a full-day
figure), and could not trip saturation until a day was nearly over — by which
point the capacity it protects has already been spent.

**Decision.** Both checks are computed from a rate measured over the span the
births themselves cover, using `(n − 1) / span` so a small sample is not
overstated by the endpoint. A day with fewer than 20 births or a span under 10
minutes reports **`basis="insufficient"` and asserts nothing** — an undecidable
check must say so rather than defaulting to agreement, which is the same
fail-closed rule the refusal semantics follow everywhere else. A **closed** day
is judged on its count, and the digest records which basis was used.

**Consequences.** The check is honest on a partial day and can fire early
enough to matter. No registered number changed; this makes the code compute
what the registration already said.

## ADR-010: The observed birth rate disagrees with the registered expectation by ~6x — reported, not reconciled

**Date:** 2026-08-16 · **Status:** accepted · the registered check fired on its first day

**Context.** The registration fixed an expected ~1,330 `amm` pools/day from
solclear's Stage B addendum (measured 2026-08-13, n = 122) and registered that
**a disagreement of more than 2× is reported as a disagreement and never
averaged away**. First measurement, 2026-08-16T16:26–16:46Z: **443 unique pools
enumerated, 95 tagged `amm`, over a 17-minute span → a measured rate of ~7,877
`amm` pools/day, 5.92× the registered expectation.** The full-feed rate,
~37,000/day, is 4.1× solclear's ~9,000/day and 2.7× its newest−oldest variant
(~14,000/day). The `amm` share also moved: **21–24% observed against solclear's
14.8%** (18 of 122).

**Decision.** The disagreement is **reported with its span and its n, and is
not reconciled, averaged, or used to edit anything.** Candidate causes are
named without picking one: (a) genuine venue-mix and activity shift in the
three days since solclear measured; (b) a methodological difference — solclear's
headline used `N ÷ (retrieval time − oldest pool_created_at)`, which includes
retrieval lag and biases *down*, while this measures newest−oldest; (c) a dex id
absent from the launch-venue denylist misclassifying a bonding curve as `amm`.
**The denylist is not edited to make the number agree** (REGISTRATION.md 9:
editing it mid-collection voids the registration). The authoritative check is
the first **complete** UTC day, judged on its count.

**Consequences, and this one needs an operator decision.** The registered
capacity plan does not fit the observed rate. At ~7,900 `amm` births/day,
outcome checkpoints need **~15,800 requests/day against a 14,400/day measured
capacity and a 10,000/day registered cap** — the arithmetic REGISTRATION.md 7
performed at ~1,330/day no longer closes. The registered saturation rule fired
and the watcher recorded it (three markers by 16:46Z). **It does not silently
sample and it does not silently drop**, so outcome coverage will simply refuse
at the cap until the operator decides between: raising the cap and re-measuring
whether a faster pace holds; amending the universe to a narrower registered
sub-cohort, which starts a new cohort; or accepting a registered, stated
sampling rule, which also starts a new cohort. **No option may be taken
silently, and this session takes none of them.**

## ADR-011: MTProto reads are accounted at one ledger charge per channel-history request

**Date:** 2026-08-17 · **Status:** accepted · closes the gap recorded in the Stage A addendum

**Context.** The registered 50,000/day telegram cap (ADR-003, registry) was not
enforced by the ledger: MTProto traffic is not HTTP and never passed the
`PacedClient`, so the cap was held only by the incidental per-cycle read limit
(50 messages × 20 channels). That is a fail-open gate — a later cadence or
limit change would have removed the constraint without any mechanism noticing,
and "a gate that never fires is still a gate" only holds when the gate is
actually wired to the thing it claims to meter.

**Decision.** The unit of MTProto accounting is the **channel-history request**
— one `charge("telegram", 1)` per channel per cycle, priced **before** the
request is sent, through the same `Ledger` the registration declares, with the
same semantics as every other source: **a read that would breach the cap
raises `RequestCapError`, nothing is fetched, the refusal names the arithmetic
and writes nothing**, and the collection cycle ends at the refusal rather than
working around it. The charge hook is injected into `telegram.consume` so an
unmetered read path is structurally unavailable, and
`tests/test_ledger.py::test_mtproto_channel_read_refuses_at_the_telegram_cap`
pins the refusal in the pattern of the existing gate tests. Flood control is
instrumented **passively** in the same change: every `FloodWaitError` is
recorded as a `flood_wait` lifecycle marker with its channel and requested
wait, the channel is skipped for that cycle, and the wall is never probed
toward or slept against — deliberately tripping it risks the account and buys
a number the measurement does not need.

**Consequences.** The cap binds through the mechanism that claims to enforce
it: at the current 20-channel list and ~5-minute cadence the spend is ~5,760
charges/day against 50,000, so the gate is quiet headroom, not friction — and
if the channel list or cadence ever changes, the ledger notices where the
incidental limit would not have. Message-level accounting (one charge per
message read) was considered and rejected: Telethon batches history into one
request per 100 messages, so per-message charges would meter a quantity that
does not correspond to outbound requests, and the registration's ledger counts
requests.

## ADR-012: The attention metric is partitioned by source; pooled is secondary, never primary

**Date:** 2026-08-17 · **Status:** accepted · implements REGISTRATION.md Amendment 2

**Context.** The resolved Telegram channels that produced rows in the first
window are automated trending-alert feeds rather than discussion communities.
Measured mechanically, before any outcome existed and with the proxies stated
before they were computed: **Telegram emits 16.25 rows per author from 4
distinct authors; Bluesky 2.19 from 3,077.** Telegram's unmatched share is
**0.031** against Bluesky's **0.487** — nearly everything Telegram emits matches
the token vocabulary, the signature of a feed that names tokens by construction
rather than of people who sometimes mention them. Its ambiguous share is
**0.831**. A single pooled attention number would sum three quantities that are
not the same quantity, and the sum would be dominated by whichever source
happened to emit most rows, which is a property of the instruments rather than
of attention.

**Decision.** The primary attention metric is **computed and reported per
source**. A **pooled** series is reported as a registered **secondary** and may
never be quoted as a headline — reported rather than suppressed, because hiding
the comparison would be its own distortion, and it costs one series in a grid
that is counted and deflated regardless. The designated primary trial becomes
`(7d, v24, mint-exact, bluesky)`: Bluesky carries it because it is the only
series aggregating many independent emitters (3,077 authors, top-author share
0.050), a mechanical ground recorded before any outcome was observed. The grid
grows to **4 × 5 × 2 × 4 = 160** and the Šidák level to **0.000321**; the one
primary trial is read at α = 0.05 and the other 159 against the adjusted level.
Every Telegram figure ships with the label **alert-feed-dominated** and its
characterisation numbers attached. The **under-detection direction is
registered now**: a narrow alert-dominated instrument under-samples community
attention, which biases the measured association **toward the null**, so a
negative on Telegram or on any pooled series carries an under-detection caveat
and a positive is not inflated by this weakness.

**Consequences.** Statistical power falls — the deflated level is ~4× stricter
than the previous 0.00128 — and that cost is accepted deliberately, because a
grid that pretends three constructs are one is cheaper only until someone reads
the number. Nothing collected changes: the channel list stays frozen under §7's
never-edit rule (Telegram has collected since 2026-08-17T04:28Z), and no
matching rule, window, horizon, death rule, cost band or kill criterion was
touched. The alternative considered and rejected was dropping Telegram from the
primary entirely; it was rejected because the characterisation is a description
of what the source emits, not a quality ruling, and discarding a collected
source after seeing its shape is the shape of decision this project's
registration discipline exists to prevent.

## ADR-013: The death floor gains a third named condition, adopted deliberately rather than ratified silently

**Date:** 2026-08-17 · **Status:** accepted · implements REGISTRATION.md Amendment 3

**Context.** §4's death floor named two conditions and was silent on a third
case: **the exit-day candle is missing while volume exists inside the
lookback**. The implementation had always booked that as a total loss with the
reason `no_exit_candle`, and **that behaviour predated any registration text
authorising it**. Stage A.3's known-answer test surfaced the gap on 2026-08-17,
where the case fired in **13 of 20 sparse-pool cells**. On a cohort that
solclear's priors put at ~97.5% dead within 30 days, this is the norm rather
than the edge, so leaving it unregistered meant the majority of the study's
deaths would have been booked by an unwritten rule.

**Decision.** Adopt the code's reading as the **primary registered rule**,
consciously and in registration text: a missing exit-day candle books −100%,
because a missing daily candle means no trades that day, no trades at exit
means no exit liquidity, and marking a position that cannot be exited to any
price manufactures an unrealizable recovery — the same rationale that produced
the dust-close condition, applied where the mark is missing rather than tiny.
Each condition becomes its own **named verdict** (`no_volume_in_lookback`,
`dust_close`, `no_exit_candle`) so results partition by which one fired. One
alternative, `carry_forward` (mark to the last available close), is registered
as a **robustness report computed alongside the primary** — never a selectable
trial, never a headline, and adding **no cells to the grid**, which stays at
**160** with **α_adj = 0.000321**.

**The bias direction, and why it is registered rather than discussed later.**
Higher-attention pools that trade more frequently will miss exit-day candles
less often, so this condition fires disproportionately on the **lower-attention
comparison group**, depressing the base rate and **biasing the measured
association toward H1**. That is the **opposite direction** from Amendment 2's
under-detection caveat, which biases toward the null. Both now sit in the
registration together; they act on different parts of the measurement and
neither cancels the other. Because this direction is unfavourable, the
mitigation is registered with it: the **per-attention-stratum firing rate of
`no_exit_candle` is a first-class Stage B output** reported with its n
alongside the returns, and **a large differential is itself a finding about the
instrument**.

**Consequences.** The rule that will book most of this study's deaths is now
written down, attributable, and partitionable, and the direction it pushes the
result is on the record before any outcome was read. The alternative reading is
available as sensitivity without becoming a second bite at the headline. The
cost accepted: `carry_forward` will sometimes look better than the primary, and
this registration forbids reporting it as the result anyway — which is the
point, and `tests/test_registration.py` pins that constraint's text along with
the grid size and the Šidák level.

## ADR-014: The collectors run under systemd user units, not a supervised shell loop

**Date:** 2026-08-18 · **Status:** accepted · corrects a defect recorded in Stage A.1

**Context.** A.1 reported the daily pass as "scheduled" and listed it as a
"third supervised component". **That was wrong, and the error is the point of
this ADR:** what existed was a `nohup`'d `while true` loop in
`scripts/run_collectors.sh`, owned by a shell whose parent was a session. There
was **no crontab entry and no systemd unit** — nothing that survives a logout,
a reboot, or the parent exiting. On 2026-08-18 the loops stopped at
02:43–02:44Z with clean lifecycle stop markers and nothing restarted them:
**1h35m of watcher downtime and 1h37m of collector downtime** before it was
noticed. In a forward-recorded cohort that gap is unrecoverable, which is
exactly the failure ADR-003 was written to avoid on the request side.

**Decision.** Persistence moves to **systemd user units**:
`solattn-watch.service` (`Restart=on-failure`), `solattn-collect.service`
(`Restart=always` — `collect` exits normally after each bounded cycle, so
systemd *is* the loop), and `solattn-daily.timer` → `solattn-daily.service`
(`OnCalendar=*-*-* 00:40:00 UTC`, **`Persistent=true`** so a run missed while
the machine was off fires on next boot). All are `enable`d into
`default.target` / `timers.target`, and **lingering is on**, so they start at
boot and survive logout. `run_collectors.sh` remains as a manual/dev tool and
is no longer the production mechanism.

**Consequences.** The schedule now survives the failure that actually happened.
`Persistent=true` proved itself immediately: enabling the timer fired the
missed 00:40Z daily pass at once, self-healing a run that the shell loop had
simply lost. Two safeguards now overlap by design — the timer's `Persistent`
and the checkpoint catch-up window (ADR-012's `due_days`) — and the redundancy
is deliberate, because a missed outcome checkpoint cannot be recovered after
the vendor's trailing history window closes. **A claim that something is
"scheduled" now means a unit file exists**, and this ADR is the standing
reminder that the previous claim did not.

## ADR-015: A mention retrieved from history is not forward attention

**Date:** 2026-08-18 · **Status:** accepted · implements REGISTRATION.md Amendment 4

**Context.** Telegram's first MTProto connect backfilled **123,225 rows posted
before collection began**, oldest 2022-01-06, because MTProto serves channel
history on connect. Bluesky and Farcaster, being firehoses, backfilled 0 and 14
respectively. Measured against the registered window rule, **0 of the 27,577
cohort-attributed pre-collection rows landed inside any `[T0, T0+24h]`
window** — the metric reads `posted_at` and already guards `offset < 0`, so
none of them were ever counted.

**Decision.** Register the exclusion **explicitly anyway**. The metric's
immunity was a property of the window arithmetic, not a stated rule, and this
project's standing discipline is that **an implementation accident is not a
rule** — a later cadence change, an anchor change, or a source whose backfill
postdates a pool's birth would silently turn it into contamination. A mention
whose `posted_at` precedes its **source's registered collection start** is
excluded, uniformly, because the registered construct is *forward* attention
velocity: a message retrieved from history was not observed as it happened, and
history is available deeply for Telegram, not at all for the firehoses, and
therefore unevenly across sources and pools.

**Consequences.** Telegram loses 123,225 stored rows from the metric (96.8% of
its rows; they remain on disk, excluded at computation rather than deleted),
Bluesky 0, Farcaster 14 — and **no counted figure changes**, because none were
counted. A pool whose window opens before a source's start now gets visibly
partial coverage from that source rather than backfill-filled coverage; the
direction is toward the null for those pools. The rule is keyed on a per-source
constant, and a source without one excludes nothing, so adding a source cannot
silently drop its rows.

## ADR-016: The enumeration miss is registered as a declared property of the cohort, not a discussion note

**Date:** 2026-08-18 · **Status:** accepted · implements REGISTRATION.md Amendment 5

**Context.** §1 states that membership "is decided by birth and by nothing
else." Stage A.5 measured, mechanically and from the feed's own ordering, that
**28–35% of births are never enumerated**: 401 of 884 consecutive sweep pairs
show zero overlap, which proves the read window advanced past what was read,
and the union of per-page read windows covers only **70.4%** of elapsed feed
time. Two independent routes — integrating each proven gap at the locally
measured rate, and the feed's own in-window rate — agree within 10.6%.

**The miss is not uniform.** It spans **8.7% at 07:00 UTC to 65.0% at 16:00**,
and the fastest birth-rate quintile carries **8.3× the missed births of the
slowest on the same number of gaps**. Uniform thinning would cost power and
nothing else. This concentrates in exactly the periods where market-wide
activity — and therefore social attention — is heaviest.

**Decision.** Register it, with its figures, its direction, and a per-result
reporting requirement, **before any outcome is read**. The selection *rule* is
unchanged and no attention surface touches enumeration; what is registered is
that the *realised* cohort is a **non-uniform sample** of the birth-ordered
population, thinned by a paced reader that cannot keep up with the feed.

The direction is registered in the pattern of Amendments 2 and 3: under-sampling
the high end of the predictor **biases the measured association toward the
null**, so **a negative carries a declared under-detection caveat and a positive
is not inflated by it**. The estimate is registered as a **lower bound on both
routes**, with the reason — route B measures the rate only during covered time
(biased quiet), route A prices gaps from the slower windows bracketing them.

**Alternatives rejected.** *Fixing enumeration instead of declaring it*: A.5
priced complete enumeration at a combined 26,330 requests/day, which only the
Lite tier ($499/mo) clears; the operator chose the free tier, so option D
governs and the documentation it requires **is** this registration. *Reporting
it in the Stage B discussion*: a caveat written after a result is read is
indistinguishable from a rationalisation of that result, which is the failure
rule 2 exists to prevent. *Restricting the universe to shrink the miss*: that
starts a new cohort and does not make the sample uniform.

**Consequences.** Every result, at every horizon, now carries the miss rate,
its non-uniformity, and its n, alongside the survivorship audit §5 already
requires — a result that omits them is not reportable. No bar moves: the grid
stays at **160** cells with **α_adj = 0.000321** and this amendment adds no
trial. Nothing collected changes and nothing already collected is discarded or
reweighted. `tests/test_registration.py` pins the figures, the lower-bound
statement, the direction and the reporting requirement, so a later deletion
breaks the build.

## ADR-017: On the enumeration path, an unanswered page is not an empty one

**Date:** 2026-08-18 · **Status:** accepted · extends ADR-012 to enumeration

**Context.** `geckoterminal.fetch_new_pools` returned `[]` on any non-2xx, and
`sweep_once` read a falsy page as the end of the feed. **A 429 therefore ended
the sweep early, silently** — no refusal marker, no error marker, and a
short read recorded as a complete one. This is precisely the absent-data versus
measured-absence shape ADR-012 fixed on the OHLCV path after the A.3
known-answer test, left live on the enumeration path.

The ledger could not have surfaced it either: it charges **before** sending and
never recorded the status, so a 429 and a 200 were indistinguishable in the
record. A.5 had to re-probe the live source to discover the rate limiter fires
at all (2 of 10 requests at ~3 s effective spacing).

**Stated precisely: the defect never fired in the collected data.** All **887
of 887** sweeps recorded `pages_read = 4` and `pools_seen = 80`; zero truncated
sweeps and zero pool-slots lost. The 429s were provoked by a probe adding a
third client alongside the two watchers of ADR-018. This ADR fixes a latent
defect, and says so rather than implying data was lost.

**Decision.** `fetch_new_pools` returns `None` when the source did not answer
and `[]` when it answered with no rows. `sweep_once` treats the two
differently: `None` writes an **error** lifecycle marker naming the page,
counts `pages_unavailable`, sets `truncated`, and stops — explicitly *not* as
end-of-feed; `[]` ends the sweep with no marker, because a served empty page is
measured absence. Both counters ride on the per-sweep heartbeat, so a
retrospective can find truncated sweeps without re-probing the source. A
truncated sweep still writes the pages that **were** served: refusing loudly
must not discard good data.

The ledger records the status as an **append-only settle row** carrying
`count = 0`. The charge is priced before the request is sent and the ledger is
append-only, so the status cannot go on the charge row and the charge row
cannot be edited. `count = 0` means recording a status can never move a cap.
Rows written before this ADR carry no `kind` and read as charges, which is what
they were.

**Consequences.** The ledger file roughly doubles in rows, and `spent()` reads
the whole file per charge, so the pre-charge read cost roughly doubles with it
— measured at well under the 6.0 s pacing interval, and the price of being able
to tell a served request from a refused one. `Ledger.statuses()` reports
per-source status tallies per day. Five tests pin the branches: a 429 is not
end-of-feed, a served empty page is, a truncated sweep is visible in the
lifecycle log, a truncated sweep still writes what it read, and a settle row
never inflates the cap.

## ADR-018: The manual collector script refuses to start alongside the systemd units

**Date:** 2026-08-18 · **Status:** accepted · closes the gap ADR-014 left open

**Context.** ADR-014 made the systemd user units the production mechanism and
recorded `scripts/run_collectors.sh` as "a manual/dev tool ... no longer the
production mechanism." **It did not stop the script, and a declaration is not a
mechanism.** Both ran concurrently from **2026-08-18T04:20:35Z** — two `start`
markers four seconds apart — until stopped: **two watchers against one source,
a doubled request rate, and ~3 s effective spacing** against a source measured
to return HTTP 429 at that spacing. A.5 found it only because the lifecycle log
carried 12 byte-identical duplicate heartbeats.

The cohort survived it: manifests deduplicate by pool on read, so no birth was
double-counted, and no sweep was truncated. The costs were budget and the
raised probability of the ADR-017 defect firing.

**Decision.** The script refuses to `start` or run `daily` while any of
`solattn-watch.service`, `solattn-collect.service` or `solattn-daily.timer` is
active. The refusal names the arithmetic and the measured cost, states that
nothing was started and nothing was written, prints the exact command to stop
the units, and exits 3 — the same refusal discipline the ledger uses. It is
overridable by `SOLATTN_ALLOW_ALONGSIDE_SYSTEMD=1`, deliberately: a guard with
no explicit override gets worked around rather than obeyed.

`status` now reports the systemd units first, because reporting only this
script's pidfiles printed "not running" while the collectors were in fact
running under systemd — the misreading that let the collision persist.

**Consequences.** The collision cannot recur on the next manual restart without
an explicit override. Five tests pin the guard against a PATH-shimmed
`systemctl`; the non-refusing paths are exercised through `status` so the test
suite can never launch a real collector. The guard is a no-op on a machine with
no `systemctl`, so the script still works as a dev tool where systemd is absent.
