"""
Thin client for Binance's B402 Bazaar public discovery API.

Verified live against the real endpoint on 2026-09-05 — see
../references/b402-bazaar-api.md for the confirmed response shape and the
open questions (token decimals) that are NOT yet resolved.

This client only does discovery (read-only, no auth, no money moved). Paying
for a discovered resource is a separate step handled by the `binance-agentic-
wallet` skill's `baw` CLI — see ../SKILL.md for why that step is a manual
verification item, not something this script does.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional

BASE_URL = "https://www.binance.com/bapi/ramp/v1/public/ramp/b402"


class BazaarError(RuntimeError):
    """Raised when the Bazaar API returns a non-success envelope, or the
    request itself fails. Per Section 9.6 of the build ruleset: this is a
    blocker to surface, not something to retry silently or paper over with
    fake data."""


@dataclass
class BazaarResource:
    resource: str
    description: str
    x402_version: int
    accepts: list[dict[str, Any]]
    last_updated: int

    @property
    def network(self) -> Optional[str]:
        return self.accepts[0].get("network") if self.accepts else None

    @property
    def asset(self) -> Optional[str]:
        return self.accepts[0].get("asset") if self.accepts else None

    @property
    def max_amount_required_raw(self) -> Optional[str]:
        """Raw integer string in the asset's smallest unit. Do NOT convert
        this to USD without first confirming the asset's decimals — see the
        reference doc. Use max_usd_price on search() instead if you need a
        USD-denominated filter."""
        return self.accepts[0].get("maxAmountRequired") if self.accepts else None

    @property
    def pay_to(self) -> Optional[str]:
        return self.accepts[0].get("payTo") if self.accepts else None


def _get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    query = {k: v for k, v in params.items() if v is not None}
    url = f"{BASE_URL}{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # network/HTTP failure
        raise BazaarError(f"Bazaar request failed: {url} — {exc}") from exc

    if not body.get("success", False):
        raise BazaarError(f"Bazaar returned an error envelope: {body}")
    return body["data"]


def _parse_resources(items: list[dict[str, Any]]) -> list[BazaarResource]:
    return [
        BazaarResource(
            resource=item["resource"],
            description=item.get("description", ""),
            x402_version=item.get("x402Version", 0),
            accepts=item.get("accepts", []),
            last_updated=item.get("lastUpdated", 0),
        )
        for item in items
    ]


def list_resources(limit: int = 25, offset: int = 0) -> list[BazaarResource]:
    """GET /bazaar/resources — confirmed live shape: data.items[]."""
    data = _get("/bazaar/resources", {"limit": limit, "offset": offset})
    return _parse_resources(data.get("items", []))


def search(
    query: Optional[str] = None,
    network: Optional[str] = None,
    asset: Optional[str] = None,
    scheme: Optional[str] = None,
    pay_to: Optional[str] = None,
    max_usd_price: Optional[float] = None,
) -> list[BazaarResource]:
    """GET /bazaar/search — per Binance's docs the payload key is
    data.resources[], NOT data.items[]. This has not been directly confirmed
    live by this project yet (Section 9.8) — the first real call should log
    and check the raw response before trusting this parsing."""
    data = _get(
        "/bazaar/search",
        {
            "query": query,
            "network": network,
            "asset": asset,
            "scheme": scheme,
            "payTo": pay_to,
            "maxUsdPrice": max_usd_price,
        },
    )
    key = "resources" if "resources" in data else "items"
    return _parse_resources(data.get(key, []))


def _main() -> None:
    parser = argparse.ArgumentParser(description="Query the B402 Bazaar discovery API.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List the full catalog.")
    p_list.add_argument("--limit", type=int, default=25)
    p_list.add_argument("--offset", type=int, default=0)

    p_search = sub.add_parser("search", help="Keyword/filter search.")
    p_search.add_argument("--query", type=str, default=None)
    p_search.add_argument("--network", type=str, default=None)
    p_search.add_argument("--max-usd-price", type=float, default=None, dest="max_usd_price")

    args = parser.parse_args()

    try:
        if args.command == "list":
            resources = list_resources(limit=args.limit, offset=args.offset)
        else:
            resources = search(query=args.query, network=args.network, max_usd_price=args.max_usd_price)
    except BazaarError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    for r in resources:
        print(f"{r.resource}\n  {r.description}\n  network={r.network} raw_amount={r.max_amount_required_raw}\n")


if __name__ == "__main__":
    _main()
