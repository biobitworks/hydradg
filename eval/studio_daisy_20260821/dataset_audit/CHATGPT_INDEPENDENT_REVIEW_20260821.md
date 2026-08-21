# HydraDG Dataset Readiness Audit — Independent Review

Review date: 2026-08-21

Reviewed branch predecessor: `6678ba6460c2c9e58d02bc653ef3ba653a248601`

Evidence class: `DETERMINISTIC_CODE_AND_RECEIPT_REVIEW`

This review preserves the original dataset readiness receipt and does not rewrite it. It identifies gates that require a successor deterministic audit before Track 01 or Track 03 should be called fully validated for all planned evaluation lanes.

## Established from committed receipt

- Track 01 source files are present; question SHA-256 is `e25066f4eff3843dd0f3df0d1348113471e072e75007ffe390a0aa83f2a80af2`; documents SHA-256 is `6b0747bf160af9427b12101537d53056ac592ada9831c1a98ae01fa50a8d2a9f`; 500 raw questions and 300 admitted rows were recorded.
- Track 02 remains correctly blocked with 0 admitted real cases.
- Track 03 source SHA-256 is `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`; 500 raw cases, 470 primary rows, and 30 secondary rows were recorded.
- The audit script contains no Ollama/model invocation path.

## Earliest audit defects

### Track 01 — evaluation-side document selection enters model-visible prompt

The audit stores `expected_doc_ids` inside `eval_reference`, but it also uses those same IDs to select `doc_ctx` that is inserted into `model_prompt`.

Therefore `EVAL_ONLY_ISOLATION_GATE=PASS` is too broad for a retrieval evaluation. This route is an `ORACLE_CONTEXT_DIRECT_BASELINE` unless a successor manifest constructs model-visible context without gold/expected document IDs.

Required successor gates:

- `ANSWER_LABEL_ISOLATION_GATE`
- `RETRIEVAL_GOLD_LEAKAGE_GATE`
- `ORACLE_CONTEXT_BASELINE_CLASSIFICATION`

### Track 01 — admission rule is deterministic but not independently justified

The admitted set is produced with `df.head(300)`. That is deterministic, but the audit does not compare the resulting 300 IDs against a separately frozen preregistered ID set or explain why the first 300 rows are the intended primary stratum.

Required successor gate:

- `TRACK01_ADMISSION_IDENTITY_GATE`

### Track 01 — document SHA recorded but not compared to a prior expected value

`SOURCE_SHA_MATCH` compares only the question parquet against the previously expected question SHA. The document SHA is recorded but not independently matched against a pre-existing frozen expected document hash.

Required successor gate:

- `TRACK01_DOCUMENT_SOURCE_SHA_GATE`

### Track 03 — "exact 30 match" is only a count check

`filter_exact_30_match` is implemented as `len(t3_secondary_lines) == 30`. It does not compare two independently defined 30-ID sets.

Required successor output:

- exact primary 470 ID root
- exact secondary 30 ID root
- independently derived set comparison and intersection/difference counts

Required successor gate:

- `TRACK03_EXACT_SECONDARY_ID_SET_GATE`

### Scorer readiness is asserted, not audited

For Track 01 and Track 03, `SCORER_READY` is assigned the literal string `PASS`. The script does not locate, hash, execute, and verify a scorer contract.

Required successor gate:

- `SCORER_CONTRACT_IDENTITY_AND_SMOKE_GATE`

### Execution-host provenance is not bound into the receipt

The script imports `socket` but does not record or enforce hostname. The committed receipt therefore does not independently prove which host generated the final bytes. Because this is a zero-model deterministic audit, that does not invalidate the source hashes, but the execution-host claim must remain bounded unless a successor receipt records the host and recomputation identity.

Required successor gate:

- `AUDIT_EXECUTION_HOST_BINDING_GATE`

## Corrected readiness interpretation

- Track 01: `SOURCE_PRESENT_AND_HASHED__MANIFEST_GENERATED__RETRIEVAL_LEAKAGE_AND_SCORER_GATES_PENDING`
- Track 02: `BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED`
- Track 03: `SOURCE_PRESENT_AND_HASHED__470_30_SPLIT_GENERATED__EXACT_ID_SET_AND_SCORER_GATES_PENDING`
- All tracks ready: `NO`

## Next safe action

Run a zero-model-call `dataset_readiness_v2` successor on `magicSTUDIObox.local` that recomputes the gates above. Do not alter or stop a valid V11 scientific run to perform this audit. Do not use `expected_doc_ids` to select evidence in HydraDG retrieval lanes; preserve that route only as an explicitly named oracle/direct-context baseline.

## Claim ceiling

`DATASET_SOURCES_AND_MANIFESTS_MATERIALIZED__TRACK02_BLOCKED__TRACK01_RETRIEVAL_LEAKAGE_AND_TRACK01_TRACK03_SCORER_EXACTNESS_GATES_PENDING`

`SIGNATURE_STATE=NOT_SIGNED`

`MERKLE_MMR_STATE=NOT_COMMITTED`
