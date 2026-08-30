# ChatGPT Independent Review — Dataset Readiness V4

Date: 2026-08-22
Reviewed commit: `98fe8ce6a3480fb268cea3ef8089ca1a38b928e5`
Frozen V11 execution SHA: `0c7e6b67c6e80b8eec4a9db9c8edb8a001290831`

## Accepted V4 findings

- Frozen V11 runner bytes were materialized from Git and hashed.
- Current worktree runner bytes matched the frozen V11 runner bytes.
- The actual inline Track 01 and Track 03 scorer branches were extracted from the frozen V11 source.
- Direct synthetic fixtures executed the actual frozen `evaluate_slot_v11()` branch with canned in-memory transport and produced the expected frozen V11 terminal states.
- Track 01 remains correctly classified as `V1_ORACLE_CONTEXT_DIRECT_BASELINE`; HydraDG Track 01 retrieval is `NOT_YET_EXECUTED`.
- Track 02 remains `BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED`.
- Track 03 is ready under the frozen V11 scorer contract.

## Custody-side defect found during review

The V4 auditor imports the frozen V11 runner and redirects `RAW_OUTPUT_BANK`, but it does **not** redirect `v11_mod.PROJECT_ROOT` or the `custody/turns` destination used inside `evaluate_slot_v11()`.

Therefore each synthetic direct fixture can write a handoff receipt into the live local worktree path:

`/Users/byron/projects/active/hydradg/custody/turns/`

Expected V4 synthetic fixture handoff names include:

- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_01.json`
- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_02.json`
- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_03.json`
- `HANDOFF_V11_deepseek-r1_14b_EnterpriseRAG-Bench_syn_04.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_01.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_02.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_03.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_04.json`
- `HANDOFF_V11_deepseek-r1_14b_LongMemEval-S_syn_05.json`

The manual pre-V4 Pro-side test shown in the operator log may also have written:

- `HANDOFF_V11_deepseek-r1_14b_syn_01.json`

GitHub inspection confirms the expected Studio synthetic fixture receipt is **not committed** in canonical Git at V4 head, so this is currently a local-worktree custody hygiene risk rather than canonical Git contamination.

## Required correction

Do not delete these artifacts silently. They are deterministic/synthetic audit evidence and must never be represented as benchmark executions.

Run a zero-model, zero-network local custody reconciliation on both Studio and Pro:

1. Enumerate the exact synthetic fixture handoff files above plus any `HANDOFF_V11_*syn_*` files created during V4/manual scorer testing.
2. Record path, host, size, SHA-256, embedded `case_id`, `evidence_class`, `git_commit`, and timestamp.
3. Verify none is referenced by the real V11 `SLOT_LEDGER.jsonl` or `CHECKPOINT.json`.
4. Move any such uncommitted synthetic receipts out of `custody/turns/` into a dedicated audit quarantine under `eval/studio_daisy_20260821/dataset_audit_v4/synthetic_fixture_custody/` on the corresponding host.
5. Preserve a compact reconciliation receipt in Git; do not commit raw synthetic handoff payloads unless needed.
6. Re-run `git status --short` and prove the active worktree has no untracked synthetic handoffs remaining under `custody/turns/`.
7. Do not interrupt or mutate valid V11 execution.

## Claim ceiling

V4 scorer reconciliation is accepted for the frozen V11 scorer contract, subject to local synthetic-fixture custody cleanup. Dataset readiness across all tracks remains incomplete because Track 02 is blocked and HydraDG Track 01 retrieval has not yet executed.

`SIGNATURE_STATE=NOT_SIGNED`

`MERKLE_MMR_STATE=NOT_COMMITTED`
