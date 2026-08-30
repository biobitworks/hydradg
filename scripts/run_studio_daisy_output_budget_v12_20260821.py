#!/usr/bin/env python3
"""HydraDG Daisy Train V12 — Output-Budget Calibration Runner.

Runs mechanical budget ladder (512, 1024, 2048, 4096) across 9 admitted models and 3 fixed diagnostic prompts on magicSTUDIObox.local.
Selects minimum non-binding budget (response_text_bytes > 0 AND done_reason != 'length') per model without using accuracy scoring.
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
V12_DIR = EVAL_DIR / "v12_calibration"
RAW_OUTPUT_BANK = Path("/Volumes/magicBLACKbox/hydradg/daisy/studio_daisy_20260821/v12_raw")
EXPECTED_HOSTNAME = "magicSTUDIObox.local"
EXPECTED_MODEL = "Mac13,1"
OLLAMA_URL = "http://127.0.0.1:11434"
DATASETS_BASE = Path("/Users/byron/.local/share/hydradg-datasets")


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_file_sha256(p: Path) -> str:
    return compute_sha256(p.read_bytes())


def check_host_identity():
    actual_host = socket.gethostname()
    if actual_host != EXPECTED_HOSTNAME:
        raise RuntimeError(f"HOST_IDENTITY_MISMATCH: expected={EXPECTED_HOSTNAME} actual={actual_host}")
    sys_ctl = subprocess.run(["sysctl", "hw.model"], capture_output=True, text=True)
    if EXPECTED_MODEL not in sys_ctl.stdout:
        raise RuntimeError(f"HARDWARE_IDENTITY_MISMATCH: expected={EXPECTED_MODEL} actual={sys_ctl.stdout}")
    print(f"✅ EXECUTION_HOST_VERIFIED: host={actual_host} hardware={EXPECTED_MODEL}")


def load_calibration_prompts() -> list[dict]:
    prompts = []

    # 1. EnterpriseRAG-Bench qst_0001
    erag_q_path = DATASETS_BASE / "track01" / "enterprise-rag-bench" / "data" / "questions" / "test.parquet"
    erag_doc_path = DATASETS_BASE / "track01" / "enterprise-rag-bench" / "data" / "documents" / "test.parquet"
    if erag_q_path.exists():
        import pandas as pd
        df_q = pd.read_parquet(erag_q_path)
        df_doc = pd.read_parquet(erag_doc_path, columns=["doc_id", "content"])
        doc_map = dict(zip(df_doc["doc_id"].astype(str), df_doc["content"].astype(str)))

        for q_target in ["qst_0001", "qst_0003"]:
            row = df_q[df_q["question_id"].astype(str) == q_target].iloc[0]
            q_id = str(row["question_id"])
            q_text = str(row["question"])
            exp_docs = list(row.get("expected_doc_ids", []))
            doc_ctx = "\n\n".join([f"Document {did}:\n{doc_map.get(str(did), 'Document content omitted.')}" for did in exp_docs])

            prompt_content = (
                f"Dataset: EnterpriseRAG-Bench\n"
                f"Question ID: {q_id}\n"
                f"Question: {q_text}\n\n"
                f"Context Documents:\n{doc_ctx}\n\n"
                f"Extract canonical entities, concepts, and evidence paths to answer the question:"
            )
            prompts.append({
                "case_id": f"EnterpriseRAG-Bench_{q_id}",
                "dataset": "EnterpriseRAG-Bench",
                "prompt_text": prompt_content,
                "prompt_sha256": compute_sha256(prompt_content.encode("utf-8"))
            })

    # 2. LongMemEval-S e47becba
    lme_path = DATASETS_BASE / "track03" / "longmemeval-cleaned" / "longmemeval_s_cleaned.json"
    if lme_path.exists():
        lme_raw = json.loads(lme_path.read_text(encoding="utf-8"))
        item = [x for x in lme_raw if str(x.get("question_id")) == "e47becba"][0]
        q_id = str(item.get("question_id"))
        q_text = str(item.get("question"))
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
        prompts.append({
            "case_id": f"LongMemEval-S_{q_id}",
            "dataset": "LongMemEval-S-full500",
            "prompt_text": prompt_content,
            "prompt_sha256": compute_sha256(prompt_content.encode("utf-8"))
        })

    return prompts


def evaluate_calibration_slot(model_info: dict, prompt_obj: dict, num_predict: int, actual_git_sha: str) -> dict:
    model_name = model_info["requested_name"]
    gen_timeout = max(300, num_predict // 4)
    start_time = time.time()

    user_prompt = prompt_obj["prompt_text"]
    prompt_sha = prompt_obj["prompt_sha256"]

    payload = {
        "model": model_name,
        "prompt": user_prompt,
        "stream": False,
        "options": {"temperature": 0.0, "seed": 42, "num_predict": num_predict},
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
            
            RAW_OUTPUT_BANK.mkdir(parents=True, exist_ok=True)
            raw_file = RAW_OUTPUT_BANK / f"v12_{transport_sha[:16]}.json"
            raw_file.write_bytes(resp_bytes)

            data = json.loads(resp_bytes.decode("utf-8"))
            raw_text = data.get("response", "")
            thinking_text = data.get("thinking", "")
            done = data.get("done", True)
            done_reason = data.get("done_reason", "stop")
            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)

            resp_bytes_cnt = len(raw_text.encode("utf-8")) if raw_text else 0
            resp_sha = compute_sha256(raw_text.encode("utf-8")) if raw_text else compute_sha256(b"")
            think_bytes_cnt = len(thinking_text.encode("utf-8")) if thinking_text else 0

            # Pass condition: response_text_bytes > 0 AND done_reason != "length"
            budget_pass = (resp_bytes_cnt > 0 and done_reason != "length")

    except Exception as exc:
        wall_sec = round(time.time() - start_time, 3)
        transport_sha = "NOT_AVAILABLE"
        resp_bytes_cnt = 0
        resp_sha = compute_sha256(b"")
        think_bytes_cnt = 0
        done = False
        done_reason = f"error: {exc}"
        prompt_eval_count = 0
        eval_count = 0
        budget_pass = False

    return {
        "model_name": model_name,
        "case_id": prompt_obj["case_id"],
        "dataset": prompt_obj["dataset"],
        "num_predict": num_predict,
        "prompt_sha256": prompt_sha,
        "request_sha256": req_sha,
        "transport_sha256": transport_sha,
        "response_text_bytes": resp_bytes_cnt,
        "response_text_sha256": resp_sha,
        "thinking_bytes": think_bytes_cnt,
        "done": done,
        "done_reason": done_reason,
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "budget_pass": budget_pass,
        "wall_sec": wall_sec,
    }


def run_v12_calibration(expected_git_sha: str):
    check_host_identity()
    actual_git_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True).stdout.strip()
    if actual_git_sha != expected_git_sha:
        raise RuntimeError(f"GIT_EXECUTION_BINDING_GATE_FAIL: expected={expected_git_sha} actual={actual_git_sha}")

    V12_DIR.mkdir(parents=True, exist_ok=True)
    models_roster = json.loads((V9_DIR / "MODEL_ROSTER.json").read_text(encoding="utf-8"))["admitted_models"]
    prompts = load_calibration_prompts()
    ladder = [512, 1024, 2048, 4096]

    print(f"=== HYDRADG DAISY V12 OUTPUT-BUDGET CALIBRATION (SHA: {actual_git_sha[:8]}) ===")
    print(f"Admitted Models: {len(models_roster)} | Fixed Prompts: {len(prompts)} | Ladder: {ladder}")

    all_results = []
    model_min_budgets = {}

    for m in models_roster:
        m_name = m["requested_name"]
        print(f"\n---> Calibrating Model: {m_name}")
        model_min_budgets[m_name] = None
        
        for p in prompts:
            print(f"  --> Prompt: {p['case_id']}")
            prompt_min = None
            
            for b in ladder:
                res = evaluate_calibration_slot(m, p, b, actual_git_sha)
                all_results.append(res)
                print(f"      num_predict={b} | text_bytes={res['response_text_bytes']} | think_bytes={res['thinking_bytes']} | done_reason={res['done_reason']} | PASS={res['budget_pass']}")
                
                if res["budget_pass"] and prompt_min is None:
                    prompt_min = b
                    break
            
            if prompt_min is None:
                print(f"❌ BUDGET_EXHAUSTED: Model {m_name} failed all ladder budgets up to 4096 on prompt {p['case_id']}")
                model_min_budgets[m_name] = "EXHAUSTED_AT_4096"
            elif model_min_budgets[m_name] is not None and isinstance(model_min_budgets[m_name], int):
                model_min_budgets[m_name] = max(model_min_budgets[m_name], prompt_min)
            else:
                model_min_budgets[m_name] = prompt_min

    # Calculate V13_GLOBAL_NUM_PREDICT
    numeric_budgets = [v for v in model_min_budgets.values() if isinstance(v, int)]
    global_budget = max(numeric_budgets) if len(numeric_budgets) == len(models_roster) else "BLOCKED_AT_4096"

    summary = {
        "schema": "hydradg.v12_calibration_summary.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "v12_frozen_git_sha": actual_git_sha,
        "models_admitted": len(models_roster),
        "calibration_prompts_count": len(prompts),
        "budget_ladder": ladder,
        "model_minimum_non_binding_budgets": model_min_budgets,
        "v13_global_num_predict": global_budget,
        "v12_output_budget_gate": "PASS" if isinstance(global_budget, int) else "BLOCKED",
        "calibration_results": all_results
    }

    sum_file = V12_DIR / "V12_CALIBRATION_SUMMARY.json"
    sum_file.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n✅ V12 Calibration Complete. Global Budget Selected: {global_budget}. Summary written to {sum_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-git-sha", required=True, type=str)
    args = parser.parse_args()

    run_v12_calibration(args.expected_git_sha)
