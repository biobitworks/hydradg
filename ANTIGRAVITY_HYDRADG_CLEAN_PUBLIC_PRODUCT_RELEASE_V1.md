# ANTIGRAVITY — HYDRADG CLEAN PUBLIC PRODUCT RELEASE CONTRACT v1
# Submission-critical. No new science.

## Mission

Turn HydraDG into one clean, public, understandable product with two operational environments:

1. LOCAL / REPRODUCIBLE
   magicSTUDIObox
   → local HydraDB
   → local Next.js
   → exact development / reproducibility / video path

2. PUBLIC / JUDGE-ACCESSIBLE
   Vercel Next.js
   → server-side HydraDB hosted API
   → public-safe HydraDG FCG projection
   → interactive judge experience

A static fallback must remain available from the same public site.

The result must be recoverable from GitHub alone and understandable by a judge in under five minutes.

Do not run new benchmarks, change scientific results, change scoring, change G* weights, or add new datasets.
This is release engineering, architecture cleanup, documentation, deployment, and verification.

---

# 0. NON-NEGOTIABLE TRUTH MODEL

Canonical order:

source/evidence
→ deterministic or probabilistic transformation
→ derived evidence
→ claim
→ artifact
→ FCO/FCG custody
→ HydraDB projection
→ website representation

HydraDB is a projection/query substrate.
HydraDB IDs must not replace canonical FCO identities.

Browser presentation must not promote a claim beyond the receipt that owns it.

Retain:
- positive results
- null results
- negative results
- abstentions
- superseded states

Do not rewrite historical results to make the demo look stronger.

---

# 1. PRESERVE + RECONCILE BEFORE CLEANUP

Repository:
`/Users/byron/projects/active/hydradg`

Remote:
`biobitworks/hydradg`

First run:

```bash
git fetch --all --prune
git status --short
git branch -vv
git log --graph --decorate --oneline --all -60
git worktree list
```

Identify:
- local HEAD
- local uncommitted changes
- unpushed commits
- PR #16 branch
- PR #17 branch
- `hydradg-video` worktree HEAD
- v1.3 KB/How-To/navigation changes
- latest local video/scientific receipts

Do not delete local history.

If dirty:
```bash
git add -A
git commit -m "checkpoint: preserve pre-public-release state [ci skip]"
```

Create and push a recovery branch from the exact current HEAD:

`recovery/pre-public-product-20260819-<timestamp>`

No force push.

Write:
`custody/PUBLIC_PRODUCT_PRECHECK.json`

---

# 2. CREATE ONE AUTHORITATIVE PUBLIC RELEASE BRANCH

Create:

`hack-hydra/public-product-final-20260819`

Reconcile the newest safe content from:
- `hack-hydra/submission-eligible-20260819`
- `hack-hydra/context-iceberg-reconcile-20260819`
- current local HEAD
- `hydradg-video`
- latest KB/How-To/navigation work
- latest public-safe receipts

Do not use old `hydradg_video_ready_sealed_v2` as release authority.
Preserve it only as historical evidence.

The authoritative branch must contain the latest:
- Context Iceberg
- interactive graph
- judge walkthrough
- Track 03 results
- Graph/FCO inspector
- Knowledge Base
- How-To
- Eligibility
- static fallback
- public-safe FCG snapshot
- remote HydraDB adapter
- local HydraDB adapter
- public deployment docs
- submission docs

After each bounded phase:
```bash
git add -A
git commit -m "<phase checkpoint>"
git push
```

If token budget becomes low:
STOP.
Commit.
Push.
Write `PUBLIC_PRODUCT_RESUME.md`.
Do not start another phase.

---

# 3. CLEAN REPOSITORY INFORMATION ARCHITECTURE

The repository should be understandable from the root.

Target top-level structure:

```text
README.md
ARCHITECTURE.md
SUBMISSION.md
LICENSE
apps/
  hydradg-web/
packages/
  hydradg-core/           # only if already consistent with repo architecture
adapters/
  hydradb/
  datasets/
docs/
  00_START_HERE.md
  01_PRODUCT_OVERVIEW.md
  02_ARCHITECTURE.md
  03_FCO_FCG.md
  04_HYDRADB.md
  05_CONTEXT_ICEBERG.md
  06_RESULTS.md
  07_KNOWLEDGE_BASE.md
  08_HOW_TO_USE.md
  09_LOCAL_DEVELOPMENT.md
  10_PUBLIC_DEPLOYMENT.md
  11_CLAIM_BOUNDARIES.md
  12_SUBMISSION_CHECKLIST.md
schemas/
scripts/
custody/
public-safe/
```

Adapt to actual existing repo structure rather than creating duplicate systems.

## Root README must answer in this order

### What is HydraDG?
One short paragraph.

### Why does it exist?
One short paragraph:
ordinary memory systems can overwrite or flatten state; HydraDG preserves provenance, contradiction,
supersession, null/negative outcomes and experimental state.

### What does HydraDB do?
Explain:
HydraDB is the graph/retrieval/query projection used by the product.

### What do FCO/FCG do?
Explain:
they are the canonical custody/provenance layer.

### What is the Context Iceberg?
Explain:
interactive visualization of context state; Cloud Drift and ΔG* remain separate from Hit@K/Recall@K.

### What was actually measured?
Give the bounded Track 03 result, including null/negative result.

### How do I try it?
- public Vercel URL
- judge walkthrough
- static fallback
- local developer commands

### How do I verify it?
- current release commit
- current public artifact root
- public FCG root
- HydraDB readback status
- claim ceiling

No research-history dump on the first screen.

---

# 4. EVERY MAJOR PIECE MUST SAY "WHY THIS EXISTS"

Create:
`docs/COMPONENT_MAP.md`

Required table:

| Component | What it does | Why it exists | Input | Output | Claim boundary |
|-----------|--------------|---------------|-------|--------|----------------|

Must include:
- FCO
- FCG
- SeedGraph
- HydraDB
- HydraDG graph adapter
- Context Iceberg
- Cloud Drift
- ΔG*
- Hit@K
- Recall@K
- Judge Demo
- Knowledge Base
- How-To
- Eligibility
- static fallback
- local-model advisory
- public snapshot
- screenshot/video custody

Each live page should also have a short human-readable "Why this page exists" note or accessible help affordance.

---

# 5. LOCAL ENVIRONMENT — MAGICSTUDIOBOX

The local environment is the reproducibility/dev path.

Desired flow:

```text
canonical local FCG
→ local HydraDB
→ deterministic readback
→ ContextIcebergState
→ local Next.js
```

Required local status:

```text
Environment: LOCAL
HydraDB: LOCAL CONNECTED
FCG root: ...
Projection root: ...
Traceability: PASS
```

Use the existing pinned HydraDB local integration.

Do not require the public internet for the local demo.

Required local route gate:
- `/`
- `/judge`
- `/track03`
- `/graph`
- `/knowledge`
- `/how-to`
- `/eligibility`
- `/backup/hydradg.html`
- `/api/graph/status`
- `/api/iceberg`

All must behave coherently.

Write:
`custody/LOCAL_PRODUCT_RECEIPT.json`

---

# 6. PUBLIC ENVIRONMENT — HYDRADB HOSTED API + VERCEL

Prefer the official HydraDB hosted API.

Base:
`https://api.hydradb.com`

Use official SDK or REST API.

Server-side environment variables:
- `HYDRA_DB_API_KEY`
- `HYDRADB_TENANT_ID`
- `HYDRADB_API_URL=https://api.hydradb.com`

Do not use `NEXT_PUBLIC_` for secrets.

The Vercel browser must call HydraDG server-side API routes.
Server-side routes call HydraDB.

Desired flow:

```text
Judge browser
→ Vercel Next.js
→ server-only HydraDG data access layer
→ HydraDB hosted API
→ public-safe HydraDG FCG projection
```

If official hosted HydraDB cannot support the project projection, use a separately hosted pinned HydraDB service,
but preserve the same server-side adapter interface.

Do not expose magicSTUDIObox directly as the only production backend.

---

# 7. REMOTE PUBLIC-SAFE FCG PROJECTION

Create one dedicated HydraDB tenant for the judge/public projection if authorized.

Only ingest public-safe material.

Exclude:
- secrets
- private keys
- private paths
- rights-restricted datasets not allowed for publication
- local-only human data
- internal credentials

Projection must contain enough for:
- one source → transformation → result chain
- Reference → Poison → Antidote
- contradiction/supersession
- Track 03 result
- at least one FCO detail
- KB term linkage
- claim ceiling
- current release artifact

Create deterministic projection receipt:

`custody/REMOTE_HYDRADB_PROJECTION_RECEIPT.json`

Required:
- input root
- public export root
- tenant
- expected canonical FCO IDs
- expected relation subset
- observed readback
- selected canary FCO
- graph relation readback
- project FCG root
- projection root
- traceability PASS/FAIL

Only display `HydraDB CONNECTED` publicly if this readback passes.

---

# 8. ONE DATA ACCESS LAYER, TWO BACKENDS

Implement a single server-only graph/data adapter with explicit environment mode.

Example conceptual interface:

```ts
interface HydraDGDataSource {
  status(): Promise<GraphStatus>
  getIcebergState(): Promise<ContextIcebergState>
  getGraph(): Promise<GraphDTO>
  getFCO(id: string): Promise<FCODTO>
  getRelations(id: string): Promise<RelationDTO[]>
}
```

Backends:
- `LocalHydraDBDataSource`
- `RemoteHydraDBDataSource`
- `FrozenPublicArtifactDataSource` as fallback

Resolver:

```text
REMOTE HYDRADB configured
→ RemoteHydraDBDataSource

else LOCAL HydraDB configured
→ LocalHydraDBDataSource

else public frozen artifact available
→ FrozenPublicArtifactDataSource

else
→ fail closed
```

No synthetic fixture in production.

The browser receives DTOs only, never credentials.

---

# 9. PUBLIC WEBSITE INFORMATION ARCHITECTURE

Persistent navigation:

`Overview | Judge Demo | Results | Graph | Knowledge | How to Use | Eligibility | Static Fallback`

## `/`
Answer:
- what is this?
- why should I care?
- current environment
- live/public status
- Context Iceberg
- Hit@K / Recall@K
- start walkthrough

Primary CTA:
`Start Judge Walkthrough`

## `/judge`
Show:
Reference → Poison → Antidote
and retained state.

CTA:
`See Executed Result`

## `/track03`
Show:
- 500 cases
- sessions/entities/facts
- baseline/treatment Hit@K
- Recall@K
- ΔHit@K
- ΔRecall@K
- evidence-path coverage
- actual null/negative interpretation
- claim ceiling

CTA:
`Trace One Result`

## `/graph`
Interactive 4D graph:
- rotate
- zoom
- time
- select FCO
- provenance inspector
- remote/local HydraDB status

CTA:
`Open Full FCO`

## `/knowledge`
Explain terms and link them to FCO/source/claim boundary.

## `/how-to`
Explain exact judge and operator traversal.

## `/eligibility`
Show:
- repository state
- release commit
- public artifact root
- FCG root
- HydraDB readback
- signature state
- Merkle state
- submission readiness

## `/backup/hydradg.html`
Must clearly say:
`STATIC FALLBACK — NOT LIVE HYDRADB`

CTA:
`Return to Live Demo`

---

# 10. PUBLIC/LOCAL BADGES MUST BE TRUTHFUL

Local:
```text
LOCAL LIVE
HydraDB: LOCAL CONNECTED
```

Remote:
```text
PUBLIC LIVE
HydraDB: HOSTED API CONNECTED
```

If using frozen public artifact:
```text
PUBLIC INTERACTIVE SNAPSHOT
Source: PUBLIC FROZEN CUSTODY ARTIFACT
Live HydraDB: unavailable
```

Static:
```text
STATIC FALLBACK
NOT LIVE HYDRADB
```

Never collapse these states.

---

# 11. METRICS CONTRACT

Judge-facing metrics:

- ΔG*
- Structural Cloud Drift
- Retrieval Cloud Drift if frozen/available
- Hit@K
- Recall@K
- ΔHit@K
- ΔRecall@K

Hit@K is retrieval hit rate, not end-to-end QA accuracy.

If UI says Accuracy:
`Accuracy proxy (Hit@K)`

Never imply:
- lower ΔG* causes better recall
- higher Cloud Drift means worse accuracy
- evidence-path coverage means better retrieval

Preserve the negative/null Track 03 result.

---

# 12. KNOWLEDGE BASE + HOW-TO ARE PART OF THE PRODUCT

Repository:
- `docs/KNOWLEDGE_BASE_GUIDE.md`
- `docs/HOW_TO_USE_HYDRADG.md`

Live:
- `/knowledge`
- `/how-to`

Every named project-specific term should be:
definition
→ why it matters
→ claim boundary
→ related FCO
→ source/receipt where applicable

Do not make the KB an ungoverned marketing glossary.

---

# 13. CLEAN PUBLIC GITHUB

Before making public:
- remove private credentials
- remove local absolute paths from public-facing docs where unnecessary
- ensure restricted datasets are not included
- ensure toy private key is unmistakably labeled toy/non-authenticating if retained
- run gitleaks across current branch/history scope appropriate for publication
- inspect large binary files
- verify README and license
- verify no `.env*` secrets
- verify no personal/private artifacts

Repository must be public only after this gate passes.

Write:
`custody/PUBLIC_REPOSITORY_GATE.json`

Required:
- secret_scan PASS
- rights_filter PASS
- private_material_filter PASS
- docs PASS
- public_export PASS

Then make repository public through an authorized GitHub operation.

Do not claim public until confirmed externally.

---

# 14. CI / RELEASE GATE

Create one easy command:

```bash
bash scripts/release_gate.sh
```

It should execute:
- typecheck
- tests
- production build
- public export validation
- route contract checks
- static fallback validation
- KB coverage
- secret scan
- receipt validation
- current release root
- local/public backend configuration checks

Output:

```text
RELEASE_READY=YES|NO
PUBLIC_REPO_READY=YES|NO
LOCAL_HYDRADB_READY=YES|NO
REMOTE_HYDRADB_READY=YES|NO
VERCEL_READY=YES|NO
STATIC_FALLBACK_READY=YES|NO
BLOCKER=...
```

No decorative green state.

---

# 15. VERCEL DEPLOYMENT

Deploy only `hack-hydra/public-product-final-20260819`.

Use the existing Vercel `hydradg` project.

Production must point to the current release commit.

Configure server-side HydraDB env vars in Production and Preview.

Redeploy after env changes.

Write:
`custody/VERCEL_RELEASE_RECEIPT.json`

Record:
- deployment ID
- deployment URL
- production alias
- Git branch
- Git SHA
- build status
- environment mode
- HydraDB backend mode
- graph status
- public release root

---

# 16. OFF-NETWORK JUDGE TEST

Use incognito/off-network/browser verification.

Require:
- GitHub repo accessible without account authorization
- Vercel accessible without Vercel authorization
- no LAN dependency
- no graph backend error
- all judge routes 200
- all major clicks work
- graph rotates/zooms/scrubs
- node inspector changes
- metrics visible
- KB and How-To work
- live → static → live works

Capture:
- overview
- judge
- track03
- graph
- FCO
- KB
- How-To
- eligibility
- static fallback
- return live

Hash screenshots and write:
`custody/PUBLIC_JUDGE_E2E_RECEIPT.json`

---

# 17. PUBLIC REPO MUST EXPLAIN LOCAL VS PUBLIC

Add a diagram to README/ARCHITECTURE:

```text
LOCAL / DEVELOPMENT
magicSTUDIObox
  ├─ local HydraDB
  ├─ local FCG
  └─ local Next.js
       ↓
reproducibility / video / debugging


PUBLIC / JUDGES
GitHub public repo
       ↓
Vercel Next.js
       ↓ server-side
HydraDB hosted API
       ↓
public-safe FCG projection
       ↓
interactive judge demo


EMERGENCY
Vercel/static host
       ↓
backup/hydradg.html
```

Explain why:
- local = reproducible/private-first development
- hosted HydraDB = remotely available graph/query backend
- Vercel = durable public UI
- static fallback = resilience if live backend fails
- FCO/FCG = canonical custody/claim boundary
- HydraDB = queryable projection, not canonical truth

---

# 18. FINAL SUBMISSION DOCUMENT

Create:
`SUBMISSION.md`

It should contain:
- project name
- track
- one-paragraph problem
- one-paragraph solution
- architecture
- meaningful HydraDB use
- demo path
- measured results
- claim boundary
- public GitHub URL
- public Vercel URL
- video URL placeholder
- team
- originality/reuse disclosure
- current release SHA/root

No unsupported performance claim.

---

# 19. TOKEN / INTERRUPTION SAFETY

After every completed phase:
1. commit
2. push
3. update `custody/PUBLIC_PRODUCT_CHECKPOINT.json`

If stopping early, create:
`PUBLIC_PRODUCT_RESUME.md`

with:

```text
LAST_COMPLETED_PHASE=
CURRENT_BRANCH=
LOCAL_HEAD=
REMOTE_HEAD=
WORKTREE_CLEAN=
PUBLIC_REPO_STATE=
LOCAL_HYDRADB=
REMOTE_HYDRADB=
REMOTE_TENANT=
VERCEL_DEPLOYMENT=
PUBLIC_URL=
LAST_PASSING_GATE=
CURRENT_BLOCKER=
NEXT_FILE=
NEXT_COMMAND=
```

Push it before stopping.

No force push.
No unpushed final work.

---

# 20. DEFINITION OF DONE

Do not report completion until all are true:

```text
AUTHORITATIVE_BRANCH_PUSHED      PASS
REMOTE_SYNC                      PASS

README_CLEAR                     PASS
COMPONENT_MAP                    PASS
ARCHITECTURE_DOC                 PASS
SUBMISSION_DOC                   PASS

LOCAL_HYDRADB                    PASS
LOCAL_TRACEABILITY               PASS

REMOTE_HYDRADB                   PASS
REMOTE_TRACEABILITY              PASS

VERCEL_CURRENT_RELEASE           PASS
PUBLIC_GRAPH                     PASS

/                                200
/judge                           200
/track03                         200
/graph                           200
/knowledge                       200
/how-to                          200
/eligibility                     200
/backup/hydradg.html             200

INTERACTIVE_4D                   PASS
HIT_RECALL_VISIBLE               PASS
LIVE_STATIC_TRAVERSAL            PASS

PUBLIC_GITHUB                    PASS
PUBLIC_SECURITY_GATE             PASS

STATIC_FALLBACK                  PASS
OFF_NETWORK_E2E                  PASS
SCREENSHOT_CUSTODY               PASS
```

Final output:

```text
PUBLIC_PRODUCT:
BRANCH:
COMMIT:
GITHUB:
GITHUB_PUBLIC:
VERCEL:
VERCEL_COMMIT:
LOCAL_HYDRADB:
REMOTE_HYDRADB:
REMOTE_TENANT:
FCG_ROOT:
REMOTE_PROJECTION_ROOT:
TRACEABILITY:
INTERACTIVE_4D:
HIT_AT_K:
RECALL_AT_K:
KB:
HOW_TO:
STATIC_FALLBACK:
OFF_NETWORK_E2E:
SECURITY:
SUBMISSION_DOC:
SIGNATURE:
MERKLE:
BLOCKER:
NEXT:
```

Success:
`NEXT=RECORD_VIDEO_AND_SUBMIT`

Claim ceiling:
`PUBLIC_PRODUCT_DEPLOYMENT_AND_HYDRADB_TRACEABILITY_ONLY`
