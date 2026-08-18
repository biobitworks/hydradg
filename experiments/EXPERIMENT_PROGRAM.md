# HydraDG fast-track experiment program

Status: ACTIVE
Purpose: support the Hack Hydra MVP and the accompanying implementation/how-to post.

## Operating mode

The MVP is experiment-driven rather than governance-gated.

Governance is intentionally **not on the critical path** for this project type. Useful governance patterns are retained as examples for future releases and preprints, but an experiment does not wait for a governance review unless the experiment itself tests a governance mechanism.

The following remain hard technical/evidentiary requirements because they are intrinsic to the claims we intend to make:
- public-source provenance;
- per-source/per-atom license evidence;
- model/agent/tool lineage;
- deterministic FCO identity where claimed;
- Anticube classification receipts where claimed;
- explicit claim ceilings;
- no seal/signature/MMR claim without an executed operation.

## Script + notebook rule

Every experiment has two first-class implementations:

1. **Runner script** — canonical reusable execution path used by tests/CI and batch runs.
2. **Jupyter notebook** — reader-facing experiment record/tutorial that imports or calls the same reusable functions and renders checks/results.

Do not implement independent scientific logic twice. Shared logic belongs under `src/` or `experiments/lib/`; the CLI and notebook call that common code.

Each experiment directory contains:

```text
EXP-NNN-name/
  README.md
  experiment.json
  run.py
  notebook.ipynb
  inputs/
  outputs/
  receipts/
  LAB_NOTE.md
```

Generated outputs and large inputs may be excluded from Git when required, but their manifests/hashes remain in the experiment record.

## Experiment manifest minimum

`experiment.json` records:
- experiment id and title;
- status (`PLANNED`, `RUNNABLE`, `EXECUTED`, `VERIFIED`, `FAILED`);
- question/hypothesis;
- public source ids;
- source versions/commits/DOIs;
- license evidence ids;
- input object hashes;
- code commit;
- runner path;
- notebook path;
- agent/session id;
- model/provider/version for model-derived steps;
- tool actions;
- deterministic vs probabilistic step classification;
- expected outputs;
- claim ceiling;
- parent experiment ids;
- execution receipt ids;
- red-team checks applicable to this experiment.

## Lab note minimum

`LAB_NOTE.md` records:
- Date/time and operator/agent identities.
- Goal.
- Inputs and exact source citations.
- Licenses.
- Environment.
- Procedure.
- Deviations from preregistered/expected procedure.
- Raw observations.
- Derived outputs.
- Hashes/receipts.
- Anticube result where applicable.
- Interpretation.
- Claim ceiling.
- Failures/abstentions.
- Next experiment.

## Fast-track sequence

### EXP-001 — Public Source + License Admission

Question: Can every candidate public source be version-pinned and assigned explicit license evidence before atom extraction?

Build:
- public source registry validator;
- DOI/GitHub source adapter interface;
- license-evidence validator;
- quarantine report.

Notebook:
- show admitted vs quarantined sources;
- show why each source failed/pass;
- print source/version/license lineage.

Pass:
- no admitted source has missing public URL, version/commit/DOI, or license evidence.

### EXP-002 — SeedGraph Total Import + Atomization

Question: Can a complete admitted source be imported and atomized deterministically while preserving hierarchy, order, citations, licenses, and extraction lineage?

Build:
- SeedGraph bundle schema;
- total-source importer;
- atomizer adapter;
- stable locator generation;
- canonical FCO hashing;
- duplicate-import equality check.

Notebook:
- source -> sections -> atoms graph summary;
- sample atoms with citations/license/model lineage;
- duplicate ingest hash comparison.

Pass:
- same bytes/config produce the same canonical source/atom IDs;
- every atom traverses to source and license evidence.

### EXP-003 — Anticube Atom Classification

Dependency: public Anticube contract/version must be pinned.

Question: Can every admitted atom be classified with a traceable Anticube receipt without overwriting earlier classifier states?

Build:
- Anticube adapter;
- batch classifier;
- classification FCO/FCG objects;
- failure quarantine.

Notebook:
- label/score distributions;
- uncertainty;
- per-atom lineage examples;
- classifier repeat/version comparison where contract permits.

Pass:
- 100% of promoted atoms have a current classification receipt;
- failed classifications remain quarantined.

### EXP-004 — Seed of Truth Construction

Question: Can admitted/classified atoms be synthesized into bounded candidate Seeds of Truth without adding unsupported factual clauses?

Build:
- candidate grouping;
- support/contradiction graph;
- synthesis adapter;
- claim-ceiling propagation;
- unsupported-clause checker.

Notebook:
- selected seed examples;
- supporting and contradicting atom paths;
- weakest-dependency ceiling calculation.

Pass:
- every promoted seed traverses to admitted atoms/public sources/license records;
- no seed claim exceeds the weakest load-bearing evidence.

### EXP-005 — Anticube Seed Classification + Drift

Question: How do atom and seed classifications change as sources, support graphs, models, or classifier versions change over time?

Build:
- Seed-level Anticube classification;
- append-only state/version model;
- drift receipt;
- `DRIFTED_FROM`, `RECLASSIFIED_AS`, `SUPERSEDED_BY`, `CONTRADICTS` edges;
- first-divergence and affected-set calculations.

Notebook:
- temporal timelines;
- label/score drift;
- source/support/model/version deltas;
- injected perturbation cases.

Pass:
- old state remains reconstructable;
- known injected first divergence and affected sets are recovered within the experiment's declared metric threshold.

### EXP-006 — HydraDB Ingest + Track-03 Queries

Question: Can the FCO/FCG/SeedGraph state be ingested into HydraDB and support current, historical, provenance, license, classification, contradiction, and drift queries?

Build:
- bundle -> HydraDB importer;
- current-state query;
- historical query;
- source/license path;
- model/agent path;
- Anticube history;
- affected-set/drift query;
- abstention on incomplete evidence.

Notebook:
- execute canonical query suite;
- compare expected graph answers with returned answers;
- latency/context/storage measurements.

Pass:
- all canonical queries return expected graph-ground-truth answers;
- missing evidence causes abstention/failure rather than promotion.

### EXP-007 — Simulated Key vs Real Custody Boundary

Question: Can the demo exercise signing UX without confusing a simulated key with an actual cryptographic signature?

Build:
- `SIMULATED_DEMO_KEYPAIR` fixture;
- simulated receipt state;
- optional real Ed25519 signer adapter using public FCO implementation only when actually invoked;
- visible UI separation.

Notebook:
- compare simulated and real receipt schemas/states;
- mutate payload and demonstrate validation behavior for executed real-signature route if available.

Pass:
- no simulated artifact is labeled signed/verified;
- real signature claims require actual verification receipt.

### EXP-008 — Red-Team + Recovery Suite

Question: Does the system fail closed under missing provenance, bad licenses, source mutations, classifier changes, prompt injection, contradictions, and broken graph edges?

Build:
- adversarial fixture generator;
- expected-failure manifest;
- recovery/restoration cases;
- scorecard.

Notebook:
- attack matrix;
- earliest divergent dependency;
- rejected/promoted counts;
- first-divergence and recovery metrics.

Pass:
- all blocking attacks are rejected/quarantined;
- recovery cases restore only the appropriate downstream states.

### EXP-009 — LongMemEval + A-D Ablation

Question: What does the full HydraDG provenance/drift layer add to HydraDB Track 03 memory performance and systems cost?

Configurations:
- A flat/vector retrieval;
- B HydraDB temporal graph;
- C HydraDB + provenance;
- D full HydraDG: FCO/FCG + Anticube + drift/admission.

Development: deterministic smoke80.
Final: all 500 official cases only after policy/query freeze.

Notebook:
- overall and category metrics;
- provenance path coverage;
- context tokens;
- p50/p95 latency;
- storage/ingest overhead;
- abstention behavior.

Pass:
- denominators remain separate from ECA/Xeno/Vithia conformance/scientific lanes;
- the notebook and script reproduce the same scorecard from the same frozen result files.

### EXP-010 — Final FCG Candidate and Seal Demonstration

Question: Can all final admitted experiment results be assembled into one verifiable FCG candidate, with seal state exactly matching the operations performed?

Build:
- final graph manifest;
- included-object list;
- graph root computation;
- optional real signing/MMR only if public implementation is pinned and actually executed;
- publication export.

Notebook:
- graph composition summary;
- dependency paths for headline claims;
- seal-state verification.

Pass:
- every headline claim has a traversable dependency path;
- graph state says `UNSEALED`, `SIGNED`, `COMMITTED`, etc. only according to executed receipts.

## Publication/how-to artifacts

The post/preprint should use the experiments as implementation examples:
- architecture figure: source -> atom -> Anticube -> seed -> Anticube -> drift -> FCG;
- one reproducible example from each key experiment;
- one provenance/license table;
- one model/agent chain-of-custody table;
- one drift timeline;
- one red-team failure/recovery figure;
- one Track 03 ablation table;
- final custody-state diagram.

The notebooks are companion evidence/tutorial artifacts, not substitutes for the reusable scripts or raw receipts.

## Deferred governance examples

Place optional/future material under `examples/governance/` and keep it out of MVP pass/fail gates. Future versions may demonstrate:
- disclosure review;
- public/private data routing;
- IP/FTO/commercialization separation;
- human approval gates;
- publication-release workflows;
- multi-operator signatures/independent verification.

These examples may cite public implementations and public preprints, but private-only `gtm-cellico` content is not copied into publication artifacts.
