# HydraDG Track 03 — Provider Execution Matrix

Status: SOURCE-REVIEWED_EXECUTION_PLAN
Updated: 2026-08-18
Scope: Hack Hydra Track 03 / Best Use of HydraDB

## Rule

HydraDB remains the graph substrate under evaluation. External providers are execution or external-retrieval surfaces; they are not substitutes for HydraDB and must not be described as databases when they are not databases.

Provider credentials remain local secret material. Receipts may preserve provider name, run/job identifier, runtime/image, non-secret parameters, start/end times, input/output SHA-256 values and cost/usage metadata when available. Never commit credential values.

## Recommended routing order

1. `magicSTUDIObox`: authoritative persistent HydraDB + local Ollarma/model path when available.
2. `Modal`: preferred burst runner for parallel frozen benchmark/evaluation shards.
3. `Kaggle`: free/budgeted GPU batch fallback for workloads that fit notebook/session constraints.
4. `Daytona`: isolated fresh-clone/reproduction and clean-room execution; useful for install/replay verification, not the primary graph database.
5. `GMI Cloud`: GPU/container fallback for workloads that require more dedicated accelerator capacity; treat as potentially billable and require an explicit budget gate before resource creation.
6. `Exa`: optional externally retrieved evidence/search lane for retrieval perturbation experiments; snapshot and hash returned evidence before admitting it to a reproducibility claim.

## Provider-specific use

### Modal

Official documentation describes Modal as serverless compute for compute-intensive applications, large-scale batch workflows and job queues. Modal API authentication can use `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` environment variables or a local Modal profile.

HydraDG use:
- parallelize frozen smoke80/full500 item shards after the evaluation protocol is frozen;
- CPU-heavy bootstrap/permutation analyses if local execution is slow;
- optional GPU model inference for fixed model-based baselines;
- return raw per-item JSONL + run receipt to the canonical evidence directory.

Do not use Modal to create a second mutable authority for graph state. The canonical graph/query semantics remain pinned to HydraDB.

Source: https://modal.com/docs
Source: https://modal.com/docs/guide/trigger-deployed-functions

### Daytona

Official Daytona SDK documentation supports programmatic sandbox creation and command/code execution. `DAYTONA_API_KEY` is the documented environment variable for API-key authentication; `DAYTONA_API_URL` and `DAYTONA_TARGET` configure the API endpoint and target region.

HydraDG use:
- clean-room fresh clone of the public candidate repository;
- install-from-scratch test;
- run deterministic evaluator/statistics code in an isolated sandbox;
- reproduce a frozen subset and compare output hashes;
- optionally create a reproducibility receipt from a fresh environment.

Daytona is an execution sandbox platform here, not a graph database and not the primary benchmark substrate.

Source: https://www.daytona.io/docs/api-keys
Source: https://www.daytona.io/docs/en/python-sdk/

### GMI Cloud

Official GMI Cloud documentation exposes authenticated REST APIs for infrastructure including containers and GPU compute. The referenced API guide uses Bearer-token API credentials and demonstrates creating and monitoring container workloads.

HydraDG use:
- fallback for a frozen GPU/model workload that does not fit local, Modal or Kaggle constraints;
- create a bounded container only after an explicit budget/cost gate;
- record container template/product/region and resource metadata without secret values;
- destroy/stop resources after the bounded job completes.

`GMI_API_KEY` and `GMI_CLOUD_API_KEY` are HydraDG probe conventions, not names asserted by the referenced GMI documentation.

Source: https://docs.gmicloud.ai/api-reference/introduction

### Exa

Official Exa documentation exposes search types from low-latency search through deep/deep-reasoning and supports structured outputs and content highlights. The documented environment variable is `EXA_API_KEY`.

HydraDG use:
- optional dynamic external-retrieval baseline;
- retrieval perturbation experiment: retrieve an external fact/evidence candidate, snapshot the exact response, hash it, convert admitted evidence into FCOs, then test supersession/contradiction/first-divergence traversal;
- never mix live unsnapshotted Exa output into the deterministic core score.

This lane can strengthen the demo because it shows how fresh external information becomes a versioned graph dependency rather than silently overwriting memory.

Source: https://exa.ai/docs/reference/search-api-guide
Source: https://exa.ai/docs/reference/quickstart

## Best Use experiment matrix

System axis:
- `S0_FLAT`: flat deterministic lookup.
- `S1_VECTOR`: vector/semantic retrieval with the same evidence budget.
- `S2_HYDRADB_GRAPH`: HydraDB graph-native relationships/traversal without full FCO/FCG policy.
- `S3_HYDRADG_FULL`: HydraDB + FCO/FCG admission, first-divergence, affected-set and recovery logic.

Condition axis:
- `A_REFERENCE`
- `B_FACT_PERTURBATION`
- `C_DERIVED_STATE_PERTURBATION`
- `D_RECOVERY`

The critical Best Use claim is supported only if paired results show that graph-native variants materially improve relational endpoints such as first-divergence localization, affected-set reconstruction, historical-state reconstruction, unsupported-claim rejection or recovery classification. Latency/context overhead must be reported alongside accuracy/evidence benefits.

## Execution sequence

1. Run `scripts/provider_capability_probe.sh` on magicPRObox. It reports presence only and never credential values.
2. Prefer local smoke80 if magicSTUDIObox transport/runtime is healthy; otherwise use Modal for compute-only shards while keeping HydraDB semantics fixed.
3. Run the same frozen per-item inputs across S0-S3 and A-D.
4. Write raw per-item JSONL. Do not aggregate away failures.
5. Run `scripts/track03_stats.py` with seed `20260818` and 10,000 bootstrap resamples.
6. Review smoke80 failure classes and effect sizes; then freeze evaluator/query/config/input manifests.
7. Run full500 only after the freeze receipt exists.
8. Run one Daytona fresh-clone reproduction of the frozen evaluator/package and compare hashes/results.
9. Use Exa only as a separately labeled external-evidence demonstration/ablation unless it is pre-registered into the quantitative protocol.
10. Use GMI only if required and only after a bounded cost authorization.

## Claim ceilings

- Provider capability probe -> `LOCAL_PROVIDER_TOOL_CONFIG_AND_CREDENTIAL_PRESENCE_ONLY`.
- Successful remote job -> `REMOTE_EXECUTION_RECEIPT` until outputs are retrieved and hashed.
- Retrieved + hashed outputs -> `RECOMPUTED_OR_EXTERNALLY_EXECUTED_BENCHMARK_EVIDENCE`, depending on execution class.
- Statistical comparison -> `BENCHMARK_RESULT`, not general correctness verification.
- Daytona match -> bounded cross-environment reproduction for the tested artifact/config only.
- Exa output -> `EXTERNALLY_RETRIEVED_EVIDENCE` until admitted by the declared FCO/FCG policy.
- No provider run implies no provider result; unavailable routes remain `NOT_RUN`.
