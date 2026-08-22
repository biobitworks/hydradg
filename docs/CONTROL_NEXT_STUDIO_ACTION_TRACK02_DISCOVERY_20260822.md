# HydraDG Control — Next Studio Action: Track 02 Real-Dependency Discovery

## Authority

Primary control: Byron + ChatGPT.

Antigravity is a bounded remote operator only.

Execution host for scientific/dataset work: `magicSTUDIObox.local`.

Do not modify Vercel, `main`, model roster, V11 configuration, Track 01/03 experiment contracts, or current scientific claims.

## Goal

Determine whether Track 02 (`HydraBlast-Real-Deps`) can be grounded in real repository dependency history without synthetic benchmark cases.

This is a **DISCOVERY / CONTRACT-FEASIBILITY audit only**.

No Track 02 model calls.
No primary generation.
No Track 02 admission yet.
Do not interrupt valid V11 execution.

## A. Preserve V11

Read deterministic V11 watchdog/process/lease state only.
Do not stop/restart/reconfigure V11 unless an execution-integrity failure is present.
Scientific failures remain valid terminal outcomes.

## B. Classify unrelated Pro worktree artifacts

On `magicPRObox.local`, inspect but do not delete:

- `custody/turns/GIT_HARD_RESET_CUSTODY_LOG.json`
- `eval/studio_daisy_20260821/V6_CANARY_ARTIFACT_CLASSIFICATION.json`

For each emit:

- path
- SHA-256
- byte size
- mtime
- whether Git-tracked at current HEAD
- `git log --all -- <path>` result
- apparent schema/type
- whether referenced by current V11 ledger/checkpoint
- classification: canonical evidence / historical local evidence / generated local artifact / unknown

Do not commit the raw artifact unless existing project governance independently requires it. Emit compact classification receipt only.

## C. Track 02 real-source discovery

Use current Git/repository bytes as source evidence. At minimum inspect:

- `package.json`
- `apps/hydradg-web/package.json`
- `apps/hydradg-web/package-lock.json`
- Git history affecting those files

The current lockfile is lockfile v3 and contains concrete package versions, resolved artifacts, integrity hashes, licenses, and dependency/optional-dependency edges.

Compute and record exact current source SHA-256 values.

## D. Historical real-change search

Using local Git only, inspect history for actual dependency/version changes affecting `apps/hydradg-web/package.json` and `apps/hydradg-web/package-lock.json`.

For each candidate historical change record:

- `base_git_sha`
- `head_git_sha`
- commit timestamp
- manifest/lockfile SHA before
- manifest/lockfile SHA after
- changed direct dependency names and versions
- whether lockfile dependency graph changed
- source files proving the change

Do not invent perturbations. A candidate case must correspond to a real committed repository change.

## E. Deterministic graph transform feasibility

For each candidate real change, build or specify a deterministic dependency graph from lockfile bytes:

- nodes = exact package identities/version or root package
- directed edges = dependency / optionalDependency / peerDependency only when represented by source bytes
- preserve edge type
- preserve package version
- preserve source path/hash

Define a proposed blast-radius transform without using a model:

`changed_dependency -> reverse-reachable dependents under frozen edge policy`

or another deterministic policy if source structure requires it.

Do not mark this as benchmark ground truth until the transformation contract is frozen and independently reproducible.

## F. Candidate-case acceptance gates

A Track 02 candidate may be reported as `REAL_CASE_CANDIDATE` only if all are true:

- BASE_SHA_PRESENT
- HEAD_SHA_PRESENT
- SOURCE_BYTES_PRESENT
- SOURCE_SHA256_RECOMPUTED
- CHANGE_IS_REAL_COMMITTED_HISTORY
- DEPENDENCY_GRAPH_DETERMINISTIC
- PERTURBATION_IDENTITY_DETERMINISTIC
- EXPECTED_BLAST_RADIUS_DERIVABLE_WITHOUT_MODEL
- NO_SYNTHETIC_INPUT
- LICENSE/RIGHTS_RECORDED

Otherwise report the failed gate explicitly.

## G. Do not admit Track 02 yet

Track 02 remains:

`BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED`

unless this discovery produces enough real candidates to justify a successor contract-design action.

Even if candidates exist, do not create a primary Track 02 case manifest or start model runs in this action.

## H. Required outputs

Create compact artifacts under:

`eval/studio_daisy_20260821/track02_discovery/`

Required:

- `TRACK02_REAL_SOURCE_DISCOVERY.json`
- `TRACK02_HISTORICAL_DEPENDENCY_CHANGES.json`
- `TRACK02_CANDIDATE_CASES.jsonl` (metadata only; no huge payloads)
- `TRACK02_DISCOVERY_SHA256SUMS.txt`
- `PRO_UNTRACKED_ARTIFACT_CLASSIFICATION.json`

Include:

- `ZERO_MODEL_CALL_GATE`
- `ZERO_PRIMARY_GENERATION_GATE`
- `V11_NOT_INTERRUPTED_GATE`
- `REAL_CASE_CANDIDATE_COUNT`
- `TRACK02_CONTRACT_FEASIBILITY` = `YES`, `NO`, or `INSUFFICIENT_EVIDENCE`
- `TRACK02_DATASET_STATE` remains blocked unless a later primary-control review explicitly promotes it.

## I. Git writeback

Commit/push only auditor/discovery code and compact receipts to:

`hack-hydra/studio-ollarma-daisy-20260821`

Do not commit `node_modules`, temporary worktrees, large graph dumps, or secrets.

Sync `magicPRObox` from origin afterward.

## J. Stop condition

After push, STOP for Byron/ChatGPT review.

Return:

```text
CURRENT_BRANCH=
CURRENT_HEAD=
ORIGIN_HEAD=
MAGICPRO_HEAD=

V11_PROCESS_STATE=
V11_SLOTS_ACCOUNTED=
V11_SLOTS_EXPECTED=6930
V11_NOT_INTERRUPTED_GATE=

ZERO_MODEL_CALL_GATE=
ZERO_PRIMARY_GENERATION_GATE=

ROOT_PACKAGE_JSON_SHA256=
WEB_PACKAGE_JSON_SHA256=
WEB_PACKAGE_LOCK_SHA256=
LOCKFILE_VERSION=

REAL_HISTORICAL_DEPENDENCY_CHANGE_COUNT=
REAL_CASE_CANDIDATE_COUNT=
TRACK02_CONTRACT_FEASIBILITY=
TRACK02_DATASET_STATE=BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED

PRO_UNTRACKED_ARTIFACT_CLASSIFICATION_GATE=

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
FINAL_REVIEW_GATE=TRACK02_DISCOVERY_COMPLETE__WAIT_FOR_PRIMARY_CONTROL_REVIEW
```
