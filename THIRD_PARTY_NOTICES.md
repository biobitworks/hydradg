# Third-party notices and external evidence sources

HydraDG participant-authored **software and reproducibility tooling** are licensed under the Apache License, Version 2.0 unless otherwise stated. Byron P. Lee / Biobitworks authored **preprints, manuscripts, narrative research text, publication-style figures, and explicitly designated research-content artifacts** are licensed under CC BY-NC-ND 4.0 unless an individual artifact states otherwise. See `LICENSE` and `LICENSING.md` for scope. Neither license relicenses third-party code, datasets, templates, APIs, papers, models, or services listed below.

## HydraDB

- Project: HydraDB
- Upstream: https://github.com/hydra-db/hydradb
- Pinned revision used by the current reproducible local lane: `6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219`
- Upstream repository license observed: AGPL-3.0
- Role: graph database/runtime dependency
- Eligibility role: pre-existing upstream open-source dependency permitted by Hack Hydra rules; not claimed as participant-authored code.

## COMPUTE template

- Name: `COMPUTE — The Platform to Build & Ship AI Agents`
- Original template author/page attribution: `kerroudj` / v0
- Template page: https://v0.app/templates/compute-the-platform-to-build-ship-ai-agents-Auw4otwlr20
- Public preview: https://v0-compute-11.vercel.app/
- User-supplied source archive SHA-256: `b363081debc07af517cea73ed53b682b840a9e4c52e6658e7d35f18ca9922e4c`
- Direct archive extraction observed in the 2026-08-19 release audit: **102 files**
- Role: visual/layout template input
- HydraDG reuse: presentation grammar only; unrelated template product claims, marketing content and service logic are not part of the HydraDG implementation.
- License/terms: no standalone LICENSE file was present in the supplied archive during this audit. Upstream template/service terms therefore remain controlling; this notice is attribution, not a legal opinion or relicensing statement.

## Track 01 datasets

### EnterpriseRAG-Bench

- Hugging Face: `onyx-dot-app/EnterpriseRAG-Bench`
- Declared upstream license: MIT
- Role: primary Track 01 benchmark
- Upstream availability/metadata: independently observed on Hugging Face during the 2026-08-19 release audit.
- Dataset bytes: stored outside the public Git repository by default.
- Current local acquisition state: **NO COMPLETED LOCAL PULL RECEIPT ADMITTED YET**.

### HERB

- Hugging Face: `Salesforce/HERB`
- Declared upstream license: CC-BY-NC-4.0
- Role: heterogeneous enterprise stress/replication lane
- Upstream availability/metadata: independently observed on Hugging Face during the 2026-08-19 release audit.
- Dataset bytes: remain outside the public Git repository by default; public redistribution is not implied by this repository.
- Current local acquisition state: **NO COMPLETED LOCAL PULL RECEIPT ADMITTED YET**.

## Track 03 datasets

### LongMemEval cleaned

- Hugging Face: `xiaowu0162/longmemeval-cleaned`
- Declared upstream license: MIT
- Role: primary executed Track 03 benchmark
- Exact source object used by the retained full500 run: `longmemeval_s_cleaned.json`
- Retained source SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- Current execution state: full500 completed; negative/neutral retrieval-ablation result retained under its declared claim ceiling.

### LongMemEval-V2

- Hugging Face: `xiaowu0162/longmemeval-v2`
- Declared upstream license: Apache-2.0
- Role: independent agent-memory stress lane
- Upstream availability/metadata: independently observed on Hugging Face during the 2026-08-19 release audit.
- Current local acquisition state: **NO COMPLETED LOCAL PULL RECEIPT ADMITTED YET**.

### BEAM

- Hugging Face: `Mohammadta/BEAM`
- Declared upstream license: CC-BY-SA-4.0
- Role: long-context scale/falsification lane
- Upstream availability/metadata: independently observed on Hugging Face during the 2026-08-19 release audit.
- Current local acquisition state: **NO COMPLETED LOCAL PULL RECEIPT ADMITTED YET**.

### BEAM-10M

- Hugging Face: `Mohammadta/BEAM-10M`
- Declared upstream license: CC-BY-SA-4.0
- Role: optional upper scale tier after lower BEAM tiers pass
- Current state: deferred.

## Track 02 external data sources

Track 02A is designed to use real package/dependency/advisory evidence after its synthetic structural canary passes:

- npm registry/package metadata
- deps.dev resolved dependency data
- OSV/GitHub Advisory Database
- real repository lockfiles

The post-August-12 HydraBlast canary implementation exists and compares a deterministic Python reverse-transitive-closure oracle with HydraDB traversal over a synthetic package graph. Its claim ceiling is `SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY_NOT_REAL_NPM_EXPOSURE`.

No real package exposure or vulnerability result is claimed merely from naming these sources. Each executed real-data snapshot requires its own source/version/byte or API-response custody receipt.

## Prior Byron/FCO/FCG research

Pre-August-12 participant-authored implementation is **not** included as Hack Hydra submission code solely because the underlying concepts predate the hackathon. Prior FCO/FCG, Vithia/Pythia, XenoDisorder, Fractal Waves/ECA and related work may be cited as prior publications/design lineage or external evidence. Any participant-authored implementation included in the final Hack Hydra tree must satisfy the August 12 start rule or be freshly reimplemented during the hackathon.

## Evidence boundary

A source identifier, license field, hash, DOI or upstream repository pointer establishes only the property it actually supports. This notice does not independently verify source correctness, legal compliance, scientific validity, authorship or license compatibility.
