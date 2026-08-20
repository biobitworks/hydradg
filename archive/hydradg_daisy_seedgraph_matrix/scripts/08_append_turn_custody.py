#!/usr/bin/env python3
"""Create an append-only local turn-custody record from text files, ready for offline signing."""
import argparse,datetime,hashlib,json
from pathlib import Path
ap=argparse.ArgumentParser()
ap.add_argument("--user",required=True)
ap.add_argument("--assistant",required=True)
ap.add_argument("--out",default="/Users/byron/projects/active/hydradg/custody/turn_custody.jsonl")
args=ap.parse_args()
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base={
 "schema":"hydradg.turn_custody.v1",
 "user_input_sha256":h(args.user),
 "assistant_output_sha256":h(args.assistant),
 "recorded_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "signature_state":"PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
 "signing_key_ref":"~/.fco/keys/fcg_signing_ed25519.pem on magicPRObox",
 "algorithm":"Ed25519",
}
root=hashlib.sha256(json.dumps(base,sort_keys=True,separators=(",",":")).encode()).hexdigest()
base["turn_root_sha256"]=root
p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True)
with p.open("a") as f:f.write(json.dumps(base,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps(base,indent=2,sort_keys=True))
