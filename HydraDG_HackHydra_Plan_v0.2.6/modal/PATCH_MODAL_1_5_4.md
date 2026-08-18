# Modal source-stability patch — v0.2.2

## Observed failure
The supplied run log shows successful Modal authentication followed by two source-integrity failures during the long image build:

1. `modal/modal_vithia_divergence.py was modified during build process`
2. `scripts/vithia_divergence_core.py was modified during build process`

This means the GPU experiment never started. It is not a training divergence result.

## Patch
`modal_vithia_divergence_v2.py`:

- uses `modal.App(..., include_source=False)`;
- uses `@app.function(..., include_source=False, serialized=True)`;
- removes `Image.add_local_file()` entirely;
- puts the bounded training fixture inside the serialized remote function;
- retains the pinned third-party image recipe;
- records the resolved Pythia-14M config and a canonical SHA-256 of that config;
- adds `--quick` for a 4-step build/runtime smoke test before the full 24-step matrix.

Modal documentation states that Function source is included by default unless
`include_source=False`, and `serialized=True` sends the Function via cloudpickle.
The current `add_local_file` API otherwise tracks a local file that is supplied to
containers.

## Recommended commands

```bash
cd /Users/byron/projects/active/hydradg/HydraDG_HackHydra_Plan_v0.2.2

# Optional but recommended if you want ~/.modal.toml to be the credential source.
# Do not print the secret.
unset MODAL_TOKEN_ID MODAL_TOKEN_SECRET
modal token info

# First prove image + GPU + training code works:
modal run modal/modal_vithia_divergence_v2.py --quick

# Then run the full initial matrix:
modal run modal/modal_vithia_divergence_v2.py
```

If a background formatter/sync agent is rewriting the live repository, the v2
launcher no longer mounts those files into the remote image; nevertheless, do not
edit `modal_vithia_divergence_v2.py` while the local Modal CLI is parsing it.

## Unrelated shell warning
`command not found: compdef` comes from the Daytona zsh completion script and is
not the cause of the Modal build failure.
