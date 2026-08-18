# Kaggle independent-run lane

I do not currently have an authenticated Kaggle session or Kaggle plugin in this ChatGPT runtime.

The official Kaggle CLI can push a notebook/kernel and request an accelerator. The current CLI
documents accelerator IDs including P100, T4, L4, A100 and others, but availability can be
restricted and the actual assigned hardware must be captured in the run receipt.

## Recommended role

Kaggle should be an **independent environment**, not the only source of results.

Run:
- one reference run;
- one repeated reference run;
- one controlled perturbation.

Export the JSON receipts and checkpoints, then ingest them into the same FCG.

## Authentication

Configure Kaggle on your own machine with its current OAuth/API-token flow. Do not commit tokens.
Once authenticated, `kaggle kernels push -p <folder> --accelerator <id>` can launch a kernel.

## Claim boundary

A Kaggle result proves only the hardware/software environment recorded in that run. Do not label
it "independent computer replication" unless the receipt establishes an execution substrate
independent of the reference run.
