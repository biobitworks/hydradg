# HydraDG Control — Next Studio Action V4 — Frozen V11 Scorer Reconciliation

Date: 2026-08-21

Authority: Byron + ChatGPT primary control plane.

Execution host: `magicSTUDIObox.local`
Controller/mirror: `magicPRObox.local`
GitHub origin: synchronization arbiter.

This action is **ZERO MODEL CALLS** and must not interrupt a valid V11 run.

## Purpose

Reconcile Dataset Readiness V3 scorer identity against the scorer actually executed by frozen V11 SHA:

`0c7e6b67c6e80b8eec4a9db9c8edb8a001290831`

V3 incorrectly attributed nonexistent functions `score_track01_canonical` and `score_track03_canonical` to V11. Preserve V3 unchanged.

## 1. Preconditions

- Sync current control branch from origin.
- Verify `magicSTUDIObox.local / Mac13,1`.
- Verify V11 deterministic watchdog state only; do not stop or modify V11 if it is valid.
- Execute no Ollama/Ollarma/model inference.
- Perform no external HTTP requests.

## 2. Freeze exact V11 source bytes

Use Git itself, not the mutable worktree, to materialize exact frozen source bytes:

```text
git show 0c7e6b67c6e80b8eec4a9db9c8edb8a001290831:scripts/run_studio_daisy_realdata_v11_20260821.py
```

Record:

- `V11_FROZEN_RUNNER_GIT_SHA`
- `V11_FROZEN_RUNNER_FILE_SHA256`
- `CURRENT_WORKTREE_RUNNER_FILE_SHA256`
- `FROZEN_VS_WORKTREE_FILE_IDENTITY_GATE`

Do not require the mutable worktree file to match in order to preserve an already-running process; simply report the result.

## 3. Extract exact scoring contract

From the frozen file bytes, locate the exact inline source regions under `evaluate_slot_v11` that assign `is_correct` for Track 01 and Track 03.

Record canonical source text and SHA-256 for each region:

- `TRACK01_V11_SCORER_SOURCE_SHA256`
- `TRACK03_V11_SCORER_SOURCE_SHA256`

The frozen V11 rules are expected to be equivalent to:

Track 01:

```python
ref_ans = case_obj["eval_reference"].get("gold_answer", "").lower()
is_correct = any(word.lower() in raw_text.lower() for word in ref_ans.split() if len(word) > 4) if ref_ans else False
```

Track 03:

```python
ref_ans = case_obj["eval_reference"].get("gold_answer", "").lower()
is_correct = (ref_ans in raw_text.lower()) if ref_ans else False
```

Do not mark PASS from these expected snippets alone; locate them in exact frozen bytes.

## 4. Direct deterministic fixture execution of frozen V11 branch

Preferred method:

- load the exact frozen V11 module from Git-materialized bytes into a temporary audit namespace;
- monkeypatch `urllib.request.urlopen` so it cannot access the network and instead returns deterministic canned Ollama JSON bytes;
- redirect `RAW_OUTPUT_BANK`, custody turn output, and any other writes to a temporary V4 audit sandbox;
- call the exact frozen `evaluate_slot_v11` implementation with synthetic fixture case objects and minimal synthetic model metadata;
- ensure no real Ollama call occurs.

Use synthetic fixture inputs only. Never label them benchmark cases.

Test at minimum:

### Track 01

1. positive where a >4-character gold token appears in response -> `SUCCESS_CORRECT`
2. negative where no qualifying gold token appears -> `SUCCESS_INCORRECT`
3. boundary proving <=4-character gold tokens are ignored
4. case-insensitive matching

### Track 03

1. exact positive
2. negative
3. gold-answer substring embedded in longer response -> positive
4. case-insensitive matching
5. whitespace boundary showing exact frozen behavior without invented normalization

For every fixture preserve:

- fixture ID
- synthetic status
- input SHA-256
- canned transport SHA-256
- observed terminal state
- expected terminal state
- exact frozen runner SHA

Require all fixtures to match expected behavior.

## 5. Zero-call proof

Produce evidence that:

- Ollama/Ollarma generation calls executed = 0
- external HTTP calls executed = 0
- fixture transport was monkeypatched/in-memory/local only

`ZERO_MODEL_CALL_GATE=PASS` only if this is mechanically established.

## 6. Gates

Return:

```text
V11_FROZEN_RUNNER_SOURCE_GATE=
FROZEN_VS_WORKTREE_FILE_IDENTITY_GATE=
TRACK01_V11_SCORER_SOURCE_IDENTITY_GATE=
TRACK03_V11_SCORER_SOURCE_IDENTITY_GATE=
TRACK01_V11_DIRECT_FIXTURE_GATE=
TRACK03_V11_DIRECT_FIXTURE_GATE=
ZERO_MODEL_CALL_GATE=
AUDIT_EXECUTION_HOST_BINDING_GATE=
```

Do not use the V3 reimplemented scorer functions as proof.

## 7. Dataset state after V4

If V4 passes:

```text
TRACK01_DATASET_STATE=ORACLE_CONTEXT_DIRECT_BASELINE_READY
HYDRADG_TRACK01_RETRIEVAL_EXECUTION_STATE=NOT_YET_EXECUTED
TRACK03_DATASET_STATE=READY_FOR_FROZEN_V11_SCORER_CONTRACT
TRACK02_DATASET_STATE=BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED
ALL_TRACKS_READY=NO
```

Track 02 remains the next dataset-development problem.

## 8. Git artifacts

Create compact artifacts under:

`eval/studio_daisy_20260821/dataset_audit_v4/`

At minimum:

- `DATASET_READINESS_V4_SCORER_AUDIT.json`
- `V11_FROZEN_RUNNER_IDENTITY.json`
- `V11_SCORER_SOURCE_REGIONS.json`
- `V11_DIRECT_SCORER_FIXTURES.json`
- `HOST_AND_ZERO_CALL_RECEIPT.json`
- `DATASET_READINESS_V4_SHA256SUMS.txt`
- audit script

No large benchmark payloads.

Commit and push to:

`hack-hydra/studio-ollarma-daisy-20260821`

Then stop.

## 9. Return receipt

```text
CURRENT_BRANCH=
CURRENT_HEAD=
ORIGIN_HEAD=
MAGICPRO_HEAD=

V11_PROCESS_STATE=
V11_SLOTS_ACCOUNTED=
V11_SLOTS_EXPECTED=6930

V11_FROZEN_RUNNER_GIT_SHA=
V11_FROZEN_RUNNER_FILE_SHA256=
CURRENT_WORKTREE_RUNNER_FILE_SHA256=
FROZEN_VS_WORKTREE_FILE_IDENTITY_GATE=

TRACK01_V11_SCORER_SOURCE_SHA256=
TRACK03_V11_SCORER_SOURCE_SHA256=
TRACK01_V11_SCORER_SOURCE_IDENTITY_GATE=
TRACK03_V11_SCORER_SOURCE_IDENTITY_GATE=
TRACK01_V11_DIRECT_FIXTURE_GATE=
TRACK03_V11_DIRECT_FIXTURE_GATE=
ZERO_MODEL_CALL_GATE=
AUDIT_EXECUTION_HOST_BINDING_GATE=

TRACK01_DATASET_STATE=
HYDRADG_TRACK01_RETRIEVAL_EXECUTION_STATE=NOT_YET_EXECUTED
TRACK02_DATASET_STATE=BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED
TRACK03_DATASET_STATE=
ALL_TRACKS_READY=NO

EVIDENCE_STATE=
EXPERIMENT_STATE=
FCO_STATE=
FCG_STATE=
HYDRADB_STATE=
EARLIEST_DIVERGENCE=
CLAIM_CEILING=
SIGNATURE_STATE=NOT_SIGNED
MERKLE_MMR_STATE=NOT_COMMITTED

NEXT_SAFE_ACTION=STOP_FOR_BYRON_CHATGPT_REVIEW
FINAL_REVIEW_GATE=DATASET_READINESS_V4_SCORER_RECONCILIATION_COMPLETE__WAIT_FOR_PRIMARY_CONTROL_REVIEW
```
