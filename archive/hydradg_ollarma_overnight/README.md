# HydraDG Ollarma Overnight Daisy Train

This package implements a bounded overnight Vithia/Pythia local training queue for
`magicstudiobox`.

## Execution boundary

- Training is performed by the existing HydraDG PyTorch fixture:
  `scripts/vithia_divergence_core.py`.
- Ollarma (`127.0.0.1:8484`) is used after each run for a local-model annotation.
- The local model does **not** choose the next run and does **not** control admission.
  The queue is predeclared and deterministic.
- Local-model annotations are stored as `LOCAL_MODEL_HYPOTHESIS`.
- No Xeno training is included because the retained evidence does not establish the
  original Xeno training kernel as available.
- No signing or Merkle/MMR operation is performed.

## Queue

11 sequential local runs:
- 3 same-seed/same-thread controls;
- 1 four-thread perturbation;
- early/mid/late one-token perturbations at seed 314159;
- two additional seeds, each with control + mid perturbation.

The queue stops launching new work at 08:00 America/Los_Angeles by default.
A currently running bounded run is allowed to finish.

## Start from magicPRObox

Place all files in one directory, then:

```bash
chmod +x start_hydradg_overnight.sh hydradg_overnight_daisy.py
./start_hydradg_overnight.sh
```

## Monitor

```bash
ssh magicstudiobox '
cd /Users/byron/projects/active/hydradg/HydraDG_DaisyTrain_v0.3.7
cat eval/vithia_overnight/VITHIA-OVERNIGHT-01/status.json
tail -40 eval/vithia_overnight/VITHIA-OVERNIGHT-01/launcher.log
'
```

## Ollarma workflow manifest

`hydradg-vithia-overnight.manifest.json` follows Ollarma's validated-script manifest
shape. It should only be invoked through `ollarma workflow` after a real HydraDG
adapter is registered and the manifest is placed under the repository's `.ollarma`
manifest root. The launcher does not assume that adapter exists.
