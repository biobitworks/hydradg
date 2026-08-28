"""Deterministic paired-binary power assessment for EXP-010 (McNemar)."""
from __future__ import annotations

import math
from typing import Any


def cell_probs(pi0: float, pi1: float, p11: float) -> tuple[float, float, float, float]:
    """Return p00, p10, p01, p11 from marginals and concordant-positive rate."""
    p11 = max(0.0, min(p11, pi0, pi1))
    p10 = pi0 - p11
    p01 = pi1 - p11
    p00 = 1.0 - p11 - p10 - p01
    if p00 < -1e-9:
        raise ValueError(f"infeasible cell probs pi0={pi0} pi1={pi1} p11={p11}")
    return p00, p10, p01, p11


def exact_mcnemar_p_value_one_sided(b: int, c: int) -> float:
    """One-sided exact McNemar p-value for H1: p01 > p10 (c discordance > b)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) * (0.5**n)
    return min(1.0, 2.0 * tail)  # one-sided upper tail for c > b


def mcnemar_power_exact(b_expect: float, c_expect: float, alpha: float = 0.05) -> float:
    """Power using Poisson/binomial mode approximation on expected discordant counts."""
    b = max(0, int(round(b_expect)))
    c = max(0, int(round(c_expect)))
    if b + c == 0:
        return alpha
    p = exact_mcnemar_p_value_one_sided(b, c)
    return 1.0 - p if p < alpha else alpha


def analytic_n_mcnemar(p10: float, p01: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Dupont/Machin analytic sample size for paired proportions (one-sided)."""
    if p01 <= p10:
        return 9999
    z_alpha = 1.645  # one-sided 0.05
    z_beta = 0.8416212335729145  # 80% power
    num = (z_alpha + z_beta) ** 2 * (p10 + p01)
    den = (p01 - p10) ** 2
    return max(2, math.ceil(num / den))


def required_paired_n(
    pi0: float,
    pi1: float,
    p11: float,
    alpha: float = 0.05,
    target_power: float = 0.80,
) -> dict[str, Any]:
    p00, p10, p01, p11_cell = cell_probs(pi0, pi1, p11)
    rd = pi1 - pi0
    n_analytic = analytic_n_mcnemar(p10, p01, alpha, target_power)
    # Verify with expected discordant counts at n_analytic
    b_exp = n_analytic * p10
    c_exp = n_analytic * p01
    return {
        "n_paired_required": n_analytic,
        "pi0": pi0,
        "pi1": pi1,
        "risk_difference": rd,
        "p11_assumption": p11,
        "p10": p10,
        "p01": p01,
        "expected_discordant_rate": p10 + p01,
        "method": "analytic_mcnemar_one_sided_dupont",
        "verification_b_expected": b_exp,
        "verification_c_expected": c_exp,
    }


def build_power_assessment(
    alpha: float = 0.05,
    target_power: float = 0.80,
    primary_mde_pp: float = 0.15,
    mde_sensitivity_pp: tuple[float, ...] = (0.10, 0.15, 0.20),
    baseline_pi0_grid: tuple[float, ...] = (0.05, 0.10, 0.20, 0.30),
    p11_grid: tuple[float, ...] = (0.0, 0.05, 0.10, 0.15),
    attrition_grid: tuple[float, ...] = (0.0, 0.10, 0.15, 0.20, 0.30),
) -> dict[str, Any]:
    sensitivity: list[dict[str, Any]] = []
    for mde in mde_sensitivity_pp:
        for pi0 in baseline_pi0_grid:
            pi1 = min(1.0, pi0 + mde)
            for p11 in p11_grid:
                if p11 > min(pi0, pi1):
                    continue
                try:
                    row = required_paired_n(pi0, pi1, p11, alpha, target_power)
                    row["mde_pp"] = mde
                    sensitivity.append(row)
                except ValueError:
                    continue

    primary_row = required_paired_n(0.10, 0.10 + primary_mde_pp, 0.05, alpha, target_power)
    n_primary = primary_row["n_paired_required"]

    mde_primary_rows = [r for r in sensitivity if r.get("mde_pp") == primary_mde_pp]
    n_worst = max((r["n_paired_required"] for r in mde_primary_rows), default=n_primary)

    attrition_inflated = []
    for attr in attrition_grid:
        inflated = math.ceil(n_worst / (1.0 - attr)) if attr < 1.0 else None
        attrition_inflated.append(
            {
                "attrition_rate_assumption": attr,
                "raw_case_bank_n_inflated": inflated,
                "formula": "ceil(n_worst / (1 - attrition))",
            }
        )

    raw_n = math.ceil(n_worst / 0.85)  # default 15% attrition planning factor

    return {
        "schema": "hydradg.daisy_overnight.exp010_power_assessment.v1",
        "test": "paired_binary_mcnemar_analytic_one_sided",
        "independent_unit": "CASE",
        "replicate_policy": "NESTED_MAJORITY_OF_3_NEVER_INFLATES_N",
        "alpha": alpha,
        "target_power": target_power,
        "primary_mde_pp": primary_mde_pp,
        "primary_assumptions": {
            "baseline_pi0": 0.10,
            "p11_concordant_positive": 0.05,
            "note": "Preregistered planning assumptions; not estimated from EXP-008/009 outcomes",
        },
        "required_paired_n_primary": n_primary,
        "required_paired_n_worst_case_mde_grid": n_worst,
        "primary_power_row": primary_row,
        "mde_sensitivity_pp": list(mde_sensitivity_pp),
        "baseline_pi0_grid": list(baseline_pi0_grid),
        "p11_concordance_grid": list(p11_grid),
        "sensitivity_surface": sensitivity,
        "attrition_sensitivity_grid": attrition_inflated,
        "raw_case_bank_n_recommended": raw_n,
        "observed_post_hoc_power": "PROHIBITED",
        "claim_ceiling": "PREREGISTERED_POWER_PLANNING_ONLY",
    }
