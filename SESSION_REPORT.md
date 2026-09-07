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

---

## Session 2: Data-Shopper Agent Logic (orchestration code + offline verification)
**Date:** 2026-09-05
**Goal:** Turn `SKILL.md`'s prose workflow into real, runnable orchestration code, with spend-limit
enforcement and decision logging exercised in code — while keeping the one unverified piece (the
live `baw` payment call) isolated and unimplemented rather than guessed.

**Assumed true from Session 1 before building (per Section 6 rule 1):** `bazaar_client.py`'s
`search()`/`list_resources()` functions and response parsing exist and were verified live; the
`data.items[]` shape is confirmed, `data.resources[]` (used by `/bazaar/search`) is documented but
still not directly confirmed live; no `baw` CLI syntax has been confirmed. This session did not
re-verify any of that against the network — see "Known stubs/TODOs" for what's still open.

**Files added/changed:**
- `scripts/data_shopper.py` — `SpendTracker` (Section 9.4, enforced in code), `_log_decision`
  (Section 9.5 shape, matches what `demo/index.html` reads), `_pay_via_baw` (the isolated,
  deliberately unimplemented payment call — raises `NotImplementedError` unless `--dry-run`), and
  `shop_for_data` tying them together into one pass over search results
- `scripts/test_data_shopper.py` — offline smoke test; monkeypatches `search()` with a fixture
  built from the real listings verified live in Session 1 (no network call in this test)
- `.gitignore` — added (`__pycache__/`, `*.pyc`, `.env`, `decision_log.json`)

**Current full file tree:**
```
.
├── .env.example
├── .gitignore
├── BUILD_ROADMAP.md
├── README.md
├── RESEARCH_BRIEF.md
├── SESSION_REPORT.md
├── SKILL.md
├── demo/
│   └── index.html
├── references/
│   └── b402-bazaar-api.md
└── scripts/
    ├── bazaar_client.py
    ├── data_shopper.py
    └── test_data_shopper.py
```

**Dependencies installed:** None — still Python standard library only (`argparse`, `json`,
`pathlib`, `datetime`).

**Env vars required:** unchanged from Session 1 (`PER_CALL_LIMIT_USD`, `SESSION_LIMIT_USD`,
`BAW_WALLET_ADDRESS`).

**Agent OS mode:** unchanged from Session 1 — no live/mainnet call has occurred under this
project yet. `data_shopper.py`'s CLI refuses to run without `--dry-run` while `_pay_via_baw` is
unimplemented, specifically to prevent an accidental live call.

**Sub-account scope & limits:** unchanged from Session 1. `SpendTracker` now enforces
`PER_CALL_LIMIT_USD` / `SESSION_LIMIT_USD` **in code** (verified by
`test_spend_tracker_allows_then_blocks`, which confirms a third call is blocked once two calls at
the per-call limit reach the session cap) — this satisfies Section 9.4's "enforced in code, not
just declared," though only against a fixture, not a live run yet.

**Decision log (this session):** No live or testnet payment action occurred. The offline test run
logged 3 fixture decisions (2 `paid`/dry-run, 1 `skipped_over_limit`) to a temp file for
verification purposes only — not a real decision log, and not committed to the repo.

**API endpoints live:** unchanged from Session 1. Note: this session did **not** re-hit the live
Bazaar — `search()` was monkeypatched for the test, so `/bazaar/search`'s real response shape is
still unconfirmed (see Known stubs/TODOs, carried over).

**Known stubs/TODOs:**
- `_pay_via_baw` in `scripts/data_shopper.py` is the same unverified placeholder as `SKILL.md`
  step 4 — now isolated into one function so implementing it later is a one-function change.
- `/bazaar/search`'s live response key (`data.resources[]` vs `data.items[]`) is still unconfirmed
  — carried over from Session 1, not addressed this session.
- Token decimals for USD accounting — carried over from Session 1, still unresolved.
- `data_shopper.py` has not been run against the live network in this sandbox (no network access
  here); only the offline, fixture-based path has been exercised.

**Assumptions carried into next session:**
- Everything carried from Session 1 (manual wallet setup, `baw` syntax confirmation) still
  applies — none of it has been resolved by this session's work.
- The first real (non-dry-run) invocation of `data_shopper.py` should be treated as the "canary"
  transaction mentioned in Session 1's report, on a machine with real network access and a signed-
  in `baw` CLI — not in this sandbox.
- Once `_pay_via_baw` is implemented for real, re-run `test_data_shopper.py` first (it doesn't
  touch that function's live path) as a fast sanity check, then do one manual `--dry-run` pass
  against the live Bazaar (real search, simulated payment) before removing `--dry-run` entirely.

**Style history:** unchanged — N/A.
