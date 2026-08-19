#!/usr/bin/env python3
"""Crawl the HydraDG release site's internal links and report external targets.

Internal links are a hard release gate. External links are optionally probed and
reported separately because upstream sites may intentionally reject automated
clients while remaining browser-accessible.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import deque

HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)
SEED_ROUTES = [
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
]


def fetch(url: str, timeout: int = 20) -> tuple[int, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "HydraDG-HackHydra-LinkAudit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode(errors="replace")
            return response.status, response.geturl(), body
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl(), exc.read().decode(errors="replace")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:3000")
    ap.add_argument("--external", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    base = args.base.rstrip("/")
    parsed_base = urllib.parse.urlsplit(base)
    queue = deque(SEED_ROUTES)
    seen: set[str] = set()
    internal_rows = []
    external: set[str] = set()

    # Add one content-addressed dynamic FCO route from the site FCG API.
    site_fcg_status, _, site_fcg_body = fetch(f"{base}/api/site-fcg")
    if site_fcg_status >= 400:
        raise SystemExit(f"site FCG API failed: HTTP {site_fcg_status}")
    site_fcg = json.loads(site_fcg_body)
    if site_fcg.get("nodes"):
        queue.append(f"/fco/{urllib.parse.quote(str(site_fcg['nodes'][0]['id']), safe='')}")

    while queue:
        route = queue.popleft()
        if route in seen:
            continue
        seen.add(route)
        url = urllib.parse.urljoin(base + "/", route.lstrip("/"))
        status, final_url, body = fetch(url)
        internal_rows.append({"route": route, "status": status, "final_url": final_url})
        if status >= 400:
            continue
        for href in HREF.findall(body):
            href = href.strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            resolved = urllib.parse.urljoin(final_url, href)
            parsed = urllib.parse.urlsplit(resolved)
            if parsed.scheme not in {"http", "https"}:
                continue
            if parsed.netloc == parsed_base.netloc:
                next_route = parsed.path or "/"
                if parsed.query:
                    next_route += "?" + parsed.query
                if next_route not in seen:
                    queue.append(next_route)
            else:
                external.add(resolved)

    broken_internal = [row for row in internal_rows if row["status"] >= 400]
    external_rows = []
    if args.external:
        for url in sorted(external):
            status, final_url, _ = fetch(url)
            external_rows.append({
                "url": url,
                "status": status,
                "final_url": final_url,
                "browser_review_required": status in {401, 403, 429},
            })

    result = {
        "schema": "hydradg.web_link_audit.v1",
        "base": base,
        "internal": internal_rows,
        "internal_broken": broken_internal,
        "internal_status": "PASS" if not broken_internal else "FAIL",
        "external_targets": sorted(external),
        "external_probe_enabled": args.external,
        "external": external_rows,
        "claim_ceiling": "HTTP_LINK_REACHABILITY_AT_AUDIT_TIME_ONLY",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.out:
        with open(args.out, "w") as handle:
            handle.write(rendered + "\n")
    if broken_internal:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
