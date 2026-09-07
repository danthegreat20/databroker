# Demo Video Script — Data Shopper

Track A requires a video demo + GitHub repo. Aim for 2-3 minutes — judges are watching many of
these. Every beat below maps to something a judge is explicitly scoring: working product,
technical execution, and the financial-safety story that's this project's actual differentiator.

**Before recording:** decide whether `_pay_via_baw` is implemented for real yet.
- **If yes:** record a real payment. A genuine on-chain settlement is far more convincing than a
  simulation — do this if there's any time left to get it working.
- **If no:** record with `--dry-run` and say so on camera in one sentence ("this run is in dry-run
  mode — no funds move — because I'm still validating the wallet CLI's exact syntax"). Don't
  hide it; judges respect an honest caveat far more than a run that looks real but isn't labeled.

## Scene 1 — The problem (0:00–0:20)

Say, on camera or as voiceover: research agents that need live data are stuck choosing between
free APIs (rate-limited, often stale) and manual subscriptions (can't be automated). x402 lets an
agent pay per-request for exactly the data it needs, no subscription. Show the B402 Bazaar
listings briefly (`python scripts/bazaar_client.py list` or the live URL) to prove these are real,
live, paid endpoints — not a toy.

## Scene 2 — The safety story, before the demo runs (0:20–0:50)

This is the part that differentiates the project — lead with it, don't bury it at the end.
Show `.env.example` and `SKILL.md`'s workflow section. Say: every payment this agent makes is
capped per-call and per-session **in code**, not just documented — show `SpendTracker` briefly.
Every decision, paid or skipped, gets logged with a timestamp and a reason. If something breaks
twice in a row, the agent stops instead of retrying blind.

## Scene 3 — Live run (0:50–1:50)

Run the agent against a real research question, e.g.:
```
python scripts/data_shopper.py --keyword "new tokens" --dry-run
```
(drop `--dry-run` if the wallet step is done). Narrate what's happening as it runs: it's
searching the Bazaar, filtering to what fits the spend cap, paying (or skipping) each candidate.

## Scene 4 — The ledger (1:50–2:20)

Open `demo/index.html` in a browser (serve it locally, e.g. `python -m http.server`, from the
`demo/` folder with a real `decision_log.json` next to it). Point at one `paid` row and one
`skipped_over_limit` row — this is the auditability story made visible: every dollar the agent
considered spending is on screen, with why.

## Scene 5 — Close (2:20–2:40)

One sentence on what's next if you had more time (e.g., resolving the token-decimals question for
exact USD figures, or expanding beyond `hyreagent.fun` to more Bazaar providers). Ending on a
known limitation, stated plainly, reads as competence, not weakness.

## Submission blurb (for the reply-with-your-submission step, keep under ~250 characters)

> Data Shopper: an AI agent that autonomously discovers and pays for x402-gated crypto data feeds
> on Binance's B402 Bazaar to answer research questions — with hard spend limits and a full
> decision log enforced in code. Built for Track A. [GitHub link]

## Longer version (for the GitHub README top section — already added, see README.md)

Already in place — see the first paragraph of `README.md`.
