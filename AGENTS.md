# HydraDG Agent and Model Custody Contract

This repository uses the FCO/FCG custody framework for every substantive human, AI-agent, model, tool, and cross-host handoff.

## Authority

Read and obey, in order:

1. `FCO_FCG_CANONICAL_SPEC.md` when present in the canonical project source set.
2. `CLAIM_CEILINGS.md`.
3. `EVIDENCE_LEVELS.md`.
4. `FCO_SCHEMA.json` / `FCG_SCHEMA.json`.
5. `SIGNING_AND_KEYS.md` or the canonical signing instructions.
6. `ANTIGRAVITY_HYDRADG_CUSTODY_REPAIR_IN_TURN_PROTOCOL_V1.md`.
7. `docs/AGENT_MODEL_HANDOFF_CUSTODY_CONTRACT.md`.
8. `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md`.
9. Current versioned reference implementations.

If a named authority file is not present in this checkout, do not invent its contents. Resolve the canonical source or record the dependency as unresolved.

## Meta-orchestration: GSD + gsigmad

HydraDG uses Get Shit Done / `gettingsciencedone` for meta-prompting, context engineering, dependency-aware planning and verification, and `gsigmad` for science-governance workflows. Read `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md` before planning or executing a substantive multi-agent/long-running work unit.

Required structure:

`fresh context -> thin orchestrator -> OFFER -> ACCEPT -> PLAN -> PLAN_CHECK -> EXECUTE -> VERIFY -> SCIENCE_CLOSEOUT -> FCO/FCG custody -> commit/push/sync -> acknowledged handoff`.

Every material work unit must preserve locked user/operator decisions, explicit deferred ideas, dependency needs/creates, role/authority ceiling, expected outputs, verification gates, stop conditions, and single-writer ownership. Use a lease/fencing token for concurrent or long-running lanes so a stale agent cannot write after ownership has moved.

Before execution, the receiving runtime must record a capability snapshot and confirm the expected host/repo/base SHA. If that check fails, stop with `BLOCKED_CAPABILITY` or a host/sync failure; never fall back silently to the current local shell, another model, or another provider.

Validate the orchestration envelope with:

```bash
python3 scripts/check_orchestration_work_unit.py <work-unit.json>
```

A gsigmad legacy `signature: SIG-...` field is treated as a deterministic receipt/interaction label only. It does **not** establish a cryptographic signature. Preserve it as `legacy_signature_label`; cryptographic state remains `NOT_SIGNED` unless an actual authorized private-key signing and verification receipt exists.

## Mandatory handoff rule

Every substantive actor must emit or be represented by a custody handoff receipt before its output is promoted to the next stage. This includes:

- HUMAN/operator turns;
- ChatGPT/Codex;
- Antigravity/Gemini;
- Claude or other frontier agents;
- Watchtower;
- Ollarma;
- every Ollama model invocation used as evidence;
- deterministic scripts/tools;
- HydraDB projection/readback operations;
- Git/GitHub synchronization checkpoints.

The canonical machine-readable shape is defined in `schemas/agent_model_handoff_receipt.schema.json`.

Each handoff must bind, where applicable:

- actor class and exact actor/model identity;
- execution host and hardware identity;
- repo, branch, and Git commit;
- parent handoff/turn hash;
- exact input/dependency hashes;
- prompt/request hash for model calls;
- raw output/artifact hash;
- evidence class and transformation class;
- FCO identity/materialization receipt;
- FCG root before/after or explicit `NOT_APPENDED` state;
- HydraDB projection/readback receipt when applicable;
- claim ceiling;
- signature state;
- Merkle/MMR state.

No actor may silently omit negative, null, failed, timeout, abstention, malformed, or contradictory outputs.

## Ollarma / Ollama

Ollarma is the governed local bridge/runtime-receipt layer. Ollama models are probabilistic execution actors, not authorities.

For every scientific Ollama invocation preserve at minimum:

`HydraDG preregistration -> Ollarma-approved model identity -> Ollama runtime model/digest -> prompt/request SHA-256 -> raw response SHA-256 -> deterministic parser/scorer -> case result -> FCG append`.

Do not use an auto-degrading helper for a frozen scientific model call. Missing/unresolved models fail closed; they are not silently substituted.

## Hashing, signatures, and commitments are different

SHA-256 hashing is mandatory where exact bytes are available.

A hash is **not** a signature.

A handoff may state `SIGNED` only when an actual authorized private-key operation occurred and the signature verifies against the declared public key. Agents and models must never fabricate, print, commit, or substitute private keys.

If the authorized private key is unavailable or the signing policy does not authorize signing that handoff, record `NOT_SIGNED` or `PENDING_EXTERNAL_PRIVATE_KEY_OPERATION` as appropriate.

Likewise, `MERKLE/MMR_COMMITTED` may only be stated when the actual commitment operation and receipt exist.

## Cross-host / GitHub handoff

For the Studio Daisy lane:

- `magicSTUDIObox.local` is the scientific execution host.
- `magicPRObox.local` is controller/mirror only.
- GitHub/origin is the Git synchronization arbiter.

After each bounded scientific block, the Studio commits and pushes compact receipts/manifests/FCG deltas. The Pro checkout then fetches and fast-forwards. Do not begin the next block until Studio HEAD = origin HEAD = Pro HEAD and required worktree gates pass.

Heavy raw model outputs may remain in the verified durable bank with hashes/pointers in Git; Git synchronization does not require duplicating all raw bytes onto the controller machine.

## Enforcement

Run:

```bash
python3 scripts/check_orchestration_work_unit.py <work-unit.json>
python3 scripts/check_agent_model_handoff_receipt.py <receipt.json> [<receipt2.json> ...]
```

A missing required orchestration or custody field is a hard gate failure for promotion, writeback, release, or claim elevation.

## Current repair note

Earlier project conversation turns did not consistently emit the full in-turn receipt sequence. Do not retroactively pretend they did. Recoverable prior material must be marked `RETROACTIVE_CUSTODY_RECONSTRUCTION_FROM_AVAILABLE_RECORD` or `PENDING_ORIGINAL_TURN_CAPTURE` according to the existing repair protocol. From this contract onward, omission is a custody failure rather than an implicit pass.

## Cursor Cloud specific instructions

Scope note: this section is about running the development environment, not the custody contract above. The custody/handoff rules still govern any substantive scientific work unit.

### Primary service: `apps/hydradg-web` (Next.js 16 + React 19 site)

- This is the only runnable application in the repo. The Python scripts under `scripts/` are one-shot custody/projection/verification tools, not long-running services.
- The startup dependency install (`npm ci` in `apps/hydradg-web`) is handled by the Cloud update script; you do not need to reinstall on a fresh pod.
- Standard commands are defined in `apps/hydradg-web/package.json` and mirrored by root `package.json` scripts (`npm run dev`, `build`, `start`, `typecheck`, `install:all`). Run web commands from `apps/hydradg-web/` (or use the root `npm --prefix apps/hydradg-web` / root scripts). Dev server listens on port 3000 by default.
- There is **no lint script**; quality gating is `npm run typecheck` (`tsc --noEmit`). Don't invent an eslint step.
- The app runs fully without any backend or secrets. When HydraDB / provider env vars are unset, `/api/status` reports `graph.configured=false` / `reachable=false` and all pages render from deterministic presentation fixtures (e.g. `lib/demoFixture.ts`, `/api/iceberg`, `/api/query`). This is expected, not a failure. HydraDB and the API keys in `apps/hydradg-web/.env.example` are optional and only needed for live-backend reconstruction.
- Interactive core-functionality surface for a quick smoke test: the homepage (`/`) "4D FCG · context iceberg" panel — its time slider drives the reference → mutation → restoration (t0/t1/t2) state transitions and updates ΔG*/Cloud Drift metrics. The full graph view is at `/graph`. The `JudgeLab.tsx` component in `app/judge/` is not wired into any route; `/judge` renders a static walkthrough instead.
- Gotcha: `next dev`/`next build` (Next 16) regenerate `apps/hydradg-web/next-env.d.ts` (flips `.next/types` ↔ `.next/dev/types` import paths) and auto-generate `apps/hydradg-web/AGENTS.md` + `apps/hydradg-web/CLAUDE.md`. These are framework-generated dev artifacts — leave them uncommitted; do not treat the `next-env.d.ts` diff as a real change.
- `.gitignore` already excludes `.next/`, `node_modules/`, and `.env*` (except `.env.example`). Put any local HydraDB token/keys in `apps/hydradg-web/.env.local`, never in Git.
