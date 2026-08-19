# HydraDG Hack Hydra release execution ledger — 2026-08-19

This file replaces unavailable GitHub Tasks/Projects for the final release pass. It is intentionally repo-tracked so progress is reviewable in ordinary Git history.

State vocabulary:
- `PASS` — the named gate actually executed and passed.
- `IMPLEMENTED` — code/artifact exists, execution still required.
- `EXTERNAL_READY` — upstream source exists and metadata was inspected; local bytes are not implied.
- `BLOCKED_EXTERNAL` — load-bearing external execution surface did not start or is unavailable.
- `PENDING` — not executed yet.
- `NOT_APPLICABLE` — deliberately excluded from release.

## Phase 0 — eligibility / custody

| Gate | State | Evidence / boundary |
|---|---|---|
| Official Aug-12 start rule | PASS | hackhydra.hydradb.com checked 2026-08-19; project work starts on/after Aug 12; no participant-authored commits before Aug 12; pre-existing upstream/templates/dependencies allowed with attribution. |
| Deadline | PASS | Aug 20, 2026 11:59 PM PT. |
| Repo-visible HydraDG history post-Aug12 | PASS | first observed participant repo commit `e45580269275018b2824227ec1836bb1a082b9bd`, Aug 18. Ceiling: repository-visible history only. |
| Content-origin audit | PENDING | Later commit dates do not prove imported participant-authored bytes were written after Aug12. Ambiguous pre-hackathon participant code remains excluded pending audit. |
| HydraDB attribution | PASS | upstream `hydra-db/hydradb`, pinned `6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219`. |
| COMPUTE archive identity | PASS | supplied ZIP SHA-256 `b363081debc07af517cea73ed53b682b840a9e4c52e6658e7d35f18ca9922e4c`; direct extraction count 102 files; no standalone LICENSE observed in archive. |
| Original HydraDG license | PASS | MIT LICENSE present; third-party terms remain separate. |

## Phase 1 — datasets

| Lane | State | Current evidence |
|---|---|---|
| Track 01 EnterpriseRAG-Bench | EXTERNAL_READY | HF repo `onyx-dot-app/EnterpriseRAG-Bench`, declared MIT; acquisition script implemented; no admitted local pull receipt yet. |
| Track 01 HERB | EXTERNAL_READY | HF repo `Salesforce/HERB`, declared CC-BY-NC-4.0; acquisition script implemented; no admitted local pull receipt yet; keep bytes outside public redistribution. |
| Track 03 LongMemEval-S | PASS | exact source object hydrated; SHA-256 `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`; full500 executed. |
| Track 03 LongMemEval-V2 | EXTERNAL_READY | HF repo `xiaowu0162/longmemeval-v2`, declared Apache-2.0; no admitted local pull receipt yet. |
| Track 03 BEAM | EXTERNAL_READY | HF repo `Mohammadta/BEAM`, declared CC-BY-SA-4.0; no admitted local pull receipt yet. |
| BEAM-10M | NOT_APPLICABLE | deferred until lower tier is useful; not required for current release. |

Dataset pull receipts establish retrieved byte identity only, not correctness or benchmark verification.

## Phase 2 — Track 03 HydraMemory

| Gate | State | Evidence / boundary |
|---|---|---|
| Pinned local HydraDB structural suite | PASS | all retained structural checks true; result SHA `69170a28743d65ae57742865068565b4be8c372fc63b2c62587609c2241f1177`; ceiling `SYNTHETIC_STRUCTURAL_CONFORMANCE_ONLY`. |
| LongMemEval full500 | PASS | 500 cases / 470 scored; result SHA `bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324`; stats SHA `8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc`; receipt `21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365`. |
| Full500 conclusion | PASS | negative/neutral retained: `NO_POSITIVE_HIT_RATE_SIGNAL`; ceiling `LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA`. |
| Live normal→poison→antidote release execution | IMPLEMENTED | release writer exists; fresh retained three-step execution receipt still required. |
| Judge Lab current-state/retrieval visualization | IMPLEMENTED | routes/code exist; public deployment E2E still required. |

## Phase 3 — Track 01 HydraOntology

| Gate | State | Evidence / boundary |
|---|---|---|
| Fresh hackathon graph canary implementation | IMPLEMENTED | `track01_hydraontology_canary.py`; SourceDocument / EntityMention / CanonicalEntity plus `MENTIONS` / `RESOLVES_TO`; deterministic Python evidence-set oracle. |
| Synthetic reference→alias split→merge test | IMPLEMENTED | intended ceiling `SYNTHETIC_TRACK01_STRUCTURAL_CANARY_ONLY_NOT_ENTERPRISERAG_OR_HERB_PERFORMANCE`. |
| GitHub Actions execution | BLOCKED_EXTERNAL | current PR job ended before any recorded steps/logs/artifacts; not treated as canary failure or pass. |
| Real EnterpriseRAG/HERB canary | PENDING | requires admitted dataset bytes and bounded real-data adapter execution. |

## Phase 4 — Track 02A HydraBlast

Chosen official option: **A — Supply-chain blast radius**.

| Gate | State | Evidence / boundary |
|---|---|---|
| Fresh hackathon graph canary implementation | IMPLEMENTED | `track02_hydrablast_canary.py`; Service / Lockfile / PackageVersion / Advisory; `USES`, `RESOLVED`, `DEPENDS_ON`, `AFFECTS`. |
| Independent expected-set oracle | IMPLEMENTED | deterministic Python reverse-transitive closure. |
| HydraDB graph algorithm | IMPLEMENTED | iterative OpenCypher one-hop reverse dependency traversal, explicitly bounded by pinned runtime capability. |
| Poison / partial repair / full repair model | IMPLEMENTED | expected exposure counts 0→2→1→0; ceiling `SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY_NOT_REAL_NPM_EXPOSURE`. |
| GitHub Actions execution | BLOCKED_EXTERNAL | current PR job ended before any recorded steps/logs/artifacts; not treated as canary failure or pass. |
| Real npm/deps/advisory canary | PENDING | acquire bounded real source snapshot and compare HydraDB set with deterministic reference closure. |

## Phase 5 — COMPUTE-derived website / site as FCG

| Gate | State | Evidence / boundary |
|---|---|---|
| Template source custody | PASS | exact user-supplied archive hashed and directly inspected. |
| Site-level FCO/FCG representation | IMPLEMENTED | `/api/site-fcg`, per-FCO `/fco/[id]`, site section FCO IDs, explicit graph edges. |
| Primary routes | IMPLEMENTED | `/`, `/judge`, `/graph`, `/knowledge`, `/evidence`, `/eligibility`, `/track01`, `/track02`, `/track03`, `/demo`. |
| Hash → FCO → dependency/source navigation | IMPLEMENTED | FCO inspector and knowledge links exist. |
| COMPUTE layout adaptation | IMPLEMENTED_PARTIAL | site uses COMPUTE-inspired section numbering/display hierarchy; exact archive remains attributed third-party input rather than participant-authored code. |
| Mobile/desktop browser verification | PENDING | deployment/browser E2E required. |

## Phase 6 — build / CI

| Gate | State | Evidence / boundary |
|---|---|---|
| Prior Judge Lab head CI | PASS | Judge Lab run #19 previously completed success before release-branch additions. |
| Current release-head GitHub Actions | BLOCKED_EXTERNAL | four workflows ended `failure`, but connected GitHub exposed no executed steps, logs or artifacts. Judge Lab rerun reproduced a no-step failure. Classification: `GITHUB_ACTIONS_RUNNER_START_FAILURE / CAUSE_NOT_ESTABLISHED`. |
| Current release typecheck/build | PENDING | must be established by an actually executing local or Vercel build; do not infer from prior head. |
| Route/link smoke | PENDING | current release deployment required. |

## Phase 7 — Vercel

| Gate | State | Evidence / boundary |
|---|---|---|
| Existing production | PASS_OLDER_ONLY | old deployment `dpl_E59xkLJrKgJuWu1s4uHx6FSiPciV` READY from branch `hack-hydra/webapp-mvp-20260818`; not the release candidate. |
| Submission-eligible preview | PENDING | no release-branch Vercel deployment observed as of this ledger update. |
| `/judge` public 200 | PENDING | cannot promote older production 404 state. |
| Runtime-error check | PENDING | run after release deployment E2E. |

## Phase 8 — public freeze / human-required items

| Gate | State |
|---|---|
| Public repository | PENDING |
| Final content-origin audit | PENDING |
| Final README review | PENDING |
| Public demo links | PENDING |
| <=3 minute demo video | HUMAN_REQUIRED |
| Submission form | HUMAN_REQUIRED |
| Final release SHA + evidence hash ledger | PENDING |

## Release ceiling

Current overall state:

`SUBMISSION_CANDIDATE / TRACK03_EXECUTED / TRACK01_AND_TRACK02_SYNTHETIC_IMPLEMENTATIONS_PRESENT / DATASET_PULL_PARTIAL / CURRENT_CI_RUNNER_BLOCKED / PUBLIC_DEPLOYMENT_PENDING / CONTENT_ORIGIN_AUDIT_PENDING`

No author signature, live HydraDB Merkle/MMR commitment, independent replication, or real-world vulnerability exposure is claimed by this ledger.
