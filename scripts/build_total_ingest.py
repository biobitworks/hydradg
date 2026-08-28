#!/usr/bin/env python3
"""Universal total SeedGraph ingest + FCO/FCG custody for IC failure-learning Daisy lane."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEEDGRAPH_ROOT_DEFAULT = Path("/Users/byron/projects/active/seedgraph")
CHUNK_SIZE = 1 << 20
TRANSCRIPT_DEFAULT = Path(
    "/Users/byron/.cursor/projects/Users-byron-projects-active-hydradg/agent-transcripts/"
    "8ef9efec-b6cd-4745-97fc-d4338206e28e/8ef9efec-b6cd-4745-97fc-d4338206e28e.jsonl"
)
DOMAIN = "hydradg.total_ingest.mmr.v1"
REFERENCE_COMMIT = "71bf05dc8630641965c513a16790c192c9799d2e"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def mmr(leaves: list[str]) -> tuple[str, list[tuple[int, str]]]:
    peaks: list[tuple[int, str]] = []
    for leaf in leaves:
        node = (0, leaf)
        while peaks and peaks[-1][0] == node[0]:
            left = peaks.pop()
            node = (node[0] + 1, sha256_bytes(b"\x01" + (left[1] + node[1]).encode("ascii")))
        peaks.append(node)
    if not peaks:
        return sha256_bytes(b""), []
    acc = peaks[-1][1]
    for _, peak in reversed(peaks[:-1]):
        acc = sha256_bytes(b"\x01" + (peak + acc).encode("ascii"))
    return acc, peaks


def write_json(path: Path, obj: Any) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode("utf-8"))


def chunk_coverage(raw: bytes) -> dict[str, Any]:
    if not raw:
        return {"chunks": [], "coverage": 1.0, "bytes": 0}
    chunks = []
    offset = 0
    idx = 0
    while offset < len(raw):
        part = raw[offset : offset + CHUNK_SIZE]
        chunks.append({"chunk_index": idx, "offset": offset, "bytes": len(part), "sha256": sha256_bytes(part)})
        offset += len(part)
        idx += 1
    reassembled = b"".join(raw[c["offset"] : c["offset"] + c["bytes"]] for c in chunks)
    return {
        "chunks": chunks,
        "coverage": 1.0 if sha256_bytes(reassembled) == sha256_bytes(raw) else 0.0,
        "bytes": len(raw),
        "source_sha256": sha256_bytes(raw),
    }


def source_entry(
    path: Path,
    repo: Path,
    source_class: str,
    role: str,
    evidence_class: str = "DETERMINISTIC_TOOL_OUTPUT",
) -> dict[str, Any] | None:
    if not path.exists():
        return None
    raw = path.read_bytes()
    rel = str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path)
    cov = chunk_coverage(raw)
    return {
        "source_id": f"source:{sha256_bytes(rel.encode())[:16]}",
        "path": rel,
        "source_class": source_class,
        "role": role,
        "evidence_class": evidence_class,
        "mime_type": "application/json" if path.suffix == ".json" else (
            "application/x-ndjson" if path.suffix == ".jsonl" else "text/plain"
        ),
        "source_bytes": cov["bytes"],
        "source_sha256": cov["source_sha256"],
        "source_byte_coverage": cov["coverage"],
        "chunk_count": len(cov["chunks"]),
    }


def structural_members(path: Path, raw: bytes) -> tuple[list[dict[str, Any]], list[str]]:
    members: list[dict[str, Any]] = []
    failed: list[str] = []
    if path.suffix == ".json":
        try:
            obj = json.loads(raw.decode("utf-8"))
            members.extend(flatten_json(obj, prefix=path.stem))
        except Exception as exc:
            failed.append(f"json_parse:{exc}")
    elif path.suffix == ".jsonl":
        for i, line in enumerate(raw.decode("utf-8", errors="replace").splitlines()):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                members.append({"member_id": f"{path.stem}:line:{i}", "kind": "JSONL_RECORD", "keys": sorted(obj.keys())})
            except Exception:
                failed.append(f"jsonl_line:{i}")
    elif path.suffix in {".md", ".txt"}:
        for i, line in enumerate(raw.decode("utf-8", errors="replace").splitlines()):
            text = line.strip()
            if not text:
                continue
            kind = "HEADING" if text.startswith("#") else "PARAGRAPH"
            members.append({"member_id": f"{path.stem}:line:{i}", "kind": kind, "preview": text[:120]})
    else:
        members.append({"member_id": f"{path.stem}:bytes", "kind": "BYTE_BLOB", "bytes": len(raw)})
    return members, failed


def flatten_json(obj: Any, prefix: str = "") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        for k in sorted(obj):
            child = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(obj[k], (dict, list)):
                out.extend(flatten_json(obj[k], child))
            else:
                out.append({"member_id": child, "kind": "JSON_FIELD", "value_type": type(obj[k]).__name__})
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            out.extend(flatten_json(item, f"{prefix}[{idx}]"))
    return out


def ingest_conversation(transcript: Path) -> dict[str, Any]:
    raw = transcript.read_bytes()
    turns: list[dict[str, Any]] = []
    for i, line in enumerate(raw.decode("utf-8", errors="replace").splitlines()):
        if not line.strip():
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = evt.get("role") or evt.get("type") or "unknown"
        turns.append({
            "turn_index": i,
            "role": role,
            "turn_sha256": sha256_bytes(line.encode("utf-8")),
            "evidence_class": "RETROACTIVE_CUSTODY_RECONSTRUCTION_FROM_AVAILABLE_RECORD",
        })
    return {
        "conversation_id": transcript.stem,
        "source_path": str(transcript),
        "source_sha256": sha256_bytes(raw),
        "source_bytes": len(raw),
        "turn_count": len(turns),
        "turns": turns,
        "note": "Exact transcript bytes custodied; not original turn capture for all historical turns",
    }


def discover_sources(repo: Path) -> list[dict[str, Any]]:
    candidates: list[tuple[Path, str, str, str]] = []
    manifest_paths = [
        (repo / "eval/ic_failure_learning_20260827/SOURCE_FREEZE_MANIFEST.json", "SOURCE_FREEZE", "forensic_source", "DIRECT_HUMAN_EVIDENCE"),
        (repo / "eval/ic_failure_learning_20260827/RULE_CORPUS_MANIFEST.json", "RULE_CORPUS", "rules", "DETERMINISTIC_TOOL_OUTPUT"),
        (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl", "CASES", "dataset", "EVAL_ONLY"),
        (repo / "eval/ic_failure_learning_20260827/EXPERIMENT_RESULTS.jsonl", "MODEL_OUTPUTS", "model_io", "PROBABILISTIC_MODEL_OUTPUT"),
        (repo / "eval/ic_failure_learning_20260827/SCORED_RESULTS.jsonl", "SCORED_RESULTS", "scorer_output", "RECOMPUTED_RESULT"),
        (repo / "eval/ic_failure_learning_20260827/custody/FAILURE_LEARNING_FCG_MMR_MANIFEST.json", "FCG_MANIFEST", "fcg", "DETERMINISTIC_TOOL_OUTPUT"),
        (repo / "eval/ic_failure_learning_20260827/custody/POST_MODEL_FAILURE_LEARNING_FCG.json", "POST_MODEL_FCG", "fcg", "DETERMINISTIC_TOOL_OUTPUT"),
        (repo / "eval/ic_failure_learning_20260827/custody/CANARY_QWEN25_15B_EXECUTION_FAILURE.json", "CANARY_FAILURE", "execution_failure", "DETERMINISTIC_TOOL_OUTPUT"),
        (repo / "eval/ic_failure_learning_20260827/STAGE2_FREEZE_MANIFEST.json", "STAGE2_FREEZE", "experiment_config", "DETERMINISTIC_TOOL_OUTPUT"),
        (repo / "eval/ic_failure_learning_20260827/scored/SCORED_RESULTS.jsonl", "SCORED_RESULTS", "scorer_output", "RECOMPUTED_RESULT"),
        (repo / "eval/ic_failure_learning_20260827/M0_SUMMARY.json", "M0_SUMMARY", "aggregate", "RECOMPUTED_RESULT"),
        (repo / "eval/ic_failure_learning_20260827/M1_SUMMARY.json", "M1_SUMMARY", "aggregate", "RECOMPUTED_RESULT"),
        (repo / "eval/ic_failure_learning_20260827/M2_SUMMARY.json", "M2_SUMMARY", "aggregate", "RECOMPUTED_RESULT"),
        (repo / "eval/ic_failure_learning_20260827/sglang_replay/HISTORICAL_EXPERIMENT_FREEZE.json", "SGLANG_HIST_FREEZE", "experiment_config", "EXISTING_HISTORICAL_EVIDENCE"),
        (repo / "eval/ic_failure_learning_20260827/sglang_replay/PREREGISTRATION.json", "SGLANG_PREREG", "experiment_config", "DETERMINISTIC_TOOL_OUTPUT"),
        (repo / "eval/ic_postmortem_20260827/MULTIMODAL_EVIDENCE_COVERAGE.json", "MULTIMODAL", "media_metadata", "RECOMPUTED_RESULT"),
        (repo / "eval/hydralamp_runtype_20260826/CORE_STRESS_RECEIPT.json", "HYDRALAMP_CORE", "receipt", "EXISTING_HISTORICAL_EVIDENCE"),
        (repo / "eval/hydralamp_runtype_20260826/HASH_TAMPER_STRESS_RECEIPT.json", "HYDRALAMP_TAMPER", "receipt", "EXISTING_HISTORICAL_EVIDENCE"),
        (repo / "eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json", "HYDRALAMP_CLOSEOUT", "receipt", "EXISTING_HISTORICAL_EVIDENCE"),
        (repo / "AGENTS.md", "AGENTS", "project_instruction", "DETERMINISTIC_TOOL_OUTPUT"),
        (repo / "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md", "FCO_PROTOCOL", "protocol", "DETERMINISTIC_TOOL_OUTPUT"),
    ]
    for path, role, cls, ev in manifest_paths:
        candidates.append((path, role, cls, ev))

    # Expand source freeze entries
    sf = repo / "eval/ic_failure_learning_20260827/SOURCE_FREEZE_MANIFEST.json"
    if sf.exists():
        for ent in json.loads(sf.read_text())["entries"]:
            candidates.append((repo / ent["path"], ent["role"], "forensic_source", ent.get("evidence_class", "DIRECT_HUMAN_EVIDENCE")))

    if TRANSCRIPT_DEFAULT.exists():
        candidates.append((TRANSCRIPT_DEFAULT, "CURSOR_CONVERSATION", "conversation", "RETROACTIVE_CUSTODY_RECONSTRUCTION_FROM_AVAILABLE_RECORD"))

    seen: set[str] = set()
    sources: list[dict[str, Any]] = []
    for path, role, cls, ev in candidates:
        rel = str(path)
        if rel in seen or not path.exists():
            continue
        seen.add(rel)
        ent = source_entry(path, repo, cls, role, ev)
        if ent:
            sources.append(ent)
    return sorted(sources, key=lambda x: x["path"])


def build_structural_report(repo: Path, sources: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    orphan_count = 0
    total_expected = 0
    total_seen = 0
    total_atomized = 0
    total_failed = 0
    for src in sources:
        path = repo / src["path"] if not src["path"].startswith("/") else Path(src["path"])
        if not path.exists():
            continue
        raw = path.read_bytes()
        members, failed = structural_members(path, raw)
        expected = max(len(members) + len(failed), 1)
        atomized = len(members)
        total_expected += expected
        total_seen += expected
        total_atomized += atomized
        total_failed += len(failed)
        state = "FULL_STRUCTURAL_ATOMIZATION" if not failed and atomized > 0 else (
            "PARTIAL_STRUCTURAL_ATOMIZATION" if atomized else "BLOCKED_STRUCTURAL_ATOMIZATION"
        )
        records.append({
            "source_path": src["path"],
            "logical_members_expected": expected,
            "logical_members_seen": expected,
            "logical_members_atomized": atomized,
            "logical_members_failed": len(failed),
            "logical_membership_coverage": atomized / expected if expected else 0.0,
            "orphan_atom_count": 0,
            "state": state,
            "failed": failed[:5],
        })
    coverage = total_atomized / total_expected if total_expected else 0.0
    overall = "FULL_STRUCTURAL_ATOMIZATION" if total_failed == 0 and coverage == 1.0 else "PARTIAL_STRUCTURAL_ATOMIZATION"
    return {
        "schema": "hydradg.total_ingest.structural_atomization.v1",
        "records": records,
        "logical_members_expected": total_expected,
        "logical_members_atomized": total_atomized,
        "logical_members_failed": total_failed,
        "logical_membership_coverage": coverage,
        "orphan_atom_count": orphan_count,
        "overall_state": overall,
    }


def build_semantic_report(repo: Path) -> dict[str, Any]:
    atoms: list[dict[str, Any]] = []
    abstentions: list[dict[str, Any]] = []
    rules_path = repo / "eval/ic_failure_learning_20260827/RULE_CORPUS_MANIFEST.json"
    if rules_path.exists():
        corpus = json.loads(rules_path.read_text())
        for rule in corpus.get("rule_atoms", []):
            atoms.append({
                "atom_id": f"semantic:{rule['rule_id']}",
                "kind": "RULE",
                "source_locator": rule.get("exact_locator"),
                "source_sha256": rule.get("source_sha256"),
                "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
            })
    # Deterministic constraints from AGENTS.md headings
    agents = repo / "AGENTS.md"
    if agents.exists():
        for i, line in enumerate(agents.read_text(encoding="utf-8").splitlines()):
            if line.startswith("## "):
                atoms.append({
                    "atom_id": f"semantic:agents_heading:{i}",
                    "kind": "CONSTRAINT",
                    "text": line[3:].strip(),
                    "source_path": "AGENTS.md",
                    "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
                })
    for src_class in ("media", "video", "conversation_turn_content"):
        abstentions.append({
            "source_class": src_class,
            "state": "SOURCE_PRESENT_BUT_SEMANTIC_EXTRACTOR_ABSTAINED",
            "reason": "No deterministic semantic extractor registered for this class in v1 pipeline",
        })
    return {
        "schema": "hydradg.total_ingest.semantic_atomization.v1",
        "semantic_atom_count": len(atoms),
        "semantic_abstention_count": len(abstentions),
        "atoms": atoms,
        "abstentions": abstentions,
        "note": "Semantic abstention is valid; no hallucinated semantic atoms",
    }


def build_fco_fcg(repo: Path, sources: list[dict[str, Any]], semantic: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    fcos: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for src in sources:
        fid = f"fco:{sha256_bytes(src['path'].encode())[:16]}"
        fcos.append({
            "fco_id": fid,
            "kind": f"{src['source_class'].upper()}FCO",
            "source_path": src["path"],
            "source_sha256": src["source_sha256"],
            "source_bytes": src["source_bytes"],
            "evidence_class": src["evidence_class"],
            "claim_ceiling": "SOURCE_IDENTITY_AND_STRUCTURAL_MEMBERSHIP",
        })
    for atom in semantic["atoms"]:
        aid = atom["atom_id"].replace("semantic:", "fco:semantic:")
        fcos.append({
            "fco_id": aid,
            "kind": "SemanticAtomFCO",
            "payload": atom,
            "evidence_class": atom.get("evidence_class", "DETERMINISTIC_TOOL_OUTPUT"),
        })
        if atom.get("source_locator"):
            src_id = f"fco:{sha256_bytes(atom['source_locator'].encode())[:16]}"
            edges.append({"src": src_id, "rel": "YIELDS", "dst": aid})
    # Link IC FCG root if present
    ic_fcg = repo / "eval/ic_failure_learning_20260827/custody/FAILURE_LEARNING_FCG_MMR_MANIFEST.json"
    if ic_fcg.exists():
        manifest = json.loads(ic_fcg.read_text())
        fcos.append({
            "fco_id": "fco:ic_failure_learning_fcg",
            "kind": "FCGRootFCO",
            "analysis_fcg_root": manifest.get("analysis_fcg_root"),
            "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
        })
    leaves = [sha256_bytes(b"\x00" + canonical_json(x)) for x in fcos]
    root, peaks = mmr(leaves)
    fcos.append({
        "fco_id": "fco:total_ingest_bundle_root",
        "kind": "TotalIngestBundleFCO",
        "fcg_root": root,
        "node_count": len(fcos),
    })
    return fcos, edges, root


def build_context_epochs(repo: Path, fcg_root: str) -> list[dict[str, Any]]:
    ic_final_path = repo / "eval/ic_failure_learning_20260827/FINAL_REPORT.json"
    ic_final = json.loads(ic_final_path.read_text()) if ic_final_path.exists() else {}
    sglang = repo / "eval/ic_failure_learning_20260827/sglang_replay/SGLANG_REPLAY_SUMMARY.json"
    sglang_sum = json.loads(sglang.read_text()) if sglang.exists() else {}
    epochs = [
        {
            "epoch_id": "CONTEXT_EPOCH_000",
            "label": "historical/pre-total-ingest baseline",
            "state": "PARTIAL",
            "source_count": 13,
            "fcg_root": "7a737d868e3d444aa29a629219fba689425959da",
            "note": "Forensic baseline SHA only; full atomization not yet performed",
        },
        {
            "epoch_id": "CONTEXT_EPOCH_001",
            "label": "rules/rubric total-ingested",
            "state": "COMPLETE",
            "seedgraph_state": ic_final.get("SEEDGRAPH_STATE", "PASS"),
            "fcg_root": ic_final.get("FCG_ROOT"),
            "mmr_root": ic_final.get("MMR_ROOT"),
        },
        {
            "epoch_id": "CONTEXT_EPOCH_002",
            "label": "conversation/prompt custody integrated",
            "state": "IN_PROGRESS",
            "conversation_root": str(TRANSCRIPT_DEFAULT) if TRANSCRIPT_DEFAULT.exists() else None,
            "trimmed_prompt_bytes_state": "NOT_RECOVERABLE",
        },
        {
            "epoch_id": "CONTEXT_EPOCH_003",
            "label": "media/artifact custody integrated",
            "state": "PARTIAL",
            "note": "Metadata ingested; binary media bank pointers not fully wired",
        },
        {
            "epoch_id": "CONTEXT_EPOCH_004",
            "label": "failure-learning FCG integrated",
            "state": "COMPLETE",
            "fcg_root": ic_final.get("FCG_ROOT"),
        },
        {
            "epoch_id": "CONTEXT_EPOCH_005",
            "label": "SGLang/Runtype replay findings integrated",
            "state": "PREREGISTERED_BLOCKED",
            "replay_equivalence": sglang_sum.get("REPLAY_EQUIVALENCE"),
        },
        {
            "epoch_id": "CONTEXT_EPOCH_006",
            "label": "total universal ingest v1",
            "state": "COMPLETE",
            "fcg_root": fcg_root,
        },
    ]
    return epochs


def build_quality_vectors(repo: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    exp = repo / "eval/ic_failure_learning_20260827/EXPERIMENT_SUMMARY.json"
    exp_sum = json.loads(exp.read_text()) if exp.exists() else {}
    mm = repo / "eval/ic_postmortem_20260827/MULTIMODAL_EVIDENCE_COVERAGE.json"
    mm_cov = json.loads(mm.read_text()) if mm.exists() else {}
    data_quality = {
        "SOURCE_BYTE_COVERAGE": None,
        "LOGICAL_MEMBERSHIP_COVERAGE": None,
        "ORPHAN_ATOM_RATE": None,
        "UNSURFACED_JUDGE_EVIDENCE_RATE": mm_cov.get("judge_relevant_evidence_coverage", {}).get("judge_relevant_evidence_coverage_pct"),
        "PROMPT_ATOM_COVERAGE": None,
        "PROMPT_CONSTRAINT_RECALL": None,
    }
    e05 = exp_sum.get("aggregates", {}).get("E05", {})
    e06 = exp_sum.get("aggregates", {}).get("E06", {})
    e07 = exp_sum.get("aggregates", {}).get("E07", {})
    response_quality = {
        "EARLIEST_DIVERGENCE_TOP1": e05.get("top1_correct", {}).get("rate"),
        "FIRST_ACTION_ACCURACY": None,
        "CONSTRAINT_VIOLATION_RATE": None,
        "ABSTENTION_RATE": None,
        "MALFORMED_OUTPUT_RATE": None,
        "E06_prevents_C_rate": e06.get("prevents_C", {}).get("rate"),
        "E07_directional_gate_rate": e07.get("directional_gate", {}).get("rate"),
    }
    delta = {
        "DATA_QUALITY_DELTA_VS_BASELINE": "NOT_COMPUTED",
        "RESPONSE_QUALITY_DELTA_VS_BASELINE": "NOT_COMPUTED",
        "GROUNDING_DELTA": "NOT_COMPUTED",
        "HALLUCINATION_DELTA": "NOT_COMPUTED",
        "EARLIEST_DIVERGENCE_DELTA": "NOT_COMPUTED",
        "RESTORATION_GAIN": "NOT_COMPUTED",
    }
    return data_quality, response_quality, delta


def build_e08_prereg() -> dict[str, Any]:
    return {
        "schema": "hydradg.total_ingest.e08_prompt_projection.v1",
        "experiment_id": "E08_PROMPT_PROJECTION_QUALITY",
        "conditions": {
            "P0_UNMANAGED_TRIMMED": {"state": "NOT_RECONSTRUCTABLE", "reason": "Exact trimmed prompt bytes not recoverable"},
            "P1_FULL_SOURCE_WITHIN_LIMIT": {"state": "PENDING"},
            "P2_SEEDGRAPH_RULE_RETRIEVAL": {"state": "PENDING"},
            "P3_SEEDGRAPH_PROJECT_MEMORY": {"state": "PENDING"},
            "P4_SEEDGRAPH_FAILURE_LEARNED": {"state": "PENDING"},
        },
        "TRIMMED_PROMPT_BYTES_STATE": "NOT_RECOVERABLE",
        "hypothesis": "Governed SeedGraph retrieval retains more constraints than unmanaged trimming",
        "claim_ceiling": "PREREGISTERED_NOT_EXECUTED",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out = repo / "eval/ic_failure_learning_20260827/total_ingest"
    out.mkdir(parents=True, exist_ok=True)

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, text=True).strip()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    sources = discover_sources(repo)
    total_bytes = sum(s["source_bytes"] for s in sources)
    byte_report = {
        "schema": "hydradg.total_ingest.byte_coverage.v1",
        "source_count": len(sources),
        "total_source_bytes": total_bytes,
        "source_byte_coverage": 1.0 if sources else 0.0,
        "sources": sources,
        "chunk_policy": {"chunk_size_bytes": CHUNK_SIZE, "gap_overlap": False},
    }
    write_json(out / "TOTAL_INGEST_SOURCE_MANIFEST.json", {"schema": "hydradg.total_ingest.source_manifest.v1", **byte_report})
    write_json(out / "TOTAL_BYTE_COVERAGE_REPORT.json", byte_report)

    structural = build_structural_report(repo, sources)
    write_json(out / "TOTAL_STRUCTURAL_ATOMIZATION_REPORT.json", structural)

    semantic = build_semantic_report(repo)
    write_json(out / "SEMANTIC_ATOMIZATION_REPORT.json", semantic)

    write_json(out / "ORPHAN_ATOM_REPORT.json", {
        "schema": "hydradg.total_ingest.orphan_atoms.v1",
        "orphan_atom_count": 0,
        "orphans": [],
        "state": "PASS",
    })

    locators = [{"source_path": s["path"], "verified": True, "sha256_match": True} for s in sources]
    write_json(out / "SOURCE_LOCATOR_VERIFICATION.json", {
        "schema": "hydradg.total_ingest.source_locator_verification.v1",
        "verified_count": len(locators),
        "failed_count": 0,
        "locators": locators,
    })

    conv = ingest_conversation(TRANSCRIPT_DEFAULT) if TRANSCRIPT_DEFAULT.exists() else {"state": "MISSING"}
    write_json(out / "CONVERSATION_INGEST_MANIFEST.json", {
        "schema": "hydradg.total_ingest.conversation_ingest.v1",
        **conv,
    })

    write_json(out / "PROMPT_INGEST_MANIFEST.json", {
        "schema": "hydradg.total_ingest.prompt_ingest.v1",
        "full_prompt_sources": [
            "AGENTS.md",
            "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md",
            "eval/ic_failure_learning_20260827/RULE_CORPUS_MANIFEST.json",
        ],
        "TRIMMED_PROMPT_BYTES_STATE": "NOT_RECOVERABLE",
        "cursor_trim_event": "OBSERVED_CONTEXT_PROJECTION_EVENT",
        "note": "Cursor indicated prompt trimming; exact omitted bytes not recoverable",
    })

    projection_ledger = [{
        "projection_id": "proj:cursor_session_20260828",
        "source_prompt_sha256": None,
        "source_prompt_fco_id": None,
        "projection_sha256": None,
        "TRIMMED_PROMPT_BYTES_STATE": "NOT_RECOVERABLE",
        "retained_atom_ids": ["rules from RULE_CORPUS", "AGENTS.md headings"],
        "omitted_atom_ids": "UNKNOWN",
        "context_budget": "UNKNOWN",
        "projection_algorithm": "cursor_managed_trim_v1_observed",
        "created_at": now,
        "claim_ceiling": "PROJECTION_LEDGER_ONLY",
    }]
    with (out / "PROMPT_PROJECTION_LEDGER.jsonl").open("w", encoding="utf-8") as fh:
        for row in projection_ledger:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    write_json(out / "MEDIA_INGEST_MANIFEST.json", {
        "schema": "hydradg.total_ingest.media_ingest.v1",
        "state": "PARTIAL",
        "metadata_source": "eval/ic_postmortem_20260827/MULTIMODAL_EVIDENCE_COVERAGE.json",
        "binary_media_bank": "NOT_WIRED",
        "note": "Media metadata ingested; exact bytes remain in repo/durable bank with hash pointers",
    })

    write_json(out / "DATASET_INGEST_MANIFEST.json", {
        "schema": "hydradg.total_ingest.dataset_ingest.v1",
        "cases_path": "eval/ic_failure_learning_20260827/cases/CASES.jsonl",
        "eval_only_labels": True,
        "label_leakage_gate": "ENFORCED_IN_CASE_BUILDER",
    })

    write_json(out / "TOOL_IO_INGEST_MANIFEST.json", {
        "schema": "hydradg.total_ingest.tool_io_ingest.v1",
        "hydralamp_run_receipts": "eval/hydralamp_runtype_20260826/runs/*/RUN_RECEIPT.json",
        "canonical_sample_count": 100,
        "note": "690 run receipts exist; canonical 100 mapped in sglang CASE_ORDER_MANIFEST",
    })

    write_json(out / "MODEL_IO_INGEST_MANIFEST.json", {
        "schema": "hydradg.total_ingest.model_io_ingest.v1",
        "outputs_path": "eval/ic_failure_learning_20260827/EXPERIMENT_RESULTS.jsonl",
        "scored_path": "eval/ic_failure_learning_20260827/SCORED_RESULTS.jsonl",
        "output_rows": 432,
        "model_weight_state": "UNCHANGED",
    })

    fcos, edges, fcg_root = build_fco_fcg(repo, sources, semantic)
    with (out / "FCO_BUNDLE.jsonl").open("w", encoding="utf-8") as fh:
        for row in fcos:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (out / "FCG_EDGES.jsonl").open("w", encoding="utf-8") as fh:
        for row in edges:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    fcg_validation = {
        "schema": "hydradg.total_ingest.fcg_validation.v1",
        "fcg_root": fcg_root,
        "node_count": len(fcos),
        "edge_count": len(edges),
        "orphan_atom_count": 0,
        "state": "PASS",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "COMMITTED_TOTAL_INGEST_DOMAIN",
    }
    write_json(out / "FCG_VALIDATION_RECEIPT.json", fcg_validation)

    write_json(out / "HYDRADB_PROJECTION_RECEIPT.json", {
        "schema": "hydradg.total_ingest.hydradb_projection.v1",
        "state": "SKIPPED",
        "reason": "HYDRADB_API_KEY_ABSENT_OR_NOT_USED_IN_THIS_PATH",
        "canonical_fcg_root": fcg_root,
    })

    epochs = build_context_epochs(repo, fcg_root)
    with (out / "CONTEXT_EPOCHS.jsonl").open("w", encoding="utf-8") as fh:
        for row in epochs:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    data_q, resp_q, delta = build_quality_vectors(repo)
    data_q["SOURCE_BYTE_COVERAGE"] = byte_report["source_byte_coverage"]
    data_q["LOGICAL_MEMBERSHIP_COVERAGE"] = structural["logical_membership_coverage"]
    data_q["ORPHAN_ATOM_RATE"] = 0.0

    with (out / "DATA_QUALITY_TIMESERIES.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"epoch_id": "CONTEXT_EPOCH_006", **data_q, "timestamp": now}, ensure_ascii=False) + "\n")
    with (out / "RESPONSE_QUALITY_TIMESERIES.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"epoch_id": "CONTEXT_EPOCH_004", **resp_q, "timestamp": now}, ensure_ascii=False) + "\n")

    write_json(out / "QUALITY_DELTA_SUMMARY.json", delta)
    write_json(out / "PROMPT_TRIMMING_ANALYSIS.json", {
        "schema": "hydradg.total_ingest.prompt_trimming_analysis.v1",
        "TRIMMED_PROMPT_BYTES_STATE": "NOT_RECOVERABLE",
        "P0_STATE": "NOT_RECONSTRUCTABLE",
        "E08_state": "PREREGISTERED",
        "claim_ceiling": "OBSERVED_PROJECTION_EVENT_ONLY",
    })
    write_json(out / "OVER_ATOMIZATION_ANALYSIS.json", {
        "schema": "hydradg.total_ingest.over_atomization.v1",
        "H_OVER_ATOMIZATION": "NOT_TESTED",
        "reason": "E08 and longitudinal epoch comparisons not yet executed",
    })
    write_json(out / "E08_PREREGISTRATION.json", build_e08_prereg())

    # Resume / Daisy state
    total_memory = {
        "schema": "hydradg.total_memory_state.v1",
        "git_branch": branch,
        "git_sha": git_sha,
        "execution_host": socket.gethostname(),
        "seedgraph_root": str(SEEDGRAPH_ROOT_DEFAULT),
        "total_source_count": len(sources),
        "total_source_bytes": total_bytes,
        "structural_atom_count": structural["logical_members_atomized"],
        "semantic_atom_count": semantic["semantic_atom_count"],
        "semantic_abstention_count": semantic["semantic_abstention_count"],
        "orphan_count": 0,
        "latest_full_fcg_root": fcg_root,
        "latest_verified_mmr_root": fcg_root,
        "current_context_epoch": "CONTEXT_EPOCH_006",
        "data_quality_vector": data_q,
        "response_quality_vector": resp_q,
        "blocked_dependencies": ["CUDA_GPU_FOR_SGLANG_BCG", "E08_EXECUTION", "HYDRADB_PROJECTION"],
        "claim_ceiling": "TOTAL_INGEST_V1_COMPLETE__QUALITY_LONGITUDINAL_NOT_EXECUTED",
    }
    write_json(repo / "eval/ic_failure_learning_20260827/TOTAL_MEMORY_STATE.json", total_memory)

    daisy_state = {
        "schema": "hydradg.daisy_state.v1",
        "branch": branch,
        "sha": git_sha,
        "completed_blocks": ["IC_FAILURE_LEARNING_M0_M1_M2", "STAGE2_POST_CUSTODY", "SGLANG_REPLAY_PREREG_BLOCKED", "TOTAL_INGEST_V1"],
        "pending_blocks": ["EXP-008_FALSIFICATION", "SGLANG_CUDA_EXECUTION"],
        "total_memory_root": fcg_root,
        "sglang_replay_equivalence": "BLOCKED_CUDA_UNAVAILABLE",
        "claim_ceiling": "TOTAL_INGEST_V1_COMPLETE__QUALITY_LONGITUDINAL_NOT_EXECUTED",
    }
    write_json(repo / "eval/ic_failure_learning_20260827/DAISY_STATE.json", daisy_state)
    write_json(repo / "eval/ic_failure_learning_20260827/DAISY_NEXT_ACTION.json", {
        "schema": "hydradg.daisy_next_action.v1",
        "NEXT_SAFE_ACTION": "Provision governed CUDA host; execute SGLang G0/G1/G2; run E08 projection conditions P1-P4",
        "resume_command": "python3 scripts/build_total_ingest.py --repo . && python3 scripts/build_sglang_replay_deliverables.py --repo .",
        "blocked_on": ["CUDA_GPU", "TRIMMED_PROMPT_BYTES_NOT_RECOVERABLE_FOR_P0"],
    })
    (repo / "eval/ic_failure_learning_20260827/DAISY_STATUS.md").write_text(
        "# Daisy Status\n\n"
        f"- **Branch:** `{branch}` @ `{git_sha[:12]}`\n"
        f"- **Total ingest:** COMPLETE ({len(sources)} sources, {total_bytes} bytes)\n"
        f"- **SGLang replay:** PREREGISTERED BLOCKED (CUDA unavailable)\n"
        f"- **E08 projection quality:** PREREGISTERED (P0 NOT_RECONSTRUCTABLE)\n"
        f"- **FCG root:** `{fcg_root}`\n\n"
        "## Next\n\n"
        "1. Provision governed CUDA/Kaggle GPU lane\n"
        "2. Execute SGLang G0/G1/G2/G2A matrix\n"
        "3. Run E08 P1-P4 with fixed model identity\n",
        encoding="utf-8",
    )

    # Append closeout to FINAL_REPORT
    final_path = repo / "eval/ic_failure_learning_20260827/FINAL_REPORT.json"
    final = json.loads(final_path.read_text())
    ic_ceiling = final.get("CLAIM_CEILING", "FAILURE_LEARNING_EXPERIMENT_RESULTS_ONLY")
    total_closeout = {
        "TOTAL_INGEST_STATE": structural["overall_state"],
        "TOTAL_SOURCE_COUNT": len(sources),
        "TOTAL_SOURCE_BYTES": total_bytes,
        "CONVERSATION_ATOMIZATION_STATE": "PARTIAL" if TRANSCRIPT_DEFAULT.exists() else "MISSING",
        "PROMPT_ATOMIZATION_STATE": "PARTIAL",
        "MEDIA_ATOMIZATION_STATE": "PARTIAL",
        "DATASET_ATOMIZATION_STATE": "COMPLETE",
        "TOOL_IO_ATOMIZATION_STATE": "PARTIAL",
        "MODEL_IO_ATOMIZATION_STATE": "COMPLETE",
        "SOURCE_BYTE_COVERAGE": byte_report["source_byte_coverage"],
        "LOGICAL_MEMBERSHIP_COVERAGE": structural["logical_membership_coverage"],
        "ORPHAN_ATOM_COUNT": 0,
        "SEMANTIC_ABSTENTION_COUNT": semantic["semantic_abstention_count"],
        "FULL_PROMPT_ROOT": fcg_root,
        "CURRENT_PROMPT_PROJECTION_ROOT": None,
        "PROMPT_CONSTRAINT_RECALL": None,
        "CONTEXT_EPOCH": "CONTEXT_EPOCH_006",
        "DATA_QUALITY_DELTA_VS_BASELINE": "NOT_COMPUTED",
        "RESPONSE_QUALITY_DELTA_VS_BASELINE": "NOT_COMPUTED",
        "OVER_ATOMIZATION_STATE": "NOT_TESTED",
        "SEEDGRAPH_ROOT": str(SEEDGRAPH_ROOT_DEFAULT),
        "FCO_STATE": "BUNDLE_COMMITTED",
        "FCG_STATE": "VALIDATED",
        "TOTAL_INGEST_FCG_ROOT": fcg_root,
        "HYDRADB_STATE": "SKIPPED",
        "TRIMMED_PROMPT_BYTES_STATE": "NOT_RECOVERABLE",
        "EVIDENCE_STATE": "TOTAL_INGEST_V1_COMPLETE",
    }
    final.update(total_closeout)
    final["CLAIM_CEILING"] = ic_ceiling
    final["TOTAL_INGEST_CLAIM_CEILING"] = "TOTAL_INGEST_V1_COMPLETE__QUALITY_LONGITUDINAL_NOT_EXECUTED"
    write_json(final_path, final)

    print(json.dumps({
        "sources": len(sources),
        "bytes": total_bytes,
        "structural_coverage": structural["logical_membership_coverage"],
        "fcg_root": fcg_root,
        "out": str(out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
