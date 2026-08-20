#!/usr/bin/env python3
"""
HydraDG Context Iceberg Score v1 & Ollarma Dual-Model Protocol Evaluator.
Computes deterministic JSD CloudDrift, Gibbs G* deltas, dual-model (M1 vs M2) advisory
predictions via local Ollarma API, and writes back atomic receipts to local FCG custody.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, math, urllib.request, urllib.error
from pathlib import Path

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def hid(kind: str, payload: dict) -> str:
    return f"{kind}:{sha_text(canon(payload))}"

# --- Deterministic Math Functions ---

def kl_divergence(p: list[float], m: list[float]) -> float:
    kl = 0.0
    for pi, mi in zip(p, m):
        if pi > 0 and mi > 0:
            kl += pi * math.log2(pi / mi)
    return kl

def jensen_shannon_divergence(p: list[float], q: list[float]) -> float:
    if len(p) != len(q):
        raise ValueError("Distribution length mismatch")
    m = [0.5 * (pi + qi) for pi, qi in zip(p, q)]
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)

def total_variation_distance(p: list[float], q: list[float]) -> float:
    return 0.5 * sum(abs(pi - qi) for pi, qi in zip(p, q))

def compute_context_cloud_distribution(aggregate_graph: dict) -> tuple[list[str], list[float]]:
    """
    Computes 8-bucket context-cloud distribution p(i) from aggregate graph counts.
    Buckets:
    0: Session nodes
    1: Entity nodes
    2: Fact nodes
    3: Temporal edges (NEXT + PREV)
    4: Semantic edges (MENTIONS + ABOUT + ASSERTS + DERIVED_FROM)
    5: Governance edges (SUPERSEDED_BY + CONTRADICTS)
    6: Case nodes (HAS_CASE + CONTAINS)
    7: Case count
    """
    buckets = [
        "session_nodes",
        "entity_nodes",
        "fact_nodes",
        "temporal_edges",
        "semantic_edges",
        "governance_edges",
        "case_nodes",
        "case_count"
    ]
    edges = aggregate_graph.get("edges", {})
    counts = [
        float(aggregate_graph.get("sessions", 0)),
        float(aggregate_graph.get("entities", 0)),
        float(aggregate_graph.get("facts", 0)),
        float(edges.get("NEXT", 0) + edges.get("PREV", 0)),
        float(edges.get("MENTIONS", 0) + edges.get("ABOUT", 0) + edges.get("ASSERTS", 0) + edges.get("DERIVED_FROM", 0)),
        float(edges.get("SUPERSEDED_BY", 0) + edges.get("CONTRADICTS", 0)),
        float(edges.get("HAS_CASE", 0) + edges.get("CONTAINS", 0)),
        float(aggregate_graph.get("cases", 0))
    ]
    total = sum(counts)
    if total <= 0:
        p = [1.0 / len(buckets)] * len(buckets)
    else:
        p = [c / total for c in counts]
    return buckets, p

def compute_gibbs_g_star(stats: dict, tau: float = 0.5, gamma: float = 0.1, expansion_ratio: float = 0.0) -> dict:
    method_d = stats["methods"]["D"] if "methods" in stats else stats
    hit = method_d["hit_at_k"]["rate"]
    recall = method_d["mean_session_recall_at_k"]
    path_cov = method_d["evidence_path_coverage_mean"]
    
    retrieval_error = 1.0 - hit
    miss_rate = 1.0 - recall
    u_star = (0.4 * retrieval_error) + (0.4 * miss_rate) + (0.2 * (1.0 - path_cov))
    s_useful = recall
    s_irrelevant = expansion_ratio
    
    g_star = u_star - (tau * s_useful) + (gamma * s_irrelevant)
    return {
        "U_star": round(u_star, 4),
        "S_useful": round(s_useful, 4),
        "S_irrelevant": round(s_irrelevant, 4),
        "G_star": round(g_star, 4),
        "tau": tau,
        "gamma": gamma,
        "hit_at_k": hit,
        "session_recall_at_k": recall,
        "evidence_path_coverage": path_cov
    }

def cohen_kappa(labels1: list[str], labels2: list[str]) -> float:
    if not labels1 or len(labels1) != len(labels2):
        return 0.0
    n = len(labels1)
    cats = sorted(list(set(labels1 + labels2)))
    if len(cats) <= 1:
        return 1.0
    po = sum(1.0 for a, b in zip(labels1, labels2) if a == b) / n
    pe = sum((labels1.count(c) / n) * (labels2.count(c) / n) for c in cats)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1.0 - pe)

# --- Local Ollarma API Bridge ---

def query_ollarma_model(prompt: str, model_name: str, base_url: str = "http://localhost:11434", timeout: int = 45) -> dict:
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 256}
    }
    raw_prompt = canon(payload)
    prompt_sha = sha_text(raw_prompt)
    
    req = urllib.request.Request(
        f"{base_url}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    start_t = datetime.datetime.now(datetime.timezone.utc)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            resp_text = str(data.get("response", "")).strip()
            resp_sha = sha_text(resp_text)
            
            # Extract structured JSON if model output contains it
            structured = {}
            if "```" in resp_text:
                lines = [l for l in resp_text.splitlines() if not l.strip().startswith("```")]
                clean_str = "\n".join(lines).strip()
            else:
                clean_str = resp_text
            try:
                lo, hi = clean_str.find("{"), clean_str.rfind("}")
                if lo >= 0 and hi > lo:
                    structured = json.loads(clean_str[lo:hi+1])
            except Exception:
                structured = {}
                
            return {
                "status": "PASS",
                "model": model_name,
                "prompt_sha256": prompt_sha,
                "response_sha256": resp_sha,
                "response_text": resp_text[:1000],
                "structured": structured,
                "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
                "duration_ms": (datetime.datetime.now(datetime.timezone.utc) - start_t).total_seconds() * 1000
            }
    except Exception as exc:
        return {
            "status": "FAIL",
            "model": model_name,
            "prompt_sha256": prompt_sha,
            "response_sha256": None,
            "error": str(exc)[:300],
            "evidence_class": "PROBABILISTIC_MODEL_OUTPUT_ERROR"
        }

if __name__ == "__main__":
    print("HydraDG Iceberg & Ollarma Evaluator module loaded successfully.")
