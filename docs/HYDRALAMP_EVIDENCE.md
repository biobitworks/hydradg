# HydraLamp Evidence + Model Matrix

## Frozen source

| Field | Value |
|-------|-------|
| Events | 46 |
| SHA-256 | `44e9d3dc7014b9b2c410a9e1e2c9b35a72cd269e4e561eba40414081ca81690d` |
| Mutability | **FROZEN — do not regenerate** |

## Review B model panel

- Models: qwen2.5:1.5b, phi4-mini:latest, qwen3:4b
- Class: **PROBABILISTIC_MODEL_OUTPUT** — not promoted to empirical evidence
- No model majority vote

## Deterministic reconciliation

- Script: `eval/ollarma_measurement_review_20260827/scripts/reconcile_measurements.py`
- Output: `SUBMISSION_FREEZE_RECONCILIATION_DELTA.json`
- Class: **DERIVED_RECONCILIATION_EVIDENCE**

## Judge strip (8 metrics)

See `JUDGE_METRIC_SURFACE.json`. Zero security counts are **gate outcomes**, not statistical superiority.

## PASS@3 lane separation

| Lane | PASS@3 | PASS^3 |
|------|--------|--------|
| 46-event golden | NOT_ESTABLISHED | NOT_ESTABLISHED |
| Authorization gauntlet (15×3) | 1.0 | 1.0 |

## CloudDrift boundary

- Canonical: `100 × JSD(P_t || P_ref)` — Context Iceberg implementation
- Gateway frozen lane: `GATEWAY_MSM_ENTROPY_PROXY_0_100 = 75.3349` — **not interchangeable**
- **Off judge strip**

## ΔG* boundary

- Dimensionless information-state diagnostic — **not physical Gibbs energy**
- ΔG*_step and ΔG*_reference preserved as separate semantics
- Engineering tier only

## Media lanes

| Lane | PIXEL_SEAL | Notes |
|------|------------|-------|
| HydraDG 46-event | NOT_RUN | Review B historical |
| Standalone HydraLamp d9f824e | PASS | BYTE_IDENTITY, tamper test PASS_REJECTED |
| FCG membership | BLOCKED | schema authority |

## Restoration gain

`RESTORATION_GAIN_TV=NOT_COMPUTED` on frozen 46-event gateway lane.
