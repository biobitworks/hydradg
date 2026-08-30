#!/usr/bin/env python3
"""HydraDG Daisy Train V9 — Governed Real-Data Matrix & Canary Runner.

Enforces:
1. Fail-closed host identity assertion (magicSTUDIObox.local / Mac13,1).
2. Dynamic Git SHA assertion (--expected-git-sha <sha>).
3. Dynamic fresh output namespace (canary_v9_frozen_<first8sha>).
4. Full raw transport persistence under /Volumes/magicBLACKbox/hydradg/daisy/studio_daisy_20260821/raw/.
5. Empty response mechanism classification (TRUE_ZERO_GENERATION, THINKING_WITHOUT_FINAL_RESPONSE, CONTEXT_OR_GENERATION_LIMIT, OTHER).
6. hydradg.agent_model_handoff.v1 receipts validated with check_agent_model_handoff_receipt.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
EVAL_DIR = PROJECT_ROOT / "eval" / "studio_daisy_20260821"
V9_DIR = EVAL_DIR / "v9"
RAW_OUTPUT_BANK = Path("/Volumes/magicBLACKbox/hydradg/daisy/studio_daisy_20260821/raw")
EXPECTED_HOSTNAME = "magicSTUDIObox.local"
EXPECTED_MODEL = "Mac13,1"
OLLAMA_URL = "http://127.0.0.1:11434"
DATASETS_BASE = Path("/Users/byron/.local/share/hydradg-datasets")

EMPTY_TEXT_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_file_sha256(p: Path) -> str:
    return compute_sha256(p.read_bytes())


def canonical_json(val: object) -> str:
    return json.dumps(val, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def check_host_identity():
    actual_host = socket.gethostname()
    if actual_host != EXPECTED_HOSTNAME:
        raise RuntimeError(f"HOST_IDENTITY_MISMATCH: expected={EXPECTED_HOSTNAME} actual={actual_host}")
    sys_ctl = subprocess.run(["sysctl", "hw.model"], capture_output=True, text=True)
    if EXPECTED_MODEL not in sys_ctl.stdout:
        raise RuntimeError(f"HARDWARE_IDENTITY_MISMATCH: expected={EXPECTED_MODEL} actual={sys_ctl.stdout}")
    print(f"✅ EXECUTION_HOST_VERIFIED: host={actual_host} hardware={EXPECTED_MODEL}")


def get_actual_git_sha() -> str:
    res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def audit_source_files() -> dict:
    contract = json.loads((V9_DIR / "DATASET_CONTRACT.json").read_text(encoding="utf-8"))
    ds_spec = contract["datasets"]

    audit_results = {}
    all_match = True

    for trk, spec in ds_spec.items():
        sp = Path(spec["expected_source_path"])
        exp_sha = spec["expected_sha256"]
        if not sp.exists():
            audit_results[trk] = {"path": str(sp), "exists": False, "match": False}
            all_match = False
            continue
        obs_sha = compute_file_sha256(sp)
        sz = sp.stat().st_size
        matches = (obs_sha == exp_sha)
        if not matches:
            all_match = False
        audit_results[trk] = {
            "path": str(sp),
            "bytes": sz,
            "expected_sha256": exp_sha,
            "observed_sha256": obs_sha,
            "match": matches,
        }

    return {"all_match": all_match, "results": audit_results}


def load_real_datasets() -> dict:
    datasets = {}

    # Track 01: EnterpriseRAG-Bench
    erag_q_path = DATASETS_BASE / "track01" / "enterprise-rag-bench" / "data" / "questions" / "test.parquet"
    erag_doc_path = DATASETS_BASE / "track01" / "enterprise-rag-bench" / "data" / "documents" / "test.parquet"
    if erag_q_path.exists():
        import pandas as pd
        df_q = pd.read_parquet(erag_q_path)
        doc_map = {}
        if erag_doc_path.exists():
            df_doc = pd.read_parquet(erag_doc_path, columns=["doc_id", "content"])
            doc_map = dict(zip(df_doc["doc_id"].astype(str), df_doc["content"].astype(str)))

        erag_source_sha = compute_file_sha256(erag_q_path)
        erag_cases = []
        for idx, row in df_q.iterrows():
            q_id = str(row["question_id"])
            q_text = str(row["question"])
            gold_ans = str(row["gold_answer"])
            facts = list(row["answer_facts"]) if isinstance(row["answer_facts"], (list, tuple)) else [str(row["answer_facts"])]
            
            exp_docs = list(row.get("expected_doc_ids", [])) if row.get("expected_doc_ids") is not None else []
            doc_ctx = "\n\n".join([f"Document {did}:\n{doc_map.get(str(did), 'Document content omitted.')}" for did in exp_docs]) if len(exp_docs) > 0 else "No specific documents linked."

            prompt_content = (
                f"Dataset: EnterpriseRAG-Bench\n"
                f"Question ID: {q_id}\n"
                f"Question: {q_text}\n\n"
                f"Context Documents:\n{doc_ctx}\n\n"
                f"Extract canonical entities, concepts, and evidence paths to answer the question:"
            )
            ref_payload = {"gold_answer": gold_ans, "answer_facts": facts}
            
            erag_cases.append({
                "case_id": f"EnterpriseRAG-Bench_{q_id}",
                "track": "track01",
                "dataset": "EnterpriseRAG-Bench",
                "source_path": str(erag_q_path),
                "source_sha256": erag_source_sha,
                "question_text": q_text,
                "model_prompt": prompt_content,
                "case_payload_sha256": compute_sha256(prompt_content.encode("utf-8")),
                "eval_reference": ref_payload,
                "eval_reference_sha256": compute_sha256(canonical_json(ref_payload).encode("utf-8")),
            })
        datasets["EnterpriseRAG-Bench"] = erag_cases

    # Track 03: LongMemEval-S full500
    lme_path = DATASETS_BASE / "track03" / "longmemeval-cleaned" / "longmemeval_s_cleaned.json"
    if lme_path.exists():
        lme_raw = json.loads(lme_path.read_text(encoding="utf-8"))
        lme_cases = []
        lme_source_sha = compute_file_sha256(lme_path)
        for item in lme_raw:
            q_id = str(item.get("question_id"))
            q_text = str(item.get("question"))
            ans_text = str(item.get("answer"))
            sessions = item.get("haystack_sessions", [])
            
            sess_lines = []
            for i, s in enumerate(sessions):
                if isinstance(s, list):
                    turn_strs = [f"  {t.get('role', 'user')}: {t.get('content', '')}" for t in s if isinstance(t, dict)]
                    sess_lines.append(f"Session {i+1}:\n" + "\n".join(turn_strs))
                elif isinstance(s, dict):
                    sess_lines.append(f"Session {i+1}:\n  {s.get('role', 'user')}: {s.get('content', '')}")
                else:
                    sess_lines.append(f"Session {i+1}: {str(s)}")
            sess_str = "\n".join(sess_lines)

            prompt_content = (
                f"Dataset: LongMemEval-S\n"
                f"Question ID: {q_id}\n"
                f"Conversation Sessions:\n{sess_str}\n\n"
                f"Question: {q_text}\n\nAnswer:"
            )
            ref_payload = {"gold_answer": ans_text}
            
            lme_cases.append({
                "case_id": f"LongMemEval-S_{q_id}",
                "track": "track03",
                "dataset": "LongMemEval-S-full500",
                "source_path": str(lme_path),
                "source_sha256": lme_source_sha,
                "question_text": q_text,
                "model_prompt": prompt_content,
                "case_payload_sha256": compute_sha256(prompt_content.encode("utf-8")),
                "eval_reference": ref_payload,
                "eval_reference_sha256": compute_sha256(canonical_json(ref_payload).encode("utf-8")),
            })
        datasets["LongMemEval-S-full500"] = lme_cases

    return datasets


def evaluate_real_case_v9(model_info: dict, case_obj: dict, actual_git_sha: str) -> dict:
    model_name = model_info["requested_name"]
    gen_timeout = model_info["gen_timeout_seconds"]
    start_time = time.time()

    user_prompt = case_obj["model_prompt"]
    prompt_bytes = user_prompt.encode("utf-8")
    prompt_sha = compute_sha256(prompt_bytes)

    # Label leakage assertion (ensure gold_answer is not in question_text or prompt instructions)
    ref_gold = case_obj["eval_reference"].get("gold_answer", "")
    q_text = case_obj.get("question_text", "")
    if ref_gold and len(ref_gold) > 3 and ref_gold.lower() in q_text.lower():
        raise RuntimeError(f"LABEL_LEAKAGE_DETECTED: gold_answer contained in question for case {case_obj['case_id']}")

    payload = {
        "model": model_name,
        "prompt": user_prompt,
        "stream": False,
        "options": {"temperature": 0.0, "seed": 42, "num_predict": 256},
    }
    req_bytes = json.dumps(payload).encode("utf-8")
    req_sha = compute_sha256(req_bytes)
    headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=req_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=gen_timeout) as resp:
            wall_sec = round(time.time() - start_time, 3)
            resp_bytes = resp.read()
            transport_sha = compute_sha256(resp_bytes)
            
            # Persist raw transport response
            RAW_OUTPUT_BANK.mkdir(parents=True, exist_ok=True)
            raw_file = RAW_OUTPUT_BANK / f"transport_v9_{transport_sha[:16]}.json"
            raw_file.write_bytes(resp_bytes)

            data = json.loads(resp_bytes.decode("utf-8"))
            raw_text = data.get("response", "")
            thinking_text = data.get("thinking", "")
            done = data.get("done", True)
            done_reason = data.get("done_reason", "stop")
            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)

            thinking_bytes_cnt = len(thinking_text.encode("utf-8")) if thinking_text else 0
            thinking_sha = compute_sha256(thinking_text.encode("utf-8")) if thinking_text else "NOT_PRESENT"

            if not raw_text or len(raw_text.strip()) == 0:
                response_text_bytes = 0
                response_text_sha = EMPTY_TEXT_SHA256
                execution_status = "FAILED_EMPTY_RESPONSE"
                successful = False
                is_correct = False
                
                # Classify empty response mechanism
                if thinking_bytes_cnt > 0:
                    empty_mechanism = "THINKING_WITHOUT_FINAL_RESPONSE"
                elif done_reason in ("length", "context_length"):
                    empty_mechanism = "CONTEXT_OR_GENERATION_LIMIT"
                else:
                    empty_mechanism = "TRUE_ZERO_GENERATION"
            else:
                raw_bytes = raw_text.encode("utf-8")
                response_text_bytes = len(raw_bytes)
                response_text_sha = compute_sha256(raw_bytes)
                execution_status = "SUCCESS"
                successful = True
                empty_mechanism = "NOT_APPLICABLE"
                
                ref_ans = ref_gold.lower()
                if case_obj["track"] == "track01":
                    is_correct = any(word.lower() in raw_text.lower() for word in ref_ans.split() if len(word) > 4) if ref_ans else False
                else:
                    is_correct = (ref_ans in raw_text.lower()) if ref_ans else False

    except Exception as exc:
        wall_sec = round(time.time() - start_time, 3)
        transport_sha = "NOT_AVAILABLE"
        response_text_bytes = 0
        response_text_sha = EMPTY_TEXT_SHA256
        execution_status = f"HTTP_OR_TRANSPORT_ERROR: {exc}"
        successful = False
        is_correct = False
        empty_mechanism = "OTHER"
        raw_text = ""
        done = False
        done_reason = "error"
        prompt_eval_count = 0
        eval_count = 0
        thinking_bytes_cnt = 0
        thinking_sha = "NOT_PRESENT"

    # Emit Handoff Receipt
    turns_dir = PROJECT_ROOT / "custody" / "turns"
    turns_dir.mkdir(parents=True, exist_ok=True)
    handoff_id = f"HANDOFF_V9_{model_name.replace(':', '_')}_{case_obj['case_id']}"
    handoff_receipt = {
        "schema": "hydradg.agent_model_handoff.v1",
        "handoff_id": handoff_id,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "actor_class": "OLLAMA_MODEL",
        "actor_id": model_name,
        "execution_host": EXPECTED_HOSTNAME,
        "repo": "biobitworks/hydradg",
        "branch": "hack-hydra/studio-ollarma-daisy-20260821",
        "git_commit": actual_git_sha,
        "parent_handoff_sha256": "7102945d9375ca32941bef197c47bac135a57757f7b0d07c714d3952d74db439",
        "input_dependencies": [
            {"id": case_obj["case_id"], "sha256": case_obj["case_payload_sha256"], "evidence_class": "PRIMARY_DATASET_CASE"}
        ],
        "prompt_sha256": prompt_sha,
        "request_sha256": req_sha,
        "output_sha256": response_text_sha,
        "transport_response_sha256": transport_sha,
        "response_text_bytes": response_text_bytes,
        "execution_status": execution_status,
        "empty_response_mechanism": empty_mechanism,
        "successful": successful,
        "model": {
            "bridge": "OLLARMA",
            "requested_name": model_name,
            "approved_name": model_name,
            "runtime_name": model_name,
            "runtime_digest": model_info["runtime_digest"],
        },
        "evidence_class": "PROBABILISTIC_MODEL_GENERATION",
        "transformation_class": "INFERENCE",
        "claim_ceiling": "STUDIO_OLLARMA_REAL_DATASET_CANARY_PASS_FULL_MATRIX_NOT_FINAL",
        "signature": {
            "state": "NOT_SIGNED",
            "algorithm": None,
            "public_key_id": None,
            "signed_scope": None,
            "signature_path": None,
            "verification_receipt_sha256": "NOT_APPLICABLE",
        },
        "merkle_mmr": {
            "state": "PENDING_OPERATION_RECEIPT_CONFIRMATION",
            "root": "e07de052fb6a47a23cf1123c1910c73c2462dc2db72722362430b2ff6104d2e9",
            "receipt_sha256": "NOT_PROJECT_COMMITTED",
        },
    }

    h_bytes = json.dumps(handoff_receipt, sort_keys=True).encode("utf-8")
    h_sha = compute_sha256(h_bytes)
    handoff_receipt["receipt_sha256"] = h_sha

    h_file = turns_dir / f"{handoff_id}.json"
    h_file.write_text(json.dumps(handoff_receipt, indent=2, sort_keys=True) + "\n")

    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "check_agent_model_handoff_receipt.py"), str(h_file)],
        check=True, capture_output=True
    )

    return {
        "model_name": model_name,
        "case_id": case_obj["case_id"],
        "dataset": case_obj["dataset"],
        "prompt_sha256": prompt_sha,
        "request_sha256": req_sha,
        "response_text_sha256": response_text_sha,
        "transport_sha256": transport_sha,
        "response_text_bytes": response_text_bytes,
        "thinking_bytes": thinking_bytes_cnt,
        "thinking_sha256": thinking_sha,
        "done": done,
        "done_reason": done_reason,
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "execution_status": execution_status,
        "empty_response_mechanism": empty_mechanism,
        "successful": successful,
        "is_correct": is_correct,
        "wall_sec": wall_sec,
        "handoff_receipt_sha256": h_sha,
    }


def run_v9_canary(expected_git_sha: str):
    check_host_identity()
    actual_git_sha = get_actual_git_sha()
    if actual_git_sha != expected_git_sha:
        raise RuntimeError(f"GIT_EXECUTION_BINDING_GATE_FAIL: expected={expected_git_sha} actual={actual_git_sha}")

    canary_dir = EVAL_DIR / f"canary_v9_frozen_{actual_git_sha[:8]}"
    if canary_dir.exists() and len(list(canary_dir.glob("*.json"))) > 0:
        raise RuntimeError(f"CLEAN_OUTPUT_NAMESPACE_GATE_FAIL: Directory {canary_dir} is not fresh")
    canary_dir.mkdir(parents=True, exist_ok=True)

    src_audit = audit_source_files()
    if not src_audit["all_match"]:
        print(f"⚠️ Source audit mismatches observed: {src_audit['results']}")

    datasets = load_real_datasets()
    t1_cases = datasets.get("EnterpriseRAG-Bench", [])
    t3_cases = datasets.get("LongMemEval-S-full500", [])

    models_roster = json.loads((V9_DIR / "MODEL_ROSTER.json").read_text(encoding="utf-8"))["admitted_models"]
    canary_cases = [t1_cases[0], t3_cases[0]]

    print(f"=== RUNNING CANONICAL FROZEN V9 CANARY (SHA: {actual_git_sha[:8]}) ===")
    print(f"Canary Cases: {len(canary_cases)} | Admitted Models: {len(models_roster)}")

    canary_results = []
    success_count = 0
    empty_count = 0

    for c in canary_cases:
        for m in models_roster:
            print(f"  --> Model: {m['requested_name']} | Case: {c['case_id']}")
            res = evaluate_real_case_v9(m, c, actual_git_sha)
            canary_results.append(res)
            if res["successful"]:
                success_count += 1
            else:
                empty_count += 1
            print(f"      Status: {res['execution_status']} | Mechanism: {res['empty_response_mechanism']} | Wall: {res['wall_sec']}s")

    canary_summary = {
        "schema": "hydradg.v9_canary_summary.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozen_git_sha": actual_git_sha,
        "canary_executions_expected": len(canary_cases) * len(models_roster),
        "canary_executions_accounted": len(canary_results),
        "successful_invocations": success_count,
        "empty_response_failures": empty_count,
        "canary_results": canary_results,
        "source_audit": src_audit,
    }

    sum_file = canary_dir / "V9_CANARY_SUMMARY.json"
    sum_file.write_text(json.dumps(canary_summary, indent=2, sort_keys=True) + "\n")
    print(f"\n✅ V9 Canary execution complete. Output written to {sum_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-git-sha", required=True, type=str)
    parser.add_argument("--canary-only", action="store_true", default=True)
    parser.add_argument("--full", action="store_true", default=False)
    args = parser.parse_args()

    if args.full:
        raise RuntimeError("FULL_MATRIX_NOT_AUTHORIZED: Must stop for operator and review before full matrix launch.")

    run_v9_canary(args.expected_git_sha)
