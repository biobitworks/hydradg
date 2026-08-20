<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->
# HydraDG Final Custody, Graph Comparison, Conversation Import, Licensing, and Linked-Knowledge Plan

Date: 2026-08-20
Status: PLAN — execution must preserve exact evidence/claim boundaries.

## Objective

Finish HydraDG as one auditable fractal custody system in which the public website, canonical FCO/FCG project graph, hosted HydraDB projection, GitHub-connector graph, research publications, model artifact, conversations, and release metadata resolve backward to explicit sources and hashes.

The final judge walkthrough must make the recursive/fractal structure visible:

source bytes -> SourceFCO -> EvidenceFCO -> KnowledgeAtomFCO -> SeedOfTruthFCO -> StateSnapshotFCO -> FCG root -> ProjectSnapshotFCO -> WebsiteReleaseFCO

Each canonical FCO has one SHA-256 identity. Each declared FCG snapshot has a root over a declared, ordered graph representation. A lower-level root may be carried as evidence in a higher-level FCO, so context, governance, and provenance recur at multiple scales. Hash identity is not correctness. A root is not a signature or a Merkle/MMR commitment unless that separate operation is actually performed.

## Authoritative licensing

1. HydraDG software, website code, scripts, workflows, software schemas, and reproducibility tooling: Apache-2.0.
2. FCO/FCG research publications and designated Byron P. Lee / Biobitworks research content: CC BY-NC-ND 4.0.
3. Earlier CC BY 4.0 FCO/FCG metadata: SUPERSEDED_METADATA_ERROR, retained as historical custody evidence only.
4. Third-party papers, datasets, upstream HydraDB material, model bases, APIs, and other external content retain upstream rights.

Execution work:
- retain root Apache-2.0 LICENSE;
- retain and strengthen LICENSING.md;
- add machine-readable LICENSE_POLICY.json or equivalent path rules;
- add SPDX identifiers to participant-authored code/research files where practical;
- never blanket-relicense third-party material;
- add a release gate that fails on missing or contradictory license classification for designated release files.

## Phase 1 — Freeze exact inputs and continue in-turn custody

For every substantive human/AI/tool turn:
- retain exact input bytes when available;
- retain exact output/action summary bytes;
- calculate SHA-256 over those exact bytes;
- add Turn, ToolAction, KnowledgeUpdate, and AdmissionDecision FCOs;
- connect the objects in the FCG;
- record human/AI/tool contribution boundaries;
- record evidence class and claim ceiling;
- state SIGNATURE_STATE and MERKLE_STATE truthfully.

Do not invent missing historical turn hashes. Mark unavailable exact transcripts RAW_EXPORT_REQUIRED.

## Phase 2 — Import project conversations

Target directory:

custody/conversations/
  raw/
  normalized/
  fco/
  manifests/
  PROJECT_CONVERSATION_IMPORT_MANIFEST.json
  PROJECT_CONVERSATION_ROOT.json

For each exported conversation:
1. save untouched raw export;
2. calculate raw_file_sha256;
3. normalize into deterministic JSONL without replacing the raw artifact;
4. calculate normalized_sha256;
5. create ConversationFCO;
6. create TurnFCOs for user/assistant/tool turns;
7. add HAS_TURN, NEXT_TURN, DERIVED_FROM, REFERENCES_ARTIFACT, PRODUCED, SUPERSEDES, and other justified FCG edges;
8. create a deterministic project-conversation manifest root over ordered conversation records;
9. do not call that root Merkle unless a real Merkle construction is run.

Exact ChatGPT export files are required for byte-exact historical custody. Summaries are evidence anchors, not substitutes for raw transcripts.

## Phase 3 — Compare the two HydraDB/project graph views

Graph A: hosted HydraDB GitHub connector graph (`app_source=github`) for repository-derived context.
Graph B: canonical HydraDG FCO/FCG project graph.

These are different graph projections and must not be asserted identical by default.

Create:
- scripts/export_hydradb_github_graph_snapshot.py
- scripts/export_project_fcg_snapshot.py
- scripts/compare_graph_hash_spaces.py
- eval/graph_comparison_20260820/GITHUB_CONNECTOR_SNAPSHOT.json
- eval/graph_comparison_20260820/PROJECT_FCG_SNAPSHOT.json
- eval/graph_comparison_20260820/HASH_COMPARISON.json
- eval/graph_comparison_20260820/GRAPH_COMPARISON_RECEIPT.json

Comparison rules:
- never compare GitHub blob SHA-1 directly to FCO SHA-256;
- calculate SHA-256 of exact repository file bytes when file-level equality is required;
- preserve GitHub blob IDs as a separate identifier namespace;
- compare canonical FCO object_sha256 values to the same SHA-256 values when those values are explicitly indexed in the GitHub-connected content;
- compare project FCG roots only to hosted projections created from the same canonical leaf/edge definition and ordering;
- do not require the generic GitHub connector graph root to equal the canonical project FCG root.

Report:
- github_graph_node_count
- github_graph_edge_count
- project_fco_count
- project_fcg_edge_count
- exact_sha256_intersection_count
- exact_sha256_intersection_root
- unique_to_github_graph_count
- unique_to_project_fcg_count
- duplicate_reference_hash_count
- conflicting_payload_same_hash_count (expected 0; if nonzero FAIL)
- project_fco_root
- project_fcg_edge_root
- github_connector_snapshot_root
- mapped_source_coverage_percent

Meaning of identical hash:
SAME_CANONICAL_IDENTITY only when the same canonical SHA-256 contract applies.

Meaning of duplicate occurrence:
SAME_IDENTITY_REFERENCED_MULTIPLE_TIMES, not a hash collision.

## Phase 4 — Website graph-comparison experience

Add a judge-visible `/graph-compare` page and link it from Graph, Evolution, Evidence, How-To, Why Graph, and breadcrumbs.

Display three sets:
- COMMON CANONICAL HASHES
- GITHUB-CONNECTOR-ONLY CONTEXT
- PROJECT-FCG-ONLY CUSTODY OBJECTS

Clicking a common hash must open:
1. canonical FCO inspector;
2. project FCG neighborhood;
3. GitHub source/file evidence;
4. hosted HydraDB query/readback evidence;
5. applicable source/KnowledgeAtom/SeedOfTruth path.

Use separate colors for equality class; do not use the Reference/Poison/Antidote state colors for graph-source equality.

## Phase 5 — Universal claim/term/source resolver

Goal: every project-specific term and every substantive numeric/factual claim on judge-facing pages should be clickable. Common prose words do not need links.

Maintain registries:
- KnowledgeTerm registry: term/aliases -> `/knowledge#slug`
- Claim registry: claim id -> evidence receipt/result/FCO
- Source registry: publication/model/dataset -> internal SourceFCO -> upstream URL
- Atom registry: claim/source -> KnowledgeAtom -> SeedOfTruth when admitted

Reusable components:
- KnowledgeTermLink
- ClaimLink
- SourceLink
- AtomTrail
- GlobalBreadcrumbs

Add a lint/release check that reports unresolved governed terms and claims on judge-facing pages.

Breadcrumb goal:
Overview > current page > evidence/term > FCO > atom/seed where available.

## Phase 6 — Fractal walkthrough

Add a highlighted walkthrough section titled `Why fractal custody?`.

Explain:
- an FCO is a content-addressed custody unit with its own canonical root/hash identity;
- an FCG is the governed relationship graph whose declared snapshot also has a root;
- a lower-level FCO/FCG root can become evidence inside a higher-level FCO;
- therefore source, atom, seed, state, experiment, hosted migration, conversation set, website release, and project release can each be independently hashed while remaining nested in one provenance chain;
- context, governance, and provenance repeat recursively across scales.

Suggested path:
Source root
  -> Evidence/Atom roots
  -> Seed root
  -> StateSnapshot root
  -> Experiment FCG root
  -> Hosted projection/readback receipt root
  -> Conversation-custody root
  -> WebsiteRelease FCO
  -> Final project FCG root

Do not say a root proves correctness.

## Phase 7 — Preprints and Hugging Face model

Register and link these research sources everywhere they are mentioned:
- Fractal Custody Objects — v4/v5 publication-version package with Vithia companion evidence — DOI 10.5281/zenodo.21829929
- Custody-Verified Classification of AI Model Outputs in a Self/Non-Self × Safe/Unsafe Matrix — DOI 10.5281/zenodo.21830287
- The Shadow Dogma: hypothesis and governed computational evidence package for fragment-inheritance aging models — DOI 10.5281/zenodo.21830361
- XenoDisorder: bounded PTM-aware disorder scoring with exact modified-row evidence and a standalone local software surface — DOI 10.5281/zenodo.21830386
- Hugging Face model: biobitworks/fco-vithia-fmo-076

For each source create/retain a SourceFCO with:
- title
- DOI/repo identifier
- authoritative license or upstream rights
- external URL
- source hash/manifest hash when locally retained
- claim ceiling
- relationship to Vithia/HydraDG where justified

Hugging Face model-card update:
- state that the research/model artifact is CC BY-NC-ND 4.0;
- identify any software utilities separately as Apache-2.0 where applicable;
- preserve upstream model/base rights;
- link HydraDG GitHub, live judge site, relevant preprints, FCO/FCG definitions, and release/evidence pages;
- add exact artifact hashes/FCO IDs only after verified;
- if the model remains gated, mark it SUPPLEMENTAL_GATED_MODEL and do not make judge readiness depend on unauthenticated model-file access.

## Phase 8 — T3/T4/T5 production metrics

Keep T0-T2 scientific distribution metrics separate from T3-T5 release/migration metrics.

T3 Hosted migration:
- canonical FCO delta
- edge delta
- content-hash delta
- root matches
- live database/collection discovery
- traceability readback

T4 Context vs Entropy:
- 18,555 / 18,567 context classified
- coverage
- abstention rate
- category-sum invariant

T5 Final release:
- exact deployed Git SHA
- WebsiteRelease FCO hash match
- canonical FCO identity validation
- build/typecheck/security/public-route/backend readback gates

G*/Cloud Drift stays N/A for T3-T5 unless a separately declared, frozen project-state distribution contract is created before interpretation.

## Phase 9 — Expected human updates from Byron

Required:
1. Export the HydraDG ChatGPT Project conversations as raw JSON/HTML/text files and place/upload them for import. Byte-exact historical hashing cannot be reconstructed from summaries.
2. Confirm which conversations are in scope if the export contains unrelated project chats.
3. For Hugging Face, either provide local repository access to Antigravity for a normal git push or manually apply the prepared model-card update. Current connector access is read-only.
4. Decide whether the gated Hugging Face model should stay gated. If gated, keep it supplemental; if judges must inspect files, grant access or change gating before submission.
5. Do not provide private API keys or private signing keys in chat/repository.
6. Approve the exact final integration SHA only after the comparison/import/license/link/security gates are green.

No human action should be required for:
- deterministic hashing of supplied raw exports;
- graph comparison computation after hosted readback is available;
- website link/claim registry construction;
- code/build/typecheck checks;
- generation of FCO/FCG receipts.

## Final gates

PASS required before final freeze:
- conversation raw-import manifest complete for all declared in-scope conversations;
- no invented historical hashes;
- license-policy audit PASS;
- software/research/third-party license boundaries explicit;
- graph A/B comparison receipt generated;
- identical/unique hash sets displayed with correct namespace semantics;
- no conflicting canonical payload for same FCO SHA-256;
- project FCO/FCG roots verified;
- hosted readback/traceability verified;
- preprint/model links resolve through internal SourceFCO/Knowledge navigation first;
- governed terms/claims link-lint PASS;
- breadcrumbs PASS;
- state calculation + Anticube consideration visible on node/FCO inspectors;
- typecheck PASS;
- production build PASS;
- exact-SHA release tests PASS;
- full-history Gitleaks PASS;
- public Vercel routes PASS;
- release SHA/API FCO identity PASS;
- SIGNATURE_STATE and MERKLE_STATE truthful.
