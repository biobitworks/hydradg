# TRAITS canonical definition and provenance boundary

Status: CURRENT_IMPLEMENTATION_DEFINITION

## Canonical current definition

For HydraDG/Antigence implementation work, TRAITS is:

- **Traceable**
- **Rigorous**
- **Accurate**
- **Interpretable**
- **Transparent**
- **Secure**

## Earliest recovered repository evidence

The earliest repository evidence currently recovered and directly verified is:

- Repository: `biobitworks/antigence`
- Commit: `7d0c2e929d4bd8fc0bf6620d60f9245ae8cd083d`
- Commit message: `Accelerate AIS with PyTorch backend and parallelize B-Cell recognition`
- Commit date context: January 2026
- Evidence in diff: the Antigence README was changed to state that the platform enforces **TRAITS (Traceable, Rigorous, Accurate, Interpretable, Transparent, Secure)**.
- Commit also records Antigence security-review and model/agent metadata, including Claude Sonnet 4.5 attribution for the development session.

This is stronger historical evidence than the later 2026-08-18 conversation correction because it is repository-versioned and predates the current HydraDG work.

## Public-source claim ceiling

`biobitworks/antigence` is currently private. Therefore:

1. The commit above is accepted as an **internal historical provenance anchor**.
2. It is **not yet an admissible public-source atom** for the HydraDG publication path under the current rule requiring a public preprint or public GitHub source.
3. If the exact commit becomes publicly accessible, or the same historical definition is published in a public preprint/public GitHub artifact with compatible rights metadata, the source registry may promote it after visibility and license verification.
4. We do not claim that this commit is cryptographically proven to be the first-ever human formulation of TRAITS; it is the earliest repository evidence recovered so far.
5. The earlier AI-generated expansion `Truth-Preserving, Resilient, Adversarially Aware, Immune-Inspired, Traceable, Sovereign` is superseded and must not be represented as the historical TRAITS definition.

## Crosswalk hypothesis to test

| TRAITS | Existing overlap | What HydraDG/Antigence adds or tests |
|---|---|---|
| **Traceable** | FAIR provenance/identifiers, SOC 2 evidence, NIST governance/documentation | FCO identity for sources, prompts, tools, models, transformations, claims, figures; FCG dependency edges; first-divergence localization |
| **Rigorous** | NIST AI RMF risk/TEVV, SOC control effectiveness | hypotheses, falsifiers, negative results, deterministic-vs-probabilistic typing, claim ceilings, replay |
| **Accurate** | SOC 2 Processing Integrity, NIST valid/reliable AI | evidence-supported claim checking; separates authentic provenance from actual correctness |
| **Interpretable** | NIST explainability/interpretability, ISO 42001 transparency | explanation tied to actual graph dependencies, admission decisions, and impact sets |
| **Transparent** | FAIR provenance, SOC system description, AI RMF accountability/transparency | human/model/agent authorship, exact model/version, prompt/tool provenance, contribution boundaries |
| **Secure** | SOC 2 Security, NIST CSF 2.0, ISO 27001, OWASP GenAI | private/local-first execution, fail-closed writes, context-root admission, secret gates, model/runtime/vendor independence |

The overlap column is a hypothesis registry, not a compliance assertion. Every mapping must be pinned to the exact public framework source/version and its usable license or rights basis before becoming an admitted mapping atom.

## FCO/FCG requirements for every TRAITS mapping atom

Each crosswalk atom must record at minimum:

- exact TRAITS term;
- external framework/control identifier;
- public source URL;
- source version/date;
- upstream license/rights evidence;
- project-output license state;
- source locator;
- atom text or normalized mapping statement;
- human author/source authorship;
- extracting or transforming agent;
- model/provider/version when known;
- prompt/tool transformation receipt;
- deterministic or probabilistic transformation type;
- SHA-256 object identity when bytes are available;
- evidence class;
- claim ceiling;
- Anticube classification receipt when the public Anticube contract is pinned;
- predecessor/successor edges if the mapping changes over time.

## Review rule

TRAITS is used as an implementation and experimental profile. HydraDG must not claim that TRAITS supplies SOC 2 compliance, FAIR compliance, NIST compliance, ISO certification, or equivalent assurance merely because a crosswalk exists.

The experiment must instead test where existing controls directly overlap, where HydraDG supplies additional implementation evidence, where the comparison is only partial, and where a claimed gap is not supported.
