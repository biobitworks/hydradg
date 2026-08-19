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

The private working repository contains a large Aug-18 snapshot of broader Byron/FCO/FCG project material. A post-Aug-12 commit timestamp does not prove every participant-authored byte in that snapshot was written during the Hack Hydra window.

The official rule says participant project work starts on/after Aug 12 and that nothing participant-authored before then can go into the submission. Pre-existing upstream libraries, templates, infrastructure and public datasets are permitted when attributed.

Therefore the private repository itself must **not** simply be made public for submission.

## Allowed top-level publication objects

The export builder copies only:

### Project/release documentation
- `README.md`
- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `docs/HACK_HYDRA_ELIGIBILITY_AUDIT_20260819.md`
- `handoff/SUBMISSION_TASKS_20260819.md`
- `handoff/RELEASE_EXECUTION_LEDGER_20260819.md`

### Web application — Hack-Hydra implementation
- `apps/hydradg-web/`

This contains the Judge Lab, site-level FCO/FCG representation, Track 01/02/03 pages, graph explorer, evidence/eligibility pages, and fail-closed local/hosted adapters developed during the Hack Hydra work window.

### Track 01/02/03 implementation substrate
Only the explicit `HydraDG_DaisyTrain_v0.3.7` files below:

- `BEST_USE_MAGICSTUDIO.md`
- `docs/DATASETS_TRACK01_TRACK03.md`
- `eval/best_use_reference/HYDRADB_CI_FAILURE_20260819.md`
- `eval/best_use_reference/REFERENCE_SMOKE80_20260818.md`
- `scripts/analyze_best_use_ablation.py`
- `scripts/best_use_local_server.py`
- `scripts/best_use_local_server_hackhydra.py`
- `scripts/best_use_magicstudio.sh`
- `scripts/best_use_structural_suite.py`
- `scripts/best_use_typed_graph.py`
- `scripts/bootstrap_best_use_magicstudio.sh`
- `scripts/pull_track01_track03_datasets.sh`
- `scripts/run_best_use_longmemeval.py`
- `scripts/run_best_use_typed_longmemeval.py`
- `scripts/run_submission_daisy_track03.sh`
- `scripts/track01_hydraontology_canary.py`
- `scripts/track02_hydrablast_canary.py`

### CI recipes
- `.github/workflows/hackhydra-best-use-v2-structural.yml`
- `.github/workflows/hackhydra-judge-lab.yml`
- `.github/workflows/hackhydra-track01-canary.yml`
- `.github/workflows/hackhydra-track02-canary.yml`

The older `hackhydra-best-use-smoke80.yml` is excluded from the public release allowlist because the final release should expose the current structural and track-specific gates, not obsolete trigger experiments.

## Explicit exclusions

The export must not include:

- historical `HydraDG_DaisyTrain_v0.3.1`, `.3.3`, `.3.4`, `.3.6` package trees;
- historical `HydraDG_HackHydra_Plan_*` snapshots;
- Vithia/Pythia implementation packages;
- XenoDisorder implementation packages;
- Fractal Waves/ECA implementation packages;
- old FCO/FCG implementation packages not freshly implemented for Hack Hydra;
- `custody/` history from unrelated/pre-hackathon work;
- local datasets or model weights;
- `.env*` other than the reviewed `.env.example` in the web app;
- private keys, bearer tokens, credentials, secret reports containing matched secret text;
- `.git` history from the private working repository;
- user-supplied COMPUTE template source archive itself unless its redistribution terms are separately established. The template is attributed as an input/reference; HydraDG's adapted implementation is what is exported.

## Data policy

Public data **identifiers and acquisition recipes** are included. Large dataset bytes remain outside Git by default.

Current executed data state:
- LongMemEval-S: executed and hash-identified.
- EnterpriseRAG-Bench: upstream source confirmed, local pull receipt pending.
- HERB: upstream source confirmed, local pull receipt pending; CC-BY-NC-4.0.
- LongMemEval-V2: upstream source confirmed, local pull receipt pending.
- BEAM: upstream source confirmed, local pull receipt pending.

## Publication gates

The builder must fail closed unless:

1. source branch is the explicit Hack Hydra release branch;
2. source worktree is clean;
3. every allowlisted path exists;
4. no unexpected `.git`, secret, private-key, model-weight, or dataset payload enters the export;
5. Gitleaks passes if installed; otherwise publication remains `SECRET_SCAN_REQUIRES_GITLEAKS`;
6. no ordinary Git file exceeds the project release size gate;
7. fresh repository history is initialized in the export directory;
8. final human review confirms content-origin eligibility before `gh repo create --public`.

## Claim boundary

A fresh-history export removes private-history contamination from the public submission surface. It does **not** independently prove the creation date or originality of every source line. The content-origin review remains a human/custody admission gate.

State:

`PUBLIC_EXPORT_POLICY_DEFINED / FRESH_HISTORY_REQUIRED / CONTENT_ORIGIN_FINAL_REVIEW_REQUIRED / NOT_SIGNED / NOT_MERKLE_COMMITTED`
