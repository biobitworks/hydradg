# Hack Hydra 2026 — HydraDG Judge Submission

HydraDG is a graph-native governed memory experiment for changing, contradictory longitudinal context. The judge-facing application uses a stable golden walkthrough — Reference → Poison → Antidote — while experimental evidence remains explicitly classified by execution state and custody.

This submission is intentionally fail-closed: development artifacts that cannot be tied to real execution receipts are retained in Git/FCO lineage but are not promoted as empirical results.

## 1. Judge delivery surface

- **Project:** HydraDG — Graph-Native Governed Context Engine
- **Primary track:** Track 03 — Memory + Context Retrieval
- **Repository:** https://github.com/biobitworks/hydradg
- **Review branch:** `hack-hydra/final-hosted-fcg-20260820`
- **Production authority:** `main` only after exact-SHA release gates pass
- **Current judge UI baseline before this submission-copy commit:** `600a2379c83c8da772e6f2c4b0fbf1d4a53186b8`
- **Video state:** `READY_TO_RECORD_TIME_STAMPED_PREVIEW`
- **BEAM state:** `PREPARED_UNEXECUTED`
- **Expanded model-matrix state:** `NOT_ESTABLISHED_FROM_REAL_CASE_EXECUTION`

The preview may receive additional **receipt-backed** experimental data through **11:59 PM PDT on August 20, 2026**. The recording is a time-stamped walkthrough of the submission architecture and evidence state; later updates must not alter the preregistered hypothesis, delete prior evidence, or promote unsupported claims.

## 2. Canonical judge walkthrough

```text
Home
→ GOLDEN PATH
   01 Reference
   02 Poison
   03 Antidote
→ Historical Track03 executed retrieval evidence
→ Expanded Matrix: audited evidence states
→ BEAM 1M: preregistered/queued architecture routes
→ Evidence / Knowledge / FCO-FCG lineage
→ Eligibility / claim boundary
```

The golden path is the stable product demonstration. It shows that a conflicting state can be introduced and later repaired without deleting the predecessor, contradiction, provenance, or recovery history.

## 3. Current executed scientific evidence

The currently established Track03 benchmark is the historical LongMemEval-S full500 K=5 retrieval ablation:

- 500 total cases
- 23,867 sessions
- 4,776 entities
- 3,506 facts
- 470 retrieval-scored cases; 30 abstentions excluded from that retrieval score

| Route | Hit@5 | Recall@5 | Interpretation |
|---|---:|---:|---|
| A — reference/flat | 0.9638297872 | 0.9065957447 | reference |
| B | 0.9468085106 | 0.8538297872 | no positive hit-rate signal |
| C | 0.9468085106 | 0.8525886500 | no positive hit-rate signal |
| D | 0.9446808500 | 0.8460283700 | no positive hit-rate signal |

Historical claim ceiling:

`LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA`

HydraDG preserves this null/negative result. It is not converted into a positive claim and is not presented as an end-to-end QA score.

## 4. Expanded local-model matrix — current claim boundary

The repository contains development attempts to expand evaluation across the local `magicstudiobox` model inventory. Forensic review found that prior versions contained literal or synthetic treatment/evaluator values.

The `100316e9...` v2 script still generated development receipts and literal K metrics rather than performing real case-level Ollama inference. Therefore the judge-facing expanded matrix now uses this claim ceiling:

`EXPANDED_MODEL_MATRIX_NOT_ESTABLISHED_FROM_REAL_CASE_EXECUTION`

Established from the current runtime review:

- 10 local generative model names can be discovered from `ollama list`;
- external evaluator packages DeepEval, Ragas, Inspect AI, BEIR, MTEB and lm-eval were not installed in the audited runtime and therefore have no promoted scores;
- Vithia/Pythia-14m repaired-ablation evidence is `NOT_ESTABLISHED_FROM_EXECUTION_RECEIPT` in the current repository review;
- historical hard-coded/synthetic evaluator artifacts remain preserved as development lineage rather than primary empirical evidence.

A future expanded result becomes authoritative only after real dataset-row inference, frozen model-output receipts, measured ranked retrieval IDs, case-level metrics, deterministic retrieval replay where claimed, explicit failure/abstention accounting, and the preregistered statistics all pass.

## 5. BEAM 1M — preregistered next experiment

HydraDG has prepared the BEAM 1M benchmark lane with:

- 35 conversations;
- 700 probes;
- Route A: dense content;
- Route B: dense + BM25;
- Route C: + sliding-window contextual enrichment;
- Route D: + adaptive query expansion;
- Route E: + bounded FCG graph traversal;
- Route F: + valid-time/current-state/supersession filtering;
- Route G: + reranking/fusion;
- Route H: + full FCO/FCG custody and claim-state controls.

Current HydraDG BEAM numerical state:

`QUEUED / PREPARED_UNEXECUTED`

HydraDB's published **82% overall BEAM 1M** score is shown only as an external reference. It is not treated as a HydraDG result and is not decomposed into invented route-by-route reference scores.

Future preregistered hypothesis:

> Can explicit FCO supersession, validity, provenance and claim-state edges improve BEAM knowledge-update and contradiction-resolution performance without degrading HydraDB-style temporal reasoning, event ordering or multi-session performance?

This hypothesis is future work and is not part of the current empirical submission.

## 6. Why HydraDB is load-bearing

HydraDB is the operational graph/query layer for governed longitudinal context. Representative relationships include:

```text
Session ─NEXT/PREV→ Session
Session ─ASSERTS→ Fact
Fact ─DERIVED_FROM→ Session
Fact ─ABOUT→ Entity
Fact ─SUPERSEDED_BY→ Fact
Fact ─CONTRADICTS→ Fact
```

The architecture is intentionally compatible with hybrid memory retrieval: contextual enrichment, dense and sparse candidates, query expansion, bounded graph traversal, temporal/current-state filtering, and reranking/fusion. FCO/FCG adds explicit custody, identity and claim-state boundaries around those transformations.

## 7. Hosted HydraDB boundary

Canonical hosted target retained in the project:

- database: `hydradg`
- collection: `hydradg-judge-demo`
- source ID: `hydradg-canonical-fcg-653-1692-v1`
- canonical target: 653 FCO identities / 1,692 FCG edges

Hosted parity must remain `NOT_ESTABLISHED` until a scoped readback proves identity mapping, missing/extra accounting and root comparison. Upload acceptance or commit messages alone are not parity evidence.

## 8. Custody and cryptographic state

- SHA-256 hashes establish content identity where actual content was hashed;
- development/synthetic hashes do not convert synthetic values into empirical observations;
- signature state: `NOT_SIGNED` unless an actual private-key signing operation and verification receipt exist;
- Merkle/MMR state: `ROOT_COMPUTED_NOT_MERKLE_COMMITTED` or `NOT_MERKLE_COMMITTED` unless an actual commitment operation is performed;
- unsigned Git commits are not cryptographically signed releases.

## 9. Video recording language

Use this disclosure near the beginning of the recording:

> This is the HydraDG judge preview as of August 20. The gold Reference → Poison → Antidote walkthrough is the stable judge path. The historical Track03 retrieval ablation is retained as executed evidence. Newer expanded model attempts that did not satisfy the execution audit were reclassified rather than promoted. BEAM 1M is preregistered and queued. The experimental evidence surface may receive additional receipt-backed results through 11:59 PM Pacific tonight, while Git preserves every prior state.

Closing line:

> HydraDG is not a leaderboard claim. It is a governed memory experiment: change state, find the first divergence, preserve custody, test recovery, and keep positive, null, negative, failed and abstaining evidence in the same graph.

## 10. Current resubmission status

| Deliverable | Current status |
|---|---|
| Public repository | PASS |
| Golden judge path | READY |
| Persistent judge breadcrumbs | SOURCE READY; use latest successful preview containing the current branch state |
| Historical Track03 retrieval evidence | EXECUTED / PRESERVED |
| Expanded real local-model matrix | NOT_ESTABLISHED_FROM_REAL_CASE_EXECUTION |
| External evaluator package scores | BLOCKED / NOT PROMOTED |
| Vithia repaired-ablation result | NOT_ESTABLISHED_FROM_EXECUTION_RECEIPT |
| BEAM 1M data/preprocessing/preregistration | PREPARED |
| BEAM 1M HydraDG numerical results | QUEUED |
| Hosted canonical HydraDB parity | NOT_ESTABLISHED |
| Replacement video | READY TO RECORD AS TIME-STAMPED PREVIEW |
| Signature state | NOT_SIGNED |
| Merkle/MMR state | NOT_MERKLE_COMMITTED unless an actual commitment receipt exists |

After the video is recorded, the URL can be inserted into this submission. Additional experiment data may be added through the stated cutoff only when backed by real execution receipts and without altering the preregistered claim boundaries.
