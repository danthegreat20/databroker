"""
Offline smoke test for data_shopper.py's control flow: spend tracking,
skip-over-limit behavior, and decision logging. Does NOT hit the network —
`search()` is monkeypatched with a fixture built from the real listings
this project verified live on 2026-09-05 (see ../references/b402-bazaar-api.md).
This does not verify the live Bazaar or the payment step; it verifies the
orchestration logic around them.

Run with: python3 test_data_shopper.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import data_shopper  # noqa: E402
from bazaar_client import BazaarResource  # noqa: E402

# Fixture: real resources from the live snapshot, not fabricated shapes.
FIXTURE = [
    BazaarResource(
        resource="https://mpp.hyreagent.fun/bsc/trenches/new-tokens",
        description="New token launches",
        x402_version=2,
        accepts=[{"scheme": "eip3009", "network": "eip155:56",
                  "asset": "0x8d0d000ee44948fc98c9b98a4fa4921476f08b0d",
                  "maxAmountRequired": "80000000000000000",
                  "payTo": "0xb5998e11e666fd1e7f3b8e8d9122a755eec1e9b7"}],
        last_updated=1782217336219,
    ),
    BazaarResource(
        resource="https://mpp.hyreagent.fun/bsc/trenches/graduating",
        description="Tokens near graduation",
        x402_version=2,
        accepts=[{"scheme": "eip3009", "network": "eip155:56",
                  "asset": "0x8d0d000ee44948fc98c9b98a4fa4921476f08b0d",
                  "maxAmountRequired": "30000000000000000",
                  "payTo": "0xb5998e11e666fd1e7f3b8e8d9122a755eec1e9b7"}],
        last_updated=1782217339989,
    ),
    BazaarResource(
        resource="https://mpp.hyreagent.fun/bsc/trenches/bags/new-tokens",
        description="New tokens from Bags.fm",
        x402_version=2,
        accepts=[{"scheme": "eip3009", "network": "eip155:56",
                  "asset": "0x8d0d000ee44948fc98c9b98a4fa4921476f08b0d",
                  "maxAmountRequired": "80000000000000000",
                  "payTo": "0xb5998e11e666fd1e7f3b8e8d9122a755eec1e9b7"}],
        last_updated=1782217352158,
    ),
]


def fake_search(*, query=None, max_usd_price=None, **kwargs):
    return FIXTURE


def test_spend_tracker_allows_then_blocks():
    tracker = data_shopper.SpendTracker(per_call_limit_usd=0.05, session_limit_usd=0.10)
    ok1, _ = tracker.check(0.05)
    assert ok1, "first call within both limits should be allowed"
    tracker.record(0.05)
    ok2, _ = tracker.check(0.05)
    assert ok2, "second call should still fit exactly at the session cap"
    tracker.record(0.05)
    ok3, reason3 = tracker.check(0.05)
    assert not ok3, "third call must be blocked — would exceed SESSION_LIMIT_USD"
    assert "session" in reason3.lower()
    print("PASS: test_spend_tracker_allows_then_blocks")


def test_shop_for_data_dry_run_logs_correctly(tmp_path: Path):
    data_shopper.search = fake_search  # monkeypatch the name used inside data_shopper
    log_path = tmp_path / "decision_log.json"

    entries = data_shopper.shop_for_data(
        keyword="new tokens",
        per_call_limit_usd=0.05,
        session_limit_usd=0.10,  # only 2 of the 3 fixture candidates should fit
        log_path=log_path,
        dry_run=True,
    )

    assert log_path.exists(), "decision log file must be created"
    on_disk = json.loads(log_path.read_text())
    assert len(on_disk) == 3, f"expected 3 logged decisions, got {len(on_disk)}"

    actions = [e["action"] for e in on_disk]
    assert actions.count("paid") == 2, f"expected 2 paid entries, got: {actions}"
    assert actions.count("skipped_over_limit") == 1, f"expected 1 skip, got: {actions}"

    paid_entries = [e for e in on_disk if e["action"] == "paid"]
    for e in paid_entries:
        assert e["amount_usd"] == 0.05
        assert "dry-run" in e["rationale"]

    # Shape check against what demo/index.html actually reads
    required_keys = {"timestamp", "resource", "description", "action", "amount_usd", "rationale", "limit_checked_against"}
    for e in on_disk:
        assert required_keys.issubset(e.keys()), f"missing keys in entry: {e}"

    print("PASS: test_shop_for_data_dry_run_logs_correctly")


if __name__ == "__main__":
    test_spend_tracker_allows_then_blocks()
    with tempfile.TemporaryDirectory() as d:
        test_shop_for_data_dry_run_logs_correctly(Path(d))
    print("\nAll offline smoke tests passed.")
