# Build Roadmap — Databroker (working title, rename freely)

Session 1 — Wallet & Skill Verification — install `binance-agentic-wallet`, sign in via MPC Wallet, run one real x402 payment against a known endpoint to confirm actual `baw` CLI behavior; lean repo skeleton (skill/system prompt + minimal static demo page, no Supabase/Next.js scaffold); initial SESSION_REPORT.md.
Session 2 — Data-Shopper Agent Logic — build the skill that takes a research question, queries B402 Bazaar (`/bazaar/search`) to find relevant paid feeds (starting with `hyreagent.fun`'s crypto/DeFi data), pays for the ones it selects via `baw x402`, and synthesizes an answer from the paid data.
Session 3 — Financial Safety Layer — hard spend/position limits enforced in code (not just declared), a full decision log per payment (timestamp, endpoint, amount, rationale, limit checked against), and exchange/API-failure handling that stops and flags rather than guessing.
Session 4 — Polish & Submission — record the demo video, write the GitHub README, clean up the repo, final check against Track A's submission requirements (video demo + GitHub repo).
