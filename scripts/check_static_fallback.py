#!/usr/bin/env python3
"""Static smoke checks for standalone HydraDG judge fallbacks."""
from pathlib import Path

checks = {
    Path("apps/hydradg-web/public/backup/hydradg.html"): [
        "See what changed. Trace why. Test the repair.",
        "Reference → poison → antidote.",
        "No positive signal",
        "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
        "NOT_SIGNED",
        "NOT_MERKLE_COMMITTED",
        "tip of the iceberg",
    ],
    Path("apps/hydradg-web/public/backup/context-iceberg.html"): [
        "Context Iceberg",
        "Cloud Drift",
        "PENDING",
        "demo control",
        "not measured Jensen-Shannon CloudDrift",
        "Direction ≠ outcome ≠ custody",
        "CloudDrift = 100 × JSD",
        "NOT MERKLE COMMITTED",
    ],
}

failures = []
for path, required in checks.items():
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    missing = [item for item in required if item.lower() not in low]
    print(f"STATIC_FALLBACK={path}")
    print(f"STATIC_FALLBACK_BYTES={path.stat().st_size}")
    print(f"STATIC_FALLBACK_MISSING={len(missing)}")
    for item in missing:
        print(f"MISSING={item}")
    if missing:
        failures.append((path, missing))

if failures:
    raise SystemExit(1)
print("STATIC_FALLBACK_SMOKE=PASS")
