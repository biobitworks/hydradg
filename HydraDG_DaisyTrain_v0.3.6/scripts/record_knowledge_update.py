import os
from pathlib import Path
import argparse,json
from fco_live_common import add_node,add_edge,sha_file,utcnow

ap=argparse.ArgumentParser()
ap.add_argument("--graph-dir",default=os.environ.get("HYDRADG_LIVE_GRAPH_DIR","custody/live"))
ap.add_argument("--turn-id",required=True)
ap.add_argument("--update-file",required=True,
                help="JSON object with update_type, admission_state, claim_ceiling, uncertainty, atoms[]")
args=ap.parse_args()

p=Path(args.update_file)
if not p.is_file(): raise FileNotFoundError(args.update_file)
obj=json.loads(p.read_text())

for k in ["update_type","admission_state","claim_ceiling","uncertainty"]:
    if k not in obj: raise ValueError(f"missing {k}")

atoms=[]
for a in obj.get("atoms",[]):
    payload={
      "content":a.get("content"),"source_ref":a.get("source_ref"),
      "evidence_class":a.get("evidence_class","MODEL_GENERATED"),
      "claim_ceiling":a.get("claim_ceiling",obj["claim_ceiling"]),
      "uncertainty":a.get("uncertainty",obj["uncertainty"]),
      "custody_state":"HASHED"
    }
    aid=add_node(args.graph_dir,"KnowledgeAtom",payload)
    atoms.append(aid)

update_payload={
 "update_type":obj["update_type"],"admission_state":obj["admission_state"],
 "claim_ceiling":obj["claim_ceiling"],"uncertainty":obj["uncertainty"],
 "timestamp_utc":utcnow(),"source_file_sha256":sha_file(p),
 "custody_state":"HASHED"
}
uid=add_node(args.graph_dir,"KnowledgeUpdate",update_payload)
add_edge(args.graph_dir,args.turn_id,"UPDATES_KNOWLEDGE",uid)
for aid in atoms:
    add_edge(args.graph_dir,uid,"HAS_ATOM",aid)

for prior in obj.get("supersedes",[]):
    add_edge(args.graph_dir,prior,"SUPERSEDED_BY",uid)
for prior in obj.get("contradicts",[]):
    add_edge(args.graph_dir,uid,"CONTRADICTS",prior)

rel={
 "ADMIT":"ADMITTED_AS","REJECT":"REJECTED_AS","CHALLENGE":"CHALLENGED_AS",
 "ABSTAIN":"CHALLENGED_AS"
}.get(str(obj["admission_state"]).upper(),"CHALLENGED_AS")
decision=add_node(args.graph_dir,"AdmissionDecision",{
 "state":obj["admission_state"],"claim_ceiling":obj["claim_ceiling"],
 "custody_state":"HASHED"
})
add_edge(args.graph_dir,uid,rel,decision)
print(json.dumps({"knowledge_update_id":uid,"atom_ids":atoms,
                  "admission_decision_id":decision},indent=2,sort_keys=True))
