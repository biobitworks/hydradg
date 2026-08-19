# HydraDG — graph-native state with verifiable evidence paths

Hack Hydra 2026 submission workspace. HydraDG uses HydraDB to represent changing context as typed graph state, preserve the dependencies behind an answer, and make perturbation/recovery mechanically inspectable.

## Build-window eligibility

Hack Hydra requires participant project work to start on or after **August 12, 2026**. The release branch applies that as a hard gate:

- participant-authored implementation written before August 12 is excluded from the submission;
- pre-existing libraries, frameworks, templates, APIs and public datasets are treated as upstream dependencies/reference inputs and attributed separately;
- repository visible history begins after August 12, but content-origin auditing is still treated separately from commit timestamps.

See `docs/HACK_HYDRA_ELIGIBILITY_AUDIT_20260819.md`.

## Three distinct track projects

### Track 01 — HydraOntology

**Problem:** enterprise context + ontology.

Graph question: which people, records, claims and events resolve to the same entity, which evidence is current, and what contradicts or supersedes it?

Primary data:
- `onyx-dot-app/EnterpriseRAG-Bench` — MIT
- `Salesforce/HERB` — CC-BY-NC-4.0; dataset bytes remain outside the public repo by default

Hack-Hydra implementation includes a fresh HydraDB identity-resolution canary before real benchmark ingestion.

Web: `/track01`

### Track 02A — HydraBlast

**Chosen option:** supply-chain blast radius.

Graph question: given an affected package version, what services are exposed through the exact resolved dependency graph, and does a patch remove every vulnerable path?

Planned real evidence sources:
- npm package/version metadata
- deps.dev resolved dependency graphs
- OSV / GitHub Advisory Database
- real lockfiles

The first fresh canary compares HydraDB reverse dependency traversal against a deterministic Python closure across reference → poison → partial repair → full repair.

Web: `/track02`

### Track 03 — HydraMemory

**Problem:** memory + context retrieval.

Graph question: after long histories and updates, which fact is current, what did it supersede, what contradicts it, and which source/session supports the result?

Primary executed dataset:
- `xiaowu0162/longmemeval-cleaned` — MIT

Additional planned stress data:
- `xiaowu0162/longmemeval-v2` — Apache-2.0
- `Mohammadta/BEAM` — CC-BY-SA-4.0
- `Mohammadta/BEAM-10M` — optional full tier

Web: `/track03`

## Why HydraDB is load-bearing

A flat retrieval system can return text. HydraDG needs graph state for operations whose semantics are relational:

```text
Session ─NEXT/PREV→ Session
Session ─ASSERTS→ Fact
Fact ─DERIVED_FROM→ Session
Fact ─ABOUT→ Entity
Fact ─SUPERSEDED_BY→ Fact
Fact ─CONTRADICTS→ Fact
```

Track 02 similarly requires reverse transitive dependency traversal, and Track 01 requires explicit entity-resolution/provenance relationships.

Without HydraDB, the project loses the traversable relationship state used to reconstruct chronology, provenance, current state, contradiction and blast radius. The benchmark ablations deliberately retain a flat baseline so this claim is testable rather than assumed.

## Current executed Track 03 evidence

Pinned HydraDB revision:

```text
6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219
```

LongMemEval-S full500 run:
- 500 total cases
- 470 retrieval-scored cases
- 23,867 Session nodes
- 4,776 Entity nodes
- 3,506 Fact nodes
- 2,457 `SUPERSEDED_BY` edges
- 4,914 `CONTRADICTS` edges

The paired full500 analysis returned:

```text
B = NO_POSITIVE_HIT_RATE_SIGNAL
C = NO_POSITIVE_HIT_RATE_SIGNAL
D = NO_POSITIVE_HIT_RATE_SIGNAL
```

This negative/neutral result is retained. **HydraDG does not claim that graph expansion improved retrieval hit rate under this tested configuration.**

Evidence class:

```text
RECOMPUTED_LIVE_HYDRADB_RETRIEVAL_ABLATION
```

Claim ceiling:

```text
LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA
```

SHA-256 identities:

```text
LongMemEval source
d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442

result
bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324

statistics
8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc

receipt
21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365
```

A digest identifies retained bytes/object content; it is not scientific verification by itself.

## Local demo architecture

```text
Browser
  ↓
HydraDG Judge Lab · Next.js
127.0.0.1:3000/judge
  ↓ /api/live
Best Use local server
127.0.0.1:8787
  ↓
pinned local HydraDB
127.0.0.1:8443
```

The public Vercel site is presentation/evidence navigation. Local-only live graph controls fail closed when the localhost Best Use server is unavailable.

## Run the local Track 03 surface

On the Hack Hydra release branch:

```bash
cd /Users/byron/projects/active/hydradg
git fetch origin
git switch hack-hydra/submission-eligible-20260819
git pull --ff-only origin hack-hydra/submission-eligible-20260819
bash HydraDG_DaisyTrain_v0.3.7/scripts/bootstrap_best_use_magicstudio.sh start
```

Then run the web app:

```bash
cd apps/hydradg-web
npm ci
npm run typecheck
npm run build
npm run start -- -p 3000
```

Open:

```text
http://127.0.0.1:3000/judge
```

## Pull Track 01 + Track 03 datasets

Large dataset bytes remain outside Git by default. The acquisition script resolves the exact Hugging Face revision and creates per-file SHA-256 manifests and a bounded pull receipt.

Core tier:

```bash
cd /Users/byron/projects/active/hydradg
bash HydraDG_DaisyTrain_v0.3.7/scripts/pull_track01_track03_datasets.sh --track all --tier core
```

Default data root:

```text
~/.local/share/hydradg-datasets
```

A script existing in Git is **not** evidence that the dataset was downloaded. Dataset state is promoted only after a local pull receipt exists.

## Judge routes

- `/` — submission overview; website FCG entry point
- `/judge` — deterministic control, live local data and hosted-API conformance lanes
- `/graph` — interactive spatial + time FCG projection
- `/knowledge` — terminology → how-to → graph query → source matrix
- `/evidence` — executed/failed/pending evidence ledger
- `/track01` — HydraOntology
- `/track02` — HydraBlast
- `/track03` — HydraMemory
- `/eligibility` — Hack Hydra custody/release boundaries
- `/api/site-fcg` — application-level website FCG JSON
- `/fco/<fco:id>` — deterministic FCO object/edge inspector

## Website-as-FCO/FCG

The website is represented as an application-level custody graph:

```text
source → evidence → transformation → claim → artifact
```

`apps/hydradg-web/lib/siteFcg.ts` creates content-addressed `SiteSection` FCOs for major routes and explicit FCG relationships among them. `/api/site-fcg` exposes the graph.

This is **not** a live HydraDB Merkle commitment, author signature, or proof that page claims are correct.

## COMPUTE template attribution

The user supplied the exact source archive for:

`COMPUTE — The Platform to Build & Ship AI Agents`

Observed supplied-archive SHA-256:

```text
b363081debc07af517cea73ed53b682b840a9e4c52e6658e7d35f18ca9922e4c
```

HydraDG ports its presentation grammar—floating navigation, monochrome editorial hierarchy, numbered sections, metrics grids and process layout—without copying its unrelated product claims or requiring its full UI dependency tree.

See `apps/hydradg-web/COMPUTE_TEMPLATE_INTEGRATION.md`.

## FCO/FCG claim discipline

HydraDG keeps these properties separate:

- hash / content identity
- provenance / dependency route
- deterministic replay
- correctness
- classification/admission
- signature
- Merkle/MMR commitment
- independent replication

Current live HydraDB results remain:

```text
SIGNATURE_STATE=NOT_SIGNED
MERKLE_STATE=NOT_MERKLE_COMMITTED
```

unless an explicit later operation establishes otherwise.

## Security

- no private signing key belongs in GitHub or Vercel;
- local HydraDB bearer tokens stay local;
- hosted API credentials are environment variables and are never returned to the browser;
- local-only proxying is restricted to loopback unless explicitly overridden;
- failed and negative executions are retained rather than rewritten as passes.

## License

Original Hack Hydra HydraDG implementation in this repository is released under the MIT License; see `LICENSE`.

Third-party software, upstream repositories, datasets and templates remain governed by their own licenses/terms and are not relicensed by the HydraDG MIT file.

## Status

The working release checklist is maintained at:

`handoff/SUBMISSION_TASKS_20260819.md`

The branch stays release-candidate/draft until eligibility, CI, public-link and final submission gates are green.
