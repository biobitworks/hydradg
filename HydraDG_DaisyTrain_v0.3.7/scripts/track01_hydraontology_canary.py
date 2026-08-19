#!/usr/bin/env python3
"""Hack Hydra Track 01 — HydraOntology identity-resolution canary.

Fresh Hack Hydra implementation. Uses a deterministic synthetic fixture to test
whether a load-bearing RESOLVES_TO edge changes the evidence set exactly as a
reference Python mapping predicts. No EnterpriseRAG/HERB benchmark result is
claimed by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from best_use_typed_graph import HydraHTTP, hydra_health


def stable_id(kind: str, *parts: object) -> int:
    return int(hashlib.sha256((kind + "|" + "|".join(map(str, parts))).encode()).hexdigest()[:13], 16) or 1


def canonical_sha(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fixture() -> dict:
    return {
        "canonical": "Soham Ratnaparkhi",
        "documents": [
            {"name": "slack-001", "alias": "@soham", "statement": "Project Atlas status is green."},
            {"name": "meeting-002", "alias": "Soham Ratnaparkhi", "statement": "Soham owns Project Atlas."},
            {"name": "ticket-003", "alias": "Alex", "statement": "Alex owns the unrelated ticket."},
        ],
        "states": {
            "reference": {"resolved_aliases": ["@soham", "Soham Ratnaparkhi"]},
            "poison_alias_split": {"resolved_aliases": ["Soham Ratnaparkhi"]},
            "antidote_merge": {"resolved_aliases": ["@soham", "Soham Ratnaparkhi"]},
        },
    }


def expected_docs(fx: dict, state: dict) -> set[str]:
    admitted = set(state["resolved_aliases"])
    return {d["name"] for d in fx["documents"] if d["alias"] in admitted}


def write_state(h: HydraHTTP, state_name: str, fx: dict, state: dict) -> dict:
    canonical_id = stable_id("track01-canonical", state_name, fx["canonical"])
    h.query(
        "UNWIND $rows AS row MERGE (n {id:row.id}) SET n:CanonicalEntity, n.name=row.name, n.state=row.state",
        {"rows": [{"id": canonical_id, "name": fx["canonical"], "state": state_name}]},
    )

    doc_rows, alias_rows = [], []
    for doc in fx["documents"]:
        doc_rows.append({
            "id": stable_id("track01-doc", state_name, doc["name"]),
            "name": doc["name"], "statement": doc["statement"], "state": state_name,
        })
        alias_rows.append({
            "id": stable_id("track01-alias", state_name, doc["alias"]),
            "name": doc["alias"], "state": state_name,
        })
    # Deduplicate aliases while retaining deterministic IDs.
    alias_by_name = {row["name"]: row for row in alias_rows}
    alias_rows = [alias_by_name[name] for name in sorted(alias_by_name)]

    h.query(
        "UNWIND $rows AS row MERGE (n {id:row.id}) SET n:SourceDocument, n.name=row.name, n.statement=row.statement, n.state=row.state",
        {"rows": doc_rows},
    )
    h.query(
        "UNWIND $rows AS row MERGE (n {id:row.id}) SET n:EntityMention, n.name=row.name, n.state=row.state",
        {"rows": alias_rows},
    )

    alias_ids = {row["name"]: row["id"] for row in alias_rows}
    doc_ids = {row["name"]: row["id"] for row in doc_rows}
    mention_rows = [
        {
            "did": doc_ids[doc["name"]],
            "aid": alias_ids[doc["alias"]],
            "rid": stable_id("track01-rel", state_name, "MENTIONS", doc["name"], doc["alias"]),
        }
        for doc in fx["documents"]
    ]
    h.query(
        "UNWIND $rows AS row MATCH (d:SourceDocument {id:row.did}),(a:EntityMention {id:row.aid}) "
        "MERGE (d)-[r:MENTIONS {id:row.rid}]->(a)",
        {"rows": mention_rows},
    )

    resolve_rows = [
        {
            "aid": alias_ids[alias],
            "cid": canonical_id,
            "rid": stable_id("track01-rel", state_name, "RESOLVES_TO", alias, fx["canonical"]),
        }
        for alias in sorted(state["resolved_aliases"])
    ]
    if resolve_rows:
        h.query(
            "UNWIND $rows AS row MATCH (a:EntityMention {id:row.aid}),(c:CanonicalEntity {id:row.cid}) "
            "MERGE (a)-[r:RESOLVES_TO {id:row.rid}]->(c)",
            {"rows": resolve_rows},
        )
    return {
        "canonical_entity": 1,
        "documents": len(doc_rows),
        "aliases": len(alias_rows),
        "MENTIONS": len(mention_rows),
        "RESOLVES_TO": len(resolve_rows),
        "canonical_id": canonical_id,
    }


def observed_docs(h: HydraHTTP, state_name: str, canonical_id: int) -> set[str]:
    q = (
        "MATCH (d:SourceDocument)-[:MENTIONS]->(a:EntityMention)-[:RESOLVES_TO]->(c:CanonicalEntity {id:$canonical}) "
        "WHERE d.state=$state RETURN DISTINCT d.name AS name LIMIT 100"
    )
    return {str(x) for x in HydraHTTP.projected(h.query(q, {"canonical": canonical_id, "state": state_name}), "name")}


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

    fx = fixture()
    rows = []
    checks: dict[str, bool] = {}
    for state_name, state in fx["states"].items():
        expected = expected_docs(fx, state)
        write_receipt = write_state(hydra, state_name, fx, state)
        observed = observed_docs(hydra, state_name, write_receipt["canonical_id"])
        checks[f"{state_name}_exact_evidence_set"] = expected == observed
        rows.append({
            "state": state_name,
            "expected_documents": sorted(expected),
            "hydradb_documents": sorted(observed),
            "exact_set_match": expected == observed,
            "graph_write": write_receipt,
        })

    counts = {row["state"]: len(row["hydradb_documents"]) for row in rows}
    checks["poison_reduces_evidence_set"] = counts["poison_alias_split"] < counts["reference"]
    checks["antidote_restores_evidence_set"] = counts["antidote_merge"] == counts["reference"] == 2

    result = {
        "schema": "hydradg.track01_hydraontology_canary.v1",
        "track": "01_ENTERPRISE_CONTEXT_ONTOLOGY",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "fixture_sha256": canonical_sha(fx),
        "checks": checks,
        "states": rows,
        "hydradb_health": health,
        "mechanism": "RESOLVES_TO_EDGE_ABLATION_AND_RESTORATION",
        "evidence_class": "RECOMPUTED_LIVE_HYDRADB_TRACK01_CANARY",
        "claim_ceiling": "SYNTHETIC_TRACK01_STRUCTURAL_CANARY_ONLY_NOT_ENTERPRISERAG_OR_HERB_PERFORMANCE",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
    }
    result["result_sha256"] = canonical_sha(result)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
