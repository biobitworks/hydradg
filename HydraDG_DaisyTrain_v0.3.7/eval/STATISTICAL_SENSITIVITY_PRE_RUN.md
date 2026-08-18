# HydraDG Track 03 — Pre-Run Statistical Sensitivity

Status: DESIGN_SENSITIVITY_ONLY
Date: 2026-08-18
Seed dependence: NONE for this exact analytic calculation
Scope: paired binary endpoints analyzed with exact two-sided McNemar testing

## Purpose

This is not a benchmark result. It quantifies what effect sizes the planned smoke80 and full500 designs can reasonably detect for paired binary endpoints before any HydraDG evaluation output is observed.

## Model

For a paired binary endpoint, let:

- `p01` = probability baseline is wrong and HydraDG is correct;
- `p10` = probability baseline is correct and HydraDG is wrong;
- `d = p01 + p10` = discordant-pair fraction;
- `delta = p01 - p10` = net paired accuracy improvement.

Power was computed exactly by summing over the random number of discordant pairs `M ~ Binomial(n, d)` and, conditional on `M=m`, the number of HydraDG-favoring discordances `X ~ Binomial(m, p01/d)`. Rejection uses the exact two-sided McNemar/binomial test at alpha=0.05.

## Approximate minimum net paired improvement for 80% power

| n | discordant fraction d | minimum delta for >=80% power |
|---:|---:|---:|
| 80 | 0.10 | 0.099 |
| 80 | 0.20 | 0.142 |
| 80 | 0.30 | 0.177 |
| 80 | 0.40 | 0.205 |
| 500 | 0.10 | 0.041 |
| 500 | 0.20 | 0.058 |
| 500 | 0.30 | 0.071 |
| 500 | 0.40 | 0.081 |

## Selected exact-power points

| n | d | delta | exact power |
|---:|---:|---:|---:|
| 80 | 0.20 | 0.10 | 0.437 |
| 80 | 0.20 | 0.15 | 0.855 |
| 80 | 0.30 | 0.15 | 0.634 |
| 80 | 0.30 | 0.20 | 0.908 |
| 500 | 0.20 | 0.05 | 0.676 |
| 500 | 0.20 | 0.10 | 0.999 |
| 500 | 0.30 | 0.05 | 0.502 |
| 500 | 0.30 | 0.10 | 0.983 |

## Interpretation for the evaluation sequence

- `smoke80` is correctly positioned as a protocol/runtime/effect-size discovery stage. Unless the relational benefit is large, it is underpowered for a definitive paired binary superiority claim.
- `full500` is substantially more informative. Under moderate discordance (`d=0.20-0.30`), a net paired improvement around 0.06-0.07 is near the 80% power boundary; a 0.10 improvement has very high power.
- The final submission should report paired effect sizes and confidence intervals even when a p-value is not significant.
- Power depends on the actual discordant-pair structure. The table must not be treated as a promise about observed benchmark power.

## Precision reference

For a single proportion near 0.50, the approximate 95% Wilson interval half-width is about:

- `0.107` at `n=80`;
- `0.0437` at `n=500`.

This further supports using smoke80 for protocol validation and full500 for the main quantitative result.

## Claim ceiling

`DESIGN_SENSITIVITY_RECOMPUTED_NOT_BENCHMARK_RESULT`

No HydraDG, HydraDB, vector, flat, Modal, Daytona, GMI, Exa, Kaggle or model performance result is asserted by this artifact.
