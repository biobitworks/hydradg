from pathlib import Path
import argparse,hashlib,urllib.request,json

DEFAULT_URL="https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json"
# Previously observed object hash in the project. Mismatch fails closed and requires source review.
DEFAULT_EXPECTED="d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"

ap=argparse.ArgumentParser()
ap.add_argument("--url",default=DEFAULT_URL)
ap.add_argument("--expected-sha256",default=DEFAULT_EXPECTED)
ap.add_argument("--out",required=True)
args=ap.parse_args()
out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
with urllib.request.urlopen(args.url,timeout=120) as r:
    b=r.read()
got=hashlib.sha256(b).hexdigest()
if got!=args.expected_sha256:
    raise SystemExit(f"FAIL SHA256: got {got}; expected {args.expected_sha256}. Review upstream object; do not silently accept.")
out.write_bytes(b)
data=json.loads(b)
print(json.dumps({"status":"PASS","sha256":got,"items":len(data),"path":str(out)},indent=2))
