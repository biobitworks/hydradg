#!/usr/bin/env python3
"""Deterministic reconciliation of FCG model-rooting proposals against present schemas/docs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


PROPOSALS = [
    {
        "id": "P01_MODEL_ACTOR_MERKLE_ROOT",
        "proposal": "Assign each Ollama model a dedicated Merkle/FCG MODEL_ACTOR_ROOT",
        "canonical_support": "ABSENT — AGENT_MODEL_HANDOFF_CUSTODY_CONTRACT forbids treating model digest as graph root; FCO_FCG_CANONICAL_SPEC absent but lineage doc separates hash/MMR/FCG root",
        "schema_support": "agent_model_handoff_receipt has model.runtime_digest as field, not root; no MODEL_ROOT type in present schemas",
        "implementation_change_required": True,
        "claim_risk": "REJECT_CONFLATES_IDENTITIES — model digest ≠ FCG root",
        "decision": "REJECT_CONFLATES_IDENTITIES",
    },
    {
        "id": "P02_ROLE_ACTOR_FCO",
        "proposal": "Persistent gateway role actor as fco:actor:ROLE (RESEARCH_AGENT, POISON_AGENT)",
        "canonical_support": "PRESENT — HydraLamp HYDRALAMP_EVENTS.jsonl uses fco:actor:ACTOR_ID on HANDSHAKE_OK",
        "schema_support": "PARTIAL — handoff actor_class enum; HydraLamp event shape is eval-local not in FCO_SCHEMA.json (absent)",
        "implementation_change_required": False,
        "claim_risk": "LOW when labeled role/capability actor not Ollama weights",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P03_OLLAMA_MODEL_IDENTITY",
        "proposal": "Persistent Ollama model identity = actor_class OLLAMA_MODEL + actor_id approved_name + runtime_digest",
        "canonical_support": "PRESENT — custody/turns/HANDOFF_V9_* receipts; handoff model{} block",
        "schema_support": "agent_model_handoff_receipt.model + actor_class OLLAMA_MODEL",
        "implementation_change_required": False,
        "claim_risk": "LOW — digest change implies new identity tuple",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P04_INVOCATION_HANDOFF_RECEIPT",
        "proposal": "One material invocation = one agent_model_handoff receipt; identity = receipt SHA-256 / handoff_id",
        "canonical_support": "PRESENT — AGENT_MODEL_HANDOFF_CUSTODY_CONTRACT §2-§6",
        "schema_support": "agent_model_handoff_receipt required fields incl parent_handoff_sha256",
        "implementation_change_required": False,
        "claim_risk": "LOW",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P05_ORCHESTRATION_WORK_UNIT",
        "proposal": "Execution envelope = orchestration_work_unit with parent_receipt_sha256[] and lease",
        "canonical_support": "PRESENT — GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE",
        "schema_support": "orchestration_work_unit.schema.json",
        "implementation_change_required": False,
        "claim_risk": "LOW — work unit is orchestration not scientific root",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P06_PARENT_HANDOFF_CHAIN",
        "proposal": "Invocation parent = parent_handoff_sha256 (prev receipt), not a new root type",
        "canonical_support": "PRESENT — handoff contract §2 parent links",
        "schema_support": "parent_handoff_sha256 in handoff schema; parent_receipt_sha256 in work unit",
        "implementation_change_required": False,
        "claim_risk": "LOW",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P07_FCG_ROOT_ON_APPEND_ONLY",
        "proposal": "FCG root_before/root_after only on canonical append / materialization events",
        "canonical_support": "PRESENT — HydraLamp events; handoff fcg{} block",
        "schema_support": "handoff fcg.root_before/root_after; events fcg_root_before/after",
        "implementation_change_required": False,
        "claim_risk": "LOW if not assigned per-model",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P08_INVOCATION_FCO_TYPE",
        "proposal": "Add new canonical FCO type INVOCATION_ROOT distinct from handoff receipt",
        "canonical_support": "ABSENT — FCO_SCHEMA.json not in checkout",
        "schema_support": "ABSENT — no invocation FCO schema field",
        "implementation_change_required": True,
        "claim_risk": "MEDIUM — duplicates handoff receipt identity",
        "decision": "REQUIRES_HUMAN_SCHEMA_DECISION",
    },
    {
        "id": "P09_UI_MODEL_GROUPING_FCO_EDGE",
        "proposal": "Add canonical FCO parent edge MODEL_ACTOR -> invocations for UI filtering",
        "canonical_support": "ABSENT as required graph edge",
        "schema_support": "ABSENT",
        "implementation_change_required": True,
        "claim_risk": "MEDIUM — UI convenience polluting FCG semantics",
        "decision": "PROJECTION_ONLY",
    },
    {
        "id": "P10_UI_HYDRADB_PROJECTION",
        "proposal": "HydraDB/query projection groups events by runtime_model + actor_id + model.runtime_digest",
        "canonical_support": "ALIGNED — HydraDB is projection substrate per orchestration profile",
        "schema_support": "handoff hydradb{} block; hydra_schema nodes include Run/Turn",
        "implementation_change_required": False,
        "claim_risk": "LOW when labeled projection not canonical append",
        "decision": "PROJECTION_ONLY",
    },
    {
        "id": "P11_MEDIA_CHILD_OF_MODEL",
        "proposal": "Screenshot FCO child of model invocation because model visible in frame",
        "canonical_support": "CONTRADICTS — provenance must reflect derivation not visibility",
        "schema_support": "ABSENT dedicated media schema in checkout",
        "implementation_change_required": False,
        "claim_risk": "HIGH — false lineage",
        "decision": "REJECT_CONFLATES_IDENTITIES",
    },
    {
        "id": "P12_MEDIA_DERIVATION_CHAIN",
        "proposal": "RAW MEDIA FCO -> PROVENANCE MEDIA FCO links to EVENT + VERIFICATION RECEIPT via verification work_unit handoff",
        "canonical_support": "PARTIAL — backup BROWSER_VERIFY.json pattern; VIDEO_RECORDING_RUNBOOK",
        "schema_support": "PARTIAL — verification_receipt in handoff signature block only",
        "implementation_change_required": False,
        "claim_risk": "LOW with explicit derivation edges",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P13_SAME_MODEL_NEW_INVOCATION_ONLY",
        "proposal": "Same Ollama model across runs: stable model identity, new handoff per invocation",
        "canonical_support": "PRESENT — HANDOFF_V9_* matrix reuses actor_id, unique handoff_id/receipt per case",
        "schema_support": "handoff_id unique per invocation",
        "implementation_change_required": False,
        "claim_risk": "LOW",
        "decision": "REUSE_CANONICAL",
    },
    {
        "id": "P14_EXECUTION_ROOT_EQUALS_FCG_AFTER",
        "proposal": "EXECUTION_ROOT := FCG root_after for each invocation",
        "canonical_support": "CONFLATES — FCG root is graph state not invocation identity",
        "schema_support": "fcg.root_after is append outcome field not invocation id",
        "implementation_change_required": False,
        "claim_risk": "HIGH — identity conflation",
        "decision": "REJECT_CONFLATES_IDENTITIES",
    },
    {
        "id": "P15_LOCAL_EXECUTION_ID",
        "proposal": "Use local_execution_id (ollarma_<uuid>) as operational correlation id only",
        "canonical_support": "PRESENT — hydralamp localModel.ts / runtype receipts",
        "schema_support": "NOT in handoff schema — eval-local operational id",
        "implementation_change_required": False,
        "claim_risk": "LOW if never promoted to FCG root",
        "decision": "PROJECTION_ONLY",
    },
]

def main() -> None:
    authority = {
        "present": [
            "AGENTS.md",
            "docs/AGENT_MODEL_HANDOFF_CUSTODY_CONTRACT.md",
            "docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md",
            "docs/FCO_FCG_SOURCE_LINEAGE.md",
            "schemas/agent_model_handoff_receipt.schema.json",
            "schemas/orchestration_work_unit.schema.json",
        ],
        "absent_not_invented": [
            "PROJECT_CONTROL.yaml",
            "FCO_FCG_CANONICAL_SPEC.md",
            "CLAIM_CEILINGS.md",
            "EVIDENCE_LEVELS.md",
            "FCO_SCHEMA.json",
            "FCG_SCHEMA.json",
            "SIGNING_AND_KEYS.md",
        ],
    }

    comparison = {
        "schema": "hydradg.ollarma_fcg_review.comparison.v1",
        "reconciled_at_utc": "2026-08-27T19:00:00Z",
        "authority": authority,
        "disagreements": [
            {
                "topic": "MODEL_ACTOR_LAYER",
                "POSITION_A": "Introduce separate model-actor FCO + invocation FCO + work-unit FCO types",
                "POSITION_B": "handoff_id receipt is invocation identity; no new FCO types",
                "POSITION_C": "work_unit FCO is invocation; model-actor FCO from model digest",
                "AGREEMENT": "No dedicated MODEL_MERKLE_ROOT; parent_handoff chain required",
                "DISAGREEMENT": "Whether to mint new FCO types vs reuse handoff receipt + work unit envelope",
                "EARLIEST_DIVERGENT_ASSUMPTION": "Whether invocation identity is already fully represented by agent_model_handoff receipt SHA-256",
                "CANONICAL_RESOLUTION": "REUSE handoff receipt as invocation identity; work_unit for orchestration; defer new FCO types until FCO_SCHEMA.json available",
            },
            {
                "topic": "SAME_MODEL_ACROSS_RUNS",
                "POSITION_A": "Different actor per invocation (model A)",
                "POSITION_B": "Same actor, new invocations",
                "POSITION_C": "Same actor (runtime_digest stable), new work_unit per invocation",
                "AGREEMENT": "Each invocation is distinct evidence",
                "DISAGREEMENT": "Actor stability across runs",
                "EARLIEST_DIVERGENT_ASSUMPTION": "Whether actor_id names a role (RESEARCH_AGENT) or Ollama tag (qwen2.5-coder:7b)",
                "CANONICAL_RESOLUTION": "Two layers: role actor fco:actor:* for gateway; OLLAMA_MODEL actor_id=approved_name with runtime_digest for inference; same tuple across runs, new handoff each call",
            },
            {
                "topic": "UI_GROUPING",
                "POSITION_A": "Canonical FCO relation for UI grouping",
                "POSITION_B": "Canonical FCO relations",
                "POSITION_C": "Canonical FCO relations (warns against HydraDB-only)",
                "AGREEMENT": "Do not invent FCG roots for UI",
                "DISAGREEMENT": "Whether grouping must be canonical graph edge vs query projection",
                "EARLIEST_DIVERGENT_ASSUMPTION": "Whether UI convenience warrants canonical edge promotion",
                "CANONICAL_RESOLUTION": "PROJECTION_ONLY via HydraDB/index on handoff receipts and events; optional deterministic UI grouping keyed by actor_id/runtime_model",
            },
            {
                "topic": "EXECUTION_ROOT",
                "POSITION_A": "Infer EXECUTION_ROOT from FCO graph (ambiguous)",
                "POSITION_B": "No EXECUTION_ROOT type",
                "POSITION_C": "EXECUTION_ROOT = FCG root_after",
                "AGREEMENT": "None on EXECUTION_ROOT semantics",
                "DISAGREEMENT": "Whether FCG root_after can name an invocation",
                "EARLIEST_DIVERGENT_ASSUMPTION": "Confusing append outcome with invocation identity",
                "CANONICAL_RESOLUTION": "REJECT — FCG root_after is graph state snapshot not invocation root",
            },
        ],
        "proposals": PROPOSALS,
    }

    recommendation = {
        "schema": "hydradg.ollarma_fcg_review.recommendation.v1",
        "recorded_at_utc": "2026-08-27T19:00:00Z",
        "claim_ceiling": "ARCHITECTURAL_RECOMMENDATION_ONLY",
        "ACTUAL_HOST": "magicSTUDIObox.local",
        "CURRENT_BRANCH": "hack-hydra/hydralamp-20260826",
        "CURRENT_SHA": "82981cfcf98f0c9d06ec06007f24570d2471efc7",
        "MODELS_INVENTORIED": 14,
        "MODELS_EXECUTED": ["qwen2.5-coder:7b", "deepseek-r1:14b", "qwen3:8b"],
        "CANONICAL_MODEL_ACTOR_REPRESENTATION": "Two-layer: (1) gateway role actor fco:actor:ROLE with runtime_model ollarma/role; (2) inference identity actor_class=OLLAMA_MODEL, actor_id=approved_name, model.runtime_digest",
        "CANONICAL_INVOCATION_REPRESENTATION": "agent_model_handoff receipt (handoff_id + receipt_sha256) per material call; optional orchestration_work_unit wrapper with parent_receipt_sha256",
        "CANONICAL_PARENT_REPRESENTATION": "parent_handoff_sha256 chain to delegating handoff/work_unit; prompt/request FCO hashes in input_dependencies",
        "MODEL_ROOT_REQUIRED": "NO",
        "MODEL_ROOT_MEANING": "N/A — do not mint Merkle/FCG roots for models; runtime_digest is content identity not graph root",
        "FCG_ROOT_USAGE": "fcg_root_before/after on canonical append and recorded on handoff fcg{} block; single project FCG not per-model",
        "MMR_ROOT_USAGE": "Separate merkle_mmr{} on handoff; NOT interchangeable with model digest or FCG root",
        "HYDRADB_MODEL_GROUPING": "PROJECTION_ONLY — index/query by actor_id, runtime_model, model.runtime_digest, handoff receipt hashes",
        "MEDIA_RELATIONSHIP_RECOMMENDATION": "EVENT or verification work_unit -> RAW MEDIA FCO (bytes) -> PROVENANCE MEDIA FCO (metadata) + VERIFICATION RECEIPT; link by event_hash/source_request_hash not model visibility",
        "REQUIRED_LINEAGE_ELEMENTS_PRESENT": [
            "parent_handoff_sha256",
            "actor_class/actor_id",
            "model.bridge/approved_name/runtime_digest",
            "prompt_sha256",
            "request_sha256",
            "output_sha256",
            "transformation_class",
            "fcg.root_before/root_after (when append occurs)"
        ],
        "REQUIRED_LINEAGE_ELEMENTS_MISSING_OR_EVAL_LOCAL": [
            "deterministic parser/scorer identity hash (not required in handoff schema today)",
            "fco.object_id materialization (handoff fco{} optional/null in many receipts)",
            "ollarma CLI bridge receipt when using direct ollama generate bypass"
        ],
        "SCHEMA_CHANGE_REQUIRED": "NO",
        "SCHEMA_CHANGE_RECOMMENDED": "DEFER until FCO_SCHEMA.json / FCG_SCHEMA.json resolved upstream; optional non-blocking handoff fields for parser_id/parser_sha256",
        "EVIDENCE_STATE": "PROBABILISTIC_MODEL_REVIEW_PLUS_DETERMINISTIC_SCHEMA_RECONCILIATION",
        "EXPERIMENT_STATE": "NO_SCIENCE_EVENTS_CHANGED",
        "FCO_STATE": "NO_CANONICAL_APPEND_FROM_REVIEW",
        "FCG_STATE": "NO_CANONICAL_APPEND_FROM_REVIEW",
        "HYDRADB_STATE": "NOT_TOUCHED",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED_BY_THIS_LANE",
        "NEXT_SAFE_ACTION": "Implement HydraDB projection + UI filter keyed on handoff receipts; wire Ollarma path to always emit handoff before promotion; do not add MODEL_ROOT to FCG",
        "FINAL_REVIEW_GATE": "Human schema authority resolves FCO_SCHEMA.json import; until then operate under agent_model_handoff + orchestration_work_unit only",
    }

    out_comparison = ROOT / "FCG_ROOTING_COMPARISON.json"
    out_rec_json = ROOT / "FCG_ROOTING_RECOMMENDATION.json"
    out_comparison.write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    out_rec_json.write_text(json.dumps(recommendation, indent=2) + "\n", encoding="utf-8")

    md = """# FCG Model Rooting Recommendation (Ollarma Parallel Review A)

**Claim ceiling:** ARCHITECTURAL_RECOMMENDATION_ONLY — not signed, not FCG-appended.

## Identity summary

| Concept | Canonical representation | NOT equivalent to |
|---|---|---|
| Role/gateway actor | `fco:actor:ROLE`, `runtime_model=ollarma/role` | Ollama weight digest |
| Ollama model identity | `actor_class=OLLAMA_MODEL`, `actor_id=approved_name`, `model.runtime_digest` | FCG root |
| Invocation | `agent_model_handoff` receipt (`handoff_id`, receipt SHA-256) | FCG root_after |
| Orchestration envelope | `orchestration_work_unit` + `parent_receipt_sha256[]` | Scientific verification |
| FCG state | `fcg_root_before` / `fcg_root_after` on append | Model root |
| MMR | `merkle_mmr.root` on receipt | SHA-256 of model weights |

## Answers

1. **Persistent MODEL ACTOR identity:** Stable tuple `(bridge=OLLARMA, approved_name, runtime_digest)` plus, for gateway lanes, role actor `fco:actor:*`.
2. **One MODEL INVOCATION:** One `hydradg.agent_model_handoff.v1` receipt per material call; optional work-unit wrapper.
3. **Parent of invocation:** `parent_handoff_sha256` (delegating receipt), with `input_dependencies[]` binding prompt/case bytes.
4. **Graph shape:** Reuse handoff parent chain + FCG append fields; **do not** add MODEL_ACTOR_ROOT / INVOCATION_ROOT Merkle nodes.
5. **Existing equivalents:** `MODEL_ACTOR` ≈ handoff `model{}` + `actor_id`; `INVOCATION` ≈ handoff receipt; `EXECUTION` ≈ work_unit (orchestration only, not a root).

## UI hierarchy (projection)

```
HYDRALAMP_RUN (work_unit / run receipt)
  ├─ role actors (fco:actor:*)
  ├─ handoff receipts (OLLAMA_MODEL invocations)
  ├─ gateway events (HYDRALAMP_EVENTS.jsonl)
  ├─ deterministic verifiers (DETERMINISTIC_TOOL handoffs)
  └─ media evidence (derived from EVENT / verification work_unit)
```

This is **HydraDB/query + deterministic UI layout**, not new canonical FCO edges.

## Media custody

- **RAW MEDIA FCO:** exact capture bytes (screenshot/video).
- **PROVENANCE MEDIA FCO:** metadata linking to triggering `event_hash` or verification scope.
- **VERIFICATION RECEIPT:** deterministic gate output (e.g. browser verify JSON).
- Parent: verification **work_unit** or **event**, not the model visible in the frame.

## Panel disagreement (resolved)

- **Earliest divergent assumption:** conflating HydraLamp **role actors** with **Ollama model tags**.
- **Resolution:** keep layers separate; same Ollama model across runs keeps stable identity tuple, **new handoff per invocation**.

## Schema change

**Not required** for minimum viable lineage. **Defer** optional FCO types until upstream `FCO_SCHEMA.json` is present in checkout.

See `FCG_ROOTING_COMPARISON.json` and `FCG_ROOTING_RECOMMENDATION.json` for machine-readable reconciliation.
"""
    (ROOT / "FCG_ROOTING_RECOMMENDATION.md").write_text(md, encoding="utf-8")
    print(json.dumps({"comparison_sha256": sha256_file(out_comparison), "recommendation_sha256": sha256_file(out_rec_json)}, indent=2))


if __name__ == "__main__":
    main()
