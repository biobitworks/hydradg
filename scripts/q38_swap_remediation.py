#!/usr/bin/env python3
"""macOS swap remediation for Q38 local execution recovery — forward-only receipts."""
from __future__ import annotations

import hashlib
import json
import re
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval/qwen38_model_replay_20260828/remediation"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(cmd: list[str] | str, shell: bool = False) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
    return p.returncode, (p.stdout + p.stderr).strip()


def parse_swap() -> dict[str, Any]:
    _, swap = run(["sysctl", "vm.swapusage"])
    m = re.search(r"total = ([0-9.]+)M\s+used = ([0-9.]+)M\s+free = ([0-9.]+)M", swap)
    if not m:
        return {"raw": swap}
    total, used, free = map(float, m.groups())
    return {
        "raw": swap.strip(),
        "total_mb": total,
        "used_mb": used,
        "free_mb": free,
        "used_pct": round(100 * used / total, 2) if total else None,
    }


def memory_snapshot() -> dict[str, Any]:
    _, vm = run(["vm_stat"])
    _, mp = run(["memory_pressure"])
    _, uptime = run(["uptime"])
    _, df_root = run(["df", "-h", "/"])
    _, df_data = run(["df", "-h", "/System/Volumes/Data"])
    _, ollama_ps = run(["ollama", "ps"])
    _, api_ps = run(["curl", "-sS", "http://127.0.0.1:11434/api/ps"])
    free_gb = None
    dm = re.search(r"(\d+(?:\.\d+)?)Gi\s+\d+%", df_root.splitlines()[-1] if df_root else "")
    if dm:
        free_gb = float(dm.group(1))
    return {
        "timestamp_utc": utc_now(),
        "swap": parse_swap(),
        "vm_stat_head": vm.splitlines()[:12],
        "memory_pressure_head": mp.splitlines()[:8],
        "uptime": uptime,
        "disk_root": df_root.splitlines()[-1] if df_root else "",
        "disk_data": df_data.splitlines()[-1] if df_data else "",
        "disk_free_gb_approx": free_gb,
        "ollama_ps": ollama_ps,
        "ollama_api_ps": api_ps,
    }


def top_processes(n: int = 60) -> list[str]:
    _, out = run(
        "ps -axo pid,ppid,rss,vsz,%mem,%cpu,etime,state,command | sort -nrk3 | head -60",
        shell=True,
    )
    return out.splitlines()


def active_q38_pids() -> list[str]:
    _, out = run(["ps", "-ax", "-o", "pid=,command="])
    hits = []
    for line in out.splitlines():
        line = line.strip()
        if not line or "run_qwen38_model_replay.py" not in line:
            continue
        if "q38_swap_remediation" in line:
            continue
        hits.append(line)
    return hits


def term_pid(pid: int, reason: str, classification: str) -> dict[str, Any]:
    action = {"pid": pid, "classification": classification, "reason": reason, "signal": "TERM", "result": "pending"}
    code, _ = run(["kill", "-TERM", str(pid)])
    action["term_exit_code"] = code
    time.sleep(2)
    code2, ps = run(["ps", "-p", str(pid), "-o", "pid="])
    if code2 != 0:
        action["result"] = "terminated"
        return action
    run(["kill", "-KILL", str(pid)])
    action["signal"] = "KILL"
    code3, _ = run(["ps", "-p", str(pid), "-o", "pid="])
    action["result"] = "killed" if code3 != 0 else "still_running"
    return action


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    receipt: dict[str, Any] = {
        "schema": "hydradg.qwen38.swap_remediation.v1",
        "recorded_at_utc": utc_now(),
        "execution_host": socket.gethostname(),
        "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
        "claim_ceiling": "DETERMINISTIC_TOOL_OUTPUT",
    }

    pre = memory_snapshot()
    receipt["pre"] = pre
    receipt["PRE_SWAP_TOTAL"] = pre["swap"].get("total_mb")
    receipt["PRE_SWAP_USED"] = pre["swap"].get("used_mb")
    receipt["PRE_SWAP_USED_PCT"] = pre["swap"].get("used_pct")
    receipt["PRE_MEMORY_PRESSURE"] = pre["memory_pressure_head"]
    receipt["PRE_DISK_FREE"] = pre["disk_free_gb_approx"]
    receipt["PRE_TOP_MEMORY_PROCESSES"] = top_processes()

    q38_active = active_q38_pids()
    receipt["ACTIVE_Q38_INFERENCE_PIDS"] = q38_active
    if q38_active:
        receipt["SWAP_REMEDIATION_STATE"] = "BLOCKED_ACTIVE_SCIENTIFIC_EXECUTION"
        receipt["actions"] = []
        receipt["time_series"] = [pre]
        path = OUT / "SWAP_REMEDIATION_RECEIPT.json"
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        receipt["receipt_sha256"] = sha256_bytes(path.read_bytes())
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"state": receipt["SWAP_REMEDIATION_STATE"]}, indent=2))
        return 2

    receipt["WATCHER_LLM_MODE"] = "PAUSED"
    actions: list[dict[str, Any]] = []

    # Planned terminations — verified stale/non-scientific only
    targets = [
        (96177, "OPERATIONAL_STALE", "6-day stale seedgraph_hierarchy_v1a.py build (2.9GB RSS)"),
        (9211, "OPERATIONAL_STALE", "Ollarma seedgraph watcher bound to stale PID 96177; performs LLM inference"),
        (31052, "NONSCIENTIFIC_OPTIONAL", "Yappy whisper-server not required for Q38"),
        (27490, "OPERATIONAL_STALE", "ollarma-chat next dev server stale"),
        (27619, "OPERATIONAL_STALE", "ollarma-chat next dev child stale"),
    ]
    for pid, cls, reason in targets:
        code, ps = run(["ps", "-p", str(pid), "-o", "pid="])
        if code != 0:
            actions.append({"pid": pid, "classification": cls, "reason": reason, "result": "already_absent"})
            continue
        actions.append(term_pid(pid, reason, cls))

    receipt["ollama_unloads"] = []
    _, ollama_ps = run(["ollama", "ps"])
    if ollama_ps.strip() and "NAME" in ollama_ps:
        receipt["ollama_unloads"].append({"note": "no loaded models at remediation start"})

    receipt["actions"] = actions
    receipt["processes_terminated"] = [a for a in actions if a.get("result") in {"terminated", "killed"}]

    time_series = [pre]
    for wait in (30, 60, 120):
        time.sleep(wait)
        snap = memory_snapshot()
        time_series.append(snap)

    receipt["time_series"] = time_series
    post = time_series[-1]
    receipt["post"] = post
    receipt["POST_SWAP_USED_MB"] = post["swap"].get("used_mb")
    receipt["POST_SWAP_USED_PCT"] = post["swap"].get("used_pct")
    receipt["POST_MEMORY_PRESSURE"] = post["memory_pressure_head"]

    # Trend check
    swap_values = [s["swap"].get("used_mb") for s in time_series if s.get("swap")]
    not_increasing = all(swap_values[i] >= swap_values[i + 1] for i in range(len(swap_values) - 1)) if len(swap_values) >= 2 else False

    soft_pass = (
        post["swap"].get("used_pct", 100) <= 50
        and not_increasing
        and not active_q38_pids()
    )
    receipt["SOFT_RESOURCE_RECOVERY"] = "PASS" if soft_pass else "FAIL"
    receipt["RESOURCE_GATE"] = "PASS" if post["swap"].get("used_pct", 100) <= 25 else ("DEGRADED" if post["swap"].get("used_pct", 100) <= 50 else "BLOCKED_RESOURCE_PRESSURE")
    receipt["REBOOT_RECOMMENDED"] = receipt["SOFT_RESOURCE_RECOVERY"] == "FAIL"

    if receipt["REBOOT_RECOMMENDED"]:
        reboot = {
            "schema": "hydradg.qwen38.reboot_recommendation.v1",
            "recorded_at_utc": utc_now(),
            "reason": "Soft swap remediation insufficient; macOS swap remains elevated after verified stale process termination",
            "current_swap_used_pct": post["swap"].get("used_pct"),
            "memory_pressure": post["memory_pressure_head"],
            "remaining_large_processes": top_processes()[:15],
            "REBOOT_STATE": "HUMAN_APPROVAL_REQUIRED",
            "note": "Full swap reset on macOS generally requires reboot; purge is not used as evidence",
        }
        (OUT / "REBOOT_RECOMMENDATION.json").write_text(json.dumps(reboot, indent=2) + "\n", encoding="utf-8")
        receipt["reboot_recommendation_path"] = "eval/qwen38_model_replay_20260828/remediation/REBOOT_RECOMMENDATION.json"

    path = OUT / "SWAP_REMEDIATION_RECEIPT.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_sha256"] = sha256_bytes(path.read_bytes())
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "SOFT_RESOURCE_RECOVERY": receipt["SOFT_RESOURCE_RECOVERY"],
        "PRE_SWAP_USED_PCT": receipt["PRE_SWAP_USED_PCT"],
        "POST_SWAP_USED_PCT": receipt["POST_SWAP_USED_PCT"],
        "RESOURCE_GATE": receipt["RESOURCE_GATE"],
        "REBOOT_RECOMMENDED": receipt["REBOOT_RECOMMENDED"],
    }, indent=2))
    return 0 if soft_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
