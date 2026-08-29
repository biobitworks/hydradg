# CURSOR MASTER PROMPT — EXP-012 AntiCube-3D, Escalation Cascade, ΔFCG/CFMO Trajectory, Deterministic Paper Figures

Execute on `magicSTUDIObox.local` only.

## Objective

Finish the currently open governed HydraDG/NewInML successor work, validate every predecessor execution/integrity block to a terminal successor state, execute EXP-012 as a real empirical test of HydraDG's governed uncertainty-reduction cascade, derive AntiCube/ΔG*/CFMO/FCG trajectories from actual receipts, generate deterministic paper figures from those receipts, validate the figures, and include them in a successor paper artifact without mutating historical evidence.

The thesis under test is:

> HydraDG treats inference as governed uncertainty reduction: deterministic structure and progressively larger models resolve increasingly difficult subsets of a content-addressed evidence graph, while AntiCube and context-state deltas govern escalation, explicit abstention preserves unresolved cases, and only residual uncertainty reaches the largest/frontier model or human adjudication.

This sentence is a hypothesis until EXP-012 evidence supports it.

---

# 0. HARD GOVERNANCE

First run:

```bash
hostname
whoami
pwd
git status --short
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch origin
```

Require:

```text
HOST=magicSTUDIObox.local
```

Then read, in authority order, if present:

```text
PROJECT_CONTROL.yaml
AGENTS.md
FCO_FCG_CANONICAL_SPEC.md
CLAIM_CEILINGS.md
EVIDENCE_LEVELS.md
FCO_SCHEMA.json
FCG_SCHEMA.json
SIGNING_AND_KEYS.md
```

Read in full:

```text
docs/EXP012_ANTICUBE_ESCALATION_PREREGISTRATION_20260829.md
```

Do not silently redefine FCO, FCG, AOK, SOT, CFMO, AntiCube, G*, ΔG*, Cloud Drift, priority, or claim ceilings.

Preserve:

```text
DIRECT_HUMAN_EVIDENCE
EXTERNALLY_RETRIEVED_EVIDENCE
DETERMINISTIC_TOOL_OUTPUT
RECOMPUTED_RESULT
PROBABILISTIC_MODEL_OUTPUT
INFERENCE_HYPOTHESIS
VERIFIED_EMPIRICAL_RESULT
NULL_RESULT
NEGATIVE_RESULT
UNDERPOWERED
FAILED
TIMEOUT
BLOCKED
ABSTAINED
CONTRADICTORY
```

Historical null/negative/failed states MUST NOT be changed to PASS.

A predecessor integrity failure may receive a successor relationship such as:

```text
FAILED_PREDECESSOR
→ SUPERSEDED_FOR_EXECUTION_BY
SUCCESSOR_RUN
```

but never:

```text
FAILED_PREDECESSOR
→ WAS_ACTUALLY_PASS
```

SHA-256 establishes byte identity only.

Do not claim `SIGNED` without an actual authorized private-key signing operation.

Do not claim `MERKLE_MMR_STATE=COMMITTED` without actual leaves, deterministic ordering, algorithm, root, and verification receipt.

---

# 1. PULL / BRANCH GATE

This prompt was committed to:

```text
cursor/exp012-anticube-escalation-figures-20260829
```

Start by fetching it from origin.

If current local work is clean and the actual PROJECT_CONTROL/Git topology permits:

```bash
git fetch origin
git switch cursor/exp012-anticube-escalation-figures-20260829
git pull --ff-only origin cursor/exp012-anticube-escalation-figures-20260829
```

If local work would be overwritten, STOP the switch, preserve current work, create a reconciliation worktree/branch, and record the divergence. Never `reset --hard` or discard uncommitted evidence.

Record:

```text
BASE_BRANCH
BASE_SHA
EXECUTION_BRANCH
EXECUTION_START_SHA
WORKTREE_STATE
```

---

# 2. PREDECESSOR STATUS RECONCILIATION — DO THIS BEFORE NEW SCIENCE

Build:

```text
eval/exp012_anticube_escalation_20260829/PREDECESSOR_GATE_MATRIX.json
```

Enumerate all material predecessor lanes referenced by PROJECT_CONTROL, current paper manifests, active PRs, recent `eval/`, `custody/`, `paper/`, and the existing Daisy state files.

At minimum inspect and classify where present:

- EXP-008
- EXP-009
- Stage-2 / IC failure learning
- SeedGraph control and real-evidence atomization batches
- interrupted/corrupt SeedGraph hierarchy predecessor
- Qwen3.8 successor lane
- local Ollarma/Ollama model inventory
- Cloudflare OS lane
- SGLang/BCG lane
- Daytona/Kaggle remote lanes if currently referenced
- HydraLamp deterministic perturbation/tamper/replay receipts if admitted to the current paper scope
- deterministic figure lineage from the prior figure task
- current NewInML paper readiness/submission receipts

For each block write:

```text
block_id
predecessor_state
predecessor_evidence_sha256
open_execution_integrity_blocker
successor_action
successor_state
successor_receipt
claim_ceiling
fcg_relationship
```

Allowed successor_state examples:

```text
PASS
RESOLVED_BY_SUCCESSOR
RETAINED_NULL
RETAINED_NEGATIVE
RETAINED_FAILURE
UNDERPOWERED
BLOCKED_EXTERNAL_DEPENDENCY
NOT_RUN
OUT_OF_SCOPE
```

Goal:

- all **execution/integrity** blockers relevant to EXP-012/paper generation become PASS/RESOLVED_BY_SUCCESSOR or remain explicit blockers;
- all scientific nulls/negatives/failures remain preserved;
- no ambiguous yellow state is silently called green.

Write:

```text
PREDECESSOR_GATE_MATRIX.md
PREDECESSOR_GATE_MATRIX.json
```

---

# 3. INVENTORY THE GIBBS / ΔG SCORE FAMILY — DO NOT GUESS

Before executing EXP-012, deterministically search the repository, admitted project sources, docs, schemas, scorers, receipts, and paper source for all G*/ΔG-like metrics.

Create:

```text
eval/exp012_anticube_escalation_20260829/DG_SCORE_REGISTRY.json
.../DG_SCORE_REGISTRY.md
```

For every distinct **formula/semantic definition**, record:

```text
metric_id
canonical_name
formula
scope
experimental_family
units_or_dimensionless
source_path
source_sha256
first_seen_commit_if_resolvable
current_status
paper_admissibility
superseded_by
```

Historical evidence indicates at least these **five named Gibbs-style quantities/definitions across project history**; verify rather than assume:

1. `G*` — HydraDG dimensionless information-state/free-cost abstraction.
2. `ΔG*` — signed change in that information-state quantity.
3. `G_Bio` — separate Bio-ΔG biological prototype potential.
4. `ΔG_poison` — biological perturbation change relative to biological reference.
5. `ΔΔG_restore` — biological restoration change relative to poison.

IMPORTANT:

The Bio-ΔG family is a separate experimental/application family. Do not import it into the NewInML paper merely because it uses Gibbs-style language.

Also inventory, but keep distinct from ΔG:

- Cloud Drift = 100 × base-2 JSD;
- Structural Cloud Drift;
- Retrieval Cloud Drift;
- mutation distance / total variation;
- restoration gain where actually computed;
- useful evidence entropy;
- irrelevant evidence entropy;
- U* components;
- any historical engineering proxy such as a gateway entropy score.

Do not count condition instances such as `G*_RAW_K5` and `G*_SG_K10` as separate formulas unless their definitions actually differ.

Output:

```text
DG_DISTINCT_FORMULA_COUNT=<deterministically computed count>
DG_CURRENT_HYDRADG_INFORMATION_STATE_COUNT=<count>
DG_HISTORICAL_OR_OTHER_PROJECT_FAMILY_COUNT=<count>
ADJACENT_CONTEXT_DIAGNOSTIC_COUNT=<count>
```

For the NewInML figure, use only metrics admitted to the current HydraDG paper lineage.

---

# 4. ANTICUBE-3D CONTRACT

AntiCube remains the canonical 2×2 state classification:

```text
                          SAFE
                           ▲
                           │
          SELF_SAFE        │       NONSELF_SAFE
                           │
 SELF ◄────────────────────┼────────────────────► NON-SELF
                           │
        SELF_NONSAFE       │     NONSELF_NONSAFE
                           │
                           ▼
                        NON-SAFE
```

The paper figure must represent it as a **cube/trajectory through time**:

- X axis = SELF ↔ NON-SELF
- Y axis = NON-SAFE ↔ SAFE
- Z axis = time/state index

Recommended categorical coordinates if the canonical implementation emits categorical states only:

```text
SELF      x=-1
NONSELF   x=+1
NONSAFE   y=-1
SAFE      y=+1
z = deterministic state_index 0..N-1
```

Do NOT invent continuous selfness/safety probabilities if the canonical classifier does not produce them.

For every state transition:

```text
AntiCubeStateFCO(t)
→ CAUSED_OR_EXPLAINED_BY exact FCG delta
→ AntiCubeStateFCO(t+1)
```

Map conceptual edge names to the canonical FCG schema.

ΔG* is NOT the Z axis if Z is time. Encode ΔG* as an orthogonal trajectory attribute, for example:

- edge annotation;
- marker size;
- line width;
- or a synchronized lower panel.

Do not use arbitrary colors as a scientific encoding unless the mapping is versioned and documented.

A useful derived transition table is:

```text
object_id
t
anticube_quadrant
x
y
z
fcg_root_before
fcg_root_after
fcg_delta_root
cfmo_before
cfmo_after
context_before
context_after
g_star_before
g_star_after
delta_g_star
cloud_drift
priority_before
priority_after
action_before
action_after
trigger_evidence_ids
```

---

# 5. DEFINE ESCALATION WITHOUT REQUIRING A TICKET

Do not make a human ticket mandatory.

Every rung has an escalation procedure and may terminate locally.

Use:

```text
R0 deterministic structure / exact identity / schema / graph
R1 tiny model
R2 small model
R3 medium model
R4 large model
R5 largest local or true frontier model if separately verified and preregistered
R6 human adjudication only when residual material uncertainty remains
```

At each rung choose exactly one scientific action:

```text
ACCEPT
REJECT
ABSTAIN
ESCALATE
```

Operational failure states remain separate.

Escalation object fields:

```text
case_id
rung
model_id_or_deterministic_tool
model_digest_or_tool_sha
inputs_root
outputs_root
decision
decision_reason_components
uncertainty_components
anticube_state
g_star
delta_g_star
cfmo_root
fcg_root
next_rung
claim_ceiling
```

Human `TicketFCO` is created only if a human decision is actually needed. Otherwise the cascade closes at the earliest sufficient rung.

---

# 6. MODEL INVENTORY + RUNG MAPPING

Reverify actual local runtime now:

```bash
ollama --version || true
ollama list || true
curl -sS http://127.0.0.1:11434/api/version || true
curl -sS http://127.0.0.1:11434/api/tags || true
curl -sS http://127.0.0.1:11434/api/ps || true
```

Inspect Ollarma using its current repository/approved invocation route.

Freeze each selected model:

```text
model_id
full_digest
parameter_scale_or_declared_size
quantization
runtime_version
prompt_template_sha256
system_prompt_sha256
structured_output_contract_sha256
temperature
seed_if_supported
context_length
```

Map actual models to:

```text
TINY
SMALL
MEDIUM
LARGE
LARGEST_LOCAL
FRONTIER_EXTERNAL
```

Do not call any local model a frontier model merely because it is the largest installed model.

Do not pull a model only to satisfy the diagram.

---

# 7. EXP-012 DATASET / CASE CONTRACT

Use a bounded set of real/admitted cases appropriate for confirming routing behavior without contaminating EVAL_ONLY labels.

Prefer cases already admitted to the current HydraDG/NewInML evidence universe and existing controlled contradiction/abstention fixtures.

Split before execution:

```text
DEVELOPMENT_CALIBRATION_SET
CONFIRMATORY_HELD_OUT_SET
```

Freeze IDs and SHA-256 roots before scoring.

The confirmatory set must include at minimum examples requiring:

- deterministic exact resolution;
- fuzzy lexical resolution;
- semantic equivalence;
- contradiction detection;
- supersession/current-state reasoning;
- provenance mismatch rejection;
- explicit abstention;
- contextually SELF_NONSAFE transition;
- admissible NONSELF_SAFE case;
- model disagreement/escalation.

No synthetic case may be represented as a real benchmark case.

---

# 8. ROUTING POLICY ABLATION

Implement paired policies:

```text
B0 = largest available/frozen reference invoked for every case
B1 = one large local model
B2 = size cascade only
B3 = cascade + FCG/provenance
B4 = B3 + AntiCube trajectory
B5 = B4 + ΔG*/CFMO/context-delta signals
```

If a real frontier model is unavailable:

```text
FRONTIER_REFERENCE_STATE=NOT_RUN_FRONTIER_UNAVAILABLE
```

and label B0 as `LARGEST_AVAILABLE_REFERENCE`, not frontier.

Do not silently use a cloud provider not preregistered.

---

# 9. DETERMINISTIC ROUTING RULES

The router itself must be inspectable.

Create versioned code under a suitable project path, e.g.:

```text
scripts/exp012/
  inventory_dg_scores.py
  build_case_contract.py
  route_r0_deterministic.py
  run_model_rung.py
  compute_anticube_trajectory.py
  compute_context_transition.py
  aggregate_exp012.py
  analyze_exp012_statistics.py
  validate_terminal_accounting.py
```

Use existing canonical implementations instead of duplicates where they already exist.

Never make ΔG* a hidden opaque threshold.

If EXP-012 tests a routing threshold/function, freeze the function/config before confirmatory execution and report the components.

Candidate component vector can include only actually measured fields such as:

```text
exact_identity_state
fuzzy_match_score
provenance_completeness
contradiction_state
supersession_state
abstention_state
model_agreement
model_parse_validity
AntiCube quadrant
ΔAntiCube
G*
ΔG*
Cloud Drift
priority
```

Do not invent confidence probabilities where the model does not produce calibrated probabilities.

---

# 10. EXECUTE THE CASCADE

For every case, preserve a complete rung trace.

Each rung must terminal-account the case as:

```text
ACCEPT
REJECT
ABSTAIN
ESCALATE
FAILED
TIMEOUT
BLOCKED
INVALID
```

Require:

```text
cases_entering_rung
=
accept + reject + abstain + escalate + failed + timeout + blocked + invalid
```

No missing cases.

Every model call stores raw output bytes and SHA-256, parse state, prompt root, model digest, and result classification.

Model output remains `PROBABILISTIC_MODEL_OUTPUT` until deterministic scoring promotes a derived result.

---

# 11. ΔFCG → ΔCFMO → ΔCONTEXT → ANTICUBE → ΔG* TRAJECTORY

For each material source/observation transition, construct and verify:

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
AntiCube position / movement
        ↓
ΔG* / decision pressure
        ↓
priority / routing change
        ↓
resolve / abstain / escalate
```

This chain is not allowed to be merely illustrative.

Every arrow must have either:

- a canonical FCG edge/transition object;
- or an explicit `NOT_IMPLEMENTED` / `NOT_COMPUTED` state.

Record the earliest missing dependency rather than bridging it with prose.

Create:

```text
TRAJECTORY_CASES.jsonl
TRAJECTORY_SUMMARY.json
FCG_DELTA_LEDGER.jsonl
CFMO_DELTA_LEDGER.jsonl
ANTICUBE_TRAJECTORIES.jsonl
DG_TRAJECTORIES.jsonl
ESCALATION_TRAJECTORIES.jsonl
```

---

# 12. STATISTICAL VALIDATION

Freeze `STATISTICAL_ANALYSIS_PLAN.json` before opening held-out results.

Primary joint question:

Does B5 reduce `largest/frontier/human` escalation relative to the reference while remaining within the preregistered quality/provenance/contradiction/abstention envelope?

Report:

- escalation-rate difference;
- effect size;
- 95% CI;
- exact N;
- McNemar discordant counts for paired binary endpoints;
- exact/adjusted p-values where inferentially valid;
- Holm correction for confirmatory policy family;
- bootstrap/permutation CIs for continuous/rate differences;
- power/MESI state.

If underpowered:

```text
UNDERPOWERED
```

If positive but not significant:

```text
DIRECTIONALLY_POSITIVE_NOT_STATISTICALLY_ESTABLISHED
```

Do not count repeated generations as independent cases.

---

# 13. SUCCESS / FAILURE DEFINITIONS

A positive routing result requires both:

```text
EXPENSIVE_ESCALATION_REDUCED
AND
QUALITY_SAFETY_ENVELOPE_NOT_VIOLATED
```

The quality/safety envelope must include, where scorable:

```text
false_early_accept
false_early_reject
provenance correctness
contradiction preservation
abstention correctness
terminal accounting
```

Any quality deterioration outside preregistered tolerance prevents a blanket efficiency claim.

---

# 14. FCG UPDATE

After each frozen phase:

```text
source/evidence
→ deterministic/model transform
→ derived evidence
→ rung decision
→ AntiCube state
→ context/ΔG observation
→ escalation/termination
→ aggregate result
→ bounded claim
```

Append through the actual canonical FCO/FCG writer.

Never direct-edit canonical graph roots merely to match expected output.

Record FCG root before/after and verify readback.

HydraDB may receive a projection only after canonical custody succeeds.

---

# 15. DETERMINISTIC PAPER FIGURES — NO HAND AUTHORED SCIENTIFIC VALUES

Create a new figure family, e.g.:

```text
paper/newinml2026_solo/figures/exp012_anticube/
```

and scripts under:

```text
scripts/figures/exp012/
```

Use Python/matplotlib and/or deterministic SVG primitives already approved by the project. Do not use an image generator.

Pin:

```text
python version
matplotlib version
numpy version
font family chosen from repository/system standard availability
renderer code SHA256
input receipt root
layout config SHA256
```

Do not embed dynamic scientific numbers in renderer code.

## FIGURE A — AntiCube-3D trajectory

Required geometry:

```text
X: SELF (-1) → NON-SELF (+1)
Y: NON-SAFE (-1) → SAFE (+1)
Z: state/time index
```

Draw the four quadrant labels on the base/reference plane:

```text
SELF_SAFE
NONSELF_SAFE
SELF_NONSAFE
NONSELF_NONSAFE
```

Plot one or more actual trajectories from `ANTICUBE_TRAJECTORIES.jsonl`.

For each transition, link annotations to:

```text
FCG delta ID
ΔG*
action
rung
```

If continuous X/Y values do not exist, points must occupy categorical coordinates only.

Do not jitter points for aesthetics unless the jitter is deterministic and explicitly labeled as visual offset only.

## FIGURE B — Governed state transition

Render:

```text
new source / observation
→ new atom(s)
→ ΔFCG
→ ΔCFMO
→ Δcontext
→ AntiCube movement
→ ΔG* / decision pressure
→ priority/routing change
→ resolve / abstain / escalate
```

Dynamic counts/roots/values come from receipts.

## FIGURE C — Escalation funnel

Render the observed case reduction:

```text
R0 deterministic
→ tiny
→ small
→ medium
→ large
→ largest/frontier
→ human
```

For every rung display receipt-owned:

```text
entering
resolved
abstained
escalated
failed
remaining
```

If a rung has no mapped/available model, show `NOT_RUN` rather than interpolating.

## FIGURE D — Selected FCG/CFMO trajectory

For a representative case selected by a preregistered deterministic rule, show t0..tn:

```text
FCG root / delta
CFMO state/root
AntiCube quadrant
G*
ΔG*
routing rung
action
```

Do not cherry-pick after seeing outcomes. Define representative-case selection before rendering, for example:

- first lexicographically sorted case that escalates >= 2 rungs and terminates correctly;
- otherwise first eligible case in sorted order.

---

# 16. FIGURE EVIDENCE MAP + ROUND TRIP

For every figure create:

```text
FIGURE_INPUT_MANIFEST.json
FIGURE_VISIBLE_VALUE_MAP.jsonl
FIGURE_LAYOUT.json
FIGURE_BUILD_ENV.json
FIGURE_BUILD_RECEIPT.json
FIGURE_VALIDATION_RECEIPT.json
```

Every visible dynamic number must map to:

```text
figure_element_id
visible_value
source_receipt_path
json_pointer_or_field
source_sha256
transform_code_sha256
```

Generate:

```text
.svg
.pdf
.png
```

Hash exact bytes.

Validation must rerun source-field extraction and verify all visible dynamic values.

For SVG, parse generated XML and verify expected text values from the manifest.

For PDF/PNG, byte identity is sufficient for deterministic build checks; do not OCR unless no better validation exists.

Run figure generation twice in clean temp dirs. Require exact SVG equality and, where the toolchain is deterministic, exact PDF/PNG equality. If PDF metadata prevents exact equality, canonicalize/fix metadata deterministically or explicitly report `PDF_BYTE_IDENTITY_NOT_ESTABLISHED` while preserving SVG canonical identity.

---

# 17. PAPER INTEGRATION

Do not overwrite the current paper/PDF.

Create a successor paper build.

Inspect the current NewInML manuscript and determine where the new experiment belongs.

Suggested manuscript role if evidence supports it:

```text
Methods:
Governed hierarchical escalation and AntiCube trajectory

Results:
EXP-012 routing funnel / escalation reduction

Figure:
AntiCube-3D + escalation trajectory
```

The paper may state the central thesis only at the claim ceiling supported by EXP-012.

If EXP-012 is incomplete or null, phrase accordingly.

Do not add Bio-ΔG biological quantities to the paper unless they are already admitted and directly relevant.

Run the existing deterministic manuscript build and readiness gates.

Create successor:

```text
PAPER_BUILD_RECEIPT.json
PAPER_FIGURE_BINDING_MANIFEST.json
SUBMISSION_READINESS successor receipt
```

Hash `main.tex`, figure inputs, figure artifacts, and final PDF.

---

# 18. VALIDATE ALL OPEN BLOCKS AFTER EXP-012

Re-run the predecessor gate matrix after completion.

The final matrix should clearly distinguish:

- historical red retained as historical evidence;
- successor execution green where actually repaired;
- scientific null/negative/underpowered retained;
- external blocks still blocked;
- not-run work explicitly not run.

Do NOT force Cloudflare OS, SGLang, Q38, remote provider, signing, or MMR lanes green merely to make the matrix visually complete.

If any is required by the current paper claim, either execute and verify it or lower the claim/remove the dependency.

---

# 19. TESTS / AUDIT

At minimum run relevant existing:

```text
unit tests
schema validation
FCO/FCG validation
SeedGraph readback/atom coverage checks required by this lane
EXP-012 deterministic terminal accounting
statistics tests
figure tests
paper build
link/citation validation if available
git diff --check
gitleaks
```

Do not change experimental results to make tests pass.

---

# 20. HASH / CUSTODY / GIT

Hash final artifacts with SHA-256.

Create a sorted SHA manifest for the EXP-012 subtree and figure/paper artifacts.

Append FCO/FCG custody only through canonical project paths.

Commit bounded groups with meaningful messages.

Push the execution branch.

Do not merge to main automatically.

Open/update a draft PR if repository governance allows.

---

# 21. FINAL REPORT

Return:

```text
HOST=
EXECUTION_BRANCH=
BASE_SHA=
FINAL_SHA=
PR=

PREDECESSOR_EXECUTION_BLOCKS_RESOLVED=
PREDECESSOR_SCIENTIFIC_NULL_NEGATIVE_FAILURES_RETAINED=
OPEN_BLOCKERS=

DG_DISTINCT_FORMULA_COUNT=
DG_CURRENT_HYDRADG_INFORMATION_STATE_COUNT=
DG_HISTORICAL_OR_OTHER_PROJECT_FAMILY_COUNT=
ADJACENT_CONTEXT_DIAGNOSTIC_COUNT=
DG_REGISTRY_SHA256=

ANTICUBE_3D_CONTRACT=
ANTICUBE_TRAJECTORY_CASES=
ANTICUBE_TRANSITIONS=

MODELS_USED=
MODEL_DIGESTS=
FRONTIER_STATE=

EXP012_CASES=
B0_ESCALATION_RATE=
B5_ESCALATION_RATE=
ESCALATION_RATE_DELTA=
QUALITY_ENVELOPE=
EFFECT_SIZE=
CI95=
P_VALUE=
ADJUSTED_P_VALUE=
POWER_STATE=
STATISTICAL_DECISION=

FCG_ROOT_BEFORE=
FCG_ROOT_AFTER=
FCG_DELTA_COUNT=
CFMO_DELTA_COUNT=
CONTEXT_DELTA_COUNT=

FIGURE_A_SHA256=
FIGURE_B_SHA256=
FIGURE_C_SHA256=
FIGURE_D_SHA256=
FIGURE_ROUNDTRIP=
PAPER_PDF_SHA256=

EVIDENCE_STATE=
EXPERIMENT_STATE=
FCO_STATE=
FCG_STATE=
HYDRADB_STATE=
EARLIEST_DIVERGENCE=
CLAIM_CEILING=
SIGNATURE_STATE=
MERKLE_MMR_STATE=
NEXT_SAFE_ACTION=
FINAL_REVIEW_GATE=
```

Do not summarize as success if any clause of the final scientific claim is unsupported.
