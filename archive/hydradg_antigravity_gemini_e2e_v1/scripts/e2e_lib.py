from __future__ import annotations
import hashlib, json, math
from pathlib import Path
from typing import Iterable, Sequence

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize_distribution(values: Sequence[float]) -> list[float]:
    vals = [max(0.0, float(v)) for v in values]
    total = sum(vals)
    if total <= 0:
        raise ValueError("distribution total must be > 0")
    return [v/total for v in vals]

def _kl_bits(p: Sequence[float], q: Sequence[float]) -> float:
    s = 0.0
    for pi, qi in zip(p, q):
        if pi <= 0:
            continue
        if qi <= 0:
            raise ValueError("q contains zero where p > 0")
        s += pi * math.log2(pi/qi)
    return s

def jsd_bits(a: Sequence[float], b: Sequence[float]) -> float:
    p = normalize_distribution(a)
    q = normalize_distribution(b)
    if len(p) != len(q):
        raise ValueError("distribution lengths differ")
    m = [(x+y)/2.0 for x,y in zip(p,q)]
    js = 0.5*_kl_bits(p,m) + 0.5*_kl_bits(q,m)
    if js < -1e-12 or js > 1+1e-12:
        raise AssertionError(f"JSD outside [0,1]: {js}")
    return max(0.0, min(1.0, js))

def cloud_drift(a: Sequence[float], b: Sequence[float]) -> float:
    return 100.0 * jsd_bits(a,b)

def exact_agreement(labels_a: Sequence[str], labels_b: Sequence[str]) -> float:
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("paired non-empty labels required")
    return sum(x == y for x,y in zip(labels_a,labels_b))/len(labels_a)

def cohen_kappa_if_informative(labels_a: Sequence[str], labels_b: Sequence[str]):
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("paired non-empty labels required")
    cats = sorted(set(labels_a) | set(labels_b))
    # With only one observed class, kappa is not informative.
    if len(cats) < 2:
        return None
    n = len(labels_a)
    po = exact_agreement(labels_a, labels_b)
    pa = {c: labels_a.count(c)/n for c in cats}
    pb = {c: labels_b.count(c)/n for c in cats}
    pe = sum(pa[c]*pb[c] for c in cats)
    if abs(1-pe) < 1e-15:
        return None
    return (po-pe)/(1-pe)

def canonical_json_sha(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
