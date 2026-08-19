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

The Hack Hydra build-window policy recorded in the project therefore keeps pre-existing upstream frameworks, templates, APIs and public datasets as attributed dependencies while excluding ambiguous participant-authored pre-window implementation from the public submission surface.

The private repository itself must **not** simply be made public for submission.

## Allowed top-level publication objects

### Project/release documentation

The current builder allowlists:

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
- `docs/TURN_HASHING_POLICY_20260819.md`
- `docs/HASHING_PROOF_20260819.md`
- `docs/HASH_PROOF_CURRENT_PASS_20260819.md`
- `docs/RELEASE_ARTIFACT_HASHING_HOWTO_20260819.md`
- `docs/HASH_REFETCH_COMMANDS_20260819.md`
- `docs/CONTEXT_ICEBERG_SCORE_SPEC.md`
- `handoff/SUBMISSION_TASKS_20260819.md`
- `handoff/RELEASE_EXECUTION_LEDGER_20260819.md`
- `handoff/RELEASE_WATCH_CONTEXT_ICEBERG_EXECUTION_20260819.md`

### Web application — Hack-Hydra implementation

- `apps/hydradg-web/`

The tree contains the public overview, Judge Lab, Track 01/02/03 surfaces, Evidence, Eligibility, application-level site FCG, content-addressed website knowledge projection, Context Iceberg/4D graph explorer, read-only release/status APIs and static fallback artifacts.

The Context Iceberg UI is a display/projection layer. It must not choose G* weights, alter the active scientific lane, or turn a display state into scientific evidence.

### Release verification / public-boundary tooling

- `scripts/check_hydradg_web_links.py`
- `scripts/check_term_knowledge_coverage.py`
- `scripts/check_static_fallback.py`
- `scripts/hash_release_artifacts.py`
- `scripts/run_hackhydra_release_batches_magicstudio.sh`
- `scripts/build_hackhydra_public_export.sh`

### Track 01/02/03 implementation substrate

Only the explicit current `HydraDG_DaisyTrain_v0.3.7` files named by the export builder may cross the boundary. Historical package trees and unrelated project implementations remain excluded.

### CI recipes

- `.github/workflows/hackhydra-best-use-v2-structural.yml`
- `.github/workflows/hackhydra-judge-lab.yml`
- `.github/workflows/hackhydra-track01-canary.yml`
- `.github/workflows/hackhydra-track02-canary.yml`

## Explicit exclusions

The export must not include:

- historical `HydraDG_DaisyTrain_v0.3.1`, `.3.3`, `.3.4`, `.3.6` package trees;
- historical HydraDG plan snapshots outside the explicit allowlist;
- Vithia/Pythia, XenoDisorder, Fractal Waves/ECA or other unrelated implementation packages;
- unrelated/pre-hackathon `custody/` history;
- local datasets or model weights;
- `.env*` other than reviewed `.env.example`;
- private keys, bearer tokens, credentials or secret reports containing matched secret text;
- `.git` history from the private working repository;
- rights-restricted HERB dataset contents;
- user-supplied COMPUTE template source archive itself unless redistribution terms are separately established.

## Data policy

Large dataset bytes remain outside Git. Public-safe identifiers, source revisions, manifests, adapters and bounded receipts may be exported when allowed.

Current acquisition state from retained local pull evidence:

- LongMemEval-S cleaned: downloaded/hash-identified and historical full500 retrieval ablation executed.
- EnterpriseRAG-Bench: downloaded and SHA-manifested; real Track 01 benchmark evaluation remains unclaimed.
- HERB: downloaded and SHA-manifested; current project rights state is `CC-BY-NC-4.0 / RIGHTS-GATED`; dataset contents excluded from public export.
- LongMemEval-V2 core: downloaded and SHA-manifested; not mixed into the frozen LongMemEval-S experiment.
- BEAM: downloaded and SHA-manifested; future adapter/evaluation state only.
- BEAM-10M: deferred.

A dataset being downloaded does not establish atomization, HydraDB projection, evaluation performance or scientific correctness.

## Context Iceberg / website knowledge policy

Public code may include:

- the deterministic CloudDrift/JSD implementation contract;
- the read-only `/api/math/current` adapter;
- application-level website knowledge FCOs;
- the `/api/knowledge` projection;
- the 4D/context-cloud visualization;
- static Context Iceberg fallback.

It must not export a private local receipt path, private signing key, private dataset bytes or invented scientific score.

When no frozen Context Iceberg observation exists, public UI must display `PENDING` and may only show the explicitly labelled demo-control halo grammar.

## Publication gates

The builder must fail closed unless:

1. source branch is the explicit admitted Hack Hydra release branch;
2. source worktree is clean;
3. every allowlisted path exists;
4. no unexpected `.git`, secret, private-key, model-weight or dataset payload enters the export;
5. Gitleaks passes;
6. no ordinary Git file exceeds the project release size gate;
7. SHA-256 manifest is generated over the exported files;
8. fresh one-commit repository history is created;
9. final human content-origin review passes before public publication.

The parallel Context Iceberg branch itself is **not** the publication source. Its changes must first be reviewed, locally built/tested, then admitted into the explicit release branch before the export builder can run.

## Claim boundary

A fresh-history export establishes a bounded selected publication surface and retained byte identities after its hashing gate. It does **not** independently prove source-line originality, scientific correctness, author signature, live HydraDB Merkle commitment or independent replication.

State:

`PUBLIC_EXPORT_POLICY_DEFINED / CONTEXT_ICEBERG_INCLUDED_AFTER_RELEASE_ADMISSION / FRESH_HISTORY_REQUIRED / FINAL_CONTENT_ORIGIN_REVIEW_REQUIRED / NOT_SIGNED / NOT_MERKLE_COMMITTED`
