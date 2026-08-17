# CHANNELS.md — the fixed Telegram channel list

**STATUS: RESOLVED AND FIXED, 2026-08-17T04:25:27Z.**

This list is now **frozen for this cohort**. It is never edited mid-collection.
A channel that goes quiet, is renamed, or is deleted stays on the list with that
status recorded — that is data, not a gap to patch. Re-running the resolver
would produce a different list and is **not permitted** for this cohort
(REGISTRATION.md Amendment 1, step 9).

## Method

**Telegram's own MTProto search**, per REGISTRATION.md **Amendment 1
(2026-08-16)**. No human or model judgment selected any channel; every step is
mechanical and reproducible from the query set and the timestamp recorded here.

| | |
|---|---|
| source | Telegram MTProto `contacts.search`, then `channels.getFullChannel` |
| query set | the registered §7 ingest vocabulary, **verbatim**, in fixed order |
| search limit | 50 per query |
| ranking field | Telegram's own **`participants_count`** (first-party), descending |
| tie-break | channel username ascending (§7's own tie-break) |
| cutoff | top 20 |
| language filter | **none applied** — Telegram exposes no language field, and substituting one would be judgment |
| read at | **2026-08-17T04:25:27Z** |

**Query set, verbatim:** `solana`, `pumpfun`, `pump.fun`, `memecoin`, `raydium`, `meteora`, `jupiter`, `dexscreener`, `birdeye`, `contract address`, `spl-token`

**Hits per query:** `birdeye` 6 · `contract address` 1 · `dexscreener` 3 · `jupiter` 1 · `memecoin` 4 · `meteora` 1 · `pump.fun` 1 · `pumpfun` 3 · `raydium` 6 · `solana` 1 · `spl-token` 0

**Exclusions, counted:** not-a-public-broadcast-channel **35** ·
no username, therefore not public **6** ·
no registered keyword in title+username **12**.
Unique eligible candidates after union and dedupe: **27**;
`participants_count` successfully read for **27**.

## The resolved list

| rank | channel | participants_count | title / matched keywords |
|---|---|---|---|
| 1 | @memecoinx | 30,278 | Memecoin Gems Shilling 🚀 — matched `memecoin` |
| 2 | @Raydiumx | 22,829 | RAYDIUM OFFICIAL ❇️ — matched `raydium` |
| 3 | @myroSOL | 16,389 | $MYRO | The Solana Founders Dog — matched `solana` |
| 4 | @MemeCoinIntelligence | 7,480 | MemeCoin Intelligence — matched `memecoin` |
| 5 | @juicecoinnft | 7,170 | $JUICE | SOL MEMECOIN — matched `memecoin` |
| 6 | @raydium | 4,274 | Raydium Official Announcements — matched `raydium` |
| 7 | @birdeye_trendings | 3,454 | BIRDEYE TRENDING — matched `birdeye` |
| 8 | @Raydiump | 3,143 | Raydium Protocol SUPPORT ❇️ — matched `raydium` |
| 9 | @birdeye_official | 2,648 | Birdeye.so Official Community — matched `birdeye` |
| 10 | @PumpLivePool | 2,287 | PumpFun Live Pool — matched `pumpfun` |
| 11 | @pumpfun_migration | 2,203 | PumpFun Migration Calls — matched `pumpfun` |
| 12 | @memecoin_signals | 1,868 | SOLANA FOMO Calls — matched `solana` |
| 13 | @BirdeyeTrendingCI | 1,138 | Birdeye Trending - By CryptoInsider — matched `birdeye` |
| 14 | @birdeyeso_official | 1,108 | Birdeye.so Official Community — matched `birdeye` |
| 15 | @fasol_vol | 573 | Raydium Volume Alerts — matched `raydium` |
| 16 | @meteoraecosystem | 564 | Meteora Ecosystem — matched `meteora` |
| 17 | @pumpfuntrackertg | 438 | Pump.fun Tracker ⚡️ — matched `pump.fun` |
| 18 | @birdeyecase | 420 | BIRDEYE КЕЙСЫ/ОТЗЫВЫ — matched `birdeye` |
| 19 | @boosterdex | 403 | Boost Dexscreener — matched `dexscreener` |
| 20 | @dexscreenerupdatealerts | 385 | Dexscreener Update Alerts | By Willi — matched `dexscreener` |

## Read this before using these figures

**The absolute sizes are small, and that is a property of the instrument, not a
defect to correct.** The largest channel here has 30,278 members and the
smallest 385. This is *not* "the twenty largest Solana channels on
Telegram" in any absolute sense — it is the top twenty by `participants_count`
**among what `contacts.search` returned for the registered query set**.
Telegram's search favours close title and username matches over raw size, so the
instrument surfaces niche, on-topic channels (trackers, shill and signal
channels) rather than large general-crypto audiences. For an attention study
that is arguably closer to the target than a general ranking would be — the
TGStat crypto ranking rejected in Amendment 1 was TON tap-games and exchange
feeds at millions of members, with zero Solana channels — but the reading of any
result must carry this: **this measures visible attention on a small, on-topic,
mechanically-selected instrument.**

**The residual bias, restated.** Amendment 1 relocated channel-selection bias
from "what a directory chose to list" to "what Telegram's search ranks for these
eleven terms". It did not remove it. What is preserved is the property §7 exists
to protect: the instrument was **fixed in advance, is mechanically reproducible
from the recorded query set and timestamp, and cannot be adjusted once results
are visible.**

Raw resolution output, including every candidate considered and its count, is
kept machine-locally at `data/state/channel_resolution_raw.json` (gitignored
with the rest of `data/`).
