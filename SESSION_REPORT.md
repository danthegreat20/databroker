## Session 1: Wallet & Skill Verification (repo scaffold + skill definition)
**Date:** 2026-09-05
**Goal:** Scaffold the Agent-skill-pattern repo and write the data-shopper skill's workflow,
against a verified (not assumed) B402 Bazaar API — leaving the actual research-question loop for
Session 2.

**Files added/changed:**
- `SKILL.md` — the agent's behavior: discover → check spend caps → pay → fetch → log → synthesize
- `scripts/bazaar_client.py` — read-only client for the Bazaar discovery API, matching the
  verified live response shape
- `references/b402-bazaar-api.md` — verified API reference, including what's still unconfirmed
- `.env.example` — `PER_CALL_LIMIT_USD`, `SESSION_LIMIT_USD`, `BAW_WALLET_ADDRESS` (names only)
- `demo/index.html` — static ledger view of `decision_log.json`, falls back to clearly-labeled
  sample data if no real log exists yet
- `README.md` — setup steps, including the manual ones this session couldn't perform
- `RESEARCH_BRIEF.md`, `BUILD_ROADMAP.md` — carried over from Session 0, included in this zip for
  completeness

**Current full file tree:**
```
.
├── .env.example
├── README.md
├── SKILL.md
├── demo/
│   └── index.html
├── references/
│   └── b402-bazaar-api.md
└── scripts/
    └── bazaar_client.py
```
(`RESEARCH_BRIEF.md` and `BUILD_ROADMAP.md` ship alongside this tree but were Session 0 output,
not created this session.)

**Dependencies installed:**
- None. `bazaar_client.py` uses only the Python standard library (`urllib`, `json`, `argparse`)
  deliberately, so discovery works with zero install step. `binance-agentic-wallet` (the `baw`
  CLI) is installed separately by the user per the README — not a dependency of this repo's own
  code.

**Supabase schema state:** N/A — this project uses the Agent-skill pattern (Section 2), no
database.

**Env vars required:**
- PER_CALL_LIMIT_USD
- SESSION_LIMIT_USD
- BAW_WALLET_ADDRESS

**Agent OS mode:** N/A in the Section 9.2 testnet/mainnet sense — this project doesn't use the
Agentic-sub-account trading MCP server at all. It uses the separate `binance-agentic-wallet`
skill, which operates on **BNB Chain mainnet** with no confirmed testnet equivalent. Treat every
real call as live/mainnet from the first one (see "Known stubs/TODOs" below).

**Sub-account scope & limits:** Not applicable in the Section 9.3 sense (no Binance sub-account
involved). The equivalent control for this project is the MPC Wallet's own funding level (fund it
with only what you're willing to spend on the demo) plus the code-enforced `PER_CALL_LIMIT_USD` /
`SESSION_LIMIT_USD` caps declared above — enforcement of those caps is written into `SKILL.md`'s
workflow (step 3) but has not yet been exercised against a real payment.

**Decision log (this session):** None. No live or testnet payment was made this session — this
was a scaffolding session only, per the Pre-Flight/Kickoff brief.

**API endpoints live:**
- `GET https://www.binance.com/bapi/ramp/v1/public/ramp/b402/bazaar/resources` — verified live,
  public, no auth
- `GET https://www.binance.com/bapi/ramp/v1/public/ramp/b402/bazaar/search` — documented, **not
  yet directly verified live by this project** (see Known stubs/TODOs)

**Known stubs/TODOs:**
- `SKILL.md` step 4's `baw x402 pay` command is a **placeholder**, explicitly marked unverified.
  Must be confirmed against the real installed CLI before Session 2.
- `bazaar_client.py`'s `search()` assumes the `data.resources[]` response key per Binance's docs;
  only `data.items[]` (from `/bazaar/resources`) has been confirmed live so far.
- The token identity/decimals behind `maxAmountRequired` for both assets seen live
  (`0xcE24439F...B666666` and `0x8d0d0...08b0d`) are unconfirmed — spend-limit enforcement
  currently relies on the Bazaar's own server-side `maxUsdPrice` filter to avoid needing this,
  which works for discovery but not yet for post-hoc USD accounting in the decision log.
- `demo/index.html` renders clearly-labeled sample data until a real `decision_log.json` exists
  — this is intentional, not a bug, per Section 9.6 (never silently fake data).

**Assumptions carried into next session:**
- The user has completed the manual setup in `README.md` (MPC Wallet created, `binance-agentic-
  wallet` installed and signed in) before Session 2 starts — Session 2 should re-confirm this
  rather than assume it, per the Pre-Flight Checklist.
- `SKILL.md`'s placeholder payment command has been replaced with the real, verified `baw`
  syntax — if not, Session 2's first job is that verification, not new agent logic.
- B402 Bazaar's live catalog may have changed since 2026-09-05 (new merchants can appear, unhealthy
  ones can be dropped) — re-query rather than trusting the snapshot in the reference doc.
- No mainnet/live spend has occurred yet under this project. The very first real `baw x402`
  payment should be treated as a deliberate, tiny "canary" transaction, not assumed safe just
  because the per-call limit is small.

**Style history:** N/A — no UI-design session has run yet; `demo/index.html` is a functional
ledger view, not a designed product surface, and doesn't carry a style-history entry under
Section 8.2.
