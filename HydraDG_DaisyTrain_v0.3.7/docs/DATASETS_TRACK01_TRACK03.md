# HydraDG Track 01 + Track 03 dataset lanes

This document defines the local dataset acquisition surface used by the Hack Hydra experiments. It is intentionally separate from scientific/evaluation claims: downloading bytes and recording hashes establishes local object identity, not benchmark correctness or independent verification.

## Track 01 — enterprise context + ontology

### EnterpriseRAG-Bench

- Hugging Face: `onyx-dot-app/EnterpriseRAG-Bench`
- upstream license metadata: `MIT`
- role: primary Track 01 benchmark corpus
- scope: synthetic enterprise corpus spanning multiple internal-source types with retrieval/reasoning questions, realistic noise, near-duplicates, conflicts, and missing-information cases
- benchmark restriction: treat evaluation data as evaluation-only; do not use the benchmark corpus as model-training data

### HERB

- Hugging Face: `Salesforce/HERB`
- upstream license metadata: `CC-BY-NC-4.0`
- role: heterogeneous enterprise deep-search stress dataset
- scope: synthetic enterprise/business-workflow artifacts with multi-hop questions and realistic noise
- release boundary: keep local/private by default; do not redistribute in a public release until the intended use has passed a license review

Track 01 graph objective:

`SourceArtifact -> Entity -> Event/Claim -> Provenance -> CurrentState -> AnswerEvidence`

The perturbation lane should exercise alias splitting, stale records, contradictory records, misfiled documents, entity merges, provenance-path changes, and current-state resolution.

## Track 03 — memory + context retrieval

### LongMemEval-S cleaned

- Hugging Face: `xiaowu0162/longmemeval-cleaned`
- upstream license metadata: `MIT`
- role: primary current HydraDG Track 03 benchmark
- canonical file for the current full500 run: `longmemeval_s_cleaned.json`
- expected SHA-256 already used by the Daisy runner: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`

### LongMemEval-V2

- Hugging Face: `xiaowu0162/longmemeval-v2`
- upstream license metadata: `Apache-2.0`
- role: harder environment-experience memory benchmark
- public release contains questions, trajectories, haystacks, schema/docs, and large screenshot archives
- `core` acquisition excludes `trajectory_screenshots/*`; `full` includes them

### BEAM

- Hugging Face: `Mohammadta/BEAM`
- upstream license metadata: `CC-BY-SA-4.0`
- role: long-context memory stress benchmark across 100K/500K/1M-scale conversations
- `Mohammadta/BEAM-10M` is acquired only with the `full` tier because of its much larger footprint

Track 03 graph objective:

`Case -> SessionOccurrence -> Entity/Fact -> NEXT/PREV -> SUPERSEDED_BY/CONTRADICTS -> RetrievalEvidence`

The benchmark answer labels remain evaluation-only and must never be used for graph construction or retrieval ranking.

## Acquisition

From repository root:

```bash
bash HydraDG_DaisyTrain_v0.3.7/scripts/pull_track01_track03_datasets.sh --track all --tier core
```

Large/full lane:

```bash
bash HydraDG_DaisyTrain_v0.3.7/scripts/pull_track01_track03_datasets.sh --track all --tier full
```

Default local destination:

```text
~/.local/share/hydradg-datasets/
```

The script resolves the current Hugging Face repository commit SHA before each download, downloads that exact revision, writes a sorted `SHA256SUMS.txt` inside each dataset directory, and emits a local JSON receipt.

Evidence ceiling:

`EXTERNALLY_RETRIEVED_DATASET_BYTES / LOCAL_DATASET_BYTE_IDENTITIES_AFTER_DOWNLOAD_ONLY`

No dataset pull is a signature, Merkle/MMR commitment, correctness validation, or independent replication.
