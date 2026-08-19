#!/usr/bin/env python3
"""Static fail-closed audit for the Release Watch Context Iceberg surface.

This checks implementation language/contracts only. It does not establish a scientific
CloudDrift/G* result and does not replace the Next.js build/browser gate.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = {
    "contract": ROOT / "apps/hydradg-web/lib/contextIceberg.ts",
    "graph": ROOT / "apps/hydradg-web/components/ContextIcebergGraph.tsx",
    "api": ROOT / "apps/hydradg-web/app/api/math/current/route.ts",
    "knowledge": ROOT / "apps/hydradg-web/lib/knowledgeLinks.ts",
    "spec": ROOT / "docs/CONTEXT_ICEBERG_SCORE_SPEC.md",
    "fallback": ROOT / "apps/hydradg-web/public/backup/context-iceberg.html",
}
for label, path in files.items():
    if not path.is_file():
        raise SystemExit(f"MISSING_{label.upper()}={path}")

contract = files["contract"].read_text(encoding="utf-8")
graph = files["graph"].read_text(encoding="utf-8")
api = files["api"].read_text(encoding="utf-8")
knowledge = files["knowledge"].read_text(encoding="utf-8")
spec = files["spec"].read_text(encoding="utf-8")
fallback = files["fallback"].read_text(encoding="utf-8")

required = {
    "contract": [
        "Math.log2",
        "jsd * 100",
        '"LOWER"',
        '"STABLE"',
        '"HIGHER"',
        '"PENDING_CANONICAL_FCO_FCG_BINDING"',
        '"OBJECT_SPECIFIC"',
        '"STATE_INHERITED"',
        '"DEMO_CONTROL"',
    ],
    "graph": [
        "cloud width encodes frozen CloudDrift",
        "Dashed halos demonstrate",
        "not JSD",
        "metric_source",
        "Context Iceberg",
    ],
    "api": [
        "HYDRADG_CONTEXT_ICEBERG_JSON",
        "GIBBS_CONFIG=PENDING" if False else "gibbs_config_state",
        "X-HydraDG-Read-Only",
        "artifact_sha256",
        "PENDING_CONTEXT_ICEBERG",
    ],
    "knowledge": [
        'slug: "context-iceberg"',
        'slug: "context-cloud"',
        'slug: "cloud-drift"',
        'slug: "jensen-shannon-divergence"',
        'slug: "context-drift-observation"',
    ],
    "spec": [
        "CloudDrift_t = 100 * JSD",
        "Do NOT label negative ΔG* as",
        "H0-PROVENANCE",
        "PENDING VERIFICATION",
    ],
    "fallback": [
        "Cloud Drift",
        "PENDING",
        "demo control",
        "not measured Jensen-Shannon CloudDrift",
    ],
}
texts = {"contract": contract, "graph": graph, "api": api, "knowledge": knowledge, "spec": spec, "fallback": fallback}
missing = []
for label, needles in required.items():
    for needle in needles:
        if needle not in texts[label]:
            missing.append(f"{label}:{needle}")

for item in missing:
    print(f"MISSING={item}")
if missing:
    raise SystemExit(1)

# Fail if the two forbidden semantic shortcuts appear in the implementation.
forbidden = [
    "negative ΔG* means better accuracy",
    "CloudDrift proves",
]
joined = "\n".join(texts.values())
violations = [item for item in forbidden if item in joined]
for item in violations:
    print(f"FORBIDDEN={item}")
if violations:
    raise SystemExit(2)

print("CONTEXT_ICEBERG_STATIC_CONTRACT=PASS")
print("SCIENTIFIC_SCORE_STATE=NOT_ESTABLISHED_BY_THIS_CHECK")
print("CLAIM_CEILING=STATIC_DISPLAY_AND_READ_ONLY_CONTRACT_ONLY")
