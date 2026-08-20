# Next-step plan

## Priority 0 — Freeze sufficient Vithia/Pythia evidence
Keep the existing v0.2.7 Modal evidence immutable. Import the bounded results; do not spend more GPU credits until Track 03 memory integration is working.

## Priority 1 — ECA-EXT80 deterministic canary
Run the self-contained ECA extension on Modal CPU.

Design:
- ECA rules: 30, 90, 110, 184.
- five deterministic seeds per rule.
- four conditions per rule/seed: baseline, cell tamper, rule drift, oracle repair.
- total: 4 × 5 × 4 = 80 trajectories.
- perturbed first-divergence denominator: 60.
- oracle-repair denominator: 20.

This lane tests serialization, first-divergence localization, impact-set measurement, and exact state recovery with known ground truth.

## Priority 2 — XenoDisorder local -> Modal replay
Recover/freeze the historical evaluator and assets. Do not infer the historical CLI from memory.

Required frozen objects:
- `cafa6_governed_eval.py`
- `ckpt_latest.pt`
- `residual_table.jsonl`
- `run_contract.json` containing the exact argv used for the local baseline.

Run local and Modal from the same frozen contract. Compare exact object hashes and numeric metric drift separately.

## Priority 3 — Normalize the three scientific/computational lanes
Normalize:
- ECA result JSON
- Xeno local/Modal comparison
- existing Vithia/Pythia result JSON

into content-addressed FCO nodes and typed FCG edges.

## Priority 4 — Pin HydraDB before writing the adapter
Record the exact HydraDB commit/API surface. Only then implement ingestion/traversal calls.

Required Track 03 graph capabilities:
- current fact query
- historical fact query
- `SUPERSEDED_BY`
- `CONTRADICTS`
- evidence/provenance path
- `FIRST_DIVERGED_AT`
- downstream `AFFECTED`
- `RECOVERED_BY`
- abstention for absent evidence

## Priority 5 — LongMemEval-S development lane
Download and verify the cleaned dataset.
- Use deterministic smoke80 while implementing HydraDB.
- Freeze graph construction, retrieval/query policy, and scorer configuration.
- Then evaluate all 500 official cases.

## Priority 6 — A-D ablation
A. flat/vector retrieval baseline
B. HydraDB temporal graph
C. HydraDB temporal graph + FCO provenance
D. full HydraDG/FCO/FCG admission/divergence/recovery path

Report accuracy and systems overhead separately.

## Priority 7 — Final freeze
Only after the application path is stable:
- rerun ECA full80 once;
- rerun Xeno only if its code/environment changed;
- run LongMemEval full500;
- run injected perturbation/recovery suite separately;
- compute all final hashes;
- generate figures and demo;
- sign or Merkle-commit only if those operations are actually implemented and verified.
