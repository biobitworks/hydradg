"""Localize first divergence across initialization, input, forward-loss, gradient, optimizer state."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from itertools import combinations

PHASES = [
    ("initial_model_state_hash", "INITIAL_MODEL_STATE"),
]

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def discover(inputs):
    out=[]
    for raw in inputs:
        p=Path(raw)
        if p.is_dir():
            out.extend(sorted(p.rglob("*.receipt.json")))
        elif p.is_file():
            out.append(p)
    if not out:
        raise FileNotFoundError("No receipt JSON files found")
    return out

def first_phase_divergence(a,b):
    if a.get("initial_model_state_hash") != b.get("initial_model_state_hash"):
        return {
            "step": -1,
            "phase": "INITIAL_MODEL_STATE",
            "a": a.get("initial_model_state_hash"),
            "b": b.get("initial_model_state_hash"),
        }

    ra={int(x["step"]):x for x in a.get("records",[])}
    rb={int(x["step"]):x for x in b.get("records",[])}
    for step in sorted(set(ra)&set(rb)):
        xa,xb=ra[step],rb[step]
        checks=[
            ("input_hash","INPUT_BATCH"),
            ("pre_step_state_hash","PRE_STEP_MODEL_STATE"),
            ("loss_float32_bits_hex","FORWARD_LOSS_FLOAT32"),
            ("gradient_hash","BACKWARD_GRADIENTS"),
            ("post_step_state_hash","POST_OPTIMIZER_MODEL_STATE"),
        ]
        for key,phase in checks:
            if xa.get(key) != xb.get(key):
                return {"step":step,"phase":phase,"a":xa.get(key),"b":xb.get(key)}
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    ps=discover(args.inputs)
    rs=[load(p) for p in ps]
    comps=[]
    for a,b in combinations(rs,2):
        comps.append({
            "run_a":a["run_id"],
            "run_b":b["run_id"],
            "first_phase_divergence":first_phase_divergence(a,b),
            "final_state_equal":a.get("final_state_hash")==b.get("final_state_hash"),
        })
    result={"runs":[r["run_id"] for r in rs],"comparisons":comps}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
