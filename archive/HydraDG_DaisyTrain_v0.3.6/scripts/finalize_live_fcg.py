import os
from pathlib import Path
import argparse,hashlib,json

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument("--graph-dir",default=os.environ.get("HYDRADG_LIVE_GRAPH_DIR","custody/live"))
ap.add_argument("--out",default="custody/live/manifest.json")
args=ap.parse_args()
g=Path(args.graph_dir)
nodes=g/"nodes.jsonl"; edges=g/"edges.jsonl"
for p in [nodes,edges]:
    if not p.exists(): p.write_text("")
obj={
 "schema":"hydradg.live_fco_fcg_manifest.v1",
 "nodes":sum(1 for _ in nodes.open()),
 "edges":sum(1 for _ in edges.open()),
 "nodes_sha256":sha(nodes),"edges_sha256":sha(edges),
 "hydradb_state":"NOT_YET_INGESTED_UNLESS_SEPARATE_RECEIPT_EXISTS",
 "signature_state":"NOT_SIGNED","merkle_state":"NOT_MERKLE_COMMITTED"
}
Path(args.out).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(obj,indent=2,sort_keys=True))
