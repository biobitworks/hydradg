# HydraLamp × Runtype — Live Multi-Model Custody Experiment (2026-08-26)

**Branch:** `hack-hydra/hydralamp-20260826`  
**Claim ceiling (until live Runtype execution):** `PREREGISTERED_RUNTYPE_HYDRALAMP_DEMO_DESIGN`  
**Synthetic fixture:** yes — **not** a real security incident  

## What the 20-second experiment demonstrates

A frozen reference FCG is perturbed in exactly one preregistered dependency. Two–three Runtype agents receive the same prompt, tools, and limits. Their tool paths may diverge. A **deterministic verifier** (not an LLM) decides PASS/FAIL/NULL/ABSTAIN/TIMEOUT/ERROR, then custody appends Experiment/Agent/Verification/Result FCOs. HydraDB is projection-only.

Judge line: **Models propose. Custody decides.**

## Deterministic vs probabilistic vs synthetic

| Layer | Class |
|-------|-------|
| Fixtures + Ed25519 toy verify + tools + verifier + FCG hashing | `DETERMINISTIC_TOOL_OUTPUT` / synthetic fixture |
| Runtype model generations | `PROBABILISTIC_MODEL_OUTPUT` |
| Tavily/etc. (not used in this tiny demo) | `EXTERNALLY_RETRIEVED_EVIDENCE` |
| Verified empirical promotion | **not** claimed by this demo |

## Toy crypto

- Key label: `TOY_DEMO_KEY`
- Authenticity: `NO_REAL_AUTHENTICITY_CLAIM`
- SHA-256 = byte identity only
- Ed25519 = verification of this toy operation only
- Real HydraLamp identity is **not** established by the toy demo

## Runtype provides

Agent/model execution, optional streaming, execution IDs, local/runtime tools pause-resume.

Requires server-side `RUNTYPE_API_KEY` (never browser/logs).

If absent: `RUNTYPE_STATE=NOT_CONFIGURED`. A clearly labeled **SYNTHETIC UI FIXTURE** may exercise the visual path; it is **not** a live Runtype demo.

## HydraLamp provides

Fixture custody neighborhood, four deterministic tools, concurrent experiment coordinator, SSE event stream, `/hydralamp` + `/hydralamp?demo=20s` visualization, FCG append receipts, HydraDB projection intent.

## Tools (models select; tools are deterministic)

1. `inspect_state` — read-only  
2. `trace_divergence` — earliest divergent dependency  
3. `verify_actor_proof` — VALID/INVALID/MISSING/REPLAYED/MALFORMED  
4. `attempt_repair` — ephemeral candidate only; **no canonical write**

`MAX_TOOL_CALLS=6`, model deadline ≈ 10s.

## FCO/FCG append order

After verification only:

`SyntheticFixtureFCO → ExperimentFCO → AgentExecutionFCOs → ProbabilisticOutputFCOs → DeterministicVerificationFCO → ResultFCO → HypothesisFCO`

## HydraDB

Canonical FCG append first. Projection/readback second. Projection failure does not roll back FCG. UI shows PROJECTED only with readback receipt.

## Reproduce

```bash
cd apps/hydradg-web
# Place key in gitignored .env.local (never commit / never paste into chat):
# RUNTYPE_API_KEY=
npx tsx scripts/discover_runtype_inventory.mts
npx tsx scripts/run_live_control_invalid.mts
npm run dev
# open /hydralamp and RUN LIVE EXPERIMENT
# or /hydralamp?demo=20s
```

Without the key:

```bash
# UI button SYNTHETIC UI FIXTURE — labeled, not live
# Live scripts exit with RUNTYPE_STATE=NOT_CONFIGURED
```

Active architecture is **inside** `biobitworks/hydradg` (`/hydralamp`). The standalone `biobitworks/hydralamp` repo is archived/reference-only — do not migrate or merge it mechanically.

## Record video

```bash
scripts/record_hydralamp_20s_demo.sh
```

Uses Chrome headless if available (no Playwright dependency). Writes under `artifacts/hydralamp/<run-id>/` with `VIDEO_SHA256.txt` when capture succeeds.

## Known limitations

- `PROJECT_CONTROL.yaml`, root `FCO_SCHEMA.json` / `FCG_SCHEMA.json`, `CLAIM_CEILINGS.md`, `EVIDENCE_LEVELS.md`, `SIGNING_AND_KEYS.md`, `FCO_FCG_CANONICAL_SPEC.md` were **not present** in this checkout (recorded, not invented).
- Live Runtype multi-model inventory requires `RUNTYPE_API_KEY`.
- No fake-success fallback.
- Signature/Merkle states remain `NOT_SIGNED` / `NOT_COMMITTED` unless separately established.

## Authority files read

- `AGENTS.md`
- `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md`
- Existing `hydralamp/*`, `/hydralamp` page, `lib/fco.ts`
