#!/usr/bin/env python3
"""SGLang BCG Kaggle GPU runtime stress — ENGINEERING_RUNTIME_STRESS_EVAL_ONLY.

Pinned: sglang==0.5.18 / Qwen/Qwen2.5-1.5B-Instruct
Conditions: C0 disabled / C1 tc_piecewise / C2 breakable (decode=full)
Corpus: SYNTHETIC_ENGINEERING_FIXTURE only. Not Daisy T00-T12. No HydraDB.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "SGLANG-BCG-KAGGLE-20260826"
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
SGLANG_VERSION = "0.5.18"
SGLANG_COMMIT = "71de97b264b04dcd514cf904003028aefe9775c8"
MAX_GPU_MINUTES = 75
BUDGET_RESERVE_S = 180  # stop before hard ceiling
PORT = 30000
REQUEST_TIMEOUT_S = 180
SERVER_READY_TIMEOUT_S = 600
START_TS = time.time()

HERE = Path(__file__).resolve().parent
# Kaggle working dir is typically /kaggle/working
OUT = Path(os.environ.get("BCG_OUT_DIR", "/kaggle/working"))
if not OUT.exists():
    OUT = HERE / "working"
OUT.mkdir(parents=True, exist_ok=True)
(RESP_DIR := OUT / "responses").mkdir(exist_ok=True)
(LOG_DIR := OUT / "server_logs").mkdir(exist_ok=True)
(COND_DIR := OUT / "conditions").mkdir(exist_ok=True)

CONDITIONS = [
    {"condition_id": "C0", "name": "EAGER_PREFILL_CONTROL", "prefill_backend": "disabled", "decode_backend": "full"},
    {"condition_id": "C1", "name": "TORCH_COMPILE_PIECEWISE_CONTROL", "prefill_backend": "tc_piecewise", "decode_backend": "full"},
    {"condition_id": "C2", "name": "BREAKABLE_CUDA_GRAPH", "prefill_backend": "breakable", "decode_backend": "full"},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def remaining_s() -> float:
    return MAX_GPU_MINUTES * 60 - (time.time() - START_TS) - BUDGET_RESERVE_S


def budget_ok(need_s: float = 60.0) -> bool:
    return remaining_s() > need_s


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def append_jsonl(path: Path, obj: Any) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True, default=str) + "\n")


def run_cmd(cmd: list[str], timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def nvidia_smi_query() -> dict[str, Any]:
    try:
        cp = run_cmd(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            timeout=30,
        )
        if cp.returncode != 0:
            return {"error": cp.stderr.strip()[:500]}
        line = cp.stdout.strip().splitlines()[0]
        parts = [p.strip() for p in line.split(",")]
        return {
            "GPU_NAME": parts[0] if parts else None,
            "GPU_DRIVER": parts[1] if len(parts) > 1 else None,
            "memory_total_mib": float(parts[2]) if len(parts) > 2 else None,
            "memory_used_mib": float(parts[3]) if len(parts) > 3 else None,
            "utilization_gpu": float(parts[4]) if len(parts) > 4 else None,
        }
    except Exception as exc:
        return {"error": str(exc)}


def extract_help_flags(help_text: str) -> dict[str, Any]:
    flags = {
        "cuda_graph_backend_prefill": "--cuda-graph-backend-prefill" in help_text,
        "cuda_graph_backend_decode": "--cuda-graph-backend-decode" in help_text,
        "cuda_graph_max_bs": bool(re.search(r"cuda-graph.*max-bs|--cuda-graph-bs", help_text)),
        "debug_cuda_graph": "--debug-cuda-graph" in help_text,
        "raw_matches": sorted(set(re.findall(r"--cuda-graph[\w\-]*", help_text))),
    }
    return flags


def install_sglang() -> dict[str, Any]:
    info: dict[str, Any] = {"spec": f"sglang=={SGLANG_VERSION}", "started_utc": utc_now()}
    t0 = time.time()
    # Prefer plain pin; extras may pull conflicting CUDA stacks on Kaggle.
    cmds = [
        [sys.executable, "-m", "pip", "install", "-q", "--upgrade", "pip"],
        [sys.executable, "-m", "pip", "install", "-q", f"sglang=={SGLANG_VERSION}"],
    ]
    logs = []
    for cmd in cmds:
        cp = run_cmd(cmd, timeout=1800)
        logs.append({"cmd": cmd, "rc": cp.returncode, "stderr_tail": (cp.stderr or "")[-2000:]})
        if cp.returncode != 0:
            info["ok"] = False
            info["logs"] = logs
            info["elapsed_s"] = time.time() - t0
            return info
    info["ok"] = True
    info["elapsed_s"] = time.time() - t0
    info["logs"] = [{"cmd": c["cmd"], "rc": c["rc"]} for c in logs]
    return info


def collect_environment(help_text: str | None) -> dict[str, Any]:
    import platform

    gpu = nvidia_smi_query()
    torch_v = None
    cuda_v = None
    try:
        import torch

        torch_v = torch.__version__
        cuda_v = getattr(torch.version, "cuda", None)
    except Exception:
        pass
    freeze = run_cmd([sys.executable, "-m", "pip", "freeze"], timeout=120)
    freeze_text = freeze.stdout or ""
    freeze_path = OUT / "pip_freeze.txt"
    freeze_path.write_text(freeze_text, encoding="utf-8")
    env = {
        "EXPERIMENT_ID": EXPERIMENT_ID,
        "recorded_utc": utc_now(),
        "SGLANG_VERSION": SGLANG_VERSION,
        "SGLANG_SOURCE": "pypi",
        "SGLANG_COMMIT_IF_SOURCE": SGLANG_COMMIT,
        "TORCH_VERSION": torch_v,
        "CUDA_VERSION": cuda_v,
        "GPU_NAME": gpu.get("GPU_NAME"),
        "GPU_DRIVER": gpu.get("GPU_DRIVER"),
        "PYTHON_VERSION": platform.python_version(),
        "platform": platform.platform(),
        "dtype_default": "float16",
        "pip_freeze_sha256": sha256_file(freeze_path),
        "gpu_query": gpu,
        "launch_server_help_flags": extract_help_flags(help_text or ""),
        "launch_server_help_sha256": sha256_bytes((help_text or "").encode()),
    }
    write_json(OUT / "environment.json", env)
    if help_text:
        (OUT / "sglang_launch_server_help.txt").write_text(help_text, encoding="utf-8")
    return env


def load_fixtures() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fix_path = HERE / "fixtures.jsonl"
    man_path = HERE / "MANIFEST.json"
    rows = []
    with fix_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    manifest = json.loads(man_path.read_text(encoding="utf-8"))
    # Verify hashes against preregistration when present
    got_fix = sha256_file(fix_path)
    got_man = sha256_file(man_path)
    if got_fix != manifest.get("fixtures_sha256"):
        raise RuntimeError(f"fixtures hash mismatch got={got_fix} expected={manifest.get('fixtures_sha256')}")
    return rows, manifest


class GpuSampler:
    def __init__(self, path: Path, interval_s: float = 2.0):
        self.path = path
        self.interval_s = interval_s
        self._stop = threading.Event()
        self._thr: threading.Thread | None = None
        self.peak_mem_mib = 0.0

    def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["utc", "t_rel_s", "memory_used_mib", "utilization_gpu"])
        self._thr = threading.Thread(target=self._loop, daemon=True)
        self._thr.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            q = nvidia_smi_query()
            mem = q.get("memory_used_mib") or 0.0
            util = q.get("utilization_gpu")
            try:
                mem_f = float(mem)
            except Exception:
                mem_f = 0.0
            self.peak_mem_mib = max(self.peak_mem_mib, mem_f)
            with self.path.open("a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([utc_now(), f"{time.time() - START_TS:.1f}", mem_f, util])
            self._stop.wait(self.interval_s)

    def stop(self) -> None:
        self._stop.set()
        if self._thr:
            self._thr.join(timeout=5)


def wait_http_ready(url: str, timeout_s: float) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if not budget_ok(30):
            return False
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status < 500:
                    return True
        except Exception:
            time.sleep(2)
    return False


def http_json(method: str, url: str, body: dict[str, Any] | None = None, timeout: float = REQUEST_TIMEOUT_S) -> tuple[int, Any, bytes]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                parsed = json.loads(raw.decode())
            except Exception:
                parsed = None
            return resp.status, parsed, raw
    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        try:
            parsed = json.loads(raw.decode())
        except Exception:
            parsed = {"error": str(e)}
        return e.code, parsed, raw


def classify_failure(text: str) -> str:
    t = (text or "").lower()
    if "out of memory" in t or "cuda oom" in t or "oom" in t:
        return "OOM"
    if "cuda graph" in t and "capture" in t:
        return "CUDA_GRAPH_CAPTURE_FAILURE"
    if "cuda graph" in t and ("replay" in t or "launch" in t):
        return "CUDA_GRAPH_REPLAY_FAILURE"
    if "unsupported" in t:
        return "UNSUPPORTED_CONFIGURATION"
    if "timeout" in t:
        return "TIMEOUT"
    return "UNKNOWN_FAILURE"


class ServerHandle:
    def __init__(self, condition: dict[str, Any], dtype: str = "float16"):
        self.condition = condition
        self.dtype = dtype
        self.proc: subprocess.Popen[str] | None = None
        self.log_path = LOG_DIR / f"{condition['condition_id']}_server.log"
        self.startup_s: float | None = None
        self.capture_s: float | None = None
        self.state = "NOT_STARTED"
        self.error: str | None = None

    def start(self) -> None:
        cid = self.condition["condition_id"]
        prefill = self.condition["prefill_backend"]
        decode = self.condition["decode_backend"]
        cmd = [
            sys.executable,
            "-m",
            "sglang.launch_server",
            "--model-path",
            MODEL,
            "--dtype",
            self.dtype,
            "--port",
            str(PORT),
            "--host",
            "127.0.0.1",
            "--trust-remote-code",
            "--mem-fraction-static",
            "0.75",
            "--cuda-graph-backend-prefill",
            prefill,
            "--cuda-graph-backend-decode",
            decode,
        ]
        self.log_path.write_text(f"# cmd={' '.join(cmd)}\n", encoding="utf-8")
        logf = self.log_path.open("a", encoding="utf-8")
        t0 = time.time()
        try:
            self.proc = subprocess.Popen(
                cmd,
                stdout=logf,
                stderr=subprocess.STDOUT,
                text=True,
                env={**os.environ, "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "0")},
            )
        except Exception as exc:
            self.state = "SERVER_CRASH"
            self.error = str(exc)
            logf.close()
            return
        ready = wait_http_ready(f"http://127.0.0.1:{PORT}/health", SERVER_READY_TIMEOUT_S)
        # fallback endpoints
        if not ready:
            ready = wait_http_ready(f"http://127.0.0.1:{PORT}/v1/models", SERVER_READY_TIMEOUT_S // 3)
        self.startup_s = time.time() - t0
        # Heuristic capture time from logs
        try:
            log_txt = self.log_path.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"capture.*?([0-9]+\.?[0-9]*)\s*s", log_txt, re.I)
            if m:
                self.capture_s = float(m.group(1))
            if "capture" in log_txt.lower() and ("fail" in log_txt.lower() or "error" in log_txt.lower()):
                if self.proc.poll() is not None:
                    self.state = classify_failure(log_txt)
                    self.error = "capture/startup failure"
                    return
        except Exception:
            pass
        if not ready or (self.proc.poll() is not None):
            log_txt = self.log_path.read_text(encoding="utf-8", errors="replace")[-8000:]
            self.state = classify_failure(log_txt) if "unsupported" in log_txt.lower() or "oom" in log_txt.lower() else "SERVER_CRASH"
            if "unsupported" in log_txt.lower() or "invalid" in log_txt.lower() and "backend" in log_txt.lower():
                self.state = "UNSUPPORTED_CONFIGURATION"
            self.error = log_txt[-2000:]
            return
        self.state = "READY"

    def stop(self) -> None:
        if not self.proc:
            return
        if self.proc.poll() is None:
            try:
                self.proc.send_signal(signal.SIGTERM)
                try:
                    self.proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
            except Exception:
                pass


def stream_completion(prompts: list[str], max_new_tokens: int) -> dict[str, Any]:
    """Call OpenAI-compatible chat/completions; measure TTFT via stream when possible."""
    # Use non-stream first for reliability; also try stream for TTFT.
    url = f"http://127.0.0.1:{PORT}/v1/chat/completions"
    # For batch>1: issue sequential requests and aggregate (SGLang continuous batch still warms graphs).
    # Record per-request then aggregate for the cell.
    per = []
    t_cell0 = time.time()
    peak_ttft = None
    all_text = []
    all_ids: list[Any] = []
    errors = []
    for i, prompt in enumerate(prompts):
        body = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "top_p": 1.0,
            "max_tokens": max_new_tokens,
            "stream": True,
        }
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        t0 = time.time()
        ttft = None
        text_parts: list[str] = []
        token_ids: list[int] = []
        finish_reason = None
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
                while True:
                    line = resp.readline()
                    if not line:
                        break
                    if not line.startswith(b"data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == b"[DONE]":
                        break
                    try:
                        chunk = json.loads(payload.decode())
                    except Exception:
                        continue
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    content = delta.get("content")
                    if content:
                        if ttft is None:
                            ttft = time.time() - t0
                        text_parts.append(content)
                    if choices[0].get("finish_reason"):
                        finish_reason = choices[0].get("finish_reason")
            e2e = time.time() - t0
            text = "".join(text_parts)
            phenotype = "PASS"
            if not text:
                phenotype = "EMPTY_OUTPUT"
            per.append(
                {
                    "index": i,
                    "ttft_s": ttft,
                    "e2e_s": e2e,
                    "text": text,
                    "token_ids": token_ids,
                    "finish_reason": finish_reason,
                    "phenotype": phenotype,
                    "response_sha256": sha256_bytes(text.encode()),
                }
            )
            all_text.append(text)
            all_ids.append(token_ids)
            if ttft is not None:
                peak_ttft = ttft if peak_ttft is None else min(peak_ttft, ttft)
        except Exception as exc:
            errors.append(str(exc))
            per.append(
                {
                    "index": i,
                    "phenotype": "TIMEOUT" if "timed out" in str(exc).lower() else "REQUEST_ERROR",
                    "error": str(exc)[:1000],
                }
            )
    wall = time.time() - t_cell0
    # usage via non-stream echo for token counts when stream omitted usage
    usage = {"prompt_tokens": None, "completion_tokens": None}
    try:
        status, parsed, _ = http_json(
            "POST",
            url,
            {
                "model": MODEL,
                "messages": [{"role": "user", "content": prompts[0]}],
                "temperature": 0.0,
                "max_tokens": 1,
                "stream": False,
            },
            timeout=60,
        )
        if status == 200 and isinstance(parsed, dict):
            usage = parsed.get("usage") or usage
    except Exception:
        pass

    phenotypes = [p.get("phenotype") for p in per]
    if any(p == "REQUEST_ERROR" for p in phenotypes):
        cell_ph = "REQUEST_ERROR"
    elif any(p == "TIMEOUT" for p in phenotypes):
        cell_ph = "TIMEOUT"
    elif any(p == "EMPTY_OUTPUT" for p in phenotypes):
        cell_ph = "EMPTY_OUTPUT"
    elif all(p == "PASS" for p in phenotypes):
        cell_ph = "PASS"
    else:
        cell_ph = "UNKNOWN_FAILURE"

    gen_tokens = sum(len(t.split()) for t in all_text)  # approximate if no IDs; runtime notes this
    prompt_tokens_est = usage.get("prompt_tokens")
    return {
        "per_request": [{k: v for k, v in p.items() if k != "text"} for p in per],
        "texts": all_text,
        "token_ids": all_ids,
        "ttft_s": peak_ttft,
        "e2e_wall_s": wall,
        "phenotype": cell_ph,
        "errors": errors,
        "usage_probe": usage,
        "generated_token_count_approx_words": gen_tokens,
        "prompt_tokens_est": prompt_tokens_est,
        "joined_response_sha256": sha256_bytes("\n---\n".join(all_text).encode()),
    }


def main() -> int:
    metrics_path = OUT / "metrics.jsonl"
    failures_path = OUT / "failures.jsonl"
    for p in (metrics_path, failures_path):
        if p.exists():
            p.unlink()

    receipt: dict[str, Any] = {
        "experiment_id": EXPERIMENT_ID,
        "classification": "ENGINEERING_RUNTIME_STRESS_EVAL_ONLY",
        "started_utc": utc_now(),
        "model": MODEL,
        "sglang_version": SGLANG_VERSION,
        "max_gpu_minutes": MAX_GPU_MINUTES,
        "daisy": "NOT_DAISY_T00_T12",
        "hydradb": "NOT_TOUCHED",
    }

    # Install
    if not budget_ok(300):
        receipt["state"] = "TIME_BUDGET_EXHAUSTED"
        write_json(OUT / "receipt.json", receipt)
        return 1
    inst = install_sglang()
    write_json(OUT / "install_receipt.json", inst)
    if not inst.get("ok"):
        receipt["state"] = "FAILED"
        receipt["failure_phenotype"] = "UNKNOWN_FAILURE"
        receipt["install"] = inst
        write_json(OUT / "receipt.json", receipt)
        write_json(OUT / "summary.json", {"state": "FAILED", "reason": "install_failed"})
        return 1

    # Help interrogation
    help_cp = run_cmd([sys.executable, "-m", "sglang.launch_server", "--help"], timeout=120)
    help_text = (help_cp.stdout or "") + "\n" + (help_cp.stderr or "")
    env = collect_environment(help_text)
    flags = env.get("launch_server_help_flags") or {}
    if not flags.get("cuda_graph_backend_prefill") or not flags.get("cuda_graph_backend_decode"):
        receipt["state"] = "UNSUPPORTED_CONFIGURATION"
        receipt["note"] = "Pinned SGLang help missing expected cuda-graph backend flags"
        write_json(OUT / "receipt.json", receipt)
        write_json(OUT / "summary.json", {"state": "UNSUPPORTED_CONFIGURATION", "flags": flags})
        return 1

    # Model support probe is implicit at server start; no silent substitution.
    fixtures, manifest = load_fixtures()
    write_json(OUT / "condition_manifest.json", {"conditions": CONDITIONS, "workload_ids": [r["workload_id"] for r in fixtures]})

    sampler = GpuSampler(OUT / "gpu_telemetry.csv")
    sampler.start()

    cells_completed = 0
    cells_expected = len(fixtures) * len(CONDITIONS)
    condition_states: dict[str, str] = {}
    # Cross-condition outputs for equivalence diagnostic: key workload_id -> {cid: sha/text}
    equiv: dict[str, dict[str, Any]] = {}

    try:
        for cond in CONDITIONS:
            cid = cond["condition_id"]
            out_cond = COND_DIR / cid
            out_cond.mkdir(exist_ok=True)
            if not budget_ok(120):
                condition_states[cid] = "TIME_BUDGET_EXHAUSTED"
                append_jsonl(
                    failures_path,
                    {"condition_id": cid, "phenotype": "TIME_BUDGET_EXHAUSTED", "utc": utc_now()},
                )
                # Mark remaining workloads unfinished
                for row in fixtures:
                    append_jsonl(
                        metrics_path,
                        {
                            "condition_id": cid,
                            "workload_id": row["workload_id"],
                            "phenotype": "TIME_BUDGET_EXHAUSTED",
                            "completed": False,
                        },
                    )
                continue

            srv = ServerHandle(cond, dtype=env.get("dtype_default") or "float16")
            srv.start()
            write_json(
                out_cond / "server_start.json",
                {
                    "state": srv.state,
                    "startup_s": srv.startup_s,
                    "capture_s": srv.capture_s,
                    "error_tail": (srv.error or "")[-1500:],
                },
            )
            if srv.state != "READY":
                condition_states[cid] = srv.state
                append_jsonl(
                    failures_path,
                    {
                        "condition_id": cid,
                        "phenotype": srv.state,
                        "startup_s": srv.startup_s,
                        "utc": utc_now(),
                    },
                )
                for row in fixtures:
                    append_jsonl(
                        metrics_path,
                        {
                            "condition_id": cid,
                            "workload_id": row["workload_id"],
                            "phenotype": srv.state,
                            "completed": False,
                            "server_startup_time_s": srv.startup_s,
                            "cuda_graph_capture_time_s": srv.capture_s,
                        },
                    )
                srv.stop()
                continue

            condition_states[cid] = "RUNNING"
            for row in fixtures:
                if not budget_ok(45):
                    append_jsonl(
                        metrics_path,
                        {
                            "condition_id": cid,
                            "workload_id": row["workload_id"],
                            "phenotype": "TIME_BUDGET_EXHAUSTED",
                            "completed": False,
                        },
                    )
                    append_jsonl(
                        failures_path,
                        {
                            "condition_id": cid,
                            "workload_id": row["workload_id"],
                            "phenotype": "TIME_BUDGET_EXHAUSTED",
                            "utc": utc_now(),
                        },
                    )
                    condition_states[cid] = "TIME_BUDGET_EXHAUSTED"
                    break

                mem_before = nvidia_smi_query().get("memory_used_mib")
                t0 = time.time()
                try:
                    result = stream_completion(row["prompts"], row["max_new_tokens"])
                except Exception as exc:
                    result = {
                        "phenotype": classify_failure(str(exc)),
                        "errors": [str(exc)],
                        "ttft_s": None,
                        "e2e_wall_s": time.time() - t0,
                        "texts": [],
                        "joined_response_sha256": None,
                    }
                mem_after = nvidia_smi_query().get("memory_used_mib")
                if srv.proc and srv.proc.poll() is not None:
                    result["phenotype"] = "SERVER_CRASH"
                    condition_states[cid] = "SERVER_CRASH"

                # Persist raw response (bounded)
                resp_obj = {
                    "condition_id": cid,
                    "workload_id": row["workload_id"],
                    "texts": result.get("texts") or [],
                    "token_ids": result.get("token_ids") or [],
                    "response_sha256": result.get("joined_response_sha256"),
                    "classification": "PROBABILISTIC_MODEL_OUTPUT",
                }
                resp_path = RESP_DIR / f"{cid}_{row['workload_id']}.json"
                write_json(resp_path, resp_obj)

                e2e = result.get("e2e_wall_s") or (time.time() - t0)
                prompt_tok = result.get("prompt_tokens_est")
                # Prefer measured; else estimate from target * batch
                if not prompt_tok:
                    prompt_tok = row["target_prompt_tokens"] * row["batch_size"]
                out_tok = result.get("generated_token_count_approx_words") or 0
                in_tps = (prompt_tok / e2e) if e2e else None
                out_tps = (out_tok / e2e) if e2e else None
                req_tps = (row["batch_size"] / e2e) if e2e else None

                metric = {
                    "condition_id": cid,
                    "prefill_backend": cond["prefill_backend"],
                    "decode_backend": cond["decode_backend"],
                    "workload_id": row["workload_id"],
                    "target_prompt_tokens": row["target_prompt_tokens"],
                    "batch_size": row["batch_size"],
                    "replicate": row["replicate"],
                    "label": "SYNTHETIC_ENGINEERING_FIXTURE",
                    "server_startup_time_s": srv.startup_s,
                    "cuda_graph_capture_time_s": srv.capture_s,
                    "ttft_s": result.get("ttft_s"),
                    "input_tokens_per_s": in_tps,
                    "output_tokens_per_s": out_tps,
                    "request_throughput": req_tps,
                    "e2e_wall_s": e2e,
                    "peak_gpu_memory_mib_sample": sampler.peak_mem_mib,
                    "memory_used_mib_before": mem_before,
                    "memory_used_mib_after": mem_after,
                    "phenotype": result.get("phenotype"),
                    "generated_token_count": out_tok,
                    "prompt_tokens": prompt_tok,
                    "response_sha256": result.get("joined_response_sha256"),
                    "completed": result.get("phenotype") == "PASS",
                    "utc": utc_now(),
                }
                append_jsonl(metrics_path, metric)
                if result.get("phenotype") != "PASS":
                    append_jsonl(
                        failures_path,
                        {
                            "condition_id": cid,
                            "workload_id": row["workload_id"],
                            "phenotype": result.get("phenotype"),
                            "errors": result.get("errors"),
                            "utc": utc_now(),
                        },
                    )
                else:
                    cells_completed += 1

                equiv.setdefault(row["workload_id"], {})[cid] = {
                    "response_sha256": result.get("joined_response_sha256"),
                    "text_norm": "\n".join((result.get("texts") or [])).strip(),
                    "token_ids": result.get("token_ids"),
                }

                if condition_states.get(cid) == "SERVER_CRASH":
                    break

            if condition_states.get(cid) == "RUNNING":
                condition_states[cid] = "COMPLETE"
            srv.stop()
            time.sleep(3)
    finally:
        sampler.stop()

    # Output equivalence diagnostic across conditions for completed workloads
    mismatches = 0
    equiv_rows = []
    for wid, by_c in sorted(equiv.items()):
        shas = {c: v.get("response_sha256") for c, v in by_c.items() if v.get("response_sha256")}
        texts = {c: v.get("text_norm") for c, v in by_c.items()}
        unique_shas = set(shas.values())
        mismatch = len(unique_shas) > 1
        if mismatch:
            mismatches += 1
        equiv_rows.append(
            {
                "workload_id": wid,
                "diagnostic": "OUTPUT_EQUIVALENCE_DIAGNOSTIC",
                "model_output_class": "PROBABILISTIC_MODEL_OUTPUT",
                "sha256_by_condition": shas,
                "mismatch": mismatch,
                "conditions_present": sorted(by_c.keys()),
            }
        )
    write_json(OUT / "output_equivalence_diagnostic.json", {"mismatches": mismatches, "rows": equiv_rows})

    gpu_min = (time.time() - START_TS) / 60.0
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "classification": "DETERMINISTIC_TOOL_OUTPUT_CLOUD_SUMMARY_UNTRUSTED_UNTIL_LOCAL_RECOMPUTE",
        "model": MODEL,
        "sglang_version": SGLANG_VERSION,
        "gpu_name": env.get("GPU_NAME"),
        "dtype": env.get("dtype_default"),
        "condition_states": condition_states,
        "cells_expected": cells_expected,
        "cells_completed_pass": cells_completed,
        "output_equivalence_mismatches": mismatches,
        "gpu_minutes_used_approx": round(gpu_min, 3),
        "peak_gpu_memory_mib": sampler.peak_mem_mib,
        "finished_utc": utc_now(),
    }
    write_json(OUT / "summary.json", summary)
    receipt.update(
        {
            "finished_utc": utc_now(),
            "state": "COMPLETE" if cells_completed == cells_expected else "PARTIAL_OR_FAILED",
            "condition_states": condition_states,
            "cells_expected": cells_expected,
            "cells_completed_pass": cells_completed,
            "gpu_min_used": round(gpu_min, 3),
            "output_equivalence_mismatches": mismatches,
            "artifacts": [
                "environment.json",
                "condition_manifest.json",
                "metrics.jsonl",
                "summary.json",
                "failures.jsonl",
                "responses/",
                "gpu_telemetry.csv",
                "server_logs/",
                "receipt.json",
                "output_equivalence_diagnostic.json",
                "pip_freeze.txt",
            ],
        }
    )
    write_json(OUT / "receipt.json", receipt)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        err = traceback.format_exc()
        try:
            append_jsonl(OUT / "failures.jsonl", {"phenotype": "UNKNOWN_FAILURE", "trace": err[-4000:], "utc": utc_now()})
            write_json(
                OUT / "receipt.json",
                {"state": "FAILED", "failure_phenotype": "UNKNOWN_FAILURE", "trace_tail": err[-2000:], "utc": utc_now()},
            )
        except Exception:
            pass
        print(err, file=sys.stderr)
        raise SystemExit(1)
