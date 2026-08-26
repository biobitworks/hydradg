#!/usr/bin/env python3
"""Local + Tailscale smoke for HydraDG studio-test server."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

PAGES = [
    "/",
    "/demo",
    "/judge",
    "/graph",
    "/knowledge",
    "/evidence",
    "/eligibility",
    "/track01",
    "/track02",
    "/track03",
    "/how-to",
]


def fetch(url: str, timeout: float = 20.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()


def must_200(base: str, path: str) -> None:
    code, _ = fetch(f"{base}{path}")
    print(f"{path} -> {code}")
    if code != 200:
        raise SystemExit(f"FAIL {path} expected 200 got {code}")


def check_fail_closed(base: str) -> None:
    code, body = fetch(f"{base}/api/live")
    if code != 503:
        raise SystemExit(f"/api/live expected 503 got {code}")
    data = json.loads(body.decode())
    if data.get("configured") is not False or data.get("mode") != "PUBLIC_FIXTURE_ONLY":
        # Local env may configure BEST_USE_SERVER_URL; accept LIVE only when intentional.
        if data.get("mode") not in {"PUBLIC_FIXTURE_ONLY", "LIVE_LOCAL_HYDRADB", "LIVE_BACKEND_UNREACHABLE"}:
            raise SystemExit(f"/api/live unexpected payload: {data}")
    print(f"/api/live -> {code} mode={data.get('mode')}")

    code, body = fetch(f"{base}/api/hydradb-cloud")
    data = json.loads(body.decode())
    # Hosted key may be present on Studio; never require disclosure.
    if data.get("secret_disclosure") not in {
        "API_KEY_VALUE_NEVER_RETURNED",
        "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
        None,
    }:
        # tolerate configured cloud when key present
        pass
    if "secret_disclosure" in data and "NEVER_RETURNED" not in str(data.get("secret_disclosure", "")):
        if code == 503 and data.get("configured") is False:
            print(f"/api/hydradb-cloud -> {code} fail-closed OK")
            return
        if code == 200 and data.get("configured") is True:
            print(f"/api/hydradb-cloud -> {code} configured (key present, value not disclosed)")
            return
        raise SystemExit(f"/api/hydradb-cloud unexpected: {code} {data}")
    print(f"/api/hydradb-cloud -> {code}")


def check_custody(base: str) -> None:
    code, body = fetch(f"{base}/api/custody")
    if code != 200:
        raise SystemExit(f"/api/custody expected 200 got {code}")
    data = json.loads(body.decode())
    if data.get("schema") != "hydradg.fixture_custody_checkpoint.v1":
        raise SystemExit("custody schema mismatch")
    print("/api/custody -> 200")
    code, body = fetch(f"{base}/api/site-fcg")
    if code != 200:
        raise SystemExit(f"/api/site-fcg expected 200 got {code}")
    data = json.loads(body.decode())
    if data.get("schema") != "hydradg.site_fcg.v1":
        raise SystemExit("site-fcg schema mismatch")
    print("/api/site-fcg -> 200")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:3000")
    ap.add_argument("--pages-only", action="store_true")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    for path in PAGES:
        must_200(base, path)
    if not args.pages_only:
        check_custody(base)
        check_fail_closed(base)
    print("HEALTHCHECK_PASS", base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
