# Statistical Analysis Plan — Successor Recovery

## Scope
Post-hoc manuscript-recovery analyses on **frozen** observations only.
No new model samples. No endpoint substitution.

## Primary experiments
- **EXP-008**: paired McNemar on E06 within case×model strata; Wilson CI on proportions.
- **EXP-009**: same; ordering claims gated separately.
- **Stage-2**: descriptive state counts; M0/M1/M2 paired comparisons from frozen verdict JSON.

## Experimental units
- EXP-008/009: case (aggregated to n_paired=2 model strata per condition comparison scope in frozen verdict).
- Stage-2: case×model×generation (432 raw rows; 414 proper).

## Multiplicity
Exploratory secondary patterns (EXP-009 mechanistic) are not pooled with confirmatory E06.

## States
- UNDERPOWERED: insufficient discordant pairs for confirmatory inference.
- DESCRIPTIVE_ONLY: Stage-2 family counts retained without promotion.
- NOT_IDENTIFIABLE: missing pairing structure.

## HydraLamp
Deterministic perturbation cells excluded from probabilistic treatment pooling.
