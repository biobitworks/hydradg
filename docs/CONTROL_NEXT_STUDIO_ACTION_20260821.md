# HydraDG Control — Next Studio Action (2026-08-21)

Authority: Byron P. Lee + ChatGPT control plane.

Purpose: execute a **zero-model-call Dataset Readiness V2 audit** on `magicSTUDIObox.local`. This supersedes the V1 audit only for readiness interpretation; preserve all V1 receipts unchanged as historical evidence.

## Do not change the active scientific run

- Do not modify, restart, stop, or reconfigure a valid V11 execution.
- Do not alter V11 dataset, scorer, prompts, model roster, output policy, or frozen execution SHA.
- This task is deterministic audit-only and must issue **zero model calls**.

## Required V2 gates

### Track 01 — EnterpriseRAG-Bench

Recompute and emit evidence for:

- `TRACK01_QUESTION_SHA_GATE`
- `TRACK01_DOCUMENT_SHA_GATE`
- `TRACK01_ADMISSION_IDENTITY_GATE`
- `TRACK01_ANSWER_LABEL_ISOLATION_GATE`
- `TRACK01_RETRIEVAL_GOLD_LEAKAGE_GATE`
- `TRACK01_ORACLE_BASELINE_CLASSIFICATION`
- `TRACK01_SCORER_IDENTITY_GATE`
- `TRACK01_SCORER_SMOKE_GATE`

Important: the V1 manifest uses `expected_doc_ids` to select model-visible documents. Treat that route as `ORACLE_CONTEXT_DIRECT_BASELINE`; do **not** classify it as a clean HydraDG retrieval evaluation.

The V2 audit must compare the exact admitted 300 IDs against a frozen/preregistered admission manifest or contract. `head(300)` alone is not sufficient evidence of intended admission identity.

### Track 03 — LongMemEval-S-full500

Recompute and emit:

- exact ordered/raw 500 case-ID set
- exact `PRIMARY_470` ID set and deterministic root
- exact `SECONDARY_30` ID set and deterministic root
- independent expected secondary-ID set/root
- `TRACK03_EXACT_SECONDARY_ID_SET_GATE`
- `TRACK03_SCORER_IDENTITY_GATE`
- `TRACK03_SCORER_SMOKE_GATE`

The gate must compare exact IDs, not only `len(secondary)==30`.

### Track 02 — HydraBlast-Real-Deps

Preserve current state as blocked unless a real non-synthetic source/case/scorer contract already exists in canonical project evidence.

Do not invent or synthesize cases to satisfy an expected count.

### Host binding

Require and record:

- hostname exactly `magicSTUDIObox.local`
- hardware identity consistent with the preregistered Studio host
- zero Ollama/Ollarma generation requests during this audit

Emit:

- `AUDIT_EXECUTION_HOST_BINDING_GATE`
- `ZERO_MODEL_CALL_GATE`

## Output namespace

Create a new successor namespace, do not overwrite V1:

`eval/studio_daisy_20260821/dataset_audit_v2/`

Required artifacts:

- `DATASET_READINESS_V2_AUDIT.json`
- `DATASET_READINESS_V2_SHA256SUMS.txt`
- `TRACK01_ADMISSION_ID_ROOT.json`
- `TRACK03_PRIMARY_470_ID_ROOT.json`
- `TRACK03_SECONDARY_30_ID_ROOT.json`
- `SCORER_CONTRACT_AUDIT.json`
- `HOST_BINDING_RECEIPT.json`

Do not commit a 225 MB raw manifest to Git. Keep large payloads on the governed local evidence store and commit compact ID/root/hash receipts sufficient to verify byte identity and case membership.

## Decision policy

Do not call `ALL_TRACKS_READY=YES` while Track 02 is blocked.

Do not call Track 01 `HYDRADG_RETRIEVAL_READY` while retrieval-gold information selects model-visible evidence.

Allowed bounded classification for the existing Track 01 V1 route:

`ORACLE_CONTEXT_DIRECT_BASELINE_READY`

Track 03 may be promoted to `DATASET_READY` only if exact ID-set equality, scorer identity/smoke, source SHA, duplicate, EVAL_ONLY, and host gates all independently pass.

## Git synchronization

Before execution, sync the controller checkout to the current branch head. Do not move the frozen V11 execution checkout if it is active.

After deterministic V2 artifacts are complete:

1. commit only compact V2 receipts + audit code;
2. push to `hack-hydra/studio-ollarma-daisy-20260821`;
3. synchronize `magicPRObox` mirror;
4. stop for Byron/ChatGPT review.

Do not start a new scientific model experiment from this task.

## Return block

```text
CURRENT_BRANCH=
CURRENT_HEAD=

AUDIT_V2_HOST=
AUDIT_V2_SHA256=
ZERO_MODEL_CALL_GATE=
AUDIT_EXECUTION_HOST_BINDING_GATE=

TRACK01_QUESTION_SHA_GATE=
TRACK01_DOCUMENT_SHA_GATE=
TRACK01_ADMISSION_IDENTITY_GATE=
TRACK01_ANSWER_LABEL_ISOLATION_GATE=
TRACK01_RETRIEVAL_GOLD_LEAKAGE_GATE=
TRACK01_ORACLE_BASELINE_CLASSIFICATION=
TRACK01_SCORER_IDENTITY_GATE=
TRACK01_SCORER_SMOKE_GATE=

TRACK02_DATASET_READY=

TRACK03_PRIMARY_ID_ROOT=
TRACK03_SECONDARY_ID_ROOT=
TRACK03_EXACT_SECONDARY_ID_SET_GATE=
TRACK03_SCORER_IDENTITY_GATE=
TRACK03_SCORER_SMOKE_GATE=

ALL_TRACKS_READY=
EARLIEST_DIVERGENCE=
CLAIM_CEILING=

SIGNATURE_STATE=NOT_SIGNED
MERKLE_MMR_STATE=NOT_COMMITTED

NEXT_SAFE_ACTION=STOP_FOR_BYRON_CHATGPT_REVIEW
FINAL_REVIEW_GATE=DATASET_READINESS_V2_COMPLETE__REVIEW_REQUIRED
```
