# How to Reproduce HydraDG

This is the short judge/operator path for reproducing the **HydraDG** website and its **HydraDB-backed graph projection** from the public repository.

For the full clean-machine procedure, use [`docs/JUDGE_REPRODUCE_FROM_SCRATCH.md`](docs/JUDGE_REPRODUCE_FROM_SCRATCH.md). For graph/data details, use [`HYDRADB_DATA.md`](HYDRADB_DATA.md).

## 1. What is included

```text
apps/hydradg-web/                  Next.js / React website source
apps/hydradg-web/.env.example      HydraDB environment template
apps/hydradg-web/package-lock.json pinned web dependencies
custody/graph/live/nodes.jsonl     public canonical FCG node snapshot
custody/graph/live/edges.jsonl     public canonical FCG edge snapshot
scripts/project_fcg_snapshot_to_hydradb.py
                                    fail-closed FCG -> HydraDB importer
HydraDG_DaisyTrain_v0.3.7/hydra/   current node/edge schema definitions
PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json
                                    preregistered Track 03 matrix design
```

**FCO = Fractal Custody Object.**  
**FCG = Fractal Custody Graph.**

HydraDB is the operational graph/query backend for the submission. The public JSONL FCG snapshot is the portable reconstruction input; HydraDB is recreated from that snapshot rather than by copying a machine-specific database directory.

## 2. Prerequisites

- Git
- Python 3.10+
- Node.js 20+ and npm
- the official Hack Hydra / HydraDB local graph environment or a compatible HydraDB graph endpoint
- a HydraDB bearer token
- an isolated HydraDB namespace beginning with `hydradg-`

HydraDB itself is an upstream dependency and is not vendored into this repository.

## 3. Clone

```bash
git clone https://github.com/biobitworks/hydradg.git
cd hydradg
```

For the hackathon submission, **`main` is the judge-facing branch**.

## 4. Fast website-only preview

The website contains deterministic presentation fixtures so reviewers can inspect the UI without writing to HydraDB. This is a presentation path, **not evidence of a live HydraDB reconstruction**.

```bash
npm run install:all
npm run typecheck
npm run build
npm run dev
```

Open the port printed by Next.js, normally `http://localhost:3000`.

Static emergency fallback:

```text
apps/hydradg-web/public/backup/hydradg.html
```

## 5. Recreate the HydraDB graph

Start the official HydraDB environment first. The local contract used by the judge guide is:

```text
HTTP base:  http://127.0.0.1:8443
Graph ID:   default
Cell ID:    cell-0
Namespace:  hydradg-judge-repro   # example isolated namespace
```

Store the token outside Git:

```bash
mkdir -p ~/.local/share/hydradg-repro
printf '%s' "$HYDRADB_AUTH_TOKEN" > ~/.local/share/hydradg-repro/hydradb-auth-token
chmod 600 ~/.local/share/hydradg-repro/hydradb-auth-token
```

Then import the public FCG snapshot:

```bash
python3 scripts/project_fcg_snapshot_to_hydradb.py \
  --nodes custody/graph/live/nodes.jsonl \
  --edges custody/graph/live/edges.jsonl \
  --endpoint http://127.0.0.1:8443/v1/graphs/default/query \
  --token-file ~/.local/share/hydradg-repro/hydradb-auth-token \
  --namespace hydradg-judge-repro \
  --allow-write \
  --out repro/receipts/HYDRADB_FCG_IMPORT_RECEIPT.json
```

Expected terminal state:

```text
HYDRADB_FCG_IMPORT=PASS
```

The importer checks the JSONL structure, node/edge integrity, isolated namespace, readback counts, and the expected Track 03 FCG-root canary before it reports PASS.

## 6. Connect the website to the reconstructed HydraDB backend

```bash
cd apps/hydradg-web
cp .env.example .env.local
```

Set the HydraDB values in `.env.local`:

```dotenv
GRAPH_BACKEND=hydradb-http
HYDRADB_HTTP_URL=http://127.0.0.1:8443
HYDRADB_GRAPH_ID=default
HYDRADB_GRAPH_NAMESPACE=hydradg-judge-repro
HYDRADB_CELL_ID=cell-0
HYDRADB_AUTH_TOKEN=<local token; never commit>
```

Then build and run:

```bash
npm ci
npm run typecheck
npm run build
npm run start -- -p 3012
```

Open:

```text
http://127.0.0.1:3012/
```

## 7. Judge routes

```text
/                       Overview
/judge                  Reference -> Poison -> Antidote walkthrough
/track03                Track 03 retrieval evidence
/graph                  4D FCG / Context Iceberg
/evidence               evidence and lineage inspector
/knowledge              project Knowledge Base
/how-to                 in-app operator guide
/eligibility            submission/custody status
/backup/hydradg.html    static presentation fallback
```

Hit@K and Recall@K are retrieval metrics, not end-to-end QA accuracy. `G*` / `Delta G*` are application-defined dimensionless information-state diagnostics, not physical Gibbs free energy.

## 8. Current schemas and experiment design

Current HydraDG schema files:

```text
HydraDG_DaisyTrain_v0.3.7/hydra/schema_nodes.json
HydraDG_DaisyTrain_v0.3.7/hydra/schema_edges.json
```

The preregistered RAW vs SeedGraph K5/K10 matrix is:

```text
PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json
```

The original LongMemEval dataset bytes are not represented by that small preregistration file; the preregistration records source identity, experimental design, null hypotheses, and claim boundaries.

## 9. Verification and security

Useful local checks:

```bash
python3 scripts/check_hydradg_web_links.py
python3 scripts/check_static_fallback.py
bash scripts/release_gate.sh
```

Final secret scan for a release commit:

```bash
gitleaks git --redact=100 --no-banner .
```

The fail-closed GitHub workflow is `.github/workflows/gitleaks-release.yml`. A historical scan does not establish that a newer commit is secret-clean.

## 10. What successful reconstruction establishes

A successful import/readback plus website build establishes reproducibility of the **public graph snapshot and application path under the documented HydraDB interface**.

It does not by itself establish benchmark superiority, end-to-end QA improvement, physical thermodynamic meaning for `G*`, a real project signature, a Merkle/MMR commitment, or independent scientific replication of every experiment.

For submission scope and evidence boundaries, see [`SUBMISSION.md`](SUBMISSION.md).
