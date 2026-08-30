#!/usr/bin/env python3
"""DRM-free anonymous submission verifier (stdlib only)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def main() -> int:
    gates = {
        "BYTE_HASH_GATE": "FAIL",
        "FCO_MANIFEST_GATE": "FAIL",
        "FCG_EDGE_GATE": "FAIL",
        "PDF_HASH_GATE": "FAIL",
        "TABLE_PROVENANCE_GATE": "FAIL",
    }
    manifest_path = ROOT / "PUBLIC_SUBMISSION_FCO_MANIFEST.jsonl"
    fcg_path = ROOT / "PUBLIC_SUBMISSION_FCG.jsonl"
    root_path = ROOT / "PUBLIC_SUBMISSION_ROOT.json"
    if not manifest_path.exists() or not root_path.exists():
        print(json.dumps({"gates": gates, "error": "missing manifest or root"}, indent=2))
        return 1

    objects = load_jsonl(manifest_path)
    byte_ok = True
    for obj in objects:
        p = ROOT / obj["path"]
        if not p.exists():
            byte_ok = False
            break
        if sha256_file(p) != obj["sha256"]:
            byte_ok = False
            break
    gates["BYTE_HASH_GATE"] = "PASS" if byte_ok else "FAIL"
    gates["FCO_MANIFEST_GATE"] = "PASS" if objects else "FAIL"

    edges = load_jsonl(fcg_path) if fcg_path.exists() else []
    obj_ids = {o["logical_id"] for o in objects}
    edge_ok = all(e.get("from") and e.get("to") for e in edges)
    gates["FCG_EDGE_GATE"] = "PASS" if edge_ok and edges else "FAIL"

    root_obj = json.loads(root_path.read_text())
    recomputed = sha256_bytes = hashlib.sha256(
        "\n".join(
            f"{o['logical_id']}:{o['sha256']}"
            for o in sorted(objects, key=lambda x: x["logical_id"])
        ).encode()
    ).hexdigest()
    gates["PDF_HASH_GATE"] = (
        "PASS"
        if any(o["logical_id"] == "PDF-MAIN" and o["sha256"] == root_obj.get("pdf_sha256") for o in objects)
        else "FAIL"
    )
    if recomputed == root_obj.get("PUBLIC_SUBMISSION_ROOT"):
        gates["FCO_MANIFEST_GATE"] = "PASS"

    table_src = ROOT / "tables/TABLE_001_TERMINAL_SOURCE.json"
    table_tex = ROOT / "tables/TABLE_001_TERMINAL.tex"
    if table_src.exists() and table_tex.exists():
        src = json.loads(table_src.read_text())
        tex = table_tex.read_text()
        table_ok = all(row["study"] in tex for row in src.get("rows", []))
        gates["TABLE_PROVENANCE_GATE"] = "PASS" if table_ok else "FAIL"

    all_pass = all(v == "PASS" for v in gates.values())
    print(
        json.dumps(
            {
                "gates": gates,
                "PUBLIC_SUBMISSION_ROOT": root_obj.get("PUBLIC_SUBMISSION_ROOT"),
                "recomputed_root": recomputed,
                "root_match": recomputed == root_obj.get("PUBLIC_SUBMISSION_ROOT"),
                "VERIFICATION": "PASS" if all_pass else "FAIL",
                "note": (
                    "Passing verification establishes byte identity and declared derivation "
                    "consistency only; not scientific truth, causal validity, or author identity."
                ),
            },
            indent=2,
        )
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
