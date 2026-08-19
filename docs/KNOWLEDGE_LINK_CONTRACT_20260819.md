# HydraDG knowledge-link contract — 2026-08-19

## Rule

A project-specific term, entity, hash, relation, metric or named internal object that appears in the judge-facing website should be navigable to a knowledge object unless explicitly exempted as ordinary language.

The declared project-term registry is:

```text
apps/hydradg-web/lib/projectTerms.ts
```

The knowledge records live in:

```text
apps/hydradg-web/lib/knowledgeLinks.ts
```

The release check is:

```text
scripts/check_term_knowledge_coverage.py
```

## Required knowledge object fields

Each record should provide enough information to connect the surface term to the custody graph:

```text
term
slug
short definition
how-to / operational meaning
graph query or relationship selector
upstream source when one exists
claim boundary when the term could be mistaken for a stronger claim
```

## Resolution route

```text
website term
  ↓
/knowledge#slug
  ↓
graph query / FCO object
  ↓
FCG neighbors
  ↓
source / receipt / version
  ↓
claim ceiling
```

The website knowledge object is an explanation and navigation layer. It does not supersede the canonical source/receipt.

## Hashes

A displayed SHA-256 digest should link to an FCO/object inspector or evidence object where possible. The digest itself is not a knowledge explanation and does not establish correctness.

## Dataset/entity examples

Dataset names such as LongMemEval, EnterpriseRAG-Bench, HERB and BEAM are entities with source repository/version/rights state. They should resolve through the knowledge layer to those source records rather than appearing as unexplained labels.

## ΔG* boundary

`ΔG*` is a HydraDG application-defined information-state metric. The knowledge entry must state that the notation is an analogy to free-energy language and is not physical Gibbs free energy unless a separate physical derivation and units are established.

## Coverage claim

The static coverage checker proves only that every slug in the declared project-term registry has a corresponding knowledge record. It does not prove that every unfamiliar word on the website has been discovered or that the knowledge content is correct.
