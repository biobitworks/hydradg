# Release Watch execution note — Context Iceberg — 2026-08-19

## Governing inputs

This branch executes the release/public/read-only portion of the supplied Release Watch parallel-safe prompt and the supplied Context Iceberg Score v1 specification.

Recorded upstream handoff identities from the supplied custody package:

```text
RELEASE_WATCH_PARALLEL_SAFE_WORK_PROMPT.md
SHA-256=89a5200d94effc64138d386e983729ba3e2f4672bd53f14494765ec954be9137

CONTEXT_ICEBERG_SCORE_SPEC.md
SHA-256=dd581b77d7e9ae20d10d169ddfb83ec371fb2ecb1c0b312266614d7d6845d49c
```

These are upstream-attested handoff identities. Repository copies must be independently rehashed before claiming byte identity to the supplied handoff files.

## Why a separate branch

Branch:

`hack-hydra/context-iceberg-20260819`

The Release Watch contract prohibits mutation of the active Daisy scientific lane. This branch therefore changes only display/read-only/release artifacts:

- Context Iceberg data/display contract;
- read-only `/api/math/current` adapter;
- navigable context-cloud 4D graph;
- website knowledge FCO projection;
- terminology coverage;
- documentation/public-export surfaces.

It does NOT:

- choose or change G* weights;
- rerun RAW/SeedGraph experiment cells;
- mutate active HydraDB experiment namespaces;
- change SeedGraph parser/atomization semantics;
- change retrieval/ranking algorithms;
- promote scientific claims.

## Visualization mapping

For any scope with an admitted Context Iceberg metric:

```text
signed ΔG* direction -> cloud/node color
CloudDrift 0..100    -> halo/cloud width
normalized burden    -> node/body size
FCG time/state       -> time slider visibility
```

Direction colors are neutral diagnostic categories:

- LOWER: cool blue;
- STABLE/PENDING: neutral gray;
- HIGHER: amber.

No direction color encodes accuracy improvement.

When a canonical CloudDrift/JSD receipt is absent, the graph may demonstrate the visual grammar using the deterministic fixture mutation-distance control, but the halo is dashed and explicitly labelled `DEMO_CONTROL`, not `CloudDrift`.

## Metric inheritance rule

The UI may receive metrics at any FCG granularity:

- atom;
- FCO/object;
- state;
- subtree;
- project.

Each displayed metric must state one of:

- `OBJECT_SPECIFIC`;
- `STATE_INHERITED`;
- `DEMO_CONTROL`;
- `PENDING`.

A state-level metric must never be silently presented as an atom-specific measurement.

## Custody boundary

The live score API reads a configured canonical receipt through `HYDRADG_CONTEXT_ICEBERG_JSON` and hashes the exact bytes it reads. The local path is not disclosed to the browser.

Without that receipt the API returns:

```text
GIBBS_CONFIG=PENDING
CloudDrift=PENDING
canonical_binding_state=PENDING_CANONICAL_FCO_FCG_BINDING
```

This is an intentional fail-closed state.

## Knowledge graph boundary

Website terminology is materialized as deterministic application-level `WebsiteKnowledgeTerm` FCOs and exposed by `/api/knowledge`.

Current state:

```text
website knowledge FCO projection = IMPLEMENTED
HydraDB KB projection             = PENDING_STABLE_RELEASE_HANDOFF
canonical scientific FCG binding  = NOT IMPLIED BY WEBSITE OBJECT
```

A later isolated projection may write these website KB objects into HydraDB after the active Daisy lane reaches a stable handoff. Until then the website projection is not represented as HydraDB-backed truth.

## Claim ceiling

`RELEASE_WATCH_CONTEXT_ICEBERG_DISPLAY_AND_NAVIGATION_IMPLEMENTATION_ONLY`

No signing or live Merkle commitment is established by this branch.
