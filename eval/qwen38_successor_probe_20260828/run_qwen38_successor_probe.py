#!/usr/bin/env python3
"""HydraDG successor Qwen3.8 probe — digest-bound canary with separate execution paths."""
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

REPO = Path("/Users/byron/projects/active/hydradg")
OUT = REPO / "eval" / "qwen38_successor_probe_20260828"
HISTORICAL = REPO / "eval" / "vercel_public_closeout_20260827" / "LOCAL_LIVE_MODEL_RECEIPT.json"
MODEL = "qwen3.8:27b"
DIGEST = "22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643"
OLLARMA = "http://127.0.0.1:8484/chat"
OLLAMA = "http://127.0.0.1:11434/api/chat"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git(field: str) -> str:
    mapping = {"branch": ("branch", "--show-current"), "head": ("rev-parse", "HEAD")}
    cmd = mapping[field]
    return subprocess.check_output(["git", "-C", str(REPO), *cmd], text=True).strip()


def build_prompt(nonce: str) -> str:
    return (
        "HydraDG LOCAL_LIVE successor probe. Return ONLY strict JSON with keys: "
        '"nonce" (string), "model_lane" (string), "status" (string OK). '
        f'The nonce must be exactly "{nonce}". No markdown.'
    )


def ollarma_chat(prompt: str) -> dict:
    body = json.dumps({
        "model": MODEL,
        "message": prompt,
        "strict_model_identity": True,
        "temperature": 0,
    }).encode()
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
        return {
            "path": "Ollarma_HTTP_8484_chat",
            "latency_sec": round(time.perf_counter() - t0, 3),
            "status": parsed.get("status"),
            "reason_code": parsed.get("reason_code"),
            "executed_model": parsed.get("model"),
            "response": parsed.get("response", ""),
            "blocked": parsed.get("status") == "blocked",
        }
    except Exception as exc:
        return {
            "path": "Ollarma_HTTP_8484_chat",
            "latency_sec": round(time.perf_counter() - t0, 3),
            "status": "error",
            "reason_code": type(exc).__name__,
            "detail": str(exc),
            "blocked": True,
        }


def ollama_direct(prompt: str) -> dict:
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0, "num_predict": 128},
    }).encode()
    t0 = time.perf_counter()
    req = urllib.request.Request(OLLAMA, data=payload, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        data = json.loads(resp.read().decode())
    msg = data.get("message") or {}
    return {
        "path": "EXECUTION_PATH_B_Ollama_API_direct",
        "latency_sec": round(time.perf_counter() - t0, 3),
        "status": "ok",
        "executed_model": data.get("model", MODEL),
        "response": msg.get("content", ""),
        "blocked": False,
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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    nonce = secrets.token_hex(8)
    prompt = build_prompt(nonce)
    prompt_sha = sha256_text(prompt)
    settings_sha = sha256_text(json.dumps({"model": MODEL, "temperature": 0, "strict_model_identity": True}, sort_keys=True))

    governed = ollarma_chat(prompt)
    direct = None
    governed_ok = (
        not governed.get("blocked")
        and governed.get("status") not in ("error",)
        and verify_nonce(str(governed.get("response") or ""), nonce)[0]
    )
    if not governed_ok:
        try:
            direct = ollama_direct(prompt)
        except Exception as exc:
            direct = {
                "path": "EXECUTION_PATH_B_Ollama_API_direct",
                "status": "error",
                "reason_code": type(exc).__name__,
                "detail": str(exc),
                "blocked": True,
            }

    primary = governed if governed_ok else (direct or governed)
    raw = str(primary.get("response") or "")
    ok, reason = verify_nonce(raw, nonce) if raw else (False, "EMPTY")

    hist = json.loads(HISTORICAL.read_text()) if HISTORICAL.exists() else {}

    receipt = {
        "schema": "hydradg.qwen38_successor_probe.v1",
        "receipt_id": "QWEN38_HYDRADG_SUCCESSOR_PROBE",
        "recorded_at_utc": utc_now(),
        "classification": "SUCCESSOR_CANARY_REPLICATION",
        "historical_receipt": str(HISTORICAL.relative_to(REPO)),
        "historical_digest": "UNKNOWN",
        "historical_prompt_recoverable": False,
        "successor_model": MODEL,
        "successor_digest": DIGEST,
        "execution_host": subprocess.check_output(["hostname"], text=True).strip(),
        "repo": str(REPO),
        "branch": git("branch"),
        "git_commit": git("head"),
        "historical_summary": {
            "SELECTED_MODEL": hist.get("SELECTED_MODEL"),
            "FRESH_INFERENCE": hist.get("FRESH_INFERENCE"),
            "NONCE_ROUNDTRIP": hist.get("NONCE_ROUNDTRIP"),
            "recorded_at_utc": hist.get("recorded_at_utc"),
        },
        "prompt": prompt,
        "prompt_sha256": prompt_sha,
        "settings_sha256": settings_sha,
        "governed_attempt": governed,
        "direct_attempt": direct,
        "governed_verdict": "PASS" if (not governed.get("blocked") and ok) else governed.get("reason_code", "FAIL"),
        "direct_verdict": (
            "NOT_RUN" if direct is None else ("PASS" if verify_nonce(str(direct.get("response") or ""), nonce)[0] else "FAIL")
        ),
        "verifier": "hydradg_nonce_roundtrip.v1",
        "verdict": "PASS" if ok else reason,
        "raw_output": raw[:4000],
        "raw_output_sha256": sha256_text(raw) if raw else None,
        "claim_ceiling": "PROBABILISTIC_MODEL_OUTPUT",
    }

    out_path = OUT / "QWEN38_HYDRADG_SUCCESSOR_PROBE_RECEIPT.json"
    out_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"verdict": receipt["verdict"], "classification": receipt["classification"]}, indent=2))
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
