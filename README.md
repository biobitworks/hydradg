# HydraDG — Graph-Native Governed Context Engine

HydraDG is a governed memory and context engine built **only on HydraDB** for **Hack Hydra 2026 — Track 03: Memory + Context Retrieval**. It preserves evolving state, provenance, contradictions, supersession, recovery, null results, and claim boundaries as an inspectable graph instead of silently overwriting context.

**Demo video:** https://youtu.be/7EDb6q-loPA  
**Submission track:** Track 03 — Memory + Context Retrieval  
**Graph backend:** HydraDB only

---

## Judge: start here

If you have three minutes:

1. Watch the demo video above.
2. Read [`SUBMISSION.md`](SUBMISSION.md) for the bounded submission claim.
3. Use [`HOW_TO.md`](HOW_TO.md) or [`docs/JUDGE_REPRODUCE_FROM_SCRATCH.md`](docs/JUDGE_REPRODUCE_FROM_SCRATCH.md) to rebuild the HydraDB graph and website on a clean machine.
4. Inspect the canonical public FCG snapshot in [`custody/graph/live/`](custody/graph/live/).
5. Inspect [`docs/COMPONENT_MAP.md`](docs/COMPONENT_MAP.md) for component purpose, inputs, outputs, and claim boundaries.

There is **no Neo4j fallback** in the judge application. The executable graph path is:

```text
HydraDG application -> HydraDB HTTP graph API -> isolated HydraDB namespace
```

---

## The problem

Long-lived AI memory systems can flatten or overwrite changing context. Once facts are updated or contradicted, it becomes difficult to determine:

- what is current;
- what was believed before;
- which source supports each state;
- where a stale or poisoned fact first entered a dependency chain;
- whether a contradiction was superseded or merely hidden;
- whether null and negative experimental results were preserved.

HydraDG makes those transitions explicit and queryable.

---

## What we built

- **HydraDB graph/query projection** for temporal state, provenance, contradiction, supersession, and evidence-path traversal.
- **Fractal Custody Objects (FCOs)** and a **Fractal Custody Graph (FCG)** for source -> transformation -> evidence -> claim -> artifact lineage.
- **4D Context Iceberg / FCG visualization** using a browser canvas plus time controls.
- **Reference -> Poison -> Antidote** state transitions that preserve prior and contradictory states rather than deleting them.
- **Track 03 LongMemEval-S full500 retrieval evaluation** with explicit retention of null/negative outcomes.
- **Knowledge Base** linking project concepts and mathematical lineage to evidence and claim ceilings.
- **Reproduction bundle** containing the website source, canonical FCG JSONL, HydraDB projection/import tooling, environment template, custody receipts, and security gates.

---

## HydraDB is load-bearing

HydraDB is the queryable graph projection layer used to traverse governed longitudinal state. Representative relationships include:

```text
Session -> NEXT/PREV -> Session
Session -> ASSERTS -> Fact
Fact -> DERIVED_FROM -> Session
Fact -> ABOUT -> Entity
Fact -> SUPERSEDED_BY -> Fact
Fact -> CONTRADICTS -> Fact
```

The FCO/FCG layer preserves canonical identity, provenance, evidence class, and claim boundaries. **HydraDB is the operational graph/query backend for the submission.**

Judge-facing configuration is under:

```text
apps/hydradg-web/.env.example
apps/hydradg-web/lib/graph.ts
apps/hydradg-web/package.json
apps/hydradg-web/package-lock.json
```

Those files are intended to contain the HydraDB path only.

---

## Reproduce the HydraDB database and website from scratch

Portable reconstruction inputs:

```text
apps/hydradg-web/                  complete Next.js / React website source
apps/hydradg-web/.env.example      HydraDB environment template
apps/hydradg-web/package-lock.json pinned web dependency resolution
custody/graph/live/nodes.jsonl     canonical public FCG nodes
custody/graph/live/edges.jsonl     canonical public FCG edges
scripts/project_fcg_snapshot_to_hydradb.py
                                    deterministic FCG -> HydraDB importer
scripts/project_website_knowledge_to_hydradb.py
                                    knowledge-FCO projection helper
HOW_TO.md                          judge-oriented setup path
docs/JUDGE_REPRODUCE_FROM_SCRATCH.md
                                    clean-machine reconstruction guide
HYDRADB_DATA.md                    graph/data specification
.github/workflows/gitleaks-release.yml
                                    fail-closed full-history secret scan
```

The HydraDB state is distributed in **portable canonical form**—the graph node/edge snapshot plus deterministic projection tooling—rather than as an opaque machine-specific database directory. A judge can create a fresh isolated HydraDB namespace, import the snapshot, and verify node/edge counts plus the expected FCG-root readback.

### Web build

```bash
git clone https://github.com/biobitworks/hydradg.git
cd hydradg/apps/hydradg-web
cp .env.example .env.local
npm ci
npm run typecheck
npm run build
npm run start -- -p 3012
```

For the HydraDB-backed reconstruction, configure the isolated HydraDB namespace first using [`docs/JUDGE_REPRODUCE_FROM_SCRATCH.md`](docs/JUDGE_REPRODUCE_FROM_SCRATCH.md).

---

## Canonical public graph snapshot

- [`custody/graph/live/nodes.jsonl`](custody/graph/live/nodes.jsonl)
- [`custody/graph/live/edges.jsonl`](custody/graph/live/edges.jsonl)
- [`HYDRADB_DATA.md`](HYDRADB_DATA.md)

Executed Track 03 experiment root used as a readback canary:

```text
experiment:fa170ab51cdfba46f9a24979c9be9b90fdc4ccedcdb292f313aa4439a92b08d8
```

The importer at [`scripts/project_fcg_snapshot_to_hydradb.py`](scripts/project_fcg_snapshot_to_hydradb.py) validates the JSONL, writes only to an isolated `hydradg-*` namespace, performs readback count checks, and verifies the expected root is present.

---

## Judge routes when running locally

```text
/
/judge
/track03
/graph
/knowledge
/how-to
/eligibility
/backup/hydradg.html
```

The static fallback is presentation-only and must not be interpreted as a live HydraDB surface.

---

## Track 03 benchmark evidence

LongMemEval-S full500:

- **500** total cases
- **23,867** sessions
- **4,776** entities
- **3,506** facts
- **470** scored cases in the historical K=5 analysis; 30 abstentions excluded

Historical K=5 retrieval results:

| Route | Hit@5 | Recall@5 | Interpretation |
|---|---:|---:|---|
| **A — reference/flat** | **0.9638** | **0.9066** | reference baseline |
| B | 0.9468 | 0.8538 | no positive Hit@5 advantage |
| C | 0.9468 | 0.8526 | no positive Hit@5 advantage |
| D | 0.9447 | 0.8460 | no positive Hit@5 advantage |

**Submission claim:** the completed K=5 retrieval ablation did **not** establish a positive B/C/D Hit@5 advantage over the reference route. HydraDG retains that null/negative result in the same custody graph rather than replacing it with a preferred result.

Hit@K and Recall@K are retrieval metrics. They are not end-to-end QA accuracy.

---

## Context Iceberg: G* and Cloud Drift

HydraDG uses an application-defined, dimensionless information-state diagnostic `G*` and reference-relative `Delta G*`.

The information-theoretic Gibbs/free-energy analogy is linked to:

**Enßlin & Weig (2010)** — *Inference with minimal Gibbs free energy in information field theory*, Physical Review E 82, 051112, DOI `10.1103/PhysRevE.82.051112`.

HydraDG's `G*` is **not physical Gibbs free energy**, is not measured in joules or kcal/mol, and lower `G*` does not automatically imply better Hit@K, Recall@K, or QA performance.

Cloud Drift is separately derived from Jensen-Shannon divergence and should not be interpreted as accuracy.

---

## FCO/FCG custody

**FCO = Fractal Custody Object.**  
**FCG = Fractal Custody Graph.**

Material source, transformation, derived-evidence, claim, and artifact relationships are kept explicitly separate where the project custody model applies. Public-safe custody receipts are under [`custody/`](custody/).

A hash does not imply a signature. A signature does not imply a Merkle/MMR commitment. Neither implies scientific verification unless the corresponding operation and evidence exist.

---

## Security gate

Before publication, the exact judge commit must pass:

```bash
gitleaks git --redact=100 --no-banner .
```

The fail-closed workflow is:

```text
.github/workflows/gitleaks-release.yml
```

It scans complete Git history and fails on any finding. A historical or partial scan is not enough to call the final repository clean.

---

## Repository map

- `apps/hydradg-web/` — website and API source
- `HydraDG_DaisyTrain_v0.3.7/` — Track 03 evaluation/reproduction tooling
- `custody/` — public-safe FCO/FCG and verification receipts
- `custody/graph/live/` — canonical public graph snapshot
- `docs/` — architecture, component, reproduction, and claim-boundary documentation
- `schemas/` — state/data schemas
- `scripts/` — HydraDB projection, verification, release, and reproduction tooling
- `SUBMISSION.md` — Hack Hydra submission scope

---

## Licensing

| Category | Licensing Scope |
|---|---|
| **HydraDG software / website / scripts** | **Apache License, Version 2.0** ([`LICENSE`](LICENSE)) |
| **Byron P. Lee / Biobitworks preprints / manuscripts / authored research content** | **CC BY-NC-ND 4.0** ([`LICENSING.md`](LICENSING.md)) |
| **HydraDB** | **Upstream HydraDB license** |
| **LongMemEval / other datasets** | **Respective upstream dataset licenses** |
| **External papers / templates / APIs** | **Respective upstream rights** |

See [`LICENSING.md`](LICENSING.md) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for scope and third-party attribution.
