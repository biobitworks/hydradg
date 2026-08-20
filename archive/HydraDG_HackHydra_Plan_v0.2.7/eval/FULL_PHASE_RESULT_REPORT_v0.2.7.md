# HydraDG v0.2.7 — executed full phase-localized result

Source terminal-log SHA-256: `b36d3eaaccc654b21402a703b933e716ac0c272a15f021e2b1234146bf1cdf63`

## Full-run result

The 24-step v5 matrix completed with both PyTorch thread pools pinned to 1.

### Same-SKU T4
Two different reported T4 GPU UUIDs produced the same final canonical model state:
`ea66d55722eb8d611894af398008c7e19dc44fc47af3acd718b12800270e0a64`.

The phase analyzer reports no observed divergence across initialization, input batches,
pre-step states, forward-loss bits, gradients, or post-optimizer model states.

### Controlled perturbation
The declared perturbation changes input token `[0,0]` by +1 at step 8.
The first observed phase divergence relative to either unperturbed T4 is:

`INPUT_BATCH @ step 8`.

This is the exact declared perturbation boundary.

### Cross-SKU
For T4↔L4, T4↔A10, and L4↔A10, the first observed phase divergence is:

`BACKWARD_GRADIENTS @ step 0`.

Because the analyzer checks initial model state, input batch, pre-step model state,
and forward-loss float32 bits before gradient hashes, those preceding recorded
objects were equal for each compared pair.

The result therefore localizes the first observed difference more tightly than
the earlier post-step analysis.

## Claim boundary
Supported:
> Under the recorded pinned software/thread fixture, the first observed cross-SKU
> divergence is localized to backward gradients at training step 0.

Not established:
- universal GPU causality;
- exact CUDA kernel/operator responsible;
- first parameter/layer whose gradient differs;
- bit/ULP/L2 magnitude of the first differing gradient tensor;
- independent provider replication.
