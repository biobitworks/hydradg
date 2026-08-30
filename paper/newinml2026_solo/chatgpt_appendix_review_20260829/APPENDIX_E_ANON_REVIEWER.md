# Appendix E — Mechanical Scientific Governance, Artificial-Immune Transfer, and Governed Component Federation

**Projection:** anonymous reviewer-facing technical appendix  
**Evidence role:** architecture / related implementation / transfer evidence  
**Not primary evidence for:** structured-context superiority, biological efficacy, universal security, or universal model determinism.

## E.1 Purpose and boundary

The primary agent-context studies remain the frozen experiments described in the main paper; both terminate as **UNDERPOWERED** and do not establish a treatment effect. This appendix documents the broader implemented research program that supplied governance, custody, atomization, model execution, perturbation testing, and transfer implementations around those studies.

For double-blind review, identifying project/repository names are replaced by functional labels. An internal source map binds every statement to exact repositories, commits, files, and license states.

## E.2 Mechanical scientific governance

A machine-operable scientific-governance implementation was built around versioned experiment specifications. Its implemented spec surface includes experiment execution, ablation, claim/output audit, data contracts, FAIR checks, experiment discovery, handoff, negative-result registration, prompt creation, and export.

The experiment runner distinguishes **CONFIRMATORY**, **EXPLORATORY**, and **REPLICATION** modes. Implemented gates include power analysis, temporal-integrity/preregistration checks intended to prevent post-hoc promotion, red-team review, data-contract validation, and drift checks. The negative-result registry explicitly distinguishes `NULL_RESULT`, `UNDERPOWERED`, and `TRUE_NEGATIVE`; an underpowered non-rejection is not permitted to become a true negative.

```text
hypothesis / requirement
        ↓
preregistration + power / MESI
        ↓
data + interface contracts
        ↓
deterministic execution gates
        ↓
probabilistic model/tool calls where needed
        ↓
deterministic scoring / verification
        ↓
positive | null | negative | underpowered | failed | blocked
        ↓
claim ceiling + custody append
```

This layer is methodological infrastructure. Its existence does not itself prove that a treatment works.

## E.3 Fractal custody as the shared interface

Across the implementations, substantive evidence follows a common bounded path:

```text
source/evidence
→ deterministic transform or probabilistic model/tool
→ derived evidence
→ claim
→ artifact
```

Cryptographic digests establish byte identity, not truth. Model/tool outputs remain probabilistic evidence until deterministic verification or an independently admitted result justifies promotion. A hash is not a digital signature, and no state is called Merkle/MMR committed without an actual construction and verification receipt.

The federation described here is therefore a **governed component federation**, not federated learning: specialized systems exchange typed evidence, references, and bounded results while retaining implementation-specific claim ceilings.

## E.4 Artificial-immune-system transfer implementation

A separate offline artificial-immune-system (AIS) implementation was built as a transfer case for deterministic guardrails around probabilistic models. Implemented computational roles include an orchestrator, B-cell-like pattern memory, NK-cell-like negative selection, dendritic-like feature/context extraction, memory retrieval, validator/adversarial checking, and regulatory calibration. The system also exposes local API/MCP surfaces, supports offline/domain-pack operation, continuous training data, and an LLM-assisted prompt-injection lane.

### Mixed empirical outcome

| Evaluation | Bounded observed result |
|---|---|
| 40 synthetic Python snippets | negative-selection detector: 0.675 accuracy, 1.000 precision, 0.350 recall; B-cell detector: 0.583 accuracy, 1.000 recall |
| 60 curated Python security patterns | B-cell and fused guardrail: 0.750 accuracy, 1.000 precision, 0.500 recall, 0 observed FPR in the reported split |
| real C/C++ vulnerability benchmark | tested detectors remained approximately chance accuracy (~0.495–0.515) with high false-positive rates |

The real-code result identifies a feature-domain failure rather than a successful vulnerability detector. The implementation's own follow-up plan calls for semantic embedding features and language-specific extractors. This motivates the ML-complement architecture: deterministic/AIS rules provide stable structure and explicit failure modes, while learned representations can supply semantic features absent from the rule features.

## E.5 ML components are complements, not promotion authorities

| Component class | Deterministic/governed core | ML complement | Promotion boundary |
|---|---|---|---|
| Scientific governance | preregistration, power, temporal integrity, data contracts, negative-result registry | hypothesis generation, code review, interpretation | formal gates + scientific/human review |
| Custody graph | canonical identity, source links, edge contracts, claim ceilings | proposed relations/claims or semantic enrichment | schema/source verification |
| Structural atomization | source hashing, structural parsing, atom/source pointers | semantic enrichment/entity resolution | structural readback + provenance gate |
| AIS/guardrail | explicit detector roles, pattern/negative-selection logic, calibration | embeddings or LLM-derived semantic features | held-out benchmark + detector contract |
| Governed model executor | pinned model/config, request/output receipts, recovery gates | local/open model inference | deterministic parser/verifier/scorer |
| Agent/context experiment | frozen cases, conditions, scorers, paired statistics | model responses | preregistered analysis + claim ceiling |
| Observability/perturbation | event chain, replay, tamper/concurrency checks | optional diagnosis/summary | deterministic systems checks |
| Scientific application pilots | source atomization, ontology bindings, explicit experiment states | classifier/KG enrichment | held-out/human-canonical or task-specific gate |

The design principle is: **probabilistic components expand the hypothesis/representation space; deterministic governance controls identity, experimental validity, scoring, and claim promotion.**

## E.6 Cross-implementation evidence

| Lane | What was actually exercised | Terminal interpretation |
|---|---|---|
| custody-mechanism experiments | divergence localization, model escalation/recompute, controlled provenance-vs-variance cases, real scientific-file admission | bounded mechanism validation only |
| agent/context experiments | two 300-cell primary studies | UNDERPOWERED; treatment effect not established |
| retrieval diagnostics | full benchmark retrieval ablations | structured route did not establish a retrieval benefit in the reported K=5 lane |
| structural atomization | bounded real-source batches and traceability checks | bounded positive traceability/readback; whole-project large build partial/non-terminal |
| observable systems validation | perturbation, synthetic tamper, concurrency, replay/restart, provider failure | positive bounded systems checks plus preserved failures |
| AIS transfer | synthetic/curated and real-code benchmarks | mixed; real-code semantic-vulnerability lane approximately chance |
| scientific-application pilot | full historical-corpus sentence atomization plus ontology/KG pilots; classifier calibration | implemented pilots; classifier progression gated on canonical human rating |
| companion model artifact | custody-bound gated model/research artifact | related transfer evidence only; no superiority claim here |

## E.7 Cross-domain implementation example

One scientific-application repository reports full sentence-level atomization of a historical source corpus (**22,096 sentence atoms**), a terminology-to-ontology pilot (**50 atoms, 1,792 annotations across four OBO ontologies**), and a semantic-KG pilot (**75 atoms, 7/7 MESI checks, 89 logic-map edges**). Its classifier calibration is procedurally closed at an intermediate agreement level and remains gated on canonical human rating before downstream full triage. This is evidence that the governance/atomization pattern was implemented outside the agent benchmark; it is not evidence that the agent treatment effect is positive.

A separate gated companion model artifact is likewise treated as related transfer evidence, not as a primary result. Historical hard-coded or synthetic model rows are development lineage and are excluded from empirical claims.

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

The linkage is an implementation pattern, not a claim that one global graph root, project signature, or federation-wide Merkle/MMR commitment already exists.

## E.9 Licensing and double-blind boundary

The reviewer package should contain summaries, derived tables, and original explanatory diagrams—not snapshots of private repositories, gated model weights, or third-party datasets whose redistribution rights are not independently verified. Software, research artifacts, manuscripts, model artifacts, and upstream datasets retain their own license terms.

The internal source map preserves repository names, SHAs, paths, and licenses. Those identifiers enter the anonymous submission only if the final self-citation/anonymity audit passes.

## E.10 Claim ceiling

This appendix supports only the bounded claim that a shared deterministic-governance and custody pattern has been implemented across multiple agent, provenance, anomaly-detection, model-execution, and scientific-application systems, with ML components used as bounded complements to deterministic identity, scoring, and claim-promotion gates. Outcomes include positive, null, negative, partial, and blocked states.

It does **not** establish that the federation improves model accuracy, that FCO/FCG is universally superior to prior provenance systems, that the AIS detector is generally effective, or that biological/clinical claims follow from these pilots.
