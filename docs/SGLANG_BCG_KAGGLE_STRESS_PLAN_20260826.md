# SGLang Breakable CUDA Graph — Kaggle GPU Runtime Stress Plan

**EXPERIMENT_ID:** `SGLANG-BCG-KAGGLE-20260826`  
**WORK_UNIT_ID:** `HYDRADG_SGLANG_KAGGLE_BCG_STRESS_20260826`  
**Date:** 2026-08-26  
**Classification:** `ENGINEERING_RUNTIME_STRESS_EVAL_ONLY` / `SUCCESSOR_EXPERIMENT` / `PROVISIONAL_UNTIL_LOCAL_VERIFICATION`

## Purpose

Gain GPU runtime evidence about SGLang CUDA-graph backends for prefill/decode, specifically whether **breakable** prefill CUDA graph alters efficiency or failure behavior vs **disabled** and **tc_piecewise**, under one frozen model/workload on one Kaggle GPU.

This is **not** Daisy T00–T12, not model training, not scientific superiority testing, not SeedGraph, not HydraDB writeback, not claim promotion.

## Primary question

Does SGLang breakable CUDA graph for PREFILL alter GPU inference efficiency or runtime failure behavior relative to disabled and tc_piecewise prefill under the same frozen model/workload?

- **H0:** Breakable prefill CUDA graph provides no improvement in the preregistered runtime efficiency endpoints relative to the controls.
- **H1:** At least one preregistered runtime endpoint differs.

No scientific model-quality hypothesis is formulated.

## Frozen stack

| Field | Value |
| --- | --- |
| Model | `Qwen/Qwen2.5-1.5B-Instruct` (fail-closed; no silent substitution) |
| Precision | FP16 unless detected GPU/stack requires explicit alternate dtype |
| SGLang | `0.5.18` from PyPI (`SGLANG_COMMIT_IF_SOURCE=71de97b264b04dcd514cf904003028aefe9775c8`) |
| Flags (expected; installed help is authoritative) | `--cuda-graph-backend-prefill`, `--cuda-graph-backend-decode` |

## Conditions (prefill varies; decode fixed = `full`)

| ID | Prefill | Decode |
| --- | --- | --- |
| C0 | `disabled` | `full` |
| C1 | `tc_piecewise` | `full` |
| C2 | `breakable` | `full` |

Unsupported configurations remain `UNSUPPORTED` — never silently replaced.

## Synthetic corpus

All rows labeled `SYNTHETIC_ENGINEERING_FIXTURE`.

- Prompt length targets: 256 / 1024 / 4096 / 8192 tokens (approximate construction; runtime records actual token counts)
- Batch sizes: 1 / 2 / 4
- `max_new_tokens`: 64
- Replicates: 3
- Identical workload ordering for C0/C1/C2
- Cells expected: 108

Hashes frozen in `kaggle/PREREGISTRATION.json` / `MANIFEST.json`.

## Metrics & failure phenotypes

See `kaggle/PREREGISTRATION.json`. Output comparison across conditions is `OUTPUT_EQUIVALENCE_DIAGNOSTIC` only. Generations remain `PROBABILISTIC_MODEL_OUTPUT`.

## Budget

`MAX_GPU_MINUTES=75`. Prefer one Kaggle GPU session. Incomplete cells → `TIME_BUDGET_EXHAUSTED`. Do not selectively rerun only favorable conditions.

## Orchestration

Reuse Ollarma burst pattern: prepare → push → status → collect → hash → receipt. Watcher is shell/Python only (poll ≥60s); no Cursor/model polling.

## Daisy connection

Produce `DAISY_RUNTIME_SUCCESSOR_RECOMMENDATION.json` only. Future Daisy use requires a new PLAN_CHECK (host/runtime/serving framework changed).

## Claim ceiling

`ONE_MODEL_ONE_KAGGLE_GPU_RUNTIME_STRESS_ONLY`
