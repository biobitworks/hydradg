# Third-party notices and external evidence sources

HydraDG's MIT License applies to original Hack Hydra participant-authored implementation in this repository. It does not relicense third-party code, datasets, templates, APIs, papers or services listed below.

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
- Observed archive file count after extraction: 111
- Role: visual/layout template input
- HydraDG reuse: presentation grammar only; unrelated template product claims, marketing content and service logic are not part of the HydraDG implementation.
- License/terms: upstream terms remain controlling; this notice is attribution, not a legal opinion or relicensing statement.

## Track 01 datasets

### EnterpriseRAG-Bench

- Hugging Face: `onyx-dot-app/EnterpriseRAG-Bench`
- Declared upstream license: MIT
- Role: primary Track 01 benchmark
- Dataset bytes: stored outside the public Git repository by default.

### HERB

- Hugging Face: `Salesforce/HERB`
- Declared upstream license: CC-BY-NC-4.0
- Role: heterogeneous enterprise stress/replication lane
- Dataset bytes: remain outside the public Git repository by default; public redistribution is not implied by this repository.

## Track 03 datasets

### LongMemEval cleaned

- Hugging Face: `xiaowu0162/longmemeval-cleaned`
- Declared upstream license: MIT
- Role: primary executed Track 03 benchmark
- Exact source object used by the retained full500 run: `longmemeval_s_cleaned.json`
- Retained source SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`

### LongMemEval-V2

- Hugging Face: `xiaowu0162/longmemeval-v2`
- Declared upstream license: Apache-2.0
- Role: planned independent agent-memory stress lane
- Current local acquisition state: no completed pull receipt has yet been admitted into the submission evidence ledger.

### BEAM

- Hugging Face: `Mohammadta/BEAM`
- Declared upstream license: CC-BY-SA-4.0
- Role: planned long-context scale/falsification lane
- Current local acquisition state: no completed pull receipt has yet been admitted into the submission evidence ledger.

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

No real package exposure or vulnerability result is claimed merely from naming these sources. Each executed snapshot requires its own source/version/byte or API-response custody receipt.

## Prior Byron/FCO/FCG research

Pre-August-12 participant-authored implementation is **not** included as Hack Hydra submission code solely because the underlying concepts predate the hackathon. Prior FCO/FCG, Vithia/Pythia, XenoDisorder, Fractal Waves/ECA and related work may be cited as prior publications/design lineage or external evidence. Any participant-authored implementation included in the final Hack Hydra tree must satisfy the August 12 start rule or be freshly reimplemented during the hackathon.

## Evidence boundary

A source identifier, license field, hash, DOI or upstream repository pointer establishes only the property it actually supports. This notice does not independently verify source correctness, legal compliance, scientific validity, authorship or license compatibility.
