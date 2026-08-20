"""Locate the first parameter gradient whose canonical hash differs."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from itertools import combinations

def discover(inputs):
    out=[]
    for raw in inputs:
        p=Path(raw)
        if p.is_dir():
            out.extend(sorted(p.rglob("*.receipt.json")))
        elif p.is_file():
            out.append(p)
    if not out:
        raise FileNotFoundError("No receipts found")
    return out

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def first_parameter_gradient_divergence(a,b):
    ra={int(x["step"]):x for x in a.get("records",[])}
    rb={int(x["step"]):x for x in b.get("records",[])}
    for step in sorted(set(ra)&set(rb)):
        ga=ra[step].get("gradient_by_parameter",{})
        gb=rb[step].get("gradient_by_parameter",{})
        for name in sorted(set(ga)|set(gb)):
            xa,xb=ga.get(name),gb.get(name)
            if xa != xb:
                # Hash equality is the primary identity test. Stats are context.
                sha_a = xa.get("sha256") if isinstance(xa,dict) else None
                sha_b = xb.get("sha256") if isinstance(xb,dict) else None
                if sha_a != sha_b:
                    return {
                        "step":step,
                        "parameter":name,
                        "sha256_a":sha_a,
                        "sha256_b":sha_b,
                        "stats_a":xa,
                        "stats_b":xb,
                    }
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
            "first_parameter_gradient_divergence":
                first_parameter_gradient_divergence(a,b)
        })
    result={"runs":[r["run_id"] for r in rs],"comparisons":comps}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
