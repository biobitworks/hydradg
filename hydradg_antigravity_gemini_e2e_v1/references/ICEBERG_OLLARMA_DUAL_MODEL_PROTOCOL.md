# HydraDG Iceberg + Ollarma Dual-Model Comparison Protocol v1

## Core rule

For every scientific Daisy run:

1. Freeze scientific output.
2. Compute deterministic metrics from frozen output:
   - G*
   - Delta G*
   - CloudDrift = 100 * Jensen-Shannon divergence
   - hit@k
   - recall@k
   - evidence precision
   - evidence-path coverage
   - rank displacement
   - graph expansion
   - provenance completeness
   - contradiction resolution
   - abstention rate
3. Repeat the scientific run according to the preregistered replicate plan.
4. Apply deterministic replicate-equality gates where the lane is promised deterministic.
5. Only after the run output and deterministic metrics are frozen, create an Ollarma
   diagnostic packet.
6. Send the identical packet and identical structured prompt independently to two approved
   local models.
7. Hash each model identity, prompt, response, config, and cache artifact.
8. Store model outputs as PROBABILISTIC_MODEL_OUTPUT FCOs.
9. Compare the models using preregistered deterministic scoring functions.
10. Freeze each model's prediction for the NEXT Daisy perturbation before that perturbation
    is executed.
11. Judge prospective prediction quality only on the subsequent held-out run.

Do not use one run both to generate a hypothesis and to validate that same hypothesis.

## Deterministic scientific lane

Let each condition/run be indexed r.

For every run compute:

G*_r = U*_r - tau*S_useful,r + gamma*S_irrelevant,r

DeltaG*_r = G*_r - G*_reference

CloudDrift_r = 100 * JSD(p_r || p_reference)

These scores are deterministic functions of:
- frozen scientific payload;
- frozen feature vocabulary;
- frozen reference distribution;
- frozen scorer code;
- frozen scorer config.

Nulls:

H0_D:
  context-cloud distribution is unchanged versus reference within preregistered tolerance.

H0_G:
  DeltaG* = 0.

H0_DA:
  CloudDrift is not associated with Delta accuracy/recall.

H0_GA:
  DeltaG* is not associated with Delta accuracy/recall.

H0_REP:
  deterministic replicate scientific roots are not identical.
  Advancement requires exact equality for deterministic lanes.

## Model lane

Approved models are M1 and M2.

Both receive the same diagnostic packet, containing only already-frozen evidence:
- experiment roots;
- H0;
- G* decomposition;
- CloudDrift decomposition;
- retrieval metrics;
- provenance/custody metrics;
- question-type strata;
- deterministic failure examples selected by a frozen rule;
- prior predictions if any.

Each model returns JSON with:
- mechanism_label
- expected_direction_next_run
- expected_metric_deltas
- falsification_test
- abstain
- optional probability for the preregistered outcome classes

No free-form model prose is used directly as a statistical endpoint.

## Model-repeat design

Model outputs are probabilistic-origin evidence.

Two useful repeat modes:

A. Replay-stability mode
   - temperature/config fixed;
   - same prompt/packet;
   - repeated N times;
   - measure exact-output hash equality and structured-label agreement.
   - This measures implementation/model replay stability, not scientific determinism.

B. Independent-sampling mode
   - frozen sampling config and seeds if supported;
   - repeated N times;
   - estimate distribution of structured predictions.
   - Preserve every response and seed/config.

Recommended minimum for hackathon diagnostics:
- 3 repeats/model/packet for replay stability;
- more only if compute/time permits and preregistered.

## Model-vs-model nulls

H0_M_AGREE:
  M1 and M2 have no systematic difference in structured mechanism classification.

For paired categorical outputs:
- Cohen's kappa for agreement;
- exact McNemar test for paired binary classifications;
- Bowker/Stuart-Maxwell only if preregistered and multi-class sample size is sufficient.

H0_M_DIRECTION:
  M1 and M2 have equal prospective accuracy for predicting the sign/direction of the next
  deterministic metric change.

For paired correctness:
- exact McNemar test.

H0_M_PROB:
  M1 and M2 have equal prospective probabilistic forecast quality.

If both emit valid frozen probabilities:
- paired Brier-score delta;
- paired permutation/bootstrap CI;
- optional log score if probabilities are bounded away from zero by a frozen rule.

H0_M_ABSTAIN:
  abstention rates do not differ.

Use paired exact test when cases are paired.

H0_M_UTILITY:
  model-generated falsification hypotheses do not differ in prospective utility.

Utility must be defined before evaluation, for example:
- predicted direction correct;
- falsification test executable;
- prediction specific enough to score;
- no unsupported claim beyond evidence.

Do not use subjective post-hoc ratings unless the rubric and rater procedure are frozen.

## Scientific nulls outrank model interpretation

The deterministic experiment decides:
- whether accuracy moved;
- whether recall moved;
- whether G* moved;
- whether CloudDrift moved;
- whether custody remained intact.

The models only propose mechanisms/predictions.

A statistically significant model difference does NOT promote the underlying scientific
claim unless the deterministic experiment supports it.

## Multiple testing

Create a preregistered family, for example:

Primary scientific family:
- Delta hit@k
- Delta recall@k

Secondary drift family:
- DeltaG*
- CloudDrift association

Model comparison family:
- prospective direction accuracy
- Brier score
- abstention rate

Apply Holm correction within each preregistered family.

Do not combine every dashboard metric into one giant multiple-testing family unless that
was preregistered.

## Sequential Daisy design

For each perturbation:

RUN N
  -> deterministic metrics
  -> replicate gate
  -> null/statistical decision
  -> freeze diagnostic packet
  -> M1 x repeats
  -> M2 x repeats
  -> freeze model predictions
  -> choose one preregistered falsification branch
  -> RUN N+1
  -> score prospective M1/M2 predictions
  -> compare models
  -> update FCO/FCG
  -> repeat

This creates:
source -> run -> scores -> model hypotheses -> prospective prediction -> next run ->
prediction score -> claim/counterevidence.

## UI

Top of iceberg:

DeltaG*       -0.07
Cloud Drift    18/100
Accuracy Delta +4.2%
Recall Delta   +3.1%

Model M1       predicts lower G* + higher recall
Model M2       predicts stable recall
Model compare  PENDING NEXT RUN

After next run:

M1 prospective accuracy  0.72
M2 prospective accuracy  0.58
paired p                 0.041
Holm-adjusted p          0.082
decision                 NO PROMOTED MODEL DIFFERENCE

The UI must show adjusted p-values and the preregistered null decision, not only nominal
significance.

## FCO/FCG custody

For each run create/bind canonical objects equivalent to:
- ExperimentRun
- IcebergScoreObservation
- ModelDiagnosticPacket
- ModelOutput M1
- ModelOutput M2
- ModelComparison
- ProspectivePrediction
- PredictionOutcome
- StatisticalDecision

Every material object records:
- exact source/root hashes;
- model digest;
- prompt hash;
- response hash;
- config hash;
- scorer code/config roots;
- evidence class;
- claim ceiling;
- signature state.

Map all identities and predicates through the canonical project FCO/FCG specification.

## Claim ceilings

Deterministic score:
  CONTEXT_DRIFT_DIAGNOSTIC

Model explanation:
  PROBABILISTIC_MODEL_OUTPUT

Model agreement:
  MODEL_COMPARISON_ONLY

Prospective model performance:
  PROSPECTIVE_MODEL_PREDICTION_EVALUATION

Scientific finding:
  only according to the deterministic benchmark/evaluation claim ceiling.

Never use:
  VERIFIED MODEL SUPERIORITY
unless a separate canonical verification procedure and adequate replicated evidence exist.
