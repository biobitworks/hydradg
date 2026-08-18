# magicPRObox / Modal runbook

Run from `HydraDG_DaisyTrain_v0.3.1`.

## 0. Verify the package

```bash
cd /Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.1
shasum -a 256 -c SHA256SUMS.txt
python scripts/verify_package.py
modal token info
```

Do not rerun Modal authentication if the token is already valid. Do not paste token secrets into evidence artifacts.

## 1. CAR 1B — ECA-EXT80

Quick canary:

```bash
modal run modal/modal_eca_extension.py --quick
```

Full 80:

```bash
modal run modal/modal_eca_extension.py
mkdir -p eval/eca
modal volume get hydradg-eca-extension-v031 /runs/eca_extension_80.json \
  eval/eca/eca_extension_80.json --force

python scripts/validate_eca_extension.py \
  eval/eca/eca_extension_80.json

python scripts/render_eca_figures.py \
  eval/eca/eca_extension_80.json \
  --outdir figures/generated
```

Then emit a stage receipt:

```bash
python scripts/daisy_receipt.py \
  --stage CAR-1B-ECA-EXT80 \
  --input modal/modal_eca_extension.py \
  --output eval/eca/eca_extension_80.json \
  --receipt receipts/CAR-1B-ECA-EXT80.json \
  --claim-ceiling BOUNDED_DETERMINISTIC_CONFORMANCE
```

## 2. CAR 1A — locate the historical ECA source

```bash
bash scripts/locate_historical_eca_source.sh \
  /Users/byron/projects/active/fractal-custody-objects
```

This step is source recovery only. Do not rewrite the old Markov/Bayesian detector from a preregistration and call that a historical replication.

## 3. CAR 2 — freeze XenoDisorder inputs

Expected historical evaluator source commit for the harness path:

`abd696baa2065af3b3ee0dac5e12152c94745d4e`

```bash
FCO=/Users/byron/projects/active/fractal-custody-objects
mkdir -p inputs/xeno

git -C "$FCO" show \
  abd696baa2065af3b3ee0dac5e12152c94745d4e:training/cafa6_governed_eval.py \
  > inputs/xeno/cafa6_governed_eval.py

cp "$FCO/scratchpad/cafa6_exp2_out/ckpt_latest.pt" \
  inputs/xeno/ckpt_latest.pt

cp "$FCO/scratchpad/cafa6_governed_eval_data/residual_table.jsonl" \
  inputs/xeno/residual_table.jsonl
```

Search the local repository/history for the exact evaluator invocation:

```bash
bash scripts/locate_xeno_command.sh "$FCO"
```

Create `inputs/xeno/run_contract.json` from `config/xeno_run_contract.template.json`.
The `argv` must be the exact command you choose to freeze. Do not guess flags.

Freeze and preflight:

```bash
python scripts/freeze_xeno_assets.py \
  --harness inputs/xeno/cafa6_governed_eval.py \
  --checkpoint inputs/xeno/ckpt_latest.pt \
  --table inputs/xeno/residual_table.jsonl \
  --contract inputs/xeno/run_contract.json \
  --out eval/xeno_asset_freeze.json

python scripts/preflight_xeno_assets.py \
  --manifest eval/xeno_asset_freeze.json
```

Run the frozen contract locally first:

```bash
python scripts/run_xeno_contract.py \
  --manifest eval/xeno_asset_freeze.json \
  --mode local \
  --out eval/xeno_local_receipt.json
```

Upload exactly the frozen four files:

```bash
modal volume create hydradg-xeno-cafa6-input-v031 || true
modal volume put hydradg-xeno-cafa6-input-v031 inputs/xeno/cafa6_governed_eval.py /cafa6_governed_eval.py
modal volume put hydradg-xeno-cafa6-input-v031 inputs/xeno/ckpt_latest.pt /ckpt_latest.pt
modal volume put hydradg-xeno-cafa6-input-v031 inputs/xeno/residual_table.jsonl /residual_table.jsonl
modal volume put hydradg-xeno-cafa6-input-v031 inputs/xeno/run_contract.json /run_contract.json
```

Run Modal:

```bash
modal run modal/modal_xenodisorder_cafa6_replay.py
mkdir -p eval/xeno_modal
modal volume get hydradg-xeno-cafa6-output-v031 /run/xeno_modal_receipt.json \
  eval/xeno_modal/xeno_modal_receipt.json --force
```

Compare:

```bash
python scripts/compare_xeno_receipts.py \
  eval/xeno_local_receipt.json \
  eval/xeno_modal/xeno_modal_receipt.json \
  --out eval/xeno_modal_comparison.json
```

Claim rule:
- identical frozen input hashes + same command + matching metrics may support a bounded same-assets cross-environment replay statement;
- it is a historical reproduction only if the frozen assets/command are themselves shown to be the historical objects.

## 4. CAR 3 — import Vithia/Pythia evidence

Copy the already-executed v0.2.7 result artifact into:

```text
inputs/vithia/MODAL_FULL_PHASE_RESULT_v0.2.7.json
```

Do not reconstruct the original receipt from prose if the original artifact is available.

## 5. CAR 4 — normalize FCO/FCG

```bash
python scripts/build_fco_fcg_import.py \
  --artifact eval/eca/eca_extension_80.json \
  --artifact eval/xeno_modal_comparison.json \
  --artifact inputs/vithia/MODAL_FULL_PHASE_RESULT_v0.2.7.json \
  --outdir hydra/import
```

Validate:

```bash
python scripts/validate_fco_fcg_import.py hydra/import
```

## 6. CAR 5 — pin HydraDB before adapter work

Record:
- HydraDB commit SHA
- build/runtime version
- exact client/API used
- schema mapping

in `config/hydradb_pin.json`.

Only after that file is real should an adapter invoke HydraDB. The current package intentionally does not invent an API surface.

## 7. CAR 6 — LongMemEval-S smoke80

```bash
python scripts/download_verify_longmemeval.py \
  --out data/longmemeval_s_cleaned.json

python scripts/build_longmemeval_smoke80.py \
  data/longmemeval_s_cleaned.json \
  --out data/longmemeval_smoke80.json \
  --manifest eval/longmemeval_smoke80_manifest.json
```

Run smoke80 through all four A-D ablations. Debug only on smoke80.

## 8. CAR 7 — full500

After graph construction/query/scoring code is frozen:

```bash
# run all 500 official cases using exactly the frozen A-D configurations
```

Never mix ECA/Xeno/Vithia observations into the official LongMemEval denominator.

## 9. CAR 8 — scorecard

Fill `eval/track03_results.json` using `config/evaluation_schema.json`, then:

```bash
python scripts/score_track03.py \
  eval/track03_results.json \
  --out eval/TRACK03_SCORECARD.md
```

The main headline should be the official LongMemEval result plus clearly separated
HydraDG provenance/divergence/recovery metrics.
