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

This definition was directly supplied by Byron P. Lee in the project conversation on 2026-08-18.

## Historical provenance boundary

Byron states that TRAITS originated earlier in the ImmunOS project, before the current FCO/FCG hashing and custody workflow.

Therefore:

1. The current six-term definition above is accepted as direct human-supplied project evidence.
2. It is **not** currently claimed to be cryptographically proven as the earliest historical wording.
3. The private `biobitworks/immunos` repository may be used for chronology/source recovery, but it is not an admissible public source atom for the HydraDG publication path while it remains private.
4. Historical-origin claims require a matching public preprint or public GitHub artifact before promotion under the MVP admission policy.
5. The earlier AI-generated expansion `Truth-Preserving, Resilient, Adversarially Aware, Immune-Inspired, Traceable, Sovereign` is superseded and must not be represented as the original TRAITS definition.

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
- license/rights evidence;
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
