# HydraDG MVP implementation plan

Status: IMPLEMENTATION_PLAN_ACTIVE
Branch: `hack-hydra/webapp-mvp-20260818`

## Goal

Build a Track 03 web application whose canonical knowledge path is:

`public source -> source/license gate -> SeedGraph total import -> atomization -> FCO -> Anticube atom classification -> Seed of Truth synthesis -> Anticube seed classification -> temporal drift graph -> review/red-team gates -> final FCG candidate -> explicit seal operation`

The final FCG is not called sealed, signed, Merkle-committed, or independently verified unless those operations actually execute and receipts verify.

## Non-negotiable admission policy

A scientific/content atom is admissible only when all of the following are present:

1. Public source: public preprint or public GitHub repository.
2. Exact source identifier: DOI/version or GitHub repository + commit/blob.
3. Source citation.
4. Source license identifier and license citation/URL.
5. Source bytes or a retrievable public representation sufficient to hash/replay the atom extraction.
6. Human authorship boundary for the source.
7. Extracting/transforming agent + model + provider + runtime/version when known.
8. Transformation/prompt/tool receipt sufficient to identify how the atom was derived.
9. Evidence class and claim ceiling.
10. Anticube classification receipt.

If any load-bearing dependency is absent, the atom is quarantined and cannot support a Seed of Truth.

## Canonical object types

### Source
Required fields:
- `source_id`
- `public_url`
- `source_type` (`PUBLIC_PREPRINT`, `PUBLIC_GITHUB`)
- `doi_or_repo`
- `version_or_commit`
- `source_sha256` when source bytes are available
- `license_id`
- `license_url`
- `license_evidence`
- `authors`
- `retrieved_at`

### KnowledgeAtom
Required fields:
- `atom_id`
- `canonical_text`
- `source_id`
- `source_locator` (page/line/blob range where possible)
- `evidence_class`
- `claim_ceiling`
- `extractor_agent_id`
- `extractor_model_id`
- `tool_action_ids[]`
- `transform_receipt_hash`
- `object_sha256`
- `admission_state`

### AnticubeClassification
Required fields:
- `classification_id`
- `subject_id` (atom or seed)
- `classifier_version`
- `classifier_agent_id`
- `classifier_model_id`
- `input_hash`
- `output_hash`
- `labels`
- `scores` when applicable
- `rationale_or_feature_receipt`
- `uncertainty`
- `claim_ceiling`

Anticube internals are not invented here. The MVP adapter must preserve the exact classifier contract recovered from a public source. Until then, classification objects remain `IMPLEMENTATION_PENDING_PUBLIC_CONTRACT`.

### SeedOfTruth
A Seed of Truth is a derived FCO supported by one or more admitted atoms. It is not automatically a scientific truth claim.

Required fields:
- `seed_id`
- `statement`
- `supporting_atom_ids[]`
- `contradicting_atom_ids[]`
- `synthesis_agent_id`
- `synthesis_model_id`
- `transform_receipt_hash`
- `evidence_class`
- `claim_ceiling`
- `object_sha256`
- `anticube_classification_id`

## Temporal/drift model

Every new classification or Seed of Truth revision is append-only.

Required graph relations:
- `DERIVED_FROM`
- `SUPPORTED_BY`
- `CONTRADICTS`
- `SUPERSEDED_BY`
- `CLASSIFIED_AS`
- `RECLASSIFIED_AS`
- `DRIFTED_FROM`
- `ADMITTED_AS`
- `REJECTED_AS`
- `CHALLENGED_AS`

For every atom/seed revision compute and store:
- source-set delta
- license delta
- text/content hash delta
- Anticube label delta
- Anticube score delta if scores exist
- claim-ceiling delta
- support/contradiction edge delta
- model/agent/version delta
- timestamp and parent state hash

## Public source reuse policy

### Reuse now
- Public FCO preprints for custody/content-addressing/signing/Merkle design where the relevant method is explicitly present in the public record.
- Public GitHub repositories only when the repository visibility is public and the exact reusable file license is known.
- Public-domain Vitalogy/Vitaology source material only when the specific source text/publication status is documented and the derived Vitaology material itself is publicly available under an explicit license.

### Do not use as source truth yet
- `biobitworks/gtm-cellico`: private governance/control-plane repository. Governance patterns may inform project management, but private-only scientific atoms are not admissible.
- `biobitworks/vitaology`: currently private in connected GitHub. Its atoms are not admissible merely because they exist there. Import only material independently available in a public preprint/public repository with license metadata.
- `biobitworks/fractal-custody-objects`: connected repository is private. Use corresponding public Zenodo publication objects or a public GitHub mirror/release when available.
- SeedGraph/Anticube implementations: source recovery required. Do not reconstruct hidden/private algorithms from memory and call them the canonical implementation.

## Task backlog

### P0 — provenance and licensing spine
- [ ] Define JSON schemas for `Source`, `LicenseEvidence`, `KnowledgeAtom`, `ModelInvocation`, `AgentSession`, `ToolAction`, `AnticubeClassification`, `SeedOfTruth`, `DriftObservation`, `ReviewDecision`, and `SealReceipt`.
- [ ] Add schema validation to CI.
- [ ] Implement public-source gate: reject/quarantine private-only or unresolved sources.
- [ ] Implement license gate: reject/quarantine atoms with no explicit license evidence.
- [ ] Implement model/agent lineage gate.
- [ ] Add deterministic canonical JSON + SHA-256 object IDs for every object.

Acceptance: an atom lacking public-source, license, or model/agent lineage fails closed and cannot be promoted.

### P0 — public source registry
- [ ] Build `config/public_source_registry.json`.
- [ ] Record DOI/version or GitHub commit for every source.
- [ ] Record license metadata independently of atom text.
- [ ] Resolve public SeedGraph source.
- [ ] Resolve public Anticube source/contract.
- [ ] Resolve public Vitaology artifacts before importing Vitaology-derived atoms.
- [ ] Resolve current public FCO version(s) used by the MVP.

Acceptance: every admitted atom references exactly one registered source/version and one registered license assertion.

### P0 — SeedGraph total import
- [ ] Define import bundle format: source bytes/metadata + atoms + source locators + licenses + extraction receipts.
- [ ] Import entire selected public artifacts, not cherry-picked claims, so missing context is detectable.
- [ ] Deduplicate by content hash while retaining multiple source/provenance edges.
- [ ] Preserve source document hierarchy and source-order relationships.
- [ ] Emit deterministic import manifest with counts and SHA-256 hashes.

Acceptance: same public source/version ingested twice produces identical canonical source/atom IDs.

### P0 — simulated key lane
- [ ] Implement an explicitly labeled `SIMULATED_DEMO_KEYPAIR` fixture for UI/demo testing.
- [ ] Never call the demo private key a production key.
- [ ] Store only a deterministic demo fixture/private-key surrogate in test fixtures if needed; never mix it with real signer identity.
- [ ] Generate signature-like demo receipts only under `SIMULATED_SIGNATURE` state.
- [ ] Separately support real Ed25519 signing when an actual key operation is invoked.

Acceptance: UI and manifests visibly distinguish `SIMULATED_SIGNATURE` from `VERIFIED_ED25519_SIGNATURE`.

### P0 — Anticube atom classification
- [ ] Pin public Anticube classifier contract/version.
- [ ] Add adapter interface and exact input/output receipt hashing.
- [ ] Classify every admitted atom.
- [ ] Store classification provenance, model/agent identity, uncertainty, and version.
- [ ] Quarantine atoms whose classifier execution fails rather than fabricating a label.

Acceptance: 100% of promoted atoms have one current Anticube classification and retain all prior classifications append-only.

### P1 — Seeds of Truth
- [ ] Group compatible admitted atoms by semantic subject while retaining source independence.
- [ ] Synthesize candidate Seed of Truth statements.
- [ ] Record supporting and contradicting atoms.
- [ ] Enforce claim ceiling = no stronger than weakest load-bearing evidence.
- [ ] Run Anticube classification on every candidate seed.
- [ ] Reject seed promotion if supporting provenance is incomplete.

Acceptance: every seed can be traversed backward to public source/license bytes and forward to its Anticube receipt.

### P1 — drift engine
- [ ] Version atom and seed classifications over time.
- [ ] Compute classification drift and source/support drift.
- [ ] Add `DRIFTED_FROM`, `SUPERSEDED_BY`, and `CONTRADICTS` edges.
- [ ] Expose first divergence and downstream affected set in HydraDB.
- [ ] Add timeline UI.

Acceptance: changing a source, classifier version, model, or support edge creates a new state; the old state remains reconstructable.

### P1 — HydraDB storage/query
- [x] Pin HydraDB upstream commit for initial web branch.
- [x] Implement server-side HydraDB HTTP query adapter.
- [x] Keep optional Neo4j/Aura Bolt adapter for development compatibility.
- [ ] Implement SeedGraph bundle ingest into HydraDB.
- [ ] Implement current-state query.
- [ ] Implement historical-state query.
- [ ] Implement evidence/license path query.
- [ ] Implement drift/affected-set query.
- [ ] Implement fail-closed abstention when evidence path is missing.

### P1 — web application
- [x] Scaffold Next.js MVP branch.
- [x] Add graph query API and status surface.
- [x] Add Exa retrieval path with optional admission.
- [ ] Add Source Registry page.
- [ ] Add Import/Atomization page.
- [ ] Add Atom Inspector: source, license, hash, model/agent, Anticube result.
- [ ] Add Seed of Truth Inspector.
- [ ] Add Drift Timeline.
- [ ] Add FCG graph/evidence-path visualization.
- [ ] Add Review/Red-Team queue.
- [ ] Add Seal Candidate page with explicit custody state.

### P2 — evaluation
- [ ] LongMemEval-S smoke80 development run.
- [ ] Full500 only after graph/query policy freezes.
- [ ] Separate injected perturbation/recovery suite.
- [ ] A-D ablation: flat/vector vs HydraDB vs provenance vs full HydraDG.
- [ ] Report latency, context tokens, storage/ingest overhead separately from accuracy.

## Definition of MVP-ready

MVP is ready for review when:
1. public-source and license gates fail closed;
2. SeedGraph total import is deterministic;
3. every promoted atom has provenance + license + model/agent receipt + Anticube classification;
4. every promoted Seed of Truth is traceable to atoms and is Anticube-classified;
5. drift can be reconstructed across at least two graph states;
6. HydraDB can answer current, historical, evidence-path, and drift queries;
7. simulated key state cannot be confused with a real cryptographic signature;
8. red-team suite passes;
9. no final seal claim is emitted before an executed seal operation.
