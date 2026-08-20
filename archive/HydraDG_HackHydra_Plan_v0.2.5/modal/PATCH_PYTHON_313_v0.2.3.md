# Modal Python 3.13 patch — v0.2.3

## Evidence from the user-supplied run
The v0.2.2 patch solved the prior live-source mutation failure: Modal successfully
built and saved the PyTorch/Transformers image. The run then stopped before GPU
training because the serialized Function was defined locally under Python 3.13
while its Modal Image explicitly used Python 3.11.

This is an execution-environment mismatch, not model divergence.

## v0.2.3 changes
1. Remote Modal Image is explicitly Python 3.13, matching the user's local Modal CLI.
2. `include_source=False` remains enabled.
3. `serialized=True` remains enabled.
4. No project source file is mounted into the remote image.
5. The Pythia-14M architecture is frozen in code from the public
   `EleutherAI/pythia-14m` `config.json` at commit
   `94f7c35d5e9f2e9bac8ca839329f505b4d007d5d`.
6. Model weights are still initialized from scratch from a fixed seed.
7. The run receipt records both the frozen config hash and source commit.
8. Results use a new Modal Volume: `hydradg-vithia-runs-v3`.

## Run exactly these commands

```bash
cd /Users/byron/projects/active/hydradg/HydraDG_HackHydra_Plan_v0.2.3
unset MODAL_TOKEN_ID MODAL_TOKEN_SECRET
modal token info
modal run modal/modal_vithia_divergence_v3.py --quick
```

Do not paste comment lines beginning with `#` into the interactive zsh session if
that shell has `INTERACTIVE_COMMENTS` disabled.

After quick succeeds:

```bash
modal run modal/modal_vithia_divergence_v3.py
modal volume ls hydradg-vithia-runs-v3 /runs
modal volume get hydradg-vithia-runs-v3 /runs modal_runs_v3
```

## Claim state
- Modal account authentication: user-log supported.
- v0.2.2 image build: user-log supported as successful.
- v0.2.2 GPU training: not started.
- v0.2.3 Python/config patch: generated and syntax-checked here.
- v0.2.3 Modal execution: not yet observed.
