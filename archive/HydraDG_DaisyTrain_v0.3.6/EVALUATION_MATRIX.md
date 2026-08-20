# Track 03 evaluation matrix

No numeric Hack Hydra judging weights are asserted here. This is the project's evaluation
scorecard, aligned to the Track 03 problem and the LongMemEval benchmark.

## Primary Track-facing denominator — LongMemEval-S full500

Report:
- overall QA accuracy / benchmark metric used by the official evaluator
- Information Extraction
- Multi-Session Reasoning
- Knowledge Updates
- Temporal Reasoning
- Abstention
- context tokens
- p50/p95 latency

Run all 500 after the HydraDB graph/query path is frozen.

## A-D ablation

A. flat/vector retrieval
B. HydraDB temporal graph
C. HydraDB temporal graph + FCO provenance
D. full HydraDG/FCO/FCG

For each configuration report:
- overall and per-category score
- evidence/provenance path coverage
- abstention precision/recall if available
- context-token count
- p50/p95 latency
- storage/ingest overhead

The ablation should answer whether provenance/admission/divergence machinery adds
explanatory capability and what accuracy/latency/storage tradeoff it introduces.

## Separate conformance denominator — ECA-EXT80

80 total trajectories:
- 20 baseline
- 20 cell-tamper
- 20 rule-drift
- 20 oracle-repair

Report:
- exact first-divergence localization: n / 60 perturbed trajectories
- state-exact recovery after oracle repair: n / 20
- deterministic result re-hash equality on a repeated run
- impact-size trajectory by rule/condition

Do not describe this as LongMemEval performance.

## Separate scientific replay denominator — XenoDisorder

Report:
- frozen input hash equality
- command-contract equality
- environment differences
- output-file hash equality
- exact matching numeric metric leaves
- max absolute numeric delta
- epsilon-threshold matching numeric leaves

Do not treat a disorder proxy score as a direct biological mechanism or clinical result.

## Separate ML execution lane — Vithia/Pythia

Import existing executed result:
- same-SKU replay
- declared token perturbation
- phase-level cross-SKU divergence
- parameter-gradient comparison

Do not claim the lexicographically first differing parameter is the temporally first CUDA/backprop operator.

## HydraDG injected perturbation suite

Keep this denominator separate from official LongMemEval.

Minimum cases should cover:
- `SUPERSEDED_BY`
- `CONTRADICTS`
- absent/removed supporting evidence
- unrelated control perturbation
- recovery

Ground-truth metrics:
- first-divergence exact match
- downstream affected-set precision/recall/F1
- affected-set exact match
- unsupported-claim rejection rate
- superseded-history reconstruction rate
- recovery classification accuracy

## Pass/fail gates

Release candidate must fail closed if:
- source hash pin fails;
- a benchmark denominator is mixed with a different lane;
- required evidence path is missing but a provenance claim is made;
- a signature/MMR claim is emitted without an executed operation;
- a historical-reproduction claim depends on substituted assets.
