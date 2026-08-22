# CONTROL — Next Studio Action V4.1: Synthetic Fixture Custody Reconciliation

Date: 2026-08-22
Authoritative branch: `hack-hydra/studio-ollarma-daisy-20260821`
Purpose: zero-model, zero-network custody hygiene only.

## Role boundary

Byron + ChatGPT remain the primary control plane.
Antigravity is a bounded executor.
Do not redesign experiments, change datasets/scorers/models/prompts/K/context/generation parameters, deploy Vercel, or alter claims.

## Preserve valid V11 execution

Do **not** stop, restart, pause, reconfigure, or mutate a valid V11 runner.
Read-only watchdog/process inspection is allowed.

## Problem to reconcile

The V4 scorer audit directly executed frozen `evaluate_slot_v11()` with canned transport. The V4 auditor redirected `RAW_OUTPUT_BANK` but did not redirect the frozen module's `PROJECT_ROOT`, so synthetic fixture calls may have written handoff receipts into live local `custody/turns/`.

Manual pre-V4 scorer tests on magicPRObox may also have written a synthetic handoff receipt.

These are `SYNTHETIC_FIXTURE_INPUT` artifacts, not benchmark executions.

## Hosts

Audit both:

- `magicSTUDIObox.local`
- `magicPRObox.local`

## Candidate synthetic handoff names

At minimum inspect:

- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_01.json`
- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_02.json`
- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_03.json`
- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_04.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_01.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_02.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_03.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_04.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_05.json`
- `HANDOFF_V11_deepseek-r1_14b_syn_01.json`

Also enumerate all files matching:

`custody/turns/HANDOFF_V11_*syn_*.json`

Do not assume the list above is exhaustive.

## Required deterministic receipt fields

For every discovered candidate record:

- host
- original path
- filename
- byte size
- SHA-256
- embedded handoff_id
- embedded case_id dependency ID if present
- embedded git_commit
- embedded evidence_class
- embedded transformation_class
- embedded execution_status / terminal_state
- timestamp_utc
- whether referenced by the real V11 `SLOT_LEDGER.jsonl`
- whether referenced by the real V11 `CHECKPOINT.json`
- classification = `SYNTHETIC_SCORER_FIXTURE_HANDOFF`

## Fail-closed safety rule

If any candidate synthetic receipt is referenced by the real V11 ledger/checkpoint, **STOP** and report `CUSTODY_RECONCILIATION_BLOCKED_UNEXPECTED_PRIMARY_REFERENCE` without moving anything.

If a candidate is not referenced by primary run state, it may be quarantined as specified below.

## Quarantine, do not delete

Move uncommitted synthetic scorer-fixture handoffs out of live `custody/turns/` into host-local:

`eval/studio_daisy_20260821/dataset_audit_v4/synthetic_fixture_custody/<host>/`

Preserve bytes exactly.

After moving:

- recompute SHA-256 and prove it matches the original SHA;
- record original and quarantine paths;
- record `BYTE_IDENTITY_AFTER_MOVE=PASS`.

Do not commit raw synthetic handoff payloads unless they are already tracked or needed to establish custody. Prefer compact hashes/metadata receipts.

## Git contamination audit

At current origin head, independently verify whether any `HANDOFF_V11_*syn_*.json` path is tracked by Git.

Expected result from primary GitHub review is no committed V4 synthetic handoff at the tested path, but recompute locally.

Record:

- `GIT_TRACKED_SYNTHETIC_HANDOFF_COUNT`
- exact tracked paths if nonzero
- `GIT_SYNTHETIC_CUSTODY_CONTAMINATION_GATE`

If tracked count > 0, do not rewrite history. Preserve and return for primary review.

## Worktree hygiene

After reconciliation run:

- `git status --short`
- enumerate `custody/turns/HANDOFF_V11_*syn_*.json`

Required gates:

- `LIVE_CUSTODY_SYNTHETIC_HANDOFF_COUNT=0`
- `PRIMARY_LEDGER_REFERENCE_COUNT=0`
- `PRIMARY_CHECKPOINT_REFERENCE_COUNT=0`
- `BYTE_IDENTITY_AFTER_MOVE=PASS` for every moved item

Do not alter legitimate V11 handoffs.

## Output artifacts

Create compact receipts under:

`eval/studio_daisy_20260821/dataset_audit_v4_1/`

Required:

- `SYNTHETIC_CUSTODY_RECONCILIATION.json`
- `SYNTHETIC_CUSTODY_SHA256SUMS.txt`
- `HOST_WORKTREE_HYGIENE.json`

The reconciliation JSON must preserve separate Studio and Pro observations.

## Git writeback

Commit only:

- reconciliation/audit script if created
- compact receipts
- no large raw payloads

Push to:

`hack-hydra/studio-ollarma-daisy-20260821`

Sync magicPRObox from origin after push.

## Stop condition

After commit/push and host sync, STOP for Byron + ChatGPT review.

Do not start a successor experiment.

## Return receipt

Return exactly enough to review:

```text
CURRENT_BRANCH=
CURRENT_HEAD=
ORIGIN_HEAD=
MAGICPRO_HEAD=

V11_PROCESS_STATE=
V11_SLOTS_ACCOUNTED=
V11_SLOTS_EXPECTED=6930

STUDIO_SYNTHETIC_HANDOFFS_FOUND=
PRO_SYNTHETIC_HANDOFFS_FOUND=
GIT_TRACKED_SYNTHETIC_HANDOFF_COUNT=
PRIMARY_LEDGER_REFERENCE_COUNT=
PRIMARY_CHECKPOINT_REFERENCE_COUNT=
QUARANTINED_SYNTHETIC_HANDOFF_COUNT=
LIVE_CUSTODY_SYNTHETIC_HANDOFF_COUNT=
BYTE_IDENTITY_AFTER_MOVE_GATE=
GIT_SYNTHETIC_CUSTODY_CONTAMINATION_GATE=
ZERO_MODEL_CALL_GATE=
ZERO_NETWORK_CALL_GATE=

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
FINAL_REVIEW_GATE=V4_1_SYNTHETIC_CUSTODY_RECONCILIATION_COMPLETE__WAIT_FOR_PRIMARY_CONTROL_REVIEW
```
