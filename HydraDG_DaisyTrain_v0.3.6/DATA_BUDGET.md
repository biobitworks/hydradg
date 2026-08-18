# Data budget and denominator discipline

| Lane | Planned scale | Role | May support |
|---|---:|---|---|
| ECA-EXT80 | 80 trajectories | deterministic conformance | first-divergence / impact / exact-repair serialization |
| XenoDisorder CAFA6 replay | frozen historical-sized evaluator inputs; exact local assets required | scientific cross-environment replay | bounded same-assets replay if dependency gates pass |
| Vithia/Pythia | existing Modal matrix | numerical/model-execution evidence | same-SKU replay and controlled/cross-SKU divergence |
| LongMemEval-S smoke80 | 80 selected official cases | development only | debugging/ablation sanity |
| LongMemEval-S full500 | all 500 official cases | primary Track 03 benchmark | final memory headline |
| HydraDG injected perturbations | separate internal suite | graph ground truth | divergence/impact/recovery/admission metrics |

## "Enough data" rule

The final memory claim should use all 500 official LongMemEval-S cases, not a custom subset.

ECA-EXT80 is intentionally small and exact: it is a deterministic conformance suite with
known injected ground truth, not a population-generalization claim.

XenoDisorder is useful because the computation is scientifically structured and environment-sensitive,
but it must remain a separate replay lane. Its rows must not inflate the apparent size of the memory benchmark.

Vithia/Pythia is a mechanistic execution-divergence lane, not a Track 03 memory accuracy benchmark.

## Confidence intervals

For binary internal metrics such as localization or exact recovery, report numerator/denominator
and a Wilson 95% interval. A 100% result on 20 or 60 tests is not described as universal proof.
