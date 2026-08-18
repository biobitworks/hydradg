# HydraDG

**Custody-aware persistent memory on HydraDB**

Hack Hydra 2026 — **Track 03: Memory + Context Retrieval**  
Secondary conceptual overlap: Track 01 — Enterprise Context + Ontology

HydraDG treats agent memory as a temporal evidence graph rather than a flat collection of messages or embeddings. It preserves where a state came from, what transformed it, what superseded it, and which current conclusions depend on earlier evidence.

## Submission links

- Public repository: `https://github.com/biobitworks/hydradg` — **must be independently confirmed public before submission**
- Live app: pending; deployment is optional for the backend proof
- 3-minute YouTube pitch/demo: **pending final recording**
- Stable demo route when deployed: `/demo`
- Interactive FCG route when deployed: `/graph`

Do not treat placeholders above as judge-accessible until the corresponding publication/access checks pass.

## What works now

The current Hack Hydra branch implements:

`source → evidence → KnowledgeAtom → FCO identity → FCG relationships → Seed of Truth → StateSnapshot → temporal mutation/restoration → HydraDB current/history/provenance queries → interactive 4D FCG`

The deterministic demo contains three temporal states:

1. reference;
2. synthetic mutation;
3. restoration/correction.

Each state is represented as an FCO and connected through explicit FCG relationships. The application can retrieve the current state, inspect supersession history, and traverse provenance back toward evidence.

## HydraDB use

HydraDB is the persistent graph backend for the Track 03 memory path. HydraDG stores deterministic numeric traversal addresses in HydraDB while retaining the complete SHA-256 `fco_id` and `object_sha256` as the canonical custody identity.

The HTTP adapter conforms to HydraDB's deliberately bounded OpenCypher mutation surface. For FCO materialization it uses an internal `INDEXES_FCO` storage edge; this is database scaffolding, not a semantic FCG relationship. Semantic FCG edges are written separately and retain their canonical `fcg_id` as graph metadata.

### Last fully green E2E receipt

GitHub Actions run **#28** / run id `32187451568` passed:

- TypeScript typecheck;
- Next.js production build;
- resumed FCO/FCG root recomputation;
- ephemeral Ed25519 sign/verify mechanism test;
- HydraDB container startup;
- direct HydraDB graph write/read round trip;
- HydraDG deterministic fixture admission;
- current-state query;
- history query;
- provenance traversal;
- `/`, `/demo`, `/graph`, `/eligibility` route checks;
- secret-pattern scan.

Recorded HydraDB image digest:

`sha256:db78309a233be54662db29744047e985a39b51c45a270d1a1f47c31a62cdb709`

E2E artifact digest:

`sha256:5c3acbbef4f266f32b1ba59f36d525e326fe04c5e31b9e9b62f52db5087b939b`

That successful run has been added back into the FCO/FCG custody graph as an execution receipt. Because adding evidence changes the graph root, the release branch must pass a final post-receipt CI run before freezing the submission commit.

## 4D FCG explorer

`/graph` presents the Fractal Custody Graph as a three-dimensional navigable projection plus an explicit time/version axis.

The user can:

- rotate with mouse or touch;
- zoom;
- move through time with a state slider;
- search visible FCOs;
- click a node to inspect its payload and custody metadata;
- view mutation, restoration, and `|ΔG*|` heat layers;
- use a toy lock/unlock interaction for demonstration nodes;
- use browser speech synthesis to hear a selected node.

The toy lock is **not production encryption or authorization**. Production key policy remains future work.

## Information-state field

HydraDG computes deterministic visualization metrics over declared state distributions:

- Shannon entropy `H(t)`;
- normalized entropy;
- total-variation mutation distance from a declared reference state;
- restoration gain;
- a declared dimensionless burden `U*(t)`;
- `G*(t) = U*(t) - τ H_norm(t)`;
- `ΔG*(t)` between successive states.

`G*` is a **dimensionless information-state abstraction inspired by information-theoretic free-energy inference**. It is not physical Gibbs free energy and must not be reported in kcal/mol, joules, or other physical units without a separately validated domain model.

Theory context: Enßlin & Weig, *Inference with minimal Gibbs free energy in information field theory*, arXiv:1004.2868 / DOI `10.1103/PhysRevE.82.051112`.

## Reused public work and boundaries

HydraDG distinguishes pre-existing reusable components from Hack-Hydra-specific implementation.

- **BioCustody** (`biobitworks/biocustody`, Apache-2.0 repository boundary): cross-device custody, device/model/agent lineage, transcript custody, claim-ceiling patterns, optional voice-interface precedent.
- **Protein Hinge** (`biobitworks/protein-hinge`, CC-BY-ND-4.0): cited/reference precedent for recompute-or-reject, first-divergence localization, and mutation-vs-record-repair tests. HydraDG independently implements generic mechanics and does not redistribute a modified Protein Hinge work under this source record.
- **FCO/FCG**: pre-existing custody framework used as a dependency; HydraDG's Hack Hydra contribution is the HydraDB-backed temporal memory implementation, query path, 4D state interface, experiments, and submission evidence.

See `config/public_source_registry.json` and `docs/FINAL_MVP_PLAN.md` for source and claim boundaries.

## Custody and signing state

A chat fork interrupted the intended per-turn custody process. The repository records that explicitly as a `CustodyGap`; missing historical hashes were **not fabricated or backfilled**.

Current resumed root convention:

`HYDRADG-FCG-RFC6962-v1`

The recovered signing design is retained:

1. include `PUBLIC_KEY.ed25519.pub` as a hashed leaf;
2. build `fcg_root`;
3. sign the hexadecimal root bytes with Ed25519;
4. store `FCG_ROOT.sig` outside the root;
5. verify the signature and the public-key fingerprint against an out-of-band anchor.

The author public-key bytes/private key are not present in GitHub CI. Therefore the current author-signature state is intentionally:

`PENDING_PUBLIC_KEY_LEAF_AND_AUTHOR_KEY`

CI verifies the signing mechanism with an ephemeral key labeled:

`EPHEMERAL_CI_KEY_NOT_AUTHOR_IDENTITY`

See `docs/CUSTODY_RESUME_AND_SIGNING.md`.

## Local/private-first run

For a Docker-capable host such as magicstudiobox:

```bash
bash scripts/magicstudiobox_mvp.sh
```

The script keeps HydraDB and Next.js bound to loopback by default, performs readiness and write/read checks, builds the web app, loads the deterministic fixture, tests current/history/provenance, checks the four judge-facing routes, and rebuilds the custody root.

Actual magicstudiobox execution must be reported separately; the existence of this script is not evidence that the host itself has already passed.

## Development

```bash
cd apps/hydradg-web
npm install
npm run typecheck
npm run build
npm run dev
```

Graph configuration is documented in `apps/hydradg-web/.env.example`. Never commit real secrets.

## Turn custody after the fork

Use exact visible-text files only:

```bash
python3 scripts/append_turn_custody.py \
  --human-file /path/to/visible_user_turn.txt \
  --assistant-file /path/to/visible_assistant_turn.txt \
  --model '<exact model/version if known>'
```

This uses the explicitly versioned `HYDRADG-TURN-RESUME-v1` convention, appends new FCO/FCG fragments, rebuilds the root, and only invokes author signing when the expected public key and local author private key are actually available.

## Claim ceiling

HydraDG can provide evidence about **identity, lineage, transformations, temporal state, and executed tests**. It does not make a statement true merely because the statement is hashed, placed in a graph, reproducible, or signed.
