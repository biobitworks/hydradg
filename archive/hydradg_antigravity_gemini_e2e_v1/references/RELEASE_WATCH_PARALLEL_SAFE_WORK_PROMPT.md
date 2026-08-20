HYDRADG RELEASE WATCH — PARALLEL SAFE WORK LANE v1
===================================================

MISSION

While Gemini/Antigravity owns the active scientific Daisy Chain, work only on tasks that
do not mutate, reinterpret, or contaminate the frozen experiment treatment.

Release Watch owns:
  evidence preservation
  public-safe export
  release/security validation
  read-only/local-server UI
  live custody visualization from already-written canonical receipts
  dataset registry presentation
  documentation/demo/submission preparation
  deployment preparation

Release Watch does NOT own:
  changing retrieval algorithms
  changing atomization semantics
  changing Gibbs weights
  rerunning active scientific cells against shared state
  editing frozen preregistration
  changing SeedGraph treatment
  promoting scientific claims

If a task would alter the active scientific code/config/data root, STOP and leave it to
the Daisy execution lane.


CURRENT MVP DATA / EVIDENCE TO PRESENT
======================================

Reverify local paths and manifests before use.

1. LONGMEMEVAL CLEANED / TRACK 03
   Expected full500 source:
     cases: 500
     bytes: 277383467
     source SHA-256:
       d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442
   Role:
     EVAL_ONLY
     training_allowed=false

   Existing historical/recomputed benchmark artifacts may include:
     23,867 sessions
     4,776 entities
     3,506 facts
     K5/K10 retrieval statistics
     30 abstention cases
     historical negative/null graph retrieval result

   DO NOT display "verified improvement".
   Display exact claim ceilings and current repaired-gate status.

2. ENTERPRISERAG-BENCH / TRACK 01 CANDIDATE
   Supplied acquisition snapshot:
     revision:
       69916e31c68aa5963c00248fd7f0bc12d04fd235
     manifest SHA-256:
       a27d470d8a5d654cd5c56714e0992781c7b8b41b9669d0dd37521bb9f1262a71
   State:
     DOWNLOADED
   Use:
     dataset registry and Track 01 canary readiness display.
   Do not claim evaluated until real canary receipt exists.

3. SALESFORCE HERB
   Supplied acquisition snapshot:
     revision:
       a00bca08f9118e482e6de9951fdcb654fbed5343
     manifest SHA-256:
       2472e14937818a35659a346c24bd2bd0348164f9e370c8f33b984ffd2c243b84
   Rights:
     current supplied project status says CC-BY-NC-4.0.
   Public release:
     exclude dataset contents unless rights policy explicitly allows.
   Registry metadata may state AVAILABLE / RIGHTS-GATED.

4. LONGMEMEVAL-V2 CORE
   Supplied acquisition snapshot:
     revision:
       f152293e235517d504809563c833d7190b8c713b
     manifest SHA-256:
       af7b570bd50061b2c0a7db07ee88e9bdba07b65e02d8d025b0a86db39e90d0ad
   State:
     DOWNLOADED
   Use:
     future extension / dataset registry.
   Do not mix into frozen LongMemEval-S experiment.

5. BEAM
   Supplied acquisition snapshot:
     revision:
       3205395e897e7318c7b094ef4e6047b9b82dbb03
     manifest SHA-256:
       3c7f329245e3aacaf226d52bd32494fd1bd3210c0420ca636c4c27f14b2adf77
   State:
     DOWNLOADED
   BEAM-10M:
     DEFERRED
   Use:
     registry / future adapter readiness only until role/null/evaluator is frozen.

6. TRACK 02 REPOSITORY / HYDRABLAST
   Use the actual repo/code source and existing HydraBlast canary lane.
   Release Watch may prepare UI/contracts/scripts.
   Do not execute if it shares mutable HydraDB state with active Daisy work.

7. CUSTODY / FCO / FCG
   Existing project artifacts include:
     preregistration
     dataset manifests
     matrix/result receipts
     turn custody
     FCG deltas
     signing handoffs
     total atomization reference package
     hash manifests

   UI must distinguish:
     HASHED
     CANONICAL_FCG_APPENDED
     SIGNED
     MERKLE_COMMITTED
     VERIFIED
   Never collapse these into one green badge.

8. LOCAL MODEL / OLLARMA
   Available model list must be reverified locally.
   Release Watch can display model provenance/readiness.
   Do not generate new scientific interpretation in the release lane.


MVP PRODUCT STORY
=================

The MVP should demonstrate:

  messy / longitudinal / code evidence
        ↓
  governed intake
        ↓
  FCO / FCG custody
        ↓
  HydraDB query projection
        ↓
  deterministic experiment gates
        ↓
  null/negative/positive result retained
        ↓
  live chain-of-custody UI

The strongest existing data story is Track 03.

Track 01 and Track 02 should appear as small canary/adaptation surfaces, not as equal
full-scale benchmarks unless their real receipts pass.


PARALLEL TASKS RELEASE WATCH MAY FINISH NOW
===========================================

A. EVIDENCE PRESERVATION
------------------------
If untracked evidence exists:
  copy it outside repo;
  create exact SHA-256 manifest;
  verify source/destination byte identity;
  only then remove or ignore the repo copy according to policy.

Produce:
  EVIDENCE_PRESERVATION_RECEIPT.json

Do not claim content validation from byte-copy validation.


B. PUBLIC-SAFE DATASET REGISTRY
-------------------------------
Build a machine-readable registry and UI table containing only:

  dataset_id
  track
  acquired state
  exact revision
  manifest SHA
  role
  rights state
  training_allowed
  evaluation_allowed
  atomization state
  FCO/FCG state
  HydraDB state
  experiment state
  claim ceiling

Use PASS/PENDING/BLOCKED, never inferred success.

HERB must visibly show RIGHTS-GATED.


C. READ-ONLY LIVE CUSTODY UI
----------------------------
Build the local test-server surface that reads existing stable artifacts/receipts.

Preferred source order:
  canonical custody store
  → canonical FCG
  → HydraDB projection
  → UI

Do not let UI become custody truth.

Build pages/components for:

1. Daisy Chain status
2. Dataset registry
3. Track 01 / 02 / 03 status
4. FCG lineage
5. artifact/hash explorer
6. null-hypothesis/statistics panel
7. total-atomization coverage
8. signature/Merkle state
9. Gibbs/math panel
10. next action / resume state

If active Daisy artifacts are not yet canonical:
  display PENDING / INCONCLUSIVE.
Do not fabricate example scientific results in production UI.


D. LIVE API CONTRACT
--------------------
Using existing server architecture, implement/read-test equivalent routes:

  /api/daisy/state
  /api/datasets
  /api/tracks
  /api/custody/root
  /api/custody/artifacts/:sha
  /api/math/current
  /api/release/status

If server already uses other route conventions, conform to them.

All APIs must be read-only against active scientific artifacts unless Release Watch owns
the specific release receipt being written.


E. GIBBS / MATH UI — DISPLAY ONLY
---------------------------------
Build UI/schema support for:

  G*
  U*
  S_useful
  S_irrelevant
  delta G*
  hit@k
  recall@k
  evidence precision
  evidence-path coverage
  rank displacement
  graph expansion
  provenance completeness
  contradiction resolution
  abstention rate
  structural coverage

Do NOT choose or change Gibbs weights in Release Watch.
Those are scientific preregistration state owned by Daisy execution.

If no frozen G* config exists:
  UI shows:
    GIBBS_CONFIG=PENDING
rather than inventing values.


F. PUBLIC EXPORT BUILDER
------------------------
Build deterministic public-safe export from stable project receipts.

Exclude:
  private keys
  auth tokens
  local absolute paths if not appropriate
  private datasets
  rights-restricted HERB contents
  giant transient logs
  unverified scientific labels

Include:
  public code
  schemas
  claim ceilings
  artifact hashes
  public receipts
  dataset metadata permitted for redistribution
  reproducibility instructions
  null/negative findings

Produce:
  PUBLIC_EXPORT_MANIFEST.json
  PUBLIC_EXPORT_POLICY_REPORT.json


G. WEB BUILD / ROUTE AUDIT
--------------------------
Complete:

  local web build
  start local web server
  route smoke tests
  internal link audit
  website-as-FCG link validation
  mobile/desktop sanity check if existing tooling supports it

Do not change scientific results to make UI tests pass.


H. SECURITY
-----------
Run/install according to local policy:
  gitleaks

Also inspect:
  tracked secrets
  tokens
  private keys
  local dataset leakage
  accidental HERB content
  internal absolute paths in public export

Produce:
  SECURITY_GATE_RECEIPT.json

A tool PASS is security-scan evidence, not proof of total security.


I. RELEASE RECEIPT
------------------
Build/finalize the release receipt writer.

Receipt should summarize:
  Git commit
  public export root
  dataset registry root
  canonical FCG root used
  HydraDB projection root used
  local web build result
  link audit
  secret scan
  track states
  signature states
  outstanding blockers
  claim ceiling

Do not mark RELEASE_BATCH_COMPLETE until required gates actually pass.


J. VERCEL PREPARATION
---------------------
Release Watch may finish:
  build compatibility
  environment-variable inventory
  deployment configuration
  public route validation
  public-safe static data adapter

Do NOT deploy stale or scientifically invalid state merely to produce a URL.

Deployment only after:
  local web green
  public export green
  security green
  current canonical release root identified.


K. DEMO / SUBMISSION MATERIAL
-----------------------------
Finish:
  VIDEO_TODO.md
  SUBMISSION_FORM_TODO.md
  demo script
  judge walkthrough
  architecture diagram text
  exact claim language
  known limitations
  null-result explanation

Do not mark human recording/submission complete.


L. TESTS
--------
Release Watch can add deterministic tests for:
  dataset registry schema
  missing receipt → PENDING
  rights-gated dataset exclusion
  hash links
  FCG traceability display
  signature state
  null result rendering
  no fake VERIFIED badge
  public-path scrub
  link audit
  local API read-only behavior


DO NOT RUN IN PARALLEL
======================

While the active Daisy scientific lane is working, do not:

  rerun RAW/SG matrix
  mutate HydraDB experiment namespaces
  reset shared HydraDB state
  change SeedGraph parser
  change FCO/FCG canonical mapping
  change G* weights
  run full Track 01/02 canaries using the same mutable backend
  update experimental algorithm/ranking
  change preregistration
  perform model training

You may BUILD these commands/interfaces, but execution waits for an explicit stable
handoff from the scientific lane.


RELEASE-WATCH DEFINITION OF DONE WHILE WAITING
==============================================

Target state:

  EVIDENCE PRESERVATION          PASS
  DATASET REGISTRY               PASS
  PUBLIC EXPORT BUILDER          PASS
  WEB BUILD                      PASS
  READ-ONLY CUSTODY UI           PASS
  DATASET/TRACK UI               PASS
  MATH/GIBBS DISPLAY CONTRACT    PASS
  INTERNAL LINKS                 PASS
  WEBSITE-AS-FCG                 PASS
  SECRET SCAN                    PASS
  RELEASE RECEIPT WRITER         PASS
  VERCEL PREP                    PASS
  VIDEO/SUBMISSION DOCS          READY
  ACTIVE SCIENTIFIC GATES        PENDING / EXTERNAL TO RELEASE WATCH

At the end report:

ITEM | STATE | ARTIFACT SHA | FCG/CUSTODY STATE | CLAIM CEILING | BLOCKER/NEXT

Hash all material outputs.
Append Release Watch's own human/AI/tool/artifact turns to canonical project FCG.
If signature key is unavailable:
  PENDING_EXTERNAL_PRIVATE_KEY_OPERATION
  + signing handoff.
