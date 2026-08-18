# Best Use of HydraDB — Statistical Evaluation Plan

Status: PRE-REGISTER_BEFORE_SMOKE80
Scope: Hack Hydra Track 03 / HydraDG

## Evaluation question

Does graph-native retrieval over typed HydraDB relationships provide measurable value over non-graph retrieval when memory contains updates, contradictions, temporal state, perturbations and recoveries?

The evaluation must test a capability that is intrinsically relational: localize the first divergent dependency, traverse the affected downstream set, reconstruct historical state, reject unsupported downstream claims and recognize recovery without erasing the failed branch.

## Experimental unit and pairing

The unit is one fixed memory/query item. Every eligible item is evaluated under the same frozen item identity across all system variants and perturbation conditions. This enables paired analysis and prevents differences in item composition from masquerading as architecture effects.

### System variants — separate from perturbation labels

- `S0_FLAT`: deterministic flat/JSON or relational-style lookup over the same admitted facts; no graph traversal.
- `S1_VECTOR`: semantic/vector retrieval over the same evidence corpus and candidate budget; no explicit dependency traversal.
- `S2_HYDRADB_GRAPH`: HydraDB nodes/relationships with graph traversal for current/historical context, but without the full FCO/FCG admission and recovery policy.
- `S3_HYDRADG_FULL`: HydraDB + FCO/FCG typed dependencies + claim ceilings + first-divergence + affected-set + recovery reasoning.

If a variant is technically unavailable, report it as `NOT_RUN`; do not synthesize a score.

### Perturbation conditions

Preserve the existing project A-D lane as a distinct dimension:

- `A_REFERENCE`: frozen reference history/state.
- `B_FACT_PERTURBATION`: update/contradiction introduces a known first divergence.
- `C_DERIVED_STATE_PERTURBATION`: index/derived-state path is stale or interrupted while source graph state changes.
- `D_RECOVERY`: rebuild/replay/repair restores the declared recovery target while preserving the failed branch in history.

The real 2026-08-18 HydraDB/LessWrong context-routing incident is a qualitative case study and a source for controlled fixtures. It is not included in aggregate statistics unless its inclusion is declared before the evaluation freeze.

## Primary endpoints

1. `first_divergence_exact`: exact match to the known earliest divergent object/edge.
2. `impact_f1`: F1 over the known affected downstream set.
3. `unsupported_claim_rejection`: correct rejection/abstention when a load-bearing dependency is invalid or unavailable.
4. `history_reconstruction`: correct reconstruction of the requested historical answer/state.
5. `recovery_class_accuracy`: correct recovery class under the frozen recovery definition.

For Best Use judging, the key comparison is `S3_HYDRADG_FULL` versus `S0_FLAT` and `S1_VECTOR`, with `S2_HYDRADB_GRAPH` separating the value of graph structure from the additional FCO/FCG policy layer.

## Secondary endpoints

- current-answer accuracy;
- affected-set precision and recall;
- affected-set exact match;
- evidence-path coverage;
- provenance completeness;
- abstention correctness;
- context bytes/tokens;
- result-row count and traversal depth;
- latency p50/p95 and paired per-item latency difference;
- deterministic result-hash equality on exact replay where determinism is claimed;
- graph query/write/read failure rate.

## Statistical analysis

Use a fixed seed and preserve the exact input item IDs and raw per-item outputs.

- Binary paired endpoints: report each system's estimate and 95% bootstrap CI; compare paired systems with exact McNemar when discordant counts permit.
- Proportions/F1: paired bootstrap over item IDs, 10,000 resamples by default, to obtain 95% percentile confidence intervals for both absolute metrics and system deltas.
- Continuous paired metrics such as latency/context size: report median, p50/p95 and paired effect distribution; use a paired permutation test as the default inferential test. Wilcoxon signed-rank may be reported as a sensitivity analysis when its assumptions are reasonable.
- Multiple inferential secondary comparisons: use Holm correction. Primary reporting must emphasize effect sizes and confidence intervals rather than p-values alone.
- Missing/failed runs: never silently drop them. Report denominator, failure class and whether the metric treats the failure as incorrect, abstained or unavailable.

No statistical test converts a benchmark result into biological, causal or general correctness evidence.

## Sample-size sequence

### Smoke80

Run the same 80 frozen items through every enabled system/condition. Smoke80 is for:

- schema validation;
- runtime failure discovery;
- metric sanity checks;
- graph-query verification;
- rough effect-size/variance estimates;
- adjudicating ambiguous labels before the protocol is frozen.

Do not optimize prompts/queries on the same 80 and then report that optimized score as an untouched confirmatory result without labeling the adaptive process.

### Freeze

After smoke80:

- freeze system definitions;
- freeze graph schema/query semantics;
- freeze perturbation generator and random seed;
- freeze metric code;
- freeze item inclusion rules;
- freeze claim ceilings.

Record hashes of the frozen evaluator, fixture manifest and configuration.

### Full500

Run the frozen protocol on all 500 LongMemEval-S items or the final declared eligible set. Report the exact denominator and exclusions. Full500 is not allowed before the freeze receipt exists.

## Graph-native query tests

At minimum, HydraDB must be shown performing real graph operations that directly affect retrieval/results:

1. current fact/state traversal;
2. historical/superseded state traversal;
3. contradiction/supersession traversal;
4. first-divergence localization;
5. downstream affected-set traversal;
6. provenance/evidence path reconstruction;
7. recovery link and recovery-class reconstruction;
8. absence/unsupported-dependency path producing abstention or rejection.

For each query family preserve query text/parameters, HydraDB pin, result rows, canonical result hash, latency, and a receipt linking the result to the source FCO/FCG objects.

## Why vector-only / relational baselines matter

The submission should not assert that these tasks are impossible in another database. The bounded claim is narrower: typed dependency traversal and temporal/perturbation context are first-class in HydraDG/HydraDB, whereas flat or vector retrieval requires external logic to reconstruct those relationships. The experiment tests whether that graph-native representation yields better divergence localization, affected-set reconstruction, admissibility and recovery behavior under equal evidence.

## Compute placement

- Canonical graph state and authoritative evaluation receipts: `magicSTUDIObox` HydraDB.
- Control, comparison and Git checkpoints: `magicPRObox`.
- Modal: preferred burst runner for frozen CPU/GPU batch computations when needed.
- Kaggle: optional GPU batch fallback; not a persistent endpoint.
- Daytona: clean-room fresh-clone/install/reproduction surface, not a database.
- Exa/Apify: optional external-evidence perturbation lane only; dynamic web data must be snapshotted/hashed before it enters a reproducibility claim.

Provider credentials remain local secret material. Evaluation receipts may record provider, job/run ID, runtime class and non-secret configuration; never commit credential values.

## Output artifacts

The evaluation should produce:

- per-item JSONL with system, condition, item ID, predictions, gold/reference labels, affected sets, recovery class, latency/context and failure class;
- aggregate JSON with all point estimates and confidence intervals;
- paired comparison JSON with deltas/tests/corrections;
- a human-readable Markdown table for the README/submission;
- raw HydraDB query/write/read receipts;
- SHA-256 manifest over frozen evaluator/config/input/result artifacts.

Status terms must distinguish `RECOMPUTED`, `EXTERNALLY_RETRIEVED`, `MODEL_OUTPUT`, `INFERENCE`, `BENCHMARK_RESULT` and `NOT_RUN`.
