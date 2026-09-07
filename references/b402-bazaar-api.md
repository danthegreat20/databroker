# B402 Bazaar API — Verified Reference

Verified live on 2026-09-06 by directly querying the endpoints below (not from documentation
alone). This file is the source of truth for field names/shapes — don't re-derive them from
memory or from the skill's own docstrings.

## Base URL

```
https://www.binance.com/bapi/ramp/v1/public/ramp/b402
```

Public, read-only, no authentication required.

## Endpoints

- `GET /bazaar/resources?limit=25&offset=0` — paginated full catalog
- `GET /bazaar/search?query=<text>` — keyword search. Per Binance's own changelog, it also
  accepts `network`, `asset`, `scheme`, `payTo`, and `maxUsdPrice` filters — `maxUsdPrice` is
  the one this project should lean on, since it lets the agent filter to affordable listings by
  USD price directly, sidestepping the raw-integer/decimals problem described below.
- `GET /bazaar/merchant?payTo=<address>` — one merchant's own listings

## Response envelope (confirmed live)

Every response wraps the real payload in Binance's standard BAPI shape:

```json
{"code": "000000", "message": null, "messageDetail": null, "data": { ... }, "success": true}
```

`/bazaar/resources` puts the catalog at `data.items[]` plus `data.pagination`.
`/bazaar/search` and `/bazaar/merchant` put it at `data.resources[]` (per Binance's docs — only
`/bazaar/resources`'s `items[]` key has been directly confirmed live by this project so far;
confirm `resources[]` the first time `/bazaar/search` is actually called, per Section 9.8).

## Resource item shape (confirmed live via `/bazaar/resources`)

```json
{
  "resource": "https://mpp.hyreagent.fun/bsc/trenches/new-tokens",
  "type": "http",
  "x402Version": 2,
  "description": "New token launches",
  "accepts": [{
    "scheme": "eip3009",
    "network": "eip155:56",
    "asset": "0x8d0d000ee44948fc98c9b98a4fa4921476f08b0d",
    "maxAmountRequired": "80000000000000000",
    "payTo": "0xb5998e11e666fd1e7f3b8e8d9122a755eec1e9b7"
  }],
  "lastUpdated": 1782217336219
}
```

`network: "eip155:56"` = BNB Smart Chain mainnet. There is no confirmed testnet equivalent for
this catalog — treat every listed resource as a real, real-money endpoint.

## ⚠️ Unresolved — do not assume, confirm before Session 3 sets spend limits

`maxAmountRequired` is a raw integer in the asset token's smallest unit. **The token's decimals
and identity are not yet confirmed** for either asset seen live:
- `0xcE24439F2D9C6a2289F741120FE202248B666666` (used by `api.xona-agent.com` listings)
- `0x8d0d000ee44948fc98c9b98a4fa4921476f08b0d` (used by `mpp.hyreagent.fun` listings — the
  provider this project's idea depends on)

Do not assume 18 decimals or any specific stablecoin. Confirm via BscScan or an ERC-20
`decimals()` call before converting `maxAmountRequired` into a USD figure for real spend-limit
logic. Until confirmed, `bazaar_client.py`'s `max_usd_price` filter (server-side, Binance's own
conversion) is the safe way to cap spend — don't hand-roll a decimals conversion in this
project's own code yet.

## Live snapshot at verification time (2026-09-06) — for context, not to hardcode against

27 resources listed, two providers:
- `api.xona-agent.com` — AI generation (image/audio/video/LLM calls), unrelated to this project's
  idea
- `mpp.hyreagent.fun` — crypto/DeFi data feeds: yield-migration advice, cross-chain swap quotes,
  Meteora LP pool lists/recommendations/strategy, top-performing-wallet data, new-token-launch
  feeds (`trenches/new-tokens`, `trenches/graduating`, `trenches/bags/new-tokens`) — this is the
  provider the data-shopper idea is built around

Listings change over time (Bazaar indexes new merchants ~30-60s after their first settle, and can
drop unhealthy ones) — re-query `/bazaar/resources` or `/bazaar/search` at build time rather than
trusting this snapshot.
