#!/usr/bin/env python3
"""
Deterministically materialize the current heuristic_v2 extraction as explicit
SeedGraph/FCO/FCG sidecars plus a frozen extraction cache consumable by the
existing HydraDG typed runner.

This does NOT use Ollarma and does NOT promote extracted statements to truth.
"""
import argparse, hashlib, json, sys
from pathlib import Path

def canon(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def sha_text(s): return hashlib.sha256(s.encode()).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("--raw", default="HydraDG_DaisyTrain_v0.3.7/evidence/track03/matrix-20260819/frozen/longmemeval_full500.raw.json")
ap.add_argument("--outdir", default="HydraDG_DaisyTrain_v0.3.7/evidence/track03/matrix-20260819/seedgraph")
ap.add_argument("--scripts-dir", default="HydraDG_DaisyTrain_v0.3.7/scripts")
args=ap.parse_args()

sys.path.insert(0,str(Path(args.scripts_dir).resolve()))
from best_use_typed_graph import heuristic_extract, session_text

rawp=Path(args.raw)
data=json.loads(rawp.read_bytes())
outdir=Path(args.outdir); cache=outdir/"cache"
outdir.mkdir(parents=True,exist_ok=True); cache.mkdir(parents=True,exist_ok=True)

fcos=[]
edges=[]
cache_files=[]
for case in data:
    qid=str(case["question_id"])
    sids=[str(x) for x in case["haystack_session_ids"]]
    sessions=case["haystack_sessions"]
    if len(sids)!=len(sessions): raise SystemExit(f"{qid}: session mismatch")
    for pos,(sid,sess) in enumerate(zip(sids,sessions)):
        text=session_text(sess)
        source_sha=sha_text(text)
        ext=heuristic_extract(text)
        cache_key=sha_text(f"heuristic||{source_sha}")
        ext.update({
            "source_sha256":source_sha,
            "cache_key":cache_key,
            "cache_hit":False,
            "seedgraph_state":"DETERMINISTIC_MATERIALIZED",
        })
        cp=cache/f"{cache_key}.json"
        cp.write_text(json.dumps(ext,indent=2,sort_keys=True)+"\n")
        cache_files.append(cp)

        payload={
            "schema":"hydradg.seedgraph_fco_session.v1",
            "question_id":qid,
            "session_id":sid,
            "position":pos,
            "source_sha256":source_sha,
            "extractor":"heuristic_v2",
            "evidence_class":"DETERMINISTIC_HEURISTIC_EXTRACTION",
            "entities":ext.get("entities",[]),
            "facts":ext.get("facts",[]),
            "claim_ceiling":"DETERMINISTIC_TRANSFORMATION_NOT_FACTUAL_VALIDATION",
        }
        fco_root=sha_text(canon(payload))
        fco=dict(payload); fco["fco_root_sha256"]=fco_root
        fcos.append(fco)
        edges.append({
            "schema":"hydradg.fcg_edge.v1",
            "source":f"fco:{fco_root}",
            "predicate":"DERIVED_FROM",
            "target":f"source_sha256:{source_sha}",
            "evidence_class":"DETERMINISTIC_TRANSFORMATION",
        })

fco_path=outdir/"fco_sessions.jsonl"
edge_path=outdir/"fcg_edges.jsonl"
fco_path.write_text("".join(canon(x)+"\n" for x in fcos))
edge_path.write_text("".join(canon(x)+"\n" for x in edges))

cache_index=[]
for p in sorted(cache_files,key=lambda x:x.name):
    cache_index.append({"file":p.name,"sha256":sha_file(p)})
cache_manifest={"schema":"hydradg.seedgraph_cache_manifest.v1","files":cache_index}
cache_manifest_sha=sha_text(canon(cache_manifest))
cache_manifest["cache_manifest_root_sha256"]=cache_manifest_sha
(outdir/"cache_manifest.json").write_text(json.dumps(cache_manifest,indent=2,sort_keys=True)+"\n")

root_obj={
 "schema":"hydradg.seedgraph_fco_fcg_freeze.v1",
 "raw_source_sha256":sha_file(rawp),
 "fco_sessions_sha256":sha_file(fco_path),
 "fcg_edges_sha256":sha_file(edge_path),
 "cache_manifest_sha256":sha_file(outdir/"cache_manifest.json"),
 "session_fco_count":len(fcos),
 "edge_count":len(edges),
 "transform":"heuristic_v2",
 "evidence_class":"DETERMINISTIC_TRANSFORMATION",
 "claim_ceiling":"TRANSFORMED_EVAL_INPUT_NOT_FACTUAL_VALIDATION",
}
root_sha=sha_text(canon(root_obj))
root_obj["seedgraph_fco_fcg_root_sha256"]=root_sha
(outdir/"SEEDGRAPH_FCO_FCG_FREEZE_MANIFEST.json").write_text(json.dumps(root_obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(root_obj,indent=2,sort_keys=True))
