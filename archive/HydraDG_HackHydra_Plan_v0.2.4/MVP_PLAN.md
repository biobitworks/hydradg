# Hack Hydra MVP plan

## Goal
Demonstrate a HydraDB-native evidence-divergence graph that joins temporal agent memory with execution reproducibility.

## Public benchmark lane
1. Import LongMemEval-S metadata/history into portable JSONL.
2. Convert sessions/turns/evidence labels into SeedGraph objects.
3. Load typed graph into HydraDB.
4. Implement current/historical fact resolution.
5. Add controlled perturbation records.
6. Compare aligned run/memory branches.
7. Find first divergence and traverse affected descendants.
8. Answer queries with evidence paths and abstention.
9. Evaluate standard LongMemEval metrics plus new divergence/custody metrics.

## Execution-divergence lane
1. Run a small Pythia/Vithia-compatible fixture twice in the same environment.
2. Run same-host thread/concurrency perturbations.
3. Export environment, RNG, data order, tensors/checkpoints and fixed-probe logits.
4. Inject one controlled perturbation.
5. Compute bit/numeric divergence and first divergent object.
6. Ingest the run receipts into HydraDB and connect them to affected evaluation/claim nodes.

## Required ablations
- flat/vector retrieval baseline;
- HydraDB temporal graph without FCO/FCG gates;
- HydraDB + provenance;
- HydraDB + provenance + first-divergence/impact;
- full HydraDG with claim admission/recovery.

## Evaluation
Primary:
- LongMemEval QA overall + category scores
- Knowledge Update
- Temporal Reasoning
- Correct Abstention

New:
- first-divergence localization accuracy
- impact-set precision / recall / exact match
- evidence-path coverage
- unsupported-claim rejection rate
- claim-impact accuracy
- recovery equivalence
- storage overhead
- ingest latency
- p50/p95 query latency
- retrieved tokens per query

## Deadline schedule
### Aug 16 night
Freeze schema, novelty statement, import pipeline, synthetic smoke graph.

### Aug 17
LongMemEval-S import; HydraDB graph load; current/history queries; first 100-question dry run.

### Aug 18
Full 500-question evaluation; controlled perturbation dataset; Vithia/Pythia divergence notebook; ablations.

### Aug 19
Recovery experiment; UI; figures; README; 3-minute demo rehearsal; verify reproducibility commands.

### Aug 20
Final rerun from clean checkout; freeze result JSON; hash artifacts; record signing/Merkle status; video; submission form.
