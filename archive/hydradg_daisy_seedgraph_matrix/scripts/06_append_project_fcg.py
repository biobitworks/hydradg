#!/usr/bin/env python3
"""Append matrix experiment/result objects to local project FCG JSONL without claiming signature."""
import argparse, datetime, hashlib, json
from pathlib import Path

def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"))
def hid(kind,payload): return f"{kind}:{hashlib.sha256(canon(payload).encode()).hexdigest()}"

ap=argparse.ArgumentParser()
ap.add_argument("--comparison", default=str(Path.home()/".local/share/hydradg-best-use/eval/matrix-20260819/MATRIX_COMPARISON.json"))
ap.add_argument("--kg", default="/Users/byron/projects/active/hydradg/custody")
args=ap.parse_args()

comp=json.loads(Path(args.comparison).read_text())
kg=Path(args.kg); live=kg/"graph/live"; live.mkdir(parents=True,exist_ok=True)
nodes=live/"nodes.jsonl"; edges=live/"edges.jsonl"
ts=datetime.datetime.now(datetime.timezone.utc).isoformat()

experiment_payload={
 "schema":"hydradg.fcg_experiment.v1","name":"LongMemEval SeedGraph × K matrix",
 "matrix_root":comp["comparison_root_sha256"],
 "claim_ceiling":comp["claim_ceiling"],
 "signature_state":"NOT_SIGNED","merkle_state":"NOT_MERKLE_COMMITTED",
}
exp_id=hid("experiment",experiment_payload)
new_nodes=[{"id":exp_id,"type":"Experiment",**experiment_payload,"recorded_utc":ts}]
new_edges=[]

for cell,meta in sorted(comp["cells"].items()):
    payload={"schema":"hydradg.fcg_matrix_cell.v1","cell":cell,
             "deterministic":meta["deterministic"],
             "canonical_sha256":meta["canonical_hashes"][0]}
    cid=hid("matrix_cell",payload)
    new_nodes.append({"id":cid,"type":"MatrixCell",**payload,"recorded_utc":ts})
    new_edges.append({"source":exp_id,"predicate":"HAS_CELL","target":cid,
                      "evidence_class":"RECOMPUTED_MATRIX_RESULT"})

for name,val in sorted(comp["comparisons"].items()):
    payload={"schema":"hydradg.fcg_comparison.v1","name":name,**val,
             "claim_ceiling":"OBSERVED_DELTA_ONLY"}
    cid=hid("comparison",payload)
    new_nodes.append({"id":cid,"type":"Comparison",**payload,"recorded_utc":ts})
    new_edges.append({"source":exp_id,"predicate":"HAS_COMPARISON","target":cid,
                      "evidence_class":"DETERMINISTIC_DERIVATION"})

with nodes.open("a") as f:
    for n in new_nodes: f.write(canon(n)+"\n")
with edges.open("a") as f:
    for e in new_edges: f.write(canon(e)+"\n")

receipt={"schema":"hydradg.fcg_append_receipt.v1","experiment_id":exp_id,
         "nodes_appended":len(new_nodes),"edges_appended":len(new_edges),
         "nodes_path":str(nodes),"edges_path":str(edges),
         "comparison_root_sha256":comp["comparison_root_sha256"],
         "signature_state":"NOT_SIGNED","recorded_utc":ts}
rp=Path(args.comparison).with_name("FCG_APPEND_RECEIPT.json")
rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps(receipt,indent=2,sort_keys=True))
