from pathlib import Path
import argparse,json,hashlib,datetime

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

ap=argparse.ArgumentParser()
ap.add_argument("--artifact",action="append",required=True)
ap.add_argument("--outdir",required=True)
args=ap.parse_args()
out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
nodes=[]; edges=[]

def node(kind,payload,source_artifact=None):
    body={"type":kind,"payload":payload}
    oid="fco:"+sha_bytes(canon(body))
    rec={"id":oid,"object_sha256":oid.split(":",1)[1],"type":kind,"payload":payload}
    if source_artifact: rec["source_artifact"]=source_artifact
    nodes.append(rec); return oid

def edge(src,rel,dst,payload=None):
    body={"src":src,"rel":rel,"dst":dst,"payload":payload or {}}
    eid="fcg:"+sha_bytes(canon(body))
    edges.append({"id":eid,**body}); return eid

for raw in args.artifact:
    p=Path(raw)
    if not p.is_file():
        raise FileNotFoundError(raw)
    fhash=sha_file(p)
    aid=node("Artifact",{"path":str(p),"sha256":fhash,"bytes":p.stat().st_size})
    try: obj=json.loads(p.read_text())
    except Exception: continue

    if isinstance(obj,dict) and isinstance(obj.get("trajectories"),list):
        exp=node("Experiment",{"experiment_id":obj.get("experiment_id"),"summary":obj.get("summary")},aid)
        edge(aid,"DESCRIBES",exp)
        for i,r in enumerate(obj["trajectories"]):
            rid=node("Trajectory",{
              "index":i,"rule":r.get("rule"),"seed_index":r.get("seed_index"),
              "condition":r.get("condition"),"first_divergence_step":r.get("first_divergence_step"),
              "expected_first_divergence_step":r.get("expected_first_divergence_step"),
              "recovery_class":r.get("recovery_class")
            },aid)
            edge(exp,"HAS_TRAJECTORY",rid)
            if r.get("perturbation"):
                pid=node("Perturbation",r["perturbation"],aid)
                edge(rid,"PERTURBED_BY",pid)
                if r.get("first_divergence_step") is not None:
                    did=node("Divergence",{"step":r["first_divergence_step"]},aid)
                    edge(pid,"FIRST_DIVERGED_AT",did)
                    edge(rid,"HAS_DIVERGENCE",did)
            if r.get("recovery_class")=="STATE_EXACT":
                rec=node("Recovery",{"class":"STATE_EXACT","step":r.get("state_exact_recovery_step")},aid)
                edge(rid,"RECOVERED_BY",rec)

    if isinstance(obj,dict) and ("same_frozen_input_hashes" in obj or "max_abs_numeric_delta" in obj):
        cid=node("ReplayComparison",obj,aid); edge(aid,"DESCRIBES",cid)

    if isinstance(obj,dict) and isinstance(obj.get("phase_findings"),list):
        runset=node("ModelReplayExperiment",{"schema":obj.get("schema"),"execution":obj.get("execution")},aid)
        edge(aid,"DESCRIBES",runset)
        for finding in obj["phase_findings"]:
            fid=node("DivergenceFinding",finding,aid)
            edge(runset,"HAS_FINDING",fid)

with (out/"nodes.jsonl").open("w") as f:
    for x in nodes: f.write(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n")
with (out/"edges.jsonl").open("w") as f:
    for x in edges: f.write(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n")
manifest={
 "schema":"hydradg.fco_fcg_import.v0.3.1","nodes":len(nodes),"edges":len(edges),
 "nodes_sha256":sha_file(out/"nodes.jsonl"),"edges_sha256":sha_file(out/"edges.jsonl"),
 "signature_state":"NOT_SIGNED","merkle_state":"NOT_MERKLE_COMMITTED"
}
(out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
print(json.dumps(manifest,indent=2,sort_keys=True))
