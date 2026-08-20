"""Analyze HydraDG Modal receipts from files and/or directories.

Examples:
  python scripts/analyze_modal_receipts.py modal_runs_v3 \
    --out eval/modal_quick_full_analysis.json \
    --seedgraph-out seedgraph/modal_quick

  python scripts/analyze_modal_receipts.py /path/to/t4_a.receipt.json /path/to/l4_a.receipt.json \
    --out eval/two_run_analysis.json \
    --seedgraph-out seedgraph/two_run

Directories are recursively searched for `*.receipt.json`.
"""
from __future__ import annotations
import argparse, json
from itertools import combinations
from pathlib import Path

def discover(inputs):
    found = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            found.extend(sorted(p.rglob("*.receipt.json")))
        elif p.is_file():
            found.append(p)
        else:
            raise FileNotFoundError(f"Input not found: {p}")
    # Deduplicate by resolved path.
    uniq = []
    seen = set()
    for p in found:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key); uniq.append(p)
    if not uniq:
        raise FileNotFoundError("No *.receipt.json files discovered")
    return uniq

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def gpu_uuid(r):
    smi = r.get("environment", {}).get("nvidia_smi", "")
    return smi.split(",")[0].strip() if smi else None

def first_step_divergence(a, b):
    ra = {int(x["step"]): x for x in a.get("records", [])}
    rb = {int(x["step"]): x for x in b.get("records", [])}
    for step in sorted(set(ra) & set(rb)):
        xa, xb = ra[step], rb[step]
        if xa.get("state_hash") != xb.get("state_hash"):
            la, lb = xa.get("probe_top_logits", []), xb.get("probe_top_logits", [])
            return {
                "step": step,
                "scale": "CANONICAL_MODEL_STATE_HASH",
                "state_hash_a": xa.get("state_hash"),
                "state_hash_b": xb.get("state_hash"),
                "loss_abs_delta": abs(float(xa.get("loss", 0.0))-float(xb.get("loss", 0.0))),
                "probe_top_ids_equal": xa.get("probe_top_ids") == xb.get("probe_top_ids"),
                "probe_top_logits_max_abs_delta": max([abs(float(x)-float(y)) for x,y in zip(la,lb)] or [0.0]),
            }
    if len(ra) != len(rb):
        return {"step": None, "scale": "RECORD_LENGTH", "steps_a": len(ra), "steps_b": len(rb)}
    return None

def compare(a, b):
    fd = first_step_divergence(a, b)
    ea, eb = a.get("environment", {}), b.get("environment", {})
    return {
        "run_a": a["run_id"], "run_b": b["run_id"],
        "gpu_a": ea.get("gpu_name"), "gpu_b": eb.get("gpu_name"),
        "gpu_uuid_a": gpu_uuid(a), "gpu_uuid_b": gpu_uuid(b),
        "same_gpu_uuid": gpu_uuid(a) == gpu_uuid(b),
        "model_config_equal": a.get("model_config_sha256") == b.get("model_config_sha256"),
        "final_canonical_state_equal": a.get("final_state_hash") == b.get("final_state_hash"),
        "checkpoint_file_bytes_equal": a.get("checkpoint_file_sha256") == b.get("checkpoint_file_sha256"),
        "torch_num_threads": [ea.get("torch_num_threads"), eb.get("torch_num_threads")],
        "torch_num_interop_threads": [ea.get("torch_num_interop_threads"), eb.get("torch_num_interop_threads")],
        "environment_thread_config_equal": (
            ea.get("torch_num_threads") == eb.get("torch_num_threads")
            and ea.get("torch_num_interop_threads") == eb.get("torch_num_interop_threads")
        ),
        "first_observed_divergence": fd,
        "perturbation_a": a.get("perturbation_receipt"),
        "perturbation_b": b.get("perturbation_receipt"),
    }

def write_seedgraph(receipts, comparisons, prefix):
    nodes=[]; edges=[]
    for r in receipts:
        rid=f"run:{r['run_id']}"
        nodes.append({
            "id":rid,"type":"Run","evidence_class":"EXECUTION_EVIDENCE",
            "claim_ceiling":"BOUNDED_EXECUTION_RECEIPT","visibility":"PUBLIC",
            "metadata":{
                "gpu_name":r.get("environment",{}).get("gpu_name"),
                "gpu_uuid":gpu_uuid(r),
                "final_state_hash":r.get("final_state_hash"),
                "checkpoint_file_sha256":r.get("checkpoint_file_sha256"),
                "model_config_sha256":r.get("model_config_sha256"),
                "torch_num_threads":r.get("environment",{}).get("torch_num_threads"),
                "torch_num_interop_threads":r.get("environment",{}).get("torch_num_interop_threads"),
                "perturbation_receipt":r.get("perturbation_receipt"),
            }
        })
    for c in comparisons:
        cid=f"comparison:{c['run_a']}:{c['run_b']}"
        nodes.append({"id":cid,"type":"Evaluation","evidence_class":"DETERMINISTIC_TRANSFORMATION",
                      "claim_ceiling":"BOUNDED_REPLAY_COMPARISON","visibility":"PUBLIC","metadata":c})
        edges.append({"src":f"run:{c['run_a']}","rel":"DEPENDS_ON","dst":cid,"metadata":{"role":"input_a"}})
        edges.append({"src":f"run:{c['run_b']}","rel":"DEPENDS_ON","dst":cid,"metadata":{"role":"input_b"}})
        if c["first_observed_divergence"] is not None:
            d=c["first_observed_divergence"]
            did=f"divergence:{c['run_a']}:{c['run_b']}:{d.get('step')}"
            nodes.append({"id":did,"type":"Perturbation","evidence_class":"DERIVED_EVIDENCE",
                          "claim_ceiling":"FIRST_OBSERVED_DIVERGENCE","visibility":"PUBLIC","metadata":d})
            edges.append({"src":cid,"rel":"FIRST_DIVERGED_AT","dst":did,"metadata":{}})
    p=Path(prefix); p.parent.mkdir(parents=True,exist_ok=True)
    p.with_suffix(".nodes.jsonl").write_text(
        "".join(json.dumps(x,sort_keys=True,separators=(",",":"))+"\n" for x in nodes),encoding="utf-8")
    p.with_suffix(".edges.jsonl").write_text(
        "".join(json.dumps(x,sort_keys=True,separators=(",",":"))+"\n" for x in edges),encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="Receipt files and/or directories")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seedgraph-out", required=True)
    args=ap.parse_args()

    paths=discover(args.inputs)
    receipts=[load(p) for p in paths]
    comparisons=[compare(a,b) for a,b in combinations(receipts,2)]
    result={
        "receipt_paths":[str(p) for p in paths],
        "runs":[r["run_id"] for r in receipts],
        "comparisons":comparisons,
        "claim_rule":"First observed difference is not automatically causal mechanism.",
        "artifact_rule":"Raw checkpoint-file identity is separate from canonical model-state identity."
    }
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    write_seedgraph(receipts,comparisons,args.seedgraph_out)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
