#!/usr/bin/env python3
"""Project the public website Knowledge FCO projection into an isolated HydraDB namespace.

This tool is intentionally NOT called by the parallel-safe Release Watch runner.
It requires --allow-write and refuses shared/default namespaces. Execute only after
Daisy/Antigravity hands Release Watch a stable isolated write boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCHEMA = "hydradg.website_knowledge_hydradb_projection.v1"
CLAIM = "APPLICATION_KNOWLEDGE_FCO_HYDRADB_PROJECTION_ONLY_NOT_SCIENTIFIC_VERIFICATION"


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def numeric(fco_id: str) -> int:
    match = re.fullmatch(r"fco:([0-9a-f]{64})", fco_id)
    if not match:
        raise ValueError(f"not an FCO id: {fco_id}")
    value = int(match.group(1)[:13], 16)
    return value or 1


class Hydra:
    def __init__(self, endpoint: str, token: str, namespace: str):
        self.endpoint = endpoint
        self.token = token
        self.namespace = namespace

    def query(self, query: str, parameters: dict | None = None) -> dict:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps({"cell_id": "cell-0", "query": query, "parameters": parameters or {}}).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.token}",
                "X-Graph-Namespace": self.namespace,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            body = error.read().decode(errors="replace")
            raise RuntimeError(f"HydraDB HTTP {error.code}: {body[:1600]}") from error

    @staticmethod
    def scalar(response: dict, column: str) -> int:
        columns = response.get("columns", [])
        rows = response.get("rows", [])
        if column not in columns or not rows:
            return 0
        value = rows[0][columns.index(column)]
        if isinstance(value, dict) and "value" in value:
            value = value["value"]
        return int(value or 0)


def validate(payload: dict) -> tuple[dict, list[dict]]:
    if payload.get("schema") != "hydradg.website_knowledge_projection.v1":
        raise RuntimeError("unexpected knowledge projection schema")
    root = payload.get("root")
    nodes = payload.get("nodes")
    if not isinstance(root, dict) or not isinstance(nodes, list) or not nodes:
        raise RuntimeError("knowledge projection requires root and non-empty nodes")
    for node in [root, *nodes]:
        if not re.fullmatch(r"fco:[0-9a-f]{64}", str(node.get("id", ""))):
            raise RuntimeError("invalid FCO id in knowledge projection")
        if node.get("object_sha256") != str(node["id"])[4:]:
            raise RuntimeError("FCO id/object_sha256 mismatch")
    return root, nodes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-json", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    parser.add_argument("--token-file", type=Path, default=Path("~/.local/share/hydradg-best-use/hydradb-auth-token").expanduser())
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--allow-write", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not args.allow_write:
        raise SystemExit("STOP: --allow-write is required after a stable Daisy handoff")
    namespace = args.namespace.strip()
    if not namespace or namespace.lower() in {"default", "shared", "prod", "production"}:
        raise SystemExit("STOP: use a dedicated isolated HydraDB namespace")
    if not namespace.startswith("hydradg-release-kb-"):
        raise SystemExit("STOP: namespace must start with hydradg-release-kb-")

    knowledge_path = args.knowledge_json.expanduser().resolve()
    token_path = args.token_file.expanduser().resolve()
    payload = json.loads(knowledge_path.read_text(encoding="utf-8"))
    root, nodes = validate(payload)
    token = token_path.read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit("STOP: empty HydraDB token")

    hydra = Hydra(args.endpoint, token, namespace)
    all_nodes = [root, *nodes]
    for node in all_nodes:
        body = node.get("payload") or {}
        hydra.query(
            "MERGE (n {id:$id}) SET n:HydraDGKnowledgeFCO, n.fco_id=$fco_id, n.object_sha256=$sha, n.fco_type=$type, n.term=$term, n.slug=$slug, n.claim_ceiling=$ceiling",
            {
                "id": numeric(node["id"]),
                "fco_id": node["id"],
                "sha": node["object_sha256"],
                "type": node.get("type", ""),
                "term": str(body.get("term", "")),
                "slug": str(body.get("slug", "")),
                "ceiling": str(body.get("claim_ceiling", CLAIM)),
            },
        )

    root_id = numeric(root["id"])
    for node in nodes:
        hydra.query(
            "MATCH (a {id:$src}),(b {id:$dst}) MERGE (a)-[:APPLICATION_PART_OF_KNOWLEDGE_INDEX]->(b)",
            {"src": numeric(node["id"]), "dst": root_id},
        )

    observed_nodes = Hydra.scalar(hydra.query("MATCH (n:HydraDGKnowledgeFCO) RETURN count(n) AS c"), "c")
    observed_edges = Hydra.scalar(hydra.query("MATCH (:HydraDGKnowledgeFCO)-[r:APPLICATION_PART_OF_KNOWLEDGE_INDEX]->(:HydraDGKnowledgeFCO) RETURN count(r) AS c"), "c")
    root_rows = hydra.query("MATCH (n:HydraDGKnowledgeFCO {fco_id:$id}) RETURN count(n) AS c", {"id": root["id"]})
    root_observed = Hydra.scalar(root_rows, "c")

    expected_nodes = len(all_nodes)
    expected_edges = len(nodes)
    passed = observed_nodes == expected_nodes and observed_edges == expected_edges and root_observed == 1
    science = {
        "namespace": namespace,
        "knowledge_json_sha256": sha_file(knowledge_path),
        "knowledge_root_fco_id": root["id"],
        "objects_expected": expected_nodes,
        "objects_observed": observed_nodes,
        "edges_expected": expected_edges,
        "edges_observed": observed_edges,
        "root_readback_count": root_observed,
        "claim_ceiling": CLAIM,
    }
    receipt = {
        "schema": SCHEMA,
        **science,
        "status": "PASS" if passed else "FAIL",
        "result_sha256": sha_bytes(canonical(science)),
        "evidence_class": "RECOMPUTED_ISOLATED_HYDRADB_APPLICATION_KNOWLEDGE_PROJECTION",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
        "timestamp_unix": int(time.time()),
    }
    out = args.out.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(f"KNOWLEDGE_HYDRADB_PROJECTION={receipt['status']}")
    print(f"RECEIPT={out}")
    print(f"RECEIPT_FILE_SHA256={sha_file(out)}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
