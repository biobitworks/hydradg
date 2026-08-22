# ChatGPT Independent Review — Dataset Readiness V2 — 2026-08-21

Reviewed commit: `8783a0da7334af02308e15b770b583bf1ca3fba4`

## Review outcome

`PARTIAL_PASS__SUCCESSOR_ZERO_MODEL_AUDIT_REQUIRED`

The V2 audit materially improves V1 by binding execution to `magicSTUDIObox.local` / `Mac13,1`, recomputing Track 01 source SHA-256 values, separating the V1 oracle-context route from a leakage-free Track 01 query manifest, and preserving Track 02 as blocked. However, several gates requested by `docs/CONTROL_NEXT_STUDIO_ACTION_20260821.md` are still self-confirming rather than independently recomputed.

## Accepted V2 evidence

- Host binding is implemented fail-closed against `magicSTUDIObox.local` and `Mac13,1`.
- Track 01 question SHA-256 is recomputed from source bytes.
- Track 01 document SHA-256 is recomputed from source bytes.
- V1 Track 01 route is correctly recognized as containing retrieval-gold leakage/oracle context.
- The separate V2 Track 01 manifest does not use `expected_doc_ids` to select documents for its model-facing query payload.
- Track 02 remains `BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED`.
- Track 03 source bytes are recomputed from the frozen source file.
- All tracks are not ready because Track 02 remains blocked.

## Remaining defects

### 1. Track 01 admission identity gate is count-only

The action auditor constructs the admitted set using `df_t1_q.head(300)` and sets `TRACK01_ADMISSION_IDENTITY_GATE=PASS` when `len(admitted_q_ids) == 300`.

This proves a deterministic 300-row selection was produced; it does not independently prove equality to an expected 300-ID contract.

Required successor classification:

- `TRACK01_ADMISSION_RULE = ORDERED_FIRST_300_SOURCE_ROWS` if this is the intended contract.
- Compute an ordered ID-list SHA-256.
- Compare against an independent earlier/frozen expected ID list if such an artifact exists.
- If no independent expected identity artifact exists, report `ADMISSION_RULE_FROZEN` rather than `ADMISSION_IDENTITY_MATCH_PASS`.

### 2. Track 03 exact-set gate is tautological

The action auditor appends each secondary ID to both `t3_secondary_items` and `t3_expected_secondary_ids` inside the same conditional, then hashes both lists and compares those roots.

Therefore equality is guaranteed by construction. The gate does not independently establish that the V2 30-ID set matches the historical/frozen 30-ID set.

Required successor check:

- Read the committed historical V1 `TRACK03_SECONDARY_30_MANIFEST.jsonl` as the independent expected set.
- Extract/sort its 30 question IDs.
- Independently derive the current 30 IDs from the frozen source dataset.
- Compare exact sets and SHA-256 roots.

### 3. `compute_merkle_root` is not a Merkle construction

The action auditor sorts IDs, joins them with newline, then computes one SHA-256 over the concatenated bytes.

That is a deterministic canonical ID-set/list digest, not a Merkle root.

Required terminology:

- `CANONICAL_ID_LIST_SHA256` or `ID_SET_SHA256`

Do not label these values Merkle/MMR roots. `MERKLE_MMR_STATE` remains `NOT_COMMITTED`.

### 4. Scorer identity gates are literal PASS assignments

`TRACK01_SCORER_IDENTITY_GATE` and `TRACK03_SCORER_IDENTITY_GATE` are written as literal `PASS` values. No actual scorer implementation path/function bytes are located and hashed.

Required successor check:

- Locate the exact scorer implementation used by the frozen experiment runner or canonical scorer contract.
- Record scorer file path, Git SHA, file SHA-256, and function/contract identity.
- If no frozen implementation exists, report `BLOCKED_SCORER_IMPLEMENTATION_NOT_FROZEN`.

### 5. Scorer smoke tests are self-fulfilling

For both Track 01 and Track 03, the smoke test sets `pred = gold` and checks that the resulting score passes. This only demonstrates an identity input passes the inline simulation.

Required successor smoke test against the actual scorer implementation:

- one positive fixture that must pass;
- one negative fixture that must fail;
- optionally one boundary/normalization fixture;
- verify actual observed outputs against frozen expected outputs.

### 6. Conflicting V2 artifacts

The commit contains two V2 auditors and two summary files with somewhat different semantics:

- `scripts/audit_dataset_readiness_v2_20260821.py`
- `scripts/audit_dataset_readiness_v2_action_20260821.py`
- `DATASET_READINESS_AUDIT_V2.json`
- `DATASET_READINESS_V2_AUDIT.json`

The first auditor calls Track 01 `DATASET_READY=PASS` after creating a leakage-free query-only prompt; the action auditor classifies it `ORACLE_CONTEXT_DIRECT_BASELINE_READY`, even though the V2 query manifest no longer supplies oracle context.

Required successor: establish one canonical V3 audit receipt and classify Track 01 lanes separately:

- `V1_ORACLE_CONTEXT_DIRECT_BASELINE`
- `V2_TRACK01_QUERY_MANIFEST_NO_GOLD_DOC_SELECTION`
- `HYDRADG_RETRIEVAL_LANE_NOT_YET_EXECUTED` unless retrieval is actually wired and run.

## Corrected claim ceiling

`DATASET_SOURCE_BYTES_AND_COMPACT_MANIFESTS_MATERIALIZED__HOST_BINDING_PASS__TRACK01_ORACLE_LEAKAGE_IDENTIFIED_AND_QUERY_MANIFEST_REPAIRED__TRACK02_BLOCKED__TRACK01_ADMISSION_IDENTITY_TRACK03_INDEPENDENT_SET_AND_SCORER_CONTRACT_GATES_PENDING`

## Earliest divergence

`TRACK01_ADMISSION_IDENTITY_GATE_REPORTED_PASS_FROM_COUNT_ONLY_WITHOUT_INDEPENDENT_EXPECTED_IDENTITY_CONTRACT`

## Next safe action

Run one final zero-model-call Dataset Readiness V3 audit on `magicSTUDIObox.local` that:

1. preserves V1 and V2 artifacts unchanged;
2. binds host identity;
3. freezes Track 01 admission rule and independently checks continuity if possible;
4. compares Track 03 current secondary IDs against the historical committed V1 30-ID manifest;
5. replaces false Merkle terminology with canonical SHA-256 list/set roots;
6. locates and hashes actual scorer implementation(s);
7. runs positive + negative fixtures through the actual scorer(s);
8. emits one canonical V3 receipt;
9. executes zero model calls;
10. stops for Byron/ChatGPT review.

Do not interrupt a valid active V11 run for this audit.

## Cryptographic state

`SIGNATURE_STATE=NOT_SIGNED`

`MERKLE_MMR_STATE=NOT_COMMITTED`
