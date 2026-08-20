# HydraDB Data, Schemas & FCO Provenance Manual

This document details the **HydraDB** graph datasets, schemas, First-Class Object (FCO) data models, and projection pipelines used in **HydraDG**.

---

## 1. Overview of HydraDB Data Architecture

HydraDG separates **immutable custody** from **queryable graph projection**:

```text
CANONICAL CUSTODY LAYER                  HYDRADB GRAPH PROJECTION LAYER
Fractal Custody Objects (FCOs)           HydraDB Nodes & Relational Edges
  ├─ fco_id (SHA-256)                      ├─ (Session:HydraDG)
  ├─ custody_state                         ├─ (Fact:HydraDG)
  ├─ evidence_class                        ├─ (Entity:HydraDG)
  └─ claim_ceiling                         └─ (KnowledgeAtom:HydraDG)
```

HydraDB acts as the high-performance graph database engine used for:
1. **Temporal State Traversal**: Moving forward/backward along `Session -[:NEXT]-> Session` timelines.
2. **Provenance & Evidence Lookup**: Tracing `Fact -[:DERIVED_FROM]-> Session` lineage.
3. **Contradiction & Supersession Querying**: Identifying `Fact -[:SUPERSEDES]-> Fact` and `Fact -[:CONTRADICTS]-> Fact` relationships without deleting historical nodes.
4. **Vector & Relational Projections**: Searching embeddings alongside strict graph constraints.

---

## 2. Included Datasets & Location in Repository

| Dataset / Artifact File | Description | Location in Repo |
|---|---|---|
| `PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json` | 500-case raw SeedGraph dataset for LongMemEval Track 03 benchmarking. | Root directory |
| `hydra/schema_nodes.json` | Node definitions for HydraDB graph projection (Session, Fact, Entity, KnowledgeAtom). | `HydraDG_DaisyTrain_v0.3.1/hydra/schema_nodes.json` |
| `hydra/schema_edges.json` | Edge relationship definitions for HydraDB graph projection (NEXT, PREV, ASSERTS, DERIVED_FROM, ABOUT, SUPERSEDES, CONTRADICTS). | `HydraDG_DaisyTrain_v0.3.1/hydra/schema_edges.json` |
| `website_knowledge_fco_projection.json` | Atomized FCO Knowledge projection dataset powering `/knowledge` and `/evidence`. | `custody/` & `HydraDG_DaisyTrain_v0.3.1/eval/` |
| `DAISY_STATE.json` | Local Daisy train state and execution custody checkpoint. | Root directory |

---

## 3. HydraDB Schema Specification

### Node Labels

```json
{
  "labels": [
    "Session",
    "Fact",
    "Entity",
    "KnowledgeAtom",
    "HydraDGKnowledgeFCO"
  ]
}
```

### Edge Types

- **`NEXT` / `PREV`**: Connects sequential user/agent sessions chronologically.
- **`ASSERTS`**: Connects a `Session` to a `Fact` asserted within it.
- **`DERIVED_FROM`**: Connects a `Fact` back to its origin `Session`.
- **`ABOUT`**: Connects a `Fact` to the target `Entity` it describes.
- **`SUPERSEDES`**: Connects a newer `Fact` to an older `Fact` it replaces.
- **`CONTRADICTS`**: Edge between conflicting facts asserted across sessions.

---

## 4. Replicating & Loading Data into HydraDB

### Method A: Out-of-the-Box Local Web App (Fixtures)
The web application includes self-contained built-in fixtures (`apps/hydradg-web/lib/demoFixture.ts`) that instantiate the graph state in memory automatically when launched via `npm run dev`.

### Method B: Live Local / Hosted HydraDB Instance
To project the repository knowledge base into a local or remote HydraDB instance:

1. Configure environment variables in `apps/hydradg-web/.env.local`:
   ```ini
   GRAPH_BACKEND=hydradb-http
   HYDRADB_HTTP_URL=http://127.0.0.1:8443
   HYDRADB_GRAPH_ID=default
   HYDRADB_GRAPH_NAMESPACE=hydradg-demo
   HYDRADB_CELL_ID=cell-0
   ```

2. Execute the projection script:
   ```bash
   python3 scripts/project_website_knowledge_to_hydradb.py \
     --knowledge-json custody/website_knowledge_fco_projection.json \
     --namespace hydradg-release-kb-demo \
     --allow-write \
     --out custody/hydradb_knowledge_projection_receipt.json
   ```

---

## 5. Summary of Track 03 Dataset Benchmarks

- **Evaluated Dataset**: `xiaowu0162/longmemeval-cleaned`
- **Total Cases**: 500 cases (23,867 sessions, 4,776 entities, 3,506 facts)
- **Scored Subset**: 470 retrieval-scored cases (30 abstentions excluded)
- **Matrix Replicability**: 100% bit-for-bit replicate equality across $2 \times 2$ execution matrix.
