#!/usr/bin/env python3
import argparse, json, math, random
from collections import defaultdict

PRIMARY_BINARY=["first_divergence_exact","unsupported_claim_rejection","history_reconstruction","recovery_class_accuracy"]
CONTINUOUS=["latency_ms","context_tokens","evidence_path_coverage","provenance_completeness"]

def mean(xs): return sum(xs)/len(xs) if xs else None
def percentile(xs,q):
    if not xs:return None
    ys=sorted(xs)
    if len(ys)==1:return ys[0]
    p=(len(ys)-1)*q; lo=math.floor(p); hi=math.ceil(p)
    return ys[lo] if lo==hi else ys[lo]+(ys[hi]-ys[lo])*(p-lo)

def proportion_ci(vals,rng,B):
    vals=[float(v) for v in vals if v is not None]
    if not vals:return {"n":0,"estimate":None,"ci95":[None,None]}
    n=len(vals); est=mean(vals)
    boots=[mean([vals[rng.randrange(n)] for _ in range(n)]) for _ in range(B)]
    return {"n":n,"estimate":est,"ci95":[percentile(boots,.025),percentile(boots,.975)]}

def mcnemar_exact(pairs):
    b01=sum((not bool(a)) and bool(b) for a,b in pairs)
    b10=sum(bool(a) and (not bool(b)) for a,b in pairs); n=b01+b10
    if n==0:return {"n_pairs":len(pairs),"discordant":0,"p_exact":1.0,"b01":b01,"b10":b10}
    k=min(b01,b10); tail=sum(math.comb(n,i) for i in range(k+1))/(2**n)
    return {"n_pairs":len(pairs),"discordant":n,"p_exact":min(1.0,2*tail),"b01":b01,"b10":b10}

def paired_bootstrap_delta(pairs,rng,B):
    if not pairs:return {"n_pairs":0,"delta":None,"ci95":[None,None]}
    ds=[float(b)-float(a) for a,b in pairs]; n=len(ds)
    boots=[mean([ds[rng.randrange(n)] for _ in range(n)]) for _ in range(B)]
    return {"n_pairs":n,"delta":mean(ds),"ci95":[percentile(boots,.025),percentile(boots,.975)]}

def paired_permutation(pairs,rng,B=20000):
    ds=[float(b)-float(a) for a,b in pairs]
    if not ds:return {"n_pairs":0,"delta_mean":None,"p_two_sided":None}
    obs=abs(mean(ds))
    if len(ds)<=20:
        total=1<<len(ds); ex=0
        for mask in range(total):
            m=mean([d if (mask>>i)&1 else -d for i,d in enumerate(ds)])
            if abs(m)>=obs-1e-15:ex+=1
        p=ex/total
    else:
        ex=0
        for _ in range(B):
            m=mean([d if rng.random()<.5 else -d for d in ds])
            if abs(m)>=obs-1e-15:ex+=1
        p=(ex+1)/(B+1)
    return {"n_pairs":len(ds),"delta_mean":mean(ds),"p_two_sided":p}

def impact_counts(rows):
    tp=fp=fn=0; exact=[]
    for r in rows:
        g=set(r.get("impact_gold") or []); p=set(r.get("impact_pred") or [])
        tp+=len(g&p); fp+=len(p-g); fn+=len(g-p); exact.append(p==g)
    return tp,fp,fn,exact

def impact_metrics(rows):
    tp,fp,fn,exact=impact_counts(rows)
    prec=tp/(tp+fp) if tp+fp else (1.0 if fn==0 else 0.0)
    rec=tp/(tp+fn) if tp+fn else 1.0
    f1=2*prec*rec/(prec+rec) if prec+rec else 0.0
    return {"tp":tp,"fp":fp,"fn":fn,"precision":prec,"recall":rec,"f1":f1,"exact_match":mean(exact)}

def impact_bootstrap_ci(rows,rng,B):
    if not rows:return {"n":0,"estimate":None,"ci95":[None,None]}
    n=len(rows); est=impact_metrics(rows)["f1"]
    boots=[]
    for _ in range(B):
        sample=[rows[rng.randrange(n)] for _ in range(n)]
        boots.append(impact_metrics(sample)["f1"])
    return {"n":n,"estimate":est,"ci95":[percentile(boots,.025),percentile(boots,.975)]}

def paired_impact_bootstrap_delta(base_rows,target_rows,rng,B):
    if not base_rows:return {"n_pairs":0,"delta":None,"ci95":[None,None]}
    if len(base_rows)!=len(target_rows):raise ValueError("paired impact rows differ in length")
    n=len(base_rows)
    delta=impact_metrics(target_rows)["f1"]-impact_metrics(base_rows)["f1"]
    boots=[]
    for _ in range(B):
        ids=[rng.randrange(n) for _ in range(n)]
        b=[base_rows[i] for i in ids]; t=[target_rows[i] for i in ids]
        boots.append(impact_metrics(t)["f1"]-impact_metrics(b)["f1"])
    return {"n_pairs":n,"delta":delta,"ci95":[percentile(boots,.025),percentile(boots,.975)]}

def holm(items):
    v=sorted((k,p) for k,p in items if p is not None); m=len(v); out={}; run=0
    for i,(k,p) in enumerate(v):
        run=max(run,min(1.0,(m-i)*p)); out[k]=run
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("input_jsonl"); ap.add_argument("-o","--output",required=True)
    ap.add_argument("--seed",type=int,default=20260818); ap.add_argument("--bootstrap",type=int,default=10000)
    a=ap.parse_args(); rows=[]; seen=set()
    for n,line in enumerate(open(a.input_jsonl,encoding="utf-8"),1):
        if not line.strip():continue
        r=json.loads(line)
        for k in ("item_id","system","condition"):
            if k not in r:raise ValueError(f"line {n}: missing {k}")
        key=(r["system"],r["condition"],r["item_id"])
        if key in seen:raise ValueError(f"line {n}: duplicate system/condition/item_id {key}")
        seen.add(key); rows.append(r)
    rng=random.Random(a.seed); groups=defaultdict(list)
    for r in rows:groups[(r["system"],r["condition"])].append(r)
    agg={}
    for (s,c),rs in sorted(groups.items()):
        g={"n_rows":len(rs),"n_unique_items":len({r["item_id"] for r in rs}),"impact":impact_metrics(rs),"impact_f1":impact_bootstrap_ci(rs,rng,a.bootstrap)}
        for m in PRIMARY_BINARY:
            vals=[r.get(m) for r in rs]
            g[m]=proportion_ci(vals,rng,a.bootstrap)
            g[m]["missing_n"]=sum(v is None for v in vals)
        for m in CONTINUOUS:
            vals=[float(r[m]) for r in rs if r.get(m) is not None]
            g[m]={"n":len(vals),"missing_n":len(rs)-len(vals),"mean":mean(vals),"median":percentile(vals,.5),"p95":percentile(vals,.95)}
        fc=defaultdict(int)
        for r in rs:
            if r.get("failure_class"):fc[str(r["failure_class"])]+=1
        g["failure_classes"]=dict(sorted(fc.items())); agg[f"{s}|{c}"]=g
    idx={(r["system"],r["condition"],r["item_id"]):r for r in rows}; comps={}; ps=[]
    for c in sorted({r["condition"] for r in rows}):
        for base in ("S0_FLAT","S1_VECTOR","S2_HYDRADB_GRAPH"):
            target="S3_HYDRADG_FULL"
            ids=sorted({r["item_id"] for r in rows if r["condition"]==c and r["system"]==base}&{r["item_id"] for r in rows if r["condition"]==c and r["system"]==target})
            if not ids:continue
            ck=f"{target}-vs-{base}|{c}"; cc={"n_pairs":len(ids),"binary":{},"impact_f1":{},"continuous":{}}
            for m in PRIMARY_BINARY:
                pairs=[(idx[(base,c,i)].get(m),idx[(target,c,i)].get(m)) for i in ids]
                pairs=[p for p in pairs if p[0] is not None and p[1] is not None]
                cc["binary"][m]={"paired_delta":paired_bootstrap_delta(pairs,rng,a.bootstrap),"mcnemar":mcnemar_exact(pairs),"missing_pair_n":len(ids)-len(pairs)}
            base_rows=[idx[(base,c,i)] for i in ids]; target_rows=[idx[(target,c,i)] for i in ids]
            cc["impact_f1"]={"paired_delta":paired_impact_bootstrap_delta(base_rows,target_rows,rng,a.bootstrap)}
            for m in ("latency_ms","context_tokens"):
                pairs=[(idx[(base,c,i)].get(m),idx[(target,c,i)].get(m)) for i in ids]
                pairs=[p for p in pairs if p[0] is not None and p[1] is not None]
                t=paired_permutation(pairs,rng); cc["continuous"][m]={"paired_delta":paired_bootstrap_delta(pairs,rng,a.bootstrap),"paired_permutation":t,"missing_pair_n":len(ids)-len(pairs)}; ps.append((f"{ck}:{m}",t["p_two_sided"]))
            comps[ck]=cc
    adj=holm(ps)
    for ck,cc in comps.items():
        for m,v in cc["continuous"].items():v["holm_adjusted_p"]=adj.get(f"{ck}:{m}")
    out={"schema":"hydradg.track03_statistics.v2","seed":a.seed,"bootstrap_resamples":a.bootstrap,"input_rows":len(rows),"aggregate":agg,"comparisons":comps,"notes":["Benchmark/statistical outputs are not correctness verification.","Failed/missing runs remain visible through denominators, missing counts and failure classes.","S3 comparisons are paired by condition and item_id.","impact_f1 confidence intervals and deltas resample paired item IDs and recompute pooled affected-set F1."]}
    with open(a.output,"w",encoding="utf-8") as f:json.dump(out,f,sort_keys=True,indent=2);f.write("\n")
if __name__=="__main__":main()
