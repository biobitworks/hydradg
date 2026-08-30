#!/usr/bin/env python3
"""PLAN_CHECK for ANB Live Empirical V1 plan packets.

Fail-closed. Does not execute experiments. Does not promote claims.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SECRETISH = re.compile(
    r"(?i)(sk-[A-Za-z0-9]{16,}|api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}|Bearer\s+[A-Za-z0-9\-._~+/]+=*)"
)
EXPECTED_BRANCH = "hack-hydra/agent-native-builders-20260826"
EXPECTED_HOST = "magicSTUDIObox.local"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(msg: str) -> None:
    raise ValueError(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_secrets(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if SECRETISH.search(text):
        fail(f"secret-like token present in {path}")
    # Never allow literal key material fields.
    doc = json.loads(text)
    blob = json.dumps(doc)
    for banned in ("TAVILY_API_KEY=", "RUNTYPE_API_KEY=", "IMMERSIVE_COMMONS_MODEL_KEY="):
        if banned in blob:
            fail(f"env assignment with secret name present in {path}")


def check_git_binding() -> dict:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=REPO, text=True).strip()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    host = subprocess.check_output(["hostname"], text=True).strip()
    if branch != EXPECTED_BRANCH:
        fail(f"branch mismatch expected={EXPECTED_BRANCH} actual={branch}")
    if host != EXPECTED_HOST:
        fail(f"host mismatch expected={EXPECTED_HOST} actual={host}")
    return {"branch": branch, "head": head, "host": host}


def check_track01(plan: dict) -> None:
    trials = plan.get("frozen_trials")
    if not isinstance(trials, list) or len(trials) != 10:
        fail("Track01 must freeze exactly 10 trial IDs")
    ids = [t.get("trial_id") for t in trials]
    if len(set(ids)) != 10:
        fail("Track01 trial IDs must be unique")
    for t in trials:
        if t.get("initial_knowledge") != "PUBLIC_HYDRADG_DOMAIN_ONLY":
            fail(f"{t.get('trial_id')} initial_knowledge not PUBLIC_HYDRADG_DOMAIN_ONLY")
        for banned in ("preconfigured_mcp_endpoint", "preconfigured_tool_catalog", "preconfigured_private_api_url", "preconfigured_hydradg_credential"):
            if t.get(banned) is not False:
                fail(f"{t.get('trial_id')} must set {banned}=false")
    sem = plan.get("credential_semantics") or {}
    required_flags = [
        "DOMAIN_DISCOVERED",
        "AGENT_MANIFEST_DISCOVERED",
        "MCP_OR_MACHINE_SURFACE_DISCOVERED",
        "CREDENTIAL_BOOTSTRAP_METHOD",
        "CREDENTIAL_DISCOVERED",
        "CREDENTIAL_ACQUIRED",
        "PREEXISTING_CREDENTIAL_USED",
        "TOOLS_DISCOVERED",
        "BENIGN_REAL_WRITE_COMPLETED",
        "PROPOSAL_QUARANTINED",
        "CUSTODY_RECEIPT_RETURNED",
        "CUSTODY_RECEIPT_VERIFIED",
        "UNAUTHORIZED_PRIVATE_READ_DENIED",
        "UNAUTHORIZED_CANONICAL_WRITE_DENIED",
    ]
    for flag in required_flags:
        if flag not in sem.get("per_trial_observation_fields", []):
            fail(f"Track01 missing observation field {flag}")
    if not sem.get("preexisting_sponsor_model_credential_not_counted_as_hydradg_cold_start_acquisition"):
        fail("Track01 credential acquisition semantics ambiguous")
    tp = plan.get("timeout_retry_policy") or {}
    if not isinstance(tp.get("trial_timeout_seconds"), int) or tp["trial_timeout_seconds"] < 1:
        fail("Track01 timeout unresolved")
    if not isinstance(tp.get("max_retries"), int) or tp["max_retries"] < 0:
        fail("Track01 retry policy unresolved")
    fallback = plan.get("tenki_fallback") or {}
    for key in ("fresh_isolated_profile", "no_hydradg_state", "no_cached_mcp_endpoint", "no_hydradg_credentials", "no_previous_conversation_state"):
        if fallback.get(key) is not True:
            fail(f"Track01 Tenki fallback missing {key}=true")


def check_track02(plan: dict) -> None:
    items = plan.get("frozen_work_items")
    if not isinstance(items, list) or len(items) != 5:
        fail("Track02 must freeze exactly five work items")
    imap = plan.get("interruption_mapping") or {}
    expected = {
        "WORK_ITEM_01": "interrupt after github_intake",
        "WORK_ITEM_02": "interrupt after runtype_agent_step",
        "WORK_ITEM_03": "interrupt after tavily_retrieval",
        "WORK_ITEM_04": "interrupt after hydradg_proposal",
        "WORK_ITEM_05": "interrupt before github_writeback",
    }
    for wid, label in expected.items():
        if imap.get(wid) != label:
            fail(f"Track02 interruption mapping unresolved for {wid}")
    for item in items:
        for key in ("work_item_id", "source_url", "query_definition", "content_sha256"):
            if not item.get(key):
                fail(f"Track02 work item missing {key}")
        if not HEX64.fullmatch(item["content_sha256"]):
            fail(f"Track02 bad content hash for {item.get('work_item_id')}")
    preserve = set(plan.get("per_item_preserve_fields") or [])
    for req in (
        "original_work_unit_id",
        "retrieval_receipt",
        "runtype_execution_id",
        "tavily_source_result_references",
        "hydradg_quarantine_proposal_id",
        "custody_receipt",
        "resume_checkpoint_id",
        "final_github_writeback_reference",
        "duplicate_write_count",
        "null_failure_timeout_abstention_state",
    ):
        if req not in preserve:
            fail(f"Track02 missing preserve field {req}")
    if plan.get("tavily_state") != "CONFIRMED":
        fail("Track02 Tavily state must be CONFIRMED")
    if plan.get("tavily_key_in_git_or_receipts") is not False:
        fail("Track02 must forbid Tavily key in git/receipts")


def check_runtype(plan: dict) -> None:
    suite = plan.get("eval_suite") or {}
    cases = suite.get("cases")
    if not isinstance(cases, list) or not (12 <= len(cases) <= 20):
        fail("Runtype eval cases unresolved (need 12-20)")
    ids = [c.get("case_id") for c in cases]
    if len(set(ids)) != len(cases):
        fail("Runtype case IDs must be unique")
    for c in cases:
        if not HEX64.fullmatch(str(c.get("content_sha256", ""))):
            fail(f"Runtype case content hash unresolved: {c.get('case_id')}")
    for label in ("variant_a", "variant_b"):
        v = plan.get(label) or {}
        for key in ("variant_id", "provider", "model_requested", "config_id", "prompt_config_version", "tool_set_id"):
            if not v.get(key):
                fail(f"Runtype {label} unresolved field {key}")
    for key in (
        "runtype_agent_version_config",
        "deterministic_flow_version_config",
        "mcp_surface_config_identity",
        "scorer_implementation_sha256",
        "timeout_seconds",
        "retry_count",
        "failure_handling",
        "missing_output_handling",
        "cost_accounting_method",
    ):
        if plan.get(key) in (None, "", []):
            fail(f"Runtype unresolved {key}")
    if not HEX64.fullmatch(str(plan["scorer_implementation_sha256"])):
        fail("Runtype scorer identity unresolved")
    scorer_path = REPO / plan["scorer_path"]
    if not scorer_path.is_file():
        fail("Runtype scorer path missing")
    if sha256_file(scorer_path) != plan["scorer_implementation_sha256"]:
        fail("Runtype scorer SHA256 mismatch vs frozen plan")
    if plan.get("no_variant_mutation_after_execute_start") is not True:
        fail("Runtype must freeze no-variant-mutation policy")
    if plan.get("preserve_runtype_execution_ids") is not True:
        fail("Runtype must require execution IDs")


def check_plan(path: Path) -> str:
    scan_secrets(path)
    plan = load(path)
    if plan.get("schema") != "hydradg.anb_live.plan.v1":
        fail("unsupported plan schema")
    if plan.get("phase") != "PLAN":
        fail("phase must be PLAN")
    if plan.get("execution_allowed") is not False:
        fail("execution_allowed must be false until PLAN_CHECK + operator execute gate")
    if plan.get("expected_host") != EXPECTED_HOST:
        fail("expected_host must be magicSTUDIObox.local")
    track = plan.get("track_id")
    if track == "ANB_TRACK01_COLD_START_V1":
        check_track01(plan)
    elif track == "ANB_TRACK02_RESUMABLE_BOUNDARY_V1":
        check_track02(plan)
    elif track == "ANB_RUNTYPE_PRODUCT_EVAL_V1":
        check_runtype(plan)
    else:
        fail(f"unknown track_id {track}")
    return track


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} <plan.json> [<plan2.json> ...]", file=sys.stderr)
        return 2
    rc = 0
    try:
        binding = check_git_binding()
        print(f"PLAN_CHECK_GIT_BINDING=PASS branch={binding['branch']} host={binding['host']} head={binding['head']}")
    except Exception as exc:
        print(f"PLAN_CHECK_GIT_BINDING=FAIL reason={exc}", file=sys.stderr)
        return 1
    for raw in argv[1:]:
        path = Path(raw)
        try:
            track = check_plan(path if path.is_absolute() else REPO / path)
            print(f"PLAN_CHECK=PASS track={track} path={path}")
        except Exception as exc:
            rc = 1
            print(f"PLAN_CHECK=FAIL path={path} reason={exc}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
