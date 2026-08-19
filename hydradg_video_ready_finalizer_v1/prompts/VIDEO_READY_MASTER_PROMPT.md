HYDRADG VIDEO-READY FINALIZATION PROMPT v1
==========================================

GOAL
----
Stop adding scientific variables. Convert the already-executed local E2E result into a
recordable, judge-facing local-private demo on magicSTUDIObox.

Final output:
VIDEO_READY=YES
or one precise BLOCKER.

DO NOT
------
- run another Daisy perturbation;
- change G* weights;
- change Structural/Retrieval Cloud Drift vocabularies;
- change approved model identities;
- hard-reset Git;
- force-push;
- wait for GitHub Actions;
- wait for Ed25519 signature before recording;
- claim verified scientific success or model superiority.

CURRENT SUPPLIED EXECUTION CLAIMS — REVERIFY FROM LOCAL RECEIPTS
---------------------------------------------------------------
- E2E master gate reported PASS.
- Git commit reported a614333.
- K15 reported: G*=-0.3448, hit@15=0.9851, recall@15=0.9582.
- M1 qwen2.5-coder:7b and M2 qwen2.5:7b both predicted lower G* prospectively.
- Decision: NO_PROMOTED_MODEL_DIFFERENCE.
- Best-Use is reported live on 127.0.0.1:8787.
- signature pending; push deferred.

Local receipts outrank this prose.

GATE V0 — RE-READ RECEIPTS
--------------------------
Discover and hash the actual current:
- E2E_VERIFICATION_RECEIPT.json
- ICEBERG_INTERPRETATION_SUPERSEDING.json
- model comparison receipt
- K15 result / prediction-outcome receipt
- latest project FCG root
- HydraDB projection receipt

Confirm exact approved model IDs/digests.
Confirm signature state.

GATE V1 — BUILD REAL ICEBERG STATE
----------------------------------
The homepage MUST NOT show the synthetic fixture during recording.

Locate:
schemas/context_iceberg_state.schema.json

Generate from actual receipts/FCG/HydraDB projection:
~/.local/share/hydradg-best-use/eval/e2e-20260819/context_iceberg_state.json

Require:
source_state = LIVE_CUSTODY_ARTIFACT
project_fcg_root = actual root
timeline = actual observed states
scene nodes = actual FCO/receipt-derived objects
signature_state = actual state
merkle_state = actual state

Do not fabricate per-object drift.
If node-specific drift was not computed, inherit state-level drift and set:
scope = STATE_INHERITED

Preserve frozen definitions:
StructuralCloudDrift remains unchanged.
RetrievalCloudDrift remains unchanged.
Do not invent nonzero drift for visual effect.

GATE V2 — WIRE WEB TO LIVE ARTIFACT
-----------------------------------
Export:
HYDRADG_ICEBERG_STATE_PATH=<actual context_iceberg_state.json>

Confirm web `/api/iceberg` returns:
source_state = LIVE_CUSTODY_ARTIFACT

Synthetic fallback => VIDEO_READY=NO.

GATE V3 — WEB BUILD
-------------------
cd /Users/byron/projects/active/hydradg/apps/hydradg-web
npm ci
npm run typecheck
npm run build

All PASS.

GATE V4 — START LOCAL PRIVATE SITE
----------------------------------
Keep:
Ollama raw API = 127.0.0.1 only
Best-Use = 127.0.0.1:8787
HydraDB = local/private

Start Next.js:
127.0.0.1:3010

No public deployment required for recording.

GATE V5 — LOCAL MODEL SMOKE
---------------------------
Verify M1 and M2 installed.

POST:
http://127.0.0.1:8787/api/local-model/explain

Require:
HTTP 200
approved model identity
structured output
prompt/response hashes
claim ceiling = PROBABILISTIC_MODEL_OUTPUT_ONLY
no scientific-state mutation

Do not add another model before the video.

GATE V6 — VIDEO ROUTES
----------------------
Require HTTP 200:
/
 /judge
 /graph
 /evidence
 /api/iceberg

Also verify:
Best-Use /api/local-model/status
Best-Use /api/models/comparison

GATE V7 — FREEZE VIDEO RECEIPT
------------------------------
Write:
~/.local/share/hydradg-best-use/eval/e2e-20260819/VIDEO_READY_RECEIPT.json

Include:
git branch/commit
working tree state
E2E receipt SHA
Iceberg state SHA
project FCG root
HydraDB projection root
approved model IDs/digests
K15 result root
site URL
route checks
local-model check
source_state
claim ceiling
signature state
Merkle state
push state
video_ready

claim_ceiling:
LOCAL_PRIVATE_END_TO_END_DEMO_ONLY

Set video_ready=true only after all required video gates PASS.

Hash the receipt.
Append through canonical FCO/FCG writer if available.
If FCG append fails, report blocker. Never fabricate append.

GATE V8 — VIDEO CLAIM LANGUAGE
------------------------------
ALLOWED:
- HydraDG is running locally on this Mac.
- The local benchmark/API pipeline executed.
- The system preserves positive, null and negative evidence.
- K15 produced the values in the actual frozen receipt.
- Both approved local models predicted the tested direction if the frozen receipts establish that.
- Neither model was promoted over the other.
- Cloud Drift is a bounded information-distribution diagnostic.
- delta-G* is a dimensionless information-system abstraction.
- model explanation is probabilistic output.
- signature is pending, if still pending.

NOT ALLOWED:
- lower G* causes better accuracy;
- statistically proven model superiority;
- independently verified;
- signed without signature receipt;
- Merkle committed without actual receipt.

FINAL OUTPUT
------------
VIDEO_READY:
LOCAL SITE:
ICEBERG SOURCE:
K15:
M1:
M2:
MODEL DECISION:
FCG ROOT:
VIDEO RECEIPT:
VIDEO RECEIPT SHA256:
SIGNATURE:
PUSH:
BLOCKER:
NEXT:

If VIDEO_READY=YES:
NEXT=RECORD_VIDEO_NOW
