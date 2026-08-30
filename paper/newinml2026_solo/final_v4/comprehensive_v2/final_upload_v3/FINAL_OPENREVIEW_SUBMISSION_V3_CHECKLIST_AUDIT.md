# NewInML OpenReview V3 — Checklist Truthfulness Audit

Audited against reviewer-facing PDF text only (`FINAL_OPENREVIEW_SUBMISSION_V3.pdf`).

| Checklist item | Answer | Supported by main PDF? | Notes |
| --- | --- | --- | --- |
| Claims | Yes | Yes | Abstract/Introduction state underpowered EXP-008/009 and non-promotion of treatment effects. |
| Limitations | Yes | Yes | Section Limitations discusses bounded replication, local-only lanes, interrupted SeedGraph, omitted successor lane. |
| Theory assumptions and proofs | N/A | Yes | No formal theorems. |
| Experimental reproducibility | Yes | Partial | Frozen manifests, conditions, models, scorers disclosed; full independent rerun not bundled (consistent with open-access No). |
| Open access to data and code | No | Yes | Correctly states internal frozen custody artifacts; no public code/data bundle. |
| Experimental setting/details | Yes | Yes | C0/C1, models, manifest, replicate count, aggregation rule in Experimental Setup. |
| Experiment statistical significance | No | Yes | Underpowered terminals; no CIs — accurate. |
| **Experiments compute resources** | **No** | **Yes** | Hardware/memory class reported; **wall-time per experiment not retained** — corrected from V2 Yes. |
| Code of ethics | Yes | Yes | No human-subjects experiments. |
| Broader impacts | N/A | Yes | Infrastructure paper; no dedicated societal-impact section. |
| Safeguards | N/A | Yes | No new high-risk model/dataset release. |
| **Licenses for existing assets** | **No** | **Yes** | Bibliography credits prior work but **does not enumerate per-asset SPDX/terms** for all third-party models/datasets — corrected from V2 Yes. |
| New assets | No | Yes | No new public assets released. |
| Crowdsourcing / human subjects | N/A | Yes | Synthetic cases only. |
| IRB | N/A | Yes | No human-subjects research. |
| LLM usage | Yes | Yes | AI and agent methodology disclosure section present. |

**CHECKLIST_TRUTHFULNESS_GATE=PASS**

License layers preserved in audit (not relabeled by article CC BY 4.0):
- Article / OpenReview submission: CC BY 4.0
- HydraDG software (repository): Apache-2.0
- Separately published companion FCO/FCG preprints: CC BY-NC-ND 4.0
- Third-party models/datasets/software: respective upstream terms (not fully enumerated in PDF → checklist No)
