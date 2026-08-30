# STATISTICAL_ANALYSIS — NEWINML-DOC-ROUNDTRIP-001

## H-S1: Structured semantic composition advantage

**Result:** `NO_SIGNIFICANT_DIFFERENCE`

| Metric | Value |
|---|---|
| N held-out cases | 12 |
| Treatment accuracy | 0/12 (0%) |
| Baseline accuracy | 0/12 (0%) |
| Absolute delta | 0.0 |
| McNemar p | 1.0 |
| Primary model | `qwen2.5-coder:7b` |

### Interpretation

Neither condition achieved `BOUNDED_CLAIM_CORRECT` on the held-out set. Dominant failure mode: **MALFORMED JSON** from `ollama run` (non-governed CLI path; Ollarma routing not used). Treatment produced some valid ABSTAIN responses but zero scored CLAIM correctness.

This is **not** evidence against structured decomposition in principle — it is evidence that the current flat CLI invocation path does not produce schema-valid semantic outputs at this N.

### Protocol integrity

- Preregistered N=45; realized N=12 (adjudication set size from deterministic sampling).
- No optional stopping applied.
- EXP-008/EXP-009 unchanged.

## H-S2

`NOT_COMPUTED` — insufficient valid CLAIM outputs to compute false-support rates.
