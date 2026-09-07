# Data Shopper

Built for the **Binance Agent OS Mini Hackathon** — Track A (build an AI agent with Agent OS),
Payment Workflows (x402) theme.

An agent that answers a research question by autonomously discovering and paying for relevant
x402-gated data feeds on Binance's B402 Bazaar, then synthesizing the paid results into an
answer — with hard spend limits and a full decision log for every payment it considers, enforced
in code, not just documented.

See `RESEARCH_BRIEF.md` for how this idea was scoped and verified, `SKILL.md` for exactly how the
agent behaves, and `VIDEO_SCRIPT.md` for the demo recording plan.

## Architecture (Agent-skill pattern)

This is **not** a hosted app. The agent is a Claude Skill (`SKILL.md`) that runs inside an
MCP-connected client (Claude Code, Claude Desktop, etc.) that already has the
`binance-agentic-wallet` skill installed and signed in. `demo/index.html` is a thin static page
for the demo video — it is not what drives the agent.

```
databroker/
├── SKILL.md                    the agent's actual behavior
├── scripts/
│   ├── bazaar_client.py        verified read-only Bazaar discovery client
│   ├── data_shopper.py         orchestration: discover → limit-check → pay → log → synthesize
│   └── test_data_shopper.py    offline smoke tests (no network/wallet needed)
├── references/b402-bazaar-api.md   verified API shape + open questions
├── demo/index.html             renders decision_log.json as a ledger, for the demo
├── .env.example                spend-limit configuration (names only)
├── VIDEO_SCRIPT.md             demo recording plan for the Track A submission
├── LICENSE                     MIT
├── RESEARCH_BRIEF.md           Session 0 output
├── BUILD_ROADMAP.md            Session 0 output
└── SESSION_REPORT.md           anti-hallucination anchor, cumulative across all sessions
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

## Running the tests

No install needed — standard library only:
```
python3 scripts/test_data_shopper.py
```
5 offline tests, fixture-based, no network or wallet required. All pass as of Session 3.

## Pre-submission checklist

- [x] Entry mechanics done (followed, reposted, submission reply, survey)
- [ ] `_pay_via_baw` implemented with verified `baw` syntax, OR video clearly labels dry-run mode
- [ ] `python3 scripts/test_data_shopper.py` passes on the machine you're recording from
- [ ] Real (or clearly-labeled dry-run) `decision_log.json` exists and `demo/index.html` renders it
- [ ] Video recorded per `VIDEO_SCRIPT.md`, under ~3 minutes
- [ ] GitHub repo public, README readable top-to-bottom without this project's internal session
      history being confusing to an outside reader (SESSION_REPORT.md can stay — it's a legible
      build log — but make sure README stands on its own)
- [ ] Submission posted before September 8, 2026, 23:59 UTC

## Status

Session 3 of 4 complete — see `SESSION_REPORT.md` for exactly what's built, what's verified, and
what's still open. Session 4 is video + final polish once the wallet step above is done.
