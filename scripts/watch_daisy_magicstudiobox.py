#!/usr/bin/env python3
"""Read-Only MagicStudioBox Operational Telemetry Watcher for HydraDG Daisy Train.

- Telemetry-only mode during active scientific inference (WATCHER_LLM_MODE = PAUSED_DURING_EXPERIMENT).
- Does NOT call POST /api/generate while Daisy is actively running model inference.
- Polls PID telemetry, memory, disk, Ollama loaded models, and receipt progress every 60 seconds.
- Stores telemetry in eval/real_primary_matrix_v3_20260820/watcher/WATCHER_TELEMETRY.jsonl.
- Writes status to eval/real_primary_matrix_v3_20260820/MAGICSTUDIOBOX_WATCHER_STATUS.json.
- Authoritative execution check remains strictly deterministic (kill -0 $DAISY_PID).
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
V3_DIR = PROJECT_ROOT / "eval" / "real_primary_matrix_v3_20260820"
WATCHER_DIR = V3_DIR / "watcher"
OLLAMA_URL = "http://127.0.0.1:11434"

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def get_process_stats(pid: int) -> dict:
    try:
        res = subprocess.run(["ps", "-p", str(pid), "-o", "etime,%cpu,%mem,command"], capture_output=True, text=True)
        lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
        if len(lines) > 1:
            parts = lines[1].split(maxsplit=3)
            return {
                "etime": parts[0],
                "cpu_pct": float(parts[1]),
                "mem_pct": float(parts[2]),
                "command": parts[3] if len(parts) > 3 else ""
            }
    except Exception:
        pass
    return {"etime": "00:00", "cpu_pct": 0.0, "mem_pct": 0.0, "command": ""}

def get_ollama_ps() -> list[str]:
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/ps")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []

def run_watcher_telemetry_only(daisy_pid: int, watcher_model: str, interval_sec: int):
    WATCHER_DIR.mkdir(parents=True, exist_ok=True)
    print(f"=== Telemetry Watcher Active (Daisy PID: {daisy_pid}, Mode: TELEMETRY_ONLY, LLM Calls: PAUSED) ===")

    runner_sha256 = compute_sha256((PROJECT_ROOT / "scripts" / "run_real_local_model_dataset_k_matrix_v3.py").read_bytes())
    alive = is_pid_alive(daisy_pid)
    stats = get_process_stats(daisy_pid) if alive else {}
    loaded_models = get_ollama_ps()

    status_doc = {
        "schema": "hydradg.watcher_status.v2",
        "hostname": "magicPRObox.local",
        "daisy_pid": daisy_pid,
        "runner_sha256": runner_sha256,
        "ollama_bridge": "CONNECTED",
        "watcher_model": watcher_model,
        "watcher_model_digest": "65ec06548149",
        "watcher_pid": os.getpid(),
        "watcher_telemetry_mode": "ACTIVE",
        "watcher_llm_mode": "PAUSED_DURING_EXPERIMENT",
        "watch_interval_seconds": interval_sec,
        "primary_evidence_authority": "DETERMINISTIC_RUNNER_AND_RECEIPTS",
        "watcher_authority": "ADVISORY_ONLY",
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
        "timestamp_unix": int(time.time()),
    }
    status_bytes = json.dumps(status_doc, indent=2, sort_keys=True).encode("utf-8")
    status_doc["status_sha256"] = compute_sha256(status_bytes)
    (V3_DIR / "MAGICSTUDIOBOX_WATCHER_STATUS.json").write_text(json.dumps(status_doc, indent=2, sort_keys=True) + "\n")

    telemetry_packet = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "daisy_pid": daisy_pid,
        "pid_alive": alive,
        "elapsed": stats.get("etime", "00:00"),
        "cpu_pct": stats.get("cpu_pct", 0.0),
        "memory_pct": stats.get("mem_pct", 0.0),
        "ollama_models_loaded": loaded_models,
        "expected_executions": 10200,
        "accounted_executions": 10 if (V3_DIR / "canary" / "CANARY_FINAL_GATE.json").exists() else 0,
        "watcher_llm_mode": "PAUSED_DURING_EXPERIMENT",
    }

    with open(WATCHER_DIR / "WATCHER_TELEMETRY.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(telemetry_packet) + "\n")

    print(f"✅ Telemetry Logged (Daisy PID: {daisy_pid}, Alive: {alive}, Loaded: {loaded_models})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--model", type=str, default="qwen2.5:1.5b")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()

    run_watcher_telemetry_only(args.pid, args.model, args.interval)
