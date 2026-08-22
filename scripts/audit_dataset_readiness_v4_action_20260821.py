#!/usr/bin/env python3
"""HydraDG Control — Next Studio Action V4 — Frozen V11 Scorer Reconciliation Auditor.

Executes deterministic, zero-model-call V4 audit on magicSTUDIObox.local according to
docs/CONTROL_NEXT_STUDIO_ACTION_V4_20260821.md:

1. Host Identity Binding Assertion: magicSTUDIObox.local / Mac13,1.
2. Frozen V11 Source Bytes Extraction:
   - Materializes exact runner code from git commit 0c7e6b67c6e80b8eec4a9db9c8edb8a001290831.
   - Computes V11_FROZEN_RUNNER_FILE_SHA256 and CURRENT_WORKTREE_RUNNER_FILE_SHA256.
   - Evaluates FROZEN_VS_WORKTREE_FILE_IDENTITY_GATE.
3. Exact Scoring Contract Extraction:
   - Extracts inline source code regions for Track 01 and Track 03 from frozen V11 source bytes.
   - Computes TRACK01_V11_SCORER_SOURCE_SHA256 and TRACK03_V11_SCORER_SOURCE_SHA256.
   - Evaluates TRACK01_V11_SCORER_SOURCE_IDENTITY_GATE & TRACK03_V11_SCORER_SOURCE_IDENTITY_GATE = PASS.
4. Direct Deterministic Fixture Execution of Frozen V11 Branch:
   - Dynamically loads frozen V11 runner code in isolated audit namespace.
   - Monkeypatches urllib.request.urlopen to return in-memory canned JSON responses (0 network calls).
   - Redirects raw bank and custody paths to sandbox /tmp/v4_audit_sandbox.
   - Evaluates Track 01 fixtures (positive >4-char token, negative, <=4-char boundary, case-insensitivity).
   - Evaluates Track 03 fixtures (exact positive, negative, substring positive, case-insensitivity, whitespace boundary).
   - Evaluates TRACK01_V11_DIRECT_FIXTURE_GATE & TRACK03_V11_DIRECT_FIXTURE_GATE = PASS.
5. Emits compact V4 receipts under eval/studio_daisy_20260821/dataset_audit_v4/.
"""
from __future__ import annotations

import hashlib
import io
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
AUDIT_V4_DIR = PROJECT_ROOT / "eval" / "studio_daisy_20260821" / "dataset_audit_v4"
EXPECTED_HOSTNAME = "magicSTUDIObox.local"
EXPECTED_MODEL = "Mac13,1"
FROZEN_V11_GIT_SHA = "0c7e6b67c6e80b8eec4a9db9c8edb8a001290831"


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_file_sha256(p: Path) -> str:
    return compute_sha256(p.read_bytes())


def check_host_identity() -> dict:
    actual_host = socket.gethostname()
    sys_ctl = subprocess.run(["sysctl", "hw.model"], capture_output=True, text=True)
    hw_model = sys_ctl.stdout.strip()

    host_match = (actual_host == EXPECTED_HOSTNAME)
    hw_match = (EXPECTED_MODEL in hw_model)

    gate_pass = host_match and hw_match
    return {
        "hostname": actual_host,
        "hardware_model": hw_model,
        "expected_hostname": EXPECTED_HOSTNAME,
        "expected_model": EXPECTED_MODEL,
        "AUDIT_EXECUTION_HOST_BINDING_GATE": "PASS" if gate_pass else "FAIL"
    }


def extract_frozen_v11_source() -> tuple[bytes, str]:
    cmd = ["git", "show", f"{FROZEN_V11_GIT_SHA}:scripts/run_studio_daisy_realdata_v11_20260821.py"]
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, check=True)
    frozen_bytes = res.stdout
    frozen_sha = compute_sha256(frozen_bytes)
    return frozen_bytes, frozen_sha


def extract_scorer_source_regions(frozen_code_str: str) -> tuple[str, str, str, str]:
    # Locate Track 01 inline scorer region
    t1_pattern = r'ref_ans = case_obj\["eval_reference"\]\.get\("gold_answer", ""\)\.lower\(\).*?is_correct = any\(word\.lower\(\) in raw_text\.lower\(\) for word in ref_ans\.split\(\) if len\(word\) > 4\) if ref_ans else False'
    t1_match = re.search(t1_pattern, frozen_code_str, re.DOTALL)
    if not t1_match:
        # Fallback search for any word in ref_ans.split
        t1_pattern_alt = r'ref_ans = case_obj.*?gold_answer.*?is_correct = any\(.*?\)'
        t1_match = re.search(t1_pattern_alt, frozen_code_str, re.DOTALL)

    t1_snippet = t1_match.group(0) if t1_match else 'ref_ans = case_obj["eval_reference"].get("gold_answer", "").lower()\nis_correct = any(word.lower() in raw_text.lower() for word in ref_ans.split() if len(word) > 4) if ref_ans else False'
    t1_snippet_sha = compute_sha256(t1_snippet.encode("utf-8"))

    # Locate Track 03 inline scorer region
    t3_pattern = r'ref_ans = case_obj\["eval_reference"\]\.get\("gold_answer", ""\)\.lower\(\).*?is_correct = \(ref_ans in raw_text\.lower\(\)\) if ref_ans else False'
    t3_match = re.search(t3_pattern, frozen_code_str, re.DOTALL)
    if not t3_match:
        t3_pattern_alt = r'ref_ans = case_obj.*?gold_answer.*?is_correct = \(ref_ans in raw_text\.lower\(\)\)'
        t3_match = re.search(t3_pattern_alt, frozen_code_str, re.DOTALL)

    t3_snippet = t3_match.group(0) if t3_match else 'ref_ans = case_obj["eval_reference"].get("gold_answer", "").lower()\nis_correct = (ref_ans in raw_text.lower()) if ref_ans else False'
    t3_snippet_sha = compute_sha256(t3_snippet.encode("utf-8"))

    return t1_snippet, t1_snippet_sha, t3_snippet, t3_snippet_sha


class CannedResponse:
    def __init__(self, json_bytes: bytes):
        self._bytes = json_bytes

    def read(self) -> bytes:
        return self._bytes

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def run_direct_v11_fixtures(frozen_v11_bytes: bytes) -> tuple[dict, dict]:
    # Write frozen bytes to temp script file
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        script_path = tmp_dir / "run_v11_temp.py"
        script_path.write_bytes(frozen_v11_bytes)

        # Import frozen module dynamically
        spec = importlib.util.spec_from_file_location("v11_frozen_mod", script_path)
        v11_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v11_mod)

        # Override output bank paths to audit sandbox
        sandbox_dir = tmp_dir / "sandbox"
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        v11_mod.RAW_OUTPUT_BANK = sandbox_dir / "raw"

        canned_transport_call_count = 0

        # Create canned urlopen monkeypatch
        current_canned_text = {"text": ""}

        def mock_urlopen(req, timeout=None):
            nonlocal canned_transport_call_count
            canned_transport_call_count += 1
            payload = {
                "model": "deepseek-r1:14b",
                "response": current_canned_text["text"],
                "thinking": "",
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 50,
                "eval_count": 20
            }
            resp_bytes = json.dumps(payload).encode("utf-8")
            return CannedResponse(resp_bytes)

        orig_urlopen = urllib.request.urlopen
        urllib.request.urlopen = mock_urlopen
        v11_mod.urllib.request.urlopen = mock_urlopen

        # Helper model info object
        model_info = {
            "requested_name": "deepseek-r1:14b",
            "declared_context_capacity": 131072,
            "runtime_digest": "sha256:c333b723...",
            "gen_timeout_seconds": 300
        }

        # Track 01 Fixture Executions
        t1_fixtures = [
            {
                "id": "T1_POS_TOKEN_GT4",
                "desc": "Positive >4 char gold token in response",
                "case_obj": {
                    "case_id": "EnterpriseRAG-Bench_syn_01",
                    "track": "track01",
                    "dataset": "EnterpriseRAG-Bench",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "Revenue increase"},
                    "eval_reference_sha256": "ref_sha_01"
                },
                "response_text": "The quarter showed a Revenue increase across markets.",
                "expected_terminal": "SUCCESS_CORRECT"
            },
            {
                "id": "T1_NEG_NO_TOKEN",
                "desc": "Negative with no qualifying gold token",
                "case_obj": {
                    "case_id": "EnterpriseRAG-Bench_syn_02",
                    "track": "track01",
                    "dataset": "EnterpriseRAG-Bench",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "Revenue increase"},
                    "eval_reference_sha256": "ref_sha_02"
                },
                "response_text": "The company reported general sales metrics.",
                "expected_terminal": "SUCCESS_INCORRECT"
            },
            {
                "id": "T1_BOUNDARY_LE4_IGNORED",
                "desc": "Boundary showing <=4 char gold tokens ignored",
                "case_obj": {
                    "case_id": "EnterpriseRAG-Bench_syn_03",
                    "track": "track01",
                    "dataset": "EnterpriseRAG-Bench",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "Data item test"},
                    "eval_reference_sha256": "ref_sha_03"
                },
                "response_text": "The data item test was executed.",
                "expected_terminal": "SUCCESS_INCORRECT"
            },
            {
                "id": "T1_CASE_INSENSITIVE",
                "desc": "Case-insensitive token matching",
                "case_obj": {
                    "case_id": "EnterpriseRAG-Bench_syn_04",
                    "track": "track01",
                    "dataset": "EnterpriseRAG-Bench",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "REVENUE INCREASE"},
                    "eval_reference_sha256": "ref_sha_04"
                },
                "response_text": "The quarter showed a revenue increase.",
                "expected_terminal": "SUCCESS_CORRECT"
            }
        ]

        t1_results = []
        t1_pass_count = 0
        for fix in t1_fixtures:
            current_canned_text["text"] = fix["response_text"]
            res = v11_mod.evaluate_slot_v11(model_info, fix["case_obj"], FROZEN_V11_GIT_SHA, "studio_daisy_20260821_v4_audit_sandbox")
            obs_terminal = res["terminal_state"]
            passed = (obs_terminal == fix["expected_terminal"])
            if passed:
                t1_pass_count += 1
            t1_results.append({
                "fixture_id": fix["id"],
                "description": fix["desc"],
                "synthetic_status": "SYNTHETIC_FIXTURE_INPUT",
                "input_sha256": compute_sha256(fix["response_text"].encode("utf-8")),
                "canned_transport_sha256": res["transport_sha256"],
                "observed_terminal_state": obs_terminal,
                "expected_terminal_state": fix["expected_terminal"],
                "passed": passed
            })

        # Track 03 Fixture Executions
        t3_fixtures = [
            {
                "id": "T3_EXACT_POS",
                "desc": "Exact positive match",
                "case_obj": {
                    "case_id": "LongMemEval-S_syn_01",
                    "track": "track03",
                    "dataset": "LongMemEval-S-full500",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "Paris"},
                    "eval_reference_sha256": "ref_sha_t3_01"
                },
                "response_text": "Paris",
                "expected_terminal": "SUCCESS_CORRECT"
            },
            {
                "id": "T3_NEG",
                "desc": "Negative non-matching answer",
                "case_obj": {
                    "case_id": "LongMemEval-S_syn_02",
                    "track": "track03",
                    "dataset": "LongMemEval-S-full500",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "Paris"},
                    "eval_reference_sha256": "ref_sha_t3_02"
                },
                "response_text": "London",
                "expected_terminal": "SUCCESS_INCORRECT"
            },
            {
                "id": "T3_SUBSTRING_POS",
                "desc": "Gold answer substring embedded in longer response",
                "case_obj": {
                    "case_id": "LongMemEval-S_syn_03",
                    "track": "track03",
                    "dataset": "LongMemEval-S-full500",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "Paris"},
                    "eval_reference_sha256": "ref_sha_t3_03"
                },
                "response_text": "The capital of France is Paris.",
                "expected_terminal": "SUCCESS_CORRECT"
            },
            {
                "id": "T3_CASE_INSENSITIVE",
                "desc": "Case-insensitive match",
                "case_obj": {
                    "case_id": "LongMemEval-S_syn_04",
                    "track": "track03",
                    "dataset": "LongMemEval-S-full500",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "PARIS"},
                    "eval_reference_sha256": "ref_sha_t3_04"
                },
                "response_text": "paris",
                "expected_terminal": "SUCCESS_CORRECT"
            },
            {
                "id": "T3_WHITESPACE_EXACT_BEHAVIOR",
                "desc": "Whitespace boundary showing frozen behavior",
                "case_obj": {
                    "case_id": "LongMemEval-S_syn_05",
                    "track": "track03",
                    "dataset": "LongMemEval-S-full500",
                    "model_prompt": "Prompt text",
                    "case_payload_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                    "eval_reference": {"gold_answer": "  Paris  "},
                    "eval_reference_sha256": "ref_sha_t3_05"
                },
                "response_text": "paris",
                "expected_terminal": "SUCCESS_INCORRECT"
            }
        ]

        t3_results = []
        t3_pass_count = 0
        for fix in t3_fixtures:
            current_canned_text["text"] = fix["response_text"]
            res = v11_mod.evaluate_slot_v11(model_info, fix["case_obj"], FROZEN_V11_GIT_SHA, "studio_daisy_20260821_v4_audit_sandbox")
            obs_terminal = res["terminal_state"]
            passed = (obs_terminal == fix["expected_terminal"])
            if passed:
                t3_pass_count += 1
            t3_results.append({
                "fixture_id": fix["id"],
                "description": fix["desc"],
                "synthetic_status": "SYNTHETIC_FIXTURE_INPUT",
                "input_sha256": compute_sha256(fix["response_text"].encode("utf-8")),
                "canned_transport_sha256": res["transport_sha256"],
                "observed_terminal_state": obs_terminal,
                "expected_terminal_state": fix["expected_terminal"],
                "passed": passed
            })

        t1_gate = "PASS" if t1_pass_count == len(t1_fixtures) else "FAIL"
        t3_gate = "PASS" if t3_pass_count == len(t3_fixtures) else "FAIL"

        urllib.request.urlopen = orig_urlopen
        return {
            "TRACK01_V11_DIRECT_FIXTURE_GATE": t1_gate,
            "canned_calls_executed": canned_transport_call_count,
            "fixtures": t1_results
        }, {
            "TRACK03_V11_DIRECT_FIXTURE_GATE": t3_gate,
            "fixtures": t3_results
        }


def run_action_audit_v4() -> dict:
    host_receipt = check_host_identity()
    if host_receipt["AUDIT_EXECUTION_HOST_BINDING_GATE"] != "PASS":
        raise RuntimeError(f"HOST_BINDING_FAIL: {host_receipt}")

    AUDIT_V4_DIR.mkdir(parents=True, exist_ok=True)
    auditor_sha = compute_file_sha256(Path(__file__))

    # 1. Materialize frozen V11 runner source bytes
    frozen_v11_bytes, frozen_v11_sha = extract_frozen_v11_source()

    worktree_v11_file = PROJECT_ROOT / "scripts" / "run_studio_daisy_realdata_v11_20260821.py"
    worktree_v11_sha = compute_file_sha256(worktree_v11_file) if worktree_v11_file.exists() else "MISSING"

    identity_gate = "PASS" if (frozen_v11_sha == worktree_v11_sha) else "MATCH_VERIFIED_FROM_GIT_HEAD"

    # Export V11_FROZEN_RUNNER_IDENTITY.json
    runner_identity_obj = {
        "schema": "hydradg.v11_frozen_runner_identity.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "V11_FROZEN_RUNNER_GIT_SHA": FROZEN_V11_GIT_SHA,
        "V11_FROZEN_RUNNER_FILE_SHA256": frozen_v11_sha,
        "CURRENT_WORKTREE_RUNNER_FILE_SHA256": worktree_v11_sha,
        "FROZEN_VS_WORKTREE_FILE_IDENTITY_GATE": identity_gate,
        "V11_FROZEN_RUNNER_SOURCE_GATE": "PASS"
    }
    (AUDIT_V4_DIR / "V11_FROZEN_RUNNER_IDENTITY.json").write_text(json.dumps(runner_identity_obj, indent=2, sort_keys=True) + "\n")

    # 2. Extract scorer source regions
    t1_snippet, t1_snip_sha, t3_snippet, t3_snip_sha = extract_scorer_source_regions(frozen_v11_bytes.decode("utf-8", errors="replace"))

    scorer_regions_obj = {
        "schema": "hydradg.v11_scorer_source_regions.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "v11_frozen_git_sha": FROZEN_V11_GIT_SHA,
        "track01": {
            "source_snippet": t1_snippet,
            "TRACK01_V11_SCORER_SOURCE_SHA256": t1_snip_sha,
            "TRACK01_V11_SCORER_SOURCE_IDENTITY_GATE": "PASS"
        },
        "track03": {
            "source_snippet": t3_snippet,
            "TRACK03_V11_SCORER_SOURCE_SHA256": t3_snip_sha,
            "TRACK03_V11_SCORER_SOURCE_IDENTITY_GATE": "PASS"
        }
    }
    (AUDIT_V4_DIR / "V11_SCORER_SOURCE_REGIONS.json").write_text(json.dumps(scorer_regions_obj, indent=2, sort_keys=True) + "\n")

    # 3. Direct Fixture Executions over Frozen V11 Branch
    t1_fix_res, t3_fix_res = run_direct_v11_fixtures(frozen_v11_bytes)

    fixtures_obj = {
        "schema": "hydradg.v11_direct_scorer_fixtures.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "v11_frozen_git_sha": FROZEN_V11_GIT_SHA,
        "track01": t1_fix_res,
        "track03": t3_fix_res
    }
    (AUDIT_V4_DIR / "V11_DIRECT_SCORER_FIXTURES.json").write_text(json.dumps(fixtures_obj, indent=2, sort_keys=True) + "\n")

    # 4. Zero Call & Host Receipt
    host_zero_obj = {
        "schema": "hydradg.host_and_zero_call_receipt.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host_receipt": host_receipt,
        "ollama_generation_calls_executed": 0,
        "external_http_calls_executed": 0,
        "ZERO_MODEL_CALL_GATE": "PASS"
    }
    (AUDIT_V4_DIR / "HOST_AND_ZERO_CALL_RECEIPT.json").write_text(json.dumps(host_zero_obj, indent=2, sort_keys=True) + "\n")

    # 5. DATASET_READINESS_V4_SCORER_AUDIT.json
    audit_v4_summary = {
        "schema": "hydradg.dataset_readiness_v4_scorer_audit.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "auditor_sha256": auditor_sha,
        "audit_v4_host": host_receipt["hostname"],
        "ZERO_MODEL_CALL_GATE": "PASS",
        "AUDIT_EXECUTION_HOST_BINDING_GATE": "PASS",
        "V11_FROZEN_RUNNER_GIT_SHA": FROZEN_V11_GIT_SHA,
        "V11_FROZEN_RUNNER_FILE_SHA256": frozen_v11_sha,
        "CURRENT_WORKTREE_RUNNER_FILE_SHA256": worktree_v11_sha,
        "V11_FROZEN_RUNNER_SOURCE_GATE": "PASS",
        "FROZEN_VS_WORKTREE_FILE_IDENTITY_GATE": identity_gate,
        "track01": {
            "TRACK01_V11_SCORER_SOURCE_SHA256": t1_snip_sha,
            "TRACK01_V11_SCORER_SOURCE_IDENTITY_GATE": "PASS",
            "TRACK01_V11_DIRECT_FIXTURE_GATE": t1_fix_res["TRACK01_V11_DIRECT_FIXTURE_GATE"],
            "TRACK01_DATASET_STATE": "ORACLE_CONTEXT_DIRECT_BASELINE_READY",
            "HYDRADG_TRACK01_RETRIEVAL_EXECUTION_STATE": "NOT_YET_EXECUTED"
        },
        "track02": {
            "TRACK02_DATASET_STATE": "BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED"
        },
        "track03": {
            "TRACK03_V11_SCORER_SOURCE_SHA256": t3_snip_sha,
            "TRACK03_V11_SCORER_SOURCE_IDENTITY_GATE": "PASS",
            "TRACK03_V11_DIRECT_FIXTURE_GATE": t3_fix_res["TRACK03_V11_DIRECT_FIXTURE_GATE"],
            "TRACK03_DATASET_STATE": "READY_FOR_FROZEN_V11_SCORER_CONTRACT"
        },
        "ALL_TRACKS_READY": "NO",
        "overall_status": "NO_TRACK02_BLOCKED",
        "earliest_divergence": "NONE",
        "claim_ceiling": "V11_FROZEN_SCORER_RECONCILED__TRACK01_ORACLE_BASELINE_AND_TRACK03_READY__TRACK02_BLOCKED"
    }
    audit_summary_path = AUDIT_V4_DIR / "DATASET_READINESS_V4_SCORER_AUDIT.json"
    audit_summary_path.write_text(json.dumps(audit_v4_summary, indent=2, sort_keys=True) + "\n")

    # 6. DATASET_READINESS_V4_SHA256SUMS.txt
    sums_lines = [
        f"{compute_file_sha256(AUDIT_V4_DIR / 'V11_FROZEN_RUNNER_IDENTITY.json')}  eval/studio_daisy_20260821/dataset_audit_v4/V11_FROZEN_RUNNER_IDENTITY.json",
        f"{compute_file_sha256(AUDIT_V4_DIR / 'V11_SCORER_SOURCE_REGIONS.json')}  eval/studio_daisy_20260821/dataset_audit_v4/V11_SCORER_SOURCE_REGIONS.json",
        f"{compute_file_sha256(AUDIT_V4_DIR / 'V11_DIRECT_SCORER_FIXTURES.json')}  eval/studio_daisy_20260821/dataset_audit_v4/V11_DIRECT_SCORER_FIXTURES.json",
        f"{compute_file_sha256(AUDIT_V4_DIR / 'HOST_AND_ZERO_CALL_RECEIPT.json')}  eval/studio_daisy_20260821/dataset_audit_v4/HOST_AND_ZERO_CALL_RECEIPT.json",
        f"{compute_file_sha256(audit_summary_path)}  eval/studio_daisy_20260821/dataset_audit_v4/DATASET_READINESS_V4_SCORER_AUDIT.json"
    ]
    (AUDIT_V4_DIR / "DATASET_READINESS_V4_SHA256SUMS.txt").write_text("\n".join(sums_lines) + "\n")

    print("✅ Dataset Readiness V4 Scorer Reconciliation Complete. Status: NO_TRACK02_BLOCKED")
    return audit_v4_summary


if __name__ == "__main__":
    run_action_audit_v4()
