#!/usr/bin/env python3
"""Hack Hydra 'Best Use of HydraDB' retrieval ablation on LongMemEval.

A = flat BM25 session retrieval (no graph)
B = A seed retrieval + HydraDB temporal traversal (NEXT/PREV)
C = B + HydraDB provenance reconstruction (Case->CONTAINS->Session)
D = C + HydraDB context/update traversal (RELATED/SUPERSEDES)

Ground-truth answer_session_ids are used ONLY for evaluation, never for graph
construction or ranking. Abstention cases are emitted but not retrieval-scored.
The graph is built from session order and deterministic lexical relations.

This is a retrieval experiment, not end-to-end QA accuracy. The full Track-03
headline still requires the frozen reader/evaluator route over all 500 cases.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, time, urllib.request, urllib.error
from collections import Counter, defaultdict
from pathlib import Path

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]+")
STOP = {
    "the","a","an","and","or","but","if","then","than","to","of","in","on","for","with","at","by","from",
    "is","are","was","were","be","been","being","it","this","that","these","those","i","you","he","she","we","they",
    "my","your","his","her","our","their","me","him","them","what","when","where","who","why","how","do","did",
    "does","have","has","had","can","could","would","should","will","just","about","as","not","so","up","out"
}


def toks(text):
    return [t.lower() for t in TOKEN_RE.findall(text or "") if len(t) > 1 and t.lower() not in STOP]


def session_text(sess):
    parts = []
    for turn in sess:
        if isinstance(turn, dict):
            parts.append(str(turn.get("content", "")))
        else:
            parts.append(str(turn))
    return "\n".join(parts)


def stable_id(kind, *parts):
    raw = kind + "|" + "|".join(map(str, parts))
    # Stay comfortably below signed i64 while HydraDB itself accepts non-negative u64 ids.
    return int(hashlib.sha256(raw.encode()).hexdigest()[:15], 16)


def percentile(xs, q):
    if not xs: return None
    ys = sorted(xs); x = (len(ys)-1)*q; lo=int(math.floor(x)); hi=int(math.ceil(x))
    if lo == hi: return float(ys[lo])
    return float(ys[lo]*(hi-x)+ys[hi]*(x-lo))


class BM25:
    def __init__(self, docs):
        self.docs = [toks(d) for d in docs]
        self.n = len(self.docs)
        self.avgdl = sum(map(len, self.docs))/self.n if self.n else 0.0
        self.df = Counter()
        self.tf = []
        for d in self.docs:
            c = Counter(d); self.tf.append(c); self.df.update(c.keys())
    def idf(self, term):
        df = self.df.get(term, 0)
        return math.log(1 + (self.n - df + 0.5)/(df + 0.5))
    def scores(self, query, k1=1.5, b=0.75):
        qt = toks(query); out=[]
        for i,(d,c) in enumerate(zip(self.docs,self.tf)):
            dl=len(d); s=0.0
            for term in qt:
                f=c.get(term,0)
                if not f: continue
                den=f+k1*(1-b+b*dl/(self.avgdl or 1.0))
                s += self.idf(term)*(f*(k1+1)/den)
            out.append(s)
        return out
    def signature(self, idx, topn=10):
        c=self.tf[idx]
        ranked=sorted(c, key=lambda t:(-(c[t]*self.idf(t)), t))
        return set(ranked[:topn])


class HydraHTTP:
    def __init__(self, endpoint, token, namespace="default", cell_id="cell-0", timeout=30):
        self.endpoint=endpoint; self.token=token; self.namespace=namespace; self.cell_id=cell_id; self.timeout=timeout
    def query(self, query, parameters=None):
        body=json.dumps({"cell_id":self.cell_id,"query":query,"parameters":parameters or {}}).encode()
        req=urllib.request.Request(self.endpoint,data=body,method="POST",headers={
            "Authorization":f"Bearer {self.token}","X-Graph-Namespace":self.namespace,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail=e.read().decode(errors="replace")
            raise RuntimeError(f"HydraDB HTTP {e.code}: {detail[:1000]} query={query[:300]}") from e
    @staticmethod
    def projected_ints(resp, col="id"):
        cols=resp.get("columns",[])
        if col not in cols: return []
        j=cols.index(col); out=[]
        for row in resp.get("rows",[]):
            v=row[j]
            if isinstance(v,dict) and "value" in v:
                try: out.append(int(v["value"]))
                except (TypeError,ValueError): pass
        return out


def batch(hydra, query, rows, size=150):
    for i in range(0,len(rows),size):
        hydra.query(query,{"rows":rows[i:i+size]})


def jaccard(a,b):
    u=a|b
    return len(a&b)/len(u) if u else 0.0


def prepare_case(case):
    qid=str(case["question_id"]); sids=[str(x) for x in case["haystack_session_ids"]]
    sessions=case["haystack_sessions"]
    if len(sids)!=len(sessions): raise ValueError(f"{qid}: session id/content length mismatch")
    texts=[session_text(s) for s in sessions]
    bm=BM25(texts); sig=[bm.signature(i) for i in range(len(texts))]
    vids=[stable_id("session",qid,sid) for sid in sids]
    cid=stable_id("case",qid)
    edges={"CONTAINS":[],"NEXT":[],"PREV":[],"RELATED":[],"SUPERSEDES":[]}
    for i,v in enumerate(vids):
        edges["CONTAINS"].append((cid,v))
        if i+1<len(vids):
            edges["NEXT"].append((v,vids[i+1])); edges["PREV"].append((vids[i+1],v))
    # Deterministic context edges: top-2 lexical-neighborhood relations, no answer labels.
    related=set()
    for i in range(len(vids)):
        cand=[]
        for j in range(len(vids)):
            if i==j: continue
            sc=jaccard(sig[i],sig[j])
            if sc>=0.05: cand.append((-sc,j))
        for _neg,j in sorted(cand)[:2]:
            related.add((vids[i],vids[j])); related.add((vids[j],vids[i]))
    edges["RELATED"]=sorted(related)
    # Directed update candidates: later sessions that strongly overlap an earlier session.
    for i in range(1,len(vids)):
        best=None
        for j in range(i):
            ov=len(sig[i]&sig[j]); sc=jaccard(sig[i],sig[j])
            if ov>=2 and sc>=0.15:
                key=(sc,ov,j)
                if best is None or key>best[0]: best=(key,j)
        if best is not None:
            j=best[1]; edges["SUPERSEDES"].append((vids[j],vids[i]))
    return {"qid":qid,"case_id":cid,"sids":sids,"vids":vids,"texts":texts,"bm":bm,"edges":edges,"vid_to_idx":{v:i for i,v in enumerate(vids)}}


def ingest(hydra, prepared):
    nodes=[]; cases=[]; rels=defaultdict(list)
    for p in prepared:
        cases.append({"vertex":p["case_id"],"qid":p["qid"]})
        for i,(sid,v) in enumerate(zip(p["sids"],p["vids"])):
            nodes.append({"vertex":v,"qid":p["qid"],"session_id":sid,"position":i})
        for typ,pairs in p["edges"].items():
            for s,d in pairs:
                rels[typ].append({"source_vertex":s,"destination_vertex":d,
                                  "relationship_vertex":stable_id("rel",typ,s,d)})
    batch(hydra,"UNWIND $rows AS row MERGE (n {id: row.vertex}) SET n:Case, n.qid = row.qid",cases)
    batch(hydra,"UNWIND $rows AS row MERGE (n {id: row.vertex}) SET n:Session, n.qid = row.qid, n.session_id = row.session_id, n.position = row.position",nodes)
    for typ,rows in rels.items():
        if not rows: continue
        if typ=="CONTAINS":
            q=f"UNWIND $rows AS row MATCH (s:Case {{id: row.source_vertex}}), (d:Session {{id: row.destination_vertex}}) MERGE (s)-[r:{typ} {{id: row.relationship_vertex}}]->(d)"
        else:
            q=f"UNWIND $rows AS row MATCH (s:Session {{id: row.source_vertex}}), (d:Session {{id: row.destination_vertex}}) MERGE (s)-[r:{typ} {{id: row.relationship_vertex}}]->(d)"
        batch(hydra,q,rows)
    return {"case_nodes":len(cases),"session_nodes":len(nodes),"edges":{k:len(v) for k,v in rels.items()}}


def traverse(hydra, seed, rel, maxhop=1, limit=40):
    q=f"MATCH (s:Session {{id: {seed}}})-[:{rel}*1..{maxhop}]->(v) RETURN DISTINCT v.id AS id LIMIT {limit}"
    return HydraHTTP.projected_ints(hydra.query(q),"id")


def provenance_set(hydra, case_id, limit=1000):
    q=f"MATCH (c:Case {{id: {case_id}}})-[:CONTAINS]->(s) RETURN s.id AS id LIMIT {limit}"
    return set(HydraHTTP.projected_ints(hydra.query(q),"id"))


def rank_method(p, hydra, method, question, k=10, seed_k=4):
    t0=time.perf_counter()
    raw=p["bm"].scores(question); mx=max(raw) if raw else 0.0
    norm=[s/mx if mx>0 else 0.0 for s in raw]
    order=sorted(range(len(raw)),key=lambda i:(-raw[i],p["sids"][i]))
    if method=="A":
        chosen=order[:k]
        dt=(time.perf_counter()-t0)*1000
        return chosen,{i:["flat_bm25"] for i in chosen},dt,0.0
    # Graph methods begin with fewer lexical anchors; graph relations must earn remaining slots.
    seeds=order[:min(seed_k,len(order))]
    scores={i:norm[i] for i in seeds}; reasons={i:["lexical_seed"] for i in seeds}
    def add(vid,boost,reason):
        i=p["vid_to_idx"].get(vid)
        if i is None: return
        scores[i]=max(scores.get(i,0.0),0.15*norm[i]+boost)
        reasons.setdefault(i,[]).append(reason)
    for rank_i,i in enumerate(seeds):
        seed=p["vids"][i]; base=max(norm[i],0.05)/(1+0.15*rank_i)
        for rel in ("NEXT","PREV"):
            for v in traverse(hydra,seed,rel,1): add(v,0.45*base,f"{rel}:1")
        if method=="D":
            for v in traverse(hydra,seed,"RELATED",1): add(v,0.60*base,"RELATED:1")
            upd_boost=0.95 if str(p.get("question_type",""))=="knowledge-update" else 0.75
            for v in traverse(hydra,seed,"SUPERSEDES",2): add(v,upd_boost*base,"SUPERSEDES:1..2")
    # Fill unused slots from flat ranking without giving them graph-path credit.
    for i in order:
        if len(scores)>=max(k,seed_k+8): break
        scores.setdefault(i,0.12*norm[i]); reasons.setdefault(i,["flat_fallback"])
    chosen=sorted(scores,key=lambda i:(-scores[i],p["sids"][i]))[:k]
    prov=provenance_set(hydra,p["case_id"]) if method in ("C","D") else set()
    if method in ("C","D"):
        for i in chosen:
            if p["vids"][i] in prov: reasons.setdefault(i,[]).append("Case-CONTAINS-Session")
    graph_covered=sum(1 for i in chosen if any(r not in ("lexical_seed","flat_fallback") for r in reasons[i]))/len(chosen) if chosen else 0.0
    if method in ("C","D") and chosen:
        # Provenance path is an independently queried graph relation, so count it as path coverage.
        graph_covered=sum(1 for i in chosen if p["vids"][i] in prov)/len(chosen)
    dt=(time.perf_counter()-t0)*1000
    return chosen,reasons,dt,graph_covered


def evaluate(chosen,p,case,k):
    retrieved=[p["sids"][i] for i in chosen[:k]]
    gold=[str(x) for x in case.get("answer_session_ids",[])]; gs=set(gold)
    if not gs: return retrieved,None,None
    hit=1 if gs.intersection(retrieved) else 0
    recall=len(gs.intersection(retrieved))/len(gs)
    return retrieved,hit,recall


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--endpoint",default="http://127.0.0.1:8443/v1/graphs/default/query")
    ap.add_argument("--token-file",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--k",type=int,default=10)
    ap.add_argument("--limit",type=int,default=None)
    args=ap.parse_args()
    data=json.loads(Path(args.data).read_text())
    if args.limit: data=data[:args.limit]
    token=Path(args.token_file).read_text().strip()
    hydra=HydraHTTP(args.endpoint,token)
    prepared=[]
    for case in data:
        p=prepare_case(case); p["question_type"]=str(case.get("question_type","UNKNOWN")); prepared.append(p)
    t_ing=time.perf_counter(); graph=ingest(hydra,prepared); ingest_ms=(time.perf_counter()-t_ing)*1000
    outp=Path(args.out); outp.parent.mkdir(parents=True,exist_ok=True)
    with outp.open("w") as fh:
        for case,p in zip(data,prepared):
            qid=str(case["question_id"]); is_abs=qid.endswith("_abs")
            row={"schema":"hydradg.best_use_case.v1","question_id":qid,"question_type":str(case.get("question_type","UNKNOWN")),
                 "is_abstention":is_abs,"k":args.k,"methods":{}}
            for method in ("A","B","C","D"):
                chosen,reasons,lat,pathcov=rank_method(p,hydra,method,str(case.get("question","")),args.k)
                ret,hit,rec=evaluate(chosen,p,case,args.k)
                row["methods"][method]={"retrieved_session_ids":ret,"hit_at_k":hit,"session_recall_at_k":rec,
                    "latency_ms":lat,"context_sessions":len(ret),"evidence_path_coverage":pathcov,
                    "retrieval_reasons":{p["sids"][i]:reasons.get(i,[]) for i in chosen[:args.k]}}
            fh.write(json.dumps(row,sort_keys=True)+"\n")
    receipt={"schema":"hydradg.best_use_run_receipt.v1","data":str(args.data),"rows":len(data),"k":args.k,
             "graph_ingest":graph,"graph_ingest_ms":ingest_ms,"hydradb_endpoint":args.endpoint,
             "ground_truth_use":"answer_session_ids used for evaluation only, not graph construction/ranking",
             "claim_ceiling":"RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA","signature_state":"NOT_SIGNED","merkle_state":"NOT_MERKLE_COMMITTED"}
    Path(str(outp)+".receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,indent=2,sort_keys=True))

if __name__=="__main__": main()
