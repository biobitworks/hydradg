#!/usr/bin/env python3
"""Static smoke checks for the standalone HydraDG judge fallback."""
from pathlib import Path

p = Path("apps/hydradg-web/public/backup/hydradg.html")
text = p.read_text(encoding="utf-8")
required = [
    "See the context move.",
    "Reference → poison → antidote.",
    "The tested retrieval advantage did not appear.",
    "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
    "Context Iceberg",
    "Cloud Drift",
    "Jensen-Shannon divergence",
    "ΔG*",
    "A halo does not by itself establish causal attribution.",
    "NOT_SIGNED",
    "NOT_MERKLE_COMMITTED",
]
low = text.lower()
missing = [item for item in required if item.lower() not in low]
print(f"STATIC_FALLBACK_BYTES={p.stat().st_size}")
print(f"STATIC_FALLBACK_MISSING={len(missing)}")
for item in missing:
    print(f"MISSING={item}")
if missing:
    raise SystemExit(1)
print("STATIC_FALLBACK_CONTEXT_ICEBERG=PASS")
print("STATIC_FALLBACK_SMOKE=PASS")
