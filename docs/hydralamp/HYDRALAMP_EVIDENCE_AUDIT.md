# HydraLamp Evidence Audit

`PROJECT_CONTROL.yaml`: **ABSENT**

## LongMemEval (bound to receipts)

Source: `docs/FINAL_ELIGIBILITY_EVIDENCE_MATRIX.json`, `RAW_FREEZE_MANIFEST.json`, `eval/track_model_k_20260820/CONTROL_RECONCILIATION_RECEIPT.json`

| Field | Value | State |
| --- | --- | --- |
| cases | 500 | EXECUTED |
| scored | 470 | EXECUTED |
| abstentions | 30 | PRESERVED |
| sessions | 23867 | FREEZE-BACKED |
| facts | 3506 | FREEZE-BACKED |
| entities | 4776 | MATRIX_STATED_ONLY (recompute mismatch) |
| K5 A Hit/Recall | 0.96383 / 0.90660 | EXECUTED |
| K5 D Hit/Recall | 0.94468 / 0.84603 | EXECUTED — **preserve negative/null advantage** |
| K10 A Hit/Recall | 0.97872 / 0.94535 | EXECUTED depth effect |
| K10 D Hit/Recall | 0.97021 / 0.92273 | EXECUTED |
| RAW vs SeedGraph ΔHit | 0 at fixed K | EXECUTED |

Do **not** replace K5 negative/null with K10 narrative.

## Dataset admission

| Dataset | Class |
| --- | --- |
| LongMemEval-S full500 | EXECUTED |
| LongMemEval-v2 | ADMITTED_NOT_EXECUTED |
| EnterpriseRAG-Bench | ADMITTED_NOT_EXECUTED / rights ok MIT declared |
| HERB | RIGHTS_GATED / ADMITTED_NOT_EXECUTED |
| BEAM | DOWNLOADED/identified — rows not materialized |
| BEAM-10M | DEFERRED |
| HydraBlast canaries | SYNTHETIC_ONLY / real advisory PENDING |
| context-vs-entropy | EXECUTED (diagnostic, not Hit@K) |

## ECA restoration

`ECA_RESTORATION_EMPIRICAL_STATE=NOT_ESTABLISHED`

ECA EXT80 exists as transparent deterministic conformance substrate (rules 30/90/110/184). Not a neural training model; not a substitute for LongMemEval empirical restoration claims.

HydraLamp poison/antidote path = governed **demo/mechanism canary**.
