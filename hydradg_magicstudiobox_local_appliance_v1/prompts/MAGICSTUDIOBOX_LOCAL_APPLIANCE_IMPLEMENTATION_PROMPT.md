HYDRADG / MAGICSTUDIOBOX LOCAL APPLIANCE IMPLEMENTATION PROMPT
===============================================================

Operate on the actual local checkout. Do NOT pull/merge until you inspect divergence first.

IMPORTANT CURRENT GIT CONDITION
The user reported a local unpushed commit:
  9fbb501
with Context Iceberg/Ollarma benchmark changes.
The remote release branch has separate Release Watch commits.
Therefore:

1. cd /Users/byron/projects/active/hydradg
2. git status -sb
3. git log --oneline --decorate -12
4. git fetch origin
5. git log --left-right --graph --oneline HEAD...origin/hack-hydra/submission-eligible-20260819

If histories diverge:
- preserve both;
- create a reconciliation branch from local HEAD;
- cherry-pick or merge the remote Release Watch commits deliberately;
- resolve conflicts by preserving the local scientific receipts AND remote read-only hero/release gates.
Never reset --hard over either lineage.

GOAL
Turn magicSTUDIObox into the actual local/private HydraDG appliance:
macOS launchd + Next.js + local HydraDG/HydraDB + Ollama loopback inference.

DO NOT USE THE DISCONTINUED macOS Server APP.

A. DISCOVERY
------------
Record:
sw_vers
uname -a
scutil --get ComputerName
scutil --get LocalHostName
command -v node npm ollama python3
node --version
npm --version
ollama --version
ollama list
launchctl print gui/$(id -u) | head
lsof -nP -iTCP:11434 -iTCP:8787 -iTCP:3010 -sTCP:LISTEN

Hash the discovery receipt and append it to the project FCG.

B. CORRECT CURRENT SCIENTIFIC CLAIMS
------------------------------------
Preserve the observed K5→K10 deltas, but amend claim language:
- one aggregate K5→K10 comparison is descriptive evidence;
- do not say H0_GA was statistically rejected merely from those two aggregate points;
- prospective / paired inference remains pending.
- if model outputs occupy only one category, use exact agreement; emit kappa only when defined/informative.

Do not delete the original receipts. Add a superseding interpretation receipt.

C. ADD RETRIEVAL CLOUD DRIFT
----------------------------
Do NOT alter the frozen Structural Cloud Drift v1 definition.

Add:
RetrievalCloudDrift = 100 × JSD(retrieved-context distribution || reference).

Freeze a retrieval bucket vocabulary BEFORE computing the next run.

Recommended first vocabulary:
[
  relevant_rank_1_5,
  relevant_rank_6_10,
  relevant_rank_gt_10,
  irrelevant_rank_1_5,
  irrelevant_rank_6_10,
  contradiction_or_supersession,
  other_graph_evidence,
  abstention
]

Compute per run and, where possible, per case.

Hero:
- outer halo = Structural Cloud Drift;
- inner halo/pulse = Retrieval Cloud Drift;
- hue = signed delta-G;
- empirical accuracy/recall remain separate.

D. LOCAL MODEL API
------------------
Keep Ollama on 127.0.0.1:11434.

The browser NEVER calls Ollama directly.

Implement server-side:
GET /api/local-model/status
POST /api/local-model/explain
GET /api/local-model/frontier

`POST /api/local-model/explain`:
- reads only frozen/validated current Iceberg and selected FCO data;
- sends bounded packet to Ollama;
- uses structured JSON schema;
- records prompt SHA, raw response SHA, model ID/digest, config, duration/token counters;
- writes model output through the governed FCO/FCG custody path;
- claim ceiling PROBABILISTIC_MODEL_OUTPUT_ONLY;
- cannot mutate scientific state.

E. MODEL LADDER
---------------
Reverify installed models.

Retain current approved references:
qwen2.5:7b
qwen2.5-coder:7b

If downloads are admitted, add tiny/small candidates one at a time:
qwen3:0.6b
qwen3:1.7b
qwen3:4b

Run the identical structured diagnostic packet ×3 per model.

Measure:
JSON validity
abstention
prospective direction correctness
Brier score if valid probabilities exist
wall-clock
load duration
prompt_eval_count/duration
eval_count/duration
tokens/sec
model bytes/digest
memory only if actually measured

Compute a Pareto frontier.
Do NOT create an arbitrary quality-cost omnibus score.

F. MACOS LOCAL SERVER
---------------------
Use a user LaunchAgent under ~/Library/LaunchAgents.

Create an appliance supervisor that:
- verifies/restarts the existing best-use stack when unhealthy;
- checks Ollama localhost health;
- runs the built Next.js site;
- keeps Ollama/HydraDB/best-use private on loopback;
- exposes ONLY the judge site on LAN when HYDRADG_APPLIANCE_BIND=0.0.0.0.

Production site:
npm ci
npm run typecheck
npm run build
npm run start -- -H "$HYDRADG_APPLIANCE_BIND" -p 3010

Default private mode:
HYDRADG_APPLIANCE_BIND=127.0.0.1

Explicit LAN demo:
HYDRADG_APPLIANCE_BIND=0.0.0.0

Display Bonjour URL using:
scutil --get LocalHostName
=> http://<LocalHostName>.local:3010

Do not expose port 11434 to LAN.

G. PRIVATE REMOTE MODE
----------------------
Document macOS Remote Login / SSH tunnel mode.

Do not require a public tunnel.

Example from another machine:
ssh -L 3010:127.0.0.1:3010 <user>@<LocalHostName>.local

Then browse:
http://127.0.0.1:3010

H. LOCAL ANALYST UX
-------------------
In the 4D hero:
- select FCO/object;
- click "Ask local analyst";
- display model name + size tier;
- display concise mechanism/falsification JSON rendered as prose;
- display model provenance root;
- label PROBABILISTIC MODEL OUTPUT;
- provide "compare tiny vs 7B" link/panel.

I. CUSTODY
----------
Every:
human turn
AI turn
install/config artifact
launchd plist
server receipt
model download/admission
model response
benchmark comparison
UI release receipt

must be hashed and appended through canonical project FCO/FCG.

Signature state must always be present.
Do not fabricate signature/Merkle state.

J. ACCEPTANCE GATES
-------------------
LOCAL_APPLIANCE_DISCOVERY=PASS
OLLAMA_LOOPBACK_ONLY=PASS
HYDRADB_LOOPBACK_ONLY=PASS
BEST_USE_LOOPBACK_ONLY=PASS
WEB_TYPECHECK=PASS
WEB_BUILD=PASS
LAUNCHAGENT_LOAD=PASS
LOCAL_SITE_HEALTH=PASS
BONJOUR_URL=PASS or PRIVATE_ON_BOX_ONLY
ICEBERG_API=PASS
LOCAL_MODEL_STATUS=PASS
LOCAL_MODEL_STRUCTURED_OUTPUT=PASS
MODEL_OUTPUT_CUSTODY=PASS
TINY_MODEL_CANARY=PASS/PENDING
PARETO_FRONTIER=COMPUTED/PENDING
SECRET_SCAN=PASS
FCG_APPEND=PASS
SIGNATURE=<actual state>

Do not call the appliance release green until all required local gates pass.

FINAL OUTPUT
------------
Print:

HOST MODE:
BONJOUR URL:
LOCAL URL:
OLLAMA:
HYDRADB:
BEST USE:
DEFAULT LOCAL ANALYST:
MODEL FRONTIER:
ICEBERG:
FCG ROOT:
SIGNATURE:
GIT BRANCH:
GIT COMMIT:
PUSH:
CLAIM CEILING:
NEXT:
