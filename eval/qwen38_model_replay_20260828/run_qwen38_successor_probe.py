#!/usr/bin/env python3
"""HydraDG Qwen3.8 successor probe — digest-bound canary with independent execution paths."""
from __future__ import annotations

import hashlib
import json
import secrets
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "local_canary"
HISTORICAL = ROOT / "eval/vercel_public_closeout_20260827/LOCAL_LIVE_MODEL_RECEIPT.json"
MODEL = "qwen3.8:27b"
EXPECTED_DIGEST = "22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643"
OLLARMA = "http://127.0.0.1:8484/chat"
OLLAMA_TAGS = "http://127.0.0.1:11434/api/tags"
OLLAMA_SHOW = "http://127.0.0.1:11434/api/show"
OLLAMA_CHAT = "http://127.0.0.1:11434/api/chat"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git(field: str) -> str:
    mapping = {"branch": ("branch", "--show-current"), "head": ("rev-parse", "HEAD")}
    cmd = mapping[field]
    return subprocess.check_output(["git", "-C", str(ROOT), *cmd], text=True).strip()


def build_prompt(nonce: str) -> str:
    return (
        "HydraDG LOCAL_LIVE successor probe. Return ONLY strict JSON with keys: "
        '"nonce" (string), "model_lane" (string), "status" (string OK). '
        f'The nonce must be exactly "{nonce}". No markdown.'
    )


def fetch_runtime_identity() -> dict:
    tags_raw = urllib.request.urlopen(OLLAMA_TAGS, timeout=15).read()
    tags = json.loads(tags_raw.decode())
    entry = next((m for m in tags.get("models", []) if m.get("name") == MODEL), None)
    show_payload = json.dumps({"name": MODEL}).encode()
    show_req = urllib.request.Request(
        OLLAMA_SHOW, data=show_payload, method="POST", headers={"Content-Type": "application/json"}
    )
    show = json.loads(urllib.request.urlopen(show_req, timeout=30).read().decode())
    observed = entry.get("digest", "") if entry else ""
    details = entry.get("details", {}) if entry else {}
    identity = {
        "schema": "hydradg.qwen38.model_runtime_identity.v1",
        "recorded_at_utc": utc_now(),
        "model_name": MODEL,
        "EXPECTED_DIGEST": EXPECTED_DIGEST,
        "OBSERVED_DIGEST": observed,
        "DIGEST_MATCH": "PASS" if observed == EXPECTED_DIGEST else "FAIL",
        "modified_at": entry.get("modified_at") if entry else None,
        "size_bytes": entry.get("size") if entry else None,
        "details": details,
        "quantization": details.get("quantization_level"),
        "parameter_size": details.get("parameter_size"),
        "families": details.get("families"),
        "capabilities": entry.get("capabilities") if entry else [],
        "show_modelfile_head": (show.get("modelfile") or "")[:500],
        "host": subprocess.check_output(["hostname"], text=True).strip(),
    }
    return identity


def ollarma_chat(prompt: str) -> dict:
    body = json.dumps(
        {
            "model": MODEL,
            "message": prompt,
            "strict_model_identity": True,
            "temperature": 0,
        }
    ).encode()
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(
            OLLARMA,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=900) as resp:
            parsed = json.loads(resp.read().decode())
        blocked = parsed.get("status") in ("blocked", "error") or parsed.get("reason_code")
        return {
            "path": "OLLARMA_GOVERNED",
            "latency_sec": round(time.perf_counter() - t0, 3),
            "status": parsed.get("status"),
            "reason_code": parsed.get("reason_code"),
            "executed_model": parsed.get("model"),
            "response": parsed.get("response", ""),
            "blocked": blocked,
            "detail": parsed.get("detail"),
        }
    except Exception as exc:
        return {
            "path": "OLLARMA_GOVERNED",
            "latency_sec": round(time.perf_counter() - t0, 3),
            "status": "error",
            "reason_code": type(exc).__name__,
            "detail": str(exc),
            "blocked": True,
        }


def ollama_direct(prompt: str) -> dict:
    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0, "num_predict": 128},
        }
    ).encode()
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(
            OLLAMA_CHAT, data=payload, method="POST", headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=900) as resp:
            data = json.loads(resp.read().decode())
        msg = data.get("message") or {}
        return {
            "path": "DIRECT_OLLAMA",
            "latency_sec": round(time.perf_counter() - t0, 3),
            "status": "ok",
            "executed_model": data.get("model", MODEL),
            "response": msg.get("content", ""),
            "blocked": False,
        }
    except Exception as exc:
        return {
            "path": "DIRECT_OLLAMA",
            "latency_sec": round(time.perf_counter() - t0, 3),
            "status": "error",
            "reason_code": type(exc).__name__,
            "detail": str(exc),
            "blocked": True,
        }


def verify_nonce(raw: str, nonce: str) -> tuple[bool, str]:
    try:
        obj = json.loads(raw.strip())
    except json.JSONDecodeError:
        return False, "NO_JSON"
    if obj.get("nonce") != nonce:
        return False, "NONCE_MISMATCH"
    if str(obj.get("status", "")).upper() != "OK":
        return False, "STATUS_NOT_OK"
    return True, "PASS"


def classify_governed(governed: dict, nonce: str) -> str:
    if governed.get("blocked"):
        rc = governed.get("reason_code") or governed.get("status") or "BLOCKED"
        if governed.get("status") == "error":
            return "OLLARMA_GOVERNED_ERROR"
        return "OLLARMA_GOVERNED_BLOCKED"
    raw = str(governed.get("response") or "")
    ok, _ = verify_nonce(raw, nonce) if raw else (False, "EMPTY")
    return "OLLARMA_GOVERNED_PASS" if ok else "OLLARMA_GOVERNED_ERROR"


def classify_direct(direct: dict, nonce: str) -> str:
    if direct.get("blocked") or direct.get("status") == "error":
        return "DIRECT_OLLAMA_FAIL"
    raw = str(direct.get("response") or "")
    ok, _ = verify_nonce(raw, nonce) if raw else (False, "EMPTY")
    return "DIRECT_OLLAMA_PASS" if ok else "DIRECT_OLLAMA_FAIL"


def ollarma_state_snapshot() -> dict:
    try:
        health = json.loads(urllib.request.urlopen("http://127.0.0.1:8484/health", timeout=10).read().decode())
    except Exception as exc:
        return {"OLLARMA_STATE": "UNREACHABLE", "error": str(exc)}
    sel = health.get("chat_selection") or {}
    return {
        "schema": "hydradg.qwen38.ollarma_state.v1",
        "recorded_at_utc": utc_now(),
        "OLLARMA_STATE": health.get("status", "UNKNOWN"),
        "effective_model": sel.get("model"),
        "selection_status": sel.get("status"),
        "reason_code": sel.get("reason_code"),
        "detail": sel.get("detail"),
        "startup_readiness": health.get("startup_readiness"),
    }


def resource_receipt() -> dict:
    import os
    import shutil

    snap: dict = {"timestamp_utc": utc_now()}
    try:
        snap["loadavg"] = os.getloadavg()
    except OSError:
        pass
    try:
        du = shutil.disk_usage("/")
        snap["disk_free_gb"] = round(du.free / (1024**3), 2)
    except OSError:
        pass
    try:
        snap["swap"] = subprocess.check_output(["sysctl", "-n", "vm.swapusage"], text=True).strip()
    except subprocess.CalledProcessError:
        pass
    return snap


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    nonce = secrets.token_hex(8)
    prompt = build_prompt(nonce)
    prompt_sha = sha256_text(prompt)

    identity = fetch_runtime_identity()
    (OUT / "MODEL_RUNTIME_IDENTITY.json").write_text(json.dumps(identity, indent=2) + "\n")

    ollarma_snap = ollarma_state_snapshot()
    (OUT / "OLLARMA_STATE.json").write_text(json.dumps(ollarma_snap, indent=2) + "\n")

    # Direct path first — governed path may block/timeout under concurrent matrix load.
    direct = ollama_direct(prompt)
    ollarma_degraded = ollarma_snap.get("reason_code") == "SELECTION_STALE"
    if ollarma_degraded:
        governed = {
            "path": "OLLARMA_GOVERNED",
            "status": "blocked",
            "reason_code": "SELECTION_STALE",
            "detail": ollarma_snap.get("detail"),
            "blocked": True,
        }
    else:
        governed = ollarma_chat(prompt)

    governed_verdict = classify_governed(governed, nonce)
    direct_verdict = classify_direct(direct, nonce)
    governed_ok = governed_verdict == "OLLARMA_GOVERNED_PASS"
    direct_ok = direct_verdict == "DIRECT_OLLAMA_PASS"

    governed_raw = str(governed.get("response") or "")
    direct_raw = str(direct.get("response") or "")

    hist = json.loads(HISTORICAL.read_text()) if HISTORICAL.exists() else {}

    receipt = {
        "schema": "hydradg.qwen38_successor_canary.v1",
        "receipt_id": "QWEN38_SUCCESSOR_CANARY_20260828",
        "recorded_at_utc": utc_now(),
        "classification": "SUCCESSOR_VERIFICATION",
        "historical_receipt": str(HISTORICAL.relative_to(ROOT)) if HISTORICAL.exists() else None,
        "successor_model": MODEL,
        "EXPECTED_DIGEST": EXPECTED_DIGEST,
        "OBSERVED_DIGEST": identity["OBSERVED_DIGEST"],
        "DIGEST_MATCH": identity["DIGEST_MATCH"],
        "execution_host": identity["host"],
        "repo": str(ROOT),
        "branch": git("branch"),
        "git_commit": git("head"),
        "MODEL_PREEXISTENCE_STATE": "PRESENT",
        "prompt_sha256": prompt_sha,
        "governed_attempt": governed,
        "direct_attempt": direct,
        "governed_verdict": governed_verdict,
        "direct_verdict": direct_verdict,
        "governed_nonce_ok": governed_ok,
        "direct_nonce_ok": direct_ok,
        "canary_pass_requires_digest_match": identity["DIGEST_MATCH"] == "PASS",
        "identity_equivalent_canary": identity["DIGEST_MATCH"] == "PASS" and direct_ok,
        "historical_summary": {
            "SELECTED_MODEL": hist.get("SELECTED_MODEL"),
            "FRESH_INFERENCE": hist.get("FRESH_INFERENCE"),
            "NONCE_ROUNDTRIP": hist.get("NONCE_ROUNDTRIP"),
        },
        "claim_ceiling": "PROBABILISTIC_MODEL_OUTPUT",
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (OUT / "QWEN38_CANARY_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    raw_out = {
        "governed_raw_sha256": sha256_text(governed_raw) if governed_raw else None,
        "direct_raw_sha256": sha256_text(direct_raw) if direct_raw else None,
        "governed_raw_head": governed_raw[:2000],
        "direct_raw_head": direct_raw[:2000],
    }
    (OUT / "RAW_OUTPUT.json").write_text(json.dumps(raw_out, indent=2) + "\n")
    (OUT / "RESOURCE_RECEIPT.json").write_text(json.dumps(resource_receipt(), indent=2) + "\n")

    print(
        json.dumps(
            {
                "DIGEST_MATCH": identity["DIGEST_MATCH"],
                "governed_verdict": governed_verdict,
                "direct_verdict": direct_verdict,
                "identity_equivalent_canary": receipt["identity_equivalent_canary"],
            },
            indent=2,
        )
    )
    return 0 if receipt["identity_equivalent_canary"] else 1


if __name__ == "__main__":
    sys.exit(main())
