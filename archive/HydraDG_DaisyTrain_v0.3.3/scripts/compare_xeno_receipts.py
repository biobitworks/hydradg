from pathlib import Path
import argparse,json,math

ap=argparse.ArgumentParser()
ap.add_argument("local")
ap.add_argument("modal")
ap.add_argument("--out",required=True)
ap.add_argument("--epsilon",type=float,default=1e-8)
args=ap.parse_args()
a=json.loads(Path(args.local).read_text()); b=json.loads(Path(args.modal).read_text())

def numeric_leaves(x,path=""):
    out={}
    if isinstance(x,dict):
        for k,v in x.items(): out.update(numeric_leaves(v,f"{path}/{k}"))
    elif isinstance(x,list):
        for i,v in enumerate(x): out.update(numeric_leaves(v,f"{path}/{i}"))
    elif isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(float(x)):
        out[path]=float(x)
    return out

na=numeric_leaves(a.get("metrics",{})); nb=numeric_leaves(b.get("metrics",{}))
common=sorted(set(na)&set(nb))
deltas={k:abs(na[k]-nb[k]) for k in common}
same_inputs=a.get("input_sha256")==b.get("input_sha256")
same_output_hashes=a.get("outputs")==b.get("outputs")
result={
  "schema":"hydradg.xeno_local_modal_comparison.v1",
  "same_frozen_input_hashes":same_inputs,
  "same_output_file_manifest":same_output_hashes,
  "numeric_metric_common_leaves":len(common),
  "numeric_metric_exact_matches":sum(d==0 for d in deltas.values()),
  "numeric_metric_epsilon_matches":sum(d<=args.epsilon for d in deltas.values()),
  "epsilon":args.epsilon,
  "max_abs_numeric_delta":max(deltas.values()) if deltas else None,
  "claim_ceiling":(
    "BOUNDED_SAME_ASSETS_CROSS_ENVIRONMENT_REPLAY"
    if same_inputs and a.get("returncode")==0 and b.get("returncode")==0
    else "REPLAY_DEPENDENCY_FAILURE"
  )
}
out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps(result,indent=2,sort_keys=True))
