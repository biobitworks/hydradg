# HydraDG Final Golden-Path Eligibility / Award Dossier — Implementation Plan

Status: LOCAL RELEASE-CANDIDATE PACKAGE ONLY — DO NOT DEPLOY YET
Baseline evidence branch reviewed: `hack-hydra/final-hosted-fcg-20260820`
Reviewed head: `c62d8d56ce6ab8cbb40a4c5d7120e66f4468cfac`

## Goal

Make `/eligibility` the final page of the judge Golden Path. It should answer, in one place:

1. Did HydraDG actually use HydraDB?
2. Why does the current live Vercel deployment say hosted HydraDB is unavailable?
3. What was executed locally, what was historically hosted, what is null/negative, and what remains unestablished?
4. Which Hack Hydra track is the strongest fit?
5. Why is HydraDG a strong Best Use of HydraDB candidate?
6. How does HydraDG map to standard graph/RAG/agent-memory terminology?
7. What is novel versus standard?
8. What did the deterministic experiments actually show?
9. What does K=5 versus K=10 mean?
10. What changes when no model, an open-source model, or the Vithia companion model is used?
11. What data/storage/compute savings are counted, measured, theoretical, or still unknown?
12. How can a judge reproduce the HydraDB projection from GitHub?
13. What are the remaining gaps and the exact promotion gates?

## Golden Path

Current:
`HOME → CHANGE STATE → READ RESULT → WHY HYDRADB → TRACE FCO → MODELS USED → VERIFY CUSTODY → EVIDENCE`

Target:
`HOME → CHANGE STATE → READ RESULT → WHY HYDRADB → TRACE FCO → MODELS USED → VERIFY CUSTODY → EVIDENCE → ELIGIBILITY / CASE`

`/best-use` remains the technical deep dive.
`/eligibility` becomes the final synthesis and award case.

## Required status language

### Live Vercel deployment
`DEGRADED / HOSTED HYDRADB CANARY NOT CONFIGURED ON THIS DEPLOYMENT`

Meaning:
- The current live deployment cannot perform a live server-side HydraDB canary.
- This is a deployment/configuration state, not evidence that HydraDG never used HydraDB.
- Server-only HydraDB endpoint/token/namespace configuration must be present and verified.
- Never expose HydraDB credentials through browser code or `NEXT_PUBLIC_*`.

### Executed HydraDB evidence
Retain the executed historical/local evidence already in the repository, including:
- Track 03 LongMemEval-S full500 graph/evaluation lane.
- 23,867 sessions.
- 4,776 entities.
- 3,506 facts.
- 470 retrieval-scored cases.
- 30 abstentions.
- Context-vs-entropy HydraDB readback marked SUCCESS:
  - 18,567 raw findings.
  - 18,555 context-classified.
  - 12 abstentions.
  - 99.9354% classification coverage.
- Historical hosted parity: 36 canonical FCOs / 24 edges, bounded to that historical scope only.

### Explicitly NOT established
Do not promote:
- Expanded current hosted parity.
- Full 20.82M-node local HydraDB writeback.
- Actual external SeedGraph admission of the 653-node / 1,692-edge conversation bundle.
- Whole-download byte savings.
- Measured energy savings.
- Model benefit in the primary K-depth matrix.
- Project Ed25519 signing or Merkle/MMR commitment.

## Critical audit findings to show

### 1. Pseudo writeback receipt
`LOCAL_HYDRADB_WRITEBACK_RECEIPT.json` says PASS, but
`scripts/write_back_to_local_hydradb.py` performs no network request.
It derives intended counts from local files and emits a receipt.

Final classification:
`PLANNED/DERIVED_WRITEBACK_COUNT_ONLY — NOT_EXECUTED_HYDRADB_WRITEBACK`

### 2. Pseudo hosted parity fallback
`verify_local_hosted_parity_readback.py` defaults hosted counts to local counts.
If the hosted request fails, it reports `LOCAL_FALLBACK` and can still calculate zero deltas.

Final classification:
`HOSTED_PARITY_NOT_ESTABLISHED_ON_NON_200`

Future verifier must:
- fail on non-200;
- never substitute local expected counts for hosted observed counts;
- compare actual FCO IDs, edge tuples, and content hashes, not counts alone.

### 3. SeedGraph admission receipt
`generate_seedgraph_admission_receipt.py` hashes/counts the candidate bundle but does not invoke SeedGraph.

Final classification:
`SEEDGRAPH_CANDIDATE_BUNDLE_HASHED — ACTUAL_ADMISSION_NOT_ESTABLISHED`

### 4. Older Daisy model/energy receipts
Some older receipts use `SIGNED_WITH_AUTHOR_PUBLIC_KEY` even though the value is an FCO identity, not an Ed25519 public key receipt, and older energy calculations were about 1,000× too large.

Final classification:
`HISTORICAL_SUPERSEDED_RECEIPT — DO_NOT_USE_FOR_CURRENT_CLAIMS`

Use the corrected synthetic 100-cell design:
`SYNTHETIC_100_CELL_MULTI_MODEL_DATASET_MATRIX_DESIGN_ONLY_NOT_MODEL_EXECUTION`
and `signature_state=NOT_SIGNED`.

## Track positioning

### Track 03 — strongest primary fit
Official problem:
cross-session memory, chronology, overwritten facts, abstention.

HydraDG executed:
- LongMemEval-S full500.
- Temporal/session/fact/entity graph.
- `SUPERSEDED_BY` and `CONTRADICTS`.
- K=5 result retained even though richer graph treatments did not beat A/reference.
- K=10 depth ablation improved retrieval metrics but reduced evidence-path density.
- RAW and SeedGraph were identical at fixed K in the retained matrix.

Recommendation:
`PRIMARY TRACK / STRONGEST CURRENT AWARD CASE`

### Track 01 — strong architecture fit, real benchmark still pending
Official problem:
enterprise ontology, aliases, contradictions, multi-hop reasoning, abstention.

HydraDG has:
- EnterpriseRAG-Bench and HERB acquisition/hash state.
- ontology/entity-resolution design;
- exact identity/provenance/supersession machinery.

Missing:
- full real corpus atomization into HydraDB;
- real entity-resolution benchmark;
- contradiction/current-state benchmark.

Recommendation:
`FUTURE / ADJACENT TRACK FIT — DO NOT CLAIM TRACK 01 WIN YET`

### Track 02 — graph structure fit, real ecosystem lane pending
Official problem:
reverse dependency closure, versioned packages, blast radius, code graph context.

HydraDG has:
- deterministic synthetic canary:
  `reference 0 → poison 2 → partial repair 1 → full repair 0`;
- independent Python closure vs HydraDB design.

Missing:
- frozen real npm/PyPI snapshot;
- OSV/GHSA version evidence;
- real reverse-closure evaluation.

Recommendation:
`FUTURE / ADJACENT TRACK FIT — DO NOT CLAIM TRACK 02 WIN YET`

### Best Use of HydraDB — strongest cross-cutting case
Use:
- content-addressed identities;
- typed custody/context edges;
- temporal/supersession/contradiction traversal;
- null/abstention retention;
- deterministic calculators;
- graph-native reproduction;
- backend-degradation visibility;
- context-state diagnostics.

## K-depth statistics

Scored N = 470; abstentions = 30.

K=5:
- A Hit@5 = 0.96383 ≈ 453/470
- D Hit@5 = 0.94468 ≈ 444/470
- A Recall@5 = 0.90660
- D Recall@5 = 0.84603
- evidence-path coverage = 0.63787
- B/C/D did not establish a positive Hit@5 advantage over A.

K=10:
- A Hit@10 = 0.97872 ≈ 460/470
- D Hit@10 = 0.97021 ≈ 456/470
- A Recall@10 = 0.94535
- D Recall@10 = 0.92273
- evidence-path coverage = 0.51511

K10 - K5:
- A Hit: +1.489 percentage points
- A Recall: +3.875 pp
- D Hit: +2.553 pp
- D Recall: +7.670 pp
- evidence-path coverage: -12.276 pp

Interpretation:
`DEPTH/CUTOFF EFFECT OBSERVED; REPRESENTATION BENEFIT NOT OBSERVED; MODEL BENEFIT NOT ESTABLISHED`

Do not claim statistical significance without the paired per-case outcome vectors / a retained paired-statistics receipt.

## Information-State Heat Layer

Backend-agnostic deterministic diagnostic over a declared state distribution.

For a declared probability vector P:
- `H(P) = -Σ p_i log2(p_i)`
- `Hnorm(P) = H(P) / log2(n)`
- `G* = U* - 0.35 × Hnorm`
- `ΔG*(t) = G*(t) - G*(t-1)`
- `Cloud Drift = 100 × JSD_base2(P_t || P_reference)`
- `Mutation distance = TV(P_t, P_reference)`
- `Restoration gain = max(0, TV_previous - TV_current)`

`G*` and `ΔG*` are dimensionless information-state diagnostics.
They are not physical Gibbs free energy.

Current deterministic synthetic fixture:

| State | P | U* | H bits | Hnorm | G* | ΔG* | Cloud Drift | TV |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| T0 reference | [0.88,0.08,0.04] | .08 | .639556 | .403515 | -.061230 | 0 | 0 | 0 |
| T1 mutation | [0.18,0.72,0.10] | .82 | 1.118731 | .705841 | .572956 | .634186 | 40.362864 | .70 |
| T2 restoration | [0.76,0.14,0.10] | .20 | 1.030209 | .649989 | -.027496 | -.600452 | 1.872865 | .12 |

T2 restoration gain = 0.58 TV units.

Claim:
`SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY`

Future use:
the same formulas can run over local/private/enterprise state distributions regardless of backend.
Comparisons are valid only when the category definition and U* contract are preregistered and held fixed.

## Scale economics

Current retained count accounting:
- raw word + sentence occurrences = 31,672,976
- canonical unique keys = 10,854,020
- repeated occurrences = 20,818,956
- identity reuse = 65.730975%

These are deterministic arithmetic over retained accounting inputs.
Some upstream dataset counts are declared/estimated rather than a fresh independent full-corpus enumeration.

Canonical Parquet declared footprint:
`1,101,473,790 bytes`

Do NOT call this download savings.

Whole-download byte savings:
`NOT_MEASURED`

New deterministic builder exists:
`scripts/build_download_byte_manifest.py`

Required real measurement:
`path + size_bytes + sha256` for every acquired file.

## Energy / time

Correct theoretical 7B scenario:
`2 × 7,000,000,000 × 20,818,956 = 291,465,384,000,000,000 FLOPs`

Under the explicit efficiency assumption:
`100,000,000,000,000 FLOP/s/W`

Energy-equivalent:
`291,465,384,000,000,000 / 100,000,000,000,000 / 3600 = 0.809626 Wh`

State:
`THEORETICAL_EQUIVALENT_ONLY`

Measured energy:
`NULL`

Time saved:
`NOT_MEASURED`

A real time claim requires measured throughput, e.g.:
`time_saved_seconds = measured_delta_tokens / measured_tokens_per_second`
or
`time_saved_seconds = theoretical_flops_avoided / measured_effective_flops_per_second`.

## Model lanes

### Lane 0 — no model
Primary K5/K10 experiment:
`MODEL = NONE`
This is the deterministic baseline.

### Lane 1 — open-source local models
Candidates only when actually executed and exact runtime identity is captured:
- `qwen2.5-coder:7b`
- `qwen2.5:7b`

Need:
- Ollama digest;
- tokenizer/version;
- prompt;
- sampling config;
- output receipt;
- cached model-derived extraction before deterministic retrieval comparison.

### Lane 2 — Vithia companion
Use exact evidence identity:
`biobitworks/fco-vithia-fmo-076`
with its actual base/model-card lineage.
Do not call it a 7B model unless a separately evidenced 7B Vithia exists.

Current role:
supplementary provenance/training model lane, not Track 03 retrieval driver.

### Lane 3 — frontier model
Not required.
If tested later:
freeze same input/retrieved evidence/prompt/context budget/provider snapshot/sampling/scoring.
Do not claim local-vs-frontier superiority until actually run.

## Reproduction path

The repository already documents the proper HydraDB path:

`custody/graph/live/nodes.jsonl`
+
`custody/graph/live/edges.jsonl`
→
`scripts/project_fcg_snapshot_to_hydradb.py`
→
isolated HydraDB namespace
→
node/edge/root readback
→
`HYDRADB_FCG_IMPORT_RECEIPT.json`

The importer:
- performs real HTTP POSTs;
- requires `--allow-write`;
- rejects unsafe/default namespaces;
- checks duplicate IDs;
- checks edge endpoints/predicates;
- reads back node count, edge count, and expected experiment root;
- exits non-zero on mismatch.

Current gap:
the latest branch does not retain a fresh `repro/receipts/HYDRADB_FCG_IMPORT_RECEIPT.json`.
Therefore:
`REPROCEDIBLE PROCEDURE PRESENT; FRESH EXPANDED REPRO RECEIPT PENDING`

## Deployment promotion gate

Do not deploy until explicitly authorized later this afternoon.

Before deployment:
1. Fix/reclassify pseudo writeback/parity/SeedGraph receipts.
2. Build final `/eligibility`.
3. Add `/eligibility` as last Golden Path step.
4. Update site FCG Golden Path.
5. Run deterministic calculation verification.
6. Run build/typecheck/routes.
7. Run secret scan.
8. Check current live deployment SHA.
9. Configure server-only hosted HydraDB environment if available.
10. Run live `/api/graph/status`.
11. Run fresh isolated FCG→HydraDB import/readback if infrastructure permits.
12. Freeze exact successor SHA.
13. Only then promote production.
