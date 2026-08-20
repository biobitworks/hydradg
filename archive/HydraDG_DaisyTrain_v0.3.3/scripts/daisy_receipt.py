from pathlib import Path
import argparse, hashlib, json, datetime

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

ap = argparse.ArgumentParser()
ap.add_argument("--stage", required=True)
ap.add_argument("--input", action="append", default=[])
ap.add_argument("--output", action="append", default=[])
ap.add_argument("--receipt", required=True)
ap.add_argument("--parent")
ap.add_argument("--claim-ceiling", required=True)
args = ap.parse_args()

def items(paths):
    out=[]
    for raw in paths:
        p=Path(raw)
        if not p.is_file():
            raise FileNotFoundError(raw)
        out.append({"path":str(p), "sha256":sha(p), "bytes":p.stat().st_size})
    return out

parent_sha = sha(args.parent) if args.parent else None
body = {
    "schema":"hydradg.daisy_stage_receipt.v1",
    "stage":args.stage,
    "timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "inputs":items(args.input),
    "outputs":items(args.output),
    "parent_receipt_sha256":parent_sha,
    "claim_ceiling":args.claim_ceiling,
    "custody_state":"HASHED",
    "signature_state":"NOT_SIGNED",
    "merkle_state":"NOT_MERKLE_COMMITTED"
}
canonical=json.dumps(body, sort_keys=True, separators=(",",":")).encode()
body["receipt_body_sha256"]=hashlib.sha256(canonical).hexdigest()
p=Path(args.receipt); p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(body, indent=2, sort_keys=True)+"\n")
print(json.dumps(body, indent=2, sort_keys=True))
