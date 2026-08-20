# HydraDB Data, Schemas & FCO/FCG Provenance Manual

This document describes the **HydraDB** graph projection used by **HydraDG**, the portable public graph snapshot, current schema files, and the boundary between canonical custody and the operational query backend.

**FCO = Fractal Custody Object.**  
**FCG = Fractal Custody Graph.**

## 1. Architecture

```text
CANONICAL / PORTABLE CUSTODY                 OPERATIONAL HYDRADB PROJECTION
custody/graph/live/nodes.jsonl               HydraDB graph nodes
custody/graph/live/edges.jsonl               HydraDB typed relationships
FCO identity + evidence class       ->       query/traversal/readback
claim ceiling + source lineage               isolated graph namespace
```

HydraDB is load-bearing for the submission's graph/query path: it supports temporal traversal, provenance lookup, contradiction/supersession traversal, and reconstruction of the public FCO/FCG projection. The repository does not require a machine-specific HydraDB database directory to reproduce the public state.

## 2. Portable reconstruction inputs

| Artifact | Purpose |
|---|---|
| `custody/graph/live/nodes.jsonl` | Public canonical FCG node snapshot used by the reproduction importer |
| `custody/graph/live/edges.jsonl` | Public canonical FCG edge snapshot used by the reproduction importer |
| `scripts/project_fcg_snapshot_to_hydradb.py` | Fail-closed FCG -> HydraDB importer and readback verifier |
| `HydraDG_DaisyTrain_v0.3.7/hydra/schema_nodes.json` | Current Track 03 node schema definitions |
| `HydraDG_DaisyTrain_v0.3.7/hydra/schema_edges.json` | Current Track 03 edge schema definitions |
| `PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json` | Preregistered matrix design, source identity, null hypotheses, and claim boundary; **not the 277 MB source dataset itself** |
| `custody/website_knowledge_fco_projection.json` | Public website/knowledge projection input where present |

The original LongMemEval source is governed separately by its exact source identity and dataset rights. Do not infer that the compact preregistration JSON is a copy of the full source dataset.

## 3. Representative graph semantics

Representative relationships used by the Track 03 memory model include:

```text
Session -> NEXT/PREV -> Session
Session -> ASSERTS -> Fact
Fact -> DERIVED_FROM -> Session
Fact -> ABOUT -> Entity
Fact -> SUPERSEDES / SUPERSEDED_BY -> Fact   # use the predicate present in the relevant frozen artifact
Fact -> CONTRADICTS -> Fact
```

The public FCG snapshot may also contain project-level provenance/custody object types beyond the benchmark's Session/Fact/Entity model. The importer preserves each public node payload and the edge predicate actually present in the JSONL rather than silently rewriting the graph into a different ontology.

## 4. Current schema files

```text
HydraDG_DaisyTrain_v0.3.7/hydra/schema_nodes.json
HydraDG_DaisyTrain_v0.3.7/hydra/schema_edges.json
```

Older DaisyTrain versions are historical evidence and should not be treated as the current judge schema unless a specific historical receipt references them.

## 5. Recreate the public FCG in HydraDB

Prerequisites:

- official Hack Hydra / HydraDB local graph environment or compatible HydraDB graph endpoint;
- bearer token stored outside Git;
- isolated namespace beginning with `hydradg-`.

Example local contract:

```text
HTTP base:  http://127.0.0.1:8443
Graph ID:   default
Cell ID:    cell-0
Namespace:  hydradg-judge-repro
```

Store the token outside the repository:

```bash
mkdir -p ~/.local/share/hydradg-repro
printf '%s' "$HYDRADB_AUTH_TOKEN" > ~/.local/share/hydradg-repro/hydradb-auth-token
chmod 600 ~/.local/share/hydradg-repro/hydradb-auth-token
```

Run the importer from repository root:

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

The importer fails closed on malformed JSONL, duplicate node IDs, missing edge endpoints, unsafe predicate tokens, shared/default namespaces, node/edge count mismatch, or failure to read back the expected Track 03 experiment root.

The expected readback canary currently encoded by the importer is:

```text
experiment:fa170ab51cdfba46f9a24979c9be9b90fdc4ccedcdb292f313aa4439a92b08d8
```

## 6. Connect the website

Copy the environment template:

```bash
cd apps/hydradg-web
cp .env.example .env.local
```

Set at minimum:

```dotenv
GRAPH_BACKEND=hydradb-http
HYDRADB_HTTP_URL=http://127.0.0.1:8443
HYDRADB_GRAPH_ID=default
HYDRADB_GRAPH_NAMESPACE=hydradg-judge-repro
HYDRADB_CELL_ID=cell-0
HYDRADB_AUTH_TOKEN=<local token; never commit>
```

Build and run:

```bash
npm ci
npm run typecheck
npm run build
npm run start -- -p 3012
```

For the complete sequence, use [`docs/JUDGE_REPRODUCE_FROM_SCRATCH.md`](docs/JUDGE_REPRODUCE_FROM_SCRATCH.md).

## 7. Track 03 evidence boundary

The historical full500 retrieval evidence records:

- 500 total cases;
- 23,867 sessions;
- 4,776 entities;
- 3,506 facts;
- 470 retrieval-scored cases with 30 abstentions excluded under the frozen analysis rule.

The bounded submission conclusion is that the completed historical K=5 B/C/D treatments did **not** establish a positive Hit@5 advantage over the A/reference route. Hit@K and Recall@K are retrieval metrics, not end-to-end QA accuracy.

Do not promote later matrix, replication, K-depth, or other claims unless the corresponding current receipt is cited and its claim ceiling permits that statement.

## 8. Security and custody boundaries

- Tokens and `.env.local` are local-only and must not be committed.
- A SHA-256 digest establishes byte identity, not authorship or scientific validity.
- A successful HydraDB projection/readback establishes reproduction of the public graph projection, not independent scientific replication of every upstream experiment.
- Real signing and Merkle/MMR status must be taken from the corresponding receipts; do not infer them from hashes.
- The exact publication commit must pass the current secret scan before it is described as secret-clean.

See [`HOW_TO.md`](HOW_TO.md), [`SUBMISSION.md`](SUBMISSION.md), and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for operator, submission, and rights boundaries.
