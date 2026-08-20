import os
from pathlib import Path
import argparse,json
from fco_live_common import add_node,add_edge,sha_file,utcnow

ap=argparse.ArgumentParser()
ap.add_argument("--graph-dir",default=os.environ.get("HYDRADG_LIVE_GRAPH_DIR","custody/live"))
ap.add_argument("--turn-id",required=True)
ap.add_argument("--tool",required=True)
ap.add_argument("--operation",required=True)
ap.add_argument("--log-file",required=True)
ap.add_argument("--exit-code",required=True,type=int)
ap.add_argument("--claim-ceiling",default="EXECUTION_RECEIPT")
args=ap.parse_args()
p=Path(args.log_file)
if not p.is_file(): raise FileNotFoundError(args.log_file)

art=add_node(args.graph_dir,"Artifact",{"path":str(p),"sha256":sha_file(p),
 "bytes":p.stat().st_size,"role":"TOOL_LOG"})
action=add_node(args.graph_dir,"ToolAction",{
 "tool":args.tool,"operation":args.operation,"timestamp_utc":utcnow(),
 "exit_code":args.exit_code,"claim_ceiling":args.claim_ceiling,
 "custody_state":"HASHED"
})
add_edge(args.graph_dir,args.turn_id,"USED_TOOL",action)
add_edge(args.graph_dir,action,"PRODUCED",art)
print(json.dumps({"tool_action_id":action,"artifact_id":art},indent=2,sort_keys=True))
