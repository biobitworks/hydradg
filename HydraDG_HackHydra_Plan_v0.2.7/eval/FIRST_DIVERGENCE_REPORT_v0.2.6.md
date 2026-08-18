# HydraDG Modal quick matrix — first-divergence result

Source log SHA-256: `0b18c484162e79cc4772b1282044cf8b3925a48cae6037c2f0219d8e7d6da3b5`

## Strongest result

Two fresh Tesla T4 executions on different reported GPU UUIDs have no observed
canonical model-state divergence across any of the four recorded quick-training
steps. Their raw `torch.save()` checkpoint files are byte-different.

The controlled T4 perturbation changes token `[0,0]` from `21725` to `21726` at
declared training step 2. Relative to both unperturbed T4 references:

- steps 0 and 1 are canonical-state identical;
- step 2 is the first observed canonical model-state divergence;
- loss absolute delta at step 2 = `0.0025396347045898438`;
- fixed-probe top-token IDs remain identical;
- max absolute delta among the recorded top logits = `0.003940582275390625`.

This supports the bounded statement:

> In this quick fixture, the declared step-2 input perturbation aligns exactly
> with the first observed post-step canonical model-state divergence.

It does not establish that every lower-level operation before the recorded
post-step state is identical.

## Cross-SKU result

T4↔L4, T4↔A10G, and L4↔A10G all first differ at recorded step 0.

At that first recorded divergence:
- loss delta is reported as `0.0`;
- top-token IDs are unchanged;
- top-logit deltas are ~1.5e-6 to 2.3e-6.

However, `torch_num_interop_threads` differs before training:
T4=17, L4=9, A10G=8. Therefore the cross-SKU observation remains
`CROSS_ENVIRONMENT_DIVERGENCE`, not GPU-architecture causation.

## Instrumentation gap

The current `records[0]` is post-optimizer-step 0. It is too coarse to distinguish:

1. identical vs divergent initialized weights;
2. forward-pass divergence;
3. loss-bit divergence;
4. backward/gradient divergence;
5. optimizer-update divergence.

The next launcher adds hashes/receipts at each of those boundaries.
