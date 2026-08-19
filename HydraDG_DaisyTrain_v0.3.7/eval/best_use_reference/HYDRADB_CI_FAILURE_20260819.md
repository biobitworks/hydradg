# Best Use v1 — live HydraDB CI failure record

Status: `FAILED_EXECUTION / LOAD_BEARING_DEPENDENCY_IDENTIFIED`

GitHub Actions run: `32206301823`  
Job: `95930141136`  
HydraDB pin: `6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219`

## What passed

- Ubuntu native prerequisites installed.
- Pinned HydraDB source checked out exactly.
- `cargo build --locked --features server-runtime --bin graph-node` passed.
- Local HydraDB `graph-node` started and `/healthz` passed.
- Official cleaned LongMemEval-S downloaded.
- Source SHA-256 matched `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`.
- Deterministic smoke80 construction passed with N=80.

## Failure

The first A/B/C/D ingest failed before retrieval statistics:

```text
HydraDB HTTP 400: GraphQuery query is not supported yet:
conflicting metadata values for vertex 937791703422015706 property position
```

The v1 Session ID was:

`stable_id("session", question_id, external_session_id)`

LongMemEval can contain the same external session ID at more than one occurrence position inside a case. The graph therefore attempted to assign different `position` values to one vertex. HydraDB rejected the conflicting metadata rather than silently overwriting it.

## Earliest divergent dependency

`external session identifier -> graph vertex identity`

—not the HydraDB build, server health, source dataset, or statistical analyzer.

## v2 correction

The v2 typed-memory graph uses:

`stable_id("session_occurrence", question_id, external_session_id, occurrence_position)`

The external session ID remains a property for benchmark scoring. The occurrence vertex is the graph identity.

The new `best_use_structural_suite.py` includes duplicate external session IDs as a regression fixture and must pass against live HydraDB before LongMemEval promotion.

## Claim ceiling

This object establishes a **real failed execution and localized software identity defect**. It does not establish HydraDB retrieval performance.

- Evidence: `GITHUB_ACTIONS_EXECUTION_LOG`
- Signature: `NOT_SIGNED`
- Merkle/MMR: `NOT_MERKLE_COMMITTED`
