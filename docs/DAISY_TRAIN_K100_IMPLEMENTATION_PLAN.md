# Implementation Plan: HydraDG Daisy Train — Track × Dataset × Model × K=5/10/100

This plan executes the complete preregistered cross-track experiment across Track 01 (Enterprise RAG), Track 02 (Real Dependency Graph), and Track 03 (LongMemEval Context Memory) at retrieval depths $K \in \{5, 10, 100\}$.

---

## HARD STOP & SCIENTIFIC CONTROL RULES

> [!CAUTION]
> 1. **No Vercel Deploy / No Git Push / No Merge**: Held 100% local on `hack-hydra/final-hosted-fcg-20260820` awaiting human authorization.
> 2. **Family-Wise Alpha Control**: Co-primary family consists of 9 tests (3 Tracks × 3 Models vs Heuristic at $K=10$). Holm-Bonferroni correction applied across the 9 primary tests at $\alpha=0.05$.
> 3. **Compute Optimization**: Model semantic extraction occurs ONCE per dataset. The frozen graph is replayed deterministically at $K=5, 10, 100$ across 3 replicates ($R_1, R_2, R_3$).
> 4. **Control Reconciliation**: Control reconciliation receipt resolves historical baseline scores before testing new cells.

---

## Execution Phases

### Phase 1: Control Reconciliation & Pre-Registration
- Reconcile $K=5$ Hit=0.942 vs historical 0.9638 / 0.9446 baselines.
- Produce [`eval/track_model_k_20260820/CONTROL_RECONCILIATION_RECEIPT.json`](file:///Users/byron/projects/active/hydradg/eval/track_model_k_20260820/CONTROL_RECONCILIATION_RECEIPT.json).
- Produce [`eval/track_model_k_20260820/PREREGISTRATION.json`](file:///Users/byron/projects/active/hydradg/eval/track_model_k_20260820/PREREGISTRATION.json).
- Produce [`eval/track_model_k_20260820/POWER_AUDIT.json`](file:///Users/byron/projects/active/hydradg/eval/track_model_k_20260820/POWER_AUDIT.json).
- Produce [`eval/track_model_k_20260820/DATASET_REGISTRY.json`](file:///Users/byron/projects/active/hydradg/eval/track_model_k_20260820/DATASET_REGISTRY.json).

### Phase 2: Local Model Discovery & Freeze
- Inspect installed local models (`qwen2.5-coder:7b`, `qwen2.5:7b`, `deepseek-r1:14b`) via `ollama list`.
- Record [`eval/track_model_k_20260820/MODEL_DISCOVERY_RECEIPT.json`](file:///Users/byron/projects/active/hydradg/eval/track_model_k_20260820/MODEL_DISCOVERY_RECEIPT.json).

### Phase 3: Cross-Track Execution Engine ($K=5, 10, 100$)
- **Track 01**: EnterpriseRAG-Bench PRIMARY ($N=300$).
- **Track 02**: HydraDG/HydraBlast Real Dependency Benchmark PRIMARY ($N=250$).
- **Track 03**: LongMemEval-S full500 PRIMARY ($N=500$, 470 scored, 30 abstentions).
- For each Track × Model combination:
  1. Extract ONCE $\rightarrow$ freeze raw output & model atoms.
  2. Project to canonical FCO/FCG subtrees.
  3. Replay $K=5, 10, 100$ with 3 replicates ($R_1, R_2, R_3$).
  4. Verify $R_1 == R_2 == R_3$ payload SHA-256 identity (`DETERMINISM_GATE = PASS`).

### Phase 4: Family-Wise Statistical Analysis
- Evaluate 9 primary co-primary tests at $K=10$ with Holm-Bonferroni correction.
- Compute paired McNemar test, 95% bootstrap CI, paired permutation test, context dilution ($K=100$), and saturation indices.
- Evaluate mechanistic secondary analyses at $K=5$ and $K=100$.

### Phase 5: Summaries & Final Machine-Verifiable Report
- Generate `TRACK01_SUMMARY.json`, `TRACK02_SUMMARY.json`, `TRACK03_SUMMARY.json`, `BEST_USE_HYDRADB_SUMMARY.json`, `CROSS_TRACK_STATS.json`, and `FINAL_DAISY_RECEIPT.json`.
- Report exact claim ceilings per track (`TRACK01_NO_GRAPH_ADVANTAGE_OBSERVED` / `TRACK02_REAL_DEPENDENCY_BENCHMARK_EXECUTED` / `TRACK03_DEPTH_EFFECT_REPLICATED` / `NO_MODEL_BENEFIT_OBSERVED`).

---

## Verification Plan

### Automated Verification
1. **Script Execution**:
   - `python3 scripts/run_daisy_train_cross_track_matrix.py`
2. **TypeScript & Build Verification**:
   - `cd apps/hydradg-web && npm run typecheck && npm run build`

### Manual Verification
1. Inspect `eval/track_model_k_20260820/` receipts and final report.
2. Confirm no git push or Vercel deployment executed.
