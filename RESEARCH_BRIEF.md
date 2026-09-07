# Research Brief — Session 0

**Hackathon:** Binance Agent OS Mini Hackathon — Track A (build an AI agent with Agent OS)
**Prize:** $20,000 USDC of a $60,000 total pool (Track B, $40,000, is separate — "connect MCPs and trade live")
**Deadline:** September 8, 2026, 23:59 UTC
**Entry status:** Done (followed @Binance, reposted, replied with submission, completed survey)
**Eligibility flag:** Not open to participants in the US, UK, EEA, Hong Kong, Singapore, or other Binance-restricted jurisdictions — confirm this doesn't apply before investing further build time.

## Idea Lock

- **Theme:** Payment Workflows (x402)
- **Idea direction:** "Autonomous data-shopper" — of three directions considered, the other two (spend-guarded invoice agent, agent-to-agent x402 commerce demo) were deprioritized for time/risk given the ~3-day runway.
- **One-line pitch:** An AI research agent that autonomously discovers, evaluates, and pays x402-gated data feeds through Binance's agentic wallet to answer a research question end-to-end — with hard spend limits and a full payment decision log.

## Agent OS Feasibility Check (Section 3 / 9.8 requirement)

- The headline hackathon MCP endpoint (`agent.binance.com/mcp/agentic`, OAuth-consent, Agentic sub-account) exposes exactly four scopes: market data, account, trade, transfer. **No x402 tool lives on this server.**
- x402 is reached through a separate product: the **Binance Skills Hub**, specifically the `binance-agentic-wallet` skill (drives a `baw` CLI). That skill bundles wallet transfers, DEX market/limit orders, prediction-market trading, DeFi ops, *and* x402 payments — x402 is one capability among several, not a dedicated payments-only tool.
- Setup differs from the trading MCP server: requires a Binance account with an **MPC Wallet created in the Binance App** (separate from an Agentic sub-account), install via `npx skills add binance/binance-skills-hub/skills/binance-web3/binance-agentic-wallet`, then sign-in via QR code / app deep link — not the browser OAuth flow.
- Binance x402 is branded **B402** in its own docs — Binance's implementation of the x402 protocol on BNB Smart Chain. It has a public, no-auth discovery API (**B402 Bazaar**, `/bazaar/resources` and `/bazaar/search`) that any agent (or plain HTTP client) can query directly.
- **Verified live** (queried `/bazaar/resources` directly, Sept 5 2026): **27 real endpoints are listed today**, all settling on BSC (`eip155:56`). Two providers dominate: `api.xona-agent.com` (AI generation — image/audio/video/LLM calls, e.g. GPT-5.2, Claude Opus 4.6, Gemini 3.5 Flash) and, more relevantly for this idea, `mpp.hyreagent.fun` (crypto/DeFi *data* feeds: yield-migration advice, cross-chain swap quotes, Meteora LP pool lists/recommendations, top-performing-wallet data, new-token-launch feeds). **The hyreagent.fun feeds are close to ideal raw material for the data-shopper agent** — real, live, paid, research-shaped data, no need to stand up a fallback endpoint.
- `/bazaar/search?query=...` supports keyword/price/network filtering for more targeted discovery once building starts.
- **Still unverified, flagged for direct doc-check before relying on it:** a secondary (non-Binance) source cited daily caps of $50k on regular swaps, $100k on DeFi transactions, $20 on x402 payments — and the exact token behind the `hyreagent.fun` pricing (asset `0x8d0d...08b0d`) needs its decimals/identity confirmed to compute real USD costs before setting spend limits.

## Prior Art

- At least one entrant is already building a Trading-track MCP demo (dry-run mode, slippage guardrails, "institutional resilience" framing) — would have been direct competition on the Trading angle.
- No competing entry found yet on the x402/agentic-wallet angle specifically — currently less contested ground on originality.

## Judging Criteria

Not located in a form specific enough to plan against — recommend pulling the exact rubric from the official Binance blog/X announcement before finalizing where build effort goes.

## Technical Shape (deviates from ruleset Section 2 default — declared per Section 2)

**Agent-skill pattern**, not full-stack: the deliverable is a skill/system prompt running inside an MCP-connected client, using `binance-agentic-wallet`'s x402 capability directly. No Next.js / Supabase / deploy pipeline. `apps/web`, if present at all, is a thin static page for demo narration only — not the thing driving the agent.
**Reason:** Track A is judged on a video demo + GitHub repo, not a hosted product, and the ~3-day runway doesn't support the full monorepo scaffold in Section 2's Standard Stack.

## Open Items Before Session 1

- [x] Confirm real BNB-Chain x402 data/API endpoints exist and are reachable — **done**: 27 live listings confirmed via `/bazaar/resources`, `hyreagent.fun`'s crypto/DeFi feeds fit this idea directly
- [ ] Confirm exact `baw` x402 subcommand syntax against the live skill (Section 6 rule 9 — verify once on first use, then trust it)
- [ ] Identify the token behind `hyreagent.fun`'s pricing (asset `0x8d0d...08b0d` on BSC) and its decimals, to convert `maxAmountRequired` into real USD costs before setting Section 9.4 spend limits
- [ ] Confirm daily x402 spend caps directly against Binance's own docs before relying on the $50k/$100k/$20 figures from a secondary source
- [ ] Re-check `/bazaar/resources` close to build time — listings are live and can change (new ones appear ~30-60s after a merchant's first settle; unhealthy ones get demoted)
