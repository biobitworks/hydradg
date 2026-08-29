# EXP-012 — AntiCube-3D Hierarchical Escalation and Governed Uncertainty Reduction

Date: 2026-08-29

## Scientific question

Can HydraDG reduce unresolved scientific-information uncertainty through a deterministic-to-model escalation cascade while preserving identity, provenance, contradiction, abstention, terminal accounting, and bounded claim ceilings; and do AntiCube state/trajectory plus context-state deltas improve the decision of when to terminate, abstain, or escalate?

## Core architecture under test

```text
new source / observation
        ↓
new atom(s)
        ↓
ΔFCG
        ↓
ΔCFMO
        ↓
Δcontext
        ↓
AntiCube position / trajectory
        ↓
ΔG* / decision pressure
        ↓
priority / escalation-state change
        ↓
resolve / abstain / escalate
```

HydraDG treats inference as governed uncertainty reduction: deterministic structure and progressively larger models resolve increasingly difficult subsets of a content-addressed evidence graph, while AntiCube and context-state deltas govern escalation, explicit abstention preserves unresolved cases, and only residual uncertainty reaches the largest available model, a frontier model if preregistered and available, or a human adjudication surface.

## AntiCube-3D definition

The canonical 2D state plane remains:

- X axis: SELF ↔ NON-SELF
- Y axis: NON-SAFE ↔ SAFE

The third axis is **time / governed state index**, producing a trajectory through the state cube rather than replacing the 2×2 classification.

For object `o` at state/time `t`:

```text
A(o,t) = (x_self(o,t), y_safe(o,t), t)
```

where the categorical quadrant is still one of:

- SELF_SAFE
- SELF_NONSAFE
- NONSELF_SAFE
- NONSELF_NONSAFE

A transition is:

```text
ΔA_t = A(o,t+1) - A(o,t)
```

Do not interpret a hash as semantic similarity, or time as a third categorical safety axis. The Z axis is state/time so movement can be shown and audited.

## Context and ΔG* abstraction

Use the existing versioned HydraDG/CFMO definitions found in canonical repository sources. Do not silently redefine them.

The experiment must inventory every distinct ΔG / G* score or component already defined in the project and produce a machine-readable registry before execution:

```text
metric_id
canonical_name
formula
units_or_dimensionless_state
scope
source_file
source_sha256
first_commit
current_status
claim_ceiling
```

At minimum distinguish any currently implemented forms such as:

- G* state
- ΔG* signed state change
- object-level ΔG* if actually implemented
- context-level ΔG* if actually implemented
- retrieval/engineering ΔG variants if present
- Cloud Drift / JSD as a separate distribution-shift metric, never mislabeled ΔG*
- any historical/superseded ΔG-like score retained in custody

**Do not hard-code the number of ΔG variants in advance.** The deterministic inventory count is an experimental output.

## Escalation ladder

The ladder is a capability hierarchy, not a requirement to invoke every rung:

```text
R0 deterministic / exact / schema / graph
R1 tiny local model
R2 small local model
R3 medium local model
R4 large local model
R5 largest/frontier model only if preregistered, available, and still unresolved
R6 human adjudication only if residual uncertainty remains materially unresolved
```

Use actual installed Ollarma/Ollama model identities and digests. Map them into rung classes from measured/declared parameter scale; do not pull models solely to fill a rung.

Every rung has exactly four scientific terminal actions:

```text
ACCEPT
REJECT
ABSTAIN
ESCALATE
```

Operational failures remain separate terminal states:

```text
FAILED
TIMEOUT
BLOCKED
INVALID
```

## Primary hypotheses

### H1 — progressive resolution

The number of unresolved cases decreases monotonically or non-increasingly across the governed cascade on the tested corpus:

```text
N_R0 >= N_R1 >= N_R2 >= N_R3 >= N_R4 >= N_R5 >= N_R6
```

A violation is preserved; do not repair it away.

### H2 — governed escalation efficiency

Compared with an otherwise matched largest-model/frontier-everything baseline, the governed cascade reduces expensive-model/human escalations while remaining within preregistered correctness, provenance, contradiction, and abstention bounds.

### H3 — AntiCube/context routing contribution

Holding the model ladder fixed, adding governed FCG/provenance, AntiCube state/trajectory, and ΔG*/context movement improves escalation decisions or reduces unnecessary escalation without violating the quality envelope.

## Routing-policy ablation

Run paired cases under:

```text
B0 = largest available model / frontier-everything reference
B1 = single large local model
B2 = size cascade only
B3 = size cascade + FCG/provenance
B4 = B3 + AntiCube trajectory
B5 = B4 + ΔG*/CFMO/context-delta signals
```

If a true external frontier model is unavailable or prohibited, classify B0/R5 as `NOT_RUN_FRONTIER_UNAVAILABLE` and use the largest frozen local model as a separately labeled reference. Do not call it frontier.

## Required measured endpoints

For each rung and policy:

- cases_entering
- ACCEPT
- REJECT
- ABSTAIN
- ESCALATE
- FAILED
- TIMEOUT
- BLOCKED
- INVALID
- cases_resolved
- cases_remaining
- false_early_accept_rate where gold/reference supports scoring
- false_early_reject_rate
- correct_abstention_rate
- contradiction_preservation
- provenance_correctness
- terminal_accounting_error_count
- mean/median model calls
- mean/median input tokens if measurable
- wall time, with runtime metrics kept separate from scientific payload when nondeterministic
- measured cost only where actually measured

Primary systems endpoint:

```text
frontier_or_human_escalation_rate
```

paired with the preregistered quality/safety envelope.

## AntiCube trajectory output

Every evaluated object/case must be capable of producing a state sequence:

```text
object_id
t_0: quadrant, x, y, z/state_index, G*, ΔG*, CFMO/context root, priority, action
t_1: ...
...
```

Each transition must link to the exact admitted FCG delta causing the change.

A trajectory with no movement is valid evidence.

## Priority

Priority is an operational routing output, not scientific truth.

Freeze the existing priority implementation if present. If absent, do not invent a single opaque scalar and call it canonical. Instead report the component vector and a clearly labeled experimental priority function.

## Controls

Positive controls:

1. exact identity duplicate terminates at R0;
2. known supported source-bound proposition can terminate before human escalation;
3. explicit contradiction remains contradictory;
4. known unanswerable item can abstain;
5. deterministic provenance mismatch is detected.

Negative/adversarial controls:

1. source-span swap;
2. wrong provenance edge;
3. contradiction pair;
4. unsupported stronger claim;
5. stale/superseded evidence;
6. same/self source becoming contextually non-safe;
7. external/non-self source that is nevertheless safe/admissible;
8. dropped terminal object;
9. score/metric missing;
10. model disagreement across rungs.

## Statistics

Freeze exact analyses before running the confirmatory set.

Use paired case-level comparisons. Do not treat repeated generations as independent scientific samples.

Candidate tests:

- exact McNemar for paired escalation/correctness events;
- paired bootstrap confidence intervals for rate/accuracy differences;
- permutation or Wilcoxon tests where metric structure supports them;
- Holm correction for multiple confirmatory comparisons.

Report effect size, 95% CI, exact N, discordant-pair counts, and corrected p-values. If underpowered, report `UNDERPOWERED`; do not manufacture significance.

## Claim ceilings

Allowed maximum claims are bounded by observed evidence:

```text
PIPELINE_EXECUTED
CASCADE_RESOLUTION_OBSERVED
ANTICUBE_TRAJECTORY_RECONSTRUCTED
FCG_CFMO_CONTEXT_TRAJECTORY_PRESERVED
ESCALATION_REDUCTION_OBSERVED
STATISTICALLY_SUPPORTED_ESCALATION_REDUCTION
```

Never promote to universal optimal routing, universal safety, universal truth preservation, or human-equivalent adjudication.

## Figure contract

Figures are deterministic derived artifacts, never hand-edited scientific evidence.

The figure generator must read machine-readable receipts only.

Required figures:

1. **AntiCube-3D trajectory**
   - X: SELF → NON-SELF
   - Y: NON-SAFE → SAFE
   - Z: time/state index
   - preserve four quadrant labels on the XY plane
   - show one or more empirically observed object trajectories
   - encode ΔG*/decision-pressure only from measured/derived fields; if visualized by line width/marker size/annotation, document mapping
   - do not imply continuous x/y semantics unless the canonical classifier actually emits continuous components

2. **Governed state-transition chain**
   - source/observation → atoms → ΔFCG → ΔCFMO → Δcontext → AntiCube movement → ΔG* / decision pressure → priority/action → resolve/abstain/escalate
   - every displayed count/value comes from a receipt

3. **Escalation funnel**
   - R0 deterministic → tiny → small → medium → large → frontier/largest → human
   - show cases entering, resolved, abstained, escalated, failed at every rung

4. **FCG trajectory panel**
   - selected example showing graph root or delta IDs across t0..tn, AntiCube state, ΔG*, and decision/action

All visible scientific text/values should originate from governed data or a versioned static label registry. Generate SVG + PDF + PNG, hash exact bytes, and create a figure manifest mapping each visible dynamic value to its source receipt field.

## Terminal accounting

Every source, case, model call, transition, and figure must have a terminal state. No disappearing cases.

## Crypto boundary

SHA-256 establishes byte identity only.

`SIGNATURE_STATE=SIGNED` only after an authorized private-key operation.

`MERKLE_MMR_STATE=COMMITTED` only after actual construction, leaf ordering, root, and verification receipt.
