# HydraDG — Final Hack Hydra MVP Plan

Status date: 2026-08-18
Primary track: **03 — Memory + Context Retrieval**
Secondary conceptual overlap: **01 — Enterprise Context + Ontology**

## Release thesis

HydraDG is a custody-aware temporal memory layer on HydraDB. The submission should demonstrate a working path, not a slide-only architecture:

`source → evidence → KnowledgeAtom → FCO identity → FCG edges → Seed of Truth → StateSnapshot → temporal mutation/restoration → current/history/provenance retrieval → interactive 4D view → custody receipt`

The judging claim is narrow: HydraDG makes changing context inspectable and queryable while preserving lineage. It does not claim that custody proves factual correctness, safety, scientific validity, or physical thermodynamics.

## P0 — must pass before release

1. **HydraDB-native backend**
   - Boot the published HydraDB container.
   - Use the pinned OpenCypher compatibility contract.
   - Round-trip a direct write/read.
   - Load the deterministic HydraDG fixture through the app API.
   - Verify current state, history, and provenance.

2. **FCO/FCG custody**
   - SHA-256 FCO identity remains canonical.
   - HydraDB numeric vertex ids are addressing adapters only.
   - Source/model/agent/device/tool metadata stays inspectable.
   - Claim ceilings are stored with each object.
   - The chat-fork hashing lapse remains a first-class `CustodyGap`; do not backfill unverifiable hashes.

3. **Temporal state**
   - Demonstrate three fixture states: reference → mutation → restoration.
   - Store each state as a `StateSnapshot` FCO.
   - Preserve `SUPERSEDED_BY` and `TRANSITIONS_TO` relationships.

4. **4D FCG explorer**
   - `/graph` must be usable with mouse and touch.
   - x/y/z = deterministic graph-space projection.
   - t = explicit snapshot/version index.
   - Node click opens the FCO inspector.
   - Time slider filters graph history.
   - Toy lock/unlock is labeled demonstration-only and must never be described as production encryption.

5. **Information-state layer**
   - Shannon entropy `H(t)` is computed from declared state distributions.
   - `U*(t)` is a dimensionless declared perturbation/inconsistency burden.
   - `G*(t) = U*(t) - τ H_norm(t)` is a project abstraction inspired by information-theoretic free-energy inference.
   - `ΔG*`, mutation distance, and restoration gain are deterministic transforms.
   - Never report these as kcal/mol, joules, or physical Gibbs free energy without a separately validated physical model.

6. **Public-safe release**
   - No API keys, passwords, private keys, PHI, or private-only source content.
   - Public source/license registry is complete enough for every surfaced external source.
   - README states pre-existing dependencies versus Hack Hydra-specific development.

## Reused public mechanics, with boundaries

### BioCustody

Public repo: `biobitworks/biocustody` (Apache-2.0 repository boundary).

Reusable mechanics:
- cross-device FCO aggregation;
- explicit device/model/agent lineage;
- per-turn transcript custody;
- deterministic/probabilistic/creative claim-ceiling separation;
- voice narration as an optional interface layer.

HydraDG does not import BioCustody provider outputs or third-party evidence under the repository license.

### Protein Hinge

Public repo: `biobitworks/protein-hinge` (CC-BY-ND-4.0).

HydraDG uses this repo as a cited/reference source for independently implemented generic mechanics:
- recompute-or-reject;
- first-divergence localization;
- byte mutation vs record-repair tamper-test distinction;
- separation of scientific evidence from legal/FTO conclusions.

No modified Protein Hinge material is distributed as part of HydraDG under this source record.

### Enßlin & Weig

Public preprint: arXiv:1004.2868; DOI: 10.1103/PhysRevE.82.051112.

Used as theory context for information-state free-energy inference. HydraDG stores bibliographic metadata and original paraphrases, not a re-licensed copy of the paper.

## P1 — submission-visible, but not backend blockers

- browser speech synthesis for selected-node accessibility;
- optional ElevenLabs/Vapi voice adapters if credentials are available;
- optional local/BYOM Ollama-compatible model for conversational graph queries;
- optional Exa retrieval after source admission;
- live app deployment on Vercel/Sauna/magicstudiobox.

The MVP must remain useful without any frontier-model API.

## P2 — post-hackathon

- production key management/KMS/HSM;
- hardware-backed device attestation;
- real authorization policy for private FCO payloads;
- benchmarked semantic search/vector index;
- full Anticube contract once its public implementation/spec is pinned;
- production voice provider routing;
- broader SOC 2/NIST/ISO/CSA TRAITS crosswalk;
- domain-specific physical energy models where physical units are actually justified.

## Signing / sealing release gate

The recovered FCO/FCG design is retained:

1. Build the content-addressed FCG root.
2. The actual `PUBLIC_KEY.ed25519.pub` is a hashed leaf.
3. Sign the hexadecimal `fcg_root` bytes with Ed25519.
4. `FCG_ROOT.sig` is stored beside the root and is **not** folded back into the root.
5. Verify with the public key.
6. Identity attribution requires checking the public-key fingerprint against an out-of-band anchor.

Current author-signature state remains `PENDING_PUBLIC_KEY_LEAF_AND_AUTHOR_KEY` until the public-key bytes are imported from the author-controlled host and the author key performs the signature. CI may use an ephemeral key only to test the signature mechanism; such a receipt must say `EPHEMERAL_CI_KEY_NOT_AUTHOR_IDENTITY`.

## Go / no-go

**GO** only if:
- HydraDB direct write/read passes;
- app fixture write passes;
- current/history/provenance pass;
- `/`, `/demo`, `/graph`, `/eligibility` render;
- custody root recomputes;
- signature mechanism verifies with an ephemeral CI key;
- no secrets are found;
- public repository and YouTube links are accessible before form submission.

**NO-GO** if the demo depends on unavailable paid APIs, graph writes require manual database edits, any signing/sealing state is falsely promoted, or private-only evidence is represented as public.
