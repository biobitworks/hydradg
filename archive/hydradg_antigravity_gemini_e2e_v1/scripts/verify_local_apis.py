#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, urllib.request
from pathlib import Path

def get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--best-use", default="http://127.0.0.1:8787")
    ap.add_argument("--web", default="http://127.0.0.1:3010")
    ap.add_argument("--out", required=True)
    a=ap.parse_args()
    endpoints=[
      ("best_use_health", a.best_use+"/health"),
      ("iceberg_headline", a.best_use+"/api/iceberg/headline"),
      ("iceberg_full", a.best_use+"/api/iceberg/full"),
      ("model_comparison", a.best_use+"/api/models/comparison"),
    ]
    results={}
    for name,url in endpoints:
        try:
            status,obj=get(url)
            results[name]={"state":"PASS","status":status,"body":obj}
        except Exception as e:
            results[name]={"state":"BLOCKED","error":str(e)}
    # Web API may be unavailable until Release Watch site is started.
    try:
        status,obj=get(a.web+"/api/iceberg")
        results["web_iceberg"]={"state":"PASS","status":status,"source_state":obj.get("source_state")}
    except Exception as e:
        results["web_iceberg"]={"state":"PENDING","error":str(e)}
    out={"schema":"hydradg.local_api_verification.v1","endpoints":results,"claim_ceiling":"LOCAL_API_SURFACE_ONLY"}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    hard=["best_use_health","iceberg_headline","iceberg_full","model_comparison"]
    if any(results[x]["state"]!="PASS" for x in hard):
        print(f"STATE=BLOCKED STAGE=LOCAL_API_VERIFY OUTPUT={a.out}")
        raise SystemExit(2)
    print(f"STATE=PASS STAGE=LOCAL_API_VERIFY OUTPUT={a.out}")
if __name__=="__main__":
    main()
