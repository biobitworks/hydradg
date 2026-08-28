"""Paired statistics for Daisy falsification experiments."""
from __future__ import annotations

import math
import random
from typing import Any


def exact_mcnemar(b: int, c: int) -> dict[str, Any]:
    """b = C0+ C1-, c = C0- C1+."""
    n = b + c
    if n == 0:
        return {"discordant": 0, "b": b, "c": c, "p_exact": None, "note": "no_discordant_pairs"}
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    p = min(1.0, 2.0 * tail)
    if p == 0.0:
        p_bound = f"<{1 / (2 ** n)}"
    else:
        p_bound = p
    return {"discordant": n, "b": b, "c": c, "p_exact": p, "p_report": p_bound}


def risk_difference(pairs: list[tuple[bool | None, bool | None]]) -> dict[str, Any]:
    valid = [(a, b) for a, b in pairs if a is not None and b is not None]
    if not valid:
        return {"n": 0, "rd": None, "c0_rate": None, "c1_rate": None}
    c0 = sum(1 for a, _ in valid if a) / len(valid)
    c1 = sum(1 for _, b in valid if b) / len(valid)
    return {"n": len(valid), "rd": c1 - c0, "c0_rate": c0, "c1_rate": c1}


def bootstrap_rd_ci(
    pairs: list[tuple[bool | None, bool | None]],
    n_boot: int = 5000,
    seed: int = 42,
) -> dict[str, Any]:
    valid = [(a, b) for a, b in pairs if a is not None and b is not None]
    if len(valid) < 2:
        return {"n": len(valid), "ci95_low": None, "ci95_high": None, "method": "bootstrap_insufficient_n"}
    rng = random.Random(seed)
    diffs: list[float] = []
    n = len(valid)
    for _ in range(n_boot):
        sample = [valid[rng.randrange(n)] for _ in range(n)]
        c0 = sum(a for a, _ in sample) / n
        c1 = sum(b for _, b in sample) / n
        diffs.append(c1 - c0)
    diffs.sort()
    lo = diffs[int(0.025 * n_boot)]
    hi = diffs[int(0.975 * n_boot)]
    return {"n": n, "ci95_low": lo, "ci95_high": hi, "method": "paired_bootstrap_percentile"}


def holm_correction(tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = [(i, t) for i, t in enumerate(tests) if t.get("p_exact") is not None]
    indexed.sort(key=lambda x: x[1]["p_exact"])
    m = len(indexed)
    out = list(tests)
    for rank, (idx, t) in enumerate(indexed, start=1):
        adj = min(1.0, t["p_exact"] * (m - rank + 1))
        out[idx] = {**t, "p_holm": adj}
    return out


def classify_experiment(
    primary: dict[str, Any],
    data_quality: dict[str, Any],
    min_power_n: int = 5,
) -> str:
    if data_quality.get("abort_reason"):
        return data_quality["abort_reason"]
    if data_quality.get("valid_parse_rate", 1.0) < 0.5:
        return "INCONCLUSIVE_DATA_QUALITY"
    n = primary.get("n_paired", 0)
    if n < min_power_n:
        return "UNDERPOWERED"
    p = primary.get("p_exact")
    rd = primary.get("rd")
    if p is None or rd is None:
        return "INCONCLUSIVE_DATA_QUALITY"
    alpha = 0.05
    if p < alpha and rd > 0:
        return "SUPPORTED_POSITIVE"
    if p < alpha and rd < 0:
        return "SUPPORTED_NEGATIVE"
    if primary.get("b", 0) > 0 and primary.get("c", 0) > 0:
        return "MIXED"
    return "RETAINED_NULL"
