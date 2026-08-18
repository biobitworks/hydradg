# EXP-011 — TRAITS Crosswalk for Antigence

Status: PLANNED / SOURCE_RECOVERED_INTERNAL / PUBLICATION_SOURCE_PENDING

## Canonical recovered expansion

`TRAITS = Truth-Preserving, Resilient, Adversarially Aware, Immune-Inspired, Traceable, Sovereign`

### Source status

- Earliest currently recovered source: Byron P. Lee conversation, 2026-07-17.
- Evidence class: DIRECT HUMAN-AUTHORED PROJECT DEFINITION recovered from prior conversation.
- Public preprint/public GitHub source containing this exact expansion: NOT YET LOCATED.
- Therefore this experiment must not claim that the acronym was previously published.
- For a future public release, the acronym should be attributed to Byron P. Lee as an original Antigence framework contribution, with the public release commit/DOI becoming the public citation anchor.

## Goal

Evaluate TRAITS as an implementation-oriented AI security/safety profile that crosswalks existing standards and frameworks while preserving a distinct design objective:

> local-first, private-first, model-agnostic, software-agnostic, hardware-agnostic enforcement with content-addressed provenance and fail-closed admission.

TRAITS is not proposed as a substitute for SOC 2, FAIR, NIST, ISO, OWASP, MITRE, or CSA. It is a technical profile/layer that can generate implementation evidence and expose gaps those frameworks do not themselves prescribe how to close.

## TRAITS dimensions

### T — Truth-Preserving

Objective:
- preserve source/evidence identity and distinguish source evidence from transformations, model outputs, inferences, and claims;
- prevent downstream claims from exceeding evidence ceilings;
- reject unsupported or provenance-broken dependent claims.

Candidate implementation evidence:
- FCO content hashes;
- FCG evidence paths;
- source/version/license links;
- model/agent transformation receipts;
- claim-ceiling propagation;
- contradiction/supersession history;
- deterministic replay where applicable.

### R — Resilient

Objective:
- maintain bounded operation under failure, drift, tampering, missing dependencies, and infrastructure changes;
- support recovery without silently erasing the failure history.

Candidate implementation evidence:
- fail-closed admission;
- append-only state versions;
- recovery receipts;
- first-divergence detection;
- affected-set analysis;
- offline/local execution path;
- provider/backend substitution tests;
- backup/export/replay of graph state.

### A — Adversarially Aware

Objective:
- treat malicious, poisoned, manipulated, or instruction-bearing inputs as expected system conditions rather than exceptional cases.

Candidate implementation evidence:
- Anticube classification;
- prompt/data injection tests;
- memory poisoning tests;
- source/license spoofing tests;
- model/tool identity substitution tests;
- supply-chain provenance checks;
- red-team fixtures mapped to OWASP Agentic Top 10 and MITRE ATLAS.

### I — Immune-Inspired

Objective:
- apply artificial-immune-system concepts such as self/non-self discrimination, negative selection, anomaly recognition, quarantine, challenge, memory, recovery, and controlled re-admission.

Candidate implementation evidence:
- self/non-self × safe/unsafe matrix;
- Anticube classification states;
- `ADMITTED_AS`, `REJECTED_AS`, `CHALLENGED_AS` edges;
- quarantine queue;
- reclassification over time;
- immune-memory/drift history;
- recovery after known perturbations.

Claim boundary:
- biological analogy is an architectural inspiration unless a specific computational mechanism is empirically evaluated.

### T — Traceable

Objective:
- every material source, transformation, model/agent invocation, tool action, classification, and final claim has explicit lineage.

Candidate implementation evidence:
- FCO/FCG graph;
- SHA-256 identifiers;
- source/version/license registry;
- model/provider/version receipts;
- human-vs-AI contribution boundaries;
- reproducible lab notes and notebooks;
- real signatures/MMR only when executed.

### S — Sovereign

Objective:
- permit local/private operation without requiring a specific model vendor, cloud, operating system, accelerator, or database product.

Candidate implementation evidence:
- local-only data path;
- bring-your-own-model/provider adapter;
- CPU/GPU/NPU-agnostic interfaces;
- hardware-independent canonical object formats;
- software-independent JSON/JSONL/FCO export;
- no mandatory third-party telemetry;
- secret isolation;
- offline verification;
- optional remote providers rather than mandatory remote dependency.

Sovereign does not mean isolated from standards or incapable of cloud use. It means custody and policy remain operable when cloud/provider dependencies are removed.

## Current framework crosswalk targets

Pin exact versions/current public sources before executing the formal crosswalk.

1. AICPA SOC 2 Trust Services Criteria — Security, Availability, Processing Integrity, Confidentiality, Privacy; current public AICPA resource remains 2017 TSC with revised points of focus (2022).
2. Open FAIR — O-RA 2.0.1 + O-RT 3.0.1; quantitative information/cyber risk analysis.
3. FAIR Cyber Risk Management Program (FAIR-CRMP) v1.0 — released 2025.
4. NIST Cybersecurity Framework 2.0 — Govern, Identify, Protect, Detect, Respond, Recover.
5. NIST AI RMF 1.0 + NIST AI 600-1 Generative AI Profile; note AI RMF 1.0 is under revision in 2026.
6. ISO/IEC 42001:2023 — AI management system.
7. OWASP Top 10 for Agentic Applications 2026.
8. MITRE ATLAS — adversarial threat landscape for AI systems.
9. CSA AI Controls Matrix (AICM) v1.1 — released 2026-06-22, 247 controls across 18 domains.
10. Optional: CSA AI Security Maturity Model (AISMM), AI-CAIQ, NIST SSDF GenAI profile, and AIUC-1 crosswalks.

## Working gap hypothesis

This experiment will test, not assume, the following gap pattern:

- SOC 2 is an assurance/control-criteria framework, not an AI-native runtime provenance or local execution architecture.
- FAIR quantifies risk but does not itself provide the technical runtime controls or custody substrate that generate the measurements.
- NIST CSF/AI RMF describe outcomes and risk-management functions but deliberately do not prescribe one implementation architecture.
- ISO/IEC 42001 is an AI management-system standard and emphasizes governance/risk processes rather than a mandatory content-addressed runtime evidence graph.
- OWASP Agentic Top 10 and MITRE ATLAS characterize threats/attack techniques, but threat taxonomies do not themselves provide complete provenance, admission, recovery, or sovereignty mechanisms.
- CSA AICM is substantially more implementation-oriented and should be treated as the strongest control-framework comparison; the experiment should identify complementary controls rather than overstate gaps.

These are hypotheses for the crosswalk and must be verified control-by-control before publication.

## Proposed TRAITS contribution

The potential contribution to test is a portable evidence/enforcement layer:

```text
source/data/model/tool
  -> content-addressed FCO
  -> explicit FCG dependencies
  -> Anticube admission/classification
  -> local policy enforcement/quarantine
  -> drift + first-divergence + recovery
  -> auditable control evidence
  -> optional mapping into SOC 2 / FAIR / NIST / ISO / OWASP / MITRE / CSA
```

This would make TRAITS a **control-evidence generator and runtime profile**, not a certification or compliance claim.

## Experiment tasks

- [ ] Create exact public-source registry entries for every framework/version.
- [ ] Extract framework requirements/categories into licensed/citable atoms where redistribution permits; otherwise store citations and derived mappings without reproducing restricted text.
- [ ] Assign each TRAITS implementation control to one or more framework outcomes/risks/controls.
- [ ] Mark mapping strength: `DIRECT`, `PARTIAL`, `COMPLEMENTARY`, `NO_MAPPING`, `NOT_ASSESSED`.
- [ ] Record evidence for every mapping and reviewer/model that derived it.
- [ ] Identify gaps from both directions: framework -> TRAITS and TRAITS -> framework.
- [ ] Build FAIR scenarios for material TRAITS failure modes to quantify loss exposure where sufficient calibrated inputs exist.
- [ ] Build SOC 2 evidence examples showing how FCO/FCG receipts could support, but never substitute for, an auditor's examination.
- [ ] Map red-team fixtures to OWASP Agentic Top 10 and MITRE ATLAS techniques.
- [ ] Map local/private-first controls against CSA AICM architectural roles and controls.
- [ ] Build a notebook and machine-readable crosswalk.
- [ ] Red-team the claim that TRAITS is hardware/software agnostic by running the same canonical evidence objects across at least two distinct execution stacks.

## Claim ceilings

Allowed after source recovery only:
- `TRAITS` expansion was recovered from Byron P. Lee's July 17, 2026 Antigence discussion.

Not yet allowed:
- `TRAITS` was previously publicly published.
- `TRAITS` fills all gaps in SOC 2, FAIR, NIST, ISO, OWASP, MITRE, or CSA.
- `TRAITS` provides SOC 2 compliance/certification.
- `TRAITS` is FAIR-conformant without a completed FAIR analysis.
- `TRAITS` is hardware/software agnostic without cross-stack execution evidence.
- `TRAITS` is secure/safe merely because custody/provenance exists.
