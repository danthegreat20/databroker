# Data Shopper

Built for the **Binance Agent OS Mini Hackathon** — Track A (build an AI agent with Agent OS),
Payment Workflows (x402) theme.

An agent that answers a research question by autonomously discovering and paying for relevant
x402-gated data feeds on Binance's B402 Bazaar, then synthesizing the paid results into an
answer — with hard spend limits and a full decision log for every payment it considers.

See `RESEARCH_BRIEF.md` for how this idea was scoped and verified, and `SKILL.md` for exactly
how the agent behaves.

## Architecture (Agent-skill pattern)

This is **not** a hosted app. The agent is a Claude Skill (`SKILL.md`) that runs inside an
MCP-connected client (Claude Code, Claude Desktop, etc.) that already has the
`binance-agentic-wallet` skill installed and signed in. `demo/index.html` is a thin static page
for the demo video — it is not what drives the agent.

```
databroker/
├── SKILL.md                    the agent's actual behavior
├── scripts/bazaar_client.py    verified read-only Bazaar discovery client
├── references/b402-bazaar-api.md   verified API shape + open questions
├── demo/index.html             renders decision_log.json as a ledger, for the demo
├── .env.example                spend-limit configuration (names only)
├── RESEARCH_BRIEF.md           Session 0 output
├── BUILD_ROADMAP.md            Session 0 output
└── SESSION_REPORT.md           anti-hallucination anchor for the next session
```

## Setup (manual, human steps — do these before Session 2)

1. Install Node.js 18+ if you don't have it.
2. In the Binance App, create an **MPC Wallet** (this is separate from any Agentic sub-account
   you may have set up for trading).
3. Install the wallet skill:
   ```
   npx skills add binance/binance-skills-hub/skills/binance-web3/binance-agentic-wallet
   ```
4. Sign in via the `baw` CLI's QR code / app deep-link flow.
5. Run `baw --help` and `baw x402 --help` and compare the real output against the placeholder
   command in `SKILL.md` step 4 — update that file with the real syntax before Session 2 writes
   any logic on top of it.
6. Copy `.env.example` to `.env` and set `PER_CALL_LIMIT_USD` / `SESSION_LIMIT_USD` — small
   numbers on purpose; these are real funds on BNB Chain mainnet, not a testnet.
7. Sanity-check discovery works before touching payments:
   ```
   python scripts/bazaar_client.py search --query "new tokens" --max-usd-price 0.05
   ```

## Status

Session 1 of 4 complete — see `SESSION_REPORT.md` for exactly what's built, what's verified, and
what's still open before Session 2 (the actual research-question loop) can safely begin.
