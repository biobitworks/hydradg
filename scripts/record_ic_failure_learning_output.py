#!/usr/bin/env python3
"""Append one raw Cloudflare OS/Ollama result to the failure-learning result ledger.

The raw response file must contain exactly the model's JSON response. The recorder hashes exact
bytes, attempts deterministic JSON parsing, and preserves parse failures rather than repairing them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--model-identity", required=True)
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--replicate", type=int, required=True)
    ap.add_argument("--raw-file", required=True)
    ap.add_argument("--cloudflare-os-commit", required=True)
    ap.add_argument("--ollama-version", required=True)
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/results/MODEL_OUTPUTS.jsonl")
    args = ap.parse_args()

    raw_path = Path(args.raw_file)
    raw = raw_path.read_bytes()
    digest = sha(raw)
    try:
        parsed = json.loads(raw.decode("utf-8"))
        parser_state = "PARSED_JSON"
    except Exception as exc:  # preserve malformed response; do not repair
        parsed = None
        parser_state = f"MALFORMED_JSON:{type(exc).__name__}"

    row = {
        "schema": "hydradg.ic_failure_learning.model_output.v1",
        "model": args.model,
        "model_identity": args.model_identity,
        "case_id": args.case_id,
        "replicate": args.replicate,
        "cloudflare_os_commit": args.cloudflare_os_commit,
        "ollama_version": args.ollama_version,
        "raw_response_sha256": digest,
        "raw_response_bytes": len(raw),
        "parser_state": parser_state,
        "parsed": parsed,
        "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED_AT_MODEL_OUTPUT_STAGE"
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if out.exists():
        existing = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    key = (args.model, args.case_id, args.replicate)
    if any((r.get("model"), r.get("case_id"), r.get("replicate")) == key for r in existing):
        raise SystemExit(f"STOP duplicate model/case/replicate key: {key}")

    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({
        "recorded": True,
        "key": key,
        "raw_response_sha256": digest,
        "parser_state": parser_state,
        "out": str(out)
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
