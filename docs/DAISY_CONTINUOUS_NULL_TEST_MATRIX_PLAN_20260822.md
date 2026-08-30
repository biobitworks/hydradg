# HydraDG Daisy Continuous Null-Test Matrix Plan — 2026-08-22

## Control intent

Build a continuously executing Daisy train on `magicSTUDIObox.local` using only the exact Ollarma-approved intersection of generation-capable models present in Ollama. The scientific train continues through positive, null, negative, abstention, timeout, and wrong-answer outcomes. It stops automatically only for execution-integrity or custody failures.

Antigravity is not the experiment designer. Antigravity is a bounded operator for high-level chain-of-custody breaks, host/runtime failures, Git divergence, HydraDB projection/readback failure, missing model binding, durable-storage failure, or other declared infrastructure faults.

Canonical authority remains project governance and Git/FCO/FCG custody.

## GettingScienceDone governance carried forward

Every confirmatory block must include:

- preregistered H0/H1 and primary endpoint;
- minimum effect size of interest (MESI);
- power target and required N where applicable;
- temporal-integrity/HARKing gate;
- frozen data contract;
- frozen model, prompt, parser, scorer, K, treatment and host identities;
- red-team/risk gate where required;
- post-run drift check;
- negative-result classification as `NULL_RESULT`, `UNDERPOWERED`, or `TRUE_NEGATIVE` only when power supports that classification.

Ablation families with 5+ conditions require a declared multiplicity correction. Default: Holm for small preregistered confirmatory families; BH-FDR for larger exploratory families.

## Matrix roster rule

Target matrix size is ten models, but `10-model` may be stated only if all ten pass:

`HydraDG preregistered roster ∩ Ollarma approved roster ∩ Ollama present models ∩ generation-capable ∩ Studio execution lane`.

No silent substitutions and no Ollarma automatic fallback for scientific calls. Each admitted model is bound to exact runtime identity/digest.

If M != 10, preserve the roster failure and do not relabel an M-model run as the 10-model matrix.

## Scientific unit and replication

Primary paired unit: benchmark case within model.

Model is a factor, not a biological/technical replicate.

Dataset/track is a cohort/stratum, not a replicate.

For deterministic transforms/retrieval: require exact canonical scientific-payload root equality across R1/R2/R3.

For model generation: preserve raw stochastic output. Replication is evaluated as outcome stability/distribution, not byte identity unless the model/config truly guarantees deterministic generation.

## Common metric panel

### Primary task outcomes

- Hit@K
- Recall@K
- MRR where rank is defined
- nDCG@K where graded relevance is defined
- exact-answer / task-specific deterministic scorer result
- abstention rate
- failure/empty-output rate

### SeedGraph/pathway outcomes

- query-seed coverage
- candidate atom count
- hierarchy nodes scored
- graph edges traversed
- evidence-path coverage
- answer-bearing ancestor enrichment
- parent-expansion depth
- relevant-rank displacement
- source dereferences
- evidence bytes returned

### Computational-biology-style diagnostic metrics

Use as diagnostics, not omnibus claims:

- enrichment factor = observed relevant descendants / expected under background;
- odds ratio + Fisher exact test for enrichment of answer-bearing nodes among selected nodes;
- sensitivity/recall, specificity, precision, F1 and MCC where a binary relevant/not-relevant classification is well-defined;
- Jaccard overlap of retrieved evidence sets across replicates/treatments;
- coefficient of variation for technical latency/resource measurements when meaningful;
- Shannon entropy / normalized entropy of evidence distribution;
- Jensen-Shannon divergence for context-distribution drift (`CloudDrift = 100 × JSD_base2`);
- Spearman correlation for monotonic association between atom context score, rank, and empirical utility;
- track/cohort heterogeneity using effect-size forest summaries and I² only after per-track effects are established.

### Efficiency outcomes

- model input bytes/tokens
- source bytes read
- evidence bytes returned
- index lookups
- graph expansions
- retrieval wall time
- time-to-first-token
- generation wall time
- end-to-end wall time
- measured memory/CPU/GPU telemetry where available

Do not convert theoretical FLOPs to measured energy savings without an actual measurement contract.

### Governance/context outcomes

- source-byte coverage
- logical-record coverage
- orphan count/rate
- provenance completeness
- broken FCG edge count
- SHA mismatch count
- EVAL_ONLY leakage count
- semantic abstention count/rate
- unresolved contradiction count/rate
- `Delta G*` as the governed dimensionless information-state diagnostic
- CloudDrift 0–100

Do not assume lower `G*`, lower CloudDrift, or more evidence paths means higher accuracy. Those relationships are separately tested hypotheses.

---

# Test blocks

## T00 — Execution and custody QC

Classification: deterministic prerequisite.

H0-QC: the frozen experiment inputs/runtime/custody chain contain no execution-integrity divergence.

PASS requires:

- Studio host identity exact;
- source SHAs exact;
- model roster exact;
- prompt/scorer/config hashes exact;
- EVAL_ONLY separation exact;
- no duplicate model-case keys;
- graph/source pointers resolve and verify;
- Git Studio == Origin == Pro after bounded checkpoint;
- HydraDB projection/readback root parity when the treatment uses HydraDB.

Scientific null/negative output does not fail T00.

Stop only on custody/infrastructure failure.

## T01 — Deterministic hierarchy reproducibility

Question: does identical SeedGraph construction/query produce identical scientific payloads?

H0: R1, R2 and R3 differ in at least one canonical deterministic payload.

Alternative operational criterion: exact equality of canonical roots across R1/R2/R3.

Metrics:

- root equality;
- Jaccard retrieved-ID overlap (expected 1.0);
- source-pointer verification rate (expected 1.0);
- orphan rate (expected 0);
- source-byte/logical-record coverage (expected 1.0).

This is an integrity gate, not a performance claim.

## T02 — Flat retrieval vs deterministic SeedGraph

Treatments:

A = frozen flat/reference retrieval.
B = deterministic SeedGraph hierarchy, score-ablated.

H0: SeedGraph does not improve task quality over the flat route (`Δ primary_metric <= 0`).

Primary metric by track: preregister one metric; Track 03 defaults to Hit@K or Recall@K according to the frozen contract.

Statistics:

- exact McNemar for paired binary hit/correct outcomes;
- paired bootstrap CI for recall/rank deltas;
- paired permutation/randomization test for continuous paired deltas;
- effect size with 95% CI.

Guardrails:

- evidence bytes returned;
- source bytes read;
- latency;
- failure/abstention rate.

## T03 — K as a retrieval-depth dose-response

Treatments: frozen K series, initially K=5 and K=10; optional K=20 only in a successor preregistration.

H0: increasing K does not improve the primary retrieval endpoint.

Diagnostics:

- `ΔRecall / ΔK` marginal utility;
- `ΔHit / ΔK`;
- answer-rank distribution;
- evidence-path coverage;
- irrelevant-evidence entropy;
- evidence bytes/tokens per recovered answer.

Use paired tests because the same cases are evaluated at each K.

Do not conclude `larger K is better` from quality alone; cost and irrelevant-evidence burden are co-primary diagnostics.

## T04 — Hierarchy-level ablation

Conditions:

1. atom only;
2. atom + sentence;
3. atom + sentence + paragraph/turn;
4. atom + sentence + paragraph/turn + document/session;
5. full allowed FCG neighborhood.

H0: added hierarchy levels do not improve primary retrieval quality.

Secondary mechanistic hypotheses:

- useful hierarchy expansion enriches answer-bearing ancestors;
- excessive expansion increases irrelevant entropy/rank displacement.

Metrics:

- Hit/Recall/MRR;
- relevant-node enrichment factor;
- Fisher OR;
- expansion ratio;
- relevant-rank displacement;
- source/evidence bytes;
- wall time.

Multiplicity: Holm across the preregistered hierarchy contrasts.

## T05 — Atom context-score navigation ablation

Run only after a deterministic score source is bound to `canonical_key` or `seed_atom_id`.

Conditions:

S0 = no atom context scores;
S1 = context mean only;
S2 = context delta only;
S3 = variance penalty only;
S4 = full frozen score utility.

H0: context-score-guided navigation does not improve quality or navigation efficiency over S0.

Metrics:

- paired task quality;
- Spearman(context score, empirical relevance/rank utility);
- enrichment of answer-bearing atoms/ancestors;
- graph nodes scored;
- evidence bytes;
- wall time.

If score binding is not exact, classify `BLOCKED_SCORE_SOURCE_NOT_BOUND`; do not invent scores.

## T06 — Provenance/custody-only ablation

Purpose: distinguish governance benefit from retrieval benefit.

Compare semantically equivalent retrieval with and without provenance/custody metadata admitted to ranking while keeping verification on for both.

H0-quality: custody metadata does not change accuracy/recall.
H0-governance: custody metadata does not improve provenance completeness or auditability.

A valid expected result may be:

`quality delta = null`, `provenance completeness > 0`, `reproducibility improved`.

This is a positive governance result without a model-performance claim.

## T07 — Contradiction/supersession resolution

Use only real benchmark cases with valid temporal/supersession labels for the primary experiment. Synthetic conformance cases remain a separate structural test lane.

H0: contradiction/supersession edges do not improve selection of the current/valid evidence state.

Metrics where binary ground truth exists:

- sensitivity;
- specificity;
- precision;
- F1;
- MCC;
- stale-evidence selection rate;
- unresolved contradiction rate;
- rank of superseding evidence.

## T08 — Lazy dereference / evidence minimization

Compare full eager context with content-addressed lazy dereference at equivalent retrieval treatment.

H0-efficiency: lazy dereference does not reduce source/model context burden at equivalent task quality.

Primary efficiency endpoints:

- source bytes read;
- evidence bytes returned;
- input tokens.

Quality guardrail: non-inferiority MESI must be preregistered before confirmatory execution.

Report geometric mean ratios and paired bootstrap CIs for skewed cost distributions.

## T09 — Ten-model size/capability interaction

Only run as `10-model` when the roster gate proves exactly ten admitted Ollarma/Ollama identities.

For each model, compute paired treatment effects from T02–T08.

H0-interaction: SeedGraph treatment effect is unrelated to model size/capability class.

Analyses:

- per-model effect + CI first;
- Spearman against log parameter count only when parameter metadata is reliable;
- mixed/hierarchical model with case as repeated unit and model/treatment interaction as a secondary analysis;
- no pooling that treats 10 models as 10 independent case replicates.

Primary question: does navigation reduce the context burden more strongly for smaller models while preserving quality?

## T10 — Failure-phenotype analysis

Treat wrong, empty, timeout, abstention, parser failure and infrastructure failure as distinct phenotypes.

H0: treatment does not change scientific failure phenotype rates.

Metrics:

- per-category rate;
- paired McNemar for binary phenotype contrasts where appropriate;
- model × dataset contingency tables;
- time-to-failure distribution;
- raw-response token budget exhaustion where measurable.

Infrastructure failure is not silently merged into scientific incorrectness.

## T11 — Context drift and G* association

H0-D: context distribution does not materially change.
H0-G: `ΔG* = 0`.
H0-DA: CloudDrift is unrelated to quality delta.
H0-GA: `ΔG*` is unrelated to quality delta.
H0-P: context drift does not imply a provenance/custody break.

Metrics:

- JSD / CloudDrift;
- `ΔG*` and frozen components;
- Spearman with Hit/Recall deltas;
- permutation CI/test for association where appropriate;
- provenance completeness separately.

No causal claim from association alone.

## T12 — Cross-track/cohort replication

Run Track 01/02/03 separately first.

H0-generalization: an observed treatment effect in one track does not reproduce across other admitted tracks.

Require:

- per-track estimates/CIs;
- direction consistency;
- dataset-specific failure phenotypes;
- heterogeneity summary (I² only when effect estimates are comparable enough to pool);
- no pooled superiority claim when one track is blocked or uses a materially different scorer endpoint.

A Track 02 blocked state remains evidence, not a reason to manufacture a dataset.

---

# Continuous Daisy state machine

The controller should execute:

`T00 -> T01 -> T02 -> T03 -> T04 -> T05(if score binding) -> T06 -> T07(if eligible real cases) -> T08 -> T09 -> T10 -> T11 -> T12 -> aggregate/FCG append`.

For each test block:

1. `PLAN_CHECK`: verify preregistration, H0, metric, MESI/power if confirmatory, exact inputs and dependencies.
2. `EXECUTE`: Ollarma routes the exact admitted model to Ollama on Studio; no fallback.
3. `FREEZE`: raw outputs + deterministic telemetry are hashed and banked.
4. `SCORE`: deterministic scorer only.
5. `STATISTICS`: run frozen test family and multiplicity correction.
6. `NEGATIVE_RESULTS`: classify null/negative outcome according to achieved power; never rewrite.
7. `CUSTODY_APPEND`: FCO/FCG source -> transform -> result -> claim ceiling.
8. `HYDRADB_PROJECT/READBACK`: when applicable, verify canonical identity/root parity.
9. `COMMIT/PUSH`: explicit bounded paths from Studio.
10. `RECEIVER_SYNC`: Pro ff-only from origin; verify SHA/tree parity.
11. automatically launch next block when all execution-integrity gates pass.

Scientific results that do NOT stop the train:

- incorrect answer;
- negative effect;
- null effect;
- abstention;
- model-produced empty response if transport completed and the outcome is correctly receipted;
- scorer returns valid zero/negative result;
- a hypothesis is rejected.

Execution/custody states that DO stop and require operator intervention:

- source SHA mismatch;
- EVAL_ONLY leakage;
- scorer/config identity mismatch;
- wrong host;
- runtime model does not match frozen model identity;
- unexpected auto-fallback/substitution;
- missing/duplicated case keys;
- source-pointer SHA verification failure;
- HydraDB projection/readback root mismatch;
- Git three-way SHA/tree divergence;
- unrecoverable disk/storage failure;
- parser/scorer crash that prevents an outcome receipt;
- process exited without terminal receipt;
- corruption of durable raw outputs.

## Antigravity escalation contract

Antigravity receives only a compact deterministic fault packet containing:

- run/test/block ID;
- expected vs observed hashes/identities;
- PID/process state;
- last terminal receipt;
- Git Studio/Origin/Pro SHAs and trees;
- HydraDB write/read roots;
- model runtime identity;
- source/scorer/config IDs;
- storage state;
- earliest divergent dependency.

Antigravity may:

- diagnose high-level execution/custody faults;
- inspect logs/configurations;
- repair an operational implementation bug in a successor version;
- restore synchronization without destroying divergent evidence;
- restart/resume only according to the frozen resume contract;
- create a repair receipt and return control to the Daisy state machine.

Antigravity may not:

- change H0/H1;
- change dataset/case set;
- change K;
- change scorer;
- change prompt;
- replace a model;
- modify metric weights;
- rerun only failed scientific cells to improve a result;
- promote claims;
- delete null/negative/failure evidence.

## Ollarma operational role

Ollarma is the governed runtime/orchestration layer. It should:

- expose the approved model roster;
- bind exact model identity to Ollama runtime identity;
- execute one scientific invocation at a time per frozen concurrency policy;
- persist request/raw-response/config/runtime receipts;
- checkpoint model x dataset blocks;
- expose deterministic progress counters;
- never auto-fallback scientific calls.

During active scientific inference, watcher model generation against the same Ollama runtime is prohibited. Monitoring is deterministic telemetry only.

## Checkpoint cadence

Prefer model-major execution:

`model -> Track 01 -> checkpoint -> Track 02 -> checkpoint -> Track 03 -> checkpoint -> next model`.

For each test/treatment, this yields bounded restartable blocks without creating per-case Git commits. Heavy raw output remains in the durable bank; Git stores manifest, hashes, result summary, FCG delta and durable pointer.

## Minimum automatic receipt per block

- test_id / hypothesis ID;
- experiment classification;
- model tag + digest;
- dataset + case-manifest root;
- treatment/K/hierarchy/score configuration root;
- prompt/parser/scorer SHAs;
- case counts expected/accounted;
- correct/incorrect/abstention/scientific-empty counts;
- infrastructure failure/timeout/parser failure counts;
- primary metric + effect + CI + p/q value where applicable;
- power/MESI fields for confirmatory tests;
- negative-result classification;
- efficiency panel;
- context/G*/CloudDrift panel where applicable;
- raw output bank root;
- FCG delta/root;
- HydraDB write/read state;
- claim ceiling;
- signature/Merkle state.

## Promotion logic

No individual p-value promotes a HydraDG superiority claim.

Promotion requires:

1. execution/custody PASS;
2. confirmatory preregistration PASS;
3. adequate power for the preregistered MESI;
4. corrected primary-family significance or a valid non-inferiority criterion, as applicable;
5. effect size/CI supporting the claim direction;
6. no catastrophic guardrail degradation;
7. replication in the required dataset/model strata;
8. claim ceiling review by Byron + ChatGPT.

All other outcomes remain queryable FCG evidence.

## Immediate implementation tasks

D01. Freeze current branch/control SHA before implementation.
D02. Add machine-readable `DAISY_TEST_REGISTRY_V1` mirroring T00–T12.
D03. Add `DAISY_STATE_MACHINE_V1` with explicit continue/stop transitions.
D04. Add Ollarma roster-binding gate and prohibit scientific auto-fallback.
D05. Add exact per-block receipt schema.
D06. Add GSD power/MESI/temporal-integrity fields to confirmatory blocks.
D07. Add negative-result registry adapter.
D08. Add deterministic statistical library wrappers: exact McNemar, paired bootstrap, paired permutation, Holm/BH-FDR, Fisher exact, MCC, JSD.
D09. Add context/enrichment metric calculator.
D10. Add navigation/efficiency telemetry calculator.
D11. Add R1/R2/R3 deterministic-root reproducibility gate.
D12. Add model-major resumable queue with durable raw-output pointers.
D13. Add deterministic watchdog; zero watcher-LLM calls during inference.
D14. Add fault-packet generator for Antigravity escalation.
D15. Add FCO/FCG append for each terminal block state including null/negative/failure.
D16. Add HydraDB projection/readback parity gate.
D17. Add bounded checkpoint commit/push and Pro ff-only sync gate.
D18. Add aggregate cross-model/cross-track report without claim promotion.
D19. Run zero-model integration tests of the entire state machine.
D20. Return to Byron + ChatGPT for PLAN_CHECK before launching the first new confirmatory scientific block.

## Current claim boundary for this plan

This document is a preregistration/control design. It does not establish that a 10-model roster is currently available, that any new test has executed, that SeedGraph improves retrieval, or that any model-size interaction exists.
