# HydraDG — Graph-Native Governed Context Engine

[![Hack Hydra 2026](https://img.shields.io/badge/Hack%20Hydra-2026-blue.svg)](https://github.com/biobitworks/hydradg)
[![Track 03](https://img.shields.io/badge/Track%2003-Memory%20%2B%20Context%20Retrieval-green.svg)](https://github.com/biobitworks/hydradg)
[![HydraDB](https://img.shields.io/badge/HydraDB-Graph%20Projection-orange.svg)](https://hydradb.com)
[![Software License: Apache-2.0](https://img.shields.io/badge/Software-Apache--2.0-yellow.svg)](LICENSE)
[![Research Content: CC BY-NC-ND 4.0](https://img.shields.io/badge/Research%20Content-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSING.md)

HydraDG is a governed memory and context engine built on **HydraDB** for **Hack Hydra 2026 — Track 03: Memory + Context Retrieval**. It preserves evolving state, provenance, contradictions, supersession, recovery, null results, and claim boundaries as an inspectable graph instead of silently overwriting context.

**Current demo video:** https://youtu.be/7EDb6q-loPA

---

## Judge: start here

If you have three minutes:

1. Watch the demo video above.
2. Read [`SUBMISSION.md`](SUBMISSION.md) for the bounded Track 03 submission claim.
3. Use [`HOW_TO.md`](HOW_TO.md) or [`docs/JUDGE_REPRODUCE_FROM_SCRATCH.md`](docs/JUDGE_REPRODUCE_FROM_SCRATCH.md) to rebuild the HydraDB graph and website on a clean machine.
4. Inspect the canonical public FCG snapshot in [`custody/graph/live/`](custody/graph/live/).
5. Inspect [`docs/COMPONENT_MAP.md`](docs/COMPONENT_MAP.md) to see what each component does, why it exists, and its claim boundary.

---

## The problem

Long-lived AI memory systems can flatten or overwrite changing context. Once facts are updated or contradicted, it becomes difficult to determine:

- what is current;
- what was believed before;
- which source supports each state;
- where a stale or poisoned fact first entered the dependency chain;
- whether a contradiction was superseded or merely hidden;
- whether null and negative experimental results were preserved.

HydraDG makes those transitions explicit and queryable.

---

## What we built

- **HydraDB graph/query projection** for temporal state, provenance, contradiction, supersession, and evidence-path traversal.
- **Fractal Custody Objects (FCOs)** and a **Fractal Custody Graph (FCG)** for source -> transformation -> evidence -> claim -> artifact lineage.
- **4D Context Iceberg / FCG visualization** with graph-space interaction plus time.
- **Reference -> Poison -> Antidote** state-transition workflow that keeps historical and contradictory states instead of deleting them.
- **Track 03 LongMemEval-S full500 retrieval evaluation** with explicit null/negative-result retention.
- **Knowledge Base** linking concepts, mathematical lineage, evidence, and claim ceilings.
- **Reproduction bundle** containing website source, canonical FCG JSONL, HydraDB import/projection tools, environment template, custody receipts, and security gates.

---

## HydraDB is load-bearing

HydraDB is the queryable graph projection layer used to traverse governed longitudinal state. Example typed relationships include:

```text
Session -> NEXT/PREV -> Session
Session -> ASSERTS -> Fact
Fact -> DERIVED_FROM -> Session
Fact -> ABOUT -> Entity
Fact -> SUPERSEDED_BY -> Fact
Fact -> CONTRADICTS -> Fact
```

The FCO/FCG layer preserves canonical identity, provenance, evidence class, and claim boundaries. **HydraDB is a projection of that custody state, not the canonical identity store.**

---

## Reproduce the database and website from scratch

The portable reconstruction inputs are in this repository:

```text
apps/hydradg-web/                  complete Next.js / React website source
apps/hydradg-web/.env.example      environment template
apps/hydradg-web/package-lock.json pinned web dependency resolution
custody/graph/live/nodes.jsonl     canonical public FCG nodes
custody/graph/live/edges.jsonl     canonical public FCG edges
scripts/project_fcg_snapshot_to_hydradb.py
                                    deterministic FCG -> HydraDB importer
scripts/project_website_knowledge_to_hydradb.py
                                    Knowledge FCO projection helper
HOW_TO.md / docs/JUDGE_REPRODUCE_FROM_SCRATCH.md
                                    complete clean-machine walkthrough
.github/workflows/gitleaks-release.yml
                                    fail-closed full-history secret scan
```

The HydraDB database is distributed in **portable canonical form**—the graph node/edge snapshot plus deterministic projection tooling—rather than as a machine-specific database directory. A judge can create a fresh isolated HydraDB namespace, import the snapshot, and verify graph counts plus the expected FCG-root readback.

### Minimal web build

```bash
git clone https://github.com/biobitworks/hydradg.git
cd hydradg
npm install
npm run dev
```

For comprehensive replication and database setup details, see [`HOW_TO.md`](HOW_TO.md) and [`HYDRADB_DATA.md`](HYDRADB_DATA.md).

---

## Canonical public graph snapshot

- [`custody/graph/live/nodes.jsonl`](custody/graph/live/nodes.jsonl)
- [`custody/graph/live/edges.jsonl`](custody/graph/live/edges.jsonl)
- **Data Manual**: Detailed specification in [`HYDRADB_DATA.md`](HYDRADB_DATA.md).
- **Node Schemas**: `HydraDG_DaisyTrain_v0.3.1/hydra/schema_nodes.json` (`Session`, `Fact`, `Entity`, `KnowledgeAtom`).
- **Edge Schemas**: `HydraDG_DaisyTrain_v0.3.1/hydra/schema_edges.json` (`NEXT`, `ASSERTS`, `DERIVED_FROM`, `ABOUT`, `SUPERSEDES`, `CONTRADICTS`).

Executed Track 03 experiment root used as a readback canary:

```text
experiment:fa170ab51cdfba46f9a24979c9be9b90fdc4ccedcdb292f313aa4439a92b08d8
```

The importer at [`scripts/project_fcg_snapshot_to_hydradb.py`](scripts/project_fcg_snapshot_to_hydradb.py) validates the JSONL, writes only to an isolated `hydradg-*` namespace, performs readback count checks, and verifies this root is present.

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

**Ensslin & Weig (2010)** — _Inference with minimal Gibbs free energy in information field theory_, Physical Review E 82, 051112, DOI `10.1103/PhysRevE.82.051112`.

HydraDG's `G*` is **not physical Gibbs free energy**, is not measured in joules or kcal/mol, and lower `G*` does not automatically imply better Hit@K, Recall@K, or QA performance.

Cloud Drift is separately derived from Jensen-Shannon divergence and should not be interpreted as accuracy.

---

## FCO/FCG custody

**FCO = Fractal Custody Object.**  
**FCG = Fractal Custody Graph.**

Material source, transformation, derived-evidence, claim, and artifact relationships are kept explicitly separate where the project custody model applies. Public-safe custody receipts are under [`custody/`](custody/).

A hash does not imply a signature. A signature does not imply a Merkle/MMR commitment. Neither implies scientific verification unless the corresponding operation and evidence exist.

- **Submission Summary**: [`SUBMISSION.md`](SUBMISSION.md)
- **Demo Video URL**: [https://youtu.be/7EDb6q-loPA](https://youtu.be/7EDb6q-loPA)
- **Repository**: [https://github.com/biobitworks/hydradg](https://github.com/biobitworks/hydradg)
- **Release Branch**: `hack-hydra/public-product-final-20260819`

---

## Security gate

Before publication, scan the exact release history:

```bash
gitleaks git --redact=100 --no-banner .
```

The release branch also contains a fail-closed GitHub Actions workflow:

```text
.github/workflows/gitleaks-release.yml
```

A historical or partial scan is not enough to call the repository clean. The exact release commit must pass the current scan.

---

## Repository map

- `apps/hydradg-web/` — website and API source
- `HydraDG_DaisyTrain_v0.3.7/` — Track 03 evaluation/reproduction tooling
- `custody/` — public-safe FCO/FCG and verification receipts
- `custody/graph/live/` — canonical public graph snapshot
- `docs/` — architecture, component, reproduction, and claim-boundary documentation
- `schemas/` — state/data schemas
- `scripts/` — projection, verification, release, and reproduction tooling
- `SUBMISSION.md` — Hack Hydra submission scope
- `LICENSE` / `LICENSING.md` / `THIRD_PARTY_NOTICES.md` — licensing and third-party notices

---

## Licensing

| Category | Licensing Scope |
|---|---|
| **HydraDG software / website / scripts** | **Apache License, Version 2.0** ([`LICENSE`](LICENSE)) |
| **Byron P. Lee / Biobitworks preprints / manuscripts / authored research content** | **CC BY-NC-ND 4.0** ([`LICENSING.md`](LICENSING.md)) |
| **HydraDB** | **Upstream HydraDB License** |
| **LongMemEval / other datasets** | **Respective Upstream Dataset Licenses** |
| **External papers / templates / APIs** | **Respective Upstream Rights** |

For complete licensing details, see [`LICENSING.md`](LICENSING.md) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
