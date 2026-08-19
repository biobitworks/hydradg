#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
from collections import defaultdict

ap=argparse.ArgumentParser()
ap.add_argument("--evaldir", default=str(Path.home()/".local/share/hydradg-best-use/eval/matrix-20260819"))
ap.add_argument("--out", default=None)
args=ap.parse_args()
d=Path(args.evaldir)
out=Path(args.out) if args.out else d/"MATRIX_COMPARISON.json"

cells={}
for rep in ("raw","seedgraph"):
    for k in (5,10):
        key=f"{rep}_k{k}"
        runs=[]
        for r in (1,2,3):
            stem=d/f"{rep}_k{k}_r{r}"
            receipt=json.loads(Path(str(stem)+".jsonl.receipt.json").read_text())
            stats=json.loads(Path(str(stem)+".stats.json").read_text())
            runs.append({"r":r,"canonical_sha256":receipt["canonical_result_sha256"],"stats":stats})
        hashes=[x["canonical_sha256"] for x in runs]
        deterministic=(len(set(hashes))==1)
        cells[key]={"deterministic":deterministic,"canonical_hashes":hashes,"runs":runs}
        if not deterministic:
            raise SystemExit(f"DETERMINISM FAIL: {key}: {hashes}")

# Use replicate 1 stats after equality gate; all deterministic outcome fields must agree.
def metrics(cell,method):
    s=cells[cell]["runs"][0]["stats"]["methods"][method]
    return {"hit":s["hit_at_k"]["rate"],"recall":s["mean_session_recall_at_k"],
            "path":s["evidence_path_coverage_mean"]}

summary={c:{m:metrics(c,m) for m in ("A","D")} for c in cells}
comparisons={}
for k in (5,10):
    raw=summary[f"raw_k{k}"]["D"]; sg=summary[f"seedgraph_k{k}"]["D"]
    comparisons[f"seedgraph_minus_raw_k{k}"]={
        "delta_hit":sg["hit"]-raw["hit"],"delta_recall":sg["recall"]-raw["recall"],
        "delta_evidence_path_coverage":sg["path"]-raw["path"],
    }
for rep in ("raw","seedgraph"):
    a=summary[f"{rep}_k5"]["D"]; b=summary[f"{rep}_k10"]["D"]
    comparisons[f"k10_minus_k5_{rep}"]={
        "delta_hit":b["hit"]-a["hit"],"delta_recall":b["recall"]-a["recall"],
        "delta_evidence_path_coverage":b["path"]-a["path"],
    }

interaction={
 "hit":comparisons["seedgraph_minus_raw_k10"]["delta_hit"]-comparisons["seedgraph_minus_raw_k5"]["delta_hit"],
 "recall":comparisons["seedgraph_minus_raw_k10"]["delta_recall"]-comparisons["seedgraph_minus_raw_k5"]["delta_recall"],
}
obj={
 "schema":"hydradg.seedgraph_k_matrix_comparison.v1",
 "cells":{k:{"deterministic":v["deterministic"],"canonical_hashes":v["canonical_hashes"]} for k,v in cells.items()},
 "summary_A_and_D":summary,
 "comparisons":comparisons,
 "interaction_seedgraph_effect_k10_minus_k5":interaction,
 "nulls":{
   "determinism":"within-cell canonical hashes equal across r1/r2/r3",
   "representation_effect":"H0: SG_k - RAW_k = 0",
   "representation_advantage_gate":"H0: SG_k - RAW_k <= 0",
   "k_advantage_gate":"H0: K10 - K5 <= 0 within representation",
   "interaction":"H0: (SG10-RAW10)-(SG5-RAW5)=0",
 },
 "claim_ceiling":"DETERMINISTIC_RETRIEVAL_MATRIX_COMPARISON_NOT_END_TO_END_QA",
 "signature_state":"NOT_SIGNED",
 "merkle_state":"NOT_MERKLE_COMMITTED",
}
raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
obj["comparison_root_sha256"]=hashlib.sha256(raw).hexdigest()
out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(obj,indent=2,sort_keys=True))
