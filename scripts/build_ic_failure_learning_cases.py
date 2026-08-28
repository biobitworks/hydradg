#!/usr/bin/env python3
"""Generate frozen HydraLamp × IC failure-learning experiment cases.

Blind cases are constructed only from the exact submitted six-field payload plus explicit
counterfactual treatment fixtures. The postmortem answer is never copied into E01-E04 cases.
E05 exposes candidate evidence strings but strips audit status/answer fields.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

EXPECTED_PAYLOAD_SHA = "230bd00a6d95e57d423dd26d2be18512c2041030f1b7007bdb0374a85722611d"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def case(case_id: str, family: str, condition: str, payload: Any, task: str, blind: bool) -> dict[str, Any]:
    body = {
        "case_id": case_id,
        "experiment_family": family,
        "condition": condition,
        "blind": blind,
        "task": task,
        "input": payload,
    }
    body["case_payload_sha256"] = sha(canon(body))
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/cases/CASES.jsonl")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()

    submitted_path = repo / "eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json"
    submitted_raw = submitted_path.read_bytes()
    if sha(submitted_raw) != EXPECTED_PAYLOAD_SHA:
        raise SystemExit("STOP: frozen submission payload hash mismatch")
    submitted = json.loads(submitted_raw)

    rows: list[dict[str, Any]] = []

    blind_task = (
        "Act as a cold hackathon pre-read. Using only the supplied submission fields, identify likely "
        "rubric risks, whether project origin/new work is legible, missing judge-visible evidence, and "
        "the first corrective action. Do not assume hidden files or media exist."
    )
    rows.append(case("E01-T0", "E01", "ACTUAL_SIX_FIELDS", submitted, blind_task, True))

    # E02 origin ablation.
    origin_treatments: list[tuple[str, dict[str, Any]]] = []
    origin_treatments.append(("T0_ACTUAL", deepcopy(submitted)))

    t1 = deepcopy(submitted)
    t1["origin_disclosure"] = {
        "hydralamp_first_commit": "757f3fa7 on 2026-08-26 14:36 PDT",
        "hydradg_substrate_first_commit": "e4558026 on 2026-08-18"
    }
    origin_treatments.append(("T1_ORIGIN_DATE", t1))

    t2 = deepcopy(submitted)
    t2["repo_url"] = "https://github.com/biobitworks/hydradg/tree/hack-hydra/hydralamp-20260826"
    origin_treatments.append(("T2_BRANCH_QUALIFIED_REPO", t2))

    t3 = deepcopy(submitted)
    t3["what_is_new_vs_prior_work"] = (
        "HydraDG is the pre-existing substrate. HydraLamp is the Aug 26-27 agent-native control-plane "
        "delta: cold-agent API surface, bounded authorization, governed execution, replay/refusal receipts, "
        "and sponsor integrations."
    )
    origin_treatments.append(("T3_DELTA_SUMMARY", t3))

    t4 = deepcopy(t3)
    t4.update(t1)
    t4["repo_url"] = t2["repo_url"]
    origin_treatments.append(("T4_ALL_ORIGIN_FIXES", t4))

    for idx, (condition, payload) in enumerate(origin_treatments):
        rows.append(case(f"E02-{idx}", "E02", condition, payload,
                         "Classify product origin as DISTINCT_HACKATHON_DELTA, PREEXISTING_PROJECT, or AMBIGUOUS using only this fixture.", True))

    # E03 evidence surfacing ablation.
    evidence_treatments: list[tuple[str, dict[str, Any]]] = [("T0_NO_VAULT", deepcopy(submitted))]
    additions = [
        ("T1_START_HERE", {"vault_visible": ["00_START_HERE.md"]}),
        ("T2_HERO_CONTACT_SHEET", {"vault_visible": ["00_START_HERE.md", "HYDRALAMP_SUBMISSION_HERO.png", "contact-sheet.png"]}),
        ("T3_VIDEO", {"vault_visible": ["00_START_HERE.md", "HYDRALAMP_SUBMISSION_HERO.png", "contact-sheet.png", "demo.mp4"]}),
        ("T4_SPONSOR_RECEIPTS", {"vault_visible": ["00_START_HERE.md", "HYDRALAMP_SUBMISSION_HERO.png", "contact-sheet.png", "demo.mp4", "sponsor-live-error-receipts.json"]}),
        ("T5_CURATED_VAULT", {"vault_visible": [
            "00_START_HERE.md", "02_WHAT_IS_NEW_VS_PRIOR_WORK.md", "HYDRALAMP_SUBMISSION_HERO.png",
            "contact-sheet.png", "demo.mp4", "agent-surface.md", "origin-timeline.md",
            "sponsor-live-error-receipts.json", "golden-path-receipt.json", "submission-payload-sha256.txt"
        ]})
    ]
    for condition, add in additions:
        payload = deepcopy(submitted)
        payload["folder_id"] = "COUNTERFACTUAL_VISIBLE_VAULT"
        payload.update(add)
        evidence_treatments.append((condition, payload))

    for idx, (condition, payload) in enumerate(evidence_treatments):
        rows.append(case(f"E03-{idx}", "E03", condition, payload,
                         "Evaluate judge-visible evidence completeness and cold-start/demo risk. Do not treat file names as proof of scientific claims.", True))

    # E04 agent surface legibility.
    surface_treatments = [
        ("T0_PROSE_ONLY", {"agent_surface": submitted["agent_surface"]}),
        ("T1_STRUCTURED_ENDPOINT_TABLE", {"agent_surface_table": [
            {"method": "GET/POST", "path": "/api/hydralamp/run", "purpose": "start governed run"},
            {"method": "GET", "path": "/api/hydralamp/status?run_id=", "purpose": "read custody status"},
            {"method": "GET", "path": "/api/hydralamp/stream?run_id=", "purpose": "stream custody events"}
        ]}),
        ("T2_WELL_KNOWN_FIXTURE", {"well_known_agent_fixture": {
            "discovery": "/.well-known/ai-agent.json",
            "run": "/api/hydralamp/run",
            "status": "/api/hydralamp/status?run_id=",
            "auth": "machine credential required for consequential live actions"
        }}),
        ("T3_START_HERE_FLOW", {"cold_start": [
            "GET /.well-known/ai-agent.json",
            "obtain/verify allowed machine credential",
            "POST /api/hydralamp/run with bounded action",
            "GET /api/hydralamp/status?run_id= and verify receipt"
        ]}),
        ("T4_AUTH_ACTION_RECEIPT", {"cold_start": {
            "discover": "GET /.well-known/ai-agent.json",
            "authenticate": "obtain scoped machine credential",
            "consequential_action": "POST /api/hydralamp/run",
            "verify": "GET /api/hydralamp/status?run_id=",
            "negative_control": "attempt unauthorized write and require explicit refusal receipt"
        }})
    ]
    for idx, (condition, payload) in enumerate(surface_treatments):
        rows.append(case(f"E04-{idx}", "E04", condition, payload,
                         "List the first three concrete actions a cold machine agent should take. Put any guessed unavailable action in invented_capabilities.", True))

    # E05 diagnosis: expose evidence strings but strip audit statuses and answer ranking.
    divergence_path = repo / "eval/ic_postmortem_20260827/EARLIEST_DIVERGENCE.json"
    divergence = json.loads(divergence_path.read_text(encoding="utf-8"))
    diagnosis_input = {
        key.split("_", 1)[0]: {
            "candidate": key,
            "evidence": value["evidence"]
        }
        for key, value in sorted(divergence["candidates_tested"].items())
    }
    rows.append(case("E05-T0", "E05", "CANDIDATE_EVIDENCE_WITHHELD_LABELS", diagnosis_input,
                     "Rank A-G by causal priority and choose the earliest divergent dependency. Audit status labels and ground-truth ranking are withheld.", False))

    # E06 protocol repair baseline vs governed protocol availability.
    rubric_path = repo / "eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json"
    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    base_input = {"event_rubric": rubric, "actual_submission": submitted}
    rows.append(case("E06-T0", "E06", "NO_FAILURE_LEARNING_PROTOCOL", base_input,
                     "Produce an ordered pre-submission workflow intended to maximize judge-visible evidence and prevent avoidable submission-process failures.", False))

    protocol_text = (repo / "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md").read_text(encoding="utf-8")
    treatment_input = {**base_input, "governed_failure_learning_protocol": protocol_text}
    rows.append(case("E06-T1", "E06", "WITH_FAILURE_LEARNING_PROTOCOL", treatment_input,
                     "Produce an ordered pre-submission workflow using the supplied governed protocol. Do not submit while required judge evidence remains unsurfaced unless a human waiver is explicit.", False))

    out = (repo / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    manifest = {
        "schema": "hydradg.ic_failure_learning.case_manifest.v1",
        "case_count": len(rows),
        "cases_sha256": sha(out.read_bytes()),
        "blind_case_count": sum(1 for row in rows if row["blind"]),
        "nonblind_case_count": sum(1 for row in rows if not row["blind"]),
        "historical_submission_payload_sha256": EXPECTED_PAYLOAD_SHA,
        "ground_truth_in_case_payload": false if False else False,
        "claim_ceiling": "EXPERIMENT_FIXTURE_ONLY_NOT_MODEL_RESULT"
    }
    (out.parent / "CASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
