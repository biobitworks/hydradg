#!/usr/bin/env python3
"""Execute one live Track 03 reference -> normal -> poison -> antidote path.

This is a post-August-12 Hack Hydra release test. It verifies live HydraDB state
transition/custody mechanics. Retrieval responses are retained as observations;
the gate does not require a positive retrieval effect because the executed
full500 ablation retained a negative/neutral retrieval result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

from best_use_typed_graph import HydraHTTP


def canonical_hash(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def request_json(url: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="GET" if body is None else "POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {detail[:2000]}") from exc


def projected_rows(response: dict) -> list[dict]:
    columns = response.get("columns", [])
    out = []
    for row in response.get("rows", []):
        decoded = {}
        for index, column in enumerate(columns):
            if index >= len(row):
                continue
            value = row[index]
            decoded[column] = value.get("value") if isinstance(value, dict) and "value" in value else value
        out.append(decoded)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:8787")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    server = args.server.rstrip("/")
    hydra = HydraHTTP(args.endpoint, Path(args.token_file).read_text().strip())

    health = request_json(f"{server}/health")
    cases = request_json(f"{server}/cases?limit=100").get("cases", [])
    if not cases:
        raise SystemExit("No cases returned by Best Use server")

    ordered = sorted(
        cases,
        key=lambda item: (0 if "update" in str(item.get("question_type", "")).lower() else 1, str(item.get("question_id", ""))),
    )

    loaded = None
    selected_case = None
    for case in ordered:
        qid = str(case.get("question_id", ""))
        candidate = request_json(f"{server}/case/load", {"question_id": qid, "extractor": "heuristic"})
        if candidate.get("facts"):
            selected_case = case
            loaded = candidate
            break
    if loaded is None or selected_case is None:
        raise SystemExit("No returned case produced a heuristic Fact for the golden path")

    qid = str(selected_case["question_id"])
    source_fact = loaded["facts"][0]
    source_vertex = int(source_fact["vertex"])
    original_object = str(source_fact.get("object", ""))
    subject = str(source_fact.get("subject", ""))
    predicate = str(source_fact.get("predicate", ""))
    if not original_object:
        raise SystemExit("Selected source Fact has an empty object")

    baseline_retrieval = request_json(
        f"{server}/retrieve",
        {"question_id": qid, "question": "", "method": "D", "k": 5, "extractor": "heuristic"},
    )

    normal = request_json(
        f"{server}/live/perturb",
        {
            "question_id": qid,
            "target_fact_vertex": source_vertex,
            "object": original_object,
            "identity_class": "SELF",
            "safety_class": "SAFE",
            "extractor": "heuristic",
        },
    )
    normal_vertex = int(normal["after"]["vertex"])

    poison_object = f"POISON::{original_object}"[:160]
    poison = request_json(
        f"{server}/live/perturb",
        {
            "question_id": qid,
            "target_fact_vertex": normal_vertex,
            "object": poison_object,
            "identity_class": "NONSELF",
            "safety_class": "NONSAFE",
            "extractor": "heuristic",
        },
    )
    poison_vertex = int(poison["after"]["vertex"])

    poisoned_retrieval = request_json(
        f"{server}/retrieve",
        {"question_id": qid, "question": "", "method": "D", "k": 5, "extractor": "heuristic"},
    )

    antidote = request_json(
        f"{server}/live/perturb",
        {
            "question_id": qid,
            "target_fact_vertex": poison_vertex,
            "object": original_object,
            "identity_class": "NONSELF",
            "safety_class": "SAFE",
            "extractor": "heuristic",
        },
    )
    antidote_vertex = int(antidote["after"]["vertex"])

    restored_retrieval = request_json(
        f"{server}/retrieve",
        {"question_id": qid, "question": "", "method": "D", "k": 5, "extractor": "heuristic"},
    )

    fact_response = hydra.query(
        "MATCH (f:Fact) WHERE f.qid=$qid AND f.subject=$subject AND f.predicate=$predicate "
        "RETURN f.id AS id, f.object AS object, f.position AS position, f.evidence_class AS evidence_class LIMIT 100",
        {"qid": qid, "subject": subject, "predicate": predicate},
    )
    edge_response = hydra.query(
        "MATCH (a:Fact)-[:SUPERSEDED_BY]->(b:Fact) WHERE a.qid=$qid AND b.qid=$qid "
        "RETURN a.id AS source, b.id AS target LIMIT 100",
        {"qid": qid},
    )
    fact_rows = projected_rows(fact_response)
    edge_rows = projected_rows(edge_response)
    fact_by_id = {int(row["id"]): row for row in fact_rows if row.get("id") is not None}
    edges = {(int(row["source"]), int(row["target"])) for row in edge_rows if row.get("source") is not None and row.get("target") is not None}

    expected_edges = {
        (source_vertex, normal_vertex),
        (normal_vertex, poison_vertex),
        (poison_vertex, antidote_vertex),
    }
    checks = {
        "server_health_hydradb": bool(health.get("hydradb", {}).get("ok")),
        "normal_targets_source": int(normal.get("before", {}).get("vertex", -1)) == source_vertex,
        "poison_targets_live_normal": int(poison.get("before", {}).get("vertex", -1)) == normal_vertex,
        "antidote_targets_live_poison": int(antidote.get("before", {}).get("vertex", -1)) == poison_vertex,
        "normal_preserves_object": str(normal.get("after", {}).get("object")) == original_object,
        "poison_changes_object": str(poison.get("after", {}).get("object")) != original_object,
        "antidote_restores_object": str(antidote.get("after", {}).get("object")) == original_object,
        "normal_admitted_safe": normal.get("anticube", {}).get("decision") == "ADMIT",
        "poison_quarantined": poison.get("anticube", {}).get("decision") == "QUARANTINE",
        "antidote_admitted_safe": antidote.get("anticube", {}).get("decision") == "ADMIT",
        "three_supersession_edges_present": expected_edges.issubset(edges),
        "antidote_fact_persisted": antidote_vertex in fact_by_id,
        "antidote_persisted_original_object": str(fact_by_id.get(antidote_vertex, {}).get("object")) == original_object,
    }

    result = {
        "schema": "hydradg.track03_live_golden_path.v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "question_id": qid,
        "question_type": selected_case.get("question_type"),
        "source_fact": source_fact,
        "checks": checks,
        "vertices": {
            "source": source_vertex,
            "normal": normal_vertex,
            "poison": poison_vertex,
            "antidote": antidote_vertex,
        },
        "objects": {
            "reference": original_object,
            "poison": poison_object,
            "restored": str(antidote.get("after", {}).get("object", "")),
        },
        "live_events": {"normal": normal, "poison": poison, "antidote": antidote},
        "hydradb_facts": fact_rows,
        "hydradb_supersession_edges": edge_rows,
        "retrieval_observation": {
            "baseline_sha256": canonical_hash(baseline_retrieval),
            "poison_sha256": canonical_hash(poisoned_retrieval),
            "restored_sha256": canonical_hash(restored_retrieval),
            "positive_retrieval_effect_required_for_gate": False,
            "reason": "full500 retained NO_POSITIVE_HIT_RATE_SIGNAL; this gate establishes live state/custody mechanics, not retrieval superiority",
        },
        "evidence_class": "RECOMPUTED_LIVE_HYDRADB_TRACK03_STATE_TRANSITION",
        "claim_ceiling": "LIVE_HYDRADB_FCG_GOLDEN_PATH_STATE_TRANSITION_ONLY_NOT_RETRIEVAL_SUPERIORITY",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
    }
    result["result_sha256"] = canonical_hash(result)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
