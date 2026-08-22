#!/usr/bin/env python3
"""Normalize an existing atom-context score artifact for SeedGraph without inference.

Accepted bindings must already contain an explicit canonical_key or seed_atom_id.
This adapter never derives semantic keys from prose and never invents scores.
"""
from __future__ import annotations
import argparse, hashlib, json, math, time
from pathlib import Path
from typing import Any

NUMERIC_FIELDS=("context_score","g_star","delta_g_star","cloud_drift_0_100","shannon_entropy","normalized_entropy","mutation_distance","restoration_gain","burden")
KEY_FIELDS=("canonical_key","seed_atom_id")

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def load_rows(p:Path)->list[dict[str,Any]]:
    s=p.suffix.lower()
    if s==".jsonl":return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
    if s==".json":
        x=json.loads(p.read_text())
        if isinstance(x,list):return x
        for k in ("atoms","rows","nodes","scores","records"):
            if isinstance(x.get(k),list):return x[k]
        raise ValueError("JSON_HAS_NO_ROW_LIST")
    if s in {".parquet",".pq"}:
        import pandas as pd
        return pd.read_parquet(p).to_dict("records")
    raise ValueError(f"UNSUPPORTED_SCORE_SOURCE:{s}")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source",required=True);ap.add_argument("--output-jsonl",required=True);ap.add_argument("--receipt",required=True);a=ap.parse_args();p=Path(a.source);raw=p.read_bytes();rows=load_rows(p);out=[];rejected=[];binding=None
    for k in KEY_FIELDS:
        if any(r.get(k) not in (None,"") for r in rows):binding=k;break
    if not binding:
        state="BLOCKED_NO_EXPLICIT_SEED_BINDING"
    else:
        state="AVAILABLE"
        for i,r in enumerate(rows):
            key=r.get(binding)
            if key in (None,""):rejected.append({"row":i,"reason":"MISSING_BINDING"});continue
            nr={binding:str(key)};numeric_count=0
            for f in NUMERIC_FIELDS:
                v=r.get(f)
                if isinstance(v,(int,float)) and math.isfinite(float(v)):nr[f]=float(v);numeric_count+=1
            if not numeric_count:rejected.append({"row":i,"reason":"NO_NUMERIC_CONTEXT_SCORE_FIELDS"});continue
            if binding=="seed_atom_id" and r.get("canonical_key"):nr["canonical_key"]=str(r["canonical_key"])
            if binding=="canonical_key":nr["canonical_key"]=str(key)
            nr["source_score_artifact_sha256"]=sha(raw);nr["evidence_class"]="EXTERNALLY_RETRIEVED_EVIDENCE_OR_RECOMPUTED_RESULT_AS_SOURCE_CLASSIFIED_UPSTREAM";out.append(nr)
        if not out:state="BLOCKED_NO_USABLE_BOUND_SCORE_ROWS"
    op=Path(a.output_jsonl);op.parent.mkdir(parents=True,exist_ok=True)
    op.write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in out))
    rec={"schema":"hydradg.seedgraph.score_adapter_receipt.v1","source_path":str(p),"source_sha256":sha(raw),"binding_field":binding,"input_rows":len(rows),"output_rows":len(out),"rejected_rows":len(rejected),"state":state,"zero_model_calls":True,"zero_network_calls":True,"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())};rec["normalized_jsonl_sha256"]=sha(op.read_bytes());rec["receipt_sha256"]=sha(json.dumps(rec,sort_keys=True,separators=(",",":")).encode());Path(a.receipt).write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n");print(json.dumps(rec,indent=2,sort_keys=True))
if __name__=="__main__":main()
