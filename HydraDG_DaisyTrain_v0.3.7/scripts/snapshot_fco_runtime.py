#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,datetime,os

def sha(p):
    p=Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None

ap=argparse.ArgumentParser()
ap.add_argument("--graph-dir",default=os.environ.get("HYDRADG_LIVE_GRAPH_DIR","custody/live"))
ap.add_argument("--out",default="handoff/FCO_RUNTIME_SNAPSHOT.json")
args=ap.parse_args()
g=Path(args.graph_dir)
types={}
for line in (g/"nodes.jsonl").read_text().splitlines() if (g/"nodes.jsonl").exists() else []:
    if not line.strip():continue
    r=json.loads(line); types[r["type"]]=types.get(r["type"],0)+1
obj={
 "schema":"hydradg.fco_runtime_snapshot.v1",
 "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "graph_dir":str(g),"type_counts":types,
 "nodes_sha256":sha(g/"nodes.jsonl"),"edges_sha256":sha(g/"edges.jsonl"),
}
Path(args.out).parent.mkdir(parents=True,exist_ok=True)
Path(args.out).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(obj,indent=2,sort_keys=True))
