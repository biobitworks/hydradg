#!/usr/bin/env python3
"""Paired statistical analysis for Hack Hydra Best Use A/B/C/D retrieval.

Input: JSONL emitted by run_best_use_longmemeval.py.
Output: JSON with Wilson intervals, exact paired McNemar tests, Holm correction,
paired bootstrap CIs, latency/context summaries, and per-category metrics.

Claim discipline:
- smoke subsets are DEVELOPMENT_SMOKE_ONLY regardless of p-values;
- full benchmark claims require --expected-n 500 and the frozen benchmark route;
- this script analyzes supplied outcomes; it does not establish data provenance.
"""
from __future__ import annotations
import argparse, json, math, random, statistics
from pathlib import Path
from collections import defaultdict

METHODS = ("A", "B", "C", "D")
Z975 = 1.959963984540054


def percentile(xs, q):
    if not xs:
        return None
    ys = sorted(xs)
    if len(ys) == 1:
        return float(ys[0])
    x = (len(ys) - 1) * q
    lo, hi = math.floor(x), math.ceil(x)
    if lo == hi:
        return float(ys[lo])
    return float(ys[lo] * (hi - x) + ys[hi] * (x - lo))


def wilson(successes, n):
    if n == 0:
        return {"n": 0, "successes": 0, "rate": None, "lo": None, "hi": None}
    p = successes / n
    den = 1 + Z975 * Z975 / n
    ctr = (p + Z975 * Z975 / (2 * n)) / den
    half = Z975 * math.sqrt(p * (1 - p) / n + Z975 * Z975 / (4 * n * n)) / den
    return {"n": n, "successes": successes, "rate": p, "lo": ctr - half, "hi": ctr + half}


def exact_mcnemar(a_hits, b_hits):
    # b10 = A correct, comparator wrong; b01 = A wrong, comparator correct.
    b10 = sum(1 for a, b in zip(a_hits, b_hits) if a == 1 and b == 0)
    b01 = sum(1 for a, b in zip(a_hits, b_hits) if a == 0 and b == 1)
    m = b10 + b01
    if m == 0:
        return {"a_only": b10, "method_only": b01, "discordant": 0, "p_exact_two_sided": 1.0}
    k = min(b10, b01)
    # Exact two-sided binomial p under H0 p=0.5.
    tail = sum(math.comb(m, i) for i in range(k + 1)) / (2 ** m)
    return {"a_only": b10, "method_only": b01, "discordant": m, "p_exact_two_sided": min(1.0, 2 * tail)}


def holm(pairs):
    ordered = sorted(pairs, key=lambda kv: kv[1])
    out = {}
    running = 0.0
    m = len(ordered)
    for i, (name, p) in enumerate(ordered):
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)
        out[name] = running
    return out


def paired_bootstrap_delta(rows, method, field, draws=5000, seed=20260818):
    vals = []
    for r in rows:
        av = r["methods"]["A"].get(field)
        bv = r["methods"][method].get(field)
        if av is not None and bv is not None:
            vals.append((float(av), float(bv)))
    if not vals:
        return {"n": 0, "mean_delta": None, "ci95": [None, None]}
    mean_delta = statistics.fmean(b - a for a, b in vals)
    rng = random.Random(seed + ord(method[0]) + sum(map(ord, field)))
    n = len(vals)
    sims = []
    for _ in range(draws):
        s = 0.0
        for _j in range(n):
            a, b = vals[rng.randrange(n)]
            s += b - a
        sims.append(s / n)
    return {"n": n, "mean_delta": mean_delta, "ci95": [percentile(sims, 0.025), percentile(sims, 0.975)]}


def summarize_method(rows, method):
    hits = [int(r["methods"][method]["hit_at_k"]) for r in rows]
    recalls = [float(r["methods"][method]["session_recall_at_k"]) for r in rows]
    lat = [float(r["methods"][method]["latency_ms"]) for r in rows]
    ctx = [float(r["methods"][method].get("context_sessions", 0)) for r in rows]
    path = [float(r["methods"][method].get("evidence_path_coverage", 0)) for r in rows]
    return {
        "hit_at_k": wilson(sum(hits), len(hits)),
        "mean_session_recall_at_k": statistics.fmean(recalls) if recalls else None,
        "latency_ms": {"median": statistics.median(lat) if lat else None, "p95": percentile(lat, 0.95)},
        "context_sessions_mean": statistics.fmean(ctx) if ctx else None,
        "evidence_path_coverage_mean": statistics.fmean(path) if path else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--expected-n", type=int, default=None)
    ap.add_argument("--bootstrap", type=int, default=5000)
    args = ap.parse_args()

    raw = [json.loads(line) for line in Path(args.input_jsonl).read_text().splitlines() if line.strip()]
    ids = [r["question_id"] for r in raw]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate question_id in input")
    for r in raw:
        missing = [m for m in METHODS if m not in r.get("methods", {})]
        if missing:
            raise SystemExit(f"{r.get('question_id')}: missing methods {missing}")

    # Official LongMemEval retrieval metrics skip abstention cases because they have no answer location.
    scored = [r for r in raw if not r.get("is_abstention", False)]
    if not scored:
        raise SystemExit("no non-abstention retrieval rows")
    if args.expected_n is not None and len(raw) != args.expected_n:
        raise SystemExit(f"expected {args.expected_n} total rows, observed {len(raw)}")

    summary = {m: summarize_method(scored, m) for m in METHODS}
    a_hits = [int(r["methods"]["A"]["hit_at_k"]) for r in scored]
    comparisons = {}
    raw_ps = []
    for m in ("B", "C", "D"):
        m_hits = [int(r["methods"][m]["hit_at_k"]) for r in scored]
        mc = exact_mcnemar(a_hits, m_hits)
        raw_ps.append((m, mc["p_exact_two_sided"]))
        comparisons[m] = {
            "vs_A": mc,
            "delta_hit_rate": statistics.fmean(m_hits) - statistics.fmean(a_hits),
            "paired_bootstrap_recall_delta": paired_bootstrap_delta(scored, m, "session_recall_at_k", args.bootstrap),
            "paired_bootstrap_latency_delta_ms": paired_bootstrap_delta(scored, m, "latency_ms", args.bootstrap),
            "paired_bootstrap_context_sessions_delta": paired_bootstrap_delta(scored, m, "context_sessions", args.bootstrap),
        }
    adjusted = holm(raw_ps)
    for m in comparisons:
        comparisons[m]["vs_A"]["p_holm_3way"] = adjusted[m]

    by_cat = {}
    cats = sorted(set(r.get("question_type", "UNKNOWN") for r in scored))
    for cat in cats:
        subset = [r for r in scored if r.get("question_type", "UNKNOWN") == cat]
        by_cat[cat] = {m: summarize_method(subset, m) for m in METHODS}

    full_route = len(raw) == 500 and args.expected_n == 500
    claim_ceiling = "FULL500_RETRIEVAL_ABLATION_ANALYZED" if full_route else "DEVELOPMENT_SMOKE_ONLY"
    decisions = {}
    for m in ("B", "C", "D"):
        d = comparisons[m]["delta_hit_rate"]
        p = comparisons[m]["vs_A"]["p_holm_3way"]
        decisions[m] = (
            "GRAPH_ADVANTAGE_OBSERVED_FULL500" if full_route and d > 0 and p < 0.05
            else "GRAPH_ADVANTAGE_SIGNAL_SMOKE_ONLY" if (not full_route and d > 0)
            else "NO_POSITIVE_HIT_RATE_SIGNAL"
        )

    out = {
        "schema": "hydradg.best_use_ablation_stats.v1",
        "input": str(args.input_jsonl),
        "total_rows": len(raw),
        "retrieval_scored_non_abstention_n": len(scored),
        "abstention_rows_excluded_from_retrieval_scoring": len(raw) - len(scored),
        "k": raw[0].get("k"),
        "methods": summary,
        "comparisons_vs_A": comparisons,
        "per_question_type": by_cat,
        "decision": decisions,
        "multiple_testing": "Holm correction across B/C/D exact paired McNemar tests",
        "claim_ceiling": claim_ceiling,
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_MERKLE_COMMITTED",
    }
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_ceiling": claim_ceiling, "n": len(raw), "scored_n": len(scored), "decision": decisions}, indent=2))

if __name__ == "__main__":
    main()
