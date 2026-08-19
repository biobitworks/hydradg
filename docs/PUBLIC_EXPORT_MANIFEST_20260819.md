# Hack Hydra public export manifest — 2026-08-19

Purpose: define the only files eligible to cross from the private HydraDG working repository into the fresh public Hack Hydra submission repository.

This is a **transformation boundary**, not a Git-history copy.

```text
PRIVATE WORKING REPO
biobitworks/hydradg
        │
        │ PUBLIC_EXPORT_v1
        │ explicit allowlist + secret/size/origin gates
        ▼
FRESH PUBLIC REPO
new Git history created after Aug 12
```

## Why a fresh export is required

The private working repository contains broader Byron/FCO/FCG project material whose content-origin dates are not all established by the Hack Hydra release evidence. A post-Aug-12 commit timestamp does not prove every participant-authored byte in that history was written during the event window.

The public submission therefore uses an explicit fresh-history export instead of making the private working repository public.

## Allowed top-level publication objects

### Project/release documentation
- `README.md`
- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `docs/HACK_HYDRA_ELIGIBILITY_AUDIT_20260819.md`
- `docs/PUBLIC_EXPORT_MANIFEST_20260819.md`
- `docs/PROJECT_FCG_UPDATE_20260819.md`
- `docs/PROJECT_FCG_CHANGELOG_20260819.json`
- `docs/WHY_FCG_UPDATED_20260819.md`
- `docs/KNOWLEDGE_LINK_CONTRACT_20260819.md`
- `docs/WEBSITE_MVP_AND_FALLBACK_20260819.md`
- `docs/LIVE_AND_STATIC_RELEASE_POLICY_20260819.md`
- `docs/MVP_RELEASE_DELIVERABLES_20260819.md`
- `docs/VIDEO_RECORDING_RUNBOOK_20260819.md`
- `docs/TURN_HASHING_POLICY_20260819.md`
- `docs/HASHING_PROOF_20260819.md`
- `docs/HASH_PROOF_CURRENT_PASS_20260819.md`
- `docs/CONTEXT_ICEBERG_4D_RELEASE_WATCH_20260819.md`
- `schemas/context_iceberg_state.schema.json`
- `handoff/SUBMISSION_TASKS_20260819.md`
- `handoff/RELEASE_EXECUTION_LEDGER_20260819.md`

### Web application — Hack-Hydra implementation
- `apps/hydradg-web/`

This contains the judge surface, Context Iceberg, site-level FCO/FCG representation, Track 01/02/03 pages, graph explorer, evidence/eligibility pages, static fallback and fail-closed local/hosted adapters developed for the Hack Hydra release.

### Track 01/02/03 implementation substrate
Only the explicit `HydraDG_DaisyTrain_v0.3.7` files selected by `scripts/build_hackhydra_public_export.sh`.

### Release verification / public-boundary tooling
- `scripts/check_hydradg_web_links.py`
- `scripts/check_static_fallback.py`
- `scripts/check_term_knowledge_coverage.py`
- `scripts/hash_release_artifacts.py`
- `scripts/run_release_watch_parallel_safe.sh`
- `scripts/video_ready_gate.sh`
- `scripts/start_video_demo.sh`
- `scripts/run_hackhydra_release_batches_magicstudio.sh`
- `scripts/build_hackhydra_public_export.sh`

The video scripts are release/presentation tooling only. `video_ready_gate.sh` is non-mutating with respect to HydraDB/SeedGraph/scientific treatments; it validates the current web build, routes, Context Iceberg contract and secret scan. `start_video_demo.sh` starts the built local application when available and otherwise serves the static fallback with an explicit fallback claim note.

### CI recipes
- `.github/workflows/hackhydra-best-use-v2-structural.yml`
- `.github/workflows/hackhydra-judge-lab.yml`
- `.github/workflows/hackhydra-track01-canary.yml`
- `.github/workflows/hackhydra-track02-canary.yml`

## Explicit exclusions

The export must not include:
- historical package trees not admitted by the export transform;
- unrelated/pre-hackathon implementation packages;
- unrelated custody history;
- local datasets or model weights;
- `.env*` other than reviewed `.env.example` files;
- private keys, bearer tokens, credentials or unredacted secret reports;
- `.git` history from the private working repository;
- user-supplied template archives unless redistribution rights are separately established.

## Data policy

Public data identifiers, hashes, revisions and acquisition recipes may be included. Large dataset bytes remain outside Git by default. License/use restrictions remain dataset-specific and must not be silently erased by the public export.

## Publication gates

The builder fails closed unless:
1. source branch is the explicit Hack Hydra release branch;
2. source worktree is clean;
3. every allowlisted path exists;
4. no unexpected `.git`, secret, private-key, model-weight or dataset payload enters the export;
5. Gitleaks passes;
6. no ordinary Git file exceeds the project release size gate;
7. fresh repository history is initialized in the export directory;
8. final human review confirms content-origin eligibility before public repository creation.

## Video boundary

A local video may be recorded before Vercel is current if `VIDEO_READY_LIVE=YES` is established by the non-mutating video gate. If only the static fallback is used, the recording must explicitly describe it as an offline presentation fallback rather than a live HydraDB control surface.

The video gate establishes build/route/security/presentation readiness only. It does not promote scientific claims, establish a signature, or establish a project Merkle/MMR commitment.

## Claim boundary

A fresh-history export removes private-history contamination from the public submission surface. It does **not** independently prove the creation date or originality of every source line. Final content-origin admission remains a human/custody gate.

State:

`PUBLIC_EXPORT_POLICY_DEFINED / FRESH_HISTORY_REQUIRED / VIDEO_GATE_DEFINED / CONTENT_ORIGIN_FINAL_REVIEW_REQUIRED / NOT_SIGNED / NOT_PROJECT_COMMITTED`
