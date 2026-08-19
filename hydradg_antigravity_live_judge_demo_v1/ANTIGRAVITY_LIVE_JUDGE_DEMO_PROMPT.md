# ANTIGRAVITY — HYDRADG LIVE JUDGE DEMO + SCREENSHOT PROMPT v1

## Goal

Do not run new science.

Convert the authoritative recording worktree into a LIVE judge-facing demo of the current
FCG/HydraDB state, then capture screenshots in Chrome as if walking judges through the product.

Authoritative worktree:
`/Users/byron/projects/active/hydradg-video`

Authoritative branch:
`hack-hydra/context-iceberg-reconcile-20260819`

Primary live URL:
`http://127.0.0.1:3012/`

Do NOT use:
`/backup/hydradg.html`
as the primary recording surface.

The static fallback remains contingency evidence only.

---

## Hard boundary

Do NOT:
- run K15 or any new Daisy perturbation;
- change G* weights;
- change Cloud Drift vocabularies;
- admit new models;
- pull new datasets;
- rewrite historical receipts;
- force push;
- claim signed/Merkle states that do not exist.

Preserve all prior receipts, including the old static/video-ready receipts, as superseded historical states.

---

## Gate 0 — Re-read current truth

From the local project, resolve and hash:

- latest canonical/project FCG root;
- latest HydraDB projection receipt/root;
- current Track 03 result receipt;
- current Context Iceberg state artifact;
- current local-model status;
- current signature state;
- current Merkle/MMR state.

Local receipts outrank chat prose.

Write:
`LIVE_JUDGE_DEMO_INPUT_RECEIPT.json`

---

## Gate 1 — Require a real live Context Iceberg

The live Next.js hero must be the interactive `ContextIcebergHero`.

Required behavior:
- drag = rotate x/y/z;
- wheel = zoom;
- click node = select FCO/object;
- time scrubber = move through states;
- play/pause = animate time;
- follow-latest = return to latest state.

Required API:
`GET /api/iceberg`

The response must contain:

- `source_state = LIVE_CUSTODY_ARTIFACT` or `LIVE_CANONICAL_CUSTODY_ARTIFACT`;
- non-null `project_fcg_root`;
- non-null `hydradb_projection_root` if a real HydraDB projection receipt exists;
- actual timeline states;
- actual scene nodes/links;
- actual signature/Merkle states.

If `source_state` contains `SYNTHETIC`, STOP.

If the page served is `/backup/hydradg.html`, STOP for the primary live demo.

---

## Gate 2 — Wire the live FCG/HydraDB read path

Do not let the browser write to HydraDB.

Preferred truth flow:

canonical FCG
→ HydraDB projection
→ deterministic readback/query receipt
→ ContextIcebergState artifact
→ SHA-256
→ `/api/iceberg`
→ live interactive hero

Implement or repair a read-only projection builder that:

1. reads the current canonical FCG / HydraDB projection;
2. selects bounded judge-demo FCOs and edges;
3. confirms those FCO IDs exist in HydraDB;
4. records expected vs observed object/edge IDs;
5. writes `context_iceberg_state.json`;
6. records `project_fcg_root`;
7. records `hydradb_projection_root`;
8. records `hydradb_traceability_canary = PASS`;
9. hashes the state artifact.

Do NOT fabricate object-level drift.
If per-object drift is unavailable:
`scope = STATE_INHERITED`.

The website may read the frozen live state artifact; the browser does not need to query HydraDB directly.
The important requirement is a current deterministic HydraDB readback receipt linking the artifact to HydraDB.

---

## Gate 3 — Add a visible "LIVE FCG" status strip

At the top of the live hero, show compact truthful status:

`LIVE FCG`
`HydraDB: CONNECTED` only if the readback canary passed
`FCG root: <compact root>`
`Projection root: <compact root>`
`Source: LIVE_CUSTODY_ARTIFACT`
`Signature: <actual state>`

Do not label HydraDB connected if only a local JSON fixture is present.

---

## Gate 4 — Judge walkthrough

Make the live site support this exact judge flow.

### Shot 1 — Hero / live 4D Context Iceberg

Route:
`/`

Show:
- interactive graph;
- LIVE FCG badge;
- FCG root;
- HydraDB projection/readback state;
- Cloud Drift;
- ΔG*;
- hit/recall separately.

Perform:
- rotate;
- zoom;
- scrub time one step backward and forward.

Capture:
`01-live-context-iceberg.png`

### Shot 2 — Reference → poison → antidote

Route:
`/judge`

Show:
- reference state;
- perturbation/poison;
- restoration/antidote;
- old state retained;
- contradiction/supersession edges visible if present.

Capture:
`02-reference-poison-antidote.png`

### Shot 3 — Track 03 executed result

Route:
`/track03` or the actual Track 03 results route.

Show actual bounded claims:
- 500 cases;
- 23,867 sessions;
- 4,776 entities;
- 3,506 facts;
- historical negative/neutral retrieval result;
- no positive retrieval advantage established under the original tested treatment.

If K10/K15 later results are shown, label them as later prospective/depth experiments and do not overwrite the original negative result.

Capture:
`03-track03-results.png`

### Shot 4 — Select one FCO in the graph

Route:
`/graph`

Click one real FCO/object.

Show:
- FCO ID;
- object type;
- parent/source;
- evidence class;
- claim ceiling;
- current/superseded relationships;
- HydraDB traceability/readback receipt.

Capture:
`04-fco-live-lineage.png`

### Shot 5 — Deep provenance

Route:
`/fco/<actual-id>` or the appropriate object-inspector route.

Trace:

FCO
→ FCG relation
→ source SHA
→ transformation
→ derived evidence
→ claim ceiling

Capture:
`05-fco-provenance.png`

### Shot 6 — Local model advisory

Use the local model endpoint only if already functioning:

`GET /api/local-model/status`
`POST /api/local-model/explain`

Show:
- approved model ID;
- bounded structured explanation;
- `PROBABILISTIC_MODEL_OUTPUT_ONLY`;
- response/prompt hash;
- no scientific mutation.

Capture:
`06-local-model-advisory.png`

If this UI is not already present, do not perform a large redesign. A compact panel is sufficient.

### Shot 7 — Eligibility / custody state

Route:
`/eligibility`

Show actual:
- FCG root;
- current hash state;
- signature state;
- Merkle/MMR state;
- push state.

Capture:
`07-custody-eligibility.png`

---

## Gate 5 — Browser verification

Use a headed browser.

Preferred:
`agent-browser --headed`

Also open actual Google Chrome.

Before screenshots:
- set browser viewport consistently;
- verify no 404/500;
- verify the hero actually responds to drag/zoom/time controls;
- verify selected node changes;
- verify `/api/iceberg` is live, not synthetic.

Write:
`LIVE_BROWSER_INTERACTION_RECEIPT.json`

Required checks:
- `rotate_changed_view = true`
- `zoom_changed_view = true`
- `time_changed_state = true`
- `node_selection_changed_inspector = true`
- `source_state_live = true`
- `hydradb_traceability_canary = PASS`

---

## Gate 6 — Screenshot custody

Capture two classes when possible:

1. deterministic browser screenshots;
2. actual Google Chrome operator-view screenshots.

For every screenshot record:
- route;
- timestamp;
- page title;
- source state;
- project FCG root;
- HydraDB projection root;
- selected FCO if applicable;
- screenshot SHA-256;
- claim ceiling.

Create:
`SCREENSHOT_SHA256SUMS.txt`
`SCREENSHOT_CUSTODY_RECEIPT.json`

Append screenshot artifacts through the governed FCO/FCG writer.

Do not treat screenshots as scientific verification.

---

## Gate 7 — Supersede the static fallback receipt

Do not delete the static fallback receipt.

Add a relation equivalent to:

`STATIC_VIDEO_READY_RECEIPT`
→ `SUPERSEDED_BY`
→ `LIVE_JUDGE_DEMO_RECEIPT`

Use canonical FCG predicates after discovering the actual schema.

The static fallback remains historical evidence.

---

## Gate 8 — Final live receipt

Write:
`LIVE_JUDGE_DEMO_RECEIPT.json`

Required fields:

- branch
- commit
- local URL
- source_state
- project_fcg_root
- hydradb_projection_root
- hydradb_traceability_canary
- interactive_hero
- time_scrubber
- node_selection
- judge_route
- track03_route
- graph_route
- fco_route
- eligibility_route
- local_model_state
- screenshot_manifest_sha256
- signature_state
- merkle_state
- claim_ceiling
- video_ready_live

Claim ceiling:
`LIVE_LOCAL_FCG_HYDRADB_PRESENTATION_AND_TRACEABILITY_DEMO_ONLY`

Set:
`video_ready_live = true`
only when all interactive/readback/screenshot gates pass.

---

## Final console output

Print exactly:

LIVE_JUDGE_DEMO:
URL:
BRANCH:
COMMIT:
ICEBERG_SOURCE:
INTERACTIVE_4D:
FCG_ROOT:
HYDRADB_PROJECTION_ROOT:
HYDRADB_TRACEABILITY:
TRACK03:
LOCAL_MODEL:
SCREENSHOTS:
SCREENSHOT_MANIFEST_SHA256:
SIGNATURE:
MERKLE:
CLAIM_CEILING:
BLOCKER:
NEXT:

If all pass:
`NEXT=RECORD_LIVE_JUDGE_WALKTHROUGH`
