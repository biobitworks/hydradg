# Historical Hosted FCG Audit Snapshot — 2026-08-20

## Supersession notice

This file is retained as **historical custody evidence**. It is **not** the current certificate for the canonical 653-FCO / 1,692-edge BYOG projection.

The earlier Section 1 `PASS` below refers to a historical `default`-collection parity scope and must not be used to claim current parity for the later canonical source `hydradg-canonical-fcg-653-1692-v1` in collection `hydradg-judge-demo`.

At pinned judge backup commit `60120da604f3bb6f30edfadc1d609018089beaef`, the current hosted state is bounded as:

`UPLOAD_ACCEPTED_INDEXING_PENDING`

Current canonical hosted parity is **NOT ESTABLISHED** until hosted readback is canonicalized and verifies expected identity/edge counts, missing/extra sets, and roots. The current `/eligibility` surface intentionally reflects this lower claim ceiling.

Nothing in this supersession notice deletes the historical receipt or failure/success evidence; it only prevents evidence from a different collection/scope from being promoted into the current claim.

---

## Historical Executive Summary

This snapshot recorded an earlier HydraDG hosted/release audit on branch `hack-hydra/final-hosted-fcg-20260820`. Subsequent hosted-ingestion work changed the canonical BYOG scope, so hosted parity statements must be interpreted using the supersession notice above.

The historical release reconciled:
- `hack-hydra/curated-vercel-lineage-20260820` (curated Vercel judge UI, Hack Hydra eligibility proofs, hosted HydraDB v2 API routes, presentation evolution lineage)
- `feat/context-vs-entropy-experiment` (Context vs Entropy secret benchmark, Gitleaks raw intake, HydraDB graph classification, Vithia baseline repair supplementary card)

---

## 1. Historical Local ↔ Hosted HydraDB v2 parity receipt

Historical scope:

- Database name: `hydradg`
- Collection: `default`
- API version: `v2`
- Environment variables: server-only `HYDRA_DB_API_KEY`, `HYDRADB_DATABASE=hydradg`, `HYDRADB_API_URL=https://api.hydradb.com`
- Historical parity receipt: `eval/hosted_migration_20260820/HOSTED_PARITY.json`

Historical payload:

```json
{
  "canonical_fco_set_delta": 0,
  "canonical_edge_delta": 0,
  "canonical_content_hash_delta": 0,
  "status": "PASS"
}
```

**Current interpretation:** `HISTORICAL_DEFAULT_COLLECTION_PARITY_ONLY`; not proof of the later `hydradg-judge-demo` 653/1,692 canonical projection.

---

## 2. Time & Space FCG State Snapshots (T0 .. T5)

Historical receipt: `eval/hosted_migration_20260820/FCG_TIMEPOINTS.json`

| Timepoint | Classification | Score State / Metrics | Note |
| :--- | :--- | :--- | :--- |
| **T0 REFERENCE** | Synthetic Fixture | `G* ≈ -0.061230`, `ΔG* = 0`, Cloud Drift `0.0` | Frozen baseline comparison state |
| **T1 MUTATION** | Synthetic Fixture | `G* ≈ 0.572956`, `ΔG* ≈ +0.634186`, Cloud Drift `40.3629` | Controlled poison perturbation state |
| **T2 RESTORATION** | Synthetic Fixture | `G* ≈ -0.027496`, `ΔG* ≈ -0.600452`, Cloud Drift `1.8729` | Antidote state preserving counterevidence |
| **T3 HOSTED MIGRATION** | Production State | `SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION` | Historical local → hosted transition |
| **T4 CONTEXT VS ENTROPY** | Production State | `SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION` | Historical context-vs-entropy state |
| **T5 JUDGE RELEASE SNAPSHOT** | Production State | `SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION` | Historical integrated judge snapshot |

These state diagnostics are not benchmark accuracy metrics.

---

## 3. Historical reference & link custody audit

Historical receipt: `eval/hosted_migration_20260820/REFERENCE_LINK_AUDIT.json`

- Total web routes audited: 11
- Unresolved link count: 0
- SourceFCO resolution coverage: 100.0%
- Jensen-Shannon Divergence / Cloud Drift citation: Lin 1991, DOI `10.1109/18.61115`

Later page/route changes require their own exact-SHA checks; this historical audit cannot establish correctness for a successor commit.

---

## 4. Presentation evolution & supersession lineage

```text
PresentationState_v1 (MVP)
       ↓ SUPERSEDED_BY
PresentationState_v2 (Context Iceberg)
       ↓ SUPERSEDED_BY
FinalJudgePresentation (curated hosted snapshot)
       ↓ SUPERSEDED_BY
CurrentResubmissionCandidate (golden path + K=5/10/100 + hosted parity ceiling)
```

---

## 5. Bounded historical scientific & technical claims

Historical evidence retained in this snapshot includes context-classification work, revoked-credential custody treatment, and Vithia supplemental baseline work. Those artifacts keep their own evidence classes and claim ceilings.

Current project-wide boundaries remain:

- no model benefit claim beyond executed statistics;
- no current canonical hosted BYOG parity claim while indexing/readback is unresolved;
- signature state: `NOT_SIGNED` unless a later authorized signing receipt exists;
- Merkle/MMR state: `NOT_MERKLE_COMMITTED` unless a later commitment receipt exists.

A hash is not a signature. Provenance is not independent replication. Historical parity in one scope is not parity in a later scope.