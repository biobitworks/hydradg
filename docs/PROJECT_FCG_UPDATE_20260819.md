# HydraDG project FCG update — 2026-08-19

Status: Hack Hydra release-candidate documentation

## Why this FCG update exists

HydraDG now has more than a graph-memory experiment. It has a website, dataset acquisition lane, total-dataset atomization layer, SeedGraph custody bridge, HydraDB projections, Track 01/02/03 experiments, public-export tooling, a Vercel presentation surface, and a local/offline fallback requirement.

The FCG therefore needs to preserve not only scientific evidence but also the chain by which a judge-facing artifact is assembled and released.

The governing dependency route is:

```text
SOURCE / DATASET / USER INPUT
        ↓
EXACT BYTE IDENTITY / VERSION
        ↓
SEEDGRAPH GOVERNED INTAKE
        ↓
STRUCTURAL ATOMIZATION
        ↓
FCO MATERIALIZATION
        ↓
FCG RELATIONSHIPS
        ↓
HYDRADB PROJECTION
        ↓
EXPERIMENT / QUERY / PERTURBATION
        ↓
RESULT / COUNTEREVIDENCE / ABSTENTION
        ↓
WEBSITE KNOWLEDGE OBJECT
        ↓
PUBLIC ARTIFACT / DEMO / VIDEO
```

No later state is promoted when its load-bearing predecessor is missing.

## Project-level custody objects

### Source objects

- Hack Hydra rule/version evidence.
- HydraDB upstream pinned source revision.
- downloaded dataset revisions and SHA-256 manifests.
- user-supplied COMPUTE template archive identity.
- SeedGraph source revision used for governed intake.
- human instructions and AI transformations where materially used.

### Transformation objects

- dataset acquisition.
- source freeze.
- structural atomization.
- semantic extraction.
- FCO binding.
- FCG construction.
- HydraDB projection.
- retrieval or graph traversal.
- poison/antidote perturbation.
- result canonicalization/statistics.
- website generation.
- public export.

### Derived evidence

- local dataset pull receipts.
- atomization completeness manifests.
- SeedGraph admission receipts.
- HydraDB projection receipts.
- structural/canary/golden-path receipts.
- LongMemEval full500 result/statistics.
- web build/link/browser receipts.
- public-export receipt.

### Claims

Claims remain bounded by the narrowest supporting evidence. In particular:

- a SHA-256 digest establishes byte/object identity only;
- SeedGraph provenance does not establish correctness;
- FCO/FCG route completeness does not establish benchmark superiority;
- HydraDB projection does not establish retrieval improvement;
- the completed LongMemEval full500 result does not show a positive B/C/D hit-rate signal;
- a deterministic fixture Merkle root is not a live HydraDB Merkle commitment;
- no author signature is claimed unless an authorized signing operation produces a verifiable signature.

## Website as an FCG artifact

The public site is itself a custody graph.

Every major route is a `SiteSection` FCO. Every novel term or project-specific entity should resolve through the website knowledge layer to:

```text
TERM / ENTITY / HASH / OBJECT
        ↓
KnowledgeAtom or FCO inspector
        ↓
FCG dependency relationships
        ↓
source/version or executed receipt
        ↓
claim ceiling
```

A visitor should be able to start from the simple public explanation and descend progressively into the exact source or receipt.

### Presentation depth

HydraDG uses a tip-of-the-iceberg information architecture:

```text
TIP / HOT
simple current-state explanation
live demo
current result
        ↓
WATERLINE / WARM
experiment overview
Track 01/02/03
result matrix
        ↓
DEEP / COLD
FCO identities
FCG edges
SeedGraph custody
HydraDB graph state
receipts
hash manifests
historical negative/null evidence
```

The metaphor is descriptive UI language. It is not a thermodynamic measurement.

`ΔG*` remains an application-defined information-state metric and must not be represented as physical Gibbs free energy. The intended analogy is that hot/recent state is operationally active and cold/deep state is retained long-term evidence. Any quantitative `ΔG*` claim remains governed by the implementation-specific definition and evidence.

## Online and offline artifact parity

The release has two presentation surfaces:

1. **Live site** — Next.js/Vercel when deployment succeeds.
2. **Static fallback** — a self-contained HTML artifact that can be opened locally or hosted on any static file service/GitHub Pages.

Both surfaces must link to the same public repository, evidence objects, track descriptions, claim boundaries, and demo story. The static fallback must not imply that local-only HydraDB controls are live.

## Current external-hosting state

At the time of this documentation update, the connected Vercel account shows the latest production deployment as `READY`, but it is still sourced from the older `hack-hydra/webapp-mvp-20260818` branch at commit `e84afb8fafa3494d274edb0bfbfa9ab02b800a96`.

Therefore:

```text
VERCEL_PLATFORM_DEPLOYMENT=READY
CURRENT_RELEASE_BRANCH_DEPLOYED=NO
PUBLIC_RELEASE_WEB_GREEN=NO
```

The live-site state and the current release-candidate state remain separate custody objects.

## Publication fallback rule

If the current release cannot be deployed before submission:

```text
fresh public GitHub export
        +
static fallback HTML
        +
recorded <=3 minute video
        +
executed evidence receipts
```

is the admissible presentation path.

This does not change the science. It changes only the artifact delivery surface.

## Verification / hashing procedure

For a retained file:

```bash
shasum -a 256 path/to/file
```

or equivalently:

```bash
python3 - <<'PY'
import hashlib
from pathlib import Path
p = Path("path/to/file")
h = hashlib.sha256(p.read_bytes()).hexdigest()
print(h)
PY
```

For a response/turn, the response body and custody record must be hashed separately so the digest is not self-referential. Signing, when available, signs the resulting turn-record digest; hashing alone must never be described as a signature.

## States after this update

```text
PROJECT_FCG_DOCUMENTED=YES
WEBSITE_AS_FCG=IMPLEMENTED
KNOWLEDGE_BACKEND_LINKAGE=IMPLEMENTED_PARTIALLY_AND_REQUIRES_TERM_COVERAGE_AUDIT
TOTAL_DATASET_ATOMIZATION=IMPLEMENTED_EXECUTION_PENDING
SEEDGRAPH_ATOM_BUNDLE_ADMISSION=IMPLEMENTED_EXECUTION_PENDING
HYDRADB_FULL_ATOM_PROJECTION=IMPLEMENTED_EXECUTION_PENDING
LIVE_RELEASE_DEPLOYMENT=PENDING
STATIC_FALLBACK=IMPLEMENTED_BY_RELEASE_BRANCH_AFTER_THIS_UPDATE
SIGNATURE_STATE=NOT_SIGNED
LIVE_MERKLE_STATE=NOT_MERKLE_COMMITTED
```
