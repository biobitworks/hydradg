# HydraDG GSD + gsigmad + FCO/FCG Orchestration Profile

Status: project-level orchestration profile for HydraDG agent/model work.

## Purpose

HydraDG uses three layers that must remain distinct:

1. **GSD / gettingsciencedone** — meta-prompting, context engineering, planning state, dependency waves, verification, and handoff orchestration.
2. **gsigmad** — science governance: role lanes, PROMPT/EXP lifecycle, preregistration, claim/audit gates, replay/closeout contracts, red-team and power-analysis surfaces.
3. **FCO/FCG** — canonical custody: exact-byte identity, evidence class, transformation lineage, claim ceilings, parent dependencies, graph append, signatures/commitments only when actually performed.

Runtime systems such as Ollarma/Ollama execute bounded work; HydraDB is a projection/query substrate; GitHub is a versioned synchronization and handoff surface. None of those systems may self-promote scientific truth.

## Upstream GSD structural invariants adopted by HydraDG

HydraDG agents MUST preserve these GSD design properties:

- **Fresh context per bounded agent/work unit.** Do not let an orchestrator accumulate the whole project context and then perform specialist work itself.
- **Thin orchestrators.** Orchestrators route, load state, spawn/hand off bounded work, collect receipts, and advance gates. Heavy reasoning/execution belongs to the assigned role/runtime.
- **File-based durable state.** Use the repo's existing `.planning/`, EXP/PROMPT, custody, and receipt surfaces. Do not create a second planning truth store when one already exists.
- **Plans are executable prompts.** A plan must contain enough context, inputs, constraints, verification and done conditions that the executor does not have to reinterpret intent.
- **Decision fidelity.** Locked operator/user decisions are immutable for the work unit; deferred ideas must not leak into execution; discretionary areas must be explicit.
- **Dependency graph + waves.** Every bounded task declares `needs` and `creates`; independent tasks may run in parallel only when their write surfaces do not collide.
- **Plan check before execution.** Verify required inputs, authority, capability, scientific preregistration and expected outputs before compute begins.
- **Post-execution verification.** A task is not complete because a process exited 0; verify the declared must-haves against actual artifacts/receipts.
- **Human/UAT gate where authority is required.** Release, claim promotion, canonical writeback, key use, and destructive reconciliation remain explicit operator actions.
- **Context budget discipline.** Pass paths/hashes/pointers and tell agents to read canonical files from disk/repo; do not inline large sibling artifacts into every subagent prompt.
- **Atomic bounded commits.** Commit the coherent work unit/experimental block, not every individual case and not unrelated work via `git add -A`.

## gsigmad structural invariants adopted by HydraDG

HydraDG additionally requires:

- explicit role lane and runtime identity;
- no runtime may up-scope itself or a child beyond its authority ceiling;
- PROMPT provenance for confirmatory/replication/material AI-assisted experiments;
- EXP closeout linkage to scripts/results/notebook/lab-notebook anchors where applicable;
- replay classification before Ollarma notebook replay;
- claim/output audit before promotion;
- negative/null/failed evidence retention;
- no direct runtime writeback into canonical truth without the owning governance path.

The current gsigmad role/provenance contract describes interactions using `slug + path + content_hash + signature + parents`. HydraDG adopts the provenance DAG but applies the cryptographic normalization below.

## Critical signature normalization

Some gsigmad draft receipts use a field named `signature` with a value shaped like:

`SIG-<timestamp>-<runtime>-<task>`

That value is a **deterministic receipt label / interaction identifier**, not a cryptographic signature.

When HydraDG ingests such a receipt:

- map the legacy value to `legacy_signature_label` or `receipt_label`;
- preserve its exact original bytes for historical custody;
- set `signature_state = NOT_SIGNED` unless an actual authorized private-key operation and verification receipt exist;
- never display the legacy label as proof of authenticity.

Hashing, receipt labels, Ed25519 signatures, and Merkle/MMR commitments are four different operations.

## Missing structural layer: two-phase handoff acceptance

A sender receipt alone is insufficient for multi-agent orchestration. Every material cross-agent handoff SHOULD be two-phase:

1. **OFFER** — sender freezes the work packet, role, dependencies, base Git SHA, expected host/runtime, stop conditions and output contract.
2. **ACCEPT** — receiving runtime records that it resolved the packet, is on the correct host/repo/SHA, has the required capability, accepts the role ceiling, and has not detected a stale lease.

No executor should begin a material work unit before ACCEPT passes.

This prevents a recurring failure mode: a prompt says `magicstudiobox`, but the receiving agent executes in its current local shell.

## Missing structural layer: lease + fencing

Every long-running or multi-agent work unit SHOULD carry:

- `work_unit_id`
- `lease_id`
- monotonic `fencing_token`
- `single_writer_scope`
- `lease_owner`
- `lease_state`

A stale agent with an older fencing token must not commit, write back, restart, or supersede the newer owner. Lease expiry does not imply automatic reclaim.

For Git work, prefer one worktree/branch per active writing lane. The Studio Daisy lane remains single-writer for scientific execution.

## Missing structural layer: capability snapshot

Before ACCEPT, freeze a capability snapshot containing only non-secret facts needed for the task:

- actual runtime/provider/agent identity;
- execution hostname + hardware identity hash;
- repo path, branch, Git SHA and clean/dirty state;
- required skills/scripts resolved and their hashes where material;
- Ollarma/Ollama/HydraDB service readiness when required;
- exact model name + runtime digest for model work;
- environment-variable **names/presence**, never secret values;
- tool/runtime versions materially affecting reproducibility.

If a required capability is missing, return `BLOCKED_CAPABILITY` rather than silently changing lane, host, model or provider.

## Work-unit lifecycle

Every substantive bounded work unit should follow:

`DISCOVER -> OFFER -> ACCEPT -> PLAN -> PLAN_CHECK -> EXECUTE -> VERIFY -> SCIENCE_AUDIT/CLOSEOUT -> CUSTODY_APPEND -> COMMIT/PUSH -> RECEIVER_SYNC -> HANDOFF_COMPLETE`

Scientific long runs may loop `EXECUTE -> CHECKPOINT -> VERIFY -> COMMIT/PUSH/SYNC` per preregistered bounded block.

### DISCOVER

Read project authority and current state. Resolve canonical files rather than reconstructing them from chat memory.

### OFFER

Freeze the exact work packet and its SHA-256. Record locked decisions, deferred ideas, role lane, parent receipts, inputs, expected outputs and stop conditions.

### ACCEPT

Receiver verifies host/repo/SHA, capability snapshot, role ceiling, lease/fencing token and worktree ownership.

### PLAN / PLAN_CHECK

Plan by dependency and goal-backward must-haves. A checker verifies that locked decisions are implemented, deferred work is absent, prerequisites exist, and scientific variables are preregistered.

### EXECUTE

Execute only inside accepted scope. Probabilistic outputs remain probabilistic evidence. No silent fallback.

### VERIFY

Check actual artifacts and receipts against must-haves. Recompute deterministic hashes/statistics when possible.

### SCIENCE_AUDIT / CLOSEOUT

Apply gsigmad claim, reproducibility, EXP/PROMPT and replay/closeout rules. A null or negative result may pass closeout.

### CUSTODY_APPEND

Materialize/append through canonical FCO/FCG machinery when available. Preserve project FCG root before/after and any HydraDB projection/readback receipt.

### COMMIT/PUSH/SYNC

Studio Daisy scientific blocks push from `magicSTUDIObox.local`; GitHub/origin is the Git arbiter; `magicPRObox.local` fetches and fast-forwards. Heavy raw data may remain in the verified durable bank with hashes/pointers committed.

### HANDOFF_COMPLETE

The receiver (or next lane) acknowledges the resulting Git SHA, receipt hash, FCG state, claim ceiling, signature state and next allowed action.

## Required work-unit fields

Machine-readable work units are defined by `schemas/orchestration_work_unit.schema.json` and must include at minimum:

- work unit + phase (`offer|accept|closeout`);
- parent receipt hashes;
- actor/runtime/role lane;
- role ceiling + writeback disposition;
- worktree/repo/branch/base SHA;
- expected host and actual host at acceptance/closeout;
- capability snapshot hash;
- plan/input packet hash;
- locked decisions + deferred ideas;
- lease ID + fencing token + single-writer scope;
- expected outputs + verification gates;
- stop conditions;
- evidence/claim ceiling;
- FCO/FCG state;
- cryptographic signature state;
- Merkle/MMR state.

## Runtime/model rule

Every Ollama model invocation used materially by HydraDG is a child work unit/receipt of the governing Ollarma/agent work unit and must bind:

`parent handoff -> approved model identity -> runtime digest -> input packet/prompt/request hashes -> raw response hash -> parser/scorer -> outcome -> custody append`

An Ollama model has no PI/PM/Operator authority. It cannot approve a claim, substitute a model, select a scientific variable, sign a project root, or decide writeback.

## Long-running work

Before launch freeze:

- run ID;
- target paths;
- active runtime and allowed fallback (HydraDG Studio Daisy: NONE for scientific execution);
- checkpoint/update cadence;
- PID and duplicate-run checks;
- preservation/no-cleanup rules;
- stop conditions;
- completion criteria;
- watcher authority.

During scientific inference, watcher models must not contend for the same Ollama runtime. Use deterministic telemetry only.

## Git/GitHub bridge

For the current HydraDG Studio Daisy lane:

`magicPRObox controller -> SSH/Tailscale -> magicSTUDIObox executor -> Git commit/push -> GitHub origin -> MagicPro fetch + ff-only mirror`

Required after each bounded block:

`STUDIO_HEAD == ORIGIN_HEAD == MAGICPRO_HEAD`

A GitHub push is a durable handoff artifact but is not itself scientific verification or a cryptographic project signature.

## Enforcement

Run both:

```bash
python3 scripts/check_orchestration_work_unit.py <work-unit.json>
python3 scripts/check_agent_model_handoff_receipt.py <handoff-receipt.json>
```

The orchestration checker validates the meta-workflow envelope; the handoff checker validates the evidence/custody envelope. Both must pass before promotion.

## Authority boundary

This profile adds orchestration structure only. It does not override the FCO/FCG canonical specification, claim ceilings, evidence levels, signing/key policy, scientific preregistration, or explicit current user instruction.
