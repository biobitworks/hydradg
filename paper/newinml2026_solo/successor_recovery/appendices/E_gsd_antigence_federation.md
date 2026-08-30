# Appendix E — Mechanical Scientific Governance, Artificial-Immune Transfer, and Governed Component Federation

**Projection:** anonymous reviewer-facing technical appendix (functional labels)  
**Evidence role:** architecture / related implementation / transfer evidence  
**Not primary evidence for:** structured-context superiority, biological efficacy, universal security, or universal model determinism.

**Independent verification:** Cursor review branch `cursor/newinml-solo-appendix-federation-v4-20260829`; claims reverse-traced to repository bytes and hydradg eval receipts (2026-08-29).

## E.1 Purpose and boundary

The primary agent-context studies remain the frozen experiments described in the main paper. **EXP-008** and **EXP-009** both terminate as **UNDERPOWERED**; confirmatory treatment effects are not established. EXP-009 exploratory/directional secondary patterns are **not promoted**.

This appendix documents the broader implemented research program that supplied governance, custody, atomization, model execution, perturbation testing, and transfer implementations around those studies. **Protein Hinge / TEAM evidence is excluded** from primary admission (count = 0).

For double-blind review, identifying project/repository names are replaced by functional labels where required. An internal source map binds every statement to exact repositories, commits, files, and license states.

## E.2 Mechanical scientific governance

A machine-operable scientific-governance implementation (**Mechanical Scientific Method layer**) was built around versioned experiment specifications. Verified spec surface at pinned SHA `484e42c865c9af947d7bcc34bb86468a5d8f83c3` (repo HEAD has moved forward; spec content at pin unchanged):

- `run-experiment`, `ablation`, `audit-claims`, `audit-output`, `create-prompt`, `data-contract`, `fair-check`, `find-experiments`, `handoff`, `negative-results`, `export`, plus session/meta-prompt/model-identifiability specs.

The experiment runner distinguishes **CONFIRMATORY**, **EXPLORATORY**, and **REPLICATION** modes. Implemented gates:

| Gate | CONFIRMATORY | EXPLORATORY | REPLICATION |
|------|:---:|:---:|:---:|
| power_analysis | halt on fail | — | — |
| temporal_integrity / preregistration | halt on fail | — | — |
| red_team | halt on fail | — | — |
| data_contract | halt on fail | halt on fail | halt on fail |
| drift_check | halt on fail | halt on fail | halt on fail |

The negative-result registry explicitly distinguishes `NULL_RESULT`, `UNDERPOWERED`, and `TRUE_NEGATIVE`. Spec edge case EC_NEG_01 rejects classifying an underpowered non-rejection as `TRUE_NEGATIVE` when achieved power < 0.80. **Correction:** no automated Python gate enforces this; misclassification remains possible without agent/skill discipline.

This layer is methodological infrastructure. Its existence does not prove that a treatment works.

## E.3 Fractal custody as the shared interface

Across implementations, substantive evidence follows:

```text
source/evidence → transform or model/tool → derived evidence → claim → artifact
```

Cryptographic digests establish **byte identity only**, not truth. SHA-256 is not a digital signature. **SIGNATURE_STATE=SIGNED** only after an authorized signing operation. **MERKLE_MMR_STATE=COMMITTED** only after actual construction, ordering, root, and verification receipt. All NewInML 2026-08-29 closeouts record `NOT_SIGNED` / `NOT_COMMITTED`.

The federation is a **governed component federation**, not federated learning: specialized systems exchange typed evidence and bounded results while retaining implementation-specific claim ceilings. No federation-wide signature/root is established.

## E.4 Artificial-immune-system transfer implementation

A separate offline AIS implementation (**Immune-inspired guardrail system**) serves as a transfer case. Verified roles at pinned SHA `060dba881293c226ee26b78d93780ef1ed9b2ba4`: orchestrator, B-cell pattern memory, NK-cell negative selection, dendritic feature extraction, memory retrieval, validator/adversarial checking, regulatory calibration. Local API/MCP surfaces exist.

### Mixed empirical outcome (BENCHMARKS.md at pin; B1–B3 unchanged)

| Evaluation | Bounded observed result |
|---|---|
| 40 synthetic Python snippets (regex 20-dim features) | NK/NegSl-AIS: 0.675 accuracy, 1.000 precision, 0.350 recall; B-cell: 0.583 accuracy, 1.000 recall |
| 60 curated Python security patterns (60/40 split) | B-cell and fused guardrail: 0.750 accuracy, 1.000 precision, 0.500 recall, 0.000 FPR in reported split |
| Real C/C++ vulnerability benchmark (Devign subsample) | All tested detectors ~0.495–0.515 accuracy with high FPR (~0.66–0.78) |

The real-code result is a **feature-domain failure**, not a successful vulnerability detector. CodeBERT/VulBERTa integration for the main regex pipeline remains **proposed/future work** (scripts exist but are not the published B1–B3 benchmark path). Ollama embeddings are executed in separate lanes (e.g., SciFact benchmark added post-pin).

## E.5 ML components are complements, not promotion authorities

See `ML_COMPLEMENT_MATRIX.tsv`. Design principle: probabilistic components expand hypothesis/representation space; deterministic governance controls identity, experimental validity, scoring, and claim promotion.

## E.6 Cross-implementation evidence (bounded)

| Lane | What was exercised | Terminal interpretation |
|---|---|---|
| FCO/FCG mechanism experiments | divergence localization, model escalation/recompute, mzML admission (48/48 localization, 0 false admissions at pin) | bounded mechanism validation only |
| EXP-008 / EXP-009 | two 300-cell primary studies | **UNDERPOWERED**; treatment effect not established |
| Retrieval diagnostics | K=5 ablations | no established retrieval benefit in reported lane |
| Structural atomization | 25-source/312-atom bounded batch + 163/163 manuscript traceability | bounded positive readback; **whole-project V1A build INTERRUPTED/NONTERMINAL** |
| Observable systems validation | 4×25 perturbation (100/100), 8/8 tamper, concurrency, replay/restart, provider quota failures preserved | positive bounded systems checks; **does not alter EXP-008/009** |
| AIS transfer | synthetic/curated/Devign benchmarks | mixed; real-code ~chance |
| Scientific-application pilot | sentence atomization + ontology/KG pilots; classifier calibration | implemented pilots; classifier **FAIL** vs κ gate (best κ_u=0.472 < 0.7); human-rating gate open |
| Companion model artifact | Zenodo + gated HF companion | related transfer evidence only; NC-ND redistribution restricted |
| Qwen3.8 / SGLang / Cloudflare OS | successor probes | **BLOCKED or NONTERMINAL**; not primary evidence |

## E.7 Cross-domain implementation example (RELATED_IMPLEMENTATION)

One scientific-application repository (pinned `0efab4aa3859cebf53df8bcb4b90083a1a88beb4`) reports:

- **22,096** sentence atoms (EXP-002 receipt verified)
- Terminology pilot: **50** atoms, **100%** coverage, **1,792** annotations across **4** OBO ontologies (EXP-004)
- Semantic-KG pilot: **75** atoms, **89** logic-map edges, MESI checks recorded (EXP-005)
- Anti-feature lints: COMPLETE_PASS (EXP-006)
- Classifier calibration: **FAIL** at intermediate agreement; canonical human-rating gate still open (EXP-003)

**Caveat:** EXP-001 toolchain receipt references 1899 ch01 imprint, not the 1906 imprint claimed in README.

This is evidence the governance/atomization pattern was implemented outside the agent benchmark; it is **not** evidence of a positive agent treatment effect.

## E.8 Federation topology

```text
MECHANICAL SCIENTIFIC GOVERNANCE
  preregistration / contracts / negative-result states
                    │
                    ▼
FRACTAL CUSTODY OBJECTS + GRAPH
  identity / lineage / evidence class / claim ceiling
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
 STRUCTURAL      AIS /       GOVERNED
 ATOMIZATION     GUARDRAIL    MODEL EXECUTION
        │           │           │
        └───────────┼───────────┘
                    ▼
          AGENT/CONTEXT EXPERIMENTS
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
  OBSERVABILITY /        SCIENTIFIC
  PERTURBATION           APPLICATION PILOTS
                    │
                    ▼
        IMPLEMENTATION-SPECIFIC RESULTS
     positive / null / negative / blocked / partial
```

## E.9 Licensing and double-blind boundary

The reviewer package contains summaries, derived tables, and original explanatory diagrams—not private repository snapshots, gated model weights, or third-party datasets without verified redistribution rights. CC-BY-NC-ND companion artifacts (Vithia) are cite/reference only. See `LICENSE_REDISTRIBUTION_MATRIX.tsv`.

## E.10 Claim ceiling

This appendix supports only the bounded claim that a shared deterministic-governance and custody pattern has been implemented across multiple agent, provenance, anomaly-detection, model-execution, and scientific-application systems, with ML components used as bounded complements. Outcomes include positive, null, negative, partial, and blocked states.

It does **not** establish federation-wide accuracy improvement, universal AIS effectiveness, SeedGraph whole-project completion, or biological/clinical claims.
