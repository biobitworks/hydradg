import os
from pathlib import Path
import argparse,json
from fco_live_common import add_node,add_edge,sha_file,utcnow

ap=argparse.ArgumentParser()
ap.add_argument("--graph-dir",default=os.environ.get("HYDRADG_LIVE_GRAPH_DIR","custody/live"))
ap.add_argument("--agent-key",required=True)
ap.add_argument("--agent-role",required=True)
ap.add_argument("--agent-runtime",required=True)
ap.add_argument("--model-key",required=True)
ap.add_argument("--model-provider",required=True)
ap.add_argument("--model-name",required=True)
ap.add_argument("--model-version",default="UNRESOLVED")
ap.add_argument("--session-key",required=True)
ap.add_argument("--turn-index",required=True,type=int)
ap.add_argument("--input-file",required=True)
ap.add_argument("--output-file",required=True)
ap.add_argument("--previous-turn-id")
ap.add_argument("--claim-ceiling",default="MODEL_GENERATED")
ap.add_argument("--evidence-class",default="MODEL_GENERATED")
ap.add_argument("--context-file")
args=ap.parse_args()

for p in [args.input_file,args.output_file]:
    if not Path(p).is_file(): raise FileNotFoundError(p)

agent_payload={
 "agent_key":args.agent_key,"role":args.agent_role,"runtime":args.agent_runtime,
 "authorship":"AI_AGENT","claim_ceiling":"AGENT_IDENTITY_RECORD",
 "custody_state":"HASHED"
}
agent=add_node(args.graph_dir,"Agent",agent_payload)

model_payload={
 "model_key":args.model_key,"provider":args.model_provider,"model_name":args.model_name,
 "version_or_digest":args.model_version,"claim_ceiling":"MODEL_IDENTITY_RECORD",
 "custody_state":"HASHED"
}
model=add_node(args.graph_dir,"Model",model_payload)

session_payload={
 "session_key":args.session_key,"agent_key":args.agent_key,
 "claim_ceiling":"SESSION_PROVENANCE","custody_state":"HASHED"
}
session=add_node(args.graph_dir,"AgentSession",session_payload)
add_edge(args.graph_dir,agent,"HAS_SESSION",session)
add_edge(args.graph_dir,session,"USES_MODEL",model)

inp_payload={"path":str(Path(args.input_file)),"sha256":sha_file(args.input_file),
             "bytes":Path(args.input_file).stat().st_size,"role":"TURN_INPUT"}
out_payload={"path":str(Path(args.output_file)),"sha256":sha_file(args.output_file),
             "bytes":Path(args.output_file).stat().st_size,"role":"TURN_OUTPUT"}
inp=add_node(args.graph_dir,"Artifact",inp_payload)
out=add_node(args.graph_dir,"Artifact",out_payload)

turn_payload={
 "turn_index":args.turn_index,"timestamp_utc":utcnow(),
 "input_sha256":inp_payload["sha256"],"output_sha256":out_payload["sha256"],
 "evidence_class":args.evidence_class,"claim_ceiling":args.claim_ceiling,
 "custody_state":"HASHED"
}
if args.context_file:
    if not Path(args.context_file).is_file(): raise FileNotFoundError(args.context_file)
    turn_payload["context_sha256"]=sha_file(args.context_file)

turn=add_node(args.graph_dir,"Turn",turn_payload)
inv=add_node(args.graph_dir,"ModelInvocation",{
 "model_id":model,"turn_id":turn,"claim_ceiling":args.claim_ceiling,
 "custody_state":"HASHED"
})

add_edge(args.graph_dir,session,"HAS_TURN",turn)
add_edge(args.graph_dir,turn,"DERIVED_FROM",inp)
add_edge(args.graph_dir,turn,"PRODUCED",out)
add_edge(args.graph_dir,turn,"INVOKED_MODEL",model)
add_edge(args.graph_dir,turn,"DESCRIBES",inv)
if args.previous_turn_id:
    add_edge(args.graph_dir,args.previous_turn_id,"FOLLOWS_TURN",turn)

result={"agent_id":agent,"model_id":model,"session_id":session,"turn_id":turn,
        "input_artifact_id":inp,"output_artifact_id":out,"invocation_id":inv}
print(json.dumps(result,indent=2,sort_keys=True))
