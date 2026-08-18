"""HydraDG deterministic math helpers.

No network access. Functions are intended to be unit-testable and backend-neutral.
"""
from __future__ import annotations
import math
import struct
from typing import Iterable, Sequence, Set, Tuple

def _u32(x: float) -> int:
    return struct.unpack(">I", struct.pack(">f", float(x)))[0]

def float32_bit_components(a: Sequence[float], b: Sequence[float]) -> dict:
    if len(a) != len(b):
        raise ValueError("length mismatch")
    total = max(1, len(a))
    sign = exponent = fraction = changed_bits = 0
    total_bits = 32 * total
    for x, y in zip(a, b):
        ux, uy = _u32(x), _u32(y)
        z = ux ^ uy
        changed_bits += z.bit_count()
        sign += (z >> 31) & 1
        exponent += ((z >> 23) & 0xff).bit_count()
        fraction += (z & 0x7fffff).bit_count()
    return {
        "bit_divergence": changed_bits / total_bits,
        "sign_divergence": sign / total,
        "exponent_bit_divergence": exponent / (8 * total),
        "fraction_bit_divergence": fraction / (23 * total),
        "changed_bits": changed_bits,
        "total_bits": total_bits,
    }

def relative_l2(a: Sequence[float], b: Sequence[float], eps: float = 1e-12) -> float:
    if len(a) != len(b):
        raise ValueError("length mismatch")
    num = math.sqrt(sum((float(x)-float(y))**2 for x, y in zip(a,b)))
    den = math.sqrt(sum(float(x)**2 for x in a)) + eps
    return num / den

def js_divergence(p: Sequence[float], q: Sequence[float], eps: float = 1e-15) -> float:
    if len(p) != len(q):
        raise ValueError("length mismatch")
    sp, sq = sum(p), sum(q)
    if sp <= 0 or sq <= 0:
        raise ValueError("distributions must have positive mass")
    p = [max(eps, x/sp) for x in p]
    q = [max(eps, x/sq) for x in q]
    m = [(x+y)/2 for x,y in zip(p,q)]
    def kl(a,b):
        return sum(x * math.log(x/y) for x,y in zip(a,b))
    return 0.5*kl(p,m) + 0.5*kl(q,m)

def impact_metrics(pred: Set[str], gold: Set[str]) -> dict:
    tp = len(pred & gold)
    precision = tp / len(pred) if pred else (1.0 if not gold else 0.0)
    recall = tp / len(gold) if gold else (1.0 if not pred else 0.0)
    return {
        "precision": precision,
        "recall": recall,
        "exact_match": pred == gold,
    }

def recovery_fraction(d_perturb: float, d_repair: float, eps: float = 1e-12) -> float:
    return 1.0 - d_repair/(d_perturb+eps)
