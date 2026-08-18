from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def first_diff(a,b,path="$"):
    if type(a) is not type(b):
        return {"path":path,"a":a,"b":b,"reason":"TYPE"}
    if isinstance(a,dict):
        ka,kb=set(a),set(b)
        if ka!=kb:
            return {"path":path,"only_a":sorted(ka-kb),"only_b":sorted(kb-ka),"reason":"KEYS"}
        for k in sorted(ka):
            if k=="result_body_sha256":
                continue
            d=first_diff(a[k],b[k],f"{path}.{k}")
            if d:return d
        return None
    if isinstance(a,list):
        if len(a)!=len(b):
            return {"path":path,"a_len":len(a),"b_len":len(b),"reason":"LENGTH"}
        for i,(x,y) in enumerate(zip(a,b)):
            d=first_diff(x,y,f"{path}[{i}]")
            if d:return d
        return None
    if a!=b:
        return {"path":path,"a":a,"b":b,"reason":"VALUE"}
    return None

ap=argparse.ArgumentParser()
ap.add_argument("results",nargs="+",help="backend=result.json or result.json")
ap.add_argument("--out",required=True)
args=ap.parse_args()

items=[]
for raw in args.results:
    if "=" in raw:
        name,path=raw.split("=",1)
    else:
        path=raw; name=Path(path).stem
    obj=load(path)
    items.append((name,path,obj))

rows=[]
for i in range(len(items)):
    for j in range(i+1,len(items)):
        na,pa,a=items[i]; nb,pb,b=items[j]
        ha=a.get("result_body_sha256"); hb=b.get("result_body_sha256")
        d=None if ha and ha==hb else first_diff(a,b)
        rows.append({
            "backend_a":na,"backend_b":nb,
            "path_a":pa,"path_b":pb,
            "result_body_sha256_a":ha,
            "result_body_sha256_b":hb,
            "result_body_sha256_equal":bool(ha and hb and ha==hb),
            "first_difference":d,
            "classification":"CONTENT_EXACT" if ha and ha==hb else "DIVERGED_OR_SCHEMA_DIFFERENCE",
        })
out={"schema":"hydradg.eca_cross_backend_compare.v1","comparisons":rows}
Path(args.out).parent.mkdir(parents=True,exist_ok=True)
Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
