#!/usr/bin/env python3
"""Run Hack Hydra Best Use v2 typed-memory A/B/C/D retrieval on LongMemEval."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from best_use_typed_graph import (
    HydraHTTP,
    OllarmaExtractor,
    evaluate_retrieval,
    ingest_typed_case,
    prepare_typed_case,
    rank_method,
)

METHODS = ("A", "B", "C", "D")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--extractor", choices=("heuristic", "ollarma", "none"), default="heuristic")
    ap.add_argument("--ollarma-url", default="http://127.0.0.1:8484")
    ap.add_argument("--model", default=None)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    source_path = Path(args.data)
    source_bytes = source_path.read_bytes()
    data = json.loads(source_bytes)
    if args.limit is not None:
        data = data[: args.limit]
    token = Path(args.token_file).read_text().strip()
    hydra = HydraHTTP(args.endpoint, token)
    cache_dir = Path(args.cache_dir) if args.cache_dir else None
    ollarma = OllarmaExtractor(args.ollarma_url, model=args.model) if args.extractor == "ollarma" else None

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    aggregate_graph = {"cases": 0, "sessions": 0, "entities": 0, "facts": 0, "edges": {}}
    started = time.perf_counter()

    with out_path.open("w") as fh:
        for ordinal, case in enumerate(data, start=1):
            prepared = prepare_typed_case(case, args.extractor, cache_dir, ollarma)
            graph = ingest_typed_case(hydra, prepared)
            aggregate_graph["cases"] += graph["case_nodes"]
            aggregate_graph["sessions"] += graph["session_nodes"]
            aggregate_graph["entities"] += graph["entity_nodes"]
            aggregate_graph["facts"] += graph["fact_nodes"]
            for rel, count in graph["edges"].items():
                aggregate_graph["edges"][rel] = aggregate_graph["edges"].get(rel, 0) + count

            qid = str(case["question_id"])
            row = {
                "schema": "hydradg.best_use_typed_case.v2",
                "question_id": qid,
                "question_type": str(case.get("question_type", "UNKNOWN")),
                "is_abstention": qid.endswith("_abs"),
                "k": args.k,
                "extractor": args.extractor,
                "graph": graph,
                "methods": {},
            }
            question = str(case.get("question", ""))
            for method in METHODS:
                chosen, reasons, latency, path_coverage = rank_method(prepared, hydra, method, question, args.k)
                retrieved, hit, recall = evaluate_retrieval(chosen, prepared, args.k)
                row["methods"][method] = {
                    "retrieved_session_ids": retrieved,
                    "hit_at_k": hit,
                    "session_recall_at_k": recall,
                    "latency_ms": latency,
                    "context_sessions": len(retrieved),
                    "evidence_path_coverage": path_coverage,
                    "retrieval_reasons": {
                        f"{prepared['sids'][idx]}@{idx}": reasons.get(idx, []) for idx in chosen[: args.k]
                    },
                }
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            print(json.dumps({"case": ordinal, "n": len(data), "question_id": qid, "facts": graph["fact_nodes"], "entities": graph["entity_nodes"]}, sort_keys=True))

    receipt = {
        "schema": "hydradg.best_use_typed_run_receipt.v2",
        "source": str(source_path),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "rows": len(data),
        "k": args.k,
        "extractor": args.extractor,
        "ollarma_url": args.ollarma_url if args.extractor == "ollarma" else None,
        "model": args.model if args.extractor == "ollarma" else None,
        "aggregate_graph": aggregate_graph,
        "elapsed_ms": (time.perf_counter() - started) * 1000,
        "ground_truth_use": "answer_session_ids used only after retrieval for evaluation",
        "identity_fix": "Session vertex is question_id + external_session_id + occurrence_position",
        "claim_ceiling": "TYPED_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
    }
    Path(str(out_path) + ".receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
