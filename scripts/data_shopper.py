"""
Core orchestration for the data-shopper agent (Session 2).

Real and runnable *today*, end-to-end, in --dry-run mode: discovery against
the live Bazaar, spend-limit checks, and decision logging all execute for
real. The one piece that is NOT real yet is the actual x402 payment call —
see _pay_via_baw() below and SKILL.md's verification-status section for why.
It is isolated into a single function on purpose, so confirming the real
`baw` syntax later means changing one function, not re-auditing this file.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Optional

from bazaar_client import BazaarError, BazaarResource, search


class SpendTracker:
    """Enforces Section 9.4: hard limits checked in code, not just declared.
    Nothing in this class can be bypassed by the caller short of not calling
    it — shop_for_data() below always checks before acting."""

    def __init__(self, per_call_limit_usd: float, session_limit_usd: float):
        self.per_call_limit_usd = per_call_limit_usd
        self.session_limit_usd = session_limit_usd
        self.session_total_usd = 0.0

    def check(self, amount_usd: float) -> tuple[bool, str]:
        if amount_usd > self.per_call_limit_usd:
            return False, (
                f"amount_usd={amount_usd:.4f} exceeds "
                f"PER_CALL_LIMIT_USD={self.per_call_limit_usd:.4f}"
            )
        would_be_total = self.session_total_usd + amount_usd
        if would_be_total > self.session_limit_usd:
            return False, (
                f"would bring session total to {would_be_total:.4f}, over "
                f"SESSION_LIMIT_USD={self.session_limit_usd:.4f} "
                f"(current total {self.session_total_usd:.4f})"
            )
        return True, (
            f"PER_CALL_LIMIT_USD={self.per_call_limit_usd:.4f}, "
            f"session_total={self.session_total_usd:.4f}/{self.session_limit_usd:.4f}"
        )

    def record(self, amount_usd: float) -> None:
        self.session_total_usd += amount_usd


def _log_decision(log_path: Path, entry: dict) -> None:
    """Appends one entry to the JSON array at log_path, creating it if
    needed. Matches the exact shape demo/index.html expects."""
    entries: list[dict] = []
    if log_path.exists():
        try:
            entries = json.loads(log_path.read_text())
        except (json.JSONDecodeError, OSError):
            entries = []
    entries.append(entry)
    log_path.write_text(json.dumps(entries, indent=2))


def _pay_via_baw(resource: BazaarResource, max_usd: float, dry_run: bool) -> dict:
    """
    ⚠️ UNVERIFIED — see SKILL.md's "Verification status" section.

    This is the ONE function in this project that touches real money, and it
    is deliberately left unimplemented for live use. Do not fill this in by
    guessing the `baw` CLI's syntax — run `baw x402 --help` against the real
    installed CLI first, confirm the actual command and output shape, then
    implement the subprocess call here.
    """
    if dry_run:
        return {
            "paid": True,
            "simulated": True,
            "amount_usd": max_usd,
            "note": "dry-run — no subprocess called, no money moved",
        }
    raise NotImplementedError(
        "baw x402 payment command is unverified (see SKILL.md). Run "
        "`baw x402 --help` for real, confirm the syntax, then implement "
        "_pay_via_baw() before running without --dry-run."
    )


def shop_for_data(
    keyword: str,
    per_call_limit_usd: float,
    session_limit_usd: float,
    log_path: Path,
    dry_run: bool,
    max_candidates: int = 5,
) -> list[dict]:
    """Discover candidates for `keyword`, pay for (or skip/fail) each one in
    turn, logging every decision. Returns the list of entries logged this
    run (not the cumulative file)."""
    tracker = SpendTracker(per_call_limit_usd, session_limit_usd)
    run_entries: list[dict] = []

    try:
        candidates = search(query=keyword, max_usd_price=per_call_limit_usd)
    except BazaarError as exc:
        # Section 9.6: an exchange/API failure is a blocker, not something
        # to route around with fabricated data.
        entry = {
            "timestamp": _now(),
            "resource": None,
            "description": f"Bazaar search failed for keyword={keyword!r}",
            "action": "failed",
            "amount_usd": 0,
            "rationale": str(exc),
            "limit_checked_against": None,
        }
        _log_decision(log_path, entry)
        return [entry]

    for resource in candidates[:max_candidates]:
        ok, reason = tracker.check(per_call_limit_usd)
        entry = {
            "timestamp": _now(),
            "resource": resource.resource,
            "description": resource.description,
            "amount_usd": per_call_limit_usd,
            "limit_checked_against": reason,
        }

        if not ok:
            entry["action"] = "skipped_over_limit"
            entry["rationale"] = reason
            _log_decision(log_path, entry)
            run_entries.append(entry)
            continue

        try:
            _pay_via_baw(resource, per_call_limit_usd, dry_run=dry_run)
        except NotImplementedError as exc:
            entry["action"] = "failed"
            entry["rationale"] = str(exc)
            _log_decision(log_path, entry)
            run_entries.append(entry)
            continue  # don't keep trying other endpoints blind either — surface it

        tracker.record(per_call_limit_usd)
        entry["action"] = "paid"
        entry["rationale"] = (
            f"Matched keyword {keyword!r}; "
            + ("dry-run simulated payment." if dry_run else "paid via baw.")
        )
        _log_decision(log_path, entry)
        run_entries.append(entry)

    return run_entries


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _main() -> None:
    parser = argparse.ArgumentParser(description="Run the data-shopper agent once.")
    parser.add_argument("--keyword", required=True, help="Search term for the Bazaar, e.g. 'new tokens'")
    parser.add_argument("--per-call-limit", type=float, default=0.05)
    parser.add_argument("--session-limit", type=float, default=0.50)
    parser.add_argument("--log-path", type=str, default="decision_log.json")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate payment (no subprocess, no money moved). Omit this flag "
        "only after _pay_via_baw() has a real, verified implementation.",
    )
    args = parser.parse_args()

    if not args.dry_run:
        print(
            "Refusing to run live: _pay_via_baw() is still unimplemented "
            "(see SKILL.md). Re-run with --dry-run, or implement that "
            "function first.",
            file=sys.stderr,
        )
        sys.exit(1)

    entries = shop_for_data(
        keyword=args.keyword,
        per_call_limit_usd=args.per_call_limit,
        session_limit_usd=args.session_limit,
        log_path=Path(args.log_path),
        dry_run=args.dry_run,
    )
    for e in entries:
        print(f"[{e['action']}] {e['description']} — {e.get('rationale', '')}")


if __name__ == "__main__":
    _main()
