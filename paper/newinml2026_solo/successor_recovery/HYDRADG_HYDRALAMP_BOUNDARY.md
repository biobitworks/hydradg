# HydraDG vs HydraLamp Boundary

## Definitions

**HydraDG** = governed experimental/reproducibility framework binding probabilistic model outputs,
deterministic transforms, custody receipts, claim ceilings, and terminal-state preservation.

**HydraLamp** = concrete HydraDG implementation / demonstration / systems-validation lane.
HydraLamp exercises perturbation, tamper, concurrency, replay, and provider-ladder failure capture.

## Classification of HydraLamp results

| Result | Classification | Paper role |
|--------|----------------|------------|
| 100/100 hash chain verification (4×25 matrix) | HYDRADG_SYSTEMS_VALIDATION | Table systems validation |
| 8/8 synthetic tamper detection | HYDRADG_SYSTEMS_VALIDATION | Figure FIG-004 |
| Concurrent execution uniqueness | HYDRADG_SYSTEMS_VALIDATION | Table systems validation |
| Live provider R0–R6 quota failure | HYDRADG_SYSTEMS_VALIDATION | Negative/blocked preserved |
| Anticube perturbation cases AC-001–014 | HYDRALAMP_IMPLEMENTATION_RESULT | Appendix D |
| Agent-native hackathon demos | HACKATHON_DEMONSTRATION | Appendix only |
| EXP-008/009 treatment effects | NOT_ADMISSIBLE from HydraLamp | Must not collapse lanes |

## Rule
Do **not** collapse HydraLamp system integrity results into EXP-008/009 treatment-effect evidence.
