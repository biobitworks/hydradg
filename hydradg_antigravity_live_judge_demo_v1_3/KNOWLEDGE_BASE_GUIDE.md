# HydraDG Knowledge Base Guide v1

## Purpose

The Knowledge Base is the human-readable and machine-addressable explanation layer for HydraDG.

It should let a judge move from an unfamiliar project term or FCO to:

term
→ definition
→ FCO identity
→ FCG neighbors
→ source/version
→ evidence class
→ claim ceiling
→ current/superseded state
→ optional HydraDB readback receipt

The Knowledge Base is not a marketing glossary. It is a governed explanation surface.

## Required live route

`/knowledge`

## Required persistent entry point

Every page navigation should expose:

`Knowledge`

## Required KB categories

### Core architecture
- Fractal Custody Object (FCO)
- Fractal Custody Graph (FCG)
- SeedGraph
- HydraDB
- Context Iceberg
- Context Cloud
- Cloud Drift
- Structural Cloud Drift
- Retrieval Cloud Drift
- ΔG*
- claim ceiling
- evidence class
- source root
- projection root
- receipt
- signature state
- Merkle/MMR state

### Experiment terminology
- reference
- poison
- antidote
- perturbation
- restoration
- contradiction
- supersession
- abstention
- null result
- negative result
- deterministic replicate
- held-out run
- canary
- golden path

### Retrieval metrics
- Hit@K
- Recall@K
- ΔHit@K
- ΔRecall@K
- evidence-path coverage
- rank displacement

### Track terminology
- Track 01 — Enterprise Context + Ontology
- Track 02 — Repos, Dependencies + Code as Graphs
- Track 03 — Memory + Context Retrieval

## Required term entry contract

Every KB term should expose:

- `term`
- `slug`
- `short_definition`
- `long_definition`
- `why_it_matters`
- `claim_boundary`
- `related_terms`
- `related_fco_ids`
- `source_refs`
- `evidence_class`
- `claim_ceiling`
- `current_state`
- `hydradb_traceability_state` if applicable

## Judge interaction

From any highlighted term, the judge should be able to click:

`Open in Knowledge Base`

Then optionally:

`Open Related FCO`
`Trace Source`
`Back to Demo`

No manual URL entry.

## FCO/FCG relationship

The KB should itself be represented as bounded application FCOs.

Preferred conceptual flow:

KnowledgeTermFCO
→ DEFINED_BY
→ KnowledgeDefinitionFCO
→ RELATES_TO
→ ProjectFCO / ExperimentFCO / ResultFCO

The live website may materialize these as read-only application FCOs.

If projected into HydraDB, use an isolated application namespace and create a readback receipt.
Do not claim scientific verification from the KB projection.

## Claim ceiling

`APPLICATION_KNOWLEDGE_BASE_AND_TRACEABILITY_ONLY`
