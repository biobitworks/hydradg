# HydraDG Hack Hydra execution schedule

Status: ACTIVE_EXECUTION_SCHEDULE
Timezone: America/Los_Angeles (PDT)
Hackathon submission boundary used by this plan: 2026-08-20 00:00 PDT
Branch: `hack-hydra/webapp-mvp-20260818`

## MVP objective

Ship a working Track 03 web application demonstrating this auditable knowledge-memory path:

`public source -> source/license gate -> SeedGraph total import -> atomization -> FCO identity -> Anticube atom classification -> Seed of Truth synthesis -> Anticube seed classification -> temporal drift -> HydraDB retrieval/history -> review/red-team -> final FCG candidate`

The demo must show that a user can ingest public material, inspect atoms and their licenses/model-agent lineage, see classification and drift, retrieve historical/current graph state, and traverse a claim back to evidence.

## Scope rule

### Release-blocking for the hackathon MVP
- public-source/version pin;
- exact upstream license/rights metadata per source/atom;
- model/agent/tool lineage for AI-derived atoms;
- deterministic FCO identity/hash generation;
- SeedGraph total import;
- Anticube adapter/classification or an explicit fail-closed blocked state if the public contract cannot be admitted;
- Seed-of-Truth derivation and claim ceilings;
- at least two temporal graph states with first-divergence/drift reconstruction;
- HydraDB current/history/evidence-path queries;
- web demo for source -> atom -> seed -> drift -> FCG path;
- secret isolation and simulated-key labeling;
- red-team/replay checks;
- reproducible scripts + paired Jupyter notebooks + lab-notebook records.

### Not a hackathon blocking gate
- full SOC 2/FAIR/NIST/ISO governance implementation;
- certification/compliance claims;
- complete TRAITS framework crosswalk;
- production PKI;
- exhaustive LongMemEval full500;
- multi-cloud production hardening.

These remain examples/future-version work and may be included in the post/preprint as clearly labeled design/implementation guidance.

## Licensing rule

Project-authored research/publication material defaults to CC BY-NC-ND 4.0 where Creative Commons licensing is appropriate. Imported sources retain their exact upstream license. Software retains applicable software licenses. No atom inherits a project license by overwriting upstream rights.

## TRAITS source state

Canonical definition:

`Traceable, Rigorous, Accurate, Interpretable, Transparent, Secure`

Earliest recovered repository evidence currently verified:

`biobitworks/antigence@7d0c2e929d4bd8fc0bf6620d60f9245ae8cd083d`

The Antigence repository is currently private, so this commit is an internal historical anchor, not yet an admissible public publication atom.

---

# Execution order

## Phase 0 — freeze architecture and source rules
### 2026-08-18 13:00–14:30 PDT

Owner lane: core architecture / custody
Priority: P0

Tasks:
- [x] Freeze canonical pipeline: SeedGraph -> FCO/FCG -> Anticube -> Seed of Truth -> drift -> final FCG candidate.
- [x] Freeze TRAITS definition and pin recovered Antigence commit internally.
- [x] Freeze base project licensing policy.
- [ ] Create/update `config/public_source_registry.json` with selected MVP sources.
- [ ] Record exact DOI/repo, version/commit, visibility, license, rights holder, and source hash where bytes are available.
- [ ] Select one small public corpus for end-to-end demo before adding Vitaology-scale material.
- [ ] Mark private-only sources `INTERNAL_REFERENCE_ONLY` and block them from publication admission.

Exit gate:
- every MVP source is either `ADMITTED_PUBLIC_SOURCE` or `QUARANTINED/INTERNAL_REFERENCE_ONLY`;
- no unresolved source is on the critical demo path.

## Phase 1 — provenance/licensing/FCO spine
### 2026-08-18 14:30–18:00 PDT

Owner lane: schemas + reusable core scripts
Priority: P0

Build reusable scripts and notebooks together:
- [ ] `scripts/validate_source.py` + `notebooks/EXP-001_source_admission.ipynb`
- [ ] `scripts/canonicalize_fco.py` + `notebooks/EXP-002_fco_identity.ipynb`
- [ ] `scripts/validate_lineage.py` + notebook cells showing human/model/agent/tool custody.
- [ ] JSON schemas for Source, LicenseEvidence, KnowledgeAtom, ModelInvocation, AgentSession, ToolAction, ReviewDecision, SealReceipt.
- [ ] deterministic canonical JSON + SHA-256 object identity.
- [ ] fail-closed public-source, license, and model/agent lineage gates.
- [ ] simulated private/public key fixture labeled `SIMULATED_DEMO_KEYPAIR` only.
- [ ] write each run into the lab-notebook template with inputs, hashes, commands, outputs, negative results, model/agent metadata, and claim ceiling.

Exit gate:
- changing one source byte changes its source/FCO identity;
- re-running unchanged canonical input reproduces the same identity;
- missing source/license/lineage blocks promotion.

## Phase 2 — SeedGraph total import
### 2026-08-18 18:00–22:00 PDT

Owner lane: ingestion
Priority: P0

Build:
- [ ] `scripts/seedgraph_total_import.py`
- [ ] `notebooks/EXP-003_seedgraph_total_import.ipynb`
- [ ] full-source hierarchy preservation;
- [ ] deterministic atomization with stable locators;
- [ ] upstream license attached to each derived atom;
- [ ] extractor agent/model/tool receipt attached to every AI-derived atom;
- [ ] content-hash dedupe without collapsing independent source provenance;
- [ ] deterministic import manifest with node/edge/object counts and SHA-256 hashes;
- [ ] HydraDB ingest adapter for the resulting bundle.

Exit gate:
- same source/version imported twice yields the same canonical source/atom IDs;
- every admitted atom traverses back to source + license + extraction lineage.

## Phase 3 — Anticube + Seed of Truth
### 2026-08-18 22:00–2026-08-19 04:00 PDT

Owner lane: classification / synthesis
Priority: P0/P1

Tasks:
- [ ] resolve and pin public Anticube contract/license if available;
- [ ] `scripts/anticube_classify.py` + `notebooks/EXP-004_anticube_atoms.ipynb`;
- [ ] classify every admitted atom, preserving classifier/model/agent/version and input/output hashes;
- [ ] fail closed if classification cannot execute;
- [ ] `scripts/build_seeds_of_truth.py` + `notebooks/EXP-005_seed_of_truth.ipynb`;
- [ ] record supporting and contradicting atoms for each seed;
- [ ] enforce claim ceiling from load-bearing evidence;
- [ ] classify every candidate/promoted seed with Anticube;
- [ ] log disagreements between atom classifications and seed classification as reviewable evidence, not overwrite events.

Contingency:
If the public Anticube source/contract cannot be admitted in time, the MVP must visibly show `IMPLEMENTATION_PENDING_PUBLIC_CONTRACT` and demonstrate the adapter/fail-closed custody behavior without fabricating Anticube labels.

Exit gate:
- 100% of promoted atoms and seeds have traceable classification receipts, or are visibly blocked from promotion.

## Phase 4 — temporal drift + HydraDB memory queries
### 2026-08-19 04:00–09:00 PDT

Owner lane: graph/history
Priority: P1

Build:
- [ ] `scripts/create_drift_fixture.py` + `notebooks/EXP-006_temporal_drift.ipynb`;
- [ ] create at least two graph states by changing a source/support/classifier/model state;
- [ ] append `SUPERSEDED_BY`, `DRIFTED_FROM`, `RECLASSIFIED_AS`, and `CONTRADICTS` edges as applicable;
- [ ] compute first divergence and downstream affected set;
- [ ] current-state HydraDB query;
- [ ] historical-state query;
- [ ] source/license evidence-path query;
- [ ] model/agent derivation-path query;
- [ ] Anticube classification-history query;
- [ ] contradiction/supersession query;
- [ ] fail-closed abstention when evidence path is absent.

Exit gate:
- one changed dependency produces a new append-only state;
- old state remains reconstructable;
- first divergence is correctly localized for the demo fixture.

## Phase 5 — web application integration
### 2026-08-19 09:00–14:00 PDT

Owner lane: web/demo
Priority: P1

Complete the existing Next.js MVP surface:
- [x] app scaffold;
- [x] graph query/status surface;
- [x] Exa retrieval path;
- [ ] Source Registry;
- [ ] Import/Atomization page;
- [ ] Atom Inspector: source, license, object hash, extractor model/agent/tool, Anticube state;
- [ ] Seed of Truth Inspector;
- [ ] Drift Timeline;
- [ ] FCG evidence/dependency graph visualization;
- [ ] Review/Red-Team queue;
- [ ] Seal Candidate page showing exact custody state;
- [ ] simulated-key state visibly different from any real-signature state.

Primary demo path:
1. choose public source;
2. show license/version;
3. total import;
4. inspect one atom;
5. inspect Anticube classification;
6. inspect Seed of Truth;
7. introduce/load second state;
8. show drift/first divergence;
9. ask HydraDB current vs historical question;
10. traverse answer -> seed -> atom -> source/license/model-agent chain.

Exit gate:
- entire primary demo path runs without manual database editing.

## Phase 6 — review, red team, experiments
### 2026-08-19 14:00–18:00 PDT

Owner lane: review / safety / reproducibility
Priority: P1

Run paired scripts + Jupyter notebooks + lab-notebook entries:
- [ ] source version mismatch attack;
- [ ] missing/wrong license attack;
- [ ] private-only source admission attempt;
- [ ] prompt/instruction injection inside retrieved source text;
- [ ] missing model/agent lineage;
- [ ] atom mutation after classification;
- [ ] duplicated source pretending to be independent evidence;
- [ ] unsupported clause inserted into Seed of Truth;
- [ ] classifier version drift;
- [ ] orphan claim/evidence path break;
- [ ] simulated signature mislabeled as real signature;
- [ ] secret/API-key leak scan;
- [ ] replay selected experiments from clean input.

Metrics to report:
- admission rejection accuracy on fixtures;
- deterministic replay success;
- first-divergence exact match;
- affected-set precision/recall/F1 where fixture ground truth exists;
- unsupported-seed rejection rate;
- historical reconstruction success;
- query latency and ingest overhead separately from correctness.

Exit gate:
- no release-blocking red-team failure remains open;
- negative results are retained in notebooks/lab notes.

## Phase 7 — benchmark/demo evidence freeze
### 2026-08-19 18:00–20:30 PDT

Priority: P1/P2

Tasks:
- [ ] run bounded Track 03 smoke benchmark / selected LongMemEval smoke set if stable;
- [ ] do not start Full500 if core policies or query behavior are still changing;
- [ ] capture demo fixture manifests and graph counts;
- [ ] capture screenshots/figures only from reproducible states;
- [ ] generate evidence table: claim -> experiment -> artifact -> hash -> limitation;
- [ ] freeze primary demo dataset and source versions.

Exit gate:
- results used in the post/demo map to specific reproducible experiment artifacts.

## Phase 8 — release candidate and submission freeze
### 2026-08-19 20:30–22:30 PDT

Priority: P0 release

Tasks:
- [ ] run full local checks/tests;
- [ ] inspect Git diff for secrets/private-only evidence;
- [ ] verify upstream/project licensing table;
- [ ] verify every displayed claim has an evidence path and claim ceiling;
- [ ] verify custody state wording: no unsupported `signed`, `sealed`, `Merkle-committed`, or `independently verified` language;
- [ ] generate final README/demo instructions;
- [ ] freeze submission commit/tag candidate;
- [ ] record commit SHA and artifact hashes in release lab-note entry.

Stop-change rule after 22:30 PDT:
Only submission-blocking bug fixes. No architecture changes, dependency upgrades, or new experimental claims.

## Phase 9 — submission buffer
### 2026-08-19 22:30–23:59 PDT

Tasks:
- [ ] final submission form/package;
- [ ] verify repository/demo links from a clean browser/session;
- [ ] verify video/demo sequence if required;
- [ ] save exact submitted commit SHA and submission metadata;
- [ ] preserve final FCG state as the submission candidate.

The graph is called sealed/signed only if an actual corresponding operation has executed and verified. Otherwise final state remains `REVIEWED_UNSEALED_GRAPH` or other exact executed state.

---

# Parallel non-blocking lane — TRAITS / governance implementation example

Run only after core critical-path tasks are on schedule.

Target: 2026-08-19 after 18:00 PDT or post-hackathon.

- [ ] build EXP-011 machine-readable TRAITS crosswalk;
- [ ] pair script + Jupyter + lab-notebook record;
- [ ] map Traceable/Rigorous/Accurate/Interpretable/Transparent/Secure to selected current framework controls;
- [ ] preserve exact framework source/version/license per mapping atom;
- [ ] red-team claimed gaps;
- [ ] explicitly separate implementation evidence from compliance/certification;
- [ ] use as a how-to example for later GitHub/preprint versions.

This lane is intentionally not allowed to delay the Track 03 web-app MVP.

# Reusable experiment package rule

Every experiment should have, where applicable:

```text
experiments/EXP-XXX-name/
  README.md                 # hypothesis, falsifier, inputs, outputs, claim ceiling
  run.py or ../../scripts/  # reusable deterministic/parameterized runner
  notebook.ipynb            # human-readable analysis and figures
  lab_notebook.md           # chronological run record
  inputs/manifest.json      # source/version/license/model-agent pins
  outputs/                  # generated results
  receipts/                 # hashes, tool/model/classifier receipts
```

The script is the reusable implementation surface. The notebook explains and interrogates the run. The lab notebook records what actually happened. None substitutes for the others.

# Definition of ready

HydraDG is hackathon-MVP ready when:

1. one public source passes source/license admission;
2. SeedGraph total import deterministically emits FCO/FCG objects;
3. every promoted atom has source/license/model-agent custody;
4. atom and seed Anticube states are either executed and traceable or explicitly blocked/fail-closed;
5. at least one Seed of Truth can be traversed to supporting/contradicting atoms;
6. at least two temporal states demonstrate drift and first divergence;
7. HydraDB answers current, historical, and evidence-path queries;
8. the web app exposes the entire path;
9. red-team/replay critical tests pass;
10. all submission claims map to named evidence artifacts with bounded claim ceilings.
