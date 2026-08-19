#!/usr/bin/env python3
"""Hack Hydra Track 02A — HydraBlast supply-chain blast-radius canary.

Fresh Hack Hydra implementation. This is deliberately a synthetic structural
canary: it proves the graph/write/traversal/reference-comparison mechanism before
we admit real npm/deps.dev/OSV data.

Evidence boundaries:
- fixture topology: deterministic synthetic test fixture
- Python reverse closure: deterministic reference computation
- HydraDB traversal: recomputed live database result
- no real vulnerability/exposure claim is made by this script
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

from best_use_typed_graph import HydraHTTP, hydra_health


def sha256_json(obj: object) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def stable_id(kind: str, *parts: object) -> int:
    raw = kind + "|" + "|".join(map(str, parts))
    return int(hashlib.sha256(raw.encode()).hexdigest()[:13], 16) or 1


def fixture() -> dict:
    base = {
        "services": ["service-alpha", "service-beta"],
        "roots": {"service-alpha": "app-a@1.0.0", "service-beta": "app-b@1.0.0"},
        "bad": "transit@3.1.0",
        "fixed": "transit@3.1.1",
        "advisory": "HYDRA-CANARY-001",
    }
    states = {
        "reference": {
            "deps": {
                "app-a@1.0.0": ["shared@2.0.0"],
                "shared@2.0.0": ["transit@3.1.0"],
                "app-b@1.0.0": ["transit@3.1.0"],
            },
            "affected": [],
        },
        "poison": {
            "deps": {
                "app-a@1.0.0": ["shared@2.0.0"],
                "shared@2.0.0": ["transit@3.1.0"],
                "app-b@1.0.0": ["transit@3.1.0"],
            },
            "affected": ["transit@3.1.0"],
        },
        "partial_repair": {
            "deps": {
                "app-a@1.0.0": ["shared@2.0.0"],
                "shared@2.0.0": ["transit@3.1.0"],
                "app-b@1.0.0": ["transit@3.1.1"],
            },
            "affected": ["transit@3.1.0"],
        },
        "full_repair": {
            "deps": {
                "app-a@1.0.0": ["shared@2.0.0"],
                "shared@2.0.0": ["transit@3.1.1"],
                "app-b@1.0.0": ["transit@3.1.1"],
            },
            "affected": ["transit@3.1.0"],
        },
    }
    return {**base, "states": states}


def reference_exposed_services(state: dict, roots: dict[str, str]) -> set[str]:
    affected = set(state.get("affected", []))
    if not affected:
        return set()

    reverse: dict[str, set[str]] = defaultdict(set)
    for parent, children in state["deps"].items():
        for child in children:
            reverse[child].add(parent)

    impacted_versions = set(affected)
    queue: deque[str] = deque(sorted(affected))
    while queue:
        child = queue.popleft()
        for parent in sorted(reverse.get(child, set())):
            if parent not in impacted_versions:
                impacted_versions.add(parent)
                queue.append(parent)

    return {service for service, root in roots.items() if root in impacted_versions}


def write_state(hydra: HydraHTTP, state_name: str, spec: dict, full: dict) -> dict:
    packages = set(spec["affected"])
    packages.add(full["bad"])
    packages.add(full["fixed"])
    packages.update(full["roots"].values())
    for parent, children in spec["deps"].items():
        packages.add(parent)
        packages.update(children)

    service_rows = []
    lock_rows = []
    package_rows = []
    for service in full["services"]:
        service_rows.append({
            "id": stable_id("track02-service", state_name, service),
            "name": service,
            "state": state_name,
        })
        lock_rows.append({
            "id": stable_id("track02-lock", state_name, service),
            "name": f"{service}.lock",
            "state": state_name,
        })
    for package in sorted(packages):
        package_rows.append({
            "id": stable_id("track02-package-version", state_name, package),
            "name": package,
            "state": state_name,
        })

    advisory_id = stable_id("track02-advisory", state_name, full["advisory"])
    hydra.query(
        "UNWIND $rows AS row MERGE (n {id: row.id}) SET n:Service, n.name=row.name, n.state=row.state",
        {"rows": service_rows},
    )
    hydra.query(
        "UNWIND $rows AS row MERGE (n {id: row.id}) SET n:Lockfile, n.name=row.name, n.state=row.state",
        {"rows": lock_rows},
    )
    hydra.query(
        "UNWIND $rows AS row MERGE (n {id: row.id}) SET n:PackageVersion, n.name=row.name, n.state=row.state",
        {"rows": package_rows},
    )
    hydra.query(
        "UNWIND $rows AS row MERGE (a {id: row.id}) SET a:Advisory, a.name=row.name, a.state=row.state",
        {"rows": [{"id": advisory_id, "name": full["advisory"], "state": state_name}]},
    )

    ids = {row["name"]: row["id"] for row in package_rows}
    service_ids = {row["name"]: row["id"] for row in service_rows}
    lock_ids = {row["name"].removesuffix(".lock"): row["id"] for row in lock_rows}

    rel_rows = []
    for service, root in sorted(full["roots"].items()):
        rel_rows.append({
            "sid": service_ids[service],
            "lid": lock_ids[service],
            "rid": stable_id("track02-rel", state_name, "USES", service),
        })
    hydra.query(
        "UNWIND $rows AS row MATCH (s:Service {id:row.sid}),(l:Lockfile {id:row.lid}) "
        "MERGE (s)-[r:USES {id:row.rid}]->(l)",
        {"rows": rel_rows},
    )

    rel_rows = []
    for service, root in sorted(full["roots"].items()):
        rel_rows.append({
            "lid": lock_ids[service],
            "pid": ids[root],
            "rid": stable_id("track02-rel", state_name, "RESOLVED", service, root),
        })
    hydra.query(
        "UNWIND $rows AS row MATCH (l:Lockfile {id:row.lid}),(p:PackageVersion {id:row.pid}) "
        "MERGE (l)-[r:RESOLVED {id:row.rid}]->(p)",
        {"rows": rel_rows},
    )

    rel_rows = []
    for parent, children in sorted(spec["deps"].items()):
        for child in sorted(children):
            rel_rows.append({
                "pid": ids[parent],
                "cid": ids[child],
                "rid": stable_id("track02-rel", state_name, "DEPENDS_ON", parent, child),
            })
    if rel_rows:
        hydra.query(
            "UNWIND $rows AS row MATCH (p:PackageVersion {id:row.pid}),(c:PackageVersion {id:row.cid}) "
            "MERGE (p)-[r:DEPENDS_ON {id:row.rid}]->(c)",
            {"rows": rel_rows},
        )

    affect_rows = [
        {
            "aid": advisory_id,
            "pid": ids[pkg],
            "rid": stable_id("track02-rel", state_name, "AFFECTS", full["advisory"], pkg),
        }
        for pkg in sorted(spec["affected"])
    ]
    if affect_rows:
        hydra.query(
            "UNWIND $rows AS row MATCH (a:Advisory {id:row.aid}),(p:PackageVersion {id:row.pid}) "
            "MERGE (a)-[r:AFFECTS {id:row.rid}]->(p)",
            {"rows": affect_rows},
        )

    return {
        "advisory_id": advisory_id,
        "service_ids": service_ids,
        "package_ids": ids,
        "node_counts": {
            "services": len(service_rows),
            "lockfiles": len(lock_rows),
            "package_versions": len(package_rows),
            "advisories": 1,
        },
        "edge_counts": {
            "USES": len(full["services"]),
            "RESOLVED": len(full["services"]),
            "DEPENDS_ON": sum(len(v) for v in spec["deps"].values()),
            "AFFECTS": len(affect_rows),
        },
    }


def hydra_exposed_services(hydra: HydraHTTP, state_name: str, advisory_id: int) -> set[str]:
    query = (
        "MATCH (a:Advisory {id:$advisory})-[:AFFECTS]->(bad:PackageVersion) "
        "MATCH (root:PackageVersion)-[:DEPENDS_ON*1..8]->(bad) "
        "MATCH (l:Lockfile)-[:RESOLVED]->(root) "
        "MATCH (s:Service)-[:USES]->(l) "
        "WHERE s.state=$state "
        "RETURN DISTINCT s.name AS name LIMIT 100"
    )
    return {str(x) for x in HydraHTTP.projected(hydra.query(query, {"advisory": advisory_id, "state": state_name}), "name")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    token = Path(args.token_file).read_text().strip()
    hydra = HydraHTTP(args.endpoint, token)
    health = hydra_health(args.endpoint.split("/v1/")[0])
    if not health.get("ok"):
        raise SystemExit(f"HydraDB health failed: {health}")

    fx = fixture()
    fixture_sha = sha256_json(fx)
    rows = []
    checks: dict[str, bool] = {}

    for state_name, spec in fx["states"].items():
        reference = reference_exposed_services(spec, fx["roots"])
        written = write_state(hydra, state_name, spec, fx)
        observed = hydra_exposed_services(hydra, state_name, written["advisory_id"])
        exact = observed == reference
        checks[f"{state_name}_exact_set_match"] = exact
        rows.append({
            "state": state_name,
            "reference_exposed_services": sorted(reference),
            "hydradb_exposed_services": sorted(observed),
            "exact_set_match": exact,
            "graph_write": written,
        })

    expected_counts = {
        "reference": 0,
        "poison": 2,
        "partial_repair": 1,
        "full_repair": 0,
    }
    for row in rows:
        checks[f"{row['state']}_expected_count"] = len(row["hydradb_exposed_services"]) == expected_counts[row["state"]]

    checks["poison_increases_exposure"] = (
        len(next(r for r in rows if r["state"] == "poison")["hydradb_exposed_services"])
        > len(next(r for r in rows if r["state"] == "reference")["hydradb_exposed_services"])
    )
    checks["partial_repair_reduces_exposure"] = (
        len(next(r for r in rows if r["state"] == "partial_repair")["hydradb_exposed_services"])
        < len(next(r for r in rows if r["state"] == "poison")["hydradb_exposed_services"])
    )
    checks["full_repair_removes_exposure"] = (
        len(next(r for r in rows if r["state"] == "full_repair")["hydradb_exposed_services"]) == 0
    )

    passed = all(checks.values())
    result = {
        "schema": "hydradg.track02_hydrablast_canary.v1",
        "track": "02A_SUPPLY_CHAIN_BLAST_RADIUS",
        "status": "PASS" if passed else "FAIL",
        "fixture_sha256": fixture_sha,
        "checks": checks,
        "states": rows,
        "hydradb_health": health,
        "reference_algorithm": "DETERMINISTIC_PYTHON_REVERSE_TRANSITIVE_CLOSURE",
        "hydradb_algorithm": "OPEN_CYPHER_REVERSE_DEPENDENCY_TRAVERSAL",
        "anticube_interpretation": "partial_repair removes one load-bearing DEPENDS_ON path; exposed set must shrink from two services to one",
        "evidence_class": "RECOMPUTED_LIVE_HYDRADB_TRACK02_CANARY",
        "claim_ceiling": "SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY_NOT_REAL_NPM_EXPOSURE",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
    }
    result["result_sha256"] = sha256_json(result)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
