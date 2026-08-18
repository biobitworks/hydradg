"""Analyze Modal HydraDG run receipts and emit divergence + SeedGraph evidence."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from itertools import combinations

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def first_step_divergence(a, b):
    ra = {int(x["step"]): x for x in a.get("records", [])}
    rb = {int(x["step"]): x for x in b.get("records", [])}
    common = sorted(set(ra) & set(rb))
    for step in common:
        xa, xb = ra[step], rb[step]
        if xa.get("state_hash") != xb.get("state_hash"):
            logits_a = xa.get("probe_top_logits", [])
            logits_b = xb.get("probe_top_logits", [])
            max_logit_delta = max([abs(float(x)-float(y)) for x,y in zip(logits_a, logits_b)] or [0.0])
            return {
                "step": step,
                "scale": "CANONICAL_MODEL_STATE_HASH",
                "a_state_hash": xa.get("state_hash"),
                "b_state_hash": xb.get("state_hash"),
                "loss_abs_delta": abs(float(xa.get("loss", 0.0))-float(xb.get("loss", 0.0))),
                "probe_top_ids_equal": xa.get("probe_top_ids") == xb.get("probe_top_ids"),
                "probe_top_logits_max_abs_delta": max_logit_delta,
            }
    if len(ra) != len(rb):
        return {"step": None, "scale": "RECORD_LENGTH", "a_steps": len(ra), "b_steps": len(rb)}
    return None

def gpu_uuid(r):
    smi = r.get("environment", {}).get("nvidia_smi", "")
    return smi.split(",")[0].strip() if smi else None

def compare(a, b):
    fd = first_step_divergence(a, b)
    return {
        "run_a": a["run_id"], "run_b": b["run_id"],
        "gpu_a": a.get("environment",{}).get("gpu_name"),
        "gpu_b": b.get("environment",{}).get("gpu_name"),
        "gpu_uuid_a": gpu_uuid(a), "gpu_uuid_b": gpu_uuid(b),
        "different_gpu_uuid": gpu_uuid(a) != gpu_uuid(b),
        "model_config_equal": a.get("model_config_sha256") == b.get("model_config_sha256"),
        "final_canonical_state_equal": a.get("final_state_hash") == b.get("final_state_hash"),
        "checkpoint_file_bytes_equal": a.get("checkpoint_file_sha256") == b.get("checkpoint_file_sha256"),
        "first_observed_divergence": fd,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipts", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seedgraph-out", required=True)
    args = ap.parse_args()
    rs = [load(p) for p in args.receipts]
    comps = [compare(a,b) for a,b in combinations(rs,2)]
    out = {"runs":[r["run_id"] for r in rs], "comparisons":comps,
           "warning":"Raw checkpoint byte equality is not canonical model-state equality."}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    nodes=[]; edges=[]
    for r in rs:
        nodes.append({"id":f"run:{r['run_id']}","type":"Run","evidence_class":"EXECUTION_EVIDENCE",
                      "claim_ceiling":"BOUNDED_EXECUTION_RECEIPT","visibility":"PUBLIC",
                      "metadata":{"gpu_name":r.get("environment",{}).get("gpu_name"),
                                  "gpu_uuid":gpu_uuid(r),
                                  "final_state_hash":r.get("final_state_hash"),
                                  "checkpoint_file_sha256":r.get("checkpoint_file_sha256"),
                                  "model_config_sha256":r.get("model_config_sha256"),
                                  "perturbation_receipt":r.get("perturbation_receipt")}})
    for c in comps:
        cid=f"comparison:{c['run_a']}:{c['run_b']}"
        nodes.append({"id":cid,"type":"Evaluation","evidence_class":"DETERMINISTIC_TRANSFORMATION",
                      "claim_ceiling":"BOUNDED_REPLAY_COMPARISON","visibility":"PUBLIC","metadata":c})
        edges.append({"src":f"run:{c['run_a']}","rel":"ANSWERED_BY","dst":cid,"metadata":{"role":"input_a"}})
        edges.append({"src":f"run:{c['run_b']}","rel":"ANSWERED_BY","dst":cid,"metadata":{"role":"input_b"}})
        if c["first_observed_divergence"] is not None:
            d=c["first_observed_divergence"]; did=f"divergence:{c['run_a']}:{c['run_b']}:{d.get('step')}"
            nodes.append({"id":did,"type":"Perturbation","evidence_class":"DERIVED_EVIDENCE",
                          "claim_ceiling":"FIRST_OBSERVED_DIVERGENCE","visibility":"PUBLIC","metadata":d})
            edges.append({"src":cid,"rel":"FIRST_DIVERGED_AT","dst":did,"metadata":{}})
    p=Path(args.seedgraph_out); p.parent.mkdir(parents=True,exist_ok=True)
    p.with_suffix(".nodes.jsonl").write_text("".join(json.dumps(x,sort_keys=True,separators=(",",":"))+"\n" for x in nodes),encoding="utf-8")
    p.with_suffix(".edges.jsonl").write_text("".join(json.dumps(x,sort_keys=True,separators=(",",":"))+"\n" for x in edges),encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
