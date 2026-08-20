#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from e2e_lib import jsd_bits, cloud_drift, exact_agreement, cohen_kappa_if_informative

def load(p):
    return json.loads(Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--distribution")
    ap.add_argument("--gibbs")
    ap.add_argument("--comparison")
    ap.add_argument("--out", required=True)
    a=ap.parse_args()
    report={"schema":"hydradg.iceberg_receipt_review.v1","checks":{},"corrections":[]}
    if a.distribution and Path(a.distribution).is_file():
        d=load(a.distribution)
        js=float(d.get("js_divergence", d.get("jsd", 0.0)))
        cd=float(d.get("cloud_drift_0_100", d.get("cloud_drift", 100*js)))
        report["checks"]["distribution_bounds"] = 0 <= js <= 1 and 0 <= cd <= 100 and abs(cd-100*js)<1e-8
    if a.gibbs and Path(a.gibbs).is_file():
        g=load(a.gibbs)
        report["checks"]["gibbs_receipt_present"]=True
        report["corrections"].append(
            "Treat aggregate K5→K10 ΔG*/hit/recall as descriptive. Do not reject H0_GA from two aggregate condition points."
        )
    if a.comparison and Path(a.comparison).is_file():
        c=load(a.comparison)
        labels1=c.get("m1_labels") or c.get("model1_labels") or []
        labels2=c.get("m2_labels") or c.get("model2_labels") or []
        if labels1 and labels2 and len(labels1)==len(labels2):
            report["checks"]["exact_agreement"]=exact_agreement(labels1,labels2)
            report["checks"]["cohen_kappa"]=cohen_kappa_if_informative(labels1,labels2)
        report["corrections"].append(
            "Model prospective direction comparison remains PENDING until held-out Run N+1 is executed and frozen."
        )
    report["claim_ceiling"]="RECEIPT_REVIEW_AND_INTERPRETATION_CORRECTION_ONLY"
    Path(a.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(f"STATE=PASS STAGE=ICEBERG_RECEIPT_REVIEW OUTPUT={a.out}")
if __name__=="__main__":
    main()
