# HydraDG Control — Next Studio Action V3 — 2026-08-21

## Authority

Byron + ChatGPT remain the primary scientific/control plane.

Antigravity is a bounded operator.

`magicSTUDIObox.local` is the only scientific/model execution host.

GitHub origin is the synchronization arbiter.

## Current reviewed state

Dataset Readiness V2 commit:

`8783a0da7334af02308e15b770b583bf1ca3fba4`

Independent V2 review commit:

`66d1a8b32f8ecfaaa0390a7f4333306f7605ac64`

V2 is `PARTIAL_PASS__SUCCESSOR_ZERO_MODEL_AUDIT_REQUIRED`.

Do not rewrite V1 or V2 artifacts.

Do not interrupt a valid active V11 execution.

## Authorized action

Execute exactly one successor:

`DATASET_READINESS_V3_INDEPENDENT_GATE_AUDIT`

This is a deterministic **zero-model-call** audit only.

No new benchmark inference, HydraDB experimental writeback, Vercel deployment, model/configuration changes, or Track 02 case fabrication are authorized.

## Gate 1 — host binding

Require:

- hostname = `magicSTUDIObox.local`
- hardware model = `Mac13,1`

Fail closed otherwise.

## Gate 2 — Track 01 source and admission contract

Recompute from exact source bytes:

- question parquet SHA-256
- document parquet SHA-256
- raw row count
- duplicate `question_id` count

Preserve the existing deterministic selection if that is the intended contract:

`TRACK01_ADMISSION_RULE=ORDERED_FIRST_300_SOURCE_ROWS`

Compute:

- ordered 300-ID list
- `TRACK01_ORDERED_300_ID_LIST_SHA256`

Do not call this an independent identity match unless an earlier/frozen expected 300-ID artifact exists and is actually compared.

If a committed earlier manifest exists, compare exact ordered IDs and report:

`TRACK01_ADMISSION_CONTINUITY_GATE=PASS|FAIL`

Otherwise:

`TRACK01_ADMISSION_CONTINUITY_GATE=NOT_ESTABLISHED_NO_INDEPENDENT_EXPECTED_ID_LIST`

## Gate 3 — Track 01 lane classification

Preserve the historical route as:

`V1_ORACLE_CONTEXT_DIRECT_BASELINE`

because `expected_doc_ids` selected model-visible documents.

Classify the V2 leakage-free manifest as:

`TRACK01_QUERY_MANIFEST_NO_GOLD_DOC_SELECTION`

Do not call it an oracle baseline and do not call it an executed HydraDG retrieval lane.

Report:

`HYDRADG_TRACK01_RETRIEVAL_EXECUTION_STATE=NOT_YET_EXECUTED`

unless canonical executed evidence proves otherwise.

## Gate 4 — Track 03 independent exact-set comparison

Independently derive current primary/secondary IDs from the frozen source dataset.

Expected secondary IDs must come from an independent committed historical artifact:

`eval/studio_daisy_20260821/dataset_audit/TRACK03_SECONDARY_30_MANIFEST.jsonl`

Extract the expected 30 IDs from that artifact.

Do not create expected and observed sets inside the same loop.

Compute and report:

- `TRACK03_CURRENT_PRIMARY_470_ID_LIST_SHA256`
- `TRACK03_CURRENT_SECONDARY_30_ID_LIST_SHA256`
- `TRACK03_HISTORICAL_EXPECTED_SECONDARY_30_ID_LIST_SHA256`
- exact missing IDs
- exact extra IDs
- `TRACK03_EXACT_SECONDARY_SET_EQUALITY_GATE=PASS|FAIL`

## Gate 5 — terminology correction

Do not call SHA-256(sorted/joined IDs) a Merkle root.

Use:

`CANONICAL_ID_LIST_SHA256`

or

`ID_SET_SHA256`

No Merkle/MMR operation is authorized in V3.

`MERKLE_MMR_STATE=NOT_COMMITTED`

## Gate 6 — actual scorer identity

For Track 01 and Track 03, locate the exact scorer implementation used by the frozen V11 experiment or the canonical scorer contract.

For each scorer report:

- repository-relative path
- Git commit containing it
- file SHA-256
- function name / contract identifier
- scorer parameters / normalization rules

If no actual frozen scorer implementation can be located:

`SCORER_IDENTITY_GATE=BLOCKED_SCORER_IMPLEMENTATION_NOT_FROZEN`

Do not assign literal PASS.

## Gate 7 — actual scorer smoke fixtures

Invoke the actual deterministic scorer implementation, not an inline duplicate simulation.

For each available scorer run at least:

1. positive fixture expected to pass;
2. negative fixture expected to fail;
3. normalization/boundary fixture if applicable.

Record fixture inputs by SHA-256 and actual outputs.

Gate passes only if observed outputs equal frozen expected fixture outputs.

## Gate 8 — Track 02

Track 02 remains:

`BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED`

unless an already-existing canonical real source/case/scorer contract is found.

Do not fabricate or synthesize cases.

## Gate 9 — zero-model-call proof

The V3 auditor itself must contain no Ollama/OpenAI/frontier model inference call.

Record:

- auditor file SHA-256
- static scan for `/api/generate`, `/api/chat`, `ollama run`, model SDK calls
- process/runtime note that the audit performs only deterministic file/process operations

Do not issue any model request merely to prove that no model requests occurred.

## Required V3 artifacts

Create only compact artifacts under:

`eval/studio_daisy_20260821/dataset_audit_v3/`

Required:

- `DATASET_READINESS_V3_AUDIT.json`
- `TRACK01_ADMISSION_CONTRACT.json`
- `TRACK03_INDEPENDENT_SET_COMPARISON.json`
- `SCORER_IDENTITY_AUDIT.json`
- `SCORER_FIXTURE_AUDIT.json`
- `HOST_BINDING_RECEIPT.json`
- `DATASET_READINESS_V3_SHA256SUMS.txt`

Do not commit large raw-payload manifests.

## Git writeback

After V3 completes:

1. commit the V3 auditor + compact receipts only;
2. push to `hack-hydra/studio-ollarma-daisy-20260821`;
3. synchronize `magicPRObox` from origin;
4. stop for Byron/ChatGPT review.

Do not auto-launch another scientific run.

## Return receipt

Return exactly:

```text
CURRENT_BRANCH=
CURRENT_HEAD=
ORIGIN_HEAD=
MAGICPRO_HEAD=

V11_PROCESS_STATE=
V11_PID=
V11_LEASE_STATE=
V11_SLOTS_ACCOUNTED=
V11_SLOTS_EXPECTED=
V11_CURRENT_MODEL=
V11_CURRENT_CASE=
V11_LAST_CHECKPOINT=

DATASET_READINESS_V3_SHA=
AUDITOR_V3_SHA256=
ZERO_MODEL_CALL_GATE=
AUDIT_EXECUTION_HOST_BINDING_GATE=

TRACK01_QUESTION_SHA_GATE=
TRACK01_DOCUMENT_SHA_GATE=
TRACK01_ADMISSION_RULE=
TRACK01_ORDERED_300_ID_LIST_SHA256=
TRACK01_ADMISSION_CONTINUITY_GATE=
TRACK01_V1_ROUTE_CLASSIFICATION=
TRACK01_V2_MANIFEST_CLASSIFICATION=
HYDRADG_TRACK01_RETRIEVAL_EXECUTION_STATE=
TRACK01_SCORER_IDENTITY_GATE=
TRACK01_SCORER_FIXTURE_GATE=
TRACK01_DATASET_STATE=

TRACK02_DATASET_STATE=

TRACK03_CURRENT_PRIMARY_470_ID_LIST_SHA256=
TRACK03_CURRENT_SECONDARY_30_ID_LIST_SHA256=
TRACK03_HISTORICAL_EXPECTED_SECONDARY_30_ID_LIST_SHA256=
TRACK03_SECONDARY_MISSING_IDS=
TRACK03_SECONDARY_EXTRA_IDS=
TRACK03_EXACT_SECONDARY_SET_EQUALITY_GATE=
TRACK03_SCORER_IDENTITY_GATE=
TRACK03_SCORER_FIXTURE_GATE=
TRACK03_DATASET_STATE=

ALL_TRACKS_READY=

EVIDENCE_STATE=
EXPERIMENT_STATE=
FCO_STATE=
FCG_STATE=
HYDRADB_STATE=
EARLIEST_DIVERGENCE=
CLAIM_CEILING=
SIGNATURE_STATE=
MERKLE_MMR_STATE=

NEXT_SAFE_ACTION=STOP_FOR_BYRON_CHATGPT_REVIEW
FINAL_REVIEW_GATE=DATASET_READINESS_V3_COMPLETE__WAIT_FOR_PRIMARY_CONTROL_REVIEW
```
