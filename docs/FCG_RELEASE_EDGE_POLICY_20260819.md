# FCG release edge policy — 2026-08-19

The release graph should preserve the distinction between scientific evidence and presentation artifacts.

Conceptual relationships:

```text
SourceDataset
  ─DERIVED_THROUGH→ Atomization
  ─SUPPORTS→ ExperimentEvidence

ExperimentEvidence
  ─BOUNDS→ Claim

Claim
  ─PRESENTED_BY→ WebsiteSection
  ─PRESENTED_BY→ StaticFallback
  ─PRESENTED_BY→ Video
```

The exact predicate names must be mapped to the canonical FCG schema before persistence. This document is conceptual and must not be used to invent incompatible canonical predicates.

A presentation artifact may depend on an evidence object; it does not become the evidence object.

The live Vercel deployment and static fallback are sibling artifact nodes with different delivery properties, not competing scientific results.
