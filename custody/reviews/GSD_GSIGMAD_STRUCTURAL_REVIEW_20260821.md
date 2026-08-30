# GSD / gsigmad Structural Review — 2026-08-21

Evidence class: externally retrieved GitHub evidence + directly supplied human instruction + deterministic repository edits.

## Human instruction

SHA-256 of the exact current human message bytes as supplied to ChatGPT:

`0c39f36e2c89c139a5acd962bd02c4b2c5f95454b698cbec154f1d47c2cd08ef`

The instruction was to review `gettingsciencedone`, `gsigmad-*`, and the upstream Get Shit Done design; identify missing structural elements; push the HydraDG integration; then provide a short Antigravity pull/review prompt.

## Sources reviewed

- `biobitworks/gsigmad` `AGENTS.md`
- `biobitworks/gsigmad` `docs/ROLE_AND_PROVENANCE_CONTRACT.md`
- `biobitworks/gsigmad` `docs/CONTROL_PLANE_BRIDGE_CONTRACT.md`
- `biobitworks/gsigmad` `docs/EXP_CLOSEOUT_CONTRACT.md`
- `biobitworks/gsigmad` `README.md`
- recent connected-GitHub commit history for private `biobitworks/gettingsciencedone`, including claim-audit, power-analysis, STATE/ROADMAP/REQUIREMENTS and flat-file governance work
- upstream `gsd-build/get-shit-done` architecture/planner documentation retrieved from public GitHub

## Existing strengths confirmed

Already present across GSD/gsigmad/HydraDG:

- meta-prompting and context engineering;
- file-backed planning state;
- phase/plan/execution/verification lifecycle;
- preregistration and EXP/PROMPT science lifecycle;
- claim audit and power-analysis surfaces;
- explicit PI/PM/SWE/Review/Operator authority lanes;
- non-upscope role inheritance;
- per-lane worktree/single-writer guidance;
- interaction provenance with parent DAGs and content hashes;
- experiment closeout and replay classification;
- no-writeback defaults and bounded runtime ownership;
- scratchpad custody;
- Ollarma bounded-runtime receipts;
- HydraDG FCO/FCG exact-byte custody and claim ceilings.

## Structural gaps added to HydraDG

1. **Two-phase OFFER/ACCEPT handoff** so the receiving runtime proves it is on the intended host/repo/SHA before execution.
2. **Lease + monotonic fencing token** so stale agents cannot commit/writeback/restart after ownership moves.
3. **Capability snapshot** freezing runtime/provider/model identity, host, repo SHA, required skills/scripts/services and non-secret environment presence.
4. **GSD decision fidelity** for locked decisions, deferred ideas and explicit discretion.
5. **Thin orchestrator + fresh-context rule** so orchestration state does not become specialist execution context rot.
6. **Dependency needs/creates + execution waves** for safe concurrency.
7. **Plan-check and post-execution verification gates** in addition to process exit status.
8. **Human/UAT/operator gate** for release, claim promotion, canonical writeback, destructive reconciliation and key use.
9. **Explicit cryptographic normalization**: gsigmad draft `signature: SIG-...` values are receipt labels, not cryptographic signatures. HydraDG records them as `legacy_signature_label` unless a real private-key signing/verification receipt exists.
10. **Unified orchestration + custody dual linting** so meta-workflow completeness and FCO/FCG evidence completeness are separately checked.

## Repository changes

Created:

- `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md`
- `schemas/orchestration_work_unit.schema.json`
- `scripts/check_orchestration_work_unit.py`

Updated:

- `AGENTS.md`

## Claim ceiling

`GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE_IMPLEMENTED_IN_GITHUB_NOT_YET_EXECUTED_ON_BOTH_HOSTS`

## Cryptographic state

- Human message: SHA-256 computed.
- GitHub commits: created through the connected GitHub API.
- FCO/FCG canonical materialization for this review: pending project-host execution.
- Cryptographic project signature: `NOT_SIGNED`.
- Merkle/MMR project commitment: `NOT_PROJECT_COMMITTED`.

A Git commit or SHA-256 digest is not treated as an Ed25519 signature.
