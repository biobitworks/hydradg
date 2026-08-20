# Hack Hydra 2026 — Submission Document

## 1. Project Information

- **Project Name:** HydraDG — Graph-Native Governed Context Engine
- **Primary Track:** Track 03 — Memory + Context Retrieval
- **Repository:** https://github.com/biobitworks/hydradg
- **Judge / release branch:** `main`
- **Repository visibility:** **PUBLIC — verified through GitHub repository metadata during final review**
- **Custody-repair checkpoint:** `5ac81968ba5bdd5d7e71a1ff29deabeb416b7182`
- **Final tested release commit:** `PENDING_EXACT_HEAD_GATE` — replace with the exact `main` SHA after build/typecheck/route/Gitleaks gates complete
- **Demo video URL:** https://youtu.be/7EDb6q-loPA
- **Demo video verification:** URL present; duration and unauthenticated accessibility require external verification before human submission
- **Superseded demo video URL:** https://youtu.be/tKWRmYZ3HCs
- **Submission form:** PENDING_HUMAN_SUBMISSION

`main` is the public judge-facing authority. Historical release branches and draft PRs are provenance/history only unless an older receipt explicitly names them.

A complete submission requires the public repository, the qualifying demo video, and the human submission form. The local interactive product can be used to record the video; a public live website is not required by the repository's supplied submission checklist.

---

## 2. Problem

Long-lived AI memory systems can flatten or overwrite changing state. When facts are updated, contradicted, or restored, provenance can become difficult to reconstruct and null/negative experimental outcomes can disappear from the operational narrative.

---

## 3. Solution

HydraDG is a governed memory/context system built on HydraDB and Fractal Custody Objects / Fractal Custody Graphs (FCO/FCG).

- **FCO — Fractal Custody Object:** a bounded custody object carrying identity, provenance, evidence class, and claim boundaries.
- **FCG — Fractal Custody Graph:** the dependency/relationship graph connecting sources, transformations, derived evidence, claims, and artifacts.
- **HydraDB:** the queryable graph projection used for traversal, retrieval, temporal state, contradiction, and provenance lookup.

The canonical custody objects remain the source of identity; HydraDB is a projection/query substrate rather than a replacement for canonical FCO identity.

---

## 4. Meaningful HydraDB Use

The Track 03 implementation materializes longitudinal memory relationships including:

```text
Session ─NEXT/PREV→ Session
Session ─ASSERTS→ Fact
Fact ─DERIVED_FROM→ Session
Fact ─ABOUT→ Entity
Fact ─SUPERSEDED_BY→ Fact
Fact ─CONTRADICTS→ Fact
```

These relationships support reconstruction of chronology, provenance, current state, contradiction, and evidence paths.

The executable judge application has no Neo4j fallback. Its graph path is:

```text
HydraDG application
-> HydraDB HTTP graph API
-> isolated hydradg-* namespace
```

The public FCG snapshot plus deterministic importer are included so a judge can reconstruct the HydraDB projection without access to the original developer machine.

---

## 5. Executed Track 03 Evidence

Dataset: `xiaowu0162/longmemeval-cleaned`

Executed graph scale:

- **500 cases**
- **23,867 sessions**
- **4,776 entities**
- **3,506 facts**
- **470 retrieval-scored cases**; 30 abstentions excluded from retrieval scoring

Completed K=5 ablation:

| Route | Hit@5 | Recall@5 | Interpretation |
|---|---:|---:|---|
| A — reference/flat route | 0.9638297872 | 0.9065957447 | reference |
| B | 0.9468085106 | 0.8538297872 | no positive hit-rate signal |
| C | 0.9468085106 | 0.85258865 | no positive hit-rate signal |
| D | 0.94468085 | 0.84602837 | no positive hit-rate signal |

The completed experiment did **not** establish a positive B/C/D hit-rate advantage over route A at the tested configuration. Evidence-path coverage increased for graph-native routes while retrieval recall declined. HydraDG preserves that null/negative result instead of promoting a preferred treatment.

**Claim ceiling:** `LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA`

Separate later local E2E/depth observations may be retained in the evidence graph, but they are not used here to claim benchmark superiority or end-to-end QA improvement.

---

## 6. Judge / Demo Flow

Local product when running the reconstructed app:

`http://127.0.0.1:3012/`

Judge/video flow:

```text
Overview
→ Judge Demo: Reference → Poison → Antidote
→ Track 03 Results
→ 4D FCG / Context Iceberg
→ select one FCO
→ source / transformation / evidence / claim ceiling
→ Knowledge Base / How-To
→ custody state
```

### Quick local replication

```bash
git clone https://github.com/biobitworks/hydradg.git
cd hydradg
npm run install:all
npm run typecheck
npm run build
```

For complete HydraDB reconstruction instructions, see [`HOW_TO.md`](HOW_TO.md), [`HYDRADB_DATA.md`](HYDRADB_DATA.md), and [`docs/JUDGE_REPRODUCE_FROM_SCRATCH.md`](docs/JUDGE_REPRODUCE_FROM_SCRATCH.md).

**Current uploaded demo:** https://youtu.be/7EDb6q-loPA

**Superseded uploaded demo:** https://youtu.be/tKWRmYZ3HCs

Static fallback:

`apps/hydradg-web/public/backup/hydradg.html`

The fallback is presentation-only and must remain labeled as not being a live HydraDB control surface.

---

## 7. G* / ΔG* Source Lineage

HydraDG's `G*` / `ΔG*` visualization is an **application-defined, dimensionless information-state diagnostic**.

Source lineage is separated by role:

```text
Enßlin & Weig (2010)
→ information-field/Gibbs-free-energy inference analogy
→ HydraDG design rationale
→ application-defined G*
→ ΔG*

Lin (1991)
→ Jensen-Shannon divergence
→ Cloud Drift
```

HydraDG `G*` is not physical Gibbs free energy, is not measured in joules or kcal/mol, and is not asserted to be identical to the Enßlin–Weig information-field functional. Lower `G*` does not by itself imply better Hit@K, Recall@K, or QA accuracy.

---

## 8. Custody, Licensing, and Claim Boundaries

Current supplied custody state includes:

- Enßlin & Weig source PDF SHA-256: `3ed1f288ac8b3f48f16833bea57d2c464d9d75da1c8d832ef13da6013ff90ab4`
- Source FCO: `fco:source:ensslin_weig_2010:3ed1f288ac8b3f48`
- HydraDG G* design FCO: `fco:design:hydradg_gstar:f4a7e547f4a380c2`
- Local HydraDB Gibbs-lineage canary: `PASS`
- Signature state: `PENDING_EXTERNAL_PRIVATE_KEY_OPERATION` unless a later authorized signing receipt exists
- Merkle/MMR state: `NOT_PROJECT_COMMITTED` unless a later commitment receipt exists

Licensing invariant for this release:

```text
HydraDG software / website / scripts
-> Apache-2.0 where declared

FCO/FCG research publications
+ designated Byron P. Lee / Biobitworks research content
-> CC BY-NC-ND 4.0

historical FCO/FCG CC BY 4.0 metadata
-> SUPERSEDED_METADATA_ERROR
-> preserved for custody/history only
-> not a version-specific licensing exception

third-party material
-> upstream rights
```

A license metadata correction does not mutate historical publication/package bytes and therefore does not itself require recomputing historical file/package hashes or signed roots.

Hash identity is not scientific correctness. Provenance is not independent replication. HydraDB projection is not benchmark superiority.

---

## 9. Final Release Gates

The final judge SHA must satisfy all of the following on the **same exact commit**:

```text
PUBLIC_REPOSITORY=PASS
MAIN_IS_JUDGE_AUTHORITY=PASS
HYDRADB_ONLY_EXECUTABLE=PASS
ISOLATED_NAMESPACE_DEFAULT=PASS
TYPECHECK=PASS
PRODUCTION_BUILD=PASS
JUDGE_ROUTES=PASS
FULL_HISTORY_GITLEAKS=PASS
LICENSING_CONSISTENCY=PASS
```

A historical CI run or secret scan cannot establish these gates for a newer SHA.

---

## 10. Required Submission Status

| Required deliverable | Current status | Completion evidence required |
|---|---|---|
| Public GitHub repository | **PASS — public `biobitworks/hydradg`, default branch `main`** | recheck at final freeze |
| Exact-head repository release gates | **PENDING** | build/typecheck/routes/Gitleaks on exact final `main` SHA |
| Demo video ≤ 3 minutes | **URL PRESENT — external verification pending** | duration ≤ 3:00 + unauthenticated access |
| Submission form | **PENDING — human submission required** | submitted-form confirmation/receipt |

`SUBMISSION_READY=YES` only when the exact-head release gates, qualifying video, and human submission requirements have actual completion evidence.

---

## 11. Final Human Attestations

Before submitting, confirm:

- final team roster and roles;
- originality/reuse disclosure;
- one-submission-per-team-member rule;
- final links work without the submitter's authenticated session;
- claims match their evidence ceilings;
- rules/code-of-conduct confirmation;
- repository, video, and form were all submitted before the deadline.
