from pathlib import Path
import argparse,json,hashlib,collections,math

ap=argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--out",required=True)
ap.add_argument("--manifest",required=True)
ap.add_argument("--n",type=int,default=80)
args=ap.parse_args()
data=json.loads(Path(args.input).read_text())
if not isinstance(data,list): raise TypeError("expected JSON list")
def qid(x,i): return str(x.get("question_id",x.get("id",i)))
def cat(x): return str(x.get("question_type",x.get("category","UNKNOWN")))
def rank(s): return hashlib.sha256(s.encode()).hexdigest()

groups=collections.defaultdict(list)
for i,x in enumerate(data):
    groups[cat(x)].append((qid(x,i),x))
N=len(data); target=min(args.n,N)
alloc={}
remaining=target
cats=sorted(groups)
# proportional floor
for c in cats:
    a=int(target*len(groups[c])/N)
    alloc[c]=a; remaining-=a
# deterministic largest remainder
remainders=sorted(cats,key=lambda c:(-(target*len(groups[c])/N-alloc[c]),c))
for c in remainders[:remaining]: alloc[c]+=1

sel=[]
for c in cats:
    rows=sorted(groups[c],key=lambda q:rank(c+"|"+q[0]))
    sel.extend(x for _,x in rows[:alloc[c]])
sel=sorted(sel,key=lambda x:rank(qid(x,0)))
Path(args.out).parent.mkdir(parents=True,exist_ok=True)
Path(args.out).write_text(json.dumps(sel,indent=2,ensure_ascii=False)+"\n")
manifest={
  "schema":"hydradg.longmemeval_smoke.v1",
  "source_sha256":hashlib.sha256(Path(args.input).read_bytes()).hexdigest(),
  "source_n":N,"selected_n":len(sel),"selection":"category-proportional + sha256 stable rank",
  "category_counts":dict(collections.Counter(cat(x) for x in sel)),
  "selected_ids":[qid(x,i) for i,x in enumerate(sel)]
}
Path(args.manifest).parent.mkdir(parents=True,exist_ok=True)
Path(args.manifest).write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in manifest.items() if k!="selected_ids"},indent=2,sort_keys=True))
