# Hack Hydra 2026 — HydraDG Resubmission Candidate

This is the current review candidate. The expanded real local-model experiment is **currently running** on `magicstudiobox`; numerical treatment results are intentionally not promoted until stable execution receipts exist.

## 1. Project and delivery surface

- **Project:** HydraDG — Graph-Native Governed Context Engine
- **Primary track:** Track 03 — Memory + Context Retrieval
- **Repository:** https://github.com/biobitworks/hydradg
- **Production authority:** `main` only after exact-SHA release gates pass
- **Review branch:** `hack-hydra/final-hosted-fcg-20260820`
- **Pinned tested application SHA:** `60120da604f3bb6f30edfadc1d609018089beaef`
- **Pinned backup deployment:** `dpl_ZYaqRFe5k9FpLsG6SoSuHX1cisoV` — READY preview/non-production
- **Pinned backup URL:** https://hydradg-4u209xn67-biobitworks.vercel.app/
- **Temporary judge-access URL:** https://hydradg-4u209xn67-biobitworks.vercel.app/?_vercel_share=B5GJZ77ZGBvnnTPP3G6xalyCEs4vzYMT
- **Replacement video:** `PENDING_REAL_MATRIX_COMPLETION_AND_USER_RECORDING`
- **Resubmission form:** `PENDING_USER_RESUBMISSION`

## 2. Current experimental state

The current headline experiment is no longer the historical full500 K=5 ablation by itself.

HydraDG is executing a broader **real local model × dataset × retrieval-depth matrix**:

- **10 local Ollama text-model lanes** from the frozen `magicstudiobox` inventory;
- **Track 01:** EnterpriseRAG-Bench, frozen scope N=300;
- **Track 02:** HydraBlast-Real-Deps, frozen scope N=250;
- **Track 03:** LongMemEval-S-full500, 500 total cases;
- **K=5, K=10, K=100** retrieval depths;
- **K=10** as the co-primary model-vs-control family;
- **K=5 and K=100** as secondary depth analyses;
- a separate **Vithia / Pythia-14m reference-basin and perturbation family**.

Current status for every expanded numerical result:

`CURRENTLY_RUNNING`

No expanded score, corrected p-value, model ranking, depth conclusion, or final claim ceiling should be asserted until the corresponding model execution, frozen FCO/FCG projection, deterministic replay, and statistical receipts exist.

Positive, null, negative, failed, timeout, malformed, and abstaining cells are all admissible evidence.

## 3. Historical Track 03 baseline

The original LongMemEval-S full500 K=5 ablation remains retained as historical executed evidence:

- 500 total cases
- 23,867 sessions
- 4,776 entities
- 3,506 facts
- 470 historical retrieval-scored cases; 30 abstentions excluded

| Route | Hit@5 | Recall@5 | Interpretation |
|---|---:|---:|---|
| A — reference/flat | 0.9638297872 | 0.9065957447 | reference |
| B | 0.9468085106 | 0.8538297872 | no positive hit-rate signal |
| C | 0.9468085106 | 0.8525886500 | no positive hit-rate signal |
| D | 0.9446808500 | 0.8460283700 | no positive hit-rate signal |

Historical claim ceiling:

`LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA`

This historical null/negative result is **not** the final headline of the expanded program. It is the first baseline against which the running real-model matrix will be compared.

## 4. Why HydraDB is load-bearing

HydraDB is the operational graph/query layer for governed longitudinal context. Representative relationships include:

```text
Session ─NEXT/PREV→ Session
Session ─ASSERTS→ Fact
Fact ─DERIVED_FROM→ Session
Fact ─ABOUT→ Entity
Fact ─SUPERSEDED_BY→ Fact
Fact ─CONTRADICTS→ Fact
```

The judge application has no Neo4j fallback. Canonical FCO identity remains distinct from the hosted HydraDB projection.

## 5. Hosted HydraDB state

Current canonical hosted projection target:

- database: `hydradg`
- collection: `hydradg-judge-demo`
- source ID: `hydradg-canonical-fcg-653-1692-v1`
- canonical target: 653 FCO identities / 1,692 FCG edges
- current state: `UPLOAD_ACCEPTED_INDEXING_PENDING`
- canonical hosted parity: `NOT_ESTABLISHED`

Do not claim `653/653` or `1692/1692` hosted parity until the readback identity mapping, missing/extra accounting, and root-comparison gates pass.

## 6. Judge path while the experiment runs

```text
Home
→ Judge Lab: Reference → Poison → Antidote
→ Real Local Model Matrix: every expanded result CURRENTLY_RUNNING
→ Historical Track 03 baseline
→ Atom Heat Map / hosted readback boundary
→ Evidence / Knowledge lineage
→ Eligibility / claim-boundary synthesis
```

Preview route: `/real-local-matrix`.

The page is deliberately pre-staged to receive the final real execution receipts without changing the information architecture.

## 7. Result publication rule

The expanded matrix becomes authoritative only after stable receipts establish:

1. actual local model invocation;
2. frozen model output identity;
3. parsed FCO atoms / graph projection;
4. deterministic K=5/K=10/K=100 replay;
5. case-level metrics;
6. corrected family statistics;
7. explicit failure and abstention accounting.

The earlier three-model development matrix must not be treated as the final real-model empirical result if its numerical values were simulated or hard-coded.

## 8. G* / ΔG* boundary

HydraDG `G*` / `ΔG*` is an application-defined dimensionless information-state diagnostic. It is not physical Gibbs free energy and is not an accuracy metric. Jensen-Shannon divergence is used separately for Cloud Drift.

## 9. Custody and cryptographic state

- hashes establish content identity where recorded;
- signature state: `NOT_SIGNED` unless an authorized signing receipt exists;
- Merkle/MMR state: `NOT_MERKLE_COMMITTED` unless an actual commitment receipt exists;
- unsigned/unverified Git commits are not cryptographically signed releases.

## 10. Current resubmission status

| Deliverable | Current status |
|---|---|
| Public repository | PASS |
| Tested backup app at `60120da...` | READY preview |
| Expanded 10-model × 3-dataset × K matrix | CURRENTLY_RUNNING |
| Vithia perturbation family | CURRENTLY_RUNNING |
| Expanded K=5 results | CURRENTLY_RUNNING |
| Expanded K=10 co-primary family | CURRENTLY_RUNNING |
| Expanded K=100 results | CURRENTLY_RUNNING |
| Final corrected statistical result | CURRENTLY_RUNNING / PENDING_RECEIPTS |
| Final expanded claim ceiling | PENDING_REAL_MATRIX_RESULTS |
| Hosted canonical BYOG parity | INDEXING / READBACK PENDING |
| Replacement video | WAIT FOR REAL MATRIX RECEIPTS |
| Signature state | NOT_SIGNED |
| Merkle/MMR state | NOT_MERKLE_COMMITTED |

Final submission wording and the replacement video should be updated from the real receipts after the running experiment completes.
