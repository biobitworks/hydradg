#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,sys,datetime,os

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def shab(b): return hashlib.sha256(b).hexdigest()
def shaf(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("--graph-dir",default=os.environ.get("HYDRADG_LIVE_GRAPH_DIR","custody/live"))
ap.add_argument("--require-agent",action="store_true")
ap.add_argument("--require-model",action="store_true")
ap.add_argument("--require-turn",action="store_true")
ap.add_argument("--require-tool-action",action="store_true")
ap.add_argument("--require-knowledge-update",action="store_true")
ap.add_argument("--max-age-minutes",type=float,default=None)
args=ap.parse_args()
g=Path(args.graph_dir)
errors=[]; warnings=[]
nodes={}; edges={}
npath=g/"nodes.jsonl"; epath=g/"edges.jsonl"
if not npath.exists(): errors.append(f"missing {npath}")
if not epath.exists(): errors.append(f"missing {epath}")

if not errors:
    for i,line in enumerate(npath.read_text().splitlines(),1):
        if not line.strip(): continue
        try:r=json.loads(line)
        except Exception as e:
            errors.append(f"nodes line {i}: invalid JSON: {e}"); continue
        exp="fco:"+shab(canon({"type":r.get("type"),"payload":r.get("payload")}))
        if r.get("id")!=exp:
            errors.append(f"node id mismatch line {i}: {r.get('id')} != {exp}")
        if r.get("id") in nodes and nodes[r["id"]]!=r:
            errors.append(f"conflicting duplicate node {r['id']}")
        nodes[r.get("id")]=r
    for i,line in enumerate(epath.read_text().splitlines(),1):
        if not line.strip(): continue
        try:r=json.loads(line)
        except Exception as e:
            errors.append(f"edges line {i}: invalid JSON: {e}"); continue
        exp="fcg:"+shab(canon({"src":r.get("src"),"rel":r.get("rel"),
                              "dst":r.get("dst"),"payload":r.get("payload") or {}}))
        if r.get("id")!=exp:
            errors.append(f"edge id mismatch line {i}: {r.get('id')} != {exp}")
        if r.get("src") not in nodes: errors.append(f"edge missing src {r.get('src')}")
        if r.get("dst") not in nodes: errors.append(f"edge missing dst {r.get('dst')}")
        edges[r.get("id")]=r

types={}
for r in nodes.values():
    types[r.get("type")]=types.get(r.get("type"),0)+1

# Recompute artifact hashes wherever an artifact points to a currently existing file.
artifact_checks=0
for oid,r in nodes.items():
    if r.get("type")!="Artifact": continue
    p=(r.get("payload") or {}).get("path")
    expected=(r.get("payload") or {}).get("sha256")
    if p and expected and Path(p).is_file():
        artifact_checks+=1
        actual=shaf(p)
        if actual!=expected:
            errors.append(f"artifact hash mismatch {oid}: {p}")

# Edge indices.
outgoing={}
incoming={}
for e in edges.values():
    outgoing.setdefault(e["src"],[]).append(e)
    incoming.setdefault(e["dst"],[]).append(e)

# Structural checks for every Turn.
turn_ids=[oid for oid,r in nodes.items() if r.get("type")=="Turn"]
for tid in turn_ids:
    outs=outgoing.get(tid,[])
    ins=incoming.get(tid,[])
    rels_out=[x["rel"] for x in outs]
    rels_in=[x["rel"] for x in ins]
    if "DERIVED_FROM" not in rels_out: errors.append(f"Turn missing DERIVED_FROM: {tid}")
    if "PRODUCED" not in rels_out: errors.append(f"Turn missing PRODUCED: {tid}")
    if "INVOKED_MODEL" not in rels_out: errors.append(f"Turn missing INVOKED_MODEL: {tid}")
    if "HAS_TURN" not in rels_in: errors.append(f"Turn missing AgentSession HAS_TURN: {tid}")

# Required counts.
requirements={
 "Agent":args.require_agent,"Model":args.require_model,"Turn":args.require_turn,
 "ToolAction":args.require_tool_action,"KnowledgeUpdate":args.require_knowledge_update,
}
for typ,required in requirements.items():
    if required and types.get(typ,0)==0:
        errors.append(f"required type missing: {typ}")

# Recency check uses Turn timestamp_utc.
latest_turn=None
for tid in turn_ids:
    ts=(nodes[tid].get("payload") or {}).get("timestamp_utc")
    if not ts: continue
    try:
        dt=datetime.datetime.fromisoformat(ts.replace("Z","+00:00"))
        if latest_turn is None or dt>latest_turn: latest_turn=dt
    except Exception:
        warnings.append(f"unparseable Turn timestamp: {tid}")
if args.max_age_minutes is not None:
    if latest_turn is None:
        errors.append("no parseable Turn timestamp for recency check")
    else:
        now=datetime.datetime.now(datetime.timezone.utc)
        if latest_turn.tzinfo is None: latest_turn=latest_turn.replace(tzinfo=datetime.timezone.utc)
        age=(now-latest_turn.astimezone(datetime.timezone.utc)).total_seconds()/60
        if age>args.max_age_minutes:
            errors.append(f"latest Turn is stale: {age:.1f} min > {args.max_age_minutes}")

result={
 "schema":"hydradg.live_custody_verification.v1",
 "graph_dir":str(g),
 "status":"PASS" if not errors else "FAIL",
 "node_count":len(nodes),"edge_count":len(edges),
 "type_counts":types,
 "artifact_files_rehashed":artifact_checks,
 "nodes_jsonl_sha256":shaf(npath) if npath.exists() else None,
 "edges_jsonl_sha256":shaf(epath) if epath.exists() else None,
 "latest_turn_timestamp_utc":latest_turn.isoformat() if latest_turn else None,
 "errors":errors,"warnings":warnings,
 "claim_boundary":"PASS verifies the local FCO/FCG journal structure and hashes only; it does not prove skill invocation, correctness, signing, Merkle commitment, or HydraDB ingestion."
}
print(json.dumps(result,indent=2,sort_keys=True))
sys.exit(0 if not errors else 1)
