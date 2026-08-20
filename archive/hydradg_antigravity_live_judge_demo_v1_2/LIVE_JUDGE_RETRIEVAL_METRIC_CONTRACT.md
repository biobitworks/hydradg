# Live Judge Retrieval Metric Contract v1

## Required display fields

Every selected result/timeline state should expose, where receipt-owned:

- `hit_at_k`
- `recall_at_k`
- `delta_hit_at_k`
- `delta_recall_at_k`

These are empirical retrieval outcomes.

They are separate from:

- `delta_g_star`
- `structural_cloud_drift`
- `retrieval_cloud_drift`

## Terminology

`Hit@K` may be described as retrieval hit rate.

Do not describe it as end-to-end QA accuracy.

If the product label must say Accuracy, render:
`Accuracy proxy (Hit@K)`.

## Claim boundary

Observed co-movement between ΔG*, Hit@K and Recall@K is descriptive unless a separate
preregistered inferential test supports association/causality.
