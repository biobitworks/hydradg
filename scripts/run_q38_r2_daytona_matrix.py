#!/usr/bin/env python3
"""Execute Q38-EXP008-R2 / Q38-EXP009-R2 matrix on Daytona from frozen manifest."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from daisy_overnight.atoms import (  # noqa: E402
    CONTEXT_CHAR_BUDGET,
    load_admissible_atoms,
    order_atoms_causal,
    order_atoms_neutral,
    render_flat_prose,
    render_ordered_context,
    render_structured_fcg,
    select_atoms,
    structured_retriever_atoms,
)
from daisy_overnight.custody import sha256_bytes  # noqa: E402
from generate_q38_r2_matrix_manifest import (  # noqa: E402
    exp008_context,
    exp009_context,
)
from run_qwen38_model_replay import THINKING_CONFIG, build_prompt  # noqa: E402

MAX_TECH_RETRIES = 2
TECHNICAL_REASONS = {
    "network_interruption",
    "provider_5xx",
    "model_server_crash",
    "verified_infrastructure_timeout",
    "corrupted_output_transfer",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_sandbox_id(repo: Path) -> str:
    p = repo / "eval/qwen38_model_replay_20260828/DAYTONA_SANDBOX_ACTIVE.json"
    if not p.exists():
        raise SystemExit("BLOCKED: DAYTONA_SANDBOX_ACTIVE.json missing — run provision first")
    return json.loads(p.read_text())["sandbox_id"]


def daytona_exec(sandbox: str, cmd: str, timeout: int = 900) -> tuple[int, str, float]:
    start = time.time()
    proc = subprocess.run(
        ["daytona", "exec", sandbox, "--", "bash", "-lc", cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip(), time.time() - start


def rebuild_prompt(
    experiment_id: str,
    case: dict,
    condition: str,
    mode: str,
    atoms_lib: list,
) -> tuple[str, str]:
    if mode == "exp008":
        context, retained, _ = exp008_context(case, condition, atoms_lib)
    else:
        context, retained, _ = exp009_context(case, condition, atoms_lib)
    prompt, proj = build_prompt(case, condition, context, retained, experiment_id)
    return prompt, proj["prompt_sha256"]


def classify_terminal(run_state: str, parser_state: str, identity_ok: bool) -> str:
    if not identity_ok:
        return "MODEL_IDENTITY_FAILURE"
    if run_state.startswith("FAILED:Timeout") or "Timeout" in run_state:
        return "TIMEOUT"
    if run_state != "OK":
        return "TECHNICAL_FAILURE"
    if parser_state == "MALFORMED_JSON":
        return "INVALID_PARSE"
    if parser_state == "PARSED_JSON":
        return "PASS_EXECUTION"
    return "TECHNICAL_FAILURE"


def ollama_generate_remote(sandbox: str, model: str, prompt: str) -> tuple[str, float, str]:
    esc = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    cmd = (
        f'curl -sS http://127.0.0.1:11434/api/generate -d '
        f'\'{{"model":"{model}","prompt":"{esc[:CONTEXT_CHAR_BUDGET]}","stream":false,'
        f'"format":"json","think":false,"options":{{"temperature":0,"num_predict":512}}}}\''
    )
    code, out, latency = daytona_exec(sandbox, cmd, timeout=900)
    if code != 0:
        return json.dumps({"state": "ABSTAIN", "error": out[:500]}), latency, f"FAILED:exit_{code}"
    try:
        payload = json.loads(out)
        return payload.get("response", out), latency, "OK"
    except json.JSONDecodeError:
        return out, latency, "OK"


def get_model_digest(sandbox: str, model: str) -> str | None:
    _, out, _ = daytona_exec(sandbox, f"ollama show {model} --digest 2>/dev/null | tail -1", timeout=60)
    d = out.strip()
    return d if len(d) == 64 else None


def update_progress(exp_dir: Path, manifest: dict, terminal_counts: dict) -> None:
    n_terminal = sum(1 for r in manifest["rows"] if r.get("state") != "PENDING")
    prog = {
        "schema": "hydradg.qwen38.matrix_progress.v1",
        "experiment_id": manifest["experiment_id"],
        "n_planned": manifest["n_planned"],
        "n_terminal": n_terminal,
        "terminal_distribution": terminal_counts,
        "MATRIX_COMPLETE": "YES" if n_terminal >= manifest["n_planned"] else "NO",
        "updated_at_utc": utc_now(),
    }
    (exp_dir / "MATRIX_PROGRESS.json").write_text(json.dumps(prog, indent=2) + "\n", encoding="utf-8")


def execute_matrix(experiment_id: str, mode: str) -> None:
    repo = ROOT
    exp_dir = repo / "eval/qwen38_model_replay_20260828" / experiment_id
    manifest_path = exp_dir / "MATRIX_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    sandbox = load_sandbox_id(repo)
    cases = {
        json.loads(line)["case_id"]: json.loads(line)
        for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
        if line.strip()
    }
    atoms = load_admissible_atoms(repo)
    raw_path = exp_dir / "RAW_OUTPUTS.jsonl"
    ledger_path = exp_dir / "PROMPT_PROJECTION_LEDGER.jsonl"
    terminal_path = exp_dir / "CELL_TERMINAL.jsonl"
    freeze = json.loads((repo / "eval/qwen38_model_replay_20260828/MODEL_IDENTITY_FREEZE.json").read_text())
    digest_map = {
        "qwen3.8:27b": freeze["models"]["QWEN38_27B"]["daytona_digest"],
        "qwen3.8-flash-next:125b-a6b-nvfp4": freeze["models"]["FLASH_NEXT_NVFP4"]["daytona_digest"],
    }
    terminal_counts: dict[str, int] = {}
    for row in manifest["rows"]:
        if row.get("state") != "PENDING":
            terminal_counts[row["state"]] = terminal_counts.get(row["state"], 0) + 1
            continue
        case = cases[row["case_id"]]
        prompt, prompt_hash = rebuild_prompt(experiment_id, case, row["condition"], mode, atoms)
        if prompt_hash != row["prompt_sha256"]:
            row["state"] = "TECHNICAL_FAILURE"
            row["failure_reason"] = "PROMPT_HASH_MISMATCH"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            raise SystemExit(f"PROMPT_HASH_MISMATCH cell={row['cell_id']}")
        model = row["model"]
        expected_digest = digest_map.get(model)
        attempt = 0
        terminal = "PENDING"
        raw = ""
        latency = 0.0
        run_state = "OK"
        parser_state = "MALFORMED_JSON"
        while attempt <= MAX_TECH_RETRIES:
            attempt += 1
            try:
                raw, latency, run_state = ollama_generate_remote(sandbox, model, prompt)
            except subprocess.TimeoutExpired:
                run_state = "FAILED:TimeoutError"
                raw = json.dumps({"state": "ABSTAIN", "error": "timeout"})
            observed_digest = get_model_digest(sandbox, model)
            identity_ok = observed_digest == expected_digest if expected_digest else False
            try:
                json.loads(raw)
                parser_state = "PARSED_JSON"
            except json.JSONDecodeError:
                parser_state = "MALFORMED_JSON"
            terminal = classify_terminal(run_state, parser_state, identity_ok)
            if terminal in {"TIMEOUT", "TECHNICAL_FAILURE"} and attempt <= MAX_TECH_RETRIES:
                continue
            break
        record = {
            "schema": "hydradg.daisy_overnight.raw_output.v1",
            "experiment_id": experiment_id,
            "cell_id": row["cell_id"],
            "case_id": row["case_id"],
            "condition": row["condition"],
            "context_mode": row["context_mode"],
            "model": model,
            "model_digest": observed_digest,
            "replicate": row["replicate"],
            "prompt_sha256": prompt_hash,
            "raw_response_sha256": sha256_bytes(raw.encode("utf-8")),
            "latency_seconds": round(latency, 3),
            "parser_state": parser_state,
            "run_state": run_state,
            "terminal_state": terminal,
            "technical_retry_count": attempt - 1,
            "thinking_configuration": THINKING_CONFIG,
            "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
            "recorded_at_utc": utc_now(),
        }
        with raw_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        with terminal_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"cell_id": row["cell_id"], "terminal_state": terminal}, sort_keys=True) + "\n")
        with ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"cell_id": row["cell_id"], "prompt_sha256": prompt_hash}, sort_keys=True) + "\n")
        row["state"] = terminal
        row["executed_digest"] = observed_digest
        terminal_counts[terminal] = terminal_counts.get(terminal, 0) + 1
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        update_progress(exp_dir, manifest, terminal_counts)
        print(f"{experiment_id} {row['cell_id']} {terminal} {latency:.1f}s")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, choices=["Q38-EXP008-R2", "Q38-EXP009-R2"])
    args = parser.parse_args()
    mode = "exp008" if "008" in args.experiment else "exp009"
    execute_matrix(args.experiment, mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
