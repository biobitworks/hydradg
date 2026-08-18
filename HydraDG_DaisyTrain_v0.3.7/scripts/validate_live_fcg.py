import os
from pathlib import Path
import argparse,json,sys

ap=argparse.ArgumentParser()
ap.add_argument("--graph-dir",default=os.environ.get("HYDRADG_LIVE_GRAPH_DIR","custody/live"))
args=ap.parse_args()
g=Path(args.graph_dir)
nodes={}
errors=[]
for line_no,line in enumerate((g/"nodes.jsonl").open(),1):
    try:r=json.loads(line)
    except Exception as e:
        errors.append(f"nodes:{line_no}:{e}"); continue
    if r["id"] in nodes and nodes[r["id"]] != r:
        errors.append(f"duplicate-conflict:{r['id']}")
    nodes[r["id"]]=r
edge_count=0
for line_no,line in enumerate((g/"edges.jsonl").open(),1):
    try:r=json.loads(line)
    except Exception as e:
        errors.append(f"edges:{line_no}:{e}"); continue
    edge_count+=1
    if r["src"] not in nodes:
        errors.append(f"missing-src:{r['src']}")
    if r["dst"] not in nodes:
        errors.append(f"missing-dst:{r['dst']}")
types={}
for r in nodes.values(): types[r["type"]]=types.get(r["type"],0)+1
out={"nodes":len(nodes),"edges":edge_count,"types":types,"errors":errors}
print(json.dumps(out,indent=2,sort_keys=True))
sys.exit(1 if errors else 0)
