#!/usr/bin/env python3
"""Run IC failure-learning Ollama experiments for M0/M1/M2 generations."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SKILL_CONDENSED = """You are a probabilistic experimental actor. Return strict JSON only.
Blind lanes (E01-E04,E07): do NOT use postmortem/EVAL_ONLY evidence.
Never invent unavailable endpoints; list them in invented_capabilities.
Do not output estimated judge scores."""

OUTPUT_SCHEMA = """Return exactly one JSON object:
{
  "state": "OK|ABSTAIN|MALFORMED_INPUT|BLOCKED_LABEL_LEAKAGE",
  "experiment_family": "E01|E02|E03|E04|E05|E06|E07",
  "condition": "string",
  "observations": ["string"],
  "predicted_weak_dimensions": ["string"],
  "origin_classification": "DISTINCT_HACKATHON_DELTA|PREEXISTING_PROJECT|AMBIGUOUS|NOT_APPLICABLE",
  "missing_evidence_classes": ["string"],
  "causal_ranking": ["A", "B", "C"],
  "earliest_divergence_candidate": "A|B|C|D|E|F|G|NOT_APPLICABLE|UNKNOWN",
  "first_three_machine_actions": ["string"],
  "ordered_workflow": ["string"],
  "recommended_first_correction": "string|null",
  "confidence_0_1": 0.0,
  "evidence_quotes": ["string"],
  "invented_capabilities": []
}"""

M0_FAMILIES = {"E01", "E02", "E03", "E04", "E07"}
M2_EXTRA = {"E05", "E06"}

PREREGISTERED_TAGS = [
    "qwen2.5:1.5b",
    "qwen3:1.7b",
    "llama3.2:3b",
    "granite4.1:3b",
    "qwen2.5:7b",
    "qwen2.5-coder:7b",
    "deepseek-r1:14b",
    "phi4-reasoning:14b",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ollama_generate(model: str, prompt: str, temperature: float = 0.0, timeout: int = 300) -> tuple[str, float]:
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "num_predict": 512},
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    latency = time.time() - start
    return payload.get("response", ""), latency


def model_identity(model: str) -> str:
    try:
        out = subprocess.check_output(["ollama", "show", model, "--modelfile"], text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            if line.startswith("FROM "):
                return line.strip()
        return out.splitlines()[0] if out else model
    except (subprocess.CalledProcessError, FileNotFoundError):
        return model


def admitted_models() -> list[str]:
    try:
        out = subprocess.check_output(["ollama", "list"], text=True)
        present = {line.split()[0] for line in out.splitlines()[1:] if line.strip()}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [tag for tag in PREREGISTERED_TAGS if tag in present]


def load_context(repo: Path, generation: str) -> str:
    parts: list[str] = []
    if generation in {"M1", "M2"}:
        rubric = json.loads((repo / "eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json").read_text())
        track = rubric["official_rubric"]["tracks"]["track01_external"]
        parts.append("IC RUBRIC SUMMARY: " + json.dumps(track["criteria"], ensure_ascii=False))
        parts.append("SUBMISSION FIELDS: title, blurb, repo_url, demo_url, agent_surface, folder_id")
        parts.append("GATE: folder_id must be populated before submit; vault required for media evidence")
    if generation == "M2":
        poison_path = repo / "eval/ic_failure_learning_20260827/README_POISON_FCO.json"
        if poison_path.exists():
            p = json.loads(poison_path.read_text())
            parts.append(
                f"KNOWN FAILURE: README presents {p['presents_project_as']}; "
                f"conflicts with {p['conflicts_with']}; Anticube={p['anticube_classification']}"
            )
        parts.append(
            "REPAIR: populate vault before submit; expose origin delta; branch-qualified repo URL"
        )
    return "\n".join(parts)


def build_prompt(repo: Path, case: dict[str, Any], generation: str) -> tuple[str, str]:
    context = load_context(repo, generation)
    case_input = case.get("input", {})
    if isinstance(case_input, dict) and "readme_poison_fixture" in case_input:
        case_input = case_input.get("readme_poison_fixture", case_input)
    case_json = json.dumps(case_input, ensure_ascii=False, indent=2)
    prompt = (
        f"{SKILL_CONDENSED}\n\n"
        f"GENERATION={generation} MODEL_WEIGHT_STATE=UNCHANGED\n"
        f"{context}\n\n"
        f"FAMILY={case['experiment_family']} CONDITION={case['condition']}\n"
        f"TASK: {case['task']}\n\n"
        f"INPUT:\n{case_json}\n\n"
        f"{OUTPUT_SCHEMA}\n"
    )
    return prompt, sha256_bytes(prompt.encode("utf-8"))


def families_for_generation(generation: str) -> set[str]:
    if generation == "M2":
        return M0_FAMILIES | M2_EXTRA
    return M0_FAMILIES


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--generation", choices=["M0", "M1", "M2"], required=True)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--cases", default="eval/ic_failure_learning_20260827/cases/CASES.jsonl")
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/results/MODEL_OUTPUTS.jsonl")
    ap.add_argument("--replicates", type=int, default=1)
    ap.add_argument("--case-ids", nargs="*", default=None, help="Optional subset for canary")
    ap.add_argument("--cloudflare-os-commit", default="DIRECT_OLLAMA_FALLBACK")
    ap.add_argument("--ollama-version", default="")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    cases_path = repo / args.cases
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    allowed = families_for_generation(args.generation)
    cases = [c for c in cases if c["experiment_family"] in allowed]
    if args.case_ids:
        wanted = set(args.case_ids)
        cases = [c for c in cases if c["case_id"] in wanted]

    models = args.models or admitted_models()
    if not models:
        raise SystemExit("STOP: no admitted models available locally")

    ollama_ver = args.ollama_version
    if not ollama_ver:
        try:
            ollama_ver = subprocess.check_output(["ollama", "--version"], text=True).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            ollama_ver = "unknown"

    out_path = repo / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing_keys = set()
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            existing_keys.add((row.get("model"), row.get("case_id"), row.get("replicate"), row.get("generation")))

    prompts_dir = repo / "eval/ic_failure_learning_20260827/prompts" / args.generation
    prompts_dir.mkdir(parents=True, exist_ok=True)
    run_log: list[dict[str, Any]] = []

    for model in models:
        mid = model_identity(model)
        for case in cases:
            for replicate in range(1, args.replicates + 1):
                key = (model, case["case_id"], replicate, args.generation)
                if key in existing_keys:
                    continue
                prompt, prompt_sha = build_prompt(repo, case, args.generation)
                prompt_file = prompts_dir / f"{case['case_id']}_{model.replace(':', '_')}_r{replicate}.txt"
                prompt_file.write_text(prompt, encoding="utf-8")
                state = "OK"
                raw = ""
                latency = 0.0
                try:
                    raw, latency = ollama_generate(model, prompt)
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                    try:
                        time.sleep(2)
                        raw, latency = ollama_generate(model, prompt, timeout=600)
                    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc2:
                        state = f"FAILED:{type(exc2).__name__}"
                        raw = json.dumps({"state": "ABSTAIN", "error": str(exc2)})

                raw_bytes = raw.encode("utf-8")
                raw_sha = sha256_bytes(raw_bytes)
                try:
                    parsed = json.loads(raw)
                    parser_state = "PARSED_JSON"
                except json.JSONDecodeError:
                    parsed = None
                    parser_state = "MALFORMED_JSON"

                row = {
                    "schema": "hydradg.ic_failure_learning.model_output.v1",
                    "generation": args.generation,
                    "model": model,
                    "model_identity": mid,
                    "case_id": case["case_id"],
                    "experiment_family": case["experiment_family"],
                    "condition": case["condition"],
                    "replicate": replicate,
                    "prompt_sha256": prompt_sha,
                    "cloudflare_os_commit": args.cloudflare_os_commit,
                    "ollama_version": ollama_ver,
                    "raw_response_sha256": raw_sha,
                    "raw_response_bytes": len(raw_bytes),
                    "latency_seconds": round(latency, 3),
                    "parser_state": parser_state,
                    "parsed": parsed,
                    "run_state": state,
                    "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
                    "model_weight_state": "UNCHANGED",
                    "signature_state": "NOT_SIGNED",
                    "merkle_mmr_state": "NOT_COMMITTED_AT_MODEL_OUTPUT_STAGE",
                }
                with out_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
                run_log.append({
                    "model": model,
                    "case_id": case["case_id"],
                    "replicate": replicate,
                    "parser_state": parser_state,
                    "latency": latency,
                })
                print(f"{args.generation} {model} {case['case_id']} r{replicate} {parser_state}")

    log_path = repo / "eval/ic_failure_learning_20260827/results" / f"RUN_LOG_{args.generation}.json"
    log_path.write_text(json.dumps(run_log, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"generation": args.generation, "runs": len(run_log)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
