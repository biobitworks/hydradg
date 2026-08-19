# HydraDG Dataset Adapter Contract

Status: Hack Hydra 2026 release-candidate contract

Purpose: provide one governed intake/evaluation interface for Track 01, Track 02 and Track 03 datasets without hard-coding LongMemEval assumptions into the custody substrate.

## Authority boundary

HydraDG treats SeedGraph as an upstream governed evidence system. HydraDG MUST NOT read or mutate SeedGraph's private Neo4j/SQLite schemas directly.

Allowed SeedGraph surfaces:
- `seedgraph import` / ingest orchestrator for governed intake;
- SeedGraph CLI JSON receipts;
- documented read/export surfaces.

SeedGraph remains authoritative for its own source identity, ledger and content-store receipts. HydraDG owns the Hack-Hydra-specific full dataset atomization, application FCO/FCG projection, HydraDB experiment namespace and evaluation receipts.

The existing SeedGraph `DatasetSeed` metadata-only invariant is NOT weakened. Full dataset atomization is a downstream deterministic transformation whose output is itself admitted back to SeedGraph as a governed atom-bundle artifact before HydraDB projection.

## Common state machine

```text
DISCOVERED
→ DOWNLOADED
→ HASHED
→ RIGHTS_CLASSIFIED
→ FROZEN
→ SEEDGRAPH_SOURCE_ADMITTED
→ FULL_ATOMIZATION_COMPLETE
→ ATOM_BUNDLE_SEEDGRAPH_ADMITTED
→ FCO_MATERIALIZED
→ FCG_LINKED
→ HYDRADB_PROJECTED
→ REPRODUCIBILITY_READY
→ EVALUATED
```

A later state MUST NOT be claimed when its load-bearing receipt is absent.

`SEEDGRAPH_SOURCE_ADMITTED` is not equivalent to `FULL_ATOMIZATION_COMPLETE`.
`ATOM_BUNDLE_SEEDGRAPH_ADMITTED` does not mean SeedGraph's private Neo4j schema contains one native node per HydraDG atom; it means the exact deterministic atom-bundle bytes are in SeedGraph custody through the supported ingest surface.

## Full atomization invariant

A dataset is `FULL_ATOMIZATION_COMPLETE` only when all of the following are true:

1. **Byte coverage = 100%.** Every file named by the frozen `SHA256SUMS.txt` manifest has a `SourceFileFCO` that contains the exact expected file SHA-256.
2. **Logical record coverage = 100% for recognized structured data formats.** Every JSON/JSONL/CSV/TSV/Parquet logical record emitted by the declared adapter has exactly one position-bound `DatasetRecordFCO`.
3. **Opaque/binary coverage = 100%.** Files for which record semantics are not declared still have a byte-exact `BlobFCO`; they are not silently omitted.
4. **Field commitment.** Every structured record commits all of its recursively enumerated scalar fields as typed, path-bound FCO leaves. Field values need not become separate HydraDB vertices.
5. **Duplicate preservation.** Record identity is position-bound. Two byte/logically identical records at different source positions MUST NOT collapse into one custody object.
6. **No orphan atoms.** Every record/blob FCO must traverse to a `SourceFileFCO`, local snapshot, upstream dataset identity and SeedGraph admission object.
7. **Deterministic root.** The complete atom-set root and deterministic science payload hash reproduce under identical input bytes + adapter version.
8. **HydraDB projection accounting.** Every projected FCO/FCG object is counted and reconciled against the locally materialized atom bundle.

### Position-bound identity

A logical record identity must include both content and position:

```text
record_preimage =
  domain_separator
  || source_file_sha256
  || logical_pointer_or_ordinal
  || canonical_record_sha256
  || field_leaf_merkle_root
```

This prevents identical duplicate rows/records from collapsing.

### Field leaves

Each scalar field leaf is bound to its position/path:

```text
field_leaf = SHA256(
  domain_separator
  || field_path
  || scalar_type
  || canonical_value_bytes
)
```

Array indices are part of `field_path`.

Field leaves may remain inside the record FCO rather than becoming separate graph vertices. This is the intended fractal representation: the graph stays navigable at dataset/file/record granularity while each record recursively commits its complete field structure.

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
  "seedgraph_source_admission": {
    "receipts": [],
    "source_hash_matches": 0,
    "source_hash_total": 0
  },
  "atomization": {
    "source_files_total": 0,
    "source_files_byte_bound": 0,
    "structured_records_total": 0,
    "structured_records_atomized": 0,
    "opaque_blob_files": 0,
    "field_leaves_total": 0,
    "orphan_count": 0,
    "atom_set_merkle_root": "...",
    "deterministic_payload_sha256": "..."
  },
  "seedgraph_atom_bundle_admission": {
    "bundle_manifest_sha256": "...",
    "receipt": "..."
  },
  "fco_projection": {
    "object_count": 0,
    "claim_ceiling": "..."
  },
  "fcg_projection": {
    "edge_count": 0,
    "orphan_count": 0
  },
  "hydradb_projection": {
    "namespace": "...",
    "objects_expected": 0,
    "objects_projected": 0,
    "edges_expected": 0,
    "edges_projected": 0,
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

## FCO hierarchy

Minimum object hierarchy:

```text
UpstreamDatasetFCO
└── LocalDatasetSnapshotFCO
    ├── SeedGraphSourceAdmissionFCO
    └── SourceFileFCO × N
        ├── DatasetRecordFCO × M
        │   └── typed field leaves × K
        └── BlobFCO when no structured-record semantics are declared

AtomBundleFCO
└── commits all file/record FCO identities

HydraDBProjectionFCO
└── commits projection receipt + expected/projected counts

EvaluationResultFCO
└── commits the experiment science payload
```

The exact file bytes stay in the local frozen source and SeedGraph content custody where admitted; the graph does not need to copy gigabytes of raw values into node properties.

## FCG edges

At minimum:

```text
LocalDatasetSnapshotFCO -[:DERIVED_FROM]-> UpstreamDatasetFCO
SeedGraphSourceAdmissionFCO -[:ADMITS]-> LocalDatasetSnapshotFCO
SourceFileFCO -[:MEMBER_OF]-> LocalDatasetSnapshotFCO
DatasetRecordFCO -[:DERIVED_FROM]-> SourceFileFCO
DatasetRecordFCO -[:NEXT]-> DatasetRecordFCO
BlobFCO -[:DERIVED_FROM]-> SourceFileFCO
AtomBundleFCO -[:COMMITS]-> SourceFileFCO / DatasetRecordFCO / BlobFCO
HydraDBProjectionFCO -[:PROJECTS]-> AtomBundleFCO
EvaluationResultFCO -[:DERIVED_FROM]-> HydraDBProjectionFCO
```

Dataset-specific semantic relationships are additional FCG/HydraDB edges; they do not replace custody edges.

## Format adapters

### JSONL

One line = one position-bound logical record. Preserve the raw-line SHA-256 and canonical parsed-record SHA-256 separately.

### JSON

For a top-level array, each array member is a logical record. For structured benchmark objects with named record arrays, the adapter must declare the JSON path used as the record stream. No silent whole-file fallback is permitted for a declared structured data file.

### CSV / TSV

One parsed data row = one logical record. The exact file SHA provides byte custody; the record FCO commits the parsed canonical row plus row ordinal and field leaves. Multiline CSV quoting therefore does not need a fabricated byte offset.

### Parquet

One logical table row = one record, streamed by row batches. The exact Parquet file hash provides byte custody. Row FCOs commit canonical typed row values and row ordinal. A missing Parquet reader is a fail-closed dependency error, not `FULL_ATOMIZATION_COMPLETE`.

### Text / Markdown

If the file is part of benchmark content rather than repository documentation, the dataset adapter must declare a deterministic record/chunk rule. Repository README/license files may be represented as byte-exact `BlobFCO`s unless they are part of the benchmark task input.

### Image / opaque binary

The file itself is a `BlobFCO` bound to the exact byte SHA. Pixel-level atomization is not implied. Derived OCR/vision outputs, if any, are separate probabilistic or deterministic derived-evidence FCOs and must point back to the blob.

## Dataset-specific semantics

### LongMemEval / LongMemEval-V2

Logical benchmark objects additionally project into session occurrence / memory-state semantics.

Relationships may include:
`NEXT`, `PREV`, `ASSERTS`, `ABOUT`, `DERIVED_FROM`, `SUPERSEDED_BY`, `CONTRADICTS`.

### EnterpriseRAG-Bench / HERB

Logical document/question records additionally project into enterprise document/chunk/entity/evidence relationships.

Track-01 ontology/entity edges are produced by the adapter and remain linked to their record FCOs.

### BEAM

Parquet rows are fully atomized through the Parquet adapter. `BlobFCO`-only treatment is insufficient for BEAM's benchmark tables.

### Track 02 HydraBlast

Track 02 applies the same contract to repository/lockfile/advisory objects. Package/version/dependency records become position/source-bound FCOs before dependency graph projection.

## Two comparison lanes

### Lane 1 — custody/provenance

A = frozen downloaded bytes plus upstream/local file hashes.

B = the same source bytes → SeedGraph admission → full record FCO atomization → FCG → SeedGraph atom-bundle admission → HydraDB projection.

Predeclared metrics:
- exact file byte coverage;
- logical record atomization coverage;
- field-leaf coverage;
- SeedGraph source-hash agreement;
- HydraDB projection coverage;
- complete source→record→projection route coverage;
- orphan rate;
- deterministic replay identity;
- perturbation localization depth / first divergent FCO.

A positive result in these metrics is a custody/provenance result only. It is not evidence of better RAG, QA, memory or ontology performance.

### Lane 2 — task performance

A = native/raw benchmark baseline.

B = dataset-specific semantic adapter → SeedGraph/FCO/FCG-governed evidence → HydraDB → same evaluation contract.

The task metric MUST use the same evaluation items, denominator and scoring rule between A and B.

Directional null by default:

```text
H0: treatment_metric <= baseline_metric
H1: treatment_metric > baseline_metric
```

Negative, null, contradictory and abstaining results remain first-class evidence objects.

Track 03's existing negative/neutral retrieval ablation is retained and prevents a blanket claim that adding graph provenance improves retrieval.

## FCO identity boundary

HydraDG application FCO IDs currently use:

```text
object_sha256 = SHA256(canonical_json({type,payload}))
id = "fco:" + object_sha256
```

The full SHA-256 remains the custody identity. Any numeric HydraDB vertex ID is an addressing adapter only.

Until canonical FCO/FCG schema conformance is explicitly checked against the authoritative specification, these objects must be described as the HydraDG application FCO implementation rather than claimed canonical-spec verification.

## CFMO boundary

CFMO is optional. The temporal sequence

```text
DOWNLOADED → SEEDGRAPH_ADMITTED → ATOMIZED → HYDRADB_PROJECTED → PERTURBED → RESTORED
```

may be represented in the FCG without calling it a CFMO.

A CFMO claim requires an implemented CFMO constructor, declared state identity rule and an actual execution receipt.

Current default:

```text
CFMO_STATE=NOT_IMPLEMENTED_BY_DATASET_ADAPTER_CONTRACT
```

## Claim ceilings

Before benchmark evaluation:

```text
FULL_DATASET_FCO_FCG_CUSTODY_PROJECTION_ONLY_NOT_BENCHMARK_PERFORMANCE
```

After a task-specific evaluation, use the narrower executed claim ceiling supported by that experiment.

SHA-256 establishes byte/object identity only. SeedGraph provenance does not establish correctness. HydraDB projection does not establish retrieval improvement. Model output does not establish independent verification.
