# fractal-custody-objects audit status — 2026-08-17

## Status
`PARTIALLY_REVIEWED / LOAD-BEARING_ARTIFACTS_RECOVERED`

The repository `biobitworks/fractal-custody-objects` and its `main` branch were
confirmed through the connected GitHub account. A complete current-main file-by-file
audit was not completed because GitHub code search returned upstream 502 errors and
commit enumeration was not accessible to the integration.

## Load-bearing material already recovered/reviewed
- Public FCO v1 manuscript/deposit and reproducibility recipe.
- Deposit structure: manuscript + data/results + figures + scripts + custody manifests.
- FCO v3 review describing the 256-rule ECA custody benchmark and its negative conclusion.
- Historical ECA identifiers/search targets such as `FMO-EXP-ECA-DEMO-01`,
  `PREREG_eca_demo.json`, `RESULTS_eca_demo.json`, and `STATS_eca_demo.json`.
- XenoDisorder historical evaluator path:
  `training/cafa6_governed_eval.py` at expected source commit
  `abd696baa2065af3b3ee0dac5e12152c94745d4e`.
- XenoDisorder local asset paths:
  `scratchpad/cafa6_exp2_out/ckpt_latest.pt` and
  `scratchpad/cafa6_governed_eval_data/residual_table.jsonl`.
- Publication-family FCG object describing FCO-v2/v3, XenoDisorder, FMO-FCG and
  related app FCG roots plus the MMR construction recipe.

## Required local audit on magicPRObox
The local clone is currently the higher-fidelity source for file/history recovery.

Run:

```bash
FCO=/Users/byron/projects/active/fractal-custody-objects
git -C "$FCO" status --short
git -C "$FCO" rev-parse HEAD
git -C "$FCO" log --oneline --decorate -25

bash scripts/locate_historical_eca_source.sh "$FCO"
bash scripts/locate_xeno_command.sh "$FCO"

find "$FCO" -type f \(   -name 'PREREG_eca_demo.json' -o   -name 'RESULTS_eca_demo.json' -o   -name 'STATS_eca_demo.json' -o   -name 'cafa6_governed_eval.py' \) -print
```

Do not call historical ECA reproduction complete until the original implementation
route and result bytes are located and rerun.
