# solattn

**An evaluation-only measurement of whether social attention velocity predicts
forward outcomes on an independently enumerated, birth-ordered Solana token
universe.**

**It does not trade. It does not suggest entries. It has no execution path in
any stage.** There is no wallet, no signer, no order, no venue connection, no
position, and no stage in which one is planned. The output is a measurement and
a documented verdict.

---

## Read this before anything else

**The prior evidence travels with this project.** It was measured elsewhere,
against bars registered before the measurements existed, and it is the reason
this project is shaped the way it is.

- **solclear measured 97.5% 30-day death on birth-ordered pools (n = 40)
  against 18.75% on attention-crawled ones (n = 16)** — a 60-point gap at 30
  days and a 79-point gap at 90 days, from the same chain over the same months,
  produced by nothing but which pages a crawler chose to archive.
  **Attention sampling manufactures survivorship.**
- **Peer-reviewed post-promotion return paths in this asset class are negative
  within days.** The direction this study proposes to look for is the direction
  the literature reports as already priced or worse.

**The registered prior that this finds a tradeable signal is 5 to 8 percent.**

**The product is the bias-controlled measurement either way, and a documented
negative is a valid and expected outcome.** Under the registered prior it is
the *modal* outcome. A negative closes the hypothesis; it does not motivate a
retune, a new statistic, or a second cohort.

---

## What is being measured

| | |
|---|---|
| **universe** | every new Solana AMM pool observed at birth from a keyless public new-pools feed, birth-ordered, **no attention input of any kind in the enumeration** |
| **expected rate** | ~1,330 AMM pools/day (solclear Stage B addendum, measured 2026-08-13), checked against the observed rate; a >2× disagreement is reported, never averaged |
| **attention metric** | mention counts, unique-author counts, and their velocity over trailing 1h / 6h / 24h windows from pool birth, per token, per source. **Mechanical only — no LLM judgment in Stage A** |
| **matching** | mint-address exact match (primary); cashtag and name (secondary). A cashtag matching more than one active mint is **ambiguous** and attributed to **nobody** |
| **horizons** | 1, 3, 7 days primary; 30 days secondary |
| **comparison** | top-attention-quintile forward return vs the birth-ordered cohort's own base rate, net of a registered 300–600 bps cost band, day-clustered bootstrap, 40 trials counted and deflated |
| **kill criteria** | no distinguishable lift over the base rate, **or** lift entirely inside the cost band — either closes the hypothesis |

The full specification is [`REGISTRATION.md`](REGISTRATION.md), committed
before any collector existed. Nothing in it may be revised to fit a result.

## The survivorship audit is a first-class output

**The death-rate gap between birth-ordered and attention-selected subsets is
reported alongside every result**, at every horizon, with its n. That gap is
itself a finding this project exists to measure forward, prospectively, on a
cohort whose enumeration is known to be unbiased — where solclear could only
measure it retrospectively against a web archive.

A gap of more than 15 percentage points means the headline rests on the
birth-ordered subset alone, and every attention-subset figure is reported
carrying that statement.

## Channel-selection bias, named plainly

**Which Telegram channels are watched shapes which attention is visible.** A
channel list assembled by browsing is an attention-selected instrument
measuring attention. There is no way to remove this bias; there is only fixing
the instrument before it is pointed at anything. The list is fixed at
registration by an objective rule — the top 20 public Solana/memecoin channels
by membership from a stated directory on a stated date — and **is never edited
mid-collection**. See [`docs/CHANNELS.md`](docs/CHANNELS.md).

## This is a separate hypothesis family from AiTrader's news-drift experiment

solattn's family is **attention and flow reflexivity**. AiTrader's is
**information incorporation**. They have different universes, different bars,
and different trial grids. **Neither project's outcome is evidence in the
other's family**, and no pooled inference across the two is permitted.

## Status

**Stage A — pre-registration, scaffold, measured access verification,
collectors live, clocks started.** No analysis has been run and none may run
before the registered maturity dates in `REGISTRATION.md` §8 and the ≥ 300
matured-pool condition in §4. See [`progress.md`](progress.md) for where the
project is right now and [`docs/ACCESS.md`](docs/ACCESS.md) for the measured
per-source access table.

## Usage

```bash
make install      # uv sync + pre-commit hooks
make verify       # measured access verification per source; writes docs/ACCESS.md
make watch        # birth-ordered universe watcher (immutable daily manifests)
make collect      # attention collectors for every source that verified
make checkpoint   # outcome candle fetch at horizon checkpoints
make counts       # daily sanity counts: messages, match rates, enumerated pools
make lint typecheck test
```

Every command is read-only with respect to the outside world: it retrieves
public data and writes local files. Nothing authenticates to a venue, and no
credential in this project has any capability beyond reading public data.

## Licence

MIT, with the not-financial-advice statement attached — see [`LICENSE`](LICENSE).
