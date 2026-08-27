# HydraDG Statistical Comparison — Morning 2026-08-27

## Verdict
Cross-track co-primary family tests **retain H0** after Holm correction (all adjusted p = 1.0 in `CROSS_TRACK_STATS.json`).
K5 control reconciliation: A Hit@5 = 0.963830, D Hit@5 = 0.944681 (N scored = 470; abstentions = 30).
Track03 primary K10 result: **NO_MODEL_BENEFIT**.

## Preregistered nulls
{
  "H0_rep": "Canonical scientific payload R1 = R2 = R3 within each cell (exact SHA-256 equality).",
  "H0_representation_k": "M(SG, k) - M(RAW, k) = 0",
  "H0_advantage_k": "M(SG, k) - M(RAW, k) <= 0",
  "H0_K_rep": "M(rep, K10) - M(rep, K5) <= 0",
  "H0_interaction": "[SG_K10 - RAW_K10] - [SG_K5 - RAW_K5] = 0"
}

## Limits
- McNemar / paired bootstrap **not** recomputed here because aligned case-level paired hit vectors were not located as a safe single table.
- Aggregate-only inferential tests are disallowed by mission rules.
- Do not promote PASS scripts to VERIFIED_EMPIRICAL_RESULT without verification contract.

## Source SHAs
- CONTROL_RECONCILIATION: `30d1978e2be5871023445f90da8dde22919f73151309797e00a92267f8869753`
- CROSS_TRACK_STATS: `90ccc2a4832bb463f1abd3d885cf512984587c08e3027beae7aa78fd6e3cf6c0`


## Audit follow-up (receipt-backed)

- RAW−SeedGraph ΔHit@K5/K10 = **0** → H0_representation / H0_advantage / H0_interaction supported as equality.
- H0_K_rep (≤0 depth gain) is **rejected if Hit@K is the metric** (raw K10−K5 Δhit ≈ +0.0255).
- H0_rep replicate SHA equality: **decision receipt NOT_FOUND**.
- Case-level ABCD hit vectors: **NOT_FOUND** — no McNemar upgrade.
- entities=4776: **matrix-stated only** (freeze recompute unique names=2558 / mentions=6130).
- Daisy 1020×N primary matrix: **NOT_ESTABLISHED** (accounted_so_far=0).
