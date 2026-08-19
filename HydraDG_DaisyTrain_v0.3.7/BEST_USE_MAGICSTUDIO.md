# Hack Hydra — Best Use v2 on magicSTUDIO

Status: `LOCAL_TEST_SURFACE_IMPLEMENTED / REMOTE_MAGICSTUDIO_EXECUTION_REQUIRED`

This surface tests graph-native memory and evidence traversal against the pinned HydraDB source commit:

`6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219`

It preserves the failed v1 lexical-relation experiment and introduces v2 typed memory objects:

- `Project -> HAS_CASE -> Case -> CONTAINS -> Session`
- `Session -> NEXT/PREV -> Session`
- `Session -> MENTIONS -> Entity`
- `Session -> ASSERTS -> Fact`
- `Fact -> DERIVED_FROM -> Session`
- `Fact -> ABOUT -> Entity`
- `Fact -> SUPERSEDED_BY -> Fact`
- `Fact <-> CONTRADICTS <-> Fact`

## Identity fix from real CI failure

The first live HydraDB CI run built and started the pinned server successfully, then failed at ingest because the v1 graph used `(question_id, external_session_id)` as Session identity. LongMemEval can contain the same external `session_id` at different positions, creating conflicting `position` metadata on one vertex.

v2 uses:

`SessionOccurrence = (question_id, external_session_id, occurrence_position)`

The external session ID remains a property used for benchmark scoring. The CI failure remains evidence and is not rewritten as a pass.

## Start locally on magicSTUDIO

From the HydraDG repository:

```bash
cd /Users/byron/projects/active/hydradg
git fetch origin
git switch hackhydra/best-use-stats-20260818
git pull --ff-only origin hackhydra/best-use-stats-20260818

bash HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh start
```

First start may compile HydraDB and download the official LongMemEval-S source. Mutable runtime state is written under:

`~/.local/share/hydradg-best-use/`

The launcher verifies the known source SHA-256 before creating deterministic smoke80.

Open:

`http://127.0.0.1:8787/`

### Optional Ollarma extraction

Default extraction is the deterministic, narrow `heuristic` lane so HydraDB can be tested without a model.

If `ollarma serve` is already healthy on `127.0.0.1:8484`, select `ollarma` in the UI/API to build model-extracted Entity/Fact/SUPERSEDES/CONTRADICTS objects. Ollarma outputs are typed as probabilistic model outputs and cached with source/prompt/response hashes. No provider secret is read or printed by HydraDG.

To default to a specific local Ollarma model:

```bash
BEST_USE_EXTRACTOR=ollarma BEST_USE_MODEL=qwen3:1.7b \
  bash HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh restart
```

### Control commands

```bash
bash HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh status
bash HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh smoke
bash HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh structural
bash HydraDG_DaisyTrain_v0.3.7/scripts/best_use_magicstudio.sh stop
```

### Remote view from magicPRObox

Keep the test UI localhost-only and tunnel it:

```bash
ssh -N -L 18787:127.0.0.1:8787 magicstudio
```

Then open `http://127.0.0.1:18787/` on magicPRObox.

## Local server endpoints

- `GET /health` — HydraDB/Ollarma/data state; never returns the bearer token.
- `GET /cases?limit=20` — bounded smoke80 case list.
- `GET /graph/stats` — graph counts when supported by the pinned query surface.
- `POST /case/load` — ingest one case with `none`, `heuristic`, or `ollarma` extraction.
- `POST /retrieve` — A/B/C/D retrieval with path reasons.
- `POST /extract` — inspect bounded extraction output before ingest.
- `POST /cypher` — read-only `MATCH/RETURN/CALL/WITH` surface for traversal inspection.

## Fast structural gate

`best_use_structural_suite.py` deliberately contains duplicate external session IDs and requires HydraDB to verify:

1. distinct session-occurrence vertices;
2. exact Case→CONTAINS provenance membership;
3. SUPERSEDED_BY traversal from Oakland to San Francisco;
4. CONTRADICTS traversal to the changed fact;
5. context-scoped semantic node identity across two cases.

This gate is synthetic structural conformance, not LongMemEval performance.

## Benchmark route

After the structural gate passes:

```bash
R="$HOME/.local/share/hydradg-best-use"
python3 HydraDG_DaisyTrain_v0.3.7/scripts/run_best_use_typed_longmemeval.py \
  "$R/data/longmemeval_smoke80.json" \
  --token-file "$R/hydradb-auth-token" \
  --extractor heuristic \
  --k 5 \
  --out "$R/eval/best_use_typed_smoke80.jsonl"

python3 HydraDG_DaisyTrain_v0.3.7/scripts/analyze_best_use_ablation.py \
  "$R/eval/best_use_typed_smoke80.jsonl" \
  --out "$R/eval/best_use_typed_smoke80_stats.json" \
  --expected-n 80 \
  --bootstrap 5000
```

Smoke80 remains `DEVELOPMENT_SMOKE_ONLY`. The final LongMemEval result requires the frozen full500 route.

## Custody boundary

- local token: generated locally, `chmod 600`, never written to Git or receipts;
- server receipts: append-only hash-linked JSONL, but **not an MMR**;
- source/result hashes: content identity only;
- Ollarma extraction: probabilistic model output, not empirical truth;
- signature: `NOT_SIGNED` unless an actual signing operation is separately performed;
- Merkle/MMR: `NOT_MERKLE_COMMITTED` unless separately performed;
- current claim ceiling before MagicStudio run: `IMPLEMENTED_AND_CODE_REVIEWABLE / LOCAL_EXECUTION_REQUIRED`.
