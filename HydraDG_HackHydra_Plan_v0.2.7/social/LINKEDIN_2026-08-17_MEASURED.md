# Aug 17 measured build update

Hack Hydra reproducibility update:

I ran the same small, from-scratch Pythia-compatible training fixture across fresh Modal GPUs.

Two different Tesla T4 GPU UUIDs produced the same canonical final model-state hash. L4 and A10G finished at different canonical states, while a controlled +1 token perturbation on T4 also diverged as expected.

One useful catch: the environments exposed different PyTorch inter-op thread counts across GPU types, so I’m not calling the cross-GPU result “GPU-caused” yet. The next run pins both thread pools before comparing architectures.

That is the point of the project: record the earliest divergence instead of promoting the final difference into a stronger causal claim than the evidence supports.

#HackHydra #HydraDB #MLReproducibility #AIAgents #OpenSource
