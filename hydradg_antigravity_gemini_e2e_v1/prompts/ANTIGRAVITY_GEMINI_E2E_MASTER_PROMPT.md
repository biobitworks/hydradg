HYDRADG — ANTIGRAVITY + GEMINI END-TO-END EXECUTION PROMPT v1
==============================================================

ROLE SPLIT
----------

Antigravity:
- owns local repository reconciliation, implementation, service startup, tests, custody append,
  local appliance, and concrete file/code changes.

Gemini:
- acts as an independent review/check agent for every hard gate;
- checks claim ceilings, null handling, evidence roots, statistical interpretation, and model
  comparison;
- must not silently rewrite the active scientific treatment.

Both agents:
- use the same `DAISY_STATE.json` / `DAISY_NEXT_ACTION.json`;
- checkpoint, hash, FCG-append, commit, and push when safe;
- stop on first unresolved hard gate.

SOURCE OF TRUTH
---------------
Canonical project custody/FCO/FCG files outrank this prompt.

Locate:
FCO_FCG_CANONICAL_SPEC.md
CLAIM_CEILINGS.md
EVIDENCE_LEVELS.md
FCO_SCHEMA.json
FCG_SCHEMA.json
SIGNING_AND_KEYS.md

If missing:
BLOCKED_CANONICAL_FCO_FCG_SPEC_NOT_FOUND

STEP 0 — PRESERVE BOTH GIT LINEAGES
-----------------------------------
The user reported local scientific work at commit `9fbb501` while Release Watch also moved
the remote `hack-hydra/submission-eligible-20260819` branch.

Do NOT `reset --hard`.
Do NOT blindly `pull`.

Run:
  git status -sb
  git log --oneline --decorate -15
  git fetch origin
  git log --left-right --graph --oneline HEAD...origin/hack-hydra/submission-eligible-20260819

If divergent:
- create a reconciliation branch from local HEAD;
- preserve local scientific receipts/code;
- merge/cherry-pick Release Watch commits deliberately;
- record the reconciliation receipt and hashes.

STEP 1 — VERIFY CUSTODY + SCIENTIFIC BASE
-----------------------------------------
Verify:
- current source SHA/bytes;
- independent frozen source inode;
- total byte coverage = 1.0;
- logical record coverage = 1.0;
- orphan count = 0;
- canonical FCO/FCG validation;
- governed SeedGraph route;
- HydraDB isolation/reset mechanism;
- latest project FCG root.

Do not infer PASS from old console prose. Read receipts.

STEP 2 — CORRECT THE CURRENT ICEBERG INTERPRETATION
---------------------------------------------------
Preserve the K5→K10 observations:
  delta_G*
  delta hit@K
  delta recall@K

But write a superseding interpretation receipt:

- aggregate K5→K10 comparison is descriptive;
- H0_GA association inference remains PENDING/NOT_REJECTED until per-case paired
  contributions or multiple preregistered conditions provide an inferential sample;
- lower G* is NOT an accuracy claim.

For model comparison:
- report exact agreement directly;
- only report Cohen kappa if category variation makes kappa defined and informative;
- H0_M_DIRECTION remains PENDING_HELD_OUT_RUN_N_PLUS_1 until prospective scoring.

STEP 3 — FREEZE TWO CLOUD-DRIFT LANES
-------------------------------------
Keep Structural Cloud Drift unchanged.

Freeze a NEW Retrieval Cloud Drift vocabulary BEFORE the next scientific run.
Default proposed vocabulary is in:
  configs/retrieval_cloud_vocab.json

Compute:
  StructuralCloudDrift = 100*JSD(structural p_t || structural p_ref)
  RetrievalCloudDrift = 100*JSD(retrieval p_t || retrieval p_ref)

Hero semantics:
  outer halo = StructuralCloudDrift
  inner halo/pulse = RetrievalCloudDrift
  hue = signed delta-G*
  hit/recall = separate empirical outcomes

STEP 4 — VERIFY APPROVED OLLARMA MODELS
---------------------------------------
Current approved pair:
  M1 qwen2.5-coder:7b
  M2 qwen2.5:7b

Reverify actual local model inventory/digests.

Do not auto-download or promote a challenger in the approved lane.

Each approved model gets the exact same frozen diagnostic packet and exact same structured
output contract.

Run 3 replay-stability calls per model.

Hash:
- packet
- prompt
- raw response
- parsed response
- model ID/digest
- config
- timing/token counters

Model outputs are:
PROBABILISTIC_MODEL_OUTPUT_ONLY

STEP 5 — LOCAL PRIVATE APPLIANCE
--------------------------------
Run:
- Ollama/Ollarma HTTP on loopback only;
- Best-Use on loopback;
- HydraDB local/private;
- Next.js private-on-box by default;
- optional site-only LAN bind for judge demo.

Browser must not call port 11434 directly.
Browser -> HydraDG server route -> local model.

Verify:
  GET /api/iceberg/headline
  GET /api/iceberg/full
  GET /api/models/comparison
and, when implemented:
  GET /api/local-model/status
  POST /api/local-model/explain
  GET /api/local-model/frontier

STEP 6 — END-TO-END WEB
-----------------------
Run:
  npm ci
  npm run typecheck
  npm run build
  local start
  route/link audit
  static fallback check
  context iceberg check
  secret scan

Do not deploy simply to get a URL.

STEP 7 — PROSPECTIVE SCIENCE
----------------------------
Before any K15 execution:
- locate the frozen M1/M2 predictions from Run N;
- verify their response hashes and prediction root;
- create/freeze K15 preregistration;
- confirm K is the only scientific variable changed.

Then execute deterministic K15 replicates according to the project replication gate.

Only AFTER K15 is frozen:
- score M1 prediction;
- score M2 prediction;
- score preregistered trivial null predictor;
- run exact paired tests where sample size supports them;
- Brier/permutation/bootstrap only if valid probabilities and enough paired observations exist;
- Holm-adjust the preregistered model-comparison family.

Possible result:
NO_PROMOTED_MODEL_DIFFERENCE

Do not force significance.

STEP 8 — TINY MODEL CHALLENGER (OPTIONAL)
-----------------------------------------
qwen3:0.6b / 1.7b / 4b are NOT approved by default.

Admit one challenger at a time only after:
- model download/admission receipt;
- structured JSON validity;
- replay stability;
- unsupported-claim hard check;
- prospective evaluation.

Compare on Pareto frontier:
quality + latency + model bytes (+ actual memory if measured).

Do not claim general equivalence to larger/cloud models.

STEP 9 — FCG/HYDRADB/UI WRITEBACK ORDER
---------------------------------------
For each stable event:
  write artifact
  -> SHA-256
  -> canonical FCO/FCG append
  -> new project FCG root
  -> HydraDB projection
  -> traceability query
  -> UI state artifact
  -> local UI update
  -> tests
  -> commit
  -> safe push
  -> signature handoff

FCG truth first. HydraDB projection second. UI third.

STEP 10 — FINAL E2E RECEIPT
---------------------------
Produce:
  E2E_VERIFICATION_RECEIPT.json

Required states:
GIT_RECONCILED
CANONICAL_FCG
SOURCE_FREEZE
TOTAL_ATOMIZATION
SEEDGRAPH_GOVERNED
HYDRADB_ISOLATION
ICEBERG_MATH
STRUCTURAL_CLOUD_DRIFT
RETRIEVAL_CLOUD_DRIFT
M1_INSTALLED
M2_INSTALLED
M1_STRUCTURED_OUTPUT
M2_STRUCTURED_OUTPUT
MODEL_REPLAY_STABILITY
MODEL_PROSPECTIVE_STATE
BEST_USE
WEB_TYPECHECK
WEB_BUILD
ICEBERG_API
LOCAL_MODEL_API
STATIC_FALLBACK
SECRET_SCAN
FCG_APPEND
SIGNATURE_STATE
MERKLE_STATE

Do not write E2E_PASS if any required hard gate is BLOCKED.

RESUME SAFETY
-------------
At every stable checkpoint update:
DAISY_STATE.json
DAISY_NEXT_ACTION.json
DAISY_STATUS.md

Then commit and push if safe.

COMPACT OUTPUT
--------------
GATE:
STATE:
INPUT ROOT:
OUTPUT ROOT:
FCG ROOT:
MODEL ROOTS:
ICEBERG:
STAT DECISION:
CLAIM CEILING:
SIGNATURE:
GIT:
PUSH:
NEXT:
