#!/usr/bin/env python3
"""HydraDG Daisy Train V11 — Production Full-Matrix Watchdog.

Monitors without generating model output:
- Process existence of V11 runner PID
- Lease validity & heartbeat state
- Current model, dataset, case iteration
- Slot accounting breakdown (SUCCESS_CORRECT, SUCCESS_INCORRECT, FAILED_EMPTY_RESPONSE, ABSTENTION_CONTEXT_OVERFLOW, etc.)
- Free disk space on /Volumes/magicBLACKbox
- Ollama API health
- Atomic checkpoint timestamp & seconds since last checkpoint
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
V11_RUN_ROOT = Path("/Volumes/magicBLACKbox/hydradg/daisy/studio_daisy_20260821/v11_full")
LEASE_FILE = PROJECT_ROOT / "custody" / "V11_SINGLE_WRITER.lease"
CHECKPOINT_FILE = V11_RUN_ROOT / "CHECKPOINT.json"
LEDGER_FILE = V11_RUN_ROOT / "SLOT_LEDGER.jsonl"
OLLAMA_URL = "http://127.0.0.1:11434"


def check_v11_watchdog_status() -> dict:
    host = socket.gethostname()

    # Process & Lease Status
    pid = None
    process_alive = False
    lease_state = "INACTIVE"
    if LEASE_FILE.exists():
        try:
            l_data = json.loads(LEASE_FILE.read_text(encoding="utf-8"))
            pid = l_data.get("pid")
            try:
                os.kill(pid, 0)
                process_alive = True
                lease_state = "ACTIVE"
            except OSError:
                process_alive = False
                lease_state = "STALE_PROCESS_DEAD"
        except Exception:
            lease_state = "CORRUPT_LEASE_FILE"

    # Ollama health
    ollama_ok = False
    try:
        req = urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3)
        ollama_ok = (req.status == 200)
    except Exception:
        ollama_ok = False

    # Free disk space
    stat = os.statvfs("/Volumes/magicBLACKbox")
    free_gb = round((stat.f_bavail * stat.f_frsize) / (1024 ** 3), 2)

    # Read Checkpoint
    chk = {}
    if CHECKPOINT_FILE.exists():
        try:
            chk = json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Count Ledger Slots
    slots_accounted = 0
    terminal_counts = {
        "SUCCESS_CORRECT": 0,
        "SUCCESS_INCORRECT": 0,
        "FAILED_EMPTY_RESPONSE": 0,
        "ABSTENTION_CONTEXT_OVERFLOW": 0,
        "TIMEOUT": 0,
        "HTTP_ERROR": 0,
        "PARSER_FAILURE": 0,
        "OTHER_EXPLICIT_FAILURE": 0
    }
    if LEDGER_FILE.exists():
        for line in LEDGER_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                slots_accounted += 1
                try:
                    obj = json.loads(line)
                    st = obj.get("terminal_state", "OTHER_EXPLICIT_FAILURE")
                    terminal_counts[st] = terminal_counts.get(st, 0) + 1
                except Exception:
                    pass

    report = {
        "schema": "hydradg.v11_watchdog_report.v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_id": "studio_daisy_20260821_v11_full",
        "hostname": host,
        "process_pid": pid,
        "process_alive": process_alive,
        "lease_state": lease_state,
        "ollama_api_healthy": ollama_ok,
        "magicblackbox_free_gb": free_gb,
        "current_model": chk.get("current_model", "NONE"),
        "current_case": chk.get("current_case", "NONE"),
        "total_slots_expected": 6930,
        "slots_accounted": slots_accounted,
        "slots_remaining": 6930 - slots_accounted,
        "terminal_counts": terminal_counts,
        "last_checkpoint_utc": chk.get("timestamp_utc", "NONE"),
        "run_state": "RUNNING" if process_alive else ("COMPLETED" if slots_accounted == 6930 else "IDLE")
    }

    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    check_v11_watchdog_status()
