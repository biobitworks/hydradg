"""Download the official cleaned LongMemEval-S release, verify SHA-256, then ingest to SeedGraph.

Source:
https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/
Expected SHA-256 is taken from the Hugging Face file page inspected 2026-08-16.

This script performs an actual hash verification when executed; the presence of this
script is not itself evidence that the dataset was downloaded or verified.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, urllib.request
from pathlib import Path

URL = "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json?download=true"
EXPECTED_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"

def sha256_file(path: Path, block=8*1024*1024):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(block)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/longmemeval_s_cleaned.json")
    ap.add_argument("--out", default="seedgraph/lme_s")
    ap.add_argument("--importer", default="scripts/ingest_longmemeval.py")
    ap.add_argument("--skip-download", action="store_true")
    args = ap.parse_args()

    data = Path(args.data)
    data.parent.mkdir(parents=True, exist_ok=True)
    if not args.skip_download:
        print("downloading", URL)
        urllib.request.urlretrieve(URL, data)

    actual = sha256_file(data)
    print(json.dumps({"path":str(data),"sha256":actual,"expected":EXPECTED_SHA256}, indent=2))
    if actual != EXPECTED_SHA256:
        raise SystemExit("SHA-256 mismatch: refusing ingestion")

    subprocess.run(
        [sys.executable, args.importer, "--input", str(data), "--out", args.out],
        check=True,
    )

if __name__ == "__main__":
    main()
