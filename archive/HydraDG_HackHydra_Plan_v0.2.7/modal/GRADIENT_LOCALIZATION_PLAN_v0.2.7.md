# v0.2.7 next experiment

The executed v5 full run localized the first observed cross-SKU difference to
`BACKWARD_GRADIENTS @ step 0`.

The v6 launcher:
- keeps both PyTorch thread pools at 1;
- explicitly sets float32 matmul precision to `highest`;
- explicitly disables TF32 for CUDA matmul and cuDNN;
- disables cuDNN benchmarking and enables deterministic cuDNN;
- records those backend flags in each receipt;
- stores a hash and summary statistics for each named parameter gradient.

This allows the next analysis to ask:
`Which named parameter/layer gradient is the first canonical object that differs?`
