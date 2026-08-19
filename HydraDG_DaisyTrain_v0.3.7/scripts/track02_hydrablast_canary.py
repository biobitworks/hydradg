#!/usr/bin/env python3
"""Hack Hydra Track 02A — HydraBlast supply-chain blast-radius canary.

Fresh Hack Hydra implementation. The fixture is synthetic and deterministic.
It compares a Python reverse-transitive-closure oracle with live pinned HydraDB
using only query shapes supported by the current HydraDB runtime.

No real npm vulnerability or production exposure claim is made here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

from best_use_typed_graph import HydraHTTP, hydra_health


def stable_id(kind: str, *parts: object) -> int:
    raw = kind + "|" + "|".join(map(str, parts))
    return int(hashlib.sha256(raw.encode()).hexdigest()[:13], 16) or 1


def sha256_json(obj: object) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def fixture() -> dict:
    return {
        "services": ["service-alpha", "service-beta"],
        "roots": {"service-alpha": "app-a@1.0.0", "service-beta": "app-b@1.0.0"},
        "bad": "transit@3.1.0",
        "fixed": "transit@3.1.1",
        "advisory": "HYDRA-CANARY-001",
        "states": {
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
        },
    }


def python_exposed_services(state: dict, roots: dict[str, str]) -> set[str]:
    affected = set(state["affected"])
    if not affected:
        return set()
    reverse: dict[str, set[str]] = defaultdict(set)
    for parent, children in state["deps"].items():
        for child in children:
            reverse[child].add(parent)
    impacted = set(affected)
    queue = deque(sorted(affected))
    while queue:
        child = queue.popleft()
        for parent in sorted(reverse.get(child, set())):
            if parent not in impacted:
                impacted.add(parent)
                queue.append(parent)
    return {service for service, root in roots.items() if root in impacted}


def write_state(h: HydraHTTP, state_name: str, spec: dict, fx: dict) -> dict:
    packages = {fx["bad"], fx["fixed"], *fx["roots"].values()}
    for parent, children in spec["deps"].items():
        packages.add(parent)
        packages.update(children)

    services = [{"id": stable_id("t2-service", state_name, x), "name": x, "state": state_name} for x in fx["services"]]
    locks = [{"id": stable_id("t2-lock", state_name, x), "name": x, "state": state_name} for x in fx["services"]]
    versions = [{"id": stable_id("t2-version", state_name, x), "name": x, "state": state_name} for x in sorted(packages)]
    advisory = {"id": stable_id("t2-advisory", state_name, fx["advisory"]), "name": fx["advisory"], "state": state_name}

    h.query("UNWIND $rows AS row MERGE (n {id:row.id}) SET n:Service,n.name=row.name,n.state=row.state", {"rows": services})
    h.query("UNWIND $rows AS row MERGE (n {id:row.id}) SET n:Lockfile,n.name=row.name,n.state=row.state", {"rows": locks})
    h.query("UNWIND $rows AS row MERGE (n {id:row.id}) SET n:PackageVersion,n.name=row.name,n.state=row.state", {"rows": versions})
    h.query("UNWIND $rows AS row MERGE (n {id:row.id}) SET n:Advisory,n.name=row.name,n.state=row.state", {"rows": [advisory]})

    sid = {x["name"]: x["id"] for x in services}
    lid = {x["name"]: x["id"] for x in locks}
    vid = {x["name"]: x["id"] for x in versions}

    uses = [{"s": sid[s], "l": lid[s], "r": stable_id("t2-rel", state_name, "USES", s)} for s in fx["services"]]
    h.query("UNWIND $rows AS row MATCH (a:Service {id:row.s}),(b:Lockfile {id:row.l}) MERGE (a)-[r:USES {id:row.r}]->(b)", {"rows": uses})

    resolved = [{"l": lid[s], "p": vid[root], "r": stable_id("t2-rel", state_name, "RESOLVED", s, root)} for s, root in sorted(fx["roots"].items())]
    h.query("UNWIND $rows AS row MATCH (a:Lockfile {id:row.l}),(b:PackageVersion {id:row.p}) MERGE (a)-[r:RESOLVED {id:row.r}]->(b)", {"rows": resolved})

    deps = []
    for parent, children in sorted(spec["deps"].items()):
        for child in sorted(children):
            deps.append({"p": vid[parent], "c": vid[child], "r": stable_id("t2-rel", state_name, "DEPENDS_ON", parent, child)})
    if deps:
        h.query("UNWIND $rows AS row MATCH (a:PackageVersion {id:row.p}),(b:PackageVersion {id:row.c}) MERGE (a)-[r:DEPENDS_ON {id:row.r}]->(b)", {"rows": deps})

    affects = [{"a": advisory["id"], "p": vid[pkg], "r": stable_id("t2-rel", state_name, "AFFECTS", fx["advisory"], pkg)} for pkg in sorted(spec["affected"])]
    if affects:
        h.query("UNWIND $rows AS row MATCH (a:Advisory {id:row.a}),(b:PackageVersion {id:row.p}) MERGE (a)-[r:AFFECTS {id:row.r}]->(b)", {"rows": affects})

    return {
        "advisory_id": advisory["id"],
        "bad_id": vid[fx["bad"]],
        "package_ids": vid,
        "node_counts": {"services": len(services), "lockfiles": len(locks), "package_versions": len(versions), "advisories": 1},
        "edge_counts": {"USES": len(uses), "RESOLVED": len(resolved), "DEPENDS_ON": len(deps), "AFFECTS": len(affects)},
    }


def hydra_exposed_services(h: HydraHTTP, state_name: str, spec: dict, written: dict, max_depth: int = 8) -> tuple[set[str], dict]:
    if not spec["affected"]:
        return set(), {"query_steps": 0, "impacted_version_ids": []}

    # First establish that the declared advisory actually points at the fixed
    # affected package ID in this state.
    direct = h.query(
        "MATCH (a:Advisory {id:$aid})-[:AFFECTS]->(p:PackageVersion {id:$pid}) RETURN p.id AS id LIMIT 2",
        {"aid": written["advisory_id"], "pid": written["bad_id"]},
    )
    if written["bad_id"] not in {int(x) for x in HydraHTTP.projected(direct, "id")}:
        return set(), {"query_steps": 1, "error": "AFFECTS_EDGE_NOT_OBSERVED", "impacted_version_ids": []}

    # Pinned HydraDB currently requires a fixed source ID for variable-length
    # MATCH. Use explicit one-hop reverse traversal instead. This remains a
    # graph-native traversal and preserves the exact runtime capability boundary.
    impacted = {written["bad_id"]}
    frontier = {written["bad_id"]}
    query_steps = 1
    for _depth in range(max_depth):
        next_frontier: set[int] = set()
        for child_id in sorted(frontier):
            response = h.query(
                "MATCH (parent:PackageVersion)-[:DEPENDS_ON]->(child:PackageVersion {id:$child}) WHERE parent.state=$state RETURN DISTINCT parent.id AS id LIMIT 100",
                {"child": child_id, "state": state_name},
            )
            query_steps += 1
            for value in HydraHTTP.projected(response, "id"):
                parent_id = int(value)
                if parent_id not in impacted:
                    impacted.add(parent_id)
                    next_frontier.add(parent_id)
        if not next_frontier:
            break
        frontier = next_frontier

    exposed: set[str] = set()
    for version_id in sorted(impacted):
        response = h.query(
            "MATCH (l:Lockfile)-[:RESOLVED]->(p:PackageVersion {id:$pid}) MATCH (s:Service)-[:USES]->(l) WHERE s.state=$state RETURN DISTINCT s.name AS name LIMIT 100",
            {"pid": version_id, "state": state_name},
        )
        query_steps += 1
        exposed.update(str(x) for x in HydraHTTP.projected(response, "name"))

    return exposed, {"query_steps": query_steps, "impacted_version_ids": sorted(impacted)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    hydra = HydraHTTP(args.endpoint, Path(args.token_file).read_text().strip())
    health = hydra_health(args.endpoint.split("/v1/")[0])
    if not health.get("ok"):
        raise SystemExit(f"HydraDB health failed: {health}")

    fx = fixture()
    checks: dict[str, bool] = {}
    rows = []
    for state_name, spec in fx["states"].items():
        expected = python_exposed_services(spec, fx["roots"])
        written = write_state(hydra, state_name, spec, fx)
        observed, traversal = hydra_exposed_services(hydra, state_name, spec, written)
        checks[f"{state_name}_exact_set_match"] = observed == expected
        rows.append({
            "state": state_name,
            "reference_exposed_services": sorted(expected),
            "hydradb_exposed_services": sorted(observed),
            "exact_set_match": observed == expected,
            "graph_write": written,
            "hydradb_traversal": traversal,
        })

    counts = {row["state"]: len(row["hydradb_exposed_services"]) for row in rows}
    checks.update({
        "reference_expected_count": counts["reference"] == 0,
        "poison_expected_count": counts["poison"] == 2,
        "partial_repair_expected_count": counts["partial_repair"] == 1,
        "full_repair_expected_count": counts["full_repair"] == 0,
        "poison_increases_exposure": counts["poison"] > counts["reference"],
        "partial_repair_reduces_exposure": counts["partial_repair"] < counts["poison"],
        "full_repair_removes_exposure": counts["full_repair"] == 0,
    })

    result = {
        "schema": "hydradg.track02_hydrablast_canary.v1",
        "track": "02A_SUPPLY_CHAIN_BLAST_RADIUS",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "fixture_sha256": sha256_json(fx),
        "checks": checks,
        "states": rows,
        "hydradb_health": health,
        "reference_algorithm": "DETERMINISTIC_PYTHON_REVERSE_TRANSITIVE_CLOSURE",
        "hydradb_algorithm": "ITERATIVE_OPEN_CYPHER_ONE_HOP_REVERSE_DEPENDENCY_TRAVERSAL",
        "runtime_capability_boundary": "VARIABLE_LENGTH_MATCH_REQUIRES_FIXED_SOURCE_ID_AT_PINNED_HYDRADB_REVISION",
        "anticube_interpretation": "partial repair removes one load-bearing dependency path; exposed set must shrink from two services to one",
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
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
