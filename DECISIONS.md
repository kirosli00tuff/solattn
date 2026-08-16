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
