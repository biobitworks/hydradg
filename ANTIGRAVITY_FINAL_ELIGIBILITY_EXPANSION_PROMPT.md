# Antigravity Prompt — HydraDG Final Eligibility + Controlled Track Expansion

You are working on HydraDG for Hack Hydra 2026.

## HARD STOP: NO DEPLOYMENT / NO PUSH UNTIL HUMAN AUTHORIZATION

Current reviewed evidence branch:
`hack-hydra/final-hosted-fcg-20260820`
reviewed head:
`c62d8d56ce6ab8cbb40a4c5d7120e66f4468cfac`

Do not:
- deploy to Vercel;
- merge to main;
- push a new commit;
- auto-commit from scripts;
- run `git add -A`, `git add .`, or bulk stage unrelated files;
- expose HydraDB tokens;
- weaken tests;
- delete negative/null evidence;
- promote a claim because a receipt filename says PASS.

Work locally in a clean branch/worktree and report the exact diff.

## FCO/FCG operating mode

For every material result preserve:
`source/evidence → transform/tool/model → derived evidence → claim → artifact`

Distinguish:
- directly supplied evidence;
- externally retrieved evidence;
- deterministic transform;
- recomputed result;
- probabilistic model output;
- inference/hypothesis;
- verified empirical result.

A downstream claim may not exceed its weakest dependency.

Do not call anything signed, Merkle-committed, hosted-parity-verified, SeedGraph-admitted, or HydraDB-written unless the actual operation occurred and its evidence/readback exists.

## Immediate audit corrections

### A. Reclassify pseudo local writeback
Inspect:
- `scripts/write_back_to_local_hydradb.py`
- `eval/hosted_migration_20260820/LOCAL_HYDRADB_WRITEBACK_RECEIPT.json`

The current script does not perform HTTP/Bolt HydraDB writes.
It counts local files and emits intended totals.

Required:
- either implement a real HydraDB write/readback using the current HydraDB API, or
- rename/reclassify it as a deterministic planned-count estimator.

Until real network write + readback:
`FULL_LOCAL_HYDRADB_WRITEBACK_NOT_ESTABLISHED`

### B. Fail closed on hosted parity
Inspect:
- `scripts/verify_local_hosted_parity_readback.py`
- `LOCAL_HOSTED_CONVERSATION_PARITY_RECEIPT.json`

Current anti-pattern:
on hosted request failure, hosted counts inherit local counts.

Fix:
- non-200 / timeout / parse error => `FAIL` or `NOT_ESTABLISHED`;
- hosted observed counts must default to null, never local expected counts;
- compare actual FCO ID set, edge tuple set, and content-hash set;
- preserve the historical 36-FCO/24-edge migration receipt only in its historical scope;
- never promote historical parity to the expanded current FCG.

### C. SeedGraph admission
Inspect:
- `generate_seedgraph_admission_receipt.py`
- `SEEDGRAPH_ADMISSION_RECEIPT.json`

Current script hashes/counts a candidate bundle but does not call SeedGraph.

Until real SeedGraph CLI/API admission + readback:
`SEEDGRAPH_CANDIDATE_BUNDLE_HASHED; ACTUAL_SEEDGRAPH_ADMISSION_NOT_ESTABLISHED`

### D. Supersede stale Daisy/model receipts
Do not use as current empirical evidence:
- `MASTER_DAISY_TRAIN_SUMMARY.json`
- `MULTI_MODEL_DATASET_MATRIX_RECEIPT.json`

They contain historical overclaims including signing/provider/energy states.

Use the corrected design artifact:
`EXTENDED_100_CELL_MATRIX_RECEIPT.json`
with:
`SYNTHETIC_100_CELL_MULTI_MODEL_DATASET_MATRIX_DESIGN_ONLY_NOT_MODEL_EXECUTION`
and `signature_state=NOT_SIGNED`.

Never convert the 100-cell design into model-execution evidence.

## Build the final Golden Path page

Make `/eligibility` the final Golden Path step.

Target:
`HOME → CHANGE STATE → READ RESULT → WHY HYDRADB → TRACE FCO → MODELS USED → VERIFY CUSTODY → EVIDENCE → ELIGIBILITY / CASE`

`/best-use` remains the HydraDB technical deep dive.
`/eligibility` becomes the final synthesis.

Required `/eligibility` sections:

1. **Live production vs local/historical HydraDB**
   - current live Vercel: `DEGRADED / HOSTED HYDRADB CANARY NOT CONFIGURED ON THIS DEPLOYMENT`
   - explain server-only endpoint/token/namespace requirement;
   - prior local/Track03 use remains real evidence;
   - historical hosted 36/24 parity is bounded;
   - expanded parity pending.

2. **Official-track fit**
   - Track 03 = strongest executed fit.
   - Track 01 = architecture/data acquired; real benchmark pending.
   - Track 02 = synthetic structural canary; real npm/PyPI graph pending.
   - Best Use HydraDB = strongest cross-cutting award case.
   - State the official multi-track rule: one team may enter multiple tracks, but each submission must be meaningfully distinct. Do not present one HydraDG build as three separate eligible submissions.

3. **Industry terminology matrix**
   Columns:
   `Industry standard | HydraDB capability | HydraDG integration | Evidence state | Gap`
   Include:
   - semantic/vector retrieval;
   - hybrid retrieval;
   - property/metadata filters;
   - knowledge graph;
   - entity resolution;
   - temporal/versioned graph;
   - graph traversal;
   - provenance/lineage;
   - contradiction/supersession;
   - abstention;
   - content dedup/canonical identity;
   - model-agnostic context;
   - deterministic replay;
   - context-state diagnostics.

4. **Executed/null/future experiment matrix**
   Use evidence classes, not marketing labels.

5. **Track 03 full statistics**
   N=500 total, N=470 scored, 30 abstentions.
   K5 A/B/C/D exact Hit@5 and Recall@5.
   K10 retained depth results.
   State:
   `K_DEPTH_EFFECT_OBSERVED`
   `RAW_EQUALS_SEEDGRAPH_AT_FIXED_K`
   `MODEL_BENEFIT_NOT_ESTABLISHED`
   `NOT_END_TO_END_QA`

6. **Information-State Heat Layer**
   Render equations:
   `H=-Σp log2p`
   `Hnorm=H/log2(n)`
   `G*=U*−0.35Hnorm`
   `ΔG*=G*(t)−G*(t−1)`
   `Cloud Drift=100×JSD_base2(Pt||Pref)`
   `TV=1/2 Σ|Pt−Pref|`

   Render deterministic T0/T1/T2 values from the code contract.
   Label:
   `SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY`
   State explicitly:
   backend-agnostic math, but not backend-independent evidence. The score can be computed over any preregistered state distribution; HydraDB supplies a useful versioned graph state source in this project.

7. **Scale economics**
   Render:
   `31,672,976 = 10,854,020 + 20,818,956`
   `reuse = 65.730975%`
   `1,101,473,790 bytes` = declared canonical Parquet footprint, NOT download savings.

   Whole-download byte savings:
   use `scripts/build_download_byte_manifest.py` against real downloaded roots.
   If roots/files are absent:
   `DOWNLOAD_BYTE_SAVINGS_NOT_MEASURED`

8. **Energy/time**
   Correct deterministic scenario:
   `291,465,384,000,000,000 FLOPs`
   `0.809626 Wh theoretical equivalent`
   `measured_energy_wh = null`
   `time_saved = NOT_MEASURED`

9. **Model/no-model ladder**
   - deterministic heuristic/no LLM baseline;
   - open-source Qwen local lane;
   - exact Vithia companion lane using `biobitworks/fco-vithia-fmo-076` and actual Pythia-14M lineage;
   - optional frontier lane only if separately authorized/executed.
   Do not describe Vithia as 7B without evidence.
   Do not use synthetic model matrix rows as executions.

10. **Reproduction**
    Link:
    - `HYDRADB_DATA.md`
    - `scripts/project_fcg_snapshot_to_hydradb.py`
    - `custody/graph/live/nodes.jsonl`
    - `custody/graph/live/edges.jsonl`
    - `docs/JUDGE_REPRODUCE_FROM_SCRATCH.md`
    Explain that the importer really performs HydraDB POST writes/readbacks.
    Current state:
    `PROCEDURE_PRESENT; FRESH_EXPANDED_IMPORT_RECEIPT_PENDING`

11. **Gap matrix**
    Rows:
    - hosted Vercel config;
    - expanded hosted parity;
    - actual SeedGraph admission;
    - actual 20M-scale HydraDB writeback;
    - real Track01 benchmark;
    - real Track02 dependency snapshot;
    - model-assisted extraction ablation;
    - measured token/latency/energy;
    - byte-level acquisition dedup;
    - cryptographic signing/Merkle.

12. **Award case**
    Rank:
    1. Track 03 — strongest currently executed track case.
    2. Best Use of HydraDB — strongest cross-cutting technical case.
    3. Track 01 / Track 02 — adjacent/future fit until distinct real-data submissions satisfy their own gates.

## Repeat experiments by track

### Shared deterministic protocol

For each track:
1. Freeze source revision/bytes.
2. Build SHA-256 manifest.
3. Define graph schema and claim ceiling.
4. Define deterministic baseline.
5. Execute HydraDB ingestion in isolated namespace.
6. Read back exact node IDs/edge tuples/content hashes.
7. Run baseline retrieval/traversal.
8. Run graph treatment.
9. Preserve null/failure.
10. Only then run optional model-assisted extraction.
11. Cache/freeze model output.
12. Re-run deterministic HydraDB evaluation over the frozen model-derived graph.
13. Produce one receipt per cell.
14. Recompute receipt with `--verify`.
15. No deployment until all gates are green.

### Track 01 — Enterprise ontology

Datasets:
- EnterpriseRAG-Bench
- Salesforce HERB where license permits local evaluation

Deterministic graph:
`Source → Document → Mention → RESOLVES_TO → Entity`
`Document/Claim → DERIVED_FROM → Source`
`Claim → CONTRADICTS → Claim`
`Claim → SUPERSEDED_BY → Claim`

Controlled conditions:
A. lexical/raw baseline
B. deterministic heuristic entity-resolution + HydraDB graph
C. model-assisted extraction with exact Qwen runtime receipt
D. Vithia-derived classifier/extractor only if the actual trained model is applicable and executable

Measure:
- source/document count;
- exact-byte manifest;
- node/edge counts;
- entity-resolution precision/recall/F1 if ground truth exists;
- contradiction resolution;
- multi-hop answer correctness;
- abstention correctness;
- Hit@K / Recall@K where defined;
- evidence-path coverage;
- ingest/query latency;
- measured tokens if a model is used;
- byte reuse.

Null is valid:
if graph/entity treatment does not improve the baseline, retain it.

### Track 02 — Dependency / code graph

Build a frozen real npm or PyPI snapshot with exact timestamp and source rights.
Use OSV/GHSA advisory evidence.

Graph:
`Service → RESOLVES → PackageVersion`
`PackageVersion → DEPENDS_ON → PackageVersion`
`PackageVersion → PUBLISHED_BY / MAINTAINED_BY → Maintainer`
`PackageVersion → AFFECTED_BY → Advisory`
`Lockfile → RESOLVES → PackageVersion`

Ground-truth oracle:
independent Python reverse dependency closure over the same frozen edge set.

Conditions:
A. independent Python oracle
B. HydraDB traversal
C. optional name/semantic typosquat ranking as a separate task

Require exact exposed-service set equality before calling traversal correct.

Measure:
- nodes/edges;
- closure size;
- path completeness;
- false positive/negative exposed services;
- query latency;
- patch state 0→2→1→0 canary;
- version-window correctness.

Do not mix semantic typosquat ranking with deterministic blast-radius correctness.

### Track 03 — Memory/context

Datasets:
- frozen LongMemEval-S full500;
- optionally LongMemEval V2 / BEAM as separate receipts.

Preserve current K5/K10 matrix.

Model conditions:
A. heuristic extraction, K5
B. heuristic extraction, K10
C. Qwen extraction, K5
D. Qwen extraction, K10
E. Vithia companion extraction/classification only if task-compatible, K5/K10

For model conditions:
- exact model card;
- runtime digest;
- tokenizer;
- prompt;
- sampling;
- raw model response hash;
- transformed graph hash.

Then freeze model-derived graph and run retrieval deterministically.

Measure:
- Hit@K;
- Recall@K;
- abstention;
- evidence-path coverage;
- stale/superseded fact rate;
- contradiction retrieval;
- token budget;
- query latency;
- model latency;
- measured energy only if actual instrumentation is available.

No frontier comparison unless separately authorized.

## Information-State Heat Layer experiment contract

Do not retrofit arbitrary distributions after seeing outcomes.

For each track define a fixed categorical state vector before execution.

Example Track 03 candidate:
`P=[answer-bearing-current, stale/superseded, contradictory, irrelevant/other]`

Define U* deterministically from an error/burden rule before running.

Then compute the same H/Hnorm/G*/ΔG*/JSD/TV functions across:
- baseline;
- perturbation/degradation;
- graph treatment;
- restoration;
- model-assisted treatment.

Use this as an additional diagnostic, never as a replacement for task metrics.

## Deliverables before asking to deploy

- updated `/eligibility`;
- GoldenPathRail patch;
- siteFcg patch;
- corrected claim-state matrix JSON;
- deterministic figures generated from receipt data;
- actual byte manifest if source roots available;
- fixed parity verifier;
- fixed/reclassified writeback receipt;
- fixed/reclassified SeedGraph receipt;
- test output;
- exact candidate SHA or local diff;
- list of anything still NOT_ESTABLISHED.

Stop before push/deploy and request human authorization.
