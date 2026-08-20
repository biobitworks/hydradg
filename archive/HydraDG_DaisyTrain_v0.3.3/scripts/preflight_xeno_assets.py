from pathlib import Path
import argparse, json, hashlib
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("--manifest", required=True)
args=ap.parse_args()
m=json.loads(Path(args.manifest).read_text())
bad=[]
for name,rec in m["assets"].items():
    p=Path(rec["path"])
    if not p.is_file():
        bad.append((name,"MISSING"))
        continue
    got=sha(p)
    if got != rec["sha256"]:
        bad.append((name,got,rec["sha256"]))
if bad:
    print(json.dumps({"status":"FAIL","differences":bad},indent=2))
    raise SystemExit(1)
print("PASS: all frozen Xeno assets match manifest")
