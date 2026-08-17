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
