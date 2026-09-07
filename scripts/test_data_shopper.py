"""
Offline smoke test for data_shopper.py's control flow: spend tracking,
skip-over-limit behavior, and decision logging. Does NOT hit the network —
`search()` is monkeypatched with a fixture built from the real listings
this project verified live on 2026-09-06 (see ../references/b402-bazaar-api.md).
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


def test_amount_is_labeled_as_capped_estimate(tmp_path: Path):
    """Session 3 fix: amount_usd is an enforced ceiling (server-side
    max_usd_price filter), not a confirmed exact charge — real decimals are
    unresolved (see references/b402-bazaar-api.md). Every paid entry must
    say so via amount_is_capped_estimate, so nothing downstream mistakes an
    upper bound for an exact figure."""
    data_shopper.search = fake_search
    log_path = tmp_path / "decision_log.json"
    data_shopper.shop_for_data(
        keyword="new tokens", per_call_limit_usd=0.05, session_limit_usd=0.50,
        log_path=log_path, dry_run=True,
    )
    on_disk = json.loads(log_path.read_text())
    paid = [e for e in on_disk if e["action"] == "paid"]
    assert paid, "expected at least one paid entry"
    assert all(e["amount_is_capped_estimate"] is True for e in paid)
    print("PASS: test_amount_is_labeled_as_capped_estimate")


def test_circuit_breaker_stops_after_consecutive_failures(tmp_path: Path):
    """A resource with no 'accepts' can't be paid for — two in a row should
    trip the breaker and stop the run rather than churn through the rest of
    the candidate list."""
    broken = BazaarResource(
        resource="https://mpp.hyreagent.fun/broken/no-accepts",
        description="Misconfigured listing",
        x402_version=2,
        accepts=[],  # no payment options at all
        last_updated=0,
    )

    def fake_search_broken(*, query=None, max_usd_price=None, **kwargs):
        return [broken, broken, FIXTURE[0]]  # third item should never be reached

    data_shopper.search = fake_search_broken
    log_path = tmp_path / "decision_log.json"
    entries = data_shopper.shop_for_data(
        keyword="new tokens", per_call_limit_usd=0.05, session_limit_usd=0.50,
        log_path=log_path, dry_run=True, max_consecutive_failures=2,
    )
    assert len(entries) == 2, f"breaker should stop after 2 failures, got {len(entries)} entries"
    assert all(e["action"] == "failed" for e in entries)
    on_disk = json.loads(log_path.read_text())
    assert len(on_disk) == 2, "the third (never-reached) candidate must not be logged"
    print("PASS: test_circuit_breaker_stops_after_consecutive_failures")


def test_malformed_search_response_is_a_failure_not_empty_results():
    """A response missing both 'items' and 'resources' must raise, not be
    silently treated as zero results — otherwise a broken API contract
    looks identical to 'nothing matched the keyword.'"""
    import bazaar_client

    class FakeResponse:
        def __init__(self, payload):
            self._payload = json.dumps(payload).encode("utf-8")
        def read(self):
            return self._payload
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_urlopen(url, timeout=10):
        return FakeResponse({"success": True, "data": {"somethingElse": []}})

    original_urlopen = bazaar_client.urllib.request.urlopen
    bazaar_client.urllib.request.urlopen = fake_urlopen
    try:
        try:
            bazaar_client.search(query="x")
            raise AssertionError("expected BazaarError for missing items/resources key")
        except bazaar_client.BazaarError as exc:
            assert "neither" in str(exc)
    finally:
        bazaar_client.urllib.request.urlopen = original_urlopen
    print("PASS: test_malformed_search_response_is_a_failure_not_empty_results")


if __name__ == "__main__":
    test_spend_tracker_allows_then_blocks()
    with tempfile.TemporaryDirectory() as d:
        test_shop_for_data_dry_run_logs_correctly(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_amount_is_labeled_as_capped_estimate(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_circuit_breaker_stops_after_consecutive_failures(Path(d))
    test_malformed_search_response_is_a_failure_not_empty_results()
    print("\nAll offline smoke tests passed.")
