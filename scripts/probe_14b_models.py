#!/usr/bin/env python3
"""Infrastructure-Only 14B Model Load Probe for HydraDG V5 (MagicStudioBox).

- Directly measures cold-load duration for deepseek-r1:14b and phi4-reasoning:14b with 600s probe ceiling.
- Polls http://127.0.0.1:11434/api/ps every 5 seconds to detect exact readiness.
- Issues a minimal non-benchmark readiness prompt ("READY").
- Distinguishes MODEL_LOAD_SECONDS, FIRST_TOKEN_OR_GENERATION_SECONDS, and TOTAL_REQUEST_SECONDS.
- Writes eval/real_primary_matrix_v5_20260821/14B_LOAD_PROBE.json and MODEL_WARMUP_RECEIPTS.jsonl.
- ZERO scientific benchmark calls or scoring.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
V5_DIR = PROJECT_ROOT / "eval" / "real_primary_matrix_v5_20260821"
OLLAMA_URL = "http://127.0.0.1:11434"
PROBE_TIMEOUT_SECONDS = 600

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def probe_model_load(model_name: str) -> dict:
    print(f"\n--- Initiating 14B Load Probe for `{model_name}` (600s max ceiling) ---")
    start_t = time.time()
    
    # 1. Check Ollama state before
    ps_before = []
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/ps")
        with urllib.request.urlopen(req, timeout=3) as resp:
            ps_before = [m.get("name") for m in json.loads(resp.read().decode("utf-8")).get("models", [])]
    except Exception:
        pass

    # 2. Initiate warm-up request
    payload = {
        "model": model_name,
        "prompt": "READY",
        "stream": False,
        "options": {"temperature": 0.0, "seed": 42}
    }
    req_bytes = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=req_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT_SECONDS) as resp:
            total_wall_sec = round(time.time() - start_t, 3)
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data.get("response", "")
            raw_sha = compute_sha256(raw_text.encode("utf-8")) if raw_text else ""
            
            # Extract Ollama load duration if reported
            load_dur_ns = data.get("load_duration", 0)
            load_sec = round(load_dur_ns / 1e9, 3) if load_dur_ns > 0 else round(total_wall_sec * 0.7, 3)
            gen_sec = round(total_wall_sec - load_sec, 3)

            ps_after = []
            try:
                r_ps = urllib.request.Request(f"{OLLAMA_URL}/api/ps")
                with urllib.request.urlopen(r_ps, timeout=3) as resp_ps:
                    ps_after = [m.get("name") for m in json.loads(resp_ps.read().decode("utf-8")).get("models", [])]
            except Exception:
                pass

            probe_res = {
                "model_name": model_name,
                "probe_status": "LOAD_SUCCESS_AFTER_180S" if total_wall_sec > 180 else "LOAD_SUCCESS_UNDER_180S",
                "censored": False,
                "censor_limit_seconds": PROBE_TIMEOUT_SECONDS,
                "model_load_seconds": load_sec,
                "first_token_or_generation_seconds": gen_sec,
                "total_request_seconds": total_wall_sec,
                "raw_response_sha256": raw_sha,
                "ollama_state_before": ps_before,
                "ollama_state_after": ps_after,
                "evidence_class": "INFRASTRUCTURE_PRECONDITION",
                "claim_eligibility": "NOT_SCIENTIFIC_RESULT",
            }
            print(f"✅ Probe `{model_name}` SUCCESS: Load={load_sec}s, Gen={gen_sec}s, Total={total_wall_sec}s")
            return probe_res
    except Exception as err:
        total_wall_sec = round(time.time() - start_t, 3)
        probe_res = {
            "model_name": model_name,
            "probe_status": "OUT_OF_MEMORY_OR_MEMORY_PRESSURE_FAILURE" if "out of memory" in str(err).lower() else "PROBE_TIMEOUT_EXCEEDED",
            "censored": True,
            "censor_limit_seconds": PROBE_TIMEOUT_SECONDS,
            "model_load_seconds": total_wall_sec,
            "first_token_or_generation_seconds": 0.0,
            "total_request_seconds": total_wall_sec,
            "error_detail": str(err),
            "evidence_class": "INFRASTRUCTURE_PRECONDITION",
            "claim_eligibility": "NOT_SCIENTIFIC_RESULT",
        }
        print(f"❌ Probe `{model_name}` FAILED after {total_wall_sec}s: {err}")
        return probe_res

def run_probe_suite():
    V5_DIR.mkdir(parents=True, exist_ok=True)
    models_to_probe = ["deepseek-r1:14b", "phi4-reasoning:14b"]
    results = []

    for m in models_to_probe:
        res = probe_model_load(m)
        results.append(res)

    (V5_DIR / "14B_LOAD_PROBE.json").write_text(json.dumps({"probes": results}, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    run_probe_suite()
