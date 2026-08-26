#!/usr/bin/env python3
"""Governed Ollarma Local Watcher Daemon for SeedGraph V1A Build PID 96177.

Monitors PID 96177 on magicSTUDIObox.local deterministically every 60s.
Appends observations to /Volumes/magicBLACKbox/hydradg/seedgraph/audits/v1a_validation_watch_20260824.jsonl.
When PID 96177 exits, validates output artifacts and queries Ollama for closeout interpretation.
"""
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

EXPECTED_HOST = "magicSTUDIObox.local"
TARGET_PID = 96177
TARGET_CMD_SUBSTRING = "seedgraph"
LOG_PATH = Path("/tmp/seedgraph_audit.log")
OUTPUT_PATH = Path("/Volumes/magicBLACKbox/hydradg/seedgraph/v1a_validation")
WATCH_RECEIPT_PATH = Path("/Volumes/magicBLACKbox/hydradg/seedgraph/audits/v1a_validation_watch_20260824.jsonl")
TERMINAL_RECEIPT_PATH = Path("/Volumes/magicBLACKbox/hydradg/seedgraph/audits/v1a_validation_watch_20260824_terminal_receipt.json")
OLLAMA_ENDPOINT = "http://127.0.0.1:11434"
OLLAMA_MODEL = "qwen2.5-coder:7b"
POLL_INTERVAL_SECONDS = 60

EXPECTED_ARTIFACTS = [
    "nodes.parquet",
    "edges.parquet",
    "seed_index.parquet",
    "questions.parquet",
    "question_seeds.parquet",
    "BUILD_RECEIPT.json",
    "SHA256SUMS.txt",
    "track03_turn_projection.parquet",
]

def get_utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_file(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check_process_status(pid: int) -> tuple[bool, bool, str, float, int, str]:
    """Returns (exists, cmd_matches, status, cpu_pct, rss_bytes, cmd_line) using standard ps command."""
    try:
        res = subprocess.run(["ps", "-p", str(pid), "-o", "state,%cpu,rss,command"], capture_output=True, text=True)
        lines = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
        if len(lines) < 2:
            return False, False, "EXITED", 0.0, 0, ""
        
        parts = lines[1].split(None, 3)
        if len(parts) < 4:
            return False, False, "UNKNOWN", 0.0, 0, ""
            
        status_str = parts[0]
        try:
            cpu = float(parts[1])
        except ValueError:
            cpu = 0.0
            
        try:
            rss_kb = int(parts[2])
            rss_bytes = rss_kb * 1024
        except ValueError:
            rss_bytes = 0
            
        cmd_line = parts[3]
        cmd_matches = TARGET_CMD_SUBSTRING in cmd_line
        
        return True, cmd_matches, status_str, cpu, rss_bytes, cmd_line
    except Exception as err:
        return False, False, f"ERROR:{err}", 0.0, 0, ""

def check_filesystem_metrics() -> tuple[int, str, int, str]:
    """Returns (log_bytes, log_mtime, out_bytes, newest_out_mtime)."""
    log_bytes = LOG_PATH.stat().st_size if LOG_PATH.exists() else 0
    log_mtime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(LOG_PATH.stat().st_mtime)) if LOG_PATH.exists() else ""
    
    out_bytes = 0
    newest_mtime_ts = 0.0
    if OUTPUT_PATH.exists():
        for root, _, files in os.walk(OUTPUT_PATH):
            for file in files:
                fp = Path(root) / file
                try:
                    st = fp.stat()
                    out_bytes += st.st_size
                    if st.st_mtime > newest_mtime_ts:
                        newest_mtime_ts = st.st_mtime
                except Exception:
                    pass
    newest_out_mtime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(newest_mtime_ts)) if newest_mtime_ts > 0 else ""
    return log_bytes, log_mtime, out_bytes, newest_out_mtime

def query_ollama_interpretation(summary_prompt: str) -> str:
    try:
        url = f"{OLLAMA_ENDPOINT}/api/generate"
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": summary_prompt,
            "stream": False,
            "options": {"temperature": 0.0}
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "Ollama response missing")
    except Exception as err:
        return f"Ollama interpretation unavailable: {err}"

def run_watcher():
    current_host = socket.gethostname()
    if current_host != EXPECTED_HOST:
        print(f"Error: Host mismatch. Expected {EXPECTED_HOST}, got {current_host}")
        sys.exit(1)
        
    WATCH_RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    start_utc = get_utc_iso()
    start_time = time.time()
    print(f"[{start_utc}] Ollarma SeedGraph V1A Watcher Daemon started on {current_host} for PID {TARGET_PID}")
    
    # First sample to verify process existence
    exists, matches, status, cpu, rss, cmd = check_process_status(TARGET_PID)
    if not exists:
        print(f"[{get_utc_iso()}] PID {TARGET_PID} not found at watcher startup.")
    elif not matches:
        print(f"[{get_utc_iso()}] PID {TARGET_PID} command does not contain '{TARGET_CMD_SUBSTRING}': {cmd}")
    else:
        print(f"[{get_utc_iso()}] PID {TARGET_PID} verified active: {cmd}")
        
    iteration = 0
    while True:
        iteration += 1
        now_utc = get_utc_iso()
        elapsed = round(time.time() - start_time, 2)
        
        exists, matches, status, cpu, rss, cmd = check_process_status(TARGET_PID)
        log_bytes, log_mtime, out_bytes, newest_out_mtime = check_filesystem_metrics()
        
        obs = {
            "type": "INTERVAL_OBSERVATION",
            "iteration": iteration,
            "utc_timestamp": now_utc,
            "host": current_host,
            "target_pid": TARGET_PID,
            "pid_exists": exists,
            "command_matches_seedgraph": matches,
            "elapsed_seconds": elapsed,
            "process_status": status,
            "cpu_pct": cpu,
            "rss_bytes": rss,
            "log_byte_count": log_bytes,
            "log_mtime_utc": log_mtime,
            "output_dir_byte_count": out_bytes,
            "newest_output_mtime_utc": newest_out_mtime,
        }
        
        with WATCH_RECEIPT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obs) + "\n")
            
        print(f"[{now_utc}] Loop #{iteration}: PID {TARGET_PID} exists={exists}, status={status}, RSS={rss/(1024**2):.1f}MB, Out={out_bytes/(1024**3):.2f}GB")
        
        if not exists or not matches:
            print(f"[{now_utc}] Terminal state detected for PID {TARGET_PID}. Initiating closeout verification...")
            break
            
        time.sleep(POLL_INTERVAL_SECONDS)
        
    # Closeout verification
    terminal_utc = get_utc_iso()
    
    # Audit output artifacts
    present_artifacts = []
    missing_artifacts = []
    partial_artifacts = []
    artifact_manifest = {}
    
    for art_name in EXPECTED_ARTIFACTS:
        fp = OUTPUT_PATH / art_name
        if fp.exists():
            sz = fp.stat().st_size
            mtime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(fp.stat().st_mtime))
            if sz == 0:
                partial_artifacts.append(art_name)
            else:
                present_artifacts.append(art_name)
            artifact_manifest[art_name] = {
                "byte_count": sz,
                "mtime_utc": mtime,
                "sha256": sha256_file(fp) if sz < 100 * 1024 * 1024 else "SKIPPED_LARGE_FILE"
            }
        else:
            missing_artifacts.append(art_name)
            
    build_receipt_path = OUTPUT_PATH / "BUILD_RECEIPT.json"
    build_receipt_valid = False
    if build_receipt_path.exists():
        try:
            br_data = json.loads(build_receipt_path.read_text())
            build_receipt_valid = (br_data.get("zero_model_calls") is True)
        except Exception:
            pass
            
    log_content = LOG_PATH.read_text() if LOG_PATH.exists() else ""
    log_sha = sha256_file(LOG_PATH) if LOG_PATH.exists() else ""
    
    # Determine build state
    if build_receipt_valid and not missing_artifacts and not partial_artifacts:
        build_state = "COMPLETED"
    elif partial_artifacts or "Traceback" in log_content or "Error:" in log_content:
        build_state = "FAILED"
    else:
        build_state = "INDETERMINATE"
        
    prompt = f"""Summarize SeedGraph V1A build completion on host {current_host}.
Target PID: {TARGET_PID}
Terminal State: {build_state}
Present Artifacts: {present_artifacts}
Missing Artifacts: {missing_artifacts}
Partial Artifacts: {partial_artifacts}
Output Total Bytes: {out_bytes}
Log Size: {log_bytes} bytes
Provide a concise 2-sentence verification interpretation."""

    ollama_interp = query_ollama_interpretation(prompt)
    
    terminal_receipt = {
        "schema": "hydradg.seedgraph.v1a.watcher_terminal_receipt.v1",
        "WATCHER_STATE": "TERMINAL_OBSERVED",
        "BUILD_STATE": build_state,
        "HOST": current_host,
        "TARGET_PID": TARGET_PID,
        "TARGET_COMMAND_VERIFIED": matches,
        "START_OBSERVED_AT_UTC": start_utc,
        "TERMINAL_OBSERVED_AT_UTC": terminal_utc,
        "LOG_PATH": str(LOG_PATH),
        "LOG_SHA256": log_sha,
        "OUTPUT_PATH": str(OUTPUT_PATH),
        "EXPECTED_ARTIFACTS": EXPECTED_ARTIFACTS,
        "PRESENT_ARTIFACTS": present_artifacts,
        "MISSING_ARTIFACTS": missing_artifacts,
        "PARTIAL_ARTIFACTS": partial_artifacts,
        "ARTIFACT_SHA256_MANIFEST": artifact_manifest,
        "ERROR_EVIDENCE": "LOG_CONTAINS_ERRORS" if "Error" in log_content else "NONE",
        "COMPLETION_EVIDENCE": "BUILD_RECEIPT_VALID" if build_receipt_valid else "BUILD_RECEIPT_MISSING_OR_INVALID",
        "OLLARMA_INTERPRETATION": ollama_interp,
        "EVIDENCE_CLASS": "DETERMINISTIC_PROCESS_AND_FILESYSTEM_OBSERVATION",
        "EARLIEST_DIVERGENCE": "NONE" if build_state == "COMPLETED" else "INCOMPLETE_OR_MISSING_ARTIFACTS",
        "CLAIM_CEILING": "SEEDGRAPH_V1A_BUILD_MONITORED_TO_TERMINAL_STATE",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "NEXT_SAFE_ACTION": "STOP_FOR_BYRON_CHATGPT_REVIEW"
    }
    
    TERMINAL_RECEIPT_PATH.write_text(json.dumps(terminal_receipt, indent=2, sort_keys=True) + "\n")
    
    # Append terminal event to JSONL
    with WATCH_RECEIPT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "type": "TERMINAL_EVENT",
            "utc_timestamp": terminal_utc,
            "terminal_receipt_path": str(TERMINAL_RECEIPT_PATH),
            "build_state": build_state,
            "ollama_interpretation": ollama_interp
        }) + "\n")
        
    print(f"[{terminal_utc}] Watcher closeout complete. Build state: {build_state}. Terminal receipt: {TERMINAL_RECEIPT_PATH}")

if __name__ == "__main__":
    run_watcher()
