# HydraLamp × Immersive Commons Failure-Learning Experiment Plan

Status: PREREGISTERED / NOT YET EXECUTED

Base forensic commit: `7a737d868e3d444aa29a629219fba689425959da`

This successor lane learns from the frozen Immersive Commons submission without mutating the historical submission seal, payload, acknowledgement, or audit-domain commitment.

## Objective

Turn the post-submission forensic record into a governed experimental system:

```text
frozen submission + rubric + postmortem
        ↓
error/failure observations
        ↓
FCO candidates + FCG causal edges
        ↓
controlled counterfactual cases
        ↓
local Ollama models via Cloudflare OS
        ↓
probabilistic diagnoses
        ↓
deterministic scoring
        ↓
positive/null/negative/failed outcomes
        ↓
new failure-learning FCO/FCG state
        ↓
canonical MMR commitment only after actual construction + verify receipt
```

The purpose is not to prove a deserved hackathon score. The purpose is to test whether a governed system can identify submission failures, locate the earliest divergent dependency, and alter future submission behavior.

## Frozen source evidence

Primary source objects:

- `eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json`
- `eval/immersive_commons_submission_20260827/seal/IC_SUBMIT_RECEIPT.json`
- `eval/ic_postmortem_20260827/POSTMORTEM.md`
- `eval/ic_postmortem_20260827/EARLIEST_DIVERGENCE.json`
- `eval/ic_postmortem_20260827/ACTUAL_SUBMISSION_FREEZE.json`
- `eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json`
- `eval/ic_postmortem_20260827/IC_TOOL_SCHEMA_SNAPSHOT.json`
- `eval/ic_postmortem_20260827/MULTIMODAL_EVIDENCE_COVERAGE.json`
- `docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md`

Historical payload identity remains:

`230bd00a6d95e57d423dd26d2be18512c2041030f1b7007bdb0374a85722611d`

## Current causal finding

The forensic audit classifies:

- A rubric not retrieved early — PARTIAL
- B text form rather than agent-native evidence surface — CONFIRMED_CONTRIBUTING
- C media/evidence not in vault before submit — CONFIRMED_PRIMARY
- D provenance/origin not exposed — CONFIRMED_CONTRIBUTING
- E product optimized over submission package — CONFIRMED_CONTRIBUTING
- F package design too late — CONFIRMED
- G no 90-second judge red-team gate — CONFIRMED

Frozen earliest causal divergence: `C_media_not_in_vault`.

This is EVAL_ONLY ground truth for diagnosis experiments. It MUST NOT be shown to models in blind lanes.

## Experiment families

### E00 — Custody / leakage gate

Deterministically verify:

- exact frozen source hashes;
- no post-submit evidence leaks into blind model inputs;
- no model sees `EARLIEST_DIVERGENCE.json` in blind lanes;
- no score-estimate JSON is shown in blind lanes;
- model/config identity is pinned before each run;
- all missing/timeout/malformed outputs remain recorded.

Integrity failure stops the affected lineage.

### E01 — Blind judge reconstruction

Input: only the six submitted IC fields plus public URLs as strings. No postmortem.

Question: Can a model identify likely rubric weaknesses and infer origin ambiguity from what IC actually received?

Primary outputs:

- predicted weak rubric bands;
- predicted project-origin interpretation;
- missing evidence classes;
- proposed first corrective action.

### E02 — Origin-confusion ablation

Compare:

- T0 actual submission;
- T1 + explicit origin date;
- T2 + branch-qualified repository URL;
- T3 + `WHAT_IS_NEW_VS_PRIOR_WORK` summary;
- T4 + all origin fixes.

Primary endpoint: proportion of runs classifying HydraLamp as a distinct Aug 26–27 hackathon delta rather than generic pre-existing HydraDG/Hack Hydra work.

### E03 — Evidence-surfacing ablation

Compare:

- T0 actual `folder_id=null` representation;
- T1 + `00_START_HERE`;
- T2 + hero/contact sheet metadata;
- T3 + demo-video metadata;
- T4 + sponsor/live receipts summary;
- T5 + full curated vault manifest.

Primary endpoint: change in model-predicted evidence completeness and demo/cold-start risk.

Do not interpret model-predicted score as actual judge score.

### E04 — Agent-surface legibility ablation

Compare the submitted prose endpoint enumeration against progressively more discoverable machine surfaces:

- prose only;
- structured endpoint table;
- `/.well-known/ai-agent.json` equivalent fixture;
- `00_START_HERE` cold-agent flow;
- explicit auth → consequential action → receipt path.

Primary endpoint: whether an unbriefed model can produce the correct first three machine actions without inventing unavailable capabilities.

### E05 — Earliest-divergence diagnosis

Input: frozen postmortem evidence, excluding the answer field from `EARLIEST_DIVERGENCE.json`.

Task: rank candidates A–G and identify the earliest causal divergence.

Ground truth: C primary, D secondary, B tertiary.

Metrics:

- top-1 accuracy;
- top-3 inclusion;
- Kendall/Spearman rank agreement where defined;
- causal-evidence citation completeness;
- hallucinated-cause rate.

### E06 — Protocol repair test

Input: event/rubric/submission requirements + `HACKATHON_SUBMISSION_FCO_PROTOCOL.md`.

Task: propose a release/submission sequence.

Deterministic scorer checks whether the plan includes, before submit:

- rubric frozen;
- track declared;
- evidence requirement graph;
- origin comparison;
- media capture;
- 90-second red team;
- vault folder populated;
- `00_START_HERE`;
- branch/origin disclosure;
- video/contact sheet;
- payload hash verification;
- explicit human waiver if judge evidence remains unsurfaced.

Primary endpoint: `C_media_not_in_vault` must be prevented by the generated sequence.

### E07 — Cross-model failure-learning stability

Run the same frozen cases across the preregistered locally available Ollama model set.

No silent substitution. Missing models produce `BLOCKED_MODEL_UNAVAILABLE`.

Report:

- model-wise diagnosis accuracy;
- condition-wise repair rate;
- agreement/disagreement matrix;
- failure phenotypes;
- null/negative outcomes.

## Replication and inference settings

Stage 1 canary: one case per experiment family × every admitted model.

Stage 2 screen: all conditions × 3 replicates per admitted model.

Default generation controls are frozen by the Studio execution receipt. If Cloudflare OS/Ollama exposes deterministic seed control, record it; otherwise model outputs remain `PROBABILISTIC_MODEL_OUTPUT` even at temperature 0.

Do not selectively rerun failed or unfavorable cells to improve aggregates. Successor reruns require a new lineage and reason.

## Cloudflare OS role

Cloudflare OS is the local agent workspace/control surface, not scientific authority.

Use its local `workerd`/Wrangler mode and an Ollama model provider. The HydraDG failure-learning Agent Skill supplies the experiment contract and frozen source paths.

Cloudflare OS may:

- select an explicitly pinned local Ollama model;
- read the failure-learning skill/context;
- execute a frozen case prompt;
- return raw model output;
- expose isolated app/workflow controls.

Cloudflare OS may NOT:

- alter ground truth;
- decide PASS/FAIL without deterministic scorer evidence;
- modify the frozen submission/audit lineage;
- fabricate missing model outputs;
- silently change the selected model.

## FCO / FCG construction

This lane creates new successor analysis objects; it does not rewrite predecessor FCOs.

Conceptual relationships:

```text
SubmissionPayloadFCO
  ├─ OBSERVED_BY → ForensicAuditFCO
  ├─ EXHIBITS → EvidenceCoverageFailureFCO
  ├─ EXHIBITS → OriginLegibilityFailureFCO
  └─ PRECEDES → PlatformAckFCO

EvidenceCoverageFailureFCO
  ├─ CAUSED_BY → VaultOmissionFCO
  └─ PREVENTED_BY → SubmissionProtocolGateFCO

ModelRunFCO
  ├─ READS → ExperimentCaseFCO
  ├─ PRODUCES → ModelDiagnosisFCO
  └─ SCORED_BY → DeterministicFailureScorerFCO

DeterministicFailureScorerFCO
  └─ PRODUCES → ExperimentResultFCO
```

Canonical identity/schema binding must use project FCO/FCG authorities. If canonical schema is unavailable on the execution host, emit candidates with `FCO_STATE=PENDING_CANONICAL_BINDING` rather than inventing a competing identity.

## MMR rule

Preserve the predecessor origin commitment unchanged. It explicitly uses a simplified linear SHA-256 chain and is not a full MMR.

The failure-learning commitment must use the canonical FCO reference recipe:

- leaf: `sha256(0x00 || atom_bytes)`;
- MMR internal node: `sha256(0x01 || (left_hex || right_hex).encode())`;
- peaks are backbones;
- bag peaks right-to-left using node tag `0x01`;
- each sub-FCO contributes `sha256(0x00 || (node_id || "|" || fco_root))` to the app/analysis FCG MMR.

Do not claim `MERKLE_MMR_STATE=COMMITTED` until leaves, ordering, algorithm, peaks/root and recomputation receipt exist.

## Claim ceiling

Before model execution:

`FAILURE_LEARNING_INFRASTRUCTURE_PREREGISTERED_ONLY`

After successful blind/ablation/diagnosis runs, ceilings are derived from observed evidence. No experiment may claim the actual hackathon score or counterfactual award outcome.

## Stop conditions

Stop affected lineage on:

- source hash mismatch;
- blind-lane leakage;
- wrong model/provider/host;
- unrecorded model substitution;
- malformed/missing custody receipt;
- scorer contract drift;
- canonical FCO binding conflict;
- MMR recomputation mismatch.

Continue on valid scientific outcomes:

- correct diagnosis;
- incorrect diagnosis;
- null effect;
- negative effect;
- timeout;
- abstention;
- malformed model response, if preserved and scored as such.
