# v0.3.2 Modal stability patch

Observed v0.3.1 failure:
`modal/modal_eca_extension.py was modified during build process`

This is the same Modal live-source mutation class previously observed and fixed in
the Vithia launcher.

## Changes
- ECA launcher: `include_source=False`, `serialized=True`, no `add_local_file`.
- ECA core is embedded in the serialized remote function.
- XenoDisorder launcher receives the same source-stability treatment proactively.
- New Modal resources use `v032` names to prevent mixing pre-patch and post-patch evidence.
- Python cache files are removed from the distribution package.
- Added `FCO_REPO_AUDIT_STATUS.md`.

## Run

```bash
modal run modal/modal_eca_extension.py --quick
```

Expected quick summary under the frozen extension:
- total trajectories: 8
- perturbed trajectories: 6
- first-divergence exact: 6
- oracle repair trajectories: 2
- state-exact recovery: 2

If quick passes:

```bash
modal run modal/modal_eca_extension.py
mkdir -p eval/eca
modal volume get hydradg-eca-extension-v032   /runs/eca_extension_80.json   eval/eca/eca_extension_80.json --force

python scripts/validate_eca_extension.py eval/eca/eca_extension_80.json
python scripts/render_eca_figures.py eval/eca/eca_extension_80.json --outdir figures/generated
```
