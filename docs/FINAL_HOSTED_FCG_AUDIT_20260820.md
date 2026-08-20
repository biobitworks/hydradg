# Final Hosted FCG Audit & Release Summary (`hack-hydra/final-hosted-fcg-20260820`)

## Executive Summary

This document certifies the final, exact-SHA, judge-reviewable **HydraDG release** on branch `hack-hydra/final-hosted-fcg-20260820`.

The release reconciles:
- `hack-hydra/curated-vercel-lineage-20260820` (Curated Vercel judge UI, Hack Hydra eligibility proofs, hosted HydraDB v2 API routes, presentation evolution lineage)
- `feat/context-vs-entropy-experiment` (Context vs Entropy secret benchmark, Gitleaks raw intake, HydraDB graph classification, Vithia baseline repair supplementary card)

---

## 1. Local ↔ Hosted HydraDB v2 Parity (`hydradg`)

- **Database Name:** `hydradg`
- **Collection:** `default` (server-side API routes `/api/hydradb-v2/collections`, `/api/hydradb-v2/query`)
- **API Version:** `v2`
- **Environment Variables:** Server-only `HYDRA_DB_API_KEY`, `HYDRADB_DATABASE=hydradg`, `HYDRADB_API_URL=https://api.hydradb.com` (no `NEXT_PUBLIC_` secret disclosure).
- **Parity Receipt:** [`eval/hosted_migration_20260820/HOSTED_PARITY.json`](file:///Users/byron/projects/active/hydradg/eval/hosted_migration_20260820/HOSTED_PARITY.json)

```json
{
  "canonical_fco_set_delta": 0,
  "canonical_edge_delta": 0,
  "canonical_content_hash_delta": 0,
  "status": "PASS"
}
```

---

## 2. Time & Space FCG State Snapshots (T0 .. T5)

Receipt: [`eval/hosted_migration_20260820/FCG_TIMEPOINTS.json`](file:///Users/byron/projects/active/hydradg/eval/hosted_migration_20260820/FCG_TIMEPOINTS.json)

| Timepoint | Classification | Score State / Metrics | Note |
| :--- | :--- | :--- | :--- |
| **T0 REFERENCE** | Synthetic Fixture | \(G^* \approx -0.061230\), \(\Delta G^* = 0\), Cloud Drift = `0.0` | Frozen baseline comparison state |
| **T1 MUTATION** | Synthetic Fixture | \(G^* \approx 0.572956\), \(\Delta G^* \approx +0.634186\), Cloud Drift = `40.3629` | Controlled poison perturbation state |
| **T2 RESTORATION** | Synthetic Fixture | \(G^* \approx -0.027496\), \(\Delta G^* \approx -0.600452\), Cloud Drift = `1.8729` | Antidote state preserving counterevidence |
| **T3 HOSTED MIGRATION** | Production State | `SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION` | Local → Hosted HydraDB v2 state transition |
| **T4 CONTEXT VS ENTROPY** | Production State | `SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION` | 18,567 findings, 99.94% coverage, 12 abstentions |
| **T5 FINAL JUDGE RELEASE** | Production State | `SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION` | Final integrated judge release SHA |

---

## 3. Reference & Link Custody Audit

Receipt: [`eval/hosted_migration_20260820/REFERENCE_LINK_AUDIT.json`](file:///Users/byron/projects/active/hydradg/eval/hosted_migration_20260820/REFERENCE_LINK_AUDIT.json)

- **Total Web Routes Audited:** `11` (`/`, `/judge`, `/track03`, `/results/context-vs-entropy`, `/graph`, `/knowledge`, `/evidence`, `/eligibility`, `/how-to`, `/evolution`, `/fco/[id]`)
- **Unresolved Link Count:** `0`
- **SourceFCO Resolution Coverage:** `100.0%`
- **Citation Lineage:**
  - **Jensen-Shannon Divergence / Cloud Drift:** Lin 1991 (`doi:10.1109/18.61115`)
  - **G* / ΔG* Information Diagnostic:** HydraDB internal governed diagnostic specification.

---

## 4. Presentation Evolution & Supersession Lineage

Legacy UI states are preserved as historical FCG states:
```
PresentationState_v1 (MVP)
       ↓  SUPERSEDED_BY
PresentationState_v2 (Context Iceberg)
       ↓  SUPERSEDED_BY
FinalJudgePresentation (Curated Hosted Release)
```

---

## 5. Bounded Scientific & Technical Claims

1. **HydraDB v2 Context Classification:** 99.94% false-positive resolution on raw Gitleaks findings via path and FCO/FCG graph context.
2. **Modal Token Item Preservation:** Preserved as `REVOKED_HISTORICAL_CREDENTIAL` (`USER_ATTESTED_REVOKED`).
3. **Vithia Supplemental Baseline:** Repaired Pythia-14m reference basin (`AdamW lr=1e-4, eps=1e-5, grad_clip_norm=1.0`) with 100% numerical admissibility. Does NOT claim improved LM accuracy or end-to-end QA superiority.
4. **No Claim Boundary Violations:** `NOT_SIGNED` (no private key signing performed), `NOT_MERKLE_COMMITTED` (no MMR commitment performed).
