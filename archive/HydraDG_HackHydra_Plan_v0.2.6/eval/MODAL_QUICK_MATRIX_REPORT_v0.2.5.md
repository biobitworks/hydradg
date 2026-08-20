# Modal quick matrix — completed execution review

Source log SHA-256: `0acecb5f593474f869e9858694e4dccb1a07b94e0049d0033a1130f8e2898146`

## Observed completed runs

| Run | GPU | Compute capability | Interop threads | Final canonical state |
|---|---|---:|---:|---|
| t4_a | Tesla T4 | 7.5 | 17 | `d6c01a331527...` |
| t4_b | Tesla T4 | 7.5 | 17 | `d6c01a331527...` |
| l4_a | NVIDIA L4 | 8.9 | 9 | `dafa9a7b95bc...` |
| a10_a | NVIDIA A10G | 8.6 | 8 | `71321f6fdaa0...` |
| t4_perturb | Tesla T4 | 7.5 | 17 | `a8c67406e089...` |

All five report the same model-config SHA-256:
`a57466dddac1d8b350b2361d0a5b380039f179f96c71774ff268ba5b2d8d093e`.

## Result 1 — same-SKU/different-device T4

`t4_a` and `t4_b` use distinct reported GPU UUIDs and have the same canonical
final model-state hash.

Bounded claim:
`BOUNDED_SAME_SKU_CROSS_DEVICE_CANONICAL_FINAL_STATE_REPRODUCIBILITY`.

Their raw checkpoint archive SHA-256s differ, so raw file identity is not asserted.

## Result 2 — cross-SKU/environment

L4 and A10G finish at different canonical model states from T4 and each other.

However, the execution receipts also show different
`torch_num_interop_threads` values before training:
T4=17, L4=9, A10G=8.

Under the FCO/FCG first-divergence protocol, this is an earlier known environment
difference. Therefore the current claim is:
`CROSS_ENVIRONMENT_FINAL_STATE_DIVERGENCE_OBSERVED_NOT_GPU_CAUSALITY`.

The next full run must pin both PyTorch intra-op and inter-op threads to 1.

## Result 3 — controlled perturbation

`t4_perturb` changed token `[0,0]` by +1 at training step 2 and finished at a
different canonical model state from the unperturbed T4 references.

This is a valid positive-control association. The exact first observed training
state divergence is not yet established because the downloaded detailed receipt
files still need to be analyzed.

## Local analyzer path correction

Modal's CLI documents that when a folder is passed to `modal volume get`, the
contents are downloaded recursively into the local destination. The successful
command used `/runs` as the remote folder and `modal_runs_v3` as destination, so
the likely local paths are:

`modal_runs_v3/t4_a.receipt.json`, etc.

The v0.2.5 analyzer accepts a directory directly and recursively discovers
`*.receipt.json`, avoiding shell-glob/path-layout ambiguity.
