# Context Iceberg 4D Release Watch — 2026-08-19

## Purpose

HydraDG's release UI now translates the FCO/FCG into a navigable spacetime field rather than a linear progress/status bar.

The visualization is a **read-only projection** of custody state. It is not the custody source of truth and it does not mutate the active Daisy scientific lane.

## Visual contract

The hero encodes four navigation dimensions:

- **x / y / z** — deterministic graph-space coordinates for FCO objects;
- **t** — graph-state / Daisy-chain time.

Every visible FCO may carry a context envelope:

- **halo width / cloud size** = `cloud_drift_0_100`;
- **halo hue** = sign/direction of `delta_g_star`;
- **warm hue** = `ΔG* > 0` (`HIGHER`);
- **cool hue** = `ΔG* < 0` (`LOWER`);
- **neutral violet** = `ΔG* ≈ 0` (`STABLE`).

These colors are deliberately **not success/failure colors**. A lower ΔG* does not imply better accuracy and a larger Cloud Drift does not imply a worse result.

Primary retrieval outcomes remain independent:

- `delta_hit_at_k`;
- `delta_recall_at_k`.

## Context Iceberg mathematics

The v1 release visualization implements the supplied Context Iceberg specification:

`CloudDrift = 100 × JSD(p_t || p_ref)`

with base-2 Jensen-Shannon divergence, bounded to `[0, 100]` after scaling.

`ΔG*` remains the signed change in the separately preregistered dimensionless information-state abstraction.

The Release Watch code **does not select or change G* weights**.

### Gibbs / information-theory lineage

The primary upstream reference for using Gibbs-free-energy language as an information/inference quantity is:

> Torsten A. Enßlin and Cornelius Weig. **Inference with minimal Gibbs free energy in information field theory.** *Physical Review E* 82, 051112 (2010). DOI: `10.1103/PhysRevE.82.051112`. arXiv: `1004.2868`.

Enßlin & Weig connect information field theory to a minimal Gibbs-free-energy principle and information/cross-information objectives. HydraDG uses that work as **conceptual/mathematical lineage for the Gibbs-information analogy**, not as evidence that HydraDG's application-defined `G*` is thermodynamic Gibbs free energy or the paper's objective verbatim.

HydraDG's current `G*` / `ΔG*` therefore has the following claim boundary:

- **supported analogy:** information-state/free-energy constructions can combine entropy/information terms and an energy/cost-like term;
- **HydraDG-specific deterministic transform:** the exact `G*` scorer, burden terms, weights, buckets, and reference state are project-defined/preregistered objects;
- **not established:** physical units, thermodynamic work, biological kcal/mol, or accuracy improvement from lower `G*`.

Separate references govern separate pieces of the display:

- Shannon (1948) → Shannon entropy;
- Lin (1991) → Jensen-Shannon divergence / Cloud Drift lane;
- Enßlin & Weig (2010) → Gibbs-information-field inference lineage;
- Friston (2010) → secondary variational/free-energy background, not a substitute for the Enßlin & Weig source.

## Object-level interpretation

`context_drift` is allowed on every scene node, regardless of FCO level:

- Source;
- Evidence;
- KnowledgeAtom;
- SeedOfTruth;
- StateSnapshot;
- future dataset/case/session/turn atoms;
- future experiment/statistic/result/release objects.

If an object supplies its own validated `context_drift`, the UI uses it.

If it does not, the UI inherits the drift envelope for the object's state/time index. This means the fallback visual says **"this object existed in this context cloud"**, not **"this object alone caused this amount of drift"**.

A future scientific lane may emit per-object attribution only after a separate attribution method is preregistered and validated.

## Live update path

The local web server polls:

`GET /api/iceberg`

approximately every 3.5 seconds.

Source behavior:

1. If `HYDRADG_ICEBERG_STATE_PATH` points to a valid JSON artifact, `/api/iceberg` reads that artifact read-only.
2. If no live artifact is configured, it returns the deterministic synthetic reference → mutation → restoration fixture.
3. Invalid live state fails closed as `BLOCKED_INVALID_ICEBERG_STATE`.

The route does not write HydraDB or active scientific artifacts.

The intended production order remains:

`canonical custody → canonical FCG → HydraDB projection → Iceberg state artifact → read-only UI`

The `HYDRADG_ICEBERG_STATE_PATH` artifact is therefore a release projection/handoff, not the scientific source of truth.

## Daisy-chain handoff

At the end of each stable Daisy gate, the active execution lane can write/update one artifact matching:

`schemas/context_iceberg_state.schema.json`

The artifact should carry, where available:

- project FCG root;
- HydraDB projection root;
- signature state;
- Merkle state;
- ordered timeline states;
- frozen context distribution per state;
- G* and ΔG* from the preregistered scorer;
- primary outcome deltas;
- FCG scene nodes/links;
- optional node-level drift envelopes;
- claim ceiling.

Release Watch then displays the new state automatically without altering the experiment.

## Claim boundaries

Current visualization claims are bounded to:

- deterministic UI computation of JSD/Cloud Drift from the supplied distribution state;
- read-only display of supplied G*/ΔG* and outcome metrics;
- evidence-linked visualization of the declared scene graph.

It does **not** establish:

- physical Gibbs free energy;
- causal attribution of drift to a node merely because the node has a halo;
- retrieval improvement;
- canonical scientific validation;
- signature or Merkle commitment unless corresponding receipts exist.

## Synthetic fallback

Until a validated live state artifact is configured, the hero is explicitly labeled:

`DETERMINISTIC SYNTHETIC TEST FIXTURE`

with claim ceiling:

`SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY`

No synthetic accuracy or recall delta is fabricated; those values render as `PENDING`.

## Local validation gate

On `magicSTUDIObox`, after syncing this branch:

```bash
cd /Users/byron/projects/active/hydradg
npm --prefix apps/hydradg-web run typecheck
npm --prefix apps/hydradg-web run build
python3 scripts/check_term_knowledge_coverage.py
python3 scripts/check_static_fallback.py
python3 scripts/hash_release_artifacts.py
```

Then start the local server and verify:

- homepage canvas renders;
- drag rotates x/y/z;
- wheel/pinch zooms;
- time scrub changes visible graph state;
- play cycles through states;
- latest follows live artifact updates;
- halo size changes with Cloud Drift;
- warm/cool/neutral hue follows signed ΔG* without success/failure labels;
- selected object shows its claim ceiling and drift envelope;
- `/api/iceberg` is read-only and exposes no local source path;
- synthetic fallback is clearly labeled when no live state is configured.

Do not mark the website build or release batch green until those local checks actually pass.
