# HydraDG NewInML final Daisy execution plan — 2026-08-29

Base submission SHA: `cfee4ee7a6a8c418f9c71a37ca96031518d895bc`.

This branch is PLAN/PREREGISTRATION only. It must not be represented as executed evidence until receipts exist.

## Current evidence boundary

- EXP-008: CLOSED, 300/300, **UNDERPOWERED**.
- EXP-009: CLOSED, 300/300, **UNDERPOWERED**; directional secondary pattern is not promoted and ordering is not established.
- HydraLamp core stress: 100 deterministic systems-validation cells, 4 conditions × 25, with historical bounded PASS receipts. These are systems validation, not statistical power for EXP-008/009.
- Qwen3.8 27B: installed locally; exact digest must remain `22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643` if the existing lane is continued. Existing Q38 successor is NONTERMINAL and must be reconciled from the latest receipts before execution.
- Cloudflare OS: currently **NOT_EXECUTED as a HydraDG/HydraLamp experiment**. Historical HydraLamp receipt recorded Cloudflare path blocked/not run. Any new result is a successor experiment.
- SGLang Breakable CUDA Graph: requires an authorized CUDA host and a pinned SGLang revision/config. No non-CUDA run may be promoted as BCG evidence.
- Large SeedGraph V1A build: interrupted/nonterminal. Do not resume monolithically; successor is piecewise, per-source and batch-checkpointed.

## Scientific separation

A scientific failure/null/negative/underpowered outcome is terminal and retained. An execution-integrity failure blocks only the affected lineage.

Do not pool heterogeneous cells across experiments as inferential n.

## Lane 0 — GUM doctor / environment repair

Before any experiment, locate the existing `gum_ai_stack_doctor.zsh` (do not invent a path), run it read-only first, and record exact tool versions, model inventory, disk, swap, RAM, Ollama/Ollarma state, uv, Snakemake, Cloudflare/Wrangler/workerd, Daytona and Kaggle capability. Only apply repairs that do not change a frozen scientific variable.

Outputs:
- `GUM_DOCTOR_BEFORE.json`
- `GUM_DOCTOR_REPAIR_PLAN.json`
- `GUM_DOCTOR_AFTER.json`

## Lane 1 — CFOS-HL-001: HydraLamp on Cloudflare OS

Purpose: establish real Cloudflare OS integration and custody/failure preservation, not model superiority.

Pin exact `cloudflare/cloudflare-os` Git SHA and its lockfile. Run locally through the documented Wrangler/workerd path first.

Reuse the exact HydraLamp logical matrix:
- CONTROL × 25
- INVALID_PROOF × 25
- REPLAYED_PROOF × 25
- BROKEN_AUTHORIZATION_EDGE × 25

Canary: 4 conditions × 2 repetitions = 8 executions. Expand only after canary gates pass to 100 executions.

Required gates:
- same logical fixtures and expected policy outcomes as historical HydraLamp receipt
- source/fixture hashes frozen
- no model labels/answers leaked
- Cloudflare OS/Gatekeeper action receipts captured
- failure/deny outcomes retained
- no unauthorized canonical write
- no plaintext leakage beyond the explicitly authorized volatile boundary

Claim ceiling after canary only: `CLOUDFLARE_OS_INTEGRATION_CANARY`.
Claim ceiling after 100 terminal cells: `CLOUDFLARE_OS_HYDRALAMP_SYSTEMS_VALIDATION_WITHIN_FROZEN_MATRIX`.

## Lane 2 — SGLANG-HL-001: HydraLamp runtime intervention

Purpose: replay the same HydraLamp logical cells while varying runtime graph mode.

Authorized CUDA host only. Pin GPU, driver, CUDA, PyTorch, SGLang Git SHA, model revision/tokenizer and container digest.

Runtime factors:
1. `disabled/eager`
2. `tc_piecewise` prefill with explicit config
3. `breakable` prefill with explicit config

Do not rely on defaults. Current SGLang exposes canonical per-phase CUDA graph configuration and supports `full`, `breakable`, `tc_piecewise`, `disabled` as applicable.

Canary: 4 HydraLamp conditions × 2 reps × 3 runtime modes = 24 execution cells.
Expansion: 4 × 25 × 3 = 300 execution cells.

Primary systems endpoints:
- policy outcome parity
- custody/hash-chain parity
- tamper detection parity
- failures/timeouts/abstentions
- TTFT, output throughput, wall time, peak VRAM

Scientific unit for policy correctness remains the logical fixture/case. Runtime repetitions are factors, not independent benchmark cases.

## Lane 3 — Q38-CLOSEOUT-001

First reconcile current Q38 receipts. Preserve every completed cell. Never selectively rerun malformed/timeout outcomes merely to improve the matrix.

Existing qwen3.8 identity must be reverified before continuation.

Local successor target remains whatever the existing preregistration actually froze; do not silently redefine it. If the currently admitted local target is 150 and 27 cells are terminal, continue only the missing cells after host resource gates pass.

Q38 remains separate from Cloudflare OS and SGLang interventions unless a new experiment is preregistered.

## Lane 4 — Q38-XENV-001: Daytona/Kaggle successor

This is a new cross-environment experiment, not continuation of the local GGUF/MPS lane.

Use the same frozen logical cells across remote environments. Prefer the same exact Hugging Face model revision, tokenizer and generation/scoring contract on Daytona and Kaggle CUDA.

Do not call local GGUF/MPS and remote HF/CUDA runtime-equivalent. Compare them descriptively unless exact runtime/model-artifact equivalence is demonstrated.

Canary: deterministically select 8 logical cells from the frozen Q38 case universe by SHA256 rank under domain separator `HYDRADG_Q38_XENV_CANARY_V1`; execute each treatment cell on each available remote provider.

Expansion after provider/model-load/canary PASS: reuse the full preregistered Q38 logical cell set on both remote providers where capacity permits.

Blocked provider states are terminal infrastructure evidence; do not synthesize substitutes.

## Lane 5 — deterministic cross-environment parity

Run a small public-safe deterministic FCO/FCG transform on Studio, Daytona and Kaggle using the same source bytes, Python/uv lock, script SHA and schema.

Expected: canonical scientific payload/root equality. Hardware telemetry is excluded from the canonical root and may differ.

This is the strongest environment-agnostic custody test.

## Lane 6 — SeedGraph piecewise successor

Do not restart the interrupted 100+ GB monolith.

Each explicit source/document/media/file is its own work unit:

`source bytes -> triage -> deterministic atomization -> FCO objects -> FCG edges -> segment verification -> segment root -> checkpoint`

Per-source outputs:
- `SOURCE_MANIFEST.json`
- `ATOMS.jsonl`
- `EDGES.jsonl`
- `INGEST_RECEIPT.json`
- `SEGMENT_ROOT.json`

Batch after every 25 successfully verified sources (or smaller on memory pressure):
- `BATCH_MANIFEST.json`
- `BATCH_ROOT.json`
- `BATCH_FCG_DELTA.jsonl`
- `BATCH_CFMO_UPDATE.json`
- `BATCH_MMR_APPEND_RECEIPT.json` only if an actual canonical MMR append and verification occur

Only verified segments enter writeback. Writeback occurs in batches and must be read back before the next batch is promoted.

Interrupted sources remain `PARTIAL`, `CORRUPT`, `NOT_READBACK_SAFE`, or `BLOCKED`; never silently disappear.

## Lane 7 — atom identity + context/governance scoring

Do not invent a scalar Anticube score if the canonical implementation is categorical.

For every currently catalogued atom, create an `ATOM_GOVERNANCE_VECTOR` containing:
- content identity SHA256
- occurrence identity
- source/provenance completeness
- context fingerprint
- actor type (human/model/tool/service)
- environment/runtime
- evidence class
- SELF/NON_SELF
- SAFE/NON_SAFE
- HydraLamp gate state where applicable
- HydraDG claim state/claim ceiling
- Context Iceberg metrics only where the governed metric contract exists
- `delta_g_star` only where actually computed under the frozen definition
- contradiction/supersession state
- security classification
- custody/hash verification state

Exact content equality groups are deterministic. Semantic/entity equivalence is separate and must never be inferred from hash equality alone.

## Lane 8 — CFMO/MMR progression

CFMO is updated from verified batch/experiment state only.

MMR state may be `COMMITTED` only when actual ordered leaves, algorithm, root and verification receipt exist. SHA256 manifests alone are not MMR commitments.

Every experiment and SeedGraph source unit appends independently so interrupted work does not invalidate previous verified leaves.

## Lane 9 — lab notebook / protocol evidence

Ingest lab notebook and protocol templates as METHOD/REQUIREMENT evidence, and actual notebook instances as experiment evidence.

Minimum templates:
- preregistration
- power plan
- run manifest
- negative/null result
- terminal cell receipt
- claim ledger
- FCO/FCG append
- CFMO update
- MMR append
- closeout

Analyze protocol drift by explicit `SUPERSEDES`/`INSTANTIATES` edges.

## Lane 10 — statistics and promotion

EXP-008 and EXP-009 remain UNDERPOWERED unless a legitimate successor experiment independently changes that evidence state. Never relabel them negative merely because the observed effect is not positive.

No powered positive primary treatment-effect result is currently established. Positive evidence currently consists primarily of deterministic/engineering PASS results (HydraLamp custody/tamper/replay, HydraDB parity, Vithia bounded reproducibility fixture), which do not substitute for powered causal model-effect evidence.

For new inferential claims preregister MESI, alpha, power target, case denominator, statistical test and multiplicity family before expansion.

## Stop/expand policy

Every lane uses `CANARY -> VERIFY -> EXPAND`.

Stop affected lane on:
- source hash mismatch
- wrong model/runtime
- label leakage
- unauthorized host
- corrupted receipt
- FCO/FCG validation failure
- MMR verification failure
- provider/runtime identity mismatch outside preregistered allowance

Continue and retain:
- wrong model answer
- null
- negative effect
- malformed model output
- timeout
- abstention
- quota/provider failure, recorded as infrastructure outcome

## Routing

Deterministic work: `uv`, Python, Snakemake, SeedGraph structural extraction, hashing, scoring, statistics, FCO/FCG verification.

Ollarma-approved local models: only unresolved semantic/entity/classification items after deterministic triage. Their outputs remain `PROBABILISTIC_MODEL_OUTPUT` until verified.

Sibling repos are read/admit sources only under exact SHA and license/custody checks; no cross-repo result is promoted merely because it exists.

## Final required report

For every lane return `PASS|PARTIAL|BLOCKED|NOT_EXECUTED`, exact branch/SHA, input roots, terminal cell counts, failures, first divergence, claim ceiling, FCO/FCG state, CFMO state, signature state, MMR state, and next safe action.
