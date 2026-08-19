# HydraDG Dataset Adapter Contract

Status: Hack Hydra 2026 release-candidate contract

Purpose: provide one governed intake/evaluation interface for Track 01, Track 02 and Track 03 datasets without hard-coding LongMemEval assumptions into the custody substrate.

## Authority boundary

HydraDG treats SeedGraph as an upstream governed evidence system. HydraDG MUST NOT read or mutate SeedGraph's private Neo4j/SQLite schemas directly.

Allowed SeedGraph surfaces:
- `seedgraph import` / ingest orchestrator for governed intake;
- SeedGraph CLI JSON receipts;
- documented read/export surfaces.

HydraDG owns the downstream FCO/FCG projection, HydraDB experiment namespace and Hack Hydra evaluation receipts.

## Common state machine

```text
DISCOVERED
→ DOWNLOADED
→ HASHED
→ RIGHTS_CLASSIFIED
→ FROZEN
→ SEEDGRAPH_INGESTED
→ FCO_MATERIALIZED
→ FCG_LINKED
→ HYDRADB_PROJECTED
→ REPRODUCIBILITY_READY
→ EVALUATED
```

A later state MUST NOT be claimed when its load-bearing receipt is absent.

## Required adapter record

Every dataset adapter emits at least:

```json
{
  "dataset_id": "...",
  "track": "01|02|03",
  "source_repository": "...",
  "source_revision": "...",
  "source_manifest_sha256": "...",
  "license_declared_upstream": "...",
  "evaluation_role": "EVAL|REPLAY|CANARY",
  "training_allowed": false,
  "source_format": ["..."],
  "adapter_version": "...",
  "seedgraph_projection": {
    "receipt_path": "...",
    "seed_ids": [],
    "source_hash_matches": 0,
    "source_hash_total": 0
  },
  "fco_projection": {
    "objects": [],
    "claim_ceiling": "..."
  },
  "fcg_projection": {
    "edges": [],
    "orphan_count": 0
  },
  "hydradb_projection": {
    "namespace": "...",
    "receipt_path": "..."
  },
  "evaluation": {
    "baseline": "...",
    "treatment": "...",
    "metrics": {},
    "decision": "..."
  }
}
```

## Two comparison lanes

### Lane 1 — custody/provenance

A = downloaded bytes plus upstream/local hash manifest.

B = the same source identity admitted through SeedGraph, materialized as application-level FCOs/FCG edges and projected to HydraDB.

Predeclared metrics:
- `source_hash_agreement`: SeedGraph source SHA equals the locally frozen source SHA where the raw object is directly imported;
- `seedgraph_intake_coverage`: admitted source objects / declared source objects;
- `hydradb_projection_coverage`: projected custody objects / admitted custody objects;
- `complete_route_coverage`: objects with a traversable source → SeedGraph intake → FCO → HydraDB route / projected objects;
- `orphan_count`: derived custody nodes with no declared upstream source;
- `replay_identity`: repeated deterministic intake resolves to the same source identity;
- `first_divergent_dependency`: earliest source/transform FCO whose identity changes under a controlled perturbation.

An improvement in these metrics is a custody/provenance result only. It is not evidence of better RAG, QA, memory or ontology performance.

### Lane 2 — task performance

A = native/raw benchmark baseline.

B = dataset-specific semantic adapter → SeedGraph-governed evidence identities → FCO/FCG → HydraDB → same evaluation contract.

The task metric is dataset-specific and MUST use the same evaluation items/denominators between A and B.

Directional null by default:

```text
H0: treatment_metric <= baseline_metric
H1: treatment_metric > baseline_metric
```

Negative, null, contradictory and abstaining results remain first-class evidence objects.

## Dataset-specific adapters

### LongMemEval / LongMemEval-V2

Semantic unit: session occurrence / memory state.

Relationships may include:
`NEXT`, `PREV`, `ASSERTS`, `ABOUT`, `DERIVED_FROM`, `SUPERSEDED_BY`, `CONTRADICTS`.

### EnterpriseRAG-Bench / HERB

Semantic unit: enterprise document/chunk/entity/evidence relation.

Required Track-01 relations are introduced by the adapter, not by changing the common custody contract.

### BEAM

The upstream repository may include Parquet. SeedGraph does not currently expose a native Parquet dataset parser in the reviewed interface. Raw Parquet objects therefore enter the common custody lane through deterministic content-hash sidecars until a bounded semantic adapter is executed. `CUSTODY_SIDECAR_ONLY` MUST NOT be described as full semantic ingestion.

### Track 02 HydraBlast

Track 02 is not primarily a Hugging Face dataset lane. The adapter contract applies to npm/deps.dev/OSV/GitHub Advisory/lockfile source objects using package/version/dependency semantics.

## FCO/FCG projection

HydraDG application FCO IDs use the existing release implementation:

```text
object_sha256 = SHA256(canonical_json({type,payload}))
id = "fco:" + object_sha256
```

The full SHA-256 remains the custody identity. Any numeric HydraDB vertex ID is an addressing adapter only.

Minimum custody route:

```text
UpstreamDataset
  → LocalDatasetSnapshot
  → SourceFile
  → SeedGraphIntake
  → CustodyFCO
  → HydraDBProjection
  → EvaluationResult
```

Edges MUST preserve typed source/transform/derived-evidence/claim/artifact boundaries.

## CFMO boundary

CFMO is optional for this release. A sequence of state snapshots or FCG edges MUST NOT be called a CFMO unless the declared CFMO construction is actually implemented and its receipt exists.

Current default:

```text
CFMO_STATE=NOT_IMPLEMENTED_BY_DATASET_ADAPTER_CONTRACT
```

The existing temporal FCG can still represent downloaded → ingested → projected → evaluated transitions without promoting a CFMO claim.

## Claim ceilings

Initial cross-system matrix:

```text
DATASET_CUSTODY_AND_PROVENANCE_COMPARISON_ONLY_NOT_BENCHMARK_PERFORMANCE
```

Semantic benchmark adapters may use their own narrower executed ceilings.

SHA-256 establishes byte/object identity only. SeedGraph provenance does not establish correctness. HydraDB projection does not establish retrieval improvement. Model output does not establish independent verification.
