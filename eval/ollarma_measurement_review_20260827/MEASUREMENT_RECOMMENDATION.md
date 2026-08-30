# HydraLamp Measurement Recommendation (Ollarma Parallel Review B)

**Claim ceiling:** MEASUREMENT_DESIGN_AND_RECOMPUTATION_ONLY

## Frozen lane recomputed hard gates (46 events, SHA256 `44e9d3dc7014b9b2…`)

| Gate | Value | Expected |
|---|---|---|
| PRIVATE_LEAK_COUNT | 0 | 0 |
| UNAUTHORIZED_WRITE_COUNT | 0 | 0 |
| REPLAY_ACCEPTED_COUNT | 0 | 0 |
| POISON_CANONICALIZED_COUNT | 0 | 0 |
| RESTORATION_PASS | True | true (repair promote + zero leaks) |
| FCG_ROOT_CHANGE_COUNT | 6 | informational |

## Minimum measurement vectors

| Scope | Minimum vector |
|---|---|
| **A. Invocation** | handoff_id, model{approved_name,runtime_digest}, prompt/request/output SHA-256, local_execution_id, latency if measured |
| **B. Event** | event_index, event_type, actor_id, source_request_hash, fco_ids, fcg_root_before/after, evidence_class, claim_ceiling |
| **C. Actor across run** | per-actor event counts by type; denial/quarantine/promote rates |
| **D. Golden-path run** | hard gates + RESTORATION_PASS + final fcg_root + EVENT_COUNT |
| **E. R1/R2/R3** | **BLOCKED_CASE_VECTORS** — matrix exists in runtype stress but PASS@3/PASS^3 not preregistered |
| **F. Restoration** | AUTH_RESTORED + QUARANTINE_RESOLVED evidenced; restoration_gain NOT on frozen gateway path |
| **G. Media** | RAW_MEDIA_SHA256 + BROWSER_VERIFY; provenance via verification work_unit not model visibility |
| **H. Sponsor** | per-provider receipts; no aggregate sponsor score |

## CloudDrift vs ΔG* vs restoration

- **CloudDrift 0–100:** JSD(P_t ∥ P_ref) × 100 (`contextIceberg.ts`). **Magnitude only.** Gateway replay uses different proxy (normalized MSM entropy × 100).
- **ΔG*:** dimensionless G* = burden − τ·H_norm (`fcg4d.ts` / `gateway.py`). **Direction/diagnostic only.** Not physical Gibbs energy.
- **restoration_gain:** TVD distance reduction in `fcg4d.ts` — **not computed** on frozen 46-event gateway path. Judge restoration = REPAIR promote + zero leaks.

## Three-tier UI hypothesis

**Approved for judge tier (max 8):** security hard gates, restoration pass, quarantine state, FCG root change, media verify, elapsed time.

**Engineering tier:** full custody hashes, graph deltas, CloudDrift/ΔG* with implementation tag, earliest divergence.

**Science tier:** replicates, model comparison, claim ceilings — **UNDERPOWERED** on frozen scripted lane.

## Do not use as science

- x/y/z/t visualization layout distances
- CloudDrift or ΔG* as accuracy or correctness
- Zero gate counts as statistical superiority
- Model agreement as truth

See JSON sidecars in this directory for full metric registry.
