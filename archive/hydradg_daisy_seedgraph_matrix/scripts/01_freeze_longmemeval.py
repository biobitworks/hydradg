#!/usr/bin/env python3
import argparse, hashlib, json, shutil, datetime
from pathlib import Path

EXPECTED = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("--source", default=str(Path.home()/".local/share/hydradg-best-use/data/longmemeval_s_cleaned.json"))
ap.add_argument("--outdir", default="HydraDG_DaisyTrain_v0.3.7/evidence/track03/matrix-20260819/frozen")
args=ap.parse_args()

src=Path(args.source)
outdir=Path(args.outdir)
outdir.mkdir(parents=True,exist_ok=True)
if not src.is_file(): raise SystemExit(f"missing source: {src}")
digest=sha(src)
if digest != EXPECTED: raise SystemExit(f"source SHA mismatch: {digest}")

raw=outdir/"longmemeval_full500.raw.json"
if raw.exists():
    if sha(raw)!=EXPECTED: raise SystemExit(f"existing frozen RAW mismatch: {raw}")
else:
    shutil.copy2(src,raw)

data=json.loads(raw.read_bytes())
if not isinstance(data,list) or len(data)!=500: raise SystemExit(f"expected 500 rows, got {len(data) if isinstance(data,list) else type(data)}")

canonical={
 "schema":"hydradg.dataset_freeze.v1",
 "dataset_id":"longmemeval-s-full500",
 "source_sha256":EXPECTED,
 "rows":500,
 "role":"EVAL_ONLY",
 "training_allowed":False,
 "evaluation_allowed":True,
}
root=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
manifest=dict(canonical)
manifest["dataset_root_sha256"]=root
manifest["frozen_path"]=str(raw)
manifest["bytes"]=raw.stat().st_size
manifest["created_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
(outdir/"RAW_FREEZE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
print(json.dumps(manifest,indent=2,sort_keys=True))
