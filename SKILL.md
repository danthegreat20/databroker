---
name: data-shopper
description: >
  Autonomously answers a research question by discovering and paying for
  relevant x402-gated data feeds on Binance's B402 Bazaar, then synthesizing
  the paid results into an answer. Use this whenever the user asks a
  research question that crypto/DeFi data feeds could help answer (yield
  opportunities, LP pool strategy, top-performing wallets, new token
  launches, cross-chain swap quotes), or explicitly asks the agent to "shop
  for data" or "pay for research." Requires the binance-agentic-wallet skill
  to already be installed and signed in — this skill does not handle wallet
  setup itself.
---

# Data Shopper

An agent that treats paid data feeds like a research assistant with a
company card: given a question, it goes shopping for the data that answers
it, spends real (small) amounts of crypto to buy it, and shows its work.

**Built for:** Binance Agent OS Mini Hackathon, Track A, Payment Workflows
(x402) theme. See `../RESEARCH_BRIEF.md` and `../BUILD_ROADMAP.md` for the
project context this skill was scoped against.

## ⚠️ Verification status — read before relying on this skill

This skill was scaffolded in a sandboxed session with no live Binance
account or network access. Two things in the workflow below are
**documented but not yet live-verified** (Section 9.8 of the build
ruleset — new tools are verified once, on first real use, before logic gets
built on top of them):

1. **The exact `baw` CLI subcommand for making an x402 payment.** The
   workflow below uses a placeholder: `baw x402 pay <url> --max-usd <cap>`.
   Before Session 2, run `baw --help` and `baw x402 --help` against the real
   installed CLI and update Step 3 below with the actual command and output
   shape.
2. **`/bazaar/search`'s response key.** `bazaar_client.py`'s `search()`
   function assumes `data.resources[]` per Binance's docs, but only
   `/bazaar/resources`'s `data.items[]` shape has actually been confirmed
   live so far. Confirm on first real call.

Do not skip this section to save time — a hallucinated CLI command here is
exactly the failure mode Section 9 of the build ruleset exists to prevent,
because the mistake fires a real payment.

## Prerequisites (manual, human, one-time — see project README)

- A Binance account with an MPC Wallet created in the Binance App
- The `binance-agentic-wallet` skill installed and signed in (`baw` CLI
  working)
- `PER_CALL_LIMIT_USD` and `SESSION_LIMIT_USD` set in `.env` (see
  `.env.example`) — these are hard caps, not suggestions

## Workflow

1. **Take the research question** from the user, e.g. "what's the best BSC
   LP pool to be in right now?"

2. **Discover candidates.** Call `scripts/bazaar_client.py search` with a
   keyword drawn from the question, and pass `--max-usd-price
   PER_CALL_LIMIT_USD` so the Bazaar's own USD conversion filters out
   anything over the per-call cap server-side — this avoids needing to
   decode `maxAmountRequired`'s raw token units locally (see the bazaar API
   reference doc for why that's still unresolved). Prefer `mpp.hyreagent.fun`
   listings for crypto/DeFi questions; they're the closest fit for this
   project's idea.

3. **Check the running session total** against `SESSION_LIMIT_USD` before
   paying for anything. If a candidate would push the session over its cap,
   skip it and log the skip with a reason — never pay past the cap to
   "just get one more data point."

4. **Pay and fetch.** For each selected endpoint, call it, receive the
   HTTP 402 response, and hand the payment requirements to `baw` to sign and
   settle:
   ```
   baw x402 pay <resource-url> --max-usd <PER_CALL_LIMIT_USD>   # ⚠️ unverified syntax, see above
   ```
   Retry the original request with the signed payment attached to get the
   real, paid response body.

5. **Log the decision — every attempt, paid or skipped.** Append one entry
   per attempt to `decision_log.json` (read by `demo/index.html`):
   ```json
   {
     "timestamp": "2026-09-06T14:03:00Z",
     "resource": "https://mpp.hyreagent.fun/bsc/trenches/new-tokens",
     "description": "New token launches",
     "action": "paid",
     "amount_usd": 0.02,
     "rationale": "Question asked about new launches; this is the closest live feed.",
     "limit_checked_against": "PER_CALL_LIMIT_USD=0.05, session_total=0.04/0.50"
   }
   ```
   `action` is one of `paid`, `skipped_over_limit`, or `failed`.

6. **Failures are blockers, not retries.** If a merchant endpoint errors,
   times out, or returns something unexpected, log it as `failed`, stop
   pursuing that endpoint, and say so plainly in the final answer — never
   fabricate data to fill the gap (Section 9.6).

7. **Synthesize the answer.** Combine the paid responses into a direct
   answer to the research question, and disclose what was paid for and how
   much as part of the answer — this is the whole point of the demo: the
   spend is a visible, auditable part of the agent's reasoning, not a hidden
   side effect.

## Files this skill depends on

- `scripts/bazaar_client.py` — verified Bazaar discovery client (read-only)
- `references/b402-bazaar-api.md` — verified API shape + open questions
- `.env.example` — spend-limit configuration
- `decision_log.json` — created at runtime by this skill, not checked in
  pre-filled
