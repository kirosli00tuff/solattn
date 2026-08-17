"""registry.py — the registration, expressed as constants.

Every number here is fixed by REGISTRATION.md, which was committed before any
collector existed. ``tests/test_registration.py`` asserts these values against
the numbers written in that document, so the two cannot drift apart and a
mid-collection edit to a bar breaks the build.

Nothing in this module may be changed to fit a result. Changing a value here
requires a dated amendment in REGISTRATION.md and starts a new cohort.
"""

from __future__ import annotations

from typing import Final

SCHEMA_VERSION: Final = 1
REGISTERED_ON: Final = "2026-08-16"

# --- Registered prior (REGISTRATION.md 0) -----------------------------------
PRIOR_TRADEABLE_SIGNAL_LOW: Final = 0.05
PRIOR_TRADEABLE_SIGNAL_HIGH: Final = 0.08

# --- The universe rule (REGISTRATION.md 1) ----------------------------------
GECKOTERMINAL_BASE: Final = "https://api.geckoterminal.com/api/v2"
NEW_POOLS_PATH: Final = "/networks/solana/new_pools"
OHLCV_PATH_TEMPLATE: Final = "/networks/solana/pools/{pool}/ohlcv/day"
NETWORK: Final = "solana"

#: Launch venues (bonding curves). A DENYLIST, not an allowlist: an AMM that
#: appears mid-collection is included automatically, where an allowlist would
#: silently drop it and bias the cohort toward venues that existed on
#: registration day (ADR-002).
LAUNCHPAD_DEXES: Final[frozenset[str]] = frozenset(
    {
        "pumpfun",
        "pump-fun",
        "pumpdotfun",
        "launchlab",
        "moonshot",
        "moonit",
        "boop-fun",
        "believe",
        "bonkfun",
        "letsbonk-fun",
        "heaven-dex",
        "raydium-launchlab",
        "virtuals",
        "daos-fun",
        "sunpump",
        "four-meme",
    }
)

VENUE_CLASS_LAUNCHPAD: Final = "launchpad"
VENUE_CLASS_AMM: Final = "amm"
PRIMARY_VENUE_CLASS: Final = VENUE_CLASS_AMM

#: Measured by solclear's Stage B addendum on 2026-08-13, n = 122 unique pools.
EXPECTED_AMM_POOLS_PER_DAY: Final = 1330
EXPECTED_FULL_FEED_POOLS_PER_DAY: Final = 9000
EXPECTED_LAUNCHPAD_POOLS_PER_DAY: Final = 7450
#: A disagreement beyond this factor is REPORTED as a disagreement, never
#: averaged away, and never authorizes editing the denylist mid-collection.
RATE_DISAGREEMENT_FACTOR: Final = 2.0

# --- The attention metric (REGISTRATION.md 2) -------------------------------
ATTENTION_WINDOW_HOURS: Final = 24
ATTENTION_SUBWINDOW_HOURS: Final[tuple[int, ...]] = (1, 6, 24)
#: One mention per day - the smallest non-zero v24 the metric can produce.
ACCEL_FLOOR: Final = 1.0 / 24.0
STATISTICS: Final[tuple[str, ...]] = ("v24", "v1", "v6", "ua24", "accel")

QUINTILE_COUNT: Final = 5
TOP_QUINTILE: Final = 5
#: Above this share of zero-attention pools a birth day is flagged
#: ``degenerate_quintiles`` and the registered binary fallback is reported
#: alongside - never instead of - the quintile result.
DEGENERATE_ZERO_FRACTION: Final = 0.80

# --- The matching rules (REGISTRATION.md 3) ---------------------------------
ACTIVE_UNIVERSE_DAYS: Final = 30
BASE58_MIN_LEN: Final = 32
BASE58_MAX_LEN: Final = 44
CASHTAG_MIN_LEN: Final = 2
CASHTAG_MAX_LEN: Final = 10
#: A name shorter than this is not name-matchable: it produces noise.
MIN_NAME_MATCH_LEN: Final = 4

MATCH_MINT: Final = "matched_mint"
MATCH_CASHTAG: Final = "matched_cashtag"
MATCH_NAME: Final = "matched_name"
MATCH_AMBIGUOUS: Final = "ambiguous"
MATCH_UNMATCHED: Final = "unmatched"
MATCH_KINDS: Final[tuple[str, ...]] = (
    MATCH_MINT,
    MATCH_CASHTAG,
    MATCH_NAME,
    MATCH_AMBIGUOUS,
    MATCH_UNMATCHED,
)
MATCH_SET_PRIMARY: Final = "mint-exact"
MATCH_SET_SECONDARY: Final = "mint+cashtag"
MATCH_SETS: Final[tuple[str, ...]] = (MATCH_SET_PRIMARY, MATCH_SET_SECONDARY)

# --- Sources ----------------------------------------------------------------
SOURCE_TELEGRAM: Final = "telegram"
SOURCE_FARCASTER: Final = "farcaster"
SOURCE_BLUESKY: Final = "bluesky"
SOURCE_GECKOTERMINAL: Final = "geckoterminal"
SOURCE_BENCHMARK: Final = "benchmark"
ATTENTION_SOURCES: Final[tuple[str, ...]] = (
    SOURCE_TELEGRAM,
    SOURCE_FARCASTER,
    SOURCE_BLUESKY,
)

# --- Horizons, bars and returns (REGISTRATION.md 4) -------------------------
#: Entry is the close of the daily candle for d0 + ENTRY_OFFSET_DAYS, which
#: opens strictly after the attention window closes for every time-of-day of
#: T0 (ADR-006). No return bar overlaps the attention window.
ENTRY_OFFSET_DAYS: Final = 2
HORIZONS_PRIMARY: Final[tuple[int, ...]] = (1, 3, 7)
HORIZONS_SECONDARY: Final[tuple[int, ...]] = (30,)
HORIZONS: Final[tuple[int, ...]] = HORIZONS_PRIMARY + HORIZONS_SECONDARY

#: The death floor, ported from solclear ADR-013.
DEATH_LOOKBACK_DAYS: Final = 14
DEATH_DUST_FRACTION: Final = 0.01
DEATH_RETURN: Final = -1.0

#: The execution-cost band, ported from solclear ADR-014. Applied to a
#: hypothetical, to ask whether a measured lift would survive costs. Nothing in
#: this repository executes anything.
COST_BPS_CENTRAL: Final = 450
COST_BPS_LOW: Final = 300
COST_BPS_HIGH: Final = 600
COST_BANDS: Final[tuple[int, ...]] = (COST_BPS_LOW, COST_BPS_CENTRAL, COST_BPS_HIGH)

BOOTSTRAP_DRAWS: Final = 10_000

#: The attention SERIES dimension (REGISTRATION.md Amendment 2, 2026-08-17).
#: The primary metric is computed and reported PER SOURCE; ``pooled`` is a
#: registered secondary series, never primary. Telegram, Bluesky and Farcaster
#: emit structurally different constructs, so one pooled number would treat
#: three things as one.
SERIES_POOLED: Final = "pooled"
ATTENTION_SERIES: Final[tuple[str, ...]] = (
    SOURCE_BLUESKY,
    SOURCE_FARCASTER,
    SOURCE_TELEGRAM,
    SERIES_POOLED,
)

#: horizons (4) x statistics (5) x match sets (2) x series (4). MAY NOT GROW.
TRIAL_GRID_SIZE: Final = len(HORIZONS) * len(STATISTICS) * len(MATCH_SETS) * len(ATTENTION_SERIES)
#: (horizon, statistic, match set, series). Bluesky carries the primary trial on
#: the mechanical ground recorded in Amendment 2: it is the only series whose
#: metric aggregates many independent emitters (3,077 authors at 2.19 rows each)
#: rather than a handful. Designated before any outcome was observed.
PRIMARY_TRIAL: Final[tuple[int, str, str, str]] = (
    7,
    "v24",
    MATCH_SET_PRIMARY,
    SOURCE_BLUESKY,
)
ALPHA: Final = 0.05
SIDAK_ALPHA: Final = 1.0 - (1.0 - ALPHA) ** (1.0 / TRIAL_GRID_SIZE)

#: Kill criteria. Either firing closes the hypothesis.
KILL_LIFT_INSIDE_COST_BAND_BPS: Final = COST_BPS_HIGH
#: Below this many matured pools in the top quintile, no significance is
#: claimed in either direction; the direction is reported as underpowered.
UNDERPOWERED_MIN_N: Final = 20
#: No Stage B analysis runs before this many matured AMM pools exist at the
#: primary horizon.
MIN_MATURED_POOLS: Final = 300

# --- The survivorship audit (REGISTRATION.md 5) -----------------------------
#: solclear Stage E, 2026-08-14.
PRIOR_BIRTH_ORDERED_DEATH_30D: Final = 0.975
PRIOR_BIRTH_ORDERED_N: Final = 40
PRIOR_ATTENTION_CRAWLED_DEATH_30D: Final = 0.1875
PRIOR_ATTENTION_CRAWLED_N: Final = 16
#: A gap wider than this means the headline rests on the birth-ordered subset
#: alone, and every attention-subset figure carries that statement.
SURVIVORSHIP_GAP_POINTS: Final = 15.0

# --- Channels and capacity (REGISTRATION.md 7) ------------------------------
CHANNEL_LIST_SIZE: Final = 20

#: Measured, not documented: solclear recorded HTTP 429 at 2.5 s spacing
#: against a documented 30/min limit; 6 s held (ADR-003).
GECKOTERMINAL_MIN_SPACING_S: Final = 6.0
GECKOTERMINAL_DAILY_CAP: Final = 10_000
BLUESKY_DAILY_CAP: Final = 200
FARCASTER_DAILY_CAP: Final = 20_000
FARCASTER_MIN_SPACING_S: Final = 1.0

WATCH_SWEEP_SECONDS: Final = 120
WATCH_PAGES_PER_SWEEP: Final = 4
#: One call at T0 + 10 d covers the entry mark and the 1/3/7-day exits with
#: their 14-day death lookbacks; one at T0 + 33 d covers the 30-day exit.
CHECKPOINT_DAYS: Final[tuple[int, ...]] = (10, 33)
#: Above this measured AMM birth rate the watcher REPORTS saturation. It does
#: not silently sample and it does not silently drop.
SATURATION_AMM_PER_DAY: Final = 2400

# --- The registered ingest filter (REGISTRATION.md 7) -----------------------
#: Rules 1 and 2 of the filter are SHAPE filters (mint-shaped, cashtag-shaped)
#: and cannot privilege particular tokens. This keyword set is rule 3: small,
#: fixed, and never extended mid-collection. Short ambiguous strings ("sol",
#: "ca") are deliberately excluded - they collide with ordinary prose.
INGEST_KEYWORDS: Final[frozenset[str]] = frozenset(
    {
        "solana",
        "pumpfun",
        "pump.fun",
        "memecoin",
        "raydium",
        "meteora",
        "jupiter",
        "dexscreener",
        "birdeye",
        "contract address",
        "spl-token",
    }
)

#: The channel-resolution query set (REGISTRATION.md Amendment 1, 2026-08-16).
#: The registered §7 ingest vocabulary used VERBATIM as MTProto search queries,
#: in a fixed order so a re-read is reproducible. A term is never dropped for
#: looking unproductive - dropping one would be a judgment.
CHANNEL_QUERY_SET: Final[tuple[str, ...]] = (
    "solana",
    "pumpfun",
    "pump.fun",
    "memecoin",
    "raydium",
    "meteora",
    "jupiter",
    "dexscreener",
    "birdeye",
    "contract address",
    "spl-token",
)
#: The query set and the ingest vocabulary are the same set by construction;
#: tests/test_registration.py pins this so the two cannot drift apart.
CHANNEL_SEARCH_LIMIT: Final = 50

DAILY_CAPS: Final[dict[str, int]] = {
    SOURCE_GECKOTERMINAL: GECKOTERMINAL_DAILY_CAP,
    SOURCE_BLUESKY: BLUESKY_DAILY_CAP,
    SOURCE_FARCASTER: FARCASTER_DAILY_CAP,
    SOURCE_TELEGRAM: 50_000,
    SOURCE_BENCHMARK: 200,
}

MIN_SPACING_S: Final[dict[str, float]] = {
    SOURCE_GECKOTERMINAL: GECKOTERMINAL_MIN_SPACING_S,
    SOURCE_FARCASTER: FARCASTER_MIN_SPACING_S,
    SOURCE_BLUESKY: 1.0,
    SOURCE_BENCHMARK: 2.0,
}
