#!/usr/bin/env python3
"""Discover existing atom-context score artifacts without inference or semantic guessing."""
from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
from typing import Any

KEYS={"canonical_key","seed_atom_id"}
SCORES={"context_score","g_star","delta_g_star","cloud_drift_0_100","shannon_entropy","normalized_entropy","mutation_distance","restoration_gain","burden"}
MAX_BYTES=32*1024*1024

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
 return h.hexdigest()
def rows_from_json(x:Any)->list[dict[str,Any]]:
 if isinstance(x,list):return [r for r in x if isinstance(r,dict)][:500]
 if isinstance(x,dict):
  for k in ("atoms","nodes","rows","scores","records","events","objects"):
   if isinstance(x.get(k),list):return [r for r in x[k] if isinstance(r,dict)][:500]
  return [x]
 return []
def inspect(p:Path)->dict[str,Any]:
 rec={"path":str(p),"byte_size":p.stat().st_size,"sha256":sha(p),"format":p.suffix.lower(),"inspect_status":"UNINSPECTED","explicit_key_fields":[],"numeric_score_fields":[],"compatible":False}
 if p.stat().st_size>MAX_BYTES:rec["inspect_status"]="SKIPPED_OVER_32MB";return rec
 try:
  if p.suffix.lower()==".jsonl":
   rows=[]
   with p.open() as f:
    for i,line in enumerate(f):
     if i>=500:break
     if line.strip():
      x=json.loads(line)
      if isinstance(x,dict):rows.append(x)
  elif p.suffix.lower()==".json":rows=rows_from_json(json.loads(p.read_text()))
  elif p.suffix.lower() in {".parquet",".pq"}:
   import pyarrow.parquet as pq
   schema_names=set(pq.ParquetFile(p).schema_arrow.names);rec["explicit_key_fields"]=sorted(KEYS&schema_names);rec["numeric_score_fields"]=sorted(SCORES&schema_names);rec["compatible"]=bool(rec["explicit_key_fields"] and rec["numeric_score_fields"]);rec["inspect_status"]="SCHEMA_ONLY";return rec
  else:rec["inspect_status"]="UNSUPPORTED_FORMAT";return rec
  fields=set()
  for r in rows:
   fields|=set(r.keys())
   for v in r.values():
    if isinstance(v,dict):fields|=set(v.keys())
  rec["explicit_key_fields"]=sorted(KEYS&fields);rec["numeric_score_fields"]=sorted(SCORES&fields);rec["compatible"]=bool(rec["explicit_key_fields"] and rec["numeric_score_fields"]);rec["inspect_status"]="SAMPLED_ROWS"
 except Exception as e:rec["inspect_status"]="ERROR";rec["error"]=str(e)
 return rec
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--repo-root",default="/Users/byron/projects/active/hydradg");ap.add_argument("--output",required=True);a=ap.parse_args();root=Path(a.repo_root);cands=[]
 # Restrict discovery to evaluation/custody-derived structured artifacts; never scan secrets/env.
 for base in [root/"eval",root/"custody"/"graph"]:
  if not base.exists():continue
  for p in base.rglob("*"):
   if not p.is_file() or p.suffix.lower() not in {".json",".jsonl",".parquet",".pq"}:continue
   n=p.name.lower()
   if any(k in n for k in ("context","score","atom","entropy","iceberg","fcg")):cands.append(p)
 results=[inspect(p) for p in sorted(set(cands))];compatible=[r for r in results if r.get("compatible")]
 out={"schema":"hydradg.seedgraph.atom_score_discovery.v1","candidate_count":len(results),"compatible_explicit_binding_count":len(compatible),"compatible_candidates":compatible,"all_candidates":results,"binding_policy":"EXPLICIT_CANONICAL_KEY_OR_SEED_ATOM_ID_PLUS_NUMERIC_SCORE_FIELD_ONLY","semantic_guessing_prohibited":True,"zero_model_calls":True,"zero_network_calls":True,"state":"EXPLICIT_BINDING_CANDIDATE_FOUND" if compatible else "BLOCKED_NO_EXPLICIT_ATOM_SCORE_BINDING_FOUND","timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())};raw=json.dumps(out,sort_keys=True,separators=(",",":")).encode();out["receipt_sha256"]=hashlib.sha256(raw).hexdigest();Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
