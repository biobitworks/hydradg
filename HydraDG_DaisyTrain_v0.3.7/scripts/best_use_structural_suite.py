#!/usr/bin/env python3
"""Fast structural conformance suite for Hack Hydra Best Use v2.

This suite validates graph identity/traversal invariants against a live HydraDB
without using LongMemEval answer labels or a language model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from best_use_typed_graph import HydraHTTP, hydra_health, ingest_typed_case, prepare_typed_case, provenance_set


def canonical_sha(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def synthetic_case(qid: str, duplicate_sid: bool = False) -> dict:
    sids = ["session-dup", "session-dup" if duplicate_sid else "session-new", "session-food"]
    return {
        "question_id": qid,
        "question_type": "knowledge-update",
        "question": "Where does the user live now?",
        "haystack_session_ids": sids,
        "haystack_sessions": [
            [{"role": "user", "content": "I live in Oakland."}],
            [{"role": "user", "content": "I now live in San Francisco."}],
            [{"role": "user", "content": "I prefer ramen."}],
        ],
        "answer_session_ids": [],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    token = Path(args.token_file).read_text().strip()
    hydra = HydraHTTP(args.endpoint, token)
    health = hydra_health(args.endpoint.split("/v1/")[0])
    if not health.get("ok"):
        raise SystemExit(f"HydraDB health failed: {health}")

    p1 = prepare_typed_case(synthetic_case("STRUCT-001", duplicate_sid=True), "heuristic", None, None)
    p2 = prepare_typed_case(synthetic_case("STRUCT-002", duplicate_sid=False), "heuristic", None, None)

    checks: dict[str, bool] = {}
    checks["duplicate_external_session_id_distinct_vertices"] = p1["vids"][0] != p1["vids"][1]
    checks["supersession_edge_constructed"] = len(p1["rels"].get("SUPERSEDED_BY", [])) >= 1
    checks["contradiction_edge_constructed"] = len(p1["rels"].get("CONTRADICTS", [])) >= 2

    # Context-scoped semantic node IDs: identical text in another case must not
    # silently join the first case's evidence graph.
    entity1 = {str(r["name"]).lower(): int(r["vertex"]) for r in p1["entity_rows"]}
    entity2 = {str(r["name"]).lower(): int(r["vertex"]) for r in p2["entity_rows"]}
    common = sorted(set(entity1) & set(entity2))
    checks["context_scoped_entity_identity"] = bool(common) and all(entity1[k] != entity2[k] for k in common)

    ingest1 = ingest_typed_case(hydra, p1)
    ingest2 = ingest_typed_case(hydra, p2)

    prov1 = provenance_set(hydra, p1["case_id"])
    checks["case_provenance_exact_membership"] = prov1 == set(p1["vids"])

    q = (
        "MATCH (s:Session {id: $seed})-[:ASSERTS]->(f:Fact)-[:SUPERSEDED_BY*1..4]->(cur:Fact)"
        "<-[:ASSERTS]-(v:Session) RETURN DISTINCT v.id AS id LIMIT 20"
    )
    current_ids = set(HydraHTTP.projected_ints(hydra.query(q, {"seed": int(p1["vids"][0])}), "id"))
    checks["supersession_traversal_reaches_current_session"] = int(p1["vids"][1]) in current_ids

    q2 = (
        "MATCH (s:Session {id: $seed})-[:ASSERTS]->(f:Fact)-[:CONTRADICTS]->(g:Fact)"
        "<-[:ASSERTS]-(v:Session) RETURN DISTINCT v.id AS id LIMIT 20"
    )
    contradiction_ids = set(HydraHTTP.projected_ints(hydra.query(q2, {"seed": int(p1["vids"][0])}), "id"))
    checks["contradiction_traversal_reaches_changed_session"] = int(p1["vids"][1]) in contradiction_ids

    passed = all(checks.values())
    result = {
        "schema": "hydradg.best_use_structural_suite.v2",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "hydradb_health": health,
        "ingest": {"STRUCT-001": ingest1, "STRUCT-002": ingest2},
        "identity_rule": "session_occurrence = SHA256(question_id | external_session_id | occurrence_position) truncated to signed-i64-safe positive id",
        "evidence_class": "RECOMPUTED_LIVE_HYDRADB_STRUCTURAL_CONFORMANCE",
        "claim_ceiling": "SYNTHETIC_STRUCTURAL_CONFORMANCE_ONLY",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
    }
    result["result_sha256"] = canonical_sha(result)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
