# Matrix Lineage Reconciliation

- Created: `2026-08-27T08:21:57.398Z`
- Git SHA: `7d48f6fd14b003d040dd8df25424e46cd6fc84fc`
- PROJECT_CONTROL.yaml: **ABSENT**

## Why 9-model status ≠ 12-model preregistration

Chronologically, Studio preflight inventory (LINEAGE_C) admitted all generation-capable Ollama tags → 12 models × 1020 = 12240. The scientific runner/status (LINEAGE_B) hardcoded a 9-model subset → 9180. Diff tags in 12 not in 9: gpt-oss:20b, llava:7b, qwen3.6:27b. This is a design split (inventory vs scientific), not yet a custody contradiction until an execution claims both ceilings as the same experiment.

## Lineages

### LINEAGE_A_HISTORICAL_10x1020
- expected_slots: `10200`
- accounted_slots: `0`
- claim_ceiling: `EXPANDED_MODEL_MATRIX_NOT_ESTABLISHED_FROM_REAL_CASE_EXECUTION`
- note: Historical repaired design; prior PASS receipts invalidated by execution_audit_20260820

### LINEAGE_B_STUDIO_SCIENTIFIC_9x1020
- expected_slots: `9180`
- accounted_slots: `9`
- claim_ceiling: `STUDIO_OLLARMA_GOVERNED_REAL_MATRIX_CANARY_PASS_FULL_MATRIX_IN_PROGRESS_NOT_FINAL`
- note: Scientific runner used 9-model subset; status overclaim audited

### LINEAGE_C_STUDIO_INVENTORY_12x1020
- expected_slots: `12240`
- accounted_slots: `0`
- claim_ceiling: `INVENTORY_PREREGISTRATION_NOT_EXECUTION`
- note: Preflight auto-admitted all generation-capable Ollama tags

### LINEAGE_D_STUDIO_9x770_V11
- expected_slots: `6930`
- accounted_slots: `48`
- claim_ceiling: `STUDIO_OLLARMA_REAL_DATASET_DIAGNOSTIC_CANARY_MATRIX_EXECUTED`
- note: Early terminated: output budget / empty responses

### LINEAGE_E_QWEN38_SUCCESSOR_FACTOR
- expected_slots: `PENDING_CANARY_AND_SUCCESSOR_FREEZE`
- accounted_slots: `0`
- claim_ceiling: `SUCCESSOR_EXPERIMENTAL_FACTOR_NOT_SILENT_REPLACEMENT`
- note: Must NOT replace qwen3.6:27b / qwen3.5:9b / qwen3:8b

