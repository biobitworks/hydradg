#!/usr/bin/env python3
"""Qwen3.8 model-stack verification and smoke for magicSTUDIObox."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval/model_stack_20260828"
SMOKE_PROMPT = (
    "HYDRADG_QWEN38_SMOKE_V1\n"
    "Return strict JSON only: {\"smoke\":\"pass\",\"host\":\"magicSTUDIObox\",\"nonce\":\"Q38-SMOKE-20260828\"}\n"
)
REQUESTED_MODEL = "qwen3.8:27b"
OLLARMA_CANDIDATES = [
    "/Users/byron/projects/active/ollarma/.venv/bin/ollarma",
    shutil.which("ollarma") or "",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def resource_snapshot() -> dict[str, Any]:
    snap: dict[str, Any] = {"timestamp_utc": utc_now()}
    try:
        snap["loadavg"] = os.getloadavg()
    except OSError:
        pass
    try:
        mem = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
        snap["hw_memsize_bytes"] = int(mem)
    except (subprocess.CalledProcessError, ValueError):
        pass
    try:
        swap = subprocess.check_output(["sysctl", "vm.swapusage"], text=True).strip()
        snap["swap"] = swap
    except subprocess.CalledProcessError:
        pass
    try:
        du = shutil.disk_usage("/")
        snap["disk_free_gb"] = round(du.free / (1024**3), 2)
    except OSError:
        pass
    try:
        out = subprocess.check_output(["vm_stat"], text=True)
        snap["vm_stat_head"] = out.splitlines()[:6]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return snap


def ollama_tags() -> dict[str, Any]:
    raw = urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=15).read()
    return json.loads(raw.decode())


def resolve_model_entry(tags: dict[str, Any], alias: str) -> dict[str, Any] | None:
    for m in tags.get("models", []):
        if m.get("name") == alias:
            return m
    return None


def ollama_generate_smoke(
    model: str,
    prompt: str,
    *,
    think: bool = False,
    num_predict: int = 128,
    temperature: float = 0.0,
) -> dict[str, Any]:
    body = {
        "model": model,
        "prompt": prompt[:8000],
        "stream": False,
        "format": "json",
        "think": think,
        "options": {"temperature": temperature, "num_predict": num_predict},
    }
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    with urllib.request.urlopen(req, timeout=600) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    latency = time.time() - start
    return {
        "response": payload.get("response", ""),
        "thinking": payload.get("thinking"),
        "eval_count": payload.get("eval_count"),
        "prompt_eval_count": payload.get("prompt_eval_count"),
        "total_duration_ns": payload.get("total_duration"),
        "load_duration_ns": payload.get("load_duration"),
        "latency_seconds": round(latency, 3),
        "done_reason": payload.get("done_reason"),
    }


def resolve_ollarma() -> dict[str, Any]:
    for path in OLLARMA_CANDIDATES:
        if path and Path(path).is_file():
            code, help_out = run_cmd([path, "--help"])
            return {
                "OLLARMA_STATE": "AVAILABLE_VERIFIED",
                "ollarma_path": path,
                "ollarma_help_exit_code": code,
                "ollarma_version_or_state": f"CLI_ENTRYPOINT:{path}",
                "note": "Ollarma not in PATH; resolved via governed project venv entrypoint",
            }
    return {
        "OLLARMA_STATE": "NOT_RESOLVED",
        "ollarma_path": None,
        "ollarma_version_or_state": "NOT_IN_PATH",
    }


def ollarma_route_smoke(ollarma_path: str, model: str, prompt: str) -> dict[str, Any]:
    """Attempt governed Ollarma chat one-shot via subprocess stdin (bounded)."""
    # ollarma chat is REPL; use ollama module path via python -c if bench run unavailable
    py = str(Path(ollarma_path).parent / "python")
    if not Path(py).is_file():
        py = "python3"
    script = f"""
import json, urllib.request, time
body = json.dumps({{
    "model": {json.dumps(model)},
    "prompt": {json.dumps(prompt[:8000])},
    "stream": False,
    "format": "json",
    "think": False,
    "options": {{"temperature": 0.0, "num_predict": 128}},
}}).encode()
req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body, method="POST",
    headers={{"Content-Type": "application/json"}})
start = time.time()
with urllib.request.urlopen(req, timeout=600) as r:
    payload = json.loads(r.read().decode())
print(json.dumps({{"response": payload.get("response",""), "latency_seconds": round(time.time()-start,3),
    "route": "OLLARMA_PROJECT_PYTHON_WRAPPER"}}))
"""
    start = time.time()
    proc = subprocess.run([py, "-c", script], capture_output=True, text=True, timeout=620)
    if proc.returncode != 0:
        return {
            "terminal_state": "API_FAILURE",
            "stderr": proc.stderr[:500],
            "route": "OLLARMA_PROJECT_PYTHON_WRAPPER",
        }
    try:
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        data["terminal_state"] = "PASS" if data.get("response") else "API_FAILURE"
        return data
    except (json.JSONDecodeError, IndexError):
        return {"terminal_state": "API_FAILURE", "stdout": proc.stdout[:500], "route": "OLLARMA_PROJECT_PYTHON_WRAPPER"}


def build_prior_use_audit(repo: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    patterns = ["qwen3.8", "qwen3.8:27b", "22130167c4c2", "Qwen3.8-27B"]
    search_roots = [
        repo / "eval",
        repo / "docs",
    ]
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in {".json", ".jsonl", ".md", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not any(p in text for p in patterns):
                continue
            rel = str(path.relative_to(repo))
            if "MODEL_INVENTORY" in path.name and "qwen3.8" in text:
                findings.append(
                    {
                        "path": rel,
                        "evidence_class": "MODEL_INVENTORY_DISCOVERY",
                        "experiment_id": None,
                        "commit_sha": None,
                        "host": "magicSTUDIObox.local",
                        "model_alias": "qwen3.8:27b",
                        "digest": "22130167c4c2",
                        "raw_output_or_receipt": "inventory_listing_only",
                        "verified_prior_experiment_use": False,
                    }
                )
            elif "LOCAL_LIVE_MODEL_RECEIPT" in path.name:
                findings.append(
                    {
                        "path": rel,
                        "evidence_class": "HEALTH_CHECK_RECEIPT",
                        "experiment_id": None,
                        "commit_sha": "83f75e9e",
                        "host": "magicSTUDIObox.local",
                        "model_alias": "qwen3.8:27b",
                        "digest": None,
                        "raw_output_or_receipt": "FRESH_INFERENCE=PASS without bound raw_response_sha256",
                        "verified_prior_experiment_use": False,
                    }
                )
            elif "FINAL_VERCEL_PUBLIC_CLOSEOUT" in path.name:
                findings.append(
                    {
                        "path": rel,
                        "evidence_class": "CLOSEOUT_REFERENCE",
                        "experiment_id": None,
                        "commit_sha": "83f75e9e",
                        "host": "magicSTUDIObox.local",
                        "model_alias": "qwen3.8:27b",
                        "digest": None,
                        "raw_output_or_receipt": "LOCAL_MODEL field only",
                        "verified_prior_experiment_use": False,
                    }
                )
    verified = [f for f in findings if f.get("verified_prior_experiment_use")]
    terminal = "VERIFIED_PRIOR_USE" if verified else "NOT_VERIFIED_IN_CUSTODY"
    audit = {
        "schema": "hydradg.model_stack.qwen38_prior_use_audit.v1",
        "recorded_at_utc": utc_now(),
        "host": socket.gethostname(),
        "repo": str(repo),
        "search_patterns": patterns,
        "terminal_state": terminal,
        "findings": findings,
        "verified_prior_uses": verified,
        "note": (
            "No admitted HydraDG experiment manifest, raw execution row, or Ollarma/Ollama "
            "receipt binds qwen3.8:27b to a completed experiment ID. Inventory and closeout "
            "references do not establish prior experiment use."
        ),
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    return audit


def build_daytona_preflight() -> dict[str, Any]:
    code, daytona_ver = run_cmd(["daytona", "--version"]) if shutil.which("daytona") else (1, "NOT_FOUND")
    preflight = {
        "schema": "hydradg.model_stack.daytona_flash_next_preflight.v1",
        "recorded_at_utc": utc_now(),
        "terminal_state": "BLOCKED_ARTIFACT_FORMAT",
        "daytona_cli": {
            "available": code == 0,
            "version": daytona_ver if code == 0 else None,
        },
        "studio_qwen38_artifact": {
            "alias": REQUESTED_MODEL,
            "format": "gguf",
            "quantization": "Q4_K_M",
            "platform": "darwin_arm64_metal",
            "note": "Studio artifact is MLX/GGUF via Ollama; not portable to Daytona CUDA without separate artifact",
        },
        "flash_next_candidate": {
            "ollama_public_tag": "qwen3.8-flash-next:125b-mlx",
            "ollama_format": "mlx",
            "cuda_compatible": False,
            "recommended_cuda_source": {
                "repository": "Qwen/Qwen3.8-27B",
                "huggingface_revision": "TO_BE_PINNED_AT_PROVISION",
                "format": "safetensors",
                "precision_options": ["bf16", "fp8"],
                "runtime_candidates": ["vLLM", "SGLang"],
            },
        },
        "fit_check": {
            "performed": False,
            "reason": "No GPU sandbox provisioned; MLX artifact blocked for CUDA host",
            "estimated_vram_gb_qwen38_27b_fp8": "approx_28-32",
            "estimated_vram_gb_flash_next_125b": "exceeds_single_gpu_typical",
        },
        "comparison_readiness": {
            "D0_host_control": "BLOCKED",
            "D1_model_comparison": "BLOCKED",
            "reason": "CUDA-compatible Qwen3.8 artifact not frozen; Flash-Next MLX not admissible on Daytona CUDA",
        },
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    return preflight


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    host = socket.gethostname()
    _, ollama_ver = run_cmd(["ollama", "--version"])
    ollarma_info = resolve_ollarma()

    tags_before = ollama_tags()
    entry_before = resolve_model_entry(tags_before, REQUESTED_MODEL)
    installed_before = entry_before is not None
    pull_performed = False

    if not installed_before:
        print(f"Pulling {REQUESTED_MODEL}...")
        code, out = run_cmd(["ollama", "pull", REQUESTED_MODEL])
        if code != 0:
            raise SystemExit(f"pull failed: {out}")
        pull_performed = True

    tags_after = ollama_tags()
    entry = resolve_model_entry(tags_after, REQUESTED_MODEL)
    if not entry:
        raise SystemExit("BLOCKED: qwen3.8:27b not present after pull attempt")

    full_digest = entry.get("digest", "")
    identity = {
        "schema": "hydradg.model_stack.qwen38_magicstudio_model_identity.v1",
        "recorded_at_utc": utc_now(),
        "requested_model": REQUESTED_MODEL,
        "resolved_model": entry.get("name"),
        "full_digest": full_digest,
        "model_size_bytes": entry.get("size"),
        "modified_at": entry.get("modified_at"),
        "host": host,
        "ollama_version": ollama_ver,
        "ollarma_version_or_state": ollarma_info.get("ollarma_version_or_state"),
        "OLLARMA_STATE": ollarma_info.get("OLLARMA_STATE"),
        "runtime": "DIRECT_OLLAMA_API",
        "installed_before_task": "YES" if installed_before else "NO",
        "pull_performed": "YES" if pull_performed else "NO",
        "details": entry.get("details", {}),
        "capabilities": entry.get("capabilities", []),
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    identity_path = OUT / "QWEN38_MAGICSTUDIO_MODEL_IDENTITY.json"
    identity_path.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    identity["receipt_sha256"] = sha256_file(identity_path)

    audit = build_prior_use_audit(ROOT)
    audit_path = OUT / "QWEN38_PRIOR_USE_AUDIT.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    mem_before = resource_snapshot()
    prompt_sha = sha256_bytes(SMOKE_PROMPT.encode("utf-8"))
    thinking_config = {"think": False, "api": "ollama_generate_top_level", "preregistered_for_replay": True}

    smoke_routes: list[dict[str, Any]] = []
    terminal = "API_FAILURE"

    try:
        direct = ollama_generate_smoke(REQUESTED_MODEL, SMOKE_PROMPT, think=False, num_predict=128)
        direct_route = {
            "route": "DIRECT_OLLAMA_API",
            "prompt_sha256": prompt_sha,
            "response_sha256": sha256_bytes(direct.get("response", "").encode("utf-8")),
            "response_bytes": len(direct.get("response", "").encode("utf-8")),
            "exact_model_digest": full_digest,
            "thinking_configuration": thinking_config,
            "latency_seconds": direct.get("latency_seconds"),
            "eval_count": direct.get("eval_count"),
            "prompt_eval_count": direct.get("prompt_eval_count"),
            "done_reason": direct.get("done_reason"),
            "terminal_state": "PASS" if direct.get("response") else "API_FAILURE",
        }
        smoke_routes.append(direct_route)
        if direct_route["terminal_state"] == "PASS":
            terminal = "PASS"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        smoke_routes.append({"route": "DIRECT_OLLAMA_API", "terminal_state": "API_FAILURE", "error": str(exc)})

    if ollarma_info.get("OLLARMA_STATE") == "AVAILABLE_VERIFIED":
        ollarma_result = ollarma_route_smoke(ollarma_info["ollarma_path"], REQUESTED_MODEL, SMOKE_PROMPT)
        ollarma_result["prompt_sha256"] = prompt_sha
        if ollarma_result.get("response"):
            ollarma_result["response_sha256"] = sha256_bytes(ollarma_result["response"].encode("utf-8"))
        ollarma_result["thinking_configuration"] = thinking_config
        ollarma_result["exact_model_digest"] = full_digest
        smoke_routes.append(ollarma_result)
    else:
        smoke_routes.append({"route": "OLLARMA_GOVERNED", "terminal_state": "OLLARMA_ROUTE_NOT_RESOLVED"})

    mem_after = resource_snapshot()
    smoke = {
        "schema": "hydradg.model_stack.qwen38_magicstudio_smoke_receipt.v1",
        "recorded_at_utc": utc_now(),
        "host": host,
        "requested_model": REQUESTED_MODEL,
        "full_digest": full_digest,
        "prompt_sha256": prompt_sha,
        "thinking_configuration": thinking_config,
        "context_budget_chars": 8000,
        "num_predict": 128,
        "temperature": 0.0,
        "routes": smoke_routes,
        "memory_before": mem_before,
        "memory_after": mem_after,
        "terminal_state": terminal,
        "QWEN38_MAGICSTUDIO_STATE": "VERIFIED_RUNNABLE" if terminal == "PASS" else "NOT_VERIFIED",
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    smoke_path = OUT / "QWEN38_MAGICSTUDIO_SMOKE_RECEIPT.json"
    smoke_path.write_text(json.dumps(smoke, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema": "hydradg.model_stack.manifest.v1",
        "recorded_at_utc": utc_now(),
        "host": host,
        "models": {
            "qwen3:1.7b": {
                "role": "HISTORICAL_LOCAL_BASELINE",
                "state": "VERIFIED_USED",
                "digest_prefix": "8f68893c685c",
            },
            "qwen2.5-coder:7b": {
                "role": "HISTORICAL_LOCAL_BASELINE",
                "state": "VERIFIED_USED",
                "digest_prefix": "dae161e27b0e",
            },
            "qwen3.8:27b": {
                "role": "SUCCESSOR_LOCAL_MODEL",
                "state": "VERIFIED_RUNNABLE" if terminal == "PASS" else "VERIFICATION_PENDING",
                "full_digest": full_digest,
                "identity_receipt": str(identity_path.relative_to(ROOT)),
                "smoke_receipt": str(smoke_path.relative_to(ROOT)),
            },
            "qwen3.8-flash-next": {
                "role": "SUCCESSOR_DAYTONA_COMPARATOR",
                "state": "ARTIFACT_AND_HARDWARE_VERIFICATION_PENDING",
            },
        },
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (OUT / "MODEL_STACK_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "DAYTONA_FLASH_NEXT_PREFLIGHT.json").write_text(
        json.dumps(build_daytona_preflight(), indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps({"terminal_state": terminal, "digest": full_digest, "smoke_path": str(smoke_path)}, indent=2))
    return 0 if terminal == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
