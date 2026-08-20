# SeedGraph submission evidence review

**Repository:** `biobitworks/seedgraph`  
**Reviewed source:** `docs/GRAPH_SCHEMA.md`  
**Reviewed Git blob SHA:** `9c504d8fd4c8f74002763f535a176e76c7369c22`  
**Evidence state:** `REPO_RETRIEVED` from the retained NewInML repository evidence audit  
**Claim ceiling:** `REPO_REVIEWED_NOT_INDEPENDENTLY_REPRODUCED`

## Why SeedGraph is load-bearing

SeedGraph is not merely adjacent prior work. It is the existing implementation substrate
for the evidence-atom and provenance layer used by the present FCO/FCG submission work.

The reviewed schema supports:

- `EvidenceSeed` with canonical SHA-256 seed identity and raw-content SHA-256;
- `Sentence` as an atomized sentence / primary evidence unit;
- per-sentence SHA-256 `atom_id`;
- byte ranges plus document/section/seed ancestry and page information;
- `Claim` distinction between `deterministic` and `ai_enriched`;
- `Evidence` distinction between `direct`, `indirect`, and `review`;
- `ProvenanceRecord` fields for agent/tool, inputs, outputs, transformation type,
  timestamp, and parameters;
- `Packet` for manuscript/traceability aggregation;
- `CANDIDATE_SATISFIES` as hypothesis semantics;
- `SATISFIES` as a stronger confirmed edge requiring review;
- W3C PROV-aligned provenance fields;
- explicit schema uncertainties rather than silent implementation assumptions.

## Submission interpretation

The submission should not present sentence-level evidence atoms or provenance records
as if they originated in the new HydraDG work.

The contribution boundary is instead:

`SeedGraph evidence atoms + provenance`
→ `FCO/FCG custody/claim ceilings`
→ `Seed candidate/admission semantics`
→ `perturbation + first-divergence + recovery`
→ `HydraDG temporal-memory integration`.

## Seed-of-Truth boundary

The current companion specification proposes a `SeedOfTruth` as a bounded claim
admitted under declared gates, not metaphysical truth.

That proposed extension includes:
- claim ceiling;
- evidence/recomputation/replication/empirical state;
- uncertainty;
- counterevidence / contradiction role;
- independence groups;
- versioned admission state;
- perturbation and recovery objects.

`SeedOfTruth` remains `CONCEPTUAL_SCHEMA_WITH_EXISTING_IMPLEMENTATION_LINEAGE`
until an end-to-end implementation actually exists.

## Internal vs anonymous review graph

Maintain two graph surfaces:

1. **Internal custody graph**
   - repository names;
   - Git blob SHAs;
   - local paths;
   - retained-run identity;
   - author-facing lineage.

2. **Anonymous review graph**
   - anonymous source IDs;
   - no author identity/local path/public project URL;
   - preserved evidence class;
   - preserved claim state and claim ceiling;
   - preserved claim-to-manuscript relationship.

An anonymous graph must be generated deterministically from the internal graph by an
explicit redaction transform. Do not manually maintain two unrelated graphs.

## Bridge schema

Use `seedgraph/bridge_schema.json` as the portable deterministic interchange layer.

It is intentionally narrower than the full SeedGraph database schema and must not be
described as reproducing all of SeedGraph/Neo4j.

Bridge object classes:
- source;
- context_envelope;
- context_atom;
- proposition;
- claim;
- seed;
- manuscript_link;
- edit_event.

## Agent/model integration

The HydraDG extension adds first-class:
- Agent;
- Model;
- AgentSession;
- Turn;
- ModelInvocation;
- ToolAction;
- KnowledgeUpdate;
- AdmissionDecision.

These should map into SeedGraph primarily through:
- `ProvenanceRecord`;
- evidence/source atoms;
- claims;
- edit/admission events;
rather than replacing SeedGraph's existing evidence ontology.

## Current review limitation

This review is grounded in the retained repository evidence audit and companion
specification. The connected GitHub code-search endpoint returned an upstream error
during the current refresh attempt, so the exact current `main` contents have not been
re-fetched file-by-file in this execution.

Do not silently upgrade this to a fresh current-main audit until that succeeds.
