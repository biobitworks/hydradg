# HydraDG — Hack Hydra Track 03 Roadmap

Status: ACTIVE_TEST_ROADMAP
Updated: 2026-08-18
Workstream: HydraDG / Hack Hydra Track 03 — Memory + Context Retrieval

## Context gate

Canonical working tuple:

- primary private repository: `biobitworks/hydradg`
- active setup/test branch: `setup/remote-work-20260818`
- HydraDB review mirror: `biobitworks/hydradb-hackhydra`
- HydraDB upstream: `hydra-db/hydradb`
- HydraDB reproducibility pin: `6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219`
- control host: `magicPRObox`
- persistent execution host: `magicSTUDIObox`
- canonical local paths: `/Users/byron/projects/active/hydradg` and `/Users/byron/projects/active/hydradb`
- transport: ordinary SSH over Tailscale
- Ollarma: governed model/API bridge, not shell administration

If this tuple does not match the active conversation/repository/host, stop and record `CONTEXT_MISMATCH` before write or execution work.

## Product thesis

HydraDG is a HydraDB-native memory and reproducibility microscope. It represents turns, evidence, transformations, claims, perturbations and recovery as typed graph objects so a retrieval system can answer not only **what is remembered now**, but **where an evidence/execution path first diverged, what downstream state is affected, what historical answer remains reconstructable, and whether repair returns the system to an admissible equivalent state**.

The Best Use of HydraDB case must demonstrate that relationships, traversal, temporal/custody context and dependency propagation materially improve the answer. HydraDB must be functional infrastructure, not a decorative persistence layer.

## Current status

| Gate | Status | Evidence / next dependency |
|---|---|---|
| Private HydraDG canonical repo | DONE | `biobitworks/hydradg` exists; private working history preserved |
| Test/stage custody concept | DONE-POLICY | private test/stage; clean public export remains separate |
| HydraDB private review mirror | DONE | `biobitworks/hydradb-hackhydra` |
| HydraDB exact source pin | DONE | `6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219` |
| MagicPro canonical HydraDB checkout | DONE | `/Users/byron/projects/active/hydradb`, mirror main + `hackhydra/track03` at pin |
| Context-drift incident captured | DONE-STAGING | HydraDB/LessWrong confusion recorded as FCO/FCG staging evidence |
| Turn-start context route gate | DONE-POLICY | `custody/CONTEXT_ROUTE_GATE.md` |
| MagicStudio SSH/Tailscale route | BLOCKED | latest bounded check ended `STUDIO_SSH_TAILSCALE_FAILED` |
| MagicStudio dependency audit | BLOCKED-BY-SSH | run from MagicPro after transport repair |
| MagicStudio repo synchronization | PENDING | HydraDG, HydraDB, Ollarma, Watchtower |
| Ollarma live local-model response | PENDING | require `/health` + real `/chat` response receipt |
| Watchtower remote dashboard | PENDING | localhost on Studio, tunnel to MagicPro |
| Persistent HydraDB on Studio | PENDING | graph-node + real write/read + tunnel receipt |
| FCO/FCG -> HydraDB adapter | PENDING | implement only after runtime write/read gate |
| Context-drift FCO ingestion into HydraDB | PENDING | ingest immutable staging IDs, then query them back |
| Track03 smoke80 | PENDING | paired, frozen schema; no full500 first |
| Controlled perturbation/recovery A-D | PENDING | first divergence, blast radius, recovery classification |
| Best-Use system ablation | PENDING | flat/vector vs graph-native vs full custody graph |
| Statistical analysis | PENDING | paired bootstrap CI + appropriate paired tests; fixed seed |
| Evaluation freeze | PENDING | freeze queries, metrics, perturbations and result schema before full500 |
| LongMemEval-S full500 | PENDING | only after smoke80 and evaluation freeze |
| Public-safe stage export | PENDING | allowlist export, secret/PII/large-file/license gates |
| Public GitHub repository | PENDING | separate clean public history; do not flip private repo public |
| Public README/setup/HydraDB explanation | PENDING | fresh-clone tested |
| Third-party attribution | PENDING | code, APIs, models, datasets and licenses |
| License package | PENDING | original HydraDG code: Apache-2.0 target; HydraDB modifications remain AGPL-3.0; content license reviewed separately |
| <=3 minute demo video | PENDING | record only after live bounded demo is reproducible |
| Official submission form | PENDING | submit only after public repo + video are final |

## Best Use of HydraDB evaluation path

1. Repair the MagicPro -> MagicStudio SSH/Tailscale path.
2. Audit Studio dependencies remotely; install only evidenced missing requirements.
3. Synchronize all canonical repositories from GitHub.
4. Prove Ollarma model response, Watchtower access, and persistent HydraDB write/read.
5. Ingest the real context-drift incident plus controlled synthetic memory histories into HydraDB.
6. Implement graph-native queries for current state, historical state, first divergence, affected descendants, contradiction/supersession and recovery.
7. Run smoke80 with identical item sets across baselines and HydraDG variants.
8. Compute paired metrics and confidence intervals; inspect failures and freeze the evaluation protocol.
9. Run full500 only after the protocol is frozen.
10. Produce a public-safe result table, architecture diagram, reproducibility receipt and <=3 minute demo.

## Compute / hosting roles

| Surface | Role |
|---|---|
| magicSTUDIObox | canonical persistent HydraDB, Ollarma/local models, Watchtower, Daisy training |
| magicPRObox | control plane, development, tunnels, Git checkpoints, review |
| Modal | preferred burst CPU/GPU for frozen batch evaluations when local compute is insufficient |
| Kaggle | optional free GPU batch fallback; not a persistent service |
| Daytona | optional clean-room sandbox for fresh-clone/install/reproduction tests; not a database |
| Exa / Apify | optional externally retrieved evidence lane; never a required dependency of the deterministic core benchmark |
| Vercel | optional public UI/static demo surface; do not expose the private home HydraDB directly |
| GitHub | public submission source + private test/stage custody checkpoints |

## Upstream HydraDB fork / PR rule

Do not modify HydraDB merely to create a pull request. Use the upstream pinned service unchanged if it already supports the required graph operations. If HydraDG discovers a reusable HydraDB bug fix or generally useful graph/query/runtime feature, implement it on `biobitworks/hydradb-hackhydra:hackhydra/track03`, test it, then create a public fork/upstream PR. Any HydraDB-derived modification remains governed by upstream AGPL-3.0.

## Submission admission gate

The submission is not COMPLETE until all three are actually present before the deadline:

- official submission form submitted;
- demo video <= 3 minutes;
- public GitHub repository.

Public repository admission additionally requires complete source, clear README, setup/run instructions, an explicit explanation of HydraDB use, dependency/environment documentation, attribution, an open-source code license, secret/PII scan, and a fresh-clone reproduction test.
