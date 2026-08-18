#!/usr/bin/env python3
"""
HydraDG Vithia overnight Daisy Train for magicstudiobox.

Execution boundary:
- Vithia/Pythia training is executed by the existing
  scripts/vithia_divergence_core.py PyTorch harness.
- Ollarma is used as the local governed model-supervision surface after each run.
- Model annotations are non-load-bearing LOCAL_MODEL_HYPOTHESIS objects and never
  control whether scientific results are admitted.
- The queue order is deterministic and predeclared.
- No Xeno training is attempted because the current evidence package does not
  establish the original Xeno training kernel as available.

Outputs are append-only under:
  eval/vithia_overnight/<run_family>/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_PACKAGE = Path("/Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7")
OLLARMA_CLIENT_DIRS = [
    Path("/Users/byron/projects/active/ollarma/clients"),
    Path("/Users/byron/projects/ollarma/clients"),
]
DEFAULT_RUN_FAMILY = "VITHIA-OVERNIGHT-01"
TZ = ZoneInfo("America/Los_Angeles")

MODEL_PREFERENCE = [
    "qwen3:1.7b",
    "qwen2.5:1.5b",
    "granite4.1:8b",
]

QUEUE = [
    {"run_id": "control_s314159_r1", "seed": 314159, "threads": 1, "perturb_step": -1, "perturb_token_delta": 0},
    {"run_id": "control_s314159_r2", "seed": 314159, "threads": 1, "perturb_step": -1, "perturb_token_delta": 0},
    {"run_id": "control_s314159_r3", "seed": 314159, "threads": 1, "perturb_step": -1, "perturb_token_delta": 0},
    {"run_id": "thread4_s314159",    "seed": 314159, "threads": 4, "perturb_step": -1, "perturb_token_delta": 0},
    {"run_id": "perturb_early_s314159", "seed": 314159, "threads": 1, "perturb_step": 2,  "perturb_token_delta": 1},
    {"run_id": "perturb_mid_s314159",   "seed": 314159, "threads": 1, "perturb_step": 8,  "perturb_token_delta": 1},
    {"run_id": "perturb_late_s314159",  "seed": 314159, "threads": 1, "perturb_step": 18, "perturb_token_delta": 1},
    {"run_id": "control_s271828",       "seed": 271828, "threads": 1, "perturb_step": -1, "perturb_token_delta": 0},
    {"run_id": "perturb_mid_s271828",   "seed": 271828, "threads": 1, "perturb_step": 8,  "perturb_token_delta": 1},
    {"run_id": "control_s161803",       "seed": 161803, "threads": 1, "perturb_step": -1, "perturb_token_delta": 0},
    {"run_id": "perturb_mid_s161803",   "seed": 161803, "threads": 1, "perturb_step": 8,  "perturb_token_delta": 1},
]


def utc_now() -> str:
    return datetime.now(tz=ZoneInfo("UTC")).isoformat()


def local_now() -> datetime:
    return datetime.now(tz=TZ)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_sha256(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def status_bar(done: int, total: int, stage: str, run_id: str = "", elapsed_s: float = 0.0) -> str:
    total = max(total, 1)
    frac = min(max(done / total, 0.0), 1.0)
    width = 24
    filled = int(width * frac)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {frac*100:6.2f}% stage={stage} run={run_id or '-'} elapsed={elapsed_s:0.0f}s"


def resolve_cutoff(cutoff_hhmm: str) -> datetime:
    hh, mm = [int(x) for x in cutoff_hhmm.split(":", 1)]
    now = local_now()
    cutoff = datetime.combine(now.date(), dtime(hh, mm), tzinfo=TZ)
    if cutoff <= now:
        cutoff += timedelta(days=1)
    return cutoff


def select_python(package_root: Path) -> str:
    candidates = [
        package_root / ".venv-hydradg/bin/python",
        Path("/Users/byron/fco-venv/bin/python3"),
        Path(sys.executable),
        Path(shutil.which("python3") or ""),
    ]
    seen = set()
    for p in candidates:
        s = str(p)
        if not s or s in seen or not p.exists():
            continue
        seen.add(s)
        probe = subprocess.run(
            [s, "-c", "import torch, transformers, numpy; print(torch.__version__, transformers.__version__, numpy.__version__)"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if probe.returncode == 0:
            return s
    raise RuntimeError("No Python interpreter with torch + transformers + numpy was found.")


class _EmbeddedOllarmaClient:
    """Zero-dependency fallback using the same localhost surfaces as ollarma_client.py."""
    OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    OLLARMA_URL = os.environ.get("OLLARMA_URL", "http://127.0.0.1:8484").rstrip("/")

    @staticmethod
    def _request(method: str, url: str, payload: dict | None = None, timeout: float = 120.0) -> dict:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if data else {}
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            # Ollarma can expose a degraded state with a non-2xx status while
            # still returning a valid JSON health body. Preserve that body.
            raw = exc.read().decode("utf-8", "replace") if exc.fp else ""
            try:
                return json.loads(raw)
            except Exception as parse_exc:
                raise RuntimeError(f"{method} {url} -> HTTP {exc.code}: {raw[:200]}") from parse_exc
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            raise RuntimeError(f"{method} {url} unreachable: {exc}") from exc
        try:
            return json.loads(raw)
        except Exception as exc:
            raise RuntimeError(f"{method} {url} -> non-JSON response: {raw[:200]}") from exc

    @classmethod
    def health(cls) -> dict:
        out = {"ollama": False, "ollarma": False, "detail": {}, "client_source": "embedded_http"}
        try:
            tags = cls._request("GET", f"{cls.OLLAMA_URL}/api/tags", timeout=5)
            out["ollama"] = True
            out["detail"]["ollama_models"] = sorted(
                m.get("name", "") for m in tags.get("models", []) if m.get("name")
            )
        except Exception as exc:
            out["detail"]["ollama"] = str(exc)[:200]
        try:
            h = cls._request("GET", f"{cls.OLLARMA_URL}/health", timeout=5)
            out["ollarma"] = True
            out["detail"]["ollarma"] = h
        except Exception as exc:
            out["detail"]["ollarma"] = str(exc)[:200]
        return out

    @classmethod
    def list_models(cls) -> list[str]:
        out = cls._request("GET", f"{cls.OLLAMA_URL}/api/tags", timeout=10)
        return sorted(m.get("name", "") for m in out.get("models", []) if m.get("name"))

    @classmethod
    def chat_full(cls, prompt: str, model: str | None = None, timeout: float = 180.0) -> dict:
        payload = {"message": prompt}
        if model:
            payload["model"] = model
        return cls._request("POST", f"{cls.OLLARMA_URL}/chat", payload, timeout=timeout)


def load_ollarma():
    """Prefer the installed Ollarma zero-dependency client; fall back to direct localhost HTTP."""
    for client_dir in OLLARMA_CLIENT_DIRS:
        client_file = client_dir / "ollarma_client.py"
        if not client_file.is_file():
            continue
        sys.path.insert(0, str(client_dir))
        try:
            import ollarma_client as oc  # type: ignore
            setattr(oc, "CLIENT_SOURCE", str(client_file))
            return oc
        except Exception:
            # Fall through to the embedded localhost client; the failure is
            # disclosed in the preflight client_source.
            pass
    _EmbeddedOllarmaClient.CLIENT_SOURCE = "embedded_http"
    return _EmbeddedOllarmaClient


def select_local_model(oc, requested: str | None) -> tuple[str, list[str]]:
    health = oc.health()
    if not health.get("ollarma"):
        raise RuntimeError(f"Ollarma health check failed: {health}")
    if not health.get("ollama"):
        raise RuntimeError(f"Ollama health check failed: {health}")
    models = oc.list_models()
    if requested:
        if requested not in models:
            raise RuntimeError(f"Requested local model {requested!r} is not installed. Installed={models}")
        return requested, models
    for model in MODEL_PREFERENCE:
        if model in models:
            return model, models
    raise RuntimeError(
        "No preferred local model is installed. "
        f"Expected one of {MODEL_PREFERENCE}; installed={models}. "
        "This runner does not pull models automatically."
    )


def completed_run_ids(results_jsonl: Path) -> set[str]:
    done: set[str] = set()
    if not results_jsonl.exists():
        return done
    for line in results_jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("status") == "COMPLETE" and row.get("run_id"):
            done.add(row["run_id"])
    return done


def append_jsonl(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def run_annotation(oc, model: str, run_summary: dict, run_dir: Path) -> dict:
    prompt_obj = {
        "task": "Bounded post-run review of one HydraDG Vithia execution receipt.",
        "rules": [
            "Return concise JSON only if possible.",
            "Do not claim verification, reproducibility, causality, signing, or Merkle commitment.",
            "Treat this as a local-model hypothesis/annotation, not scientific evidence.",
            "Flag obvious anomalies in the supplied run summary only.",
            "Do not propose changing or deleting frozen artifacts.",
        ],
        "run_summary": run_summary,
    }
    prompt = json.dumps(prompt_obj, sort_keys=True, separators=(",", ":"))
    request = {
        "requested_model": model,
        "prompt_sha256": sha256_text(prompt),
        "created_utc": utc_now(),
    }
    try:
        full = oc.chat_full(prompt, model=model, timeout=180.0)
        turn = {
            "schema": "hydradg.ollarma_local_annotation.v1",
            "trust_tier": "LOCAL_MODEL_HYPOTHESIS",
            "request": request,
            "response": full,
            "status": "COMPLETE",
        }
    except Exception as exc:
        turn = {
            "schema": "hydradg.ollarma_local_annotation.v1",
            "trust_tier": "LOCAL_MODEL_HYPOTHESIS",
            "request": request,
            "response": None,
            "status": "FAILED",
            "error": repr(exc),
        }
    turn["object_sha256"] = canonical_sha256({k: v for k, v in turn.items() if k != "object_sha256"})
    atomic_json(run_dir / "ollarma_annotation.json", turn)
    return turn


def write_status(status_path: Path, *, stage: str, current_run: str | None, completed: int,
                 failed: int, total: int, started_utc: str, cutoff: datetime, extra: dict | None = None) -> None:
    obj = {
        "schema": "hydradg.vithia_overnight_status.v1",
        "status": stage,
        "current_run": current_run,
        "completed_runs": completed,
        "failed_runs": failed,
        "total_runs": total,
        "started_utc": started_utc,
        "updated_utc": utc_now(),
        "cutoff_local": cutoff.isoformat(),
        "pid": os.getpid(),
    }
    if extra:
        obj.update(extra)
    atomic_json(status_path, obj)


def first_state_divergence(base: dict, other: dict) -> int | None:
    a = base.get("records", [])
    b = other.get("records", [])
    for ra, rb in zip(a, b):
        if ra.get("state_hash") != rb.get("state_hash"):
            return int(ra.get("step", -1))
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def safe_load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def finalize(run_root: Path, queue_rows: list[dict]) -> None:
    receipt_by_id: dict[str, dict] = {}
    for row in queue_rows:
        rp = row.get("receipt_path")
        if row.get("status") == "COMPLETE" and rp and Path(rp).exists():
            receipt_by_id[row["run_id"]] = safe_load_json(Path(rp))

    comparisons = []

    def compare(base_id: str, other_id: str, comparison_type: str):
        if base_id not in receipt_by_id or other_id not in receipt_by_id:
            return
        base = receipt_by_id[base_id]
        other = receipt_by_id[other_id]
        first = first_state_divergence(base, other)
        comparisons.append({
            "baseline_run_id": base_id,
            "comparison_run_id": other_id,
            "comparison_type": comparison_type,
            "final_state_exact": base.get("final_state_hash") == other.get("final_state_hash"),
            "first_state_divergence_step": first,
            "classification": "STATE_EXACT" if first is None else f"DIVERGED_AT_STEP_{first}",
        })

    compare("control_s314159_r1", "control_s314159_r2", "same_seed_same_threads_replica")
    compare("control_s314159_r1", "control_s314159_r3", "same_seed_same_threads_replica")
    compare("control_s314159_r1", "thread4_s314159", "thread_count_perturbation")
    compare("control_s314159_r1", "perturb_early_s314159", "token_perturbation")
    compare("control_s314159_r1", "perturb_mid_s314159", "token_perturbation")
    compare("control_s314159_r1", "perturb_late_s314159", "token_perturbation")
    compare("control_s271828", "perturb_mid_s271828", "token_perturbation")
    compare("control_s161803", "perturb_mid_s161803", "token_perturbation")

    atomic_json(run_root / "vithia_first_divergence_table.json", {
        "schema": "hydradg.vithia_first_divergence_table.v1",
        "comparisons": comparisons,
        "claim_boundary": (
            "Bounded local Vithia/Pythia fixture only. "
            "No causal hardware claim, historical-corpus reproduction claim, or global determinism claim."
        ),
    })

    matrix = {
        "schema": "hydradg.vithia_overnight_matrix.v1",
        "run_family": run_root.name,
        "queue_results": queue_rows,
        "comparisons": comparisons,
        "claim_boundary": (
            "Executed local training fixture and derived comparisons only. "
            "Ollarma annotations are LOCAL_MODEL_HYPOTHESIS and non-load-bearing."
        ),
    }
    atomic_json(run_root / "vithia_overnight_matrix.json", matrix)

    evidence = []
    for p in sorted(run_root.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix == ".pt":
            continue
        try:
            evidence.append({
                "path": str(p),
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            })
        except OSError:
            pass
    atomic_json(run_root / "EVIDENCE_INDEX.json", {
        "schema": "hydradg.evidence_index.v1",
        "artifacts": evidence,
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
    })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package-root", default=str(DEFAULT_PACKAGE))
    ap.add_argument("--run-family", default=DEFAULT_RUN_FAMILY)
    ap.add_argument("--cutoff-local", default="08:00")
    ap.add_argument("--model", default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    package_root = Path(args.package_root).resolve()
    core = package_root / "scripts/vithia_divergence_core.py"
    if not package_root.is_dir():
        raise SystemExit(f"PACKAGE_MISSING: {package_root}")
    if not core.is_file():
        raise SystemExit(f"VITHIA_CORE_MISSING: {core}")

    run_root = package_root / "eval/vithia_overnight" / args.run_family
    runs_dir = run_root / "runs"
    logs_dir = run_root / "logs"
    handoff_dir = package_root / "handoff"
    status_path = run_root / "status.json"
    results_jsonl = run_root / "queue_results.jsonl"

    run_root.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    handoff_dir.mkdir(parents=True, exist_ok=True)

    if results_jsonl.exists() and not args.resume:
        raise SystemExit(
            f"RUN_FAMILY_ALREADY_EXISTS: {run_root}. "
            "Use --resume to continue without overwriting completed runs."
        )

    started_utc = utc_now()
    cutoff = resolve_cutoff(args.cutoff_local)

    try:
        py = select_python(package_root)
        oc = load_ollarma()
        model, installed_models = select_local_model(oc, args.model)
    except Exception as exc:
        err = {
            "schema": "hydradg.overnight_preflight_failure.v1",
            "timestamp_utc": utc_now(),
            "error": repr(exc),
            "traceback": traceback.format_exc(),
        }
        atomic_json(run_root / "preflight_failure.json", err)
        atomic_text(handoff_dir / "LAST_ERROR_FOR_CHAT.txt", json.dumps(err, indent=2) + "\n")
        print(f"PRECHECK_FAILED: {exc}", file=sys.stderr)
        return 2

    preflight = {
        "schema": "hydradg.vithia_overnight_preflight.v1",
        "run_family": args.run_family,
        "package_root": str(package_root),
        "core_path": str(core),
        "core_sha256": sha256_file(core),
        "python": py,
        "host": platform.node(),
        "platform": platform.platform(),
        "ollarma_client_source": getattr(oc, "CLIENT_SOURCE", getattr(oc, "__file__", "embedded_http")),
        "ollarma_url": getattr(oc, "OLLARMA_URL", "UNRESOLVED"),
        "ollama_url": getattr(oc, "OLLAMA_URL", "UNRESOLVED"),
        "selected_local_model": model,
        "installed_models": installed_models,
        "queue": QUEUE,
        "cutoff_local": cutoff.isoformat(),
        "started_utc": started_utc,
        "claim_boundary": (
            "Preflight/queue declaration only. Local model supervises annotations; "
            "training is performed by the frozen Vithia PyTorch fixture."
        ),
    }
    preflight["object_sha256"] = canonical_sha256({k: v for k, v in preflight.items() if k != "object_sha256"})
    atomic_json(run_root / "preflight.json", preflight)

    already_done = completed_run_ids(results_jsonl)
    completed = len(already_done)
    failed = 0
    total = len(QUEUE)

    print(status_bar(completed, total, "PREFLIGHT_PASS", elapsed_s=0))
    print(f"selected_local_model={model}")
    print(f"python={py}")
    print(f"cutoff_local={cutoff.isoformat()}")
    sys.stdout.flush()

    if args.dry_run:
        write_status(
            status_path, stage="DRY_RUN_COMPLETE", current_run=None, completed=completed,
            failed=failed, total=total, started_utc=started_utc, cutoff=cutoff,
            extra={"selected_local_model": model}
        )
        return 0

    queue_rows = []
    if results_jsonl.exists():
        for line in results_jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    queue_rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    for idx, spec in enumerate(QUEUE, start=1):
        run_id = spec["run_id"]
        if run_id in already_done:
            print(status_bar(completed, total, "SKIP_COMPLETE", run_id))
            continue

        if local_now() >= cutoff:
            write_status(
                status_path, stage="CUTOFF_REACHED", current_run=None, completed=completed,
                failed=failed, total=total, started_utc=started_utc, cutoff=cutoff,
                extra={"selected_local_model": model}
            )
            print(status_bar(completed, total, "CUTOFF_REACHED"))
            break

        run_dir = run_root / "per_run" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = run_dir / "stdout.log"
        stderr_path = run_dir / "stderr.log"
        receipt_path = runs_dir / f"{run_id}.receipt.json"
        checkpoint_path = runs_dir / f"{run_id}.pt"

        cmd = [
            py, str(core),
            "--run-id", run_id,
            "--outdir", str(runs_dir),
            "--seed", str(spec["seed"]),
            "--steps", "24",
            "--batch", "2",
            "--seq", "128",
            "--lr", "0.0003",
        ]
        if spec["perturb_step"] >= 0:
            cmd += ["--perturb-step", str(spec["perturb_step"])]
        if spec["perturb_token_delta"]:
            cmd += ["--perturb-token-delta", str(spec["perturb_token_delta"])]

        env = os.environ.copy()
        env.update({
            "OMP_NUM_THREADS": str(spec["threads"]),
            "MKL_NUM_THREADS": str(spec["threads"]),
            "PYTHONHASHSEED": str(spec["seed"]),
            "TOKENIZERS_PARALLELISM": "false",
        })

        manifest = {
            "schema": "hydradg.vithia_local_run_manifest.v1",
            "run_family": args.run_family,
            "run_id": run_id,
            "queue_index": idx,
            "queue_total": total,
            "command": cmd,
            "cwd": str(package_root),
            "declared_env": {
                "OMP_NUM_THREADS": env["OMP_NUM_THREADS"],
                "MKL_NUM_THREADS": env["MKL_NUM_THREADS"],
                "PYTHONHASHSEED": env["PYTHONHASHSEED"],
                "TOKENIZERS_PARALLELISM": env["TOKENIZERS_PARALLELISM"],
            },
            "core_sha256": preflight["core_sha256"],
            "selected_local_model": model,
            "started_utc": utc_now(),
            "perturbation": {
                "perturb_step": spec["perturb_step"],
                "perturb_token_delta": spec["perturb_token_delta"],
            },
        }
        manifest["object_sha256"] = canonical_sha256({k: v for k, v in manifest.items() if k != "object_sha256"})
        atomic_json(run_dir / "run_manifest.json", manifest)

        write_status(
            status_path, stage="RUNNING", current_run=run_id, completed=completed,
            failed=failed, total=total, started_utc=started_utc, cutoff=cutoff,
            extra={"selected_local_model": model, "queue_index": idx}
        )

        t0 = time.time()
        with stdout_path.open("w", encoding="utf-8") as so, stderr_path.open("w", encoding="utf-8") as se:
            proc = subprocess.Popen(cmd, cwd=package_root, env=env, stdout=so, stderr=se, text=True)
            while proc.poll() is None:
                elapsed = time.time() - t0
                print("\r" + status_bar(completed, total, "TRAINING", run_id, elapsed), end="", flush=True)
                write_status(
                    status_path, stage="RUNNING", current_run=run_id, completed=completed,
                    failed=failed, total=total, started_utc=started_utc, cutoff=cutoff,
                    extra={
                        "selected_local_model": model,
                        "queue_index": idx,
                        "child_pid": proc.pid,
                        "elapsed_s": round(elapsed, 3),
                    }
                )
                time.sleep(10)
            rc = proc.returncode
        elapsed = time.time() - t0
        print()

        row = {
            "schema": "hydradg.vithia_queue_result.v1",
            "run_id": run_id,
            "queue_index": idx,
            "returncode": rc,
            "wall_s": round(elapsed, 3),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "stdout_sha256": sha256_file(stdout_path),
            "stderr_sha256": sha256_file(stderr_path),
            "finished_utc": utc_now(),
            "status": "FAILED",
        }

        if rc == 0 and receipt_path.exists():
            row.update({
                "status": "COMPLETE",
                "receipt_path": str(receipt_path),
                "receipt_sha256": sha256_file(receipt_path),
                "checkpoint_path": str(checkpoint_path) if checkpoint_path.exists() else None,
                "checkpoint_sha256": sha256_file(checkpoint_path) if checkpoint_path.exists() else None,
            })
            receipt = safe_load_json(receipt_path)
            run_summary = {
                "run_id": run_id,
                "seed": receipt.get("seed"),
                "threads": spec["threads"],
                "perturb_step": receipt.get("perturb_step"),
                "perturb_token_delta": receipt.get("perturb_token_delta"),
                "final_state_hash": receipt.get("final_state_hash"),
                "checkpoint_file_sha256": receipt.get("checkpoint_file_sha256"),
                "environment": receipt.get("environment"),
                "wall_s": row["wall_s"],
            }
            annotation = run_annotation(oc, model, run_summary, run_dir)
            row["ollarma_annotation_path"] = str(run_dir / "ollarma_annotation.json")
            row["ollarma_annotation_sha256"] = sha256_file(run_dir / "ollarma_annotation.json")
            row["ollarma_annotation_status"] = annotation["status"]
            completed += 1
            already_done.add(run_id)
            append_jsonl(results_jsonl, row)
            queue_rows.append(row)
            print(status_bar(completed, total, "RUN_COMPLETE", run_id, elapsed))
            continue

        failed += 1
        if rc == 0 and not receipt_path.exists():
            row["failure_reason"] = "RETURN_CODE_0_BUT_RECEIPT_MISSING"
        else:
            row["failure_reason"] = f"NONZERO_RETURN_CODE_{rc}"
        append_jsonl(results_jsonl, row)
        queue_rows.append(row)

        error_packet = {
            "schema": "hydradg.vithia_overnight_failure.v1",
            "run_family": args.run_family,
            "failed_run": row,
            "next_action": "Inspect preserved stdout/stderr and repair explicitly before --resume.",
            "timestamp_utc": utc_now(),
        }
        atomic_json(run_root / "failure.json", error_packet)
        atomic_text(handoff_dir / "LAST_ERROR_FOR_CHAT.txt", json.dumps(error_packet, indent=2) + "\n")
        write_status(
            status_path, stage="FAILED", current_run=run_id, completed=completed,
            failed=failed, total=total, started_utc=started_utc, cutoff=cutoff,
            extra={"selected_local_model": model, "failure_reason": row["failure_reason"]}
        )
        print(status_bar(completed, total, "FAILED", run_id, elapsed))
        finalize(run_root, queue_rows)
        return 1

    finalize(run_root, queue_rows)

    final_state = "COMPLETE" if completed == total else "PARTIAL_CUTOFF"
    write_status(
        status_path, stage=final_state, current_run=None, completed=completed,
        failed=failed, total=total, started_utc=started_utc, cutoff=cutoff,
        extra={"selected_local_model": model}
    )

    matrix_path = run_root / "vithia_overnight_matrix.json"
    matrix_sha = sha256_file(matrix_path) if matrix_path.exists() else "MISSING"
    evidence_path = run_root / "EVIDENCE_INDEX.json"
    evidence_sha = sha256_file(evidence_path) if evidence_path.exists() else "MISSING"

    status_md = f"""# HydraDG overnight Daisy status

Run family: `{args.run_family}`
Status: `{final_state}`
Completed: `{completed}/{total}`
Failed: `{failed}`
Selected local model via Ollarma: `{model}`
Matrix SHA-256: `{matrix_sha}`
Evidence index SHA-256: `{evidence_sha}`

Claim boundary:
- local Vithia/Pythia fixture execution only;
- Ollarma annotations are LOCAL_MODEL_HYPOTHESIS;
- no signing operation performed;
- no Merkle/MMR commitment performed;
- no historical Xeno training reproduction attempted.
"""
    atomic_text(handoff_dir / "LAST_STATUS.md", status_md)
    atomic_text(
        handoff_dir / "NEXT_COMMAND.txt",
        f"python3 {Path(__file__).resolve()} --package-root {package_root} "
        f"--run-family {args.run_family} --resume\n"
    )
    atomic_json(handoff_dir / "BACKEND_MATRIX.json", {
        "schema": "hydradg.backend_matrix.v1",
        "magicstudiobox_vithia": {
            "status": final_state,
            "completed": completed,
            "total": total,
            "selected_local_model": model,
            "matrix_path": str(matrix_path),
            "matrix_sha256": matrix_sha,
        }
    })
    if evidence_path.exists():
        shutil.copy2(evidence_path, handoff_dir / "EVIDENCE_INDEX.json")

    print(status_bar(completed, total, final_state))
    print(f"matrix={matrix_path}")
    print(f"matrix_sha256={matrix_sha}")
    print(f"evidence_index={evidence_path}")
    print(f"evidence_index_sha256={evidence_sha}")
    print("signature_state=NOT_SIGNED")
    print("merkle_state=NOT_MERKLE_COMMITTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
