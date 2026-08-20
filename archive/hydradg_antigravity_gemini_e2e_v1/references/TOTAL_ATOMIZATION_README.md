# HydraDG Daisy Train — Total Atomization Reference v0.2.0

**Status:** reference design + deterministic scaffold  
**Integration state:** NOT_YET_INTEGRATED_WITH_LOCAL_HYDRADG  
**Signature state:** NOT_SIGNED  
**Merkle state:** NOT_MERKLE_COMMITTED

## Goal

Build a reusable Hack Hydra daisy train:

SOURCE DATASET
→ exact source freeze
→ 100% source-byte coverage
→ 100% logical-record coverage
→ SeedGraph governed atom/semantic derivation
→ canonical FCO hierarchy binding
→ canonical FCG projection binding
→ HydraDB projection
→ isolated golden-route experiment
→ deterministic replicate gate
→ statistical output
→ cross-track promotion gate
→ optional TRAIN-only model training
→ public release

Tracks 01, 02, and 03 are all exercised. A track is promoted only if it clears
pre-registered hard gates. If no track qualifies, the correct output is
`NO_PROMOTED_TRACK`.

## Hard atomization invariant

A dataset may be called `FULL_STRUCTURAL_ATOMIZATION` only when all are true:

1. **source_byte_coverage == 1.0**
2. **logical_record_coverage == 1.0**
3. **orphan_atom_count == 0**
4. **every atom records the exact downloaded `source_sha256`**
5. **every logical atom has a deterministic source locator**
6. **the atomization root is reproducible under identical source/config**

This package does **not** create a second FCO identity standard. It emits
deterministic source locators and coverage objects that must be bound to the
project's canonical FCO/FCG implementation during integration.

## Extreme token efficiency

Full data/logs stay local. Every stage emits:
- a full JSON receipt;
- content hashes;
- a compact one-line status;
- an optional small work packet for Ollarma/Daytona/Kaggle/custom compute.

Model calls are never required for the deterministic S0 structural layer.

## Start here

- `docs/DAISY_TRAIN_DESIGN.md`
- `docs/COVERAGE_AND_IDENTITY_INVARIANTS.md`
- `nulls/STAGE_NULLS.json`
- `prompts/ANTIGRAVITY_IMPLEMENTATION_PROMPT.md`
- `prompts/OLLARMA_OFFLOAD_ROUTER_PROMPT.md`
