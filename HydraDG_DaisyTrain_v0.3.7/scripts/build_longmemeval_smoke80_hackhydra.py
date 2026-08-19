#!/usr/bin/env python3
"""Build a deterministic Hack-Hydra-only LongMemEval smoke subset.

This helper is a fresh release implementation so the public submission does not
depend on an origin-ambiguous pre-hackathon participant utility. Selection is
content-stable: rows are ordered by SHA-256(question_id) then question_id, and
the first N are emitted without using answer_session_ids.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def row_key(row: dict) -> tuple[str, str]:
    qid = str(row.get("question_id", ""))
    return hashlib.sha256(qid.encode()).hexdigest(), qid


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--n", type=int, default=80)
    args = ap.parse_args()

    source = Path(args.source)
    source_bytes = source.read_bytes()
    rows = json.loads(source_bytes)
    if not isinstance(rows, list):
        raise SystemExit("LongMemEval source must be a JSON array")
    if args.n < 1 or args.n > len(rows):
        raise SystemExit(f"invalid --n={args.n}; source rows={len(rows)}")

    selected = sorted(rows, key=row_key)[: args.n]
    out_bytes = (json.dumps(selected, indent=2, ensure_ascii=False) + "\n").encode()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(out_bytes)

    ids = [str(row.get("question_id", "")) for row in selected]
    manifest = {
        "schema": "hydradg.longmemeval_smoke_hackhydra.v1",
        "source_path": str(source),
        "source_sha256": sha256_bytes(source_bytes),
        "source_rows": len(rows),
        "selected_rows": len(selected),
        "selection": "SORT_BY_SHA256_QUESTION_ID_THEN_QUESTION_ID_TAKE_N",
        "answer_session_ids_used_for_selection": False,
        "selected_question_ids": ids,
        "output_path": str(out),
        "output_sha256": sha256_bytes(out_bytes),
        "evidence_class": "DETERMINISTIC_SOURCE_SUBSET_TRANSFORM",
        "claim_ceiling": "DEVELOPMENT_SMOKE_SUBSET_ONLY_NOT_BENCHMARK_RESULT",
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(manifest_bytes)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
