#!/usr/bin/env python3
"""
Prepare a compact deterministic Antigravity evidence packet from VITHIA-OVERNIGHT-01.

This script:
- reads only the bounded known artifacts;
- recomputes SHA-256;
- includes the full status/matrix/runtime snapshot;
- includes the evidence index;
- extracts evidence-index entries mentioning representative run IDs;
- writes one compact JSON packet.

It does NOT sign, verify signatures, or build a Merkle/MMR.
"""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPRESENTATIVE_RUNS = [
    "control_s314159_r1",
    "thread4_s314159",
    "perturb_mid_s314159",
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def collect_mentions(obj: Any, needles: list[str], path: str = "$") -> list[dict]:
    out = []
    if isinstance(obj, dict):
        serialized = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        hits = [n for n in needles if n in serialized]
        if hits:
            out.append({"path": path, "runs": hits, "object": obj})
            return out
        for k, v in obj.items():
            out.extend(collect_mentions(v, needles, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(collect_mentions(v, needles, f"{path}[{i}]"))
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--package",
        default="/Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7",
    )
    ap.add_argument(
        "--out",
        default="eval/vithia_overnight/VITHIA-OVERNIGHT-01/ANTIGRAVITY_PACKET.json",
    )
    args = ap.parse_args()

    pkg = Path(args.package).resolve()
    run = pkg / "eval/vithia_overnight/VITHIA-OVERNIGHT-01"
    paths = {
        "status": run / "status.json",
        "matrix": run / "vithia_overnight_matrix.json",
        "evidence_index": run / "EVIDENCE_INDEX.json",
        "runtime_snapshot": pkg / "eval/vithia_runtime/runtime_snapshot.json",
    }

    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise SystemExit("Missing required bounded artifacts:\n" + "\n".join(missing))

    loaded = {k: load_json(p) for k, p in paths.items()}
    hashes = {k: {"path": str(p), "sha256": sha256_file(p)} for k, p in paths.items()}

    packet = {
        "schema": "hydradg.antigravity_packet.v1",
        "experiment": "VITHIA-OVERNIGHT-01",
        "representative_runs": REPRESENTATIVE_RUNS,
        "artifact_hashes": hashes,
        "status": loaded["status"],
        "runtime_snapshot": loaded["runtime_snapshot"],
        "matrix": loaded["matrix"],
        "evidence_index": loaded["evidence_index"],
        "representative_evidence_index_mentions": collect_mentions(
            loaded["evidence_index"], REPRESENTATIVE_RUNS
        ),
        "claim_boundary": (
            "Deterministic compact evidence packet only. "
            "No signature verification, Merkle/MMR commitment, or scientific validation is implied."
        ),
    }

    out = Path(args.out)
    if not out.is_absolute():
        out = pkg / out
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n"
    out.write_text(data, encoding="utf-8")
    print(out)
    print("sha256=" + hashlib.sha256(data.encode("utf-8")).hexdigest())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
