# HydraDG Control — SeedGraph Hierarchical Retrieval v1a Studio Validation

## Authority and role boundary

Primary scientific/control plane: Byron + ChatGPT.

Antigravity is a bounded remote operator only.

Scientific/dataset execution host: `magicSTUDIObox.local`.

GitHub origin is the synchronization arbiter.

Do not modify Vercel or `main`.

Do not stop, restart, reconfigure, or mutate a valid V11 failure-complete run.

## Goal

Validate the newly frozen SeedGraph hierarchy mechanically before any SeedGraph model experiment.

The key architecture is:

```text
semantic / structural query seeds
-> graph/index object IDs
-> context-score / delta / variance enriched path selection
-> hierarchical expansion
-> lazy source pointer dereference
-> SHA-256 byte verification
-> bounded evidence packet
```

SHA-256 is identity/governance, not semantic similarity.

Context scores enrich path choice; they do not establish custody identity.

## Authoritative implementation files

Read:

- `docs/SEEDGRAPH_HIERARCHICAL_RETRIEVAL_CONTRACT_V1.md`
- `schemas/seedgraph_hierarchy.schema.json`
- `scripts/seedgraph_hierarchy_v1a.py`
- `scripts/seedgraph_score_adapter_v1.py`
- `scripts/discover_seedgraph_atom_scores_v1.py`
- `scripts/audit_seedgraph_hierarchy_v1a_20260822.py`

The earlier `scripts/seedgraph_hierarchy_v1.py` is a preserved development draft and is **SUPERSEDED_FOR_VALIDATION_BY_V1A**. Do not execute it as the current lane.

## Zero-call boundary

This action requires:

```text
ZERO_MODEL_CALLS=YES
ZERO_NETWORK_MODEL_CALLS=YES
ZERO_EXTERNAL_WEB_CALLS=YES
```

Do not invoke Ollama/Ollarma for SeedGraph validation.

Deterministic local Git, filesystem, Parquet/JSON processing and hashes are allowed.

## Preserve V11

Before validation, read deterministic V11 watchdog/process/lease state.

Do not interfere with V11 unless an execution-integrity failure exists.

Record only:

- process state;
- PID;
- lease state;
- accounted/expected slots;
- current model/case;
- last checkpoint.

Scientific failures are not execution-integrity failures.

## Phase A — source and code preflight

On Studio:

1. sync/fetch the current Daisy control branch without moving the frozen V11 scientific execution checkout;
2. verify `magicSTUDIObox.local` host identity;
3. `python3 -m py_compile` all SeedGraph v1a scripts;
4. verify the established real-source SHA-256 values:

```text
Track01 questions:
e25066f4eff3843dd0f3df0d1348113471e072e75007ffe390a0aa83f2a80af2

Track01 documents:
6b0747bf160af9427b12101537d53056ac592ada9831c1a98ae01fa50a8d2a9f

Track03 source JSON:
d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442
```

Fail closed on source drift.

## Phase B — discover existing atom context scores

Run:

```bash
python3 scripts/discover_seedgraph_atom_scores_v1.py \
  --repo-root /Users/byron/projects/active/hydradg \
  --output eval/studio_daisy_20260821/seedgraph_v1a_validation/ATOM_SCORE_BINDING_DISCOVERY.json
```

The discovery is allowed to find an enrichment source only when the structured artifact contains an **explicit**:

```text
canonical_key
OR
seed_atom_id
```

plus at least one numeric context metric such as:

```text
context_score
g_star
delta_g_star
cloud_drift_0_100
shannon_entropy
normalized_entropy
mutation_distance
restoration_gain
burden
```

Do not infer a join from prose.
Do not fuzzy-match hashes.
Do not use an LLM to invent the mapping.

### If a compatible explicit binding exists

Inspect the exact candidate and its provenance.

Use `scripts/seedgraph_score_adapter_v1.py` to produce a normalized local JSONL and score-adapter receipt.

The normalized score JSONL is a generated validation artifact and should remain outside Git if large; commit only compact hashes/receipts.

### If no compatible explicit binding exists

Continue the structural validation without scores, but preserve:

```text
ATOM_SCORE_STATE=UNAVAILABLE
SCORE_GUIDED_NAVIGATION_GATE=BLOCKED_SCORE_SOURCE_NOT_BOUND
```

Do not synthesize replacement scores.

## Phase C — structural hierarchy validation

Use an external generated namespace:

```text
/Volumes/magicBLACKbox/hydradg/seedgraph/v1a_validation
```

Run the validation auditor **without scores first**:

```bash
python3 scripts/audit_seedgraph_hierarchy_v1a_20260822.py
```

The audit must prove:

- exact source SHA matches;
- host binding;
- no model/network calls in the engine;
- Track01 question count = 300;
- Track03 primary count = 470;
- Track03 secondary count = 30;
- current secondary 30 set equals the historical committed secondary 30 set exactly;
- required hierarchy object types exist;
- required FCG hierarchy relations exist;
- source prose is absent from graph/index metadata tables;
- EVAL_ONLY columns are absent from model-visible tables;
- source pointers are lazy-dereferenced only after evidence-node selection;
- selected evidence SHA-256 verification passes;
- repeated identical queries produce identical selected object IDs and evidence hashes;
- generated large Parquet artifacts remain outside Git.

## Phase D — score-guided validation if and only if score binding exists

If Phase B produced a valid normalized score JSONL, run the same audit again with:

```bash
python3 scripts/audit_seedgraph_hierarchy_v1a_20260822.py \
  --atom-scores-jsonl <NORMALIZED_SCORE_JSONL> \
  --output-dir /Volumes/magicBLACKbox/hydradg/seedgraph/v1a_validation_scored \
  --receipt-dir /Users/byron/projects/active/hydradg/eval/studio_daisy_20260821/seedgraph_v1a_validation_scored
```

Require:

```text
ATOM_SCORE_STATE=AVAILABLE
SCORE_GUIDED_NAVIGATION_GATE=PASS
```

For each deterministic query sample retain:

- selected object IDs;
- selected hierarchy levels;
- selected evidence hashes;
- query coverage;
- context score state;
- graph edges traversed;
- candidate occurrences;
- hierarchy nodes scored;
- source dereference count;
- source bytes read;
- index/graph wall time;
- dereference/verification wall time.

Do not interpret timing differences as a model-speed result yet. These are deterministic host/configuration measurements only.

## Phase E — compact implementation receipt

Create:

```text
eval/studio_daisy_20260821/seedgraph_v1a_validation/
  ATOM_SCORE_BINDING_DISCOVERY.json
  SEEDGRAPH_V1A_VALIDATION_AUDIT.json
  QUERY_SAMPLE_RECEIPTS_COMPACT.json
  SEEDGRAPH_V1A_IMPLEMENTATION_RECEIPT.json
```

If scored validation exists, also retain compact scored validation receipts under:

```text
eval/studio_daisy_20260821/seedgraph_v1a_validation_scored/
```

`SEEDGRAPH_V1A_IMPLEMENTATION_RECEIPT.json` must state independently:

```text
STRUCTURAL_VALIDATION_GATE=
SCORE_GUIDED_NAVIGATION_GATE=
LAZY_SOURCE_DEREFERENCE_GATE=
SOURCE_SHA_VERIFICATION_GATE=
EVAL_ONLY_ISOLATION_GATE=
TRACK03_EXACT_470_30_GATE=
DETERMINISTIC_PATH_GATE=
MODEL_EXPERIMENT_AUTHORIZED=NO
```

This action does not authorize a model experiment even if all validation gates pass.

## Git writeback

Commit/push only:

- auditor/control changes if needed;
- compact JSON receipts;
- compact hashes/manifests.

Do not commit:

- `nodes.parquet`;
- `edges.parquet`;
- `seed_index.parquet`;
- Track03 turn projection Parquet;
- large evidence dumps;
- raw V11 transport;
- secrets.

Push to:

`hack-hydra/studio-ollarma-daisy-20260821`

Sync `magicPRObox` from origin afterward.

## Stop condition

After compact receipts are pushed, STOP for Byron/ChatGPT review.

Return:

```text
CURRENT_BRANCH=
CURRENT_HEAD=
ORIGIN_HEAD=
MAGICPRO_HEAD=

V11_PROCESS_STATE=
V11_PID=
V11_LEASE_STATE=
V11_SLOTS_ACCOUNTED=
V11_SLOTS_EXPECTED=6930
V11_CURRENT_MODEL=
V11_CURRENT_CASE=
V11_LAST_CHECKPOINT=
V11_NOT_INTERRUPTED_GATE=

SEEDGRAPH_CONTRACT_SHA256=
SEEDGRAPH_ENGINE_V1A_SHA256=
SEEDGRAPH_VALIDATOR_SHA256=

ZERO_MODEL_CALL_GATE=
ZERO_NETWORK_CALL_GATE=
HOST_BINDING_GATE=
SOURCE_SHA_VERIFICATION_GATE=

ATOM_SCORE_BINDING_DISCOVERY_STATE=
ATOM_SCORE_SOURCE_PATH=
ATOM_SCORE_SOURCE_SHA256=
ATOM_SCORE_NORMALIZED_SHA256=
ATOM_SCORE_STATE=
SCORE_GUIDED_NAVIGATION_GATE=

TRACK01_QUESTION_COUNT=
TRACK03_PRIMARY_COUNT=
TRACK03_SECONDARY_COUNT=
TRACK03_EXACT_SECONDARY_SET_GATE=

HIERARCHY_OBJECT_TYPE_GATE=
HIERARCHY_RELATION_GATE=
METADATA_ONLY_GRAPH_GATE=
EVAL_ONLY_ISOLATION_GATE=
LAZY_SOURCE_DEREFERENCE_GATE=
DETERMINISTIC_PATH_GATE=

SEEDGRAPH_STRUCTURAL_VALIDATION_GATE=
SEEDGRAPH_MODEL_EXPERIMENT_AUTHORIZED=NO

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
FINAL_REVIEW_GATE=SEEDGRAPH_V1A_ZERO_MODEL_VALIDATION_COMPLETE__WAIT_FOR_PRIMARY_CONTROL_REVIEW
```
