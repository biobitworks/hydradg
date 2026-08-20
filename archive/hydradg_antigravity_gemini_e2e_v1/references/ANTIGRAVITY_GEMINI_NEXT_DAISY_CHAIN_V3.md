HYDRADG / HACK HYDRA
NEXT DAISY CHAIN — LIVE CUSTODY + MATHEMATICAL DIAGNOSTICS v3.0
================================================================

MISSION
=======

Finalize the current HydraDG Daisy Train repair/integration work, then initiate the next
Daisy Chain so that:

1. every scientific/engineering gate is deterministic where promised;
2. every material human/AI/tool/artifact object is hashed and added to the canonical
   project FCO/FCG;
3. HydraDB receives a real-time QUERY PROJECTION of the evolving custody graph;
4. the local test server updates as each gate completes;
5. the UI shows current chain of custody, null hypotheses, gate state, statistical
   results, claim ceilings, and exact artifact roots;
6. the UI also shows an explicitly NON-PHYSICAL "Gibbs abstraction" plus complementary
   information-theoretic / retrieval diagnostics;
7. Ollarma models help explain why accuracy SHOULD NOT be assumed to increase, and test
   mechanistic hypotheses without contaminating the deterministic reference lane;
8. all three Hack Hydra tracks are touched through the same custody substrate;
9. one track emerges as a PROMOTION_CANDIDATE only after hard gates and empirical evidence;
10. the entire project remains resumable if Gemini/Antigravity runs out of context.

Do not optimize for a positive result.
Optimize for a mechanically auditable result.


================================================================
PRIORITY 0 — RECONCILE THE CURRENT CUSTODY CHAIN
================================================================

Before the next scientific experiment:

A. Locate and read canonical:
   FCO_FCG_CANONICAL_SPEC.md
   CLAIM_CEILINGS.md
   EVIDENCE_LEVELS.md
   FCO_SCHEMA.json
   FCG_SCHEMA.json
   SIGNING_AND_KEYS.md

B. Locate the existing HydraDG project custody store.

C. Import/bind the latest chat handoff / FCG-delta artifacts available locally if present.

D. For every substantive prior conversation capture that exists byte-for-byte locally:
   - SHA-256 exact bytes;
   - actor = HUMAN or AI;
   - bind through canonical FCO implementation;
   - append to canonical FCG;
   - connect to prior turn root.

E. If only a summary exists:
   - hash the summary that exists;
   - create PENDING_ORIGINAL_TURN_CAPTURE;
   - NEVER manufacture the original conversation hash.

F. After binding the latest custody delta:
   - canonical FCG validation;
   - append receipt;
   - exact file hash;
   - project FCG root;
   - update DAISY_STATE.json;
   - commit;
   - safe push;
   - signature handoff if private key is elsewhere.

A custody failure is a hard gate failure.


================================================================
PRIORITY 1 — REPAIR/CONFIRM EXPERIMENT SUBSTRATE
================================================================

Do not promote the earlier RAW/SG matrix until the following are resolved.

1. SOURCE FREEZE
   - inode-independent frozen source;
   - byte-identical to canonical source;
   - expected LongMemEval full500 SHA:
     d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442
   - bytes = 277383467
   - role = EVAL
   - training_allowed = false.

2. CODE FREEZE
   - inspect all changes made after prior preregistration;
   - classify each REQUIRED_FIX / OPERATIONAL_ONLY / SCIENTIFIC_VARIABLE_CHANGE / UNINTENDED;
   - freeze intentional code in a new commit;
   - create superseding preregistration if code root changed.

3. TOTAL STRUCTURAL ATOMIZATION
   Require:
     source_byte_coverage == 1.0
     logical_record_coverage == 1.0
     orphan_atom_count == 0
     every atom source_sha256 == exact downloaded source SHA
     deterministic structural root replay.

4. GOVERNED SEEDGRAPH
   - use actual SeedGraph governed import/ledger/graph route;
   - no direct SQLite ledger writes;
   - no direct SeedGraph Neo4j writes;
   - generic whole-file import is root custody only;
   - transformed treatment requires governed record/atom materialization.

5. CANONICAL FCO/FCG
   - AtomLocator is not itself automatically a canonical FCO ID;
   - bind through the project's actual canonical implementation;
   - validate every FCO/edge before append.

6. HYDRADB ISOLATION
   Preferred:
     per-replicate authorized namespace/graph scope.
   Must pass sentinel cross-visibility test.
   Fallback:
     serial ISOLATION_BY_CLEAN_RESET with RESET_RECEIPT before each run.
   Shared default without verified reset is not acceptable.


================================================================
PRIORITY 2 — BUILD THE LIVE CUSTODY EVENT BUS
================================================================

Do NOT make the UI scrape random log files.

Create one deterministic event schema, e.g. conceptually:

DaisyEvent {
  event_id
  event_sequence
  event_time_operational
  project_id
  track_id
  daisy_chain_id
  gate_id
  state
  null_hypothesis
  decision
  source_roots[]
  transform_roots[]
  artifact_roots[]
  fco_ids[]
  fcg_delta_root
  project_fcg_root
  hydradb_projection_receipt
  canonical_scientific_root
  statistics
  math_diagnostics
  claim_ceiling
  signature_state
  merkle_state
  git_commit
  push_receipt
  next_action
}

The event's SCIENTIFIC identity must exclude operational fields like timestamps/latency
unless the canonical spec says otherwise.

Write events append-only to the canonical project evidence/custody mechanism.

Every material event:
  write → fsync if available → hash → FCO/FCG bind → FCG append → HydraDB projection → UI event.

Ordering rule:
  canonical FCG append FIRST;
  HydraDB projection SECOND;
  UI notification THIRD.

The UI and HydraDB must not become the source of custody truth.


================================================================
PRIORITY 3 — HYDRADB REAL-TIME FCG PROJECTION
================================================================

HydraDB should expose the current custody chain as a queryable projection.

For every canonical FCO/FCG delta, project enough identity to trace back to custody truth:

Nodes SHOULD include where applicable:
  project
  daisy_chain
  dataset
  source_file
  record
  atom
  semantic_atom
  transform
  experiment
  replicate
  statistic
  hypothesis
  result
  artifact
  model
  human_turn
  ai_turn
  tool_result
  git_commit
  push_receipt
  signing_handoff

Each projected node should carry:
  canonical FCO ID
  source/root SHA
  evidence class
  claim ceiling
  signature state
  dataset role
  track
  gate
  projection version

Edges should reflect canonical FCG predicates.
Do NOT invent predicate names if the canonical schema already defines them.

HydraDB projection receipt must include:
  project_fcg_root before
  FCG delta root
  expected nodes/edges
  actual nodes/edges
  projection query
  projection version
  exact result hash
  traceability validation result.

After each append, run a deterministic traceability canary:
  choose a stable event/object;
  traverse HydraDB back to source SHA / canonical FCO;
  compare to custody store;
  PASS only if exact identity matches.


================================================================
PRIORITY 4 — LOCAL TEST SERVER LIVE UPDATE
================================================================

Extend the EXISTING local test server rather than creating a competing application.

First discover the existing server/API/UI structure.

Add a judge-facing "Daisy Chain / Custody" surface.

Minimum API contract, adapted to existing routes:

  GET /api/daisy/state
  GET /api/daisy/chains
  GET /api/daisy/chains/{id}
  GET /api/daisy/gates/{id}
  GET /api/custody/root
  GET /api/custody/artifacts/{sha}
  GET /api/math/current
  GET /api/tracks/status

For live update use the server's existing best-supported mechanism:
  SSE preferred for simple one-way events,
  WebSocket if already used,
  deterministic polling otherwise.

Do not add an unnecessary framework.

UI must show at minimum:

A. CURRENT GATE
   PASS / FAIL / BLOCKED / NULL_RETAINED / INCONCLUSIVE

B. CHAIN OF CUSTODY
   source SHA
   transform root
   FCO/FCG root
   HydraDB projection receipt
   result root
   Git commit
   push state
   signature state

C. NULL HYPOTHESIS
   exact preregistered H0
   test
   p-value/CI where appropriate
   decision
   claim ceiling

D. DATASET COVERAGE
   source-byte %
   logical-record %
   orphan count
   semantic abstention count

E. REPLICATE DETERMINISM
   R1/R2/R3 canonical roots
   equality gate
   first divergence if failed

F. ACCURACY / RETRIEVAL
   hit@k
   recall@k
   evidence-path coverage
   question-type breakdown
   abstention rate

G. MATHEMATICAL DIAGNOSTICS
   Gibbs abstraction
   entropy/diversity
   contradiction burden
   provenance completeness
   graph expansion
   rank displacement
   marginal utility per added context slot

H. TRACK STATUS
   Track 01
   Track 02
   Track 03
   hard-gate completion
   promotion score only after eligibility.

I. CLAIM LANGUAGE
   UI must never display VERIFIED/SIGNED/MERKLE unless backed by actual receipts.


================================================================
PRIORITY 5 — GIBBS ABSTRACTION
================================================================

This is an INFORMATION-SYSTEM ABSTRACTION, NOT PHYSICAL THERMODYNAMICS.

Do not imply joules, kcal/mol, real temperature, or literal Gibbs free energy.

Define a preregistered mathematical diagnostic:

  G* = U* - tau * S*

where:

  G* = dimensionless "governed retrieval free-cost" abstraction

  U* = normalized error/constraint cost

  S* = normalized useful-state entropy / diversity term

  tau = preregistered dimensionless tradeoff parameter

At minimum define U* transparently from bounded normalized terms such as:

  U* =
      w_error        * retrieval_error
    + w_miss         * answer_session_miss_rate
    + w_contradict   * unresolved_contradiction_rate
    + w_orphan       * orphan_rate
    + w_provenance   * (1 - provenance_completeness)
    + w_abstain      * semantic_abstention_rate
    + w_displacement * relevant_rank_displacement

Do NOT include latency unless preregistered as a separate operational objective.

Possible S*:

  S* = normalized entropy or effective diversity of useful retrieved evidence

For retrieved evidence probabilities p_i:

  H = -sum_i p_i log(p_i)

Normalize if needed:

  S* = H / log(n)

But distinguish:
  diversity of useful evidence
from:
  entropy caused by irrelevant graph expansion.

Therefore also calculate:

  relevant_evidence_entropy
  irrelevant_evidence_entropy
  evidence_precision
  graph_expansion_ratio

Prefer the decomposition:

  G* = U* - tau * S_useful + gamma * S_irrelevant

with preregistered:
  tau >= 0
  gamma >= 0.

Do not tune weights after seeing benchmark outcomes for the same experiment.
Freeze weights/config in the preregistration.

Record:
  G*_RAW_K5
  G*_RAW_K10
  G*_SG_K5
  G*_SG_K10
  delta G* for each controlled change.


================================================================
GIBBS NULLS
================================================================

Do NOT assume lower G* means higher accuracy.

Test it.

H0_G1:
  ΔG* has no association with Δaccuracy across preregistered paired conditions.

H0_G2:
  lower G* does not predict higher session recall.

H0_G3:
  graph expansion does not reduce G* after controlling for useful evidence recovered.

H0_G4:
  semantic contradiction/supersession resolution does not reduce error cost U*.

H0_G5:
  any relationship between G* and retrieval accuracy is unstable across question types.

Use:
  paired deltas
  Spearman rho where sufficient observations exist
  permutation/bootstrap CI
  question-type stratification.

If sample size is too small:
  report INCONCLUSIVE;
  do not manufacture a correlation claim.


================================================================
OTHER MATHEMATICAL DIAGNOSTICS
================================================================

Compute these separately from G* so one abstraction cannot hide a failure.

1. ACCURACY / HIT
   hit@k

2. SESSION RECALL
   |retrieved ∩ ground_truth| / |ground_truth|

3. PRECISION OF RETRIEVED EVIDENCE
   relevant retrieved / all retrieved

4. EVIDENCE-PATH COVERAGE

5. RANK DISPLACEMENT
   rank_treatment(answer) - rank_baseline(answer)

6. GRAPH EXPANSION RATIO
   graph-derived candidates / total returned candidates

7. MARGINAL K UTILITY
   [metric(K10) - metric(K5)] / 5 additional slots

8. PROVENANCE COMPLETENESS
   evidence objects with complete source path / evidence objects

9. CONTRADICTION RESOLUTION RATE
   contradictions with explicit current/superseded relation / contradictions observed

10. ABSTENTION RATE

11. STRUCTURAL COVERAGE
   source-byte coverage
   logical-record coverage

12. CUSTODY INTEGRITY
   orphan FCO count
   broken FCG edge count
   artifact-hash mismatch count

13. CONTEXT EFFICIENCY
   accuracy or recall per retrieved token/character if deterministically measurable.

14. CALIBRATION
   only if an actual confidence/probability output exists.
   Do not invent model confidence from scores that are not probabilities.


================================================================
WHEN SHOULD ACCURACY INCREASE?
================================================================

Do not display "accuracy should increase" as a fact.

Generate mechanistic predictions BEFORE treatment results.

Examples:

P1 DEPTH-LIMITED RETRIEVAL:
  If relevant evidence is ranked 6-10 under both RAW and SG:
    K10 should improve recall vs K5.
  Falsifier:
    answer-bearing sessions remain outside top10.

P2 GRAPH-DISPLACEMENT:
  If graph expansion inserts connected but irrelevant sessions above answer sessions:
    evidence-path coverage may rise while hit/recall falls.
  Prediction:
    rank displacement > 0 for answer sessions;
    irrelevant entropy/expansion rises.
  Intervention:
    ranking changes, not more semantic atoms.

P3 SEMANTIC-RESCUE:
  If lexical RAW misses paraphrased/temporally updated evidence and semantic atoms capture it:
    SG should improve specific question classes.
  Falsifier:
    SG and RAW retrieved IDs remain identical or semantic edges never influence rank.

P4 CONTRADICTION/SUPERSESSION:
  For update questions, explicit current-vs-stale relations should reduce stale retrieval.
  Prediction:
    contradiction resolution rate rises and stale-answer errors fall.
  Falsifier:
    relations exist but ranking ignores them.

P5 OVER-ATOMIZATION:
  If atomization increases candidate noise faster than useful evidence:
    provenance may improve while retrieval worsens.
  Prediction:
    provenance completeness ↑
    graph expansion ↑
    evidence precision ↓
    G* may worsen despite richer custody.

P6 CUSTODY-ONLY BENEFIT:
  SeedGraph/FCO/FCG may improve auditability with Δaccuracy = 0.
  This is a valid result.
  Show:
    provenance completeness / reproducibility gains separately from retrieval gains.

These predictions must be preregistered before a new treatment change.


================================================================
OLLARMA SCIENTIFIC DIAGNOSTIC LOOP
================================================================

Ollarma is an ADVISORY / MODEL-DERIVED layer.

Use local models for bounded diagnosis after deterministic metrics are computed.

For each failed/null/positive transition build a compact diagnostic packet containing:

  preregistered prediction
  H0
  baseline/treatment metric deltas
  G* decomposition
  rank displacement summary
  graph expansion ratio
  contradiction resolution
  provenance completeness
  question-type distribution
  first divergent/failing examples by deterministic selection
  artifact roots

Ask multiple local models independently, e.g. if currently available:
  qwen2.5-coder:7b
  deepseek-r1:14b
  qwen2.5:7b

REVERIFY actual models first.

Prompt each model to output JSON:

{
  "mechanistic_hypotheses": [
    {
      "hypothesis": "...",
      "supporting_metrics": [...],
      "counterevidence": [...],
      "next_falsification_test": "...",
      "expected_direction_if_true": {...}
    }
  ],
  "do_not_change": [...],
  "recommended_single_variable_change": "...",
  "confidence_is_model_self_report_only": true
}

Hash:
  model ID/digest
  prompt
  response
  config
  diagnostic input packet
  cache

Add each to FCG as PROBABILISTIC_MODEL_OUTPUT.

Then create a deterministic CONSENSUS COMPARISON artifact:
  agreements
  disagreements
  unsupported statements
  proposed falsification tests.

Never average model prose into a scientific result.
The science remains the deterministic experiment.


================================================================
NEXT DAISY CHAIN DESIGN
================================================================

After the repaired Track 03 reference matrix:

DAISY CHAIN N+1 must change ONE scientific variable at a time.

Candidate chain branches are chosen from deterministic evidence:

BRANCH A — K / retrieval budget
BRANCH B — semantic extractor treatment
BRANCH C — graph ranking weights
BRANCH D — contradiction/supersession traversal
BRANCH E — evidence-path penalty/bonus
BRANCH F — question-type-specific policy

Do not choose the branch because it seems most likely to win.

Choose the branch because the previous results distinguish a falsifiable mechanism.

Each branch requires:
  preregistered mechanistic hypothesis
  H0
  one changed variable
  frozen code/config
  replicate ×3
  canonical equality gate
  statistical test
  G* and independent diagnostics
  FCG update
  UI update
  Ollarma diagnostic AFTER deterministic results.


================================================================
TRACK 01 / 02 / 03 LIVE INTEGRATION
================================================================

All tracks use the same event/custody/math infrastructure.

TRACK 03:
  primary LongMemEval reference lane.

TRACK 01:
  EnterpriseRAG-Bench after rights/role gate.
  Use document/record/entity/ontology atomization.
  Dashboard shows ontology coverage, entity-link precision where labels allow,
  provenance completeness, retrieval metrics, G* decomposition.

TRACK 02:
  HydraBlast/repository dependency lane.
  Use repo/file/symbol/dependency atomization.
  Dashboard shows dependency-path recovery, chained traversal, false path rate,
  provenance, G* decomposition.

Do not process full large datasets until a small deterministic canary passes.

Touch all three tracks.

Promote only after hard gates.


================================================================
TRACK PROMOTION
================================================================

Hard gates include:
  RIGHTS_PASS
  SOURCE_FREEZE_PASS
  BYTE_COVERAGE_PASS
  LOGICAL_RECORD_COVERAGE_PASS
  NO_ORPHAN_ATOMS_PASS
  CUSTODY_COMPLETENESS_PASS
  FCO_FCG_VALIDATION_PASS
  HYDRADB_PROJECTION_PASS
  LIVE_UI_TRACEABILITY_PASS
  CANARY_PASS
  REPLICATE_DETERMINISM_PASS
  LEAKAGE_GATE_PASS
  FRESH_GOLDEN_ROUTE_PASS
  RECEIPT_COMPLETENESS_PASS

No score can rescue failed hard gates.

Only after eligibility apply the frozen rubric.

Outputs:
  NO_PROMOTED_TRACK
  TIED_CANDIDATES
  PROMOTION_CANDIDATE

Do not use VERIFIED_SUCCESS unless a separate canonical verification procedure actually
passes and evidence exists.


================================================================
LOCAL TEST SERVER RELEASE GATE
================================================================

After every stable gate:

1. persist exact scientific/custody artifacts;
2. hash artifacts;
3. append canonical FCG delta;
4. project delta to HydraDB;
5. verify traceability;
6. update API state;
7. emit live UI event;
8. run local UI/API tests;
9. capture a machine-readable local-server receipt;
10. hash receipt;
11. add receipt to FCG;
12. update DAISY_STATE / NEXT_ACTION;
13. commit;
14. safe push.

UI failure does not invalidate a completed scientific artifact.
Scientific failure does not become PASS because the UI renders.


================================================================
RESUME / TOKEN FAILURE
================================================================

Maintain:
  DAISY_STATE.json
  DAISY_NEXT_ACTION.json
  DAISY_STATUS.md

Also add:
  LIVE_SERVER_STATE.json
  MATH_STATE.json
  HYDRADB_PROJECTION_STATE.json

At each checkpoint store:
  last canonical FCG root
  last HydraDB projection receipt
  last UI event sequence
  last G* config/root
  last stats root
  last Ollarma diagnostic roots
  next exact command.

Commit/push after stable checkpoints.

If push blocked:
  create and hash git bundle/patch.


================================================================
IN-TURN HASHING + SIGNATURE
================================================================

For EVERY substantive human/AI turn:

HUMAN:
  exact captured bytes → SHA-256 → canonical FCO → FCG

AI:
  exact materialized response/instruction artifact → SHA-256 → canonical FCO → FCG

Material tools/artifacts:
  exact bytes/log → SHA-256 → canonical FCO → FCG

Turn/gate root:
  use canonical project algorithm if defined.
  otherwise label implementation-specific receipt root.

Signature:
  if canonical private key available on authorized signing machine:
    sign canonical turn/gate root;
    verify;
    append signature receipt to FCG.
  else:
    signature_state = PENDING_EXTERNAL_PRIVATE_KEY_OPERATION
    create SIGNING_HANDOFF.

Never omit signature state.

Never fabricate signature.

Never mark MERKLE_COMMITTED without actual operation.


================================================================
GATE OUTPUT
================================================================

At each gate print only:

GATE:
STATE:
H0:
SOURCE ROOT:
SCIENTIFIC ROOT:
FCG ROOT:
HYDRADB PROJECTION ROOT:
UI EVENT SEQUENCE:
GIBBS G*:
DELTA G*:
PRIMARY METRIC:
DELTA PRIMARY METRIC:
STAT TEST:
OLLARMA DIAGNOSTIC ROOTS:
CLAIM CEILING:
SIGNATURE STATE:
GIT COMMIT:
PUSH:
NEXT:

Full detail remains in local artifacts.


================================================================
START
================================================================

1. Reconcile canonical FCO/FCG custody and latest turn/artifact hashes.
2. Repair/verify freeze, code root, total atomization, SeedGraph governance, HydraDB isolation.
3. Update local server with live custody APIs/UI.
4. Implement HydraDB FCG projection receipts and traceability canary.
5. Freeze the G* specification and weights BEFORE new treatment evaluation.
6. Re-run/validate the canonical Track 03 reference matrix if required by repaired gates.
7. Populate live server/HydraDB from the canonical event stream.
8. Run deterministic mathematical diagnostics.
9. Run Ollarma multi-model diagnostic packets only after deterministic output is frozen.
10. Select ONE falsifiable next Daisy Chain variable.
11. Preregister it.
12. Execute ×3 deterministic replicates.
13. Update FCG → HydraDB → local server after every completed gate.
14. Touch Track 01 and Track 02 with small canaries.
15. Run track promotion only when hard gates pass.
16. Commit/push continuously at stable checkpoints.

DO NOT claim that accuracy should increase.
The system must explain:
  whether it increased;
  whether it stayed null;
  whether it decreased;
  the mechanistic evidence for why;
  the falsification test that should come next.
