# HydraDG Context Iceberg Score v1

## Purpose

Add a compact, deterministic "tip of the iceberg" indicator to the live HydraDG custody UI while retaining the full mathematical and provenance decomposition below the waterline.

This is an information-system abstraction. It is NOT physical thermodynamics.

## Headline display

Show two values together:

`ΔG*  +0.08 ↑   |   Cloud Drift 17/100`

Interpretation:
- `ΔG* < 0`: governed retrieval free-cost decreased relative to reference.
- `ΔG* = 0`: no change under the frozen abstraction.
- `ΔG* > 0`: governed retrieval free-cost increased relative to reference.
- `Cloud Drift`: magnitude of context-cloud distribution change, independent of whether the resulting retrieval outcome became better or worse.

Do NOT label negative ΔG* as "better accuracy". Accuracy/recall remain separate measured outcomes.

## G* abstraction

Use the preregistered HydraDG abstraction:

`G* = U* - tau*S_useful + gamma*S_irrelevant`

and:

`ΔG*_t = G*_t - G*_{reference}`

All weights and the reference state must be frozen before evaluating a new treatment.

## Context-cloud distribution

Define a stable, deterministic context-cloud feature vocabulary before comparison.

Candidate buckets may include:
- source/session class;
- semantic atom type;
- evidence relation type;
- question type;
- contradiction/supersession state;
- provenance class;
- retrieved rank bucket;
- source age/time bucket if deterministic and preregistered.

For bucket i:

`p_t(i) = count_t(i) / sum_j count_t(j)`

The reference distribution is `p_ref`.

### Cloud Drift

Use Jensen-Shannon divergence with base-2 logarithms:

`JSD(p_t || p_ref) = 0.5*KL(p_t || m) + 0.5*KL(p_ref || m)`

where:

`m = 0.5*(p_t + p_ref)`

With log base 2, JSD is bounded in [0,1].

Define the top-level drift magnitude:

`CloudDrift_t = 100 * JSD(p_t || p_ref)`

Therefore:
- 0 = identical distribution;
- 100 = maximally separated under the chosen frozen bucket vocabulary.

Do not silently change the bucket vocabulary or reference distribution between runs.

## Optional waterline metrics

Directly under the headline show:
- `Δ hit@k`
- `Δ recall@k`
- `Δ evidence-path coverage`
- `Δ provenance completeness`
- `mean answer rank displacement`

These are outcomes/components, not folded into CloudDrift v1.

Keeping CloudDrift purely distributional avoids an arbitrary omnibus score.

## Below-water decomposition

### Distribution
- Jensen-Shannon divergence
- total variation distance
- useful-evidence entropy
- irrelevant-evidence entropy
- semantic-atom mix shift
- relation-type mix shift

### Retrieval
- hit@k
- session recall@k
- evidence precision
- answer-rank displacement
- graph expansion ratio
- marginal K utility

### Governance
- provenance completeness
- orphan FCO count
- broken FCG edge count
- artifact hash mismatch count
- signature state
- Merkle state
- semantic abstention rate
- unresolved contradiction rate

### Identity
- current project FCG root
- reference project FCG root
- dataset/source root
- scorer/config root
- scientific result root
- HydraDB projection receipt root

## FCO/FCG object

Create a canonical project object equivalent to `ContextDriftObservation` only after binding to the canonical FCO/FCG schema.

Payload should contain:
- current_state_root
- reference_state_root
- distribution_schema_version
- distribution_schema_sha256
- scorer_version
- scorer_code_sha256
- config_sha256
- G_current
- G_reference
- delta_G
- js_divergence
- cloud_drift_0_100
- component_metrics
- primary_outcome_deltas
- null_hypotheses
- claim_ceiling
- signature_state
- Merkle_state

Dependency semantics:

`reference state + current state + scorer/config -> drift observation -> UI projection`

Map edge names through the canonical FCG schema; do not invent canonical predicates.

## Null hypotheses

### H0-DISTRIBUTION
The current context distribution is not detectably different from the frozen reference distribution beyond the preregistered tolerance/resampling criterion.

### H0-GIBBS
`ΔG* = 0`

### H0-ACCURACY-LINK
CloudDrift is not associated with a change in hit/recall.

### H0-GIBBS-ACCURACY-LINK
`ΔG*` is not associated with a change in hit/recall.

### H0-PROVENANCE
Context-cloud redistribution does not imply a custody/provenance break.

A custody hash mismatch is evaluated separately and is always a hard integrity event.

## Statistical treatment

When there are enough paired cases:
- bootstrap/permutation CI for ΔG*;
- bootstrap/permutation CI for CloudDrift or per-case drift contributions;
- Spearman association between per-case drift and outcome delta;
- stratify by question type;
- Holm correction for preregistered families.

When sample size is insufficient:
- report deterministic descriptive drift only;
- state `INCONCLUSIVE` for inferential claims.

## Live server presentation

Top of iceberg:

```text
CONTEXT ICEBERG
ΔG*          +0.08 ↑
Cloud Drift   17 / 100
Accuracy Δ    +0.0%
Recall Δ      -1.3%
Custody       HASHED · SIGNATURE PENDING
```

Waterline:

```text
Reference FCG  abc...
Current FCG    def...
JSD            0.170
Rank shift     +0.8
Provenance     100%
```

Below water: expandable component tables and lineage graph.

## State colors / language

Do not color `ΔG* < 0` green merely because it is negative.

Use neutral directional language:
- LOWER
- STABLE
- HIGHER

Separate empirical outcome:
- ACCURACY UP
- ACCURACY NULL
- ACCURACY DOWN

Separate custody:
- INTACT
- DRIFTED
- BROKEN
- PENDING VERIFICATION

## Recommended MVP decision

For v1 use exactly two tip scores:

1. `ΔG*` — signed directional abstraction.
2. `CloudDrift = 100 × JSD` — bounded magnitude of context distribution drift.

Do not introduce a third weighted omnibus score until empirical evidence shows it adds value.

This keeps the top-level indicator simple, while the full FCO/FCG lineage and diagnostic decomposition remain visible below the waterline.
