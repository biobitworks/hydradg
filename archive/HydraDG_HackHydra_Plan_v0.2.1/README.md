# HydraDG Hack Hydra Plan v0.2.0

This package is an AI-assisted planning/research artifact for the Hack Hydra Track 03 project.

## Core claim
The project does **not** claim to invent temporal graph memory, provenance-aware memory, bitwise reproducibility, or divergence diagnostics individually. It tests a prospective integration: execution divergence linked through a temporal evidence graph to answer/claim impact and typed recovery.

## Contents
- `NOVELTY_AUDIT.md`
- `TERMINOLOGY.md`
- `MATH.md`
- `MVP_PLAN.md`
- `seedgraph/`
- `hydradb/`
- `scripts/`
- `notebooks/`
- `eval/`
- `social/`

## Public/private split
The public graph is suitable for LongMemEval, synthetic data, project documentation and public literature metadata. `PRIVATE_PHI_TWIN.md` defines a schema-compatible private architecture; it contains no PHI and is not a compliance certification.

## Execution state
- math helper smoke tests: executed in artifact generation
- Python syntax checks: executed
- notebook JSON validation: executed
- LongMemEval import: NOT EXECUTED (dataset not downloaded in this runtime)
- HydraDB ingestion: NOT EXECUTED
- Vithia/Kaggle training: NOT EXECUTED
- signatures: NOT SIGNED
- Merkle commitment: NOT MERKLE_COMMITTED

## v0.2.1 execution routes

- `scripts/download_verify_ingest_longmemeval.py` — official cleaned LongMemEval-S download + SHA-256 verification + SeedGraph ingestion.
- `scripts/vithia_divergence_core.py` — backend-neutral small-model divergence fixture.
- `modal/modal_vithia_divergence.py` — T4/L4/A10 cross-hardware run matrix.
- `magicstudiobox/README.md` — same-host and thread-perturbation commands.
- `kaggle/README.md` — independent Kaggle lane.
- `RUN_MATRIX.json` — claim-bounded execution matrix.

The current runtime could not download the 277 MB LongMemEval-S Xet object because outbound
container networking is unavailable. The script pins the expected official file SHA-256 so the
first network-enabled execution can fail closed on data mismatch.
