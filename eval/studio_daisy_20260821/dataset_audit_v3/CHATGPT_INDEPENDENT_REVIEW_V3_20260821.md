# ChatGPT Independent Review — Dataset Readiness V3 — 2026-08-21

Reviewed commit: `1d1af3388c522d88199bd26b91e934a2971ba8d9`

## Verdict

V3 is a **partial pass**.

Accepted as deterministic evidence:

- `AUDIT_EXECUTION_HOST_BINDING_GATE=PASS` for `magicSTUDIObox.local / Mac13,1`.
- Track 01 question and document corpus SHA gates pass.
- Track 01 admission rule is explicitly classified as `ORDERED_FIRST_300_SOURCE_ROWS` and continuity with the committed V2 300-ID manifest is established.
- Track 01 V1 is correctly classified as `V1_ORACLE_CONTEXT_DIRECT_BASELINE`.
- Track 01 V2 is correctly classified as `TRACK01_QUERY_MANIFEST_NO_GOLD_DOC_SELECTION`.
- HydraDG Track 01 retrieval remains `NOT_YET_EXECUTED`.
- Track 02 remains `BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED`.
- Track 03 current secondary set exactly matches the previously committed historical V1 secondary manifest: no missing or extra IDs; 470 primary + 30 secondary.
- ID hashes are correctly named canonical ID-list SHA-256 values rather than Merkle roots.
- `MERKLE_MMR_STATE` remains `NOT_COMMITTED`.

## Remaining scorer-identity defect

V3 reports:

- `TRACK01_SCORER_IDENTITY_GATE=PASS` with function identifier `score_track01_canonical` at frozen V11 commit `0c7e6b67...`.
- `TRACK03_SCORER_IDENTITY_GATE=PASS` with function identifier `score_track03_canonical` at the same commit.

This is not supported by the exact frozen V11 source.

At `0c7e6b67c6e80b8eec4a9db9c8edb8a001290831`, `scripts/run_studio_daisy_realdata_v11_20260821.py` does not define those functions. Correctness is computed inline inside `evaluate_slot_v11`:

Track 01 actual V11 rule:

```python
ref_ans = case_obj["eval_reference"].get("gold_answer", "").lower()
is_correct = any(
    word.lower() in raw_text.lower()
    for word in ref_ans.split()
    if len(word) > 4
) if ref_ans else False
```

Track 03 actual V11 rule:

```python
ref_ans = case_obj["eval_reference"].get("gold_answer", "").lower()
is_correct = (ref_ans in raw_text.lower()) if ref_ans else False
```

The V3 auditor instead defines new local functions with different rules:

- Track 01: normalized exact answer OR >=0.8 answer-fact substring coverage.
- Track 03: whitespace-normalized exact OR normalized substring.

Therefore the V3 fixture tests validate **V3 reimplemented scorer functions**, not the actual frozen V11 scoring branch.

## Correct classification

```text
TRACK01_SCORER_IDENTITY_GATE=FAIL_MISATTRIBUTED_NONEXISTENT_FUNCTION
TRACK03_SCORER_IDENTITY_GATE=FAIL_MISATTRIBUTED_NONEXISTENT_FUNCTION
V3_SCORER_FIXTURE_RESULT=RECOMPUTED_RESULT_FOR_V3_REIMPLEMENTATION_ONLY
```

This does not invalidate V11 execution. It means the dataset-readiness scorer audit has not yet faithfully tested the scorer actually used by V11.

## Next safe action

Run a zero-model-call V4 scorer reconciliation without interrupting V11.

V4 must:

1. Retrieve the exact frozen V11 file bytes from Git commit `0c7e6b67c6e80b8eec4a9db9c8edb8a001290831` using `git show` or an equivalent deterministic Git operation.
2. Record the exact frozen file SHA-256 separately from the current worktree file SHA-256.
3. Locate/hash the exact inline Track 01 and Track 03 scoring source regions in `evaluate_slot_v11`.
4. Do not claim nonexistent scorer function identifiers.
5. Exercise the exact frozen `evaluate_slot_v11` scoring branch using deterministic canned transport responses and a monkeypatched/no-network `urllib.request.urlopen`, or otherwise provide an equally strong direct execution of the frozen scoring branch with zero model/network calls.
6. Include positive, negative, and normalization/substring boundary fixtures for both tracks.
7. Preserve V3 unchanged as historical evidence.

Track 02 remains blocked and is the main dataset gap after scorer reconciliation.

## Claim ceiling

`TRACK01_AND_TRACK03_DATASET_SOURCE_AND_CASE_PARTITIONS_ESTABLISHED__V11_SCORER_IDENTITY_NOT_YET_RECONCILED__TRACK02_BLOCKED`

No signature or Merkle/MMR commitment is established by this review.
