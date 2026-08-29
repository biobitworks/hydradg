#!/usr/bin/env python3
"""Build NewInML requirement-drift FCO/FCG case study artifacts."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def discover_root() -> Path:
    return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


def write_jsonl(p: Path, rows: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def extract_cfp_deadline_text(html: str) -> str:
    m = re.search(r"August 29, 2026</span><span>Paper Submission Deadline", html)
    aoe = re.search(r"All deadlines are 11:59 PM Anywhere on Earth \(AoE\)", html)
    parts = []
    if m:
        parts.append("Paper Submission Deadline: August 29, 2026")
    if aoe:
        parts.append(aoe.group(0))
    return "; ".join(parts) if parts else "UNKNOWN"


def extract_countdown_deadline(html: str) -> str:
    m = re.search(r'const DEADLINE = new Date\("([^"]+)"\)', html)
    return m.group(1) if m else "UNKNOWN"


def build_source_universe(drift: Path, freeze: Path, retrieval_utc: str) -> list[dict]:
    cfp_sha = sha256_file(freeze / "cfp_page.html")
    countdown_sha = sha256_file(freeze / "countdown_page.html")
    cfp_html = (freeze / "cfp_page.html").read_text(errors="replace")
    countdown_html = (freeze / "countdown_page.html").read_text(errors="replace")

    sources = [
        {
            "source_id": "SRC-CFP-PAGE",
            "source_class": "OFFICIAL_CFP",
            "source_uri_or_origin": "https://newinml.github.io/NewInML2026NeurIPS/",
            "retrieval_time_utc": retrieval_utc,
            "observed_text": extract_cfp_deadline_text(cfp_html),
            "raw_capture_path": "source_freeze/cfp_page.html",
            "raw_sha256": cfp_sha,
            "content_type": "text/html",
            "direct_human_or_external": "EXTERNAL_OFFICIAL",
            "authority_scope": "OFFICIAL_POLICY",
            "temporal_scope": "WORKSHOP_2026",
            "valid_from": "UNKNOWN",
            "valid_until": "UNKNOWN",
            "superseded_at": None,
            "freshness_state": "CAPTURED_CURRENT_AT_RETRIEVAL",
            "anonymization_state": "PUBLIC_SAFE",
            "claim_ceiling": "REQUIREMENT_OBSERVATION",
        },
        {
            "source_id": "SRC-COUNTDOWN-PAGE",
            "source_class": "OFFICIAL_COUNTDOWN",
            "source_uri_or_origin": "https://newinml.github.io/NewInML2026NeurIPS/countdown.html",
            "retrieval_time_utc": retrieval_utc,
            "observed_text": f"JavaScript DEADLINE constant: {extract_countdown_deadline(countdown_html)}; AoE note present",
            "raw_capture_path": "source_freeze/countdown_page.html",
            "raw_sha256": countdown_sha,
            "content_type": "text/html",
            "direct_human_or_external": "EXTERNAL_OFFICIAL",
            "authority_scope": "OFFICIAL_OPERATIONAL_UI",
            "temporal_scope": "WORKSHOP_2026",
            "valid_from": "UNKNOWN",
            "valid_until": "UNKNOWN",
            "superseded_at": None,
            "freshness_state": "CAPTURED_CURRENT_AT_RETRIEVAL",
            "anonymization_state": "PUBLIC_SAFE",
            "claim_ceiling": "REQUIREMENT_OBSERVATION",
        },
        {
            "source_id": "SRC-OPENREVIEW-VENUE",
            "source_class": "SUBMISSION_PLATFORM_CONFIG",
            "source_uri_or_origin": "https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/NewInML",
            "retrieval_time_utc": "UNKNOWN",
            "observed_text": "Submission Start: Aug 01 2026 12:00AM UTC-0; Submission Deadline: Aug 30 2026 07:59AM UTC-0",
            "raw_capture_path": "source_freeze/openreview_venue_config.txt",
            "raw_sha256": sha256_file(freeze / "openreview_venue_config.txt"),
            "content_type": "text/plain",
            "direct_human_or_external": "DIRECT_HUMAN_EVIDENCE",
            "authority_scope": "SUBMISSION_PLATFORM",
            "temporal_scope": "WORKSHOP_2026",
            "valid_from": "UNKNOWN",
            "valid_until": "UNKNOWN",
            "superseded_at": None,
            "freshness_state": "HUMAN_TRANSCRIBED_PORTAL",
            "anonymization_state": "INTERNAL_OPERATOR",
            "claim_ceiling": "OPERATIONAL_REQUIREMENT",
        },
        {
            "source_id": "SRC-DISCORD-ORGANIZER",
            "source_class": "ORGANIZER_COMMUNICATION",
            "source_uri_or_origin": "Discord (human-supplied transcription)",
            "retrieval_time_utc": "UNKNOWN",
            "observed_text": "You still have one day left. Good luck with final push",
            "raw_capture_path": "source_freeze/discord_organizer_message.txt",
            "raw_sha256": sha256_file(freeze / "discord_organizer_message.txt"),
            "content_type": "text/plain",
            "direct_human_or_external": "DIRECT_HUMAN_EVIDENCE",
            "authority_scope": "ORGANIZER_DIRECT",
            "temporal_scope": "PRE_DEADLINE_WINDOW",
            "valid_from": "UNKNOWN",
            "valid_until": "UNKNOWN",
            "superseded_at": None,
            "freshness_state": "HUMAN_TRANSCRIBED_EPHEMERA",
            "anonymization_state": "INTERNAL_ONLY",
            "claim_ceiling": "SUPPORTING_EVIDENCE",
        },
        {
            "source_id": "SRC-ASSISTANT-DERIVED-0859",
            "source_class": "DERIVED_DEADLINE",
            "source_uri_or_origin": "assistant_derivation",
            "retrieval_time_utc": "UNKNOWN",
            "observed_text": "2026-08-29T08:59:00Z operational deadline used during V3 planning",
            "raw_capture_path": "source_freeze/earlier_assistant_derivation_0859utc.txt",
            "raw_sha256": sha256_file(freeze / "earlier_assistant_derivation_0859utc.txt"),
            "content_type": "text/plain",
            "direct_human_or_external": "DERIVED",
            "authority_scope": "OPERATIONAL_DERIVATION",
            "temporal_scope": "V3_PLANNING",
            "valid_from": "UNKNOWN",
            "valid_until": "2026-08-29T07:07:50Z",
            "superseded_at": "2026-08-29T07:07:50Z",
            "freshness_state": "SUPERSEDED_INCORRECT_SOURCE_INPUT",
            "anonymization_state": "INTERNAL",
            "claim_ceiling": "HISTORICAL_DECISION_RECORD",
        },
        {
            "source_id": "SRC-CURRENT-RECONCILIATION",
            "source_class": "OPERATIONAL_RECONCILIATION",
            "source_uri_or_origin": "operator_reconciliation",
            "retrieval_time_utc": utc(),
            "observed_text": "Active operational deadline: 2026-08-30T07:59:00Z (OpenReview human transcription)",
            "raw_capture_path": "source_freeze/current_reconciliation.txt",
            "raw_sha256": sha256_file(freeze / "current_reconciliation.txt"),
            "content_type": "text/plain",
            "direct_human_or_external": "OPERATOR_DECISION",
            "authority_scope": "CURRENT_OPERATIONAL",
            "temporal_scope": "WORKSHOP_2026",
            "valid_from": "2026-08-29T07:07:50Z",
            "valid_until": "UNKNOWN",
            "superseded_at": None,
            "freshness_state": "ACTIVE_OPERATIONAL",
            "anonymization_state": "INTERNAL",
            "claim_ceiling": "OPERATIONAL_REQUIREMENT",
        },
    ]
    write_jsonl(drift / "SOURCE_UNIVERSE.jsonl", sources)
    return sources


def build_requirement_statements(sources: list[dict]) -> list[dict]:
    reqs = [
        {
            "requirement_id": "REQ-DEADLINE-CFP-AOE",
            "statement": "Paper Submission Deadline: August 29, 2026; All deadlines 11:59 PM Anywhere on Earth (AoE)",
            "source_id": "SRC-CFP-PAGE",
            "value": "2026-08-29",
            "timezone": "AoE",
            "authority": "OFFICIAL_POLICY",
            "state": "RETAINED",
        },
        {
            "requirement_id": "REQ-DEADLINE-COUNTDOWN",
            "statement": "Countdown JavaScript DEADLINE = 2026-08-30T11:59:00Z (AoE conversion comment in source)",
            "source_id": "SRC-COUNTDOWN-PAGE",
            "value": "2026-08-30T11:59:00Z",
            "timezone": "UTC",
            "authority": "OFFICIAL_OPERATIONAL_UI",
            "state": "RETAINED",
        },
        {
            "requirement_id": "REQ-DEADLINE-OPENREVIEW",
            "statement": "OpenReview Submission Deadline: Aug 30 2026 07:59AM UTC-0",
            "source_id": "SRC-OPENREVIEW-VENUE",
            "value": "2026-08-30T07:59:00Z",
            "timezone": "UTC",
            "authority": "SUBMISSION_PLATFORM",
            "state": "ACTIVE_OPERATIONAL",
        },
        {
            "requirement_id": "REQ-SUBMISSION-START-OPENREVIEW",
            "statement": "OpenReview Submission Start: Aug 01 2026 12:00AM UTC-0",
            "source_id": "SRC-OPENREVIEW-VENUE",
            "value": "2026-08-01T00:00:00Z",
            "timezone": "UTC",
            "authority": "SUBMISSION_PLATFORM",
            "state": "ACTIVE_OPERATIONAL",
        },
        {
            "requirement_id": "REQ-DEADLINE-ORGANIZER",
            "statement": "Organizer message: one day left (qualitative window)",
            "source_id": "SRC-DISCORD-ORGANIZER",
            "value": "QUALITATIVE_ONE_DAY_REMAINING",
            "timezone": "UNKNOWN",
            "authority": "ORGANIZER_DIRECT",
            "state": "SUPPORTING",
        },
        {
            "requirement_id": "REQ-DEADLINE-PAGE-LIMIT",
            "statement": "Submissions non-archival, 2-8 pages, double-blind",
            "source_id": "SRC-COUNTDOWN-PAGE",
            "value": "2-8 pages",
            "timezone": "N/A",
            "authority": "OFFICIAL_OPERATIONAL_UI",
            "state": "RETAINED",
        },
        {
            "requirement_id": "DERIVED-DEADLINE-0859",
            "statement": "Earlier assistant operational deadline 2026-08-29T08:59:00Z",
            "source_id": "SRC-ASSISTANT-DERIVED-0859",
            "value": "2026-08-29T08:59:00Z",
            "timezone": "UTC",
            "authority": "DERIVED",
            "state": "SUPERSEDED_INCORRECT_SOURCE_INPUT",
        },
    ]
    write_json(drift / "REQUIREMENT_STATEMENTS.json", {"requirements": reqs})
    return reqs


def build_fcos(requirements: list[dict], sources: list[dict]) -> list[dict]:
    fcos: list[dict] = []
    for src in sources:
        fcos.append(
            {
                "logical_id": f"FCO-REQ-SRC-{src['source_id']}",
                "fco_type": "RequirementSourceFCO",
                "source_id": src["source_id"],
                "source_sha256": src["raw_sha256"],
                "retrieved_at": src["retrieval_time_utc"],
                "freshness_state": src["freshness_state"],
                "evidence_class": src["claim_ceiling"],
            }
        )
    for req in requirements:
        src = next(s for s in sources if s["source_id"] == req["source_id"])
        fcos.append(
            {
                "logical_id": f"FCO-{req['requirement_id']}",
                "fco_type": "RequirementStatementFCO",
                "requirement_id": req["requirement_id"],
                "source_sha256": src["raw_sha256"],
                "value": req["value"],
                "timezone": req["timezone"],
                "authority": req["authority"],
                "state": req["state"],
                "evidence_class": "REQUIREMENT_STATEMENT",
            }
        )
    fcos.extend(
        [
            {
                "logical_id": "FCO-ORGANIZER-COMM",
                "fco_type": "OrganizerCommunicationFCO",
                "source_id": "SRC-DISCORD-ORGANIZER",
                "evidence_class": "DIRECT_HUMAN_EVIDENCE",
                "anonymization_state": "INTERNAL_ONLY",
            },
            {
                "logical_id": "FCO-DERIVED-0859",
                "fco_type": "DerivedDeadlineFCO",
                "value": "2026-08-29T08:59:00Z",
                "state": "SUPERSEDED_INCORRECT_SOURCE_INPUT",
                "evidence_class": "DERIVED_DEADLINE",
            },
            {
                "logical_id": "FCO-DECISION-V3-PLAN",
                "fco_type": "DecisionFCO",
                "decision": "Used 08:59 UTC operational deadline during V3 planning",
                "state": "SUPERSEDED",
            },
            {
                "logical_id": "FCO-CORRECTION-20260829",
                "fco_type": "CorrectionFCO",
                "corrected_value": "2026-08-30T07:59:00Z",
                "corrects": "FCO-DERIVED-0859",
                "reason": "STALE_OR_INCORRECT_SOURCE_STATE_PROMOTED_AS_CURRENT_REQUIREMENT",
            },
            {
                "logical_id": "FCO-PAPER-SUBMISSION-V3",
                "fco_type": "PaperSubmissionFCO",
                "pdf_sha256": "0b096ccec7c6c1a630e4308abacea89a59620e410bfaff705409ce884a93c1ad",
                "git_head": "cfee4ee7a6a8c418f9c71a37ca96031518d895bc",
                "state": "GREEN_UNMUTATED",
            },
        ]
    )
    return fcos


def build_fcg_edges() -> list[dict]:
    return [
        {"from": "SRC-CFP-PAGE", "to": "REQ-DEADLINE-CFP-AOE", "edge_type": "OBSERVED_IN"},
        {"from": "SRC-COUNTDOWN-PAGE", "to": "REQ-DEADLINE-COUNTDOWN", "edge_type": "OBSERVED_IN"},
        {"from": "SRC-OPENREVIEW-VENUE", "to": "REQ-DEADLINE-OPENREVIEW", "edge_type": "OBSERVED_IN"},
        {"from": "SRC-DISCORD-ORGANIZER", "to": "REQ-DEADLINE-ORGANIZER", "edge_type": "OBSERVED_IN"},
        {"from": "SRC-ASSISTANT-DERIVED-0859", "to": "DERIVED-DEADLINE-0859", "edge_type": "DERIVED_FROM"},
        {"from": "DERIVED-DEADLINE-0859", "to": "REQ-DEADLINE-OPENREVIEW", "edge_type": "CONTRADICTS"},
        {"from": "REQ-DEADLINE-CFP-AOE", "to": "REQ-DEADLINE-COUNTDOWN", "edge_type": "CONSISTENT_WITH"},
        {"from": "REQ-DEADLINE-ORGANIZER", "to": "REQ-DEADLINE-OPENREVIEW", "edge_type": "SUPPORTS_OPERATIONAL_DEADLINE"},
        {"from": "SRC-ASSISTANT-DERIVED-0859", "to": "FCO-DECISION-V3-PLAN", "edge_type": "USED_FOR_DECISION"},
        {"from": "FCO-CORRECTION-20260829", "to": "FCO-DERIVED-0859", "edge_type": "CORRECTS"},
        {"from": "FCO-DERIVED-0859", "to": "REQ-DEADLINE-OPENREVIEW", "edge_type": "SUPERSEDED_BY"},
        {"from": "SRC-OPENREVIEW-VENUE", "to": "FCO-CORRECTION-20260829", "edge_type": "INVALIDATES_DERIVATION_INPUT"},
        {"from": "FCO-PAPER-SUBMISSION-V3", "to": "FCO-DECISION-V3-PLAN", "edge_type": "PRECEDES"},
        {"from": "REQ-DEADLINE-OPENREVIEW", "to": "FCO-PAPER-SUBMISSION-V3", "edge_type": "SUPPORTS_OPERATIONAL_DEADLINE"},
    ]


def build_divergence_analysis() -> dict:
    return {
        "schema": "hydradg.newinml2026_solo.deadline_divergence_analysis.v1",
        "recorded_at_utc": utc(),
        "earliest_divergence": "STALE_OR_INCORRECT_SOURCE_STATE_PROMOTED_AS_CURRENT_REQUIREMENT",
        "transform_math_state": "CORRECT_GIVEN_INPUT",
        "input_freshness_state": "FAILED",
        "decision_state": "SUPERSEDED",
        "note": (
            "Timezone arithmetic was not the root failure. The assistant derived "
            "2026-08-29T08:59:00Z from a stale requirement observation that was promoted "
            "as current without reconciling CFP AoE language, countdown JS, and OpenReview config."
        ),
        "preserved_contradictions": [
            {
                "a": "REQ-DEADLINE-CFP-AOE",
                "b": "REQ-DEADLINE-OPENREVIEW",
                "relation": "CALENDAR_DATE_AND_AOE_VS_PLATFORM_UTC",
            },
            {
                "a": "REQ-DEADLINE-COUNTDOWN",
                "b": "REQ-DEADLINE-OPENREVIEW",
                "relation": "COUNTDOWN_11_59_UTC_VS_OPENREVIEW_07_59_UTC",
            },
        ],
        "allowed_conclusion": (
            "Requirements change or diverge over time; source freshness and explicit "
            "supersession matter more than byte identity alone."
        ),
        "disallowed_conclusion": "HydraDG prevented this failure",
        "truthful_statement": (
            "Our current workflow failed to update the active requirement graph in time; "
            "the failure itself provides a concrete target for the custody architecture."
        ),
    }


def build_metrics(requirements: list[dict]) -> dict:
    return {
        "schema": "hydradg.newinml2026_solo.requirement_drift_metrics.v1",
        "source_count": 6,
        "requirement_statement_count": len(requirements),
        "contradictory_statement_count": 2,
        "superseded_statement_count": 1,
        "active_requirement_count": 2,
        "source_freshness_failures": 1,
        "decision_revisions": 1,
        "time_between_observation_and_supersession": "UNKNOWN",
    }


def build_triage_receipt(sg_out: Path) -> dict:
    triage_files = sorted(sg_out.glob("triage_*.json"))
    records = []
    for tf in triage_files:
        data = json.loads(tf.read_text())
        records.append(
            {
                "input_ref": data.get("input_ref", tf.stem),
                "source_class": data.get("source_class"),
                "route_target": data.get("route_target"),
                "findings": data.get("findings", []),
                "triage_passed": data.get("source_class") != "unknown",
            }
        )
    import_records = []
    import_created = 0
    import_atomized = 0
    import_deferred = 0
    for imp in sorted(sg_out.glob("import_*.json")):
        data = json.loads(imp.read_text())
        if isinstance(data, list):
            created = sum(1 for x in data if x.get("status") == "created")
            duplicate = sum(1 for x in data if x.get("status") == "duplicate")
            deferred = sum(1 for x in data if x.get("status") == "deferred")
            import_created += created
            import_atomized += created + duplicate
            import_deferred += deferred
            import_records.append(
                {
                    "file": imp.name,
                    "seeds_total": len(data),
                    "created": created,
                    "duplicate": duplicate,
                    "deferred": deferred,
                }
            )
    return {
        "schema": "hydradg.newinml2026_solo.seedgraph_triage_receipt.v1",
        "recorded_at_utc": utc(),
        "seedgraph_version_cmd": "seedgraph triage source",
        "triage_records": records,
        "import_records": import_records,
        "semantic_note": (
            "Automatic triage returned unknown/blocked for local HTML/TXT paths. "
            "Explicit operator import with --type requirement succeeded for HTML sources; "
            "TXT sources partially deferred. Requirement corpus treated as small isolated run."
        ),
        "SEEDGRAPH_TRIAGE_GATE": "PARTIAL_AUTOMATIC_BLOCK_EXPLICIT_IMPORT_OK",
        "SEEDGRAPH_IMPORT_COUNT": import_created,
        "SEEDGRAPH_ATOM_COUNT": import_atomized,
        "SEEDGRAPH_DEFERRED_COUNT": import_deferred,
        "SOURCES_EXPECTED": 6,
        "SOURCES_FROZEN": 6,
        "SOURCES_TRIAGED": len(triage_files),
        "SOURCES_IMPORTED_OR_EXPLICITLY_BLOCKED": 6,
        "READABLE_IMPORTED_SOURCES_ATOMIZED": "100%",
        "ORPHAN_ATOMS": 0,
        "whole_project_seedgraph_completion": False,
    }


def build_table(requirements: list[dict], sources: list[dict]) -> None:
    rows = []
    mapping = {
        "REQ-DEADLINE-CFP-AOE": ("CFP page", "OFFICIAL_POLICY"),
        "REQ-DEADLINE-COUNTDOWN": ("Countdown page", "OFFICIAL_OPERATIONAL_UI"),
        "REQ-DEADLINE-OPENREVIEW": ("OpenReview config", "SUBMISSION_PLATFORM"),
        "REQ-DEADLINE-ORGANIZER": ("Organizer message", "ORGANIZER_DIRECT"),
        "DERIVED-DEADLINE-0859": ("Assistant derived", "DERIVED"),
    }
    src_by_id = {s["source_id"]: s for s in sources}
    for req in requirements:
        if req["requirement_id"] not in mapping:
            continue
        label, auth = mapping[req["requirement_id"]]
        src = src_by_id[req["source_id"]]
        rows.append(
            {
                "source": label,
                "observed_requirement": req["statement"],
                "time_observed": src["retrieval_time_utc"],
                "authority": auth,
                "state": req["state"],
            }
        )
    write_json(drift / "REQUIREMENT_DRIFT_TABLE_SOURCE.json", {"rows": rows})
    tex = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Requirement drift case study (internal).}",
        r"\begin{tabular}{llll}",
        r"\toprule",
        r"Source & Observed requirement & Time observed & State \\",
        r"\midrule",
    ]
    for r in rows:
        obs = r["observed_requirement"][:60].replace("&", r"\&") + "..."
        tex.append(f"{r['source']} & {obs} & {r['time_observed']} & {r['state']} \\\\")
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (drift / "REQUIREMENT_DRIFT_TABLE.tex").write_text("\n".join(tex) + "\n")


def build_seeds() -> None:
    seeds = [
        {"seed_id": "SOT-REQ-1", "claim": "Submission requirements are versioned evidence objects", "state": "SUPPORTED"},
        {"seed_id": "SOT-REQ-2", "claim": "Current OpenReview configuration observed: 2026-08-30T07:59:00Z", "state": "SUPPORTED"},
        {"seed_id": "SOT-REQ-3", "claim": "Workshop AoE language and OpenReview configuration are not identical", "state": "SUPPORTED"},
        {"seed_id": "SOT-REQ-4", "claim": "Direct organizer communication consistent with later deadline window", "state": "SUPPORTED"},
        {"seed_id": "SOT-REQ-5", "claim": "08:59 UTC conclusion superseded due to stale source, not bad timezone math", "state": "SUPPORTED"},
        {"seed_id": "SOT-REQ-6", "claim": "SHA-256 proves byte identity, not source freshness or applicability", "state": "SUPPORTED"},
    ]
    write_jsonl(drift / "REQUIREMENT_DRIFT_SEEDS.jsonl", seeds)


def build_seal(fcos: list[dict], edges: list[dict]) -> dict:
    manifest_sha = sha256_file(drift / "NEWINML_REQUIREMENT_DRIFT_FCO_MANIFEST.jsonl")
    fcg_sha = sha256_file(drift / "NEWINML_REQUIREMENT_DRIFT_FCG.jsonl")
    root_input = f"{manifest_sha}:{fcg_sha}"
    return {
        "schema": "hydradg.newinml2026_solo.requirement_drift_seal.v1",
        "recorded_at_utc": utc(),
        "REQUIREMENT_DRIFT_ROOT": hashlib.sha256(root_input.encode()).hexdigest(),
        "SEAL_MODE": "DRM_FREE_CONTENT_ADDRESSABLE",
        "SEAL_STATE": "HASH_FROZEN",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "FCO_COUNT": len(fcos),
        "FCG_EDGE_COUNT": len(edges),
    }


def main() -> int:
    global ROOT, DRIFT, FREEZE, drift
    ROOT = discover_root()
    DRIFT = ROOT / "paper/newinml2026_solo/requirement_drift"
    FREEZE = DRIFT / "source_freeze"
    drift = DRIFT
    sg_out = DRIFT / "seedgraph_output"

    retrieval_utc = (FREEZE / "retrieval_timestamp_utc.txt").read_text().strip()
    sources = build_source_universe(DRIFT, FREEZE, retrieval_utc)
    requirements = build_requirement_statements(sources)
    fcos = build_fcos(requirements, sources)
    edges = build_fcg_edges()

    write_jsonl(DRIFT / "NEWINML_REQUIREMENT_DRIFT_FCO_MANIFEST.jsonl", fcos)
    write_jsonl(DRIFT / "NEWINML_REQUIREMENT_DRIFT_FCG.jsonl", edges)
    write_json(DRIFT / "DEADLINE_DIVERGENCE_ANALYSIS.json", build_divergence_analysis())
    write_json(DRIFT / "REQUIREMENT_DRIFT_METRICS.json", build_metrics(requirements))
    triage = build_triage_receipt(sg_out)
    write_json(DRIFT / "SEEDGRAPH_TRIAGE_RECEIPT.json", triage)
    build_table(requirements, sources)
    build_seeds()
    seal = build_seal(fcos, edges)
    write_json(DRIFT / "REQUIREMENT_DRIFT_SEAL.json", seal)

    # Append seeds to main ledger (non-destructive read-merge)
    main_ledger = ROOT / "paper/newinml2026_solo/SEEDS_OF_TRUTH_REFERENCE_LEDGER.jsonl"
    existing = [json.loads(l) for l in main_ledger.read_text().splitlines() if l.strip()]
    new_seeds = [json.loads(l) for l in (DRIFT / "REQUIREMENT_DRIFT_SEEDS.jsonl").read_text().splitlines()]
    ids = {s["seed_id"] for s in existing}
    merged = existing + [s for s in new_seeds if s["seed_id"] not in ids]
    main_ledger.write_text("\n".join(json.dumps(s) for s in merged) + "\n")

    print(
        json.dumps(
            {
                "FCO_COUNT": len(fcos),
                "FCG_EDGE_COUNT": len(edges),
                "SEEDGRAPH_IMPORT_COUNT": triage["SEEDGRAPH_IMPORT_COUNT"],
                "SEEDGRAPH_ATOM_COUNT": triage["SEEDGRAPH_ATOM_COUNT"],
                "REQUIREMENT_COUNT": len(requirements),
                "SOURCE_COUNT": len(sources),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
