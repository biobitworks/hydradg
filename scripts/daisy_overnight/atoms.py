"""Frozen admissible FCO atom library for Daisy falsification experiments."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTEXT_CHAR_BUDGET = 8000
LABEL_LEAK_FAMILIES = {"E05"}  # never inject ground-truth ranking atoms


def load_admissible_atoms(repo: Path) -> list[dict[str, Any]]:
    rubric = json.loads((repo / "eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json").read_text())
    poison = json.loads((repo / "eval/ic_failure_learning_20260827/README_POISON_FCO.json").read_text())
    track = rubric["official_rubric"]["tracks"]["track01_external"]
    criteria = track["criteria"]

    atoms: list[dict[str, Any]] = [
        {
            "fco_id": "FCO_RUBRIC_TRACK01",
            "kind": "RequirementFCO",
            "families": ["E01", "E02", "E03", "E04", "E06", "E07"],
            "priority": 10,
            "prose": (
                f"IC Track01 question: {track['question']} "
                f"criteria weights: cold_start_success max {criteria['cold_start_success']['max']}, "
                f"it_runs gate required, demo max {criteria['demo']['max']}, "
                f"surface_quality max {criteria['surface_quality']['max']}."
            ),
            "structured": {
                "node_id": "FCO_RUBRIC_TRACK01",
                "kind": "RequirementFCO",
                "edges": [{"rel": "REQUIRES", "dst": "FCO_SUBMISSION_FIELDS"}],
                "payload": criteria,
            },
        },
        {
            "fco_id": "FCO_SUBMISSION_FIELDS",
            "kind": "RequirementFCO",
            "families": ["E01", "E03", "E06"],
            "priority": 20,
            "prose": (
                "Submission fields: title, blurb, repo_url, demo_url, agent_surface, folder_id. "
                "GATE: folder_id must be populated with vault before submit; vault required for media evidence."
            ),
            "structured": {
                "node_id": "FCO_SUBMISSION_FIELDS",
                "kind": "RequirementFCO",
                "edges": [{"rel": "GATE_BEFORE", "dst": "FCO_VAULT_BEFORE_SUBMIT"}],
                "fields": ["title", "blurb", "repo_url", "demo_url", "agent_surface", "folder_id"],
            },
        },
        {
            "fco_id": "FCO_VAULT_BEFORE_SUBMIT",
            "kind": "FailureRelationshipFCO",
            "families": ["E01", "E03", "E04", "E06"],
            "priority": 30,
            "prose": (
                "Failure pattern: submitting with folder_id=null while media exists off-platform "
                "creates judge-visible evidence gap. Vault population must precede ic_hack_submit."
            ),
            "structured": {
                "node_id": "FCO_VAULT_BEFORE_SUBMIT",
                "kind": "FailureRelationshipFCO",
                "edges": [
                    {"rel": "PREVENTS", "dst": "FCO_MEDIA_NOT_IN_VAULT_CLASS"},
                    {"rel": "REQUIRED_BEFORE", "dst": "FCO_SUBMIT_ACTION"},
                ],
            },
        },
        {
            "fco_id": "FCO_MEDIA_NOT_IN_VAULT_CLASS",
            "kind": "FailureClassFCO",
            "families": ["E01", "E03", "E06"],
            "priority": 31,
            "prose": (
                "Failure class: media/screenshot/video/contact-sheet not in vault at submit time. "
                "Remediation: ic_folder_create, ic_files_put, record folder_id before submit."
            ),
            "structured": {
                "node_id": "FCO_MEDIA_NOT_IN_VAULT_CLASS",
                "kind": "FailureClassFCO",
                "edges": [{"rel": "DIVERGED_AT", "dst": "FCO_VAULT_BEFORE_SUBMIT"}],
            },
        },
        {
            "fco_id": "FCO_README_POISON",
            "kind": "ContradictionFCO",
            "families": ["E02", "E07"],
            "priority": 40,
            "prose": (
                f"README poison: presents {poison['presents_project_as']}; "
                f"conflicts with {poison['conflicts_with']}; "
                f"anticube={poison['anticube_classification']}."
            ),
            "structured": {
                "node_id": "FCO_README_POISON",
                "kind": "ContradictionFCO",
                "payload": poison,
                "edges": [{"rel": "CONTRADICTS", "dst": "FCO_ORIGIN_DISCLOSURE"}],
            },
        },
        {
            "fco_id": "FCO_ORIGIN_DISCLOSURE",
            "kind": "RequirementFCO",
            "families": ["E02", "E03", "E06", "E07"],
            "priority": 50,
            "prose": (
                "Origin disclosure required: branch-qualified repo URL, origin dates/SHAs, "
                "what_is_new_vs_prior_work in vault, 02_WHAT_IS_NEW_VS_PRIOR_WORK.md."
            ),
            "structured": {
                "node_id": "FCO_ORIGIN_DISCLOSURE",
                "kind": "RequirementFCO",
                "edges": [{"rel": "REQUIRES", "dst": "FCO_VAULT_BEFORE_SUBMIT"}],
            },
        },
        {
            "fco_id": "FCO_PROTOCOL_ORDER",
            "kind": "GovernedProtocolFCO",
            "families": ["E04", "E06"],
            "priority": 60,
            "prose": (
                "Governed submission pipeline order: EVENT_CONTEXT → RUBRIC → BUILD_PLAN → "
                "EVIDENCE_GRAPH → BUILD/TEST → MEDIA_CAPTURE → ORIGIN → RED_TEAM → "
                "SCORECARD → VAULT_BUNDLE → SUBMIT. Hard gate: no submit while judge evidence unsurfaced."
            ),
            "structured": {
                "node_id": "FCO_PROTOCOL_ORDER",
                "kind": "GovernedProtocolFCO",
                "ordered_phases": [
                    "EVENT_CONTEXT", "RUBRIC", "BUILD_PLAN", "EVIDENCE_GRAPH", "BUILD",
                    "MEDIA_CAPTURE", "ORIGIN", "RED_TEAM", "SCORECARD", "VAULT", "SUBMIT",
                ],
                "edges": [{"rel": "ORDERS", "dst": "FCO_VAULT_BEFORE_SUBMIT"}],
            },
        },
        {
            "fco_id": "FCO_RED_TEAM_90S",
            "kind": "RequirementFCO",
            "families": ["E03", "E06"],
            "priority": 70,
            "prose": "RED_TEAM 90-second judge gate mandatory before submit; reuse skeptic and agent-native meta gates.",
            "structured": {
                "node_id": "FCO_RED_TEAM_90S",
                "kind": "RequirementFCO",
                "edges": [{"rel": "GATE_BEFORE", "dst": "FCO_SUBMIT_ACTION"}],
            },
        },
        {
            "fco_id": "FCO_COLD_START",
            "kind": "RequirementFCO",
            "families": ["E01", "E04"],
            "priority": 80,
            "prose": (
                "Cold-start path: discover via /.well-known/ai-agent.json or start_here, "
                "authenticate, bounded run action, verify receipt/status before consequential submit."
            ),
            "structured": {
                "node_id": "FCO_COLD_START",
                "kind": "RequirementFCO",
                "edges": [{"rel": "ENABLES", "dst": "FCO_SUBMIT_ACTION"}],
            },
        },
        {
            "fco_id": "FCO_STAGE2_NULL",
            "kind": "NegativeEvidenceFCO",
            "families": ["E01", "E02", "E03", "E04", "E05", "E06", "E07"],
            "priority": 5,
            "prose": (
                "Stage2 null result: M1 rubric context and M2 failure-learning FCG context did NOT "
                "establish behavioral improvement vs M0. E05 top1=0/7, E06 prevents-C=0/13. "
                "Claim ceiling: FAILURE_LEARNING_BEHAVIOR_IMPROVEMENT_NOT_ESTABLISHED."
            ),
            "structured": {
                "node_id": "FCO_STAGE2_NULL",
                "kind": "NegativeEvidenceFCO",
                "edges": [{"rel": "REFUTES", "dst": "FCO_CONTEXT_IMPROVES_BEHAVIOR"}],
            },
        },
        {
            "fco_id": "FCO_CLAIM_CEILING",
            "kind": "ClaimCeilingFCO",
            "families": ["E01", "E02", "E03", "E04", "E05", "E06", "E07"],
            "priority": 1,
            "prose": "Do not invent unavailable endpoints; list in invented_capabilities. No estimated judge scores.",
            "structured": {
                "node_id": "FCO_CLAIM_CEILING",
                "kind": "ClaimCeilingFCO",
                "claim_ceiling": "FAILURE_LEARNING_EXPERIMENT_RESULTS_ONLY",
            },
        },
        {
            "fco_id": "FCO_POSTMORTEM_VAULT_FAILURE",
            "kind": "ProvenanceFCO",
            "families": ["E03", "E06"],
            "exclude_families": list(LABEL_LEAK_FAMILIES),
            "priority": 35,
            "prose": (
                "Historical postmortem: actual submit used folder_id=null; vault upload packet created "
                "after acknowledgement. Evidence existed before submit but was not surfaced in submission."
            ),
            "structured": {
                "node_id": "FCO_POSTMORTEM_VAULT_FAILURE",
                "kind": "ProvenanceFCO",
                "edges": [{"rel": "SUPPORTS", "dst": "FCO_VAULT_BEFORE_SUBMIT"}],
            },
        },
        {
            "fco_id": "FCO_CAUSAL_RANKING_METHOD",
            "kind": "MethodFCO",
            "families": ["E05"],
            "priority": 90,
            "prose": (
                "For causal ranking: prioritize earliest dependency that blocks downstream evidence surfacing. "
                "Do not use withheld audit labels; use only supplied candidate evidence text."
            ),
            "structured": {
                "node_id": "FCO_CAUSAL_RANKING_METHOD",
                "kind": "MethodFCO",
                "note": "No ground-truth letter injected",
            },
        },
    ]
    return atoms


def select_atoms(atoms: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    selected = []
    for atom in atoms:
        ex = set(atom.get("exclude_families") or [])
        if family in ex:
            continue
        fams = atom.get("families")
        if fams and family not in fams:
            continue
        selected.append(atom)
    return sorted(selected, key=lambda a: a.get("priority", 99))


def render_flat_prose(atoms: list[dict[str, Any]], budget: int = CONTEXT_CHAR_BUDGET) -> tuple[str, list[str]]:
    retained: list[str] = []
    parts: list[str] = []
    for atom in atoms:
        chunk = f"[{atom['fco_id']}] {atom['prose']}"
        if sum(len(p) for p in parts) + len(chunk) + 1 > budget:
            break
        parts.append(chunk)
        retained.append(atom["fco_id"])
    return "\n".join(parts), retained


def render_structured_fcg(atoms: list[dict[str, Any]], budget: int = CONTEXT_CHAR_BUDGET) -> tuple[str, list[str]]:
    retained: list[str] = []
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for atom in atoms:
        node = atom["structured"]
        blob = json.dumps(node, sort_keys=True, ensure_ascii=False)
        if sum(len(json.dumps(n, sort_keys=True)) for n in nodes) + len(blob) > budget:
            break
        nodes.append(node)
        retained.append(atom["fco_id"])
        for edge in node.get("edges") or []:
            edges.append({"src": node["node_id"], **edge})
    payload = {"schema": "hydradg.daisy.structured_context.v1", "nodes": nodes, "edges": edges}
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if len(text) > budget:
        text = json.dumps({"schema": "hydradg.daisy.structured_context.v1", "nodes": nodes[: max(1, len(nodes) // 2)]}, indent=2)
        retained = retained[: len(json.loads(text)["nodes"])]
    return text, retained


# EXP-008 structured retriever: same selection as render_structured_fcg
def structured_retriever_atoms(atoms: list[dict[str, Any]], family: str, budget: int = CONTEXT_CHAR_BUDGET) -> tuple[list[dict[str, Any]], list[str]]:
    selected = select_atoms(atoms, family)
    retained: list[str] = []
    ordered: list[dict[str, Any]] = []
    for atom in selected:
        node = atom["structured"]
        blob = json.dumps(node, sort_keys=True, ensure_ascii=False)
        if sum(len(json.dumps(a["structured"], sort_keys=True)) for a in ordered) + len(blob) > budget:
            break
        ordered.append(atom)
        retained.append(atom["fco_id"])
    return ordered, retained


CAUSAL_KIND_RANK = {
    "ProvenanceFCO": 1,
    "MethodFCO": 1,
    "RequirementFCO": 2,
    "ContradictionFCO": 4,
    "FailureRelationshipFCO": 5,
    "FailureClassFCO": 5,
    "GovernedProtocolFCO": 7,
    "NegativeEvidenceFCO": 9,
    "ClaimCeilingFCO": 9,
}


def order_atoms_neutral(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Stable canonical FCO ID ordering — no semantic prioritization."""
    return sorted(atoms, key=lambda a: a["fco_id"])


def order_atoms_causal(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic FCG topology ordering: rank → kind → canonical ID."""
    return sorted(
        atoms,
        key=lambda a: (
            CAUSAL_KIND_RANK.get(a.get("kind", ""), 6),
            a.get("priority", 99),
            a["fco_id"],
        ),
    )


def render_ordered_context(
    atoms: list[dict[str, Any]],
    order_label: str,
    budget: int = CONTEXT_CHAR_BUDGET,
) -> tuple[str, list[str], list[str]]:
    """Render ordered atoms as structured FCG JSON. Returns text, ordered IDs, prose hashes."""
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    retained: list[str] = []
    prose_hashes: list[str] = []
    import hashlib

    for atom in atoms:
        node = atom["structured"]
        blob = json.dumps(node, sort_keys=True, ensure_ascii=False)
        if sum(len(json.dumps(n, sort_keys=True)) for n in nodes) + len(blob) > budget:
            break
        nodes.append(node)
        retained.append(atom["fco_id"])
        prose_hashes.append(hashlib.sha256(atom["prose"].encode("utf-8")).hexdigest())
        for edge in node.get("edges") or []:
            edges.append({"src": node["node_id"], **edge})
    payload = {
        "schema": "hydradg.daisy.ordered_structured_context.v1",
        "order_mode": order_label,
        "nodes": nodes,
        "edges": edges,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if len(text) > budget:
        half = max(1, len(nodes) // 2)
        nodes = nodes[:half]
        retained = retained[:half]
        prose_hashes = prose_hashes[:half]
        payload["nodes"] = nodes
        payload["truncated"] = True
        text = json.dumps(payload, indent=2, ensure_ascii=False)
    return text, retained, prose_hashes

