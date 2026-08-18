# Bounded novelty audit

## Conclusion

**Do not claim invention of temporal graph memory, provenance-aware agent memory, bitwise reproducibility, divergence diagnosis, or claim/action gating individually.**

The reviewed 2026 landscape contains close prior/concurrent work:

- HydraDB already implements append-only bitemporal/versioned agent memory and reports LongMemEval-S results.
- SodaMem already combines evidence provenance with temporal `SUPERSEDES`, `CONTRADICTS`, and `UPDATES`.
- MAP-Graph already combines provenance-aware memory, trust/access gating, and retained lineage.
- RepDL targets bit-level reproducibility across heterogeneous hardware.
- NVIDIA Megatron has deterministic/rerun diagnostics, including same-GPU and different-GPU reruns.
- FLARE localizes divergent LLM training at cluster scale.
- LongMemEval / LongMemEval-V2 provide established memory evaluation data.

## Defensible prospective novelty

The proposed Hack Hydra contribution is the **coupled evidence-divergence graph**:

`execution state divergence -> first divergent FCO -> dependency traversal -> temporal memory/evidence divergence -> answer/evaluation divergence -> claim/admission impact -> typed recovery`

with these additional properties:

1. multiscale divergence from bytes/bits through tensors, activations, outputs, evaluations and claims;
2. first-divergence localization represented as a graph object;
3. downstream impact set ("blast radius") over evidence/memory/claim dependencies;
4. explicit FCO/FCG claim ceilings and separate custody/replay/validation gates;
5. version-preserving recovery rather than destructive overwrite;
6. optional continuous CFMO trajectory with discrete cryptographic checkpoints;
7. public benchmark graph plus a schema-compatible, data-isolated PHI-private twin.

**Claim ceiling:** literature/product search supports `BOUNDED_NOVELTY_HYPOTHESIS`, not patentability, priority, FTO, or proof that no one else has implemented the same combination.
