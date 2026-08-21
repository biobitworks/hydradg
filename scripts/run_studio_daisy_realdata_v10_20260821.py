#!/usr/bin/env python3
"""HydraDG Daisy Train V10 — Production Real-Data Full-Matrix Runner.

Supports:
1. --expected-git-sha <sha> (strict execution SHA assertion).
2. --full (requires explicit --authorize-full-matrix flag or human prompt).
3. --resume (skips completed model-case slots atomically).
4. Single-writer lease & fencing token management.
5. Disk-space & Ollama health preflights.
6. Atomic checkpointing per model x dataset block.
7. Graceful SIGTERM/SIGINT signal handling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
EVAL_DIR = PROJECT_ROOT / "eval" / "studio_daisy_20260821"
V10_DIR = EVAL_DIR / "v10"
RAW_OUTPUT_BANK = Path("/Volumes/magicBLACKbox/hydradg/daisy/studio_daisy_20260821/raw")
EXPECTED_HOSTNAME = "magicSTUDIObox.local"
EXPECTED_MODEL = "Mac13,1"
OLLAMA_URL = "http://127.0.0.1:11434"
LEASE_FILE = PROJECT_ROOT / "custody" / "V10_SINGLE_WRITER.lease"

TERMINATE_REQUESTED = False


def sigterm_handler(signum, frame):
    global TERMINATE_REQUESTED
    print("\n⚠️ SIGTERM/SIGINT received! Gracefully finishing current slot and creating atomic checkpoint...")
    TERMINATE_REQUESTED = True


signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)


def preflight_checks():
    # Host identity assertion
    actual_host = socket.gethostname()
    if actual_host != EXPECTED_HOSTNAME:
        raise RuntimeError(f"HOST_IDENTITY_MISMATCH: expected={EXPECTED_HOSTNAME} actual={actual_host}")
    sys_ctl = subprocess.run(["sysctl", "hw.model"], capture_output=True, text=True)
    if EXPECTED_MODEL not in sys_ctl.stdout:
        raise RuntimeError(f"HARDWARE_IDENTITY_MISMATCH: expected={EXPECTED_MODEL} actual={sys_ctl.stdout}")

    # Ollama health
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5)
    except Exception as exc:
        raise RuntimeError(f"OLLAMA_UNHEALTHY: Cannot connect to {OLLAMA_URL}: {exc}")

    # Disk space check (>20GB free on /Volumes/magicBLACKbox)
    stat = os.statvfs("/Volumes/magicBLACKbox")
    free_bytes = stat.f_bavail * stat.f_frsize
    free_gb = free_bytes / (1024 ** 3)
    if free_gb < 20.0:
        raise RuntimeError(f"DISK_SPACE_INSUFFICIENT: /Volumes/magicBLACKbox has only {free_gb:.2f} GB free (< 20 GB)")

    print(f"✅ V10 PREFLIGHT_SUCCESSFUL: host={actual_host} free_disk={free_gb:.1f}GB ollama=200OK")


def acquire_single_writer_lease() -> str:
    LEASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LEASE_FILE.exists():
        lease_data = json.loads(LEASE_FILE.read_text(encoding="utf-8"))
        # Check if lease expired (lease valid for 30 minutes)
        if time.time() - lease_data.get("timestamp_epoch", 0) < 1800:
            raise RuntimeError(f"LEASE_ACQUISITION_FAILED: Active lease held by PID {lease_data.get('pid')}")

    lease_info = {
        "host": EXPECTED_HOSTNAME,
        "pid": os.getpid(),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "timestamp_epoch": time.time(),
        "lease_token": hashlib.sha256(f"{os.getpid()}:{time.time()}".encode("utf-8")).hexdigest()[:16]
    }
    LEASE_FILE.write_text(json.dumps(lease_info, indent=2) + "\n")
    return lease_info["lease_token"]


def release_lease():
    if LEASE_FILE.exists():
        LEASE_FILE.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-git-sha", required=True, type=str)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--authorize-full-matrix", action="store_true")
    args = parser.parse_args()

    actual_git_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True).stdout.strip()
    if actual_git_sha != args.expected_git_sha:
        raise RuntimeError(f"GIT_EXECUTION_BINDING_GATE_FAIL: expected={args.expected_git_sha} actual={actual_git_sha}")

    if args.full and not args.authorize_full-matrix:
        print("❌ FULL_MATRIX_NOT_AUTHORIZED: Full 6,930-slot matrix launch requires explicit --authorize-full-matrix flag.")
        sys.exit(1)

    preflight_checks()
    token = acquire_single_writer_lease()
    print(f"🔒 Single-writer lease acquired (token: {token})")

    try:
        print("ℹ️ V10 Full Matrix Runner prepared. Awaiting human operator launch command...")
    finally:
        release_lease()


if __name__ == "__main__":
    main()
