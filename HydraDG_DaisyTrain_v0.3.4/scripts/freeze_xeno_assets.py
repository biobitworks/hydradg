from pathlib import Path
import argparse, hashlib, json, datetime

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("--harness", required=True)
ap.add_argument("--checkpoint", required=True)
ap.add_argument("--table", required=True)
ap.add_argument("--contract", required=True)
ap.add_argument("--out", required=True)
args=ap.parse_args()

files = {
    "HARNESS": Path(args.harness).resolve(),
    "CHECKPOINT": Path(args.checkpoint).resolve(),
    "TABLE": Path(args.table).resolve(),
    "CONTRACT": Path(args.contract).resolve()
}
for k,p in files.items():
    if not p.is_file():
        raise FileNotFoundError(f"{k}: {p}")

contract=json.loads(files["CONTRACT"].read_text())
argv=contract.get("argv", [])
if not argv or any("REPLACE_WITH" in str(x) for x in argv):
    raise RuntimeError("run_contract.json is still a template; freeze exact argv first")

manifest={
  "schema":"hydradg.xeno_asset_freeze.v1",
  "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "assets":{k:{"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size} for k,p in files.items()},
  "contract":contract,
  "claim_boundary":"Frozen local assets. Historical identity requires separate evidence."
}
out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
print(json.dumps(manifest,indent=2,sort_keys=True))
