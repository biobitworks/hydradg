# Hack Hydra 2026 — HydraDG Resubmission Candidate

This document is the current review candidate for a Hack Hydra resubmission. It supersedes the older submission copy for **resubmission wording only**; historical submission/video records remain custody evidence.

## 1. Project and delivery surface

- **Project:** HydraDG — Graph-Native Governed Context Engine
- **Primary track:** Track 03 — Memory + Context Retrieval
- **Repository:** https://github.com/biobitworks/hydradg
- **Production authority:** `main` after the final exact-SHA release gates pass
- **Current review branch:** `hack-hydra/final-hosted-fcg-20260820`
- **Pinned backup application commit:** `60120da604f3bb6f30edfadc1d609018089beaef`
- **Pinned backup Vercel deployment:** `dpl_ZYaqRFe5k9FpLsG6SoSuHX1cisoV` — `READY`, preview/non-production
- **Pinned backup URL:** https://hydradg-4u209xn67-biobitworks.vercel.app/
- **Temporary judge-access URL:** https://hydradg-4u209xn67-biobitworks.vercel.app/?_vercel_share=B5GJZ77ZGBvnnTPP3G6xalyCEs4vzYMT
- **Temporary access expiry:** 2026-08-21 21:16 UTC / 2026-08-21 14:16 PDT
- **Backup deployment record:** [`docs/JUDGE_BACKUP_DEPLOYMENT_20260820.md`](docs/JUDGE_BACKUP_DEPLOYMENT_20260820.md)
- **Previously submitted demo video:** https://youtu.be/7EDb6q-loPA
- **Replacement golden-path video:** `PENDING_USER_RECORDING_AND_UPLOAD`
- **Resubmission form:** `PENDING_USER_RESUBMISSION`

The temporary Vercel share URL is intentionally ephemeral. It is a bridge while production redeployment is deferred; it is not the permanent production URL. The pinned deployment itself is bound to the exact source commit above.

## 2. What changed since the earlier submission

The project now exposes a clearer judge path and additional bounded evidence:

1. a golden-path walkthrough centered on **Reference → Poison → Antidote** state transitions;
2. a cross-track **dataset × model × K=5/10/100** Daisy Train matrix;
3. a local-vs-hosted atom/FCO heat-map surface;
4. stricter hosted HydraDB claim ceilings that distinguish **upload accepted / indexing pending** from verified canonical parity;
5. explicit retention of the null result: **0 of 9 co-primary K=10 model-vs-control tests were significant after Holm-Bonferroni correction**.

The resubmission must not convert these additions into a model-superiority claim.

## 3. Problem

Long-lived AI memory systems can flatten or overwrite changing state. When facts are updated, contradicted, or restored, provenance can become difficult to reconstruct, and null or negative experimental outcomes can disappear from the operational narrative.

## 4. Solution

HydraDG is a governed memory/context system built on HydraDB and Fractal Custody Objects / Fractal Custody Graphs (FCO/FCG).

- **FCO — Fractal Custody Object:** bounded content identity plus provenance, evidence class, and claim boundary.
- **FCG — Fractal Custody Graph:** typed dependencies connecting sources, transformations, evidence, claims, and artifacts.
- **HydraDB:** operational query/projection layer for graph traversal, retrieval, temporal state, contradiction, supersession, and provenance lookup.

Canonical FCO identity remains distinct from the hosted HydraDB projection.

## 5. Meaningful HydraDB use

Representative Track 03 relationships include:

```text
Session ─NEXT/PREV→ Session
Session ─ASSERTS→ Fact
Fact ─DERIVED_FROM→ Session
Fact ─ABOUT→ Entity
Fact ─SUPERSEDED_BY→ Fact
Fact ─CONTRADICTS→ Fact
```

The judge application has no Neo4j fallback. The intended operational path is HydraDG → HydraDB → governed graph readback.

## 6. Executed Track 03 evidence

Historical LongMemEval-S full500 evaluation:

- 500 total cases
- 23,867 sessions
- 4,776 entities
- 3,506 facts
- 470 retrieval-scored cases in the K=5 analysis; 30 abstentions excluded

| Route | Hit@5 | Recall@5 | Interpretation |
|---|---:|---:|---|
| A — reference/flat | 0.9638297872 | 0.9065957447 | reference |
| B | 0.9468085106 | 0.8538297872 | no positive hit-rate signal |
| C | 0.9468085106 | 0.8525886500 | no positive hit-rate signal |
| D | 0.9446808500 | 0.8460283700 | no positive hit-rate signal |

The completed K=5 experiment did **not** establish a positive B/C/D Hit@5 advantage over route A. This remains a null/negative result, not a leaderboard claim.

Historical claim ceiling: `LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA`.

## 7. Daisy Train cross-track model × dataset × K evidence

The later cross-track matrix used three datasets, a heuristic control, and three local model lanes. K=10 is the co-primary family; K=5 and K=100 provide depth context.

| Track | Dataset | Heuristic K=10 | Qwen2.5-Coder 7B | Qwen2.5 7B | DeepSeek-R1 14B | Holm result |
|---|---|---:|---:|---:|---:|---|
| Track 01 | EnterpriseRAG-Bench, N=300 | 0.865 | 0.861 | 0.858 | 0.863 | 0/3 significant |
| Track 02 | HydraBlast-Real-Deps, N=250 | 0.932 | 0.929 | 0.926 | 0.931 | 0/3 significant |
| Track 03 | LongMemEval-S, N=470 | 0.941 | 0.935 | 0.931 | 0.938 | 0/3 significant |

Family result: **0 / 9 significant after Holm-Bonferroni correction at alpha 0.05**.

Track 03 heuristic depth observations were `K=5 0.884 → K=10 0.941 → K=100 0.962`. The K=100 lane is interpreted as secondary saturation/dilution evidence, not a new superiority claim.

Overall claim ceiling: `NO_MODEL_BENEFIT_OBSERVED`.

## 8. Hosted HydraDB state

Current canonical hosted projection scope:

- database: `hydradg`
- intended judge collection: `hydradg-judge-demo`
- canonical FCO target: 653
- canonical edge target: 1,692
- source ID: `hydradg-canonical-fcg-653-1692-v1`
- current state at the pinned backup commit: `UPLOAD_ACCEPTED_INDEXING_PENDING`

Canonical 653-FCO / 1,692-edge hosted readback parity is **not established** until readback identity canonicalization, missing/extra accounting, and root comparison pass on hosted evidence.

A historical `default`-collection parity receipt is retained as historical custody evidence and must not be used as proof of the current canonical BYOG projection. See the supersession notice in [`docs/FINAL_HOSTED_FCG_AUDIT_20260820.md`](docs/FINAL_HOSTED_FCG_AUDIT_20260820.md).

## 9. Golden path for judges and the replacement video

Recommended walkthrough:

```text
Home / problem
→ Judge Lab: Reference → Poison → Antidote
→ Track 03 executed evidence
→ Eligibility: cross-track K=5/10/100 matrix + null ceiling
→ Atom Heat Map: local vs hosted status
→ Evidence / Knowledge: FCO → FCG → source lineage
→ Eligibility / closing claim boundary
```

Replacement recording script: [`docs/DEMO_WALKTHROUGH_SCRIPT.md`](docs/DEMO_WALKTHROUGH_SCRIPT.md).

The previously submitted video remains historical/current submission evidence until a replacement video is actually recorded and uploaded. Do not put a placeholder URL into the resubmission form.

## 10. G* / ΔG* boundary

HydraDG `G*` / `ΔG*` is an **application-defined, dimensionless information-state diagnostic**. It is not physical Gibbs free energy and is not measured in joules or kcal/mol. Jensen-Shannon divergence is used separately for Cloud Drift. Neither diagnostic is equivalent to Hit@K, Recall@K, or end-to-end QA accuracy.

## 11. Custody and cryptographic state

- SHA-256 hashes establish byte/content identity where recorded.
- Current project signature state: `NOT_SIGNED` unless a later authorized signing receipt exists.
- Current project Merkle/MMR state: `NOT_MERKLE_COMMITTED` unless a later commitment receipt exists.
- A GitHub commit marked `unverified` / `unsigned` is not a signed Git commit.
- Hash identity, signatures, and provenance do not independently establish scientific correctness.

Licensing remains:

```text
HydraDG software / website / scripts
→ Apache-2.0 where declared

FCO/FCG research publications
+ designated Byron P. Lee / Biobitworks research content
→ CC BY-NC-ND 4.0

historical FCO/FCG CC BY 4.0 metadata
→ SUPERSEDED_METADATA_ERROR
→ custody/history only
```

## 12. Current resubmission status

| Deliverable | Current status |
|---|---|
| Public GitHub repository | PASS |
| Pinned backup Vercel deployment at `60120da...` | READY / preview |
| Temporary judge access link | ACTIVE until stated expiry |
| Current hosted canonical BYOG parity | NOT ESTABLISHED / INDEXING PENDING |
| Daisy Train K=5/10/100 family | EXECUTED; 0/9 Holm-significant |
| Scientific claim ceiling | `NO_MODEL_BENEFIT_OBSERVED` |
| Replacement golden-path video | PENDING USER RECORDING/UPLOAD |
| Resubmission form | PENDING USER RESUBMISSION |
| Signature state | NOT_SIGNED |
| Merkle/MMR state | NOT_MERKLE_COMMITTED |

The permanent production URL and exact final `main` SHA should replace the temporary delivery state only after the production release gates pass on that exact successor.