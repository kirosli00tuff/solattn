# CHANNELS.md — the fixed Telegram channel list

**STATUS: NOT YET FIXED (as of 2026-08-16). The Telegram collector is therefore
inactive, and no Telegram attention is being recorded.**

This is a deliberate outcome, not an oversight. ADR-007 fixes the list by an
objective rule *before* collection, and states plainly that **a provisional list
that gets "improved" later is worse than a late start** — an edited list is an
attention-selected instrument measuring attention, which is the exact
circularity this project exists to avoid.

## The registered rule (REGISTRATION.md 7, ADR-007)

- **the top 20 public Solana / memecoin Telegram channels by member count**,
- **from a single stated public directory**, named with its URL,
- **read on a single stated date**, recorded with the retrieval timestamp,
- ranked by the directory's own member-count field, ties broken by channel
  username ascending,
- excluding only channels the directory itself marks as non-public or
  non-English, with each exclusion recorded by name and reason.

**Once written below, the list is never edited mid-collection.** A channel that
goes quiet stays on the list with zero messages recorded — that is data, not a
gap to patch. Any change requires a dated amendment in REGISTRATION.md and
**starts a new cohort**.

## Why it is not fixed yet — the directories probed, measured 2026-08-16

Six public directories were probed for a machine-readable listing carrying both
a channel username and a member count. **None served one.**

| directory | URL | result (2026-08-16) |
|---|---|---|
| TGStat | `https://tgstat.com/en/ratings/channels/cryptocurrencies` | HTTP 404 |
| TGStat | `https://tgstat.com/en/cryptocurrency` | HTTP 404 |
| TGStat search | `https://tgstat.com/en/search?q=solana` | HTTP 200, 0 username+member pairs in the served HTML |
| Telemetr | `https://telemetr.io/en/channels/category/crypto` | DNS failure (name does not resolve) |
| telegramchannels.me | `https://telegramchannels.me/search?q=solana` | HTTP 200, 0 username+member pairs in the served HTML |
| Combot | `https://combot.org/top/telegram/groups?q=solana` | HTTP 200, 0 username+member pairs in the served HTML |
| Lyzem | `https://lyzem.com/search?q=solana&type=channel` | HTTP 200, 4 usernames, no member counts |

The pages that returned HTTP 200 render their rankings client-side or behind an
account, so no member-count field is available to rank by. Ranking by anything
else — search relevance, page order, apparent activity — would **not** be the
registered rule, and substituting a different rule silently is precisely what
REGISTRATION.md 9 lists as voiding the registration.

## What unblocks it

Either is sufficient, and both are operator actions:

1. **Name a directory** that publishes member counts (a TGStat account with API
   access, or any directory the operator prefers). The rule is then applied to
   it mechanically and the resolved list is written below with its URL and
   retrieval timestamp.
2. **Supply the twenty channels directly**, with the ranking source and date
   they came from, so the provenance is recorded even though the resolution was
   manual.

Note that Telegram is blocked on a **second, independent** operator action
regardless of this one: MTProto has no non-interactive user login, so an
authorized session must be created once via
`uv run python scripts/telegram_login.py`. The api_id/api_hash pair itself is
already verified as valid (see `docs/ACCESS.md`).

## The resolved list

*Empty. `solattn/attention/channels.py` parses the table below and returns an
empty list while it has no rows, which keeps the Telegram collector inactive by
construction rather than by remembering to switch it off.*

| rank | channel | members | note |
|---|---|---|---|

**Directory:** *(not yet fixed)*
**Read on:** *(not yet fixed)*
**Exclusions:** *(none recorded — no list resolved)*
