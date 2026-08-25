#!/usr/bin/env python3
"""HydraDG SeedGraph v1a — deterministic lazy-pointer hierarchy.

Supersedes the first v1 implementation draft for validation. Important rules:
- graph/index tables do NOT store source prose;
- semantic lookup uses canonical seed keys, never SHA similarity;
- SHA-256 identifies/verifies objects and selected evidence bytes;
- source prose is dereferenced only after path selection;
- question FCOs contain no gold/reference/expected-doc fields;
- atom context scores, deltas and variances enrich path ranking when supplied;
- zero model/network calls.
"""
from __future__ import annotations

import argparse, functools, hashlib, json, math, re, socket, statistics, time, unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA="hydradg.seedgraph.hierarchy.v1a"
EXPECTED_HOST="magicSTUDIObox.local"
STOPWORDS=frozenset("a an and are as at be been by for from has have he her hers him his i in is it its of on or our she that the their them they this to was we were what when where which who why will with you your".split())
TOKEN_RE=re.compile(r"[A-Za-z0-9]+(?:[._:/-][A-Za-z0-9]+)*")
SENTENCE_BREAK_RE=re.compile(r"(?<=[.!?])\s+|\n+")
PARAGRAPH_BREAK_RE=re.compile(r"\n\s*\n+")


def sha256_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
    return h.hexdigest()
def cjson(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def norm(s:str)->str:return unicodedata.normalize("NFKC",s)
def typed_id(kind:str,identity:dict[str,Any])->tuple[str,str]:
    d=sha256_bytes(b"hydradg.seedgraph.object.v1a\0"+cjson({"kind":kind,**identity}));return f"{kind.lower()}:{d}",d

@functools.lru_cache(maxsize=524288)
def seed_id(key:str)->tuple[str,str]:
    d=sha256_bytes(b"hydradg.seedgraph.seed.v1\0"+key.encode());return f"seed_atom_fco:{d}",d


def split_spans(text:str,breaker:re.Pattern[str])->list[tuple[int,int,str]]:
    out=[];start=0
    for m in breaker.finditer(text):
        a,b=start,m.start();start=m.end()
        while a<b and text[a].isspace():a+=1
        while b>a and text[b-1].isspace():b-=1
        if a<b:out.append((a,b,text[a:b]))
    a,b=start,len(text)
    while a<b and text[a].isspace():a+=1
    while b>a and text[b-1].isspace():b-=1
    if a<b:out.append((a,b,text[a:b]))
    return out


def seeds(text:str,max_n:int=3)->list[dict[str,Any]]:
    text=norm(text);t=[]
    for m in TOKEN_RE.finditer(text):
        k=m.group(0).lower()
        if k not in STOPWORDS and len(k)>1:t.append((k,m.start(),m.end()))
    out=[]
    for n in range(1,max_n+1):
        for i in range(len(t)-n+1):
            w=t[i:i+n];out.append({"canonical_key":" ".join(x[0] for x in w),"char_start":w[0][1],"char_end":w[-1][2]})
    return out


def pvar(v:list[float])->float|None:return statistics.pvariance(v) if len(v)>1 else (0.0 if v else None)


class Builder:
    def __init__(self,out_dir:Path,scores:dict[str,dict[str,Any]]):
        import pyarrow as pa, pyarrow.parquet as pq
        self.out_dir=out_dir;self.scores=scores;self.seed_occ=defaultdict(list);self.seed_key={};self.seed_containers=defaultdict(set)
        self.questions=[];self.question_seeds=[];self.desc_scores=defaultdict(list);self.seed_seen=set()
        self.nodes_schema=pa.schema([("schema",pa.string()),("object_id",pa.string()),("object_sha256",pa.string()),("object_type",pa.string()),("visibility",pa.string()),("depth",pa.int64()),("canonical_key",pa.string()),("source_sha256",pa.string()),("source_pointer_json",pa.string()),("score_bundle_json",pa.string()),("aggregate_scores_json",pa.string()),("metadata_json",pa.string())])
        self.edges_schema=pa.schema([("source",pa.string()),("target",pa.string()),("relation",pa.string()),("edge_sha256",pa.string())])
        self.nodes_writer=pq.ParquetWriter(out_dir/"nodes.parquet",self.nodes_schema)
        self.edges_writer=pq.ParquetWriter(out_dir/"edges.parquet",self.edges_schema)
        self.node_buf=[];self.edge_buf=[];self.node_count=0;self.edge_count=0

    def _flush_nodes(self):
        if self.node_buf:
            import pyarrow as pa
            self.nodes_writer.write_table(pa.Table.from_pylist(self.node_buf,schema=self.nodes_schema))
            self.node_count+=len(self.node_buf);self.node_buf.clear()

    def _flush_edges(self):
        if self.edge_buf:
            import pyarrow as pa
            self.edges_writer.write_table(pa.Table.from_pylist(self.edge_buf,schema=self.edges_schema))
            self.edge_count+=len(self.edge_buf);self.edge_buf.clear()

    def node(self,row:dict[str,Any])->str:
        self.node_buf.append(row)
        if len(self.node_buf)>=50000:self._flush_nodes()
        return row["object_id"]

    def edge(self,s:str,t:str,r:str):
        self.edge_buf.append({"source":s,"target":t,"relation":r,"edge_sha256":sha256_bytes(b"hydradg.seedgraph.edge.v1a\0"+cjson([s,t,r]))})
        if len(self.edge_buf)>=50000:self._flush_edges()

    def source(self,dataset:str,path:Path,source_sha:str)->str:
        oid=f"source_file_fco:{source_sha}"
        return self.node({"schema":SCHEMA,"object_id":oid,"object_sha256":source_sha,"object_type":"SOURCE_FILE_FCO","visibility":"MODEL_VISIBLE_SAFE","depth":5,"canonical_key":None,"source_sha256":source_sha,"source_pointer_json":json.dumps({"dataset_id":dataset,"source_path":str(path),"source_file_sha256":source_sha},sort_keys=True),"score_bundle_json":"{}","aggregate_scores_json":"{}","metadata_json":json.dumps({"byte_size":path.stat().st_size},sort_keys=True)})

    def text_node(self,kind:str,depth:int,parent:str,relation:str,text:str,pointer:dict[str,Any],meta:dict[str,Any])->str:
        content_sha=sha256_bytes(text.encode());oid,objsha=typed_id(kind,{"content_sha256":content_sha,"pointer":pointer,"identity":meta})
        self.node({"schema":SCHEMA,"object_id":oid,"object_sha256":objsha,"object_type":kind,"visibility":"MODEL_VISIBLE","depth":depth,"canonical_key":None,"source_sha256":pointer.get("source_file_sha256"),"source_pointer_json":json.dumps(pointer,sort_keys=True),"score_bundle_json":"{}","aggregate_scores_json":"{}","metadata_json":json.dumps({**meta,"content_sha256":content_sha,"byte_size":len(text.encode())},sort_keys=True)})
        self.edge(oid,parent,relation);return oid

    def atoms(self,text:str,sentence:str,pointer:dict[str,Any],ancestors:list[str],container_id:str):
        for o in seeds(text):
            key=o["canonical_key"];sid,ssha=seed_id(key);score=self.scores.get(key,{})
            if sid not in self.seed_seen:
                self.seed_seen.add(sid)
                score_json=json.dumps(score,sort_keys=True) if score else "{}"
                self.node({"schema":SCHEMA,"object_id":sid,"object_sha256":ssha,"object_type":"SEED_ATOM_FCO","visibility":"MODEL_VISIBLE","depth":0,"canonical_key":key,"source_sha256":None,"source_pointer_json":"{}","score_bundle_json":score_json,"aggregate_scores_json":"{}","metadata_json":"{}"})
                self.seed_key[sid]=key
            ptr=dict(pointer);base=int(pointer.get("char_start") or 0);ptr["char_start"]=base+o["char_start"];ptr["char_end"]=base+o["char_end"]
            selected=text[o["char_start"]:o["char_end"]];ptr["selected_text_sha256"]=sha256_bytes(selected.encode())
            oid,osha=typed_id("ATOM_OCCURRENCE_FCO",{"seed_atom_id":sid,"sentence_id":sentence,"pointer":ptr})
            score_json=json.dumps(score,sort_keys=True) if score else "{}"
            self.node({"schema":SCHEMA,"object_id":oid,"object_sha256":osha,"object_type":"ATOM_OCCURRENCE_FCO","visibility":"MODEL_VISIBLE","depth":0,"canonical_key":key,"source_sha256":ptr.get("source_file_sha256"),"source_pointer_json":json.dumps(ptr,sort_keys=True),"score_bundle_json":score_json,"aggregate_scores_json":"{}","metadata_json":json.dumps({"seed_atom_id":sid,"selected_text_sha256":ptr["selected_text_sha256"]},sort_keys=True)})
            self.edge(oid,sid,"INSTANCE_OF");self.edge(oid,sentence,"IN_SENTENCE");self.seed_occ[sid].append(oid);self.seed_containers[key].add(container_id)
            val=score.get("context_score")
            if isinstance(val,(int,float)):
                for x in [sentence,*ancestors]:self.desc_scores[x].append(float(val))

    def hierarchy(self,text:str,parent:str,pointer:dict[str,Any],meta:dict[str,Any],container_id:str):
        paras=split_spans(text,PARAGRAPH_BREAK_RE) or [(0,len(text),text)]
        for pi,(a,b,ptext) in enumerate(paras):
            pp=dict(pointer);pp.update({"char_start":a,"char_end":b,"selected_text_sha256":sha256_bytes(ptext.encode())});pid=self.text_node("PARAGRAPH_FCO",2,parent,"IN_PARENT",ptext,pp,{**meta,"paragraph_index":pi})
            sents=split_spans(ptext,SENTENCE_BREAK_RE) or [(0,len(ptext),ptext)]
            for si,(s0,s1,stext) in enumerate(sents):
                aa,bb=a+s0,a+s1;sp=dict(pointer);sp.update({"char_start":aa,"char_end":bb,"selected_text_sha256":sha256_bytes(stext.encode())});sid=self.text_node("SENTENCE_FCO",1,pid,"IN_PARAGRAPH",stext,sp,{**meta,"paragraph_index":pi,"sentence_index":si});self.atoms(stext,sid,sp,[pid,parent],container_id)

    def question(self,dataset:str,case_id:str,text:str,pointer:dict[str,Any],stratum:str):
        qid,qsha=typed_id("QUESTION_FCO",{"dataset":dataset,"case_id":case_id,"question_sha256":sha256_bytes(text.encode())})
        self.questions.append({"schema":SCHEMA,"question_fco_id":qid,"object_sha256":qsha,"dataset":dataset,"case_id":case_id,"question_text":text,"question_sha256":sha256_bytes(text.encode()),"stratum":stratum,"visibility":"EVAL_QUERY","source_pointer_json":json.dumps(pointer,sort_keys=True)})
        for o in seeds(text):
            sid,_=seed_id(o["canonical_key"]);oid,osha=typed_id("QUESTION_ATOM_OCCURRENCE_FCO",{"question_fco_id":qid,"seed_atom_id":sid,"char_start":o["char_start"],"char_end":o["char_end"]});self.question_seeds.append({"question_fco_id":qid,"question_atom_occurrence_id":oid,"object_sha256":osha,"seed_atom_id":sid,"canonical_key":o["canonical_key"],"char_start":o["char_start"],"char_end":o["char_end"],"visibility":"EVAL_QUERY"})

    def finalize(self):
        self._flush_nodes()
        self._flush_edges()
        self.nodes_writer.close()
        self.edges_writer.close()


def load_scores(path:Path|None)->tuple[dict[str,dict[str,Any]],str,str|None]:
    if not path:return {},"UNAVAILABLE",None
    raw=path.read_bytes();m={}
    for line in raw.decode().splitlines():
        if not line.strip():continue
        x=json.loads(line);key=x.get("canonical_key")
        if key:m[str(key)]={k:v for k,v in x.items() if k!="canonical_key"}
    return m,("AVAILABLE" if m else "UNAVAILABLE"),sha256_bytes(raw)


def flatten_lme(src:Path,out:Path)->tuple[str,list[dict[str,Any]]]:
    import pandas as pd
    source_sha=sha256_file(src);raw=json.loads(src.read_text());rows=[]
    for item_i,item in enumerate(raw):
        cid=str(item.get("question_id"));sessions=item.get("haystack_sessions",[])
        for si,session in enumerate(sessions):
            turns=session if isinstance(session,list) else [session]
            for ti,turn in enumerate(turns):
                role=str(turn.get("role","user")) if isinstance(turn,dict) else "unknown";content=str(turn.get("content","")) if isinstance(turn,dict) else str(turn);key=f"{cid}|{si}|{ti}"
                rows.append({"pointer_key":key,"case_id":cid,"item_index":item_i,"session_index":si,"turn_index":ti,"role":role,"content":content,"content_sha256":sha256_bytes(content.encode()),"origin_json_sha256":source_sha})
    pd.DataFrame(rows).to_parquet(out,index=False);return sha256_file(out),rows


def build(a)->dict[str,Any]:
    if a.require_studio and socket.gethostname()!=EXPECTED_HOST:raise RuntimeError(f"HOST_IDENTITY_MISMATCH expected={EXPECTED_HOST} actual={socket.gethostname()}")
    import pandas as pd
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);q=Path(a.track01_questions);d=Path(a.track01_documents);l=Path(a.track03_json)
    for p in [q,d,l]:
        if not p.exists():raise FileNotFoundError(p)
    scores,score_state,score_sha=load_scores(Path(a.atom_scores) if a.atom_scores else None);g=Builder(out,scores);hs={"track01_questions":sha256_file(q),"track01_documents":sha256_file(d),"track03_json":sha256_file(l)}
    sd=g.source("EnterpriseRAG-Bench",d,hs["track01_documents"]);docs=pd.read_parquet(d,columns=["doc_id","content"])
    for _,r in docs.iterrows():
        did,text=str(r.doc_id),str(r.content);ptr={"dataset_id":"EnterpriseRAG-Bench","source_path":str(d),"source_file_sha256":hs["track01_documents"],"storage_kind":"PARQUET","row_key_field":"doc_id","row_key":did,"field_path":"content","char_start":0,"char_end":len(text),"selected_text_sha256":sha256_bytes(text.encode())};dn=g.text_node("DOCUMENT_FCO",3,sd,"IN_SOURCE",text,ptr,{"doc_id":did});g.hierarchy(text,dn,ptr,{"doc_id":did},dn)
    qs=pd.read_parquet(q,columns=["question_id","question"]).head(300)
    for _,r in qs.iterrows():
        qid,text=str(r.question_id),str(r.question);ptr={"dataset_id":"EnterpriseRAG-Bench","source_path":str(q),"source_file_sha256":hs["track01_questions"],"storage_kind":"PARQUET","row_key_field":"question_id","row_key":qid,"field_path":"question","char_start":0,"char_end":len(text),"selected_text_sha256":sha256_bytes(text.encode())};g.question("EnterpriseRAG-Bench",f"EnterpriseRAG-Bench_{qid}",text,ptr,"PRIMARY_300")
    proj=out/"track03_turn_projection.parquet";psha,turns=flatten_lme(l,proj);st=g.source("LongMemEval-S-full500",proj,psha);raw=json.loads(l.read_text())
    for item in raw:
        qid,text=str(item.get("question_id")),str(item.get("question"));qtype=str(item.get("question_type",""));stratum="SECONDARY_30" if qtype=="single-session-preference" else "PRIMARY_470";ptr={"dataset_id":"LongMemEval-S-full500","source_path":str(l),"source_file_sha256":hs["track03_json"],"storage_kind":"JSON","row_key_field":"question_id","row_key":qid,"field_path":"question","selected_text_sha256":sha256_bytes(text.encode())};g.question("LongMemEval-S-full500",f"LongMemEval-S_{qid}",text,ptr,stratum)
    grouped=defaultdict(list)
    for r in turns:grouped[(r["case_id"],int(r["session_index"]))].append(r)
    for (cid,si),trs in grouped.items():
        sess,sesssha=typed_id("SESSION_FCO",{"case_id":cid,"session_index":si,"projection_sha256":psha});g.node({"schema":SCHEMA,"object_id":sess,"object_sha256":sesssha,"object_type":"SESSION_FCO","visibility":"MODEL_VISIBLE","depth":4,"canonical_key":None,"source_sha256":psha,"source_pointer_json":"{}","score_bundle_json":"{}","aggregate_scores_json":"{}","metadata_json":json.dumps({"case_id":cid,"session_index":si},sort_keys=True)});g.edge(sess,st,"IN_SOURCE")
        for r in sorted(trs,key=lambda x:int(x["turn_index"])):
            text=r["content"];ptr={"dataset_id":"LongMemEval-S-full500","source_path":str(proj),"source_file_sha256":psha,"origin_source_sha256":hs["track03_json"],"storage_kind":"PARQUET","row_key_field":"pointer_key","row_key":r["pointer_key"],"field_path":"content","char_start":0,"char_end":len(text),"selected_text_sha256":r["content_sha256"]};tn=g.text_node("TURN_FCO",3,sess,"IN_SESSION",text,ptr,{"case_id":cid,"session_index":si,"turn_index":int(r["turn_index"]),"role":r["role"]});g.hierarchy(text,tn,ptr,{"case_id":cid,"session_index":si,"turn_index":int(r["turn_index"])},tn)
    g.finalize();idx=[]
    for sid,occs in g.seed_occ.items():
        key=g.seed_key[sid];idx.append({"seed_atom_id":sid,"canonical_key":key,"occurrence_count":len(occs),"container_frequency":len(g.seed_containers[key]),"occurrence_ids_json":json.dumps(sorted(occs))})
    pd.DataFrame(idx).to_parquet(out/"seed_index.parquet",index=False)
    pd.DataFrame(g.questions).to_parquet(out/"questions.parquet",index=False)
    pd.DataFrame(g.question_seeds).to_parquet(out/"question_seeds.parquet",index=False)
    # Fail closed if model-visible tables expose known evaluation-only field names.
    prohibited={"gold_answer","answer_facts","expected_doc_ids","target_answer","eval_reference"}
    visible_cols=set(g.nodes_schema.names)|set(g.edges_schema.names)|set(["seed_atom_id","canonical_key","occurrence_count","container_frequency","occurrence_ids_json"])|set(g.questions[0].keys() if g.questions else [])
    leakage=sorted(prohibited&visible_cols)
    if leakage:raise RuntimeError(f"EVAL_ONLY_COLUMN_LEAKAGE:{leakage}")
    paths=[out/"nodes.parquet",out/"edges.parquet",out/"seed_index.parquet",out/"questions.parquet",out/"question_seeds.parquet"]
    ah={p.name:sha256_file(p) for p in paths+[proj]};receipt={"schema":"hydradg.seedgraph.build_receipt.v1a","execution_host":socket.gethostname(),"source_hashes":hs,"track03_projection_sha256":psha,"atom_score_state":score_state,"atom_score_contract_sha256":score_sha,"artifact_hashes":ah,"counts":{"nodes":g.node_count,"edges":g.edge_count,"seed_atoms":len(idx),"questions":len(g.questions),"question_seed_occurrences":len(g.question_seeds)},"source_prose_in_nodes_gate":"PASS_METADATA_ONLY","eval_only_column_leakage_gate":"PASS","track01_question_contract":"ORDERED_FIRST_300_SOURCE_ROWS","track03_strata_contract":"PRIMARY_470_PLUS_SECONDARY_30_QUESTION_TYPE_RULE","track02_state":"BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED","zero_model_calls":True,"zero_network_calls":True,"signature_state":"NOT_SIGNED","merkle_mmr_state":"NOT_COMMITTED","timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())};receipt["receipt_sha256"]=sha256_bytes(cjson(receipt));(out/"BUILD_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n");(out/"SHA256SUMS.txt").write_text("\n".join(f"{v}  {k}" for k,v in sorted(ah.items()))+"\n");return receipt


def minmax(v:float|None,vals:list[float])->float:
    if v is None or not vals:return 0.0
    lo,hi=min(vals),max(vals);return 0.0 if hi==lo else (v-lo)/(hi-lo)


def deref(ptr:dict[str,Any])->tuple[bytes,dict[str,Any]]:
    """Lazy dereference one selected source object; verify selected bytes."""
    path=Path(ptr["source_path"]);kind=ptr.get("storage_kind");field=ptr.get("field_path");rowkey=ptr.get("row_key");rowfield=ptr.get("row_key_field")
    if kind=="PARQUET":
        import pyarrow.parquet as pq
        tab=pq.read_table(path,columns=[rowfield,field],filters=[(rowfield,"=",rowkey)]);vals=tab.column(field).to_pylist()
        if not vals:raise RuntimeError(f"POINTER_ROW_NOT_FOUND:{rowfield}={rowkey}")
        base=str(vals[0])
    elif kind=="JSON":
        raw=json.loads(path.read_text());found=None
        for item in raw:
            if str(item.get(rowfield))==str(rowkey):found=str(item.get(field,""));break
        if found is None:raise RuntimeError(f"POINTER_ROW_NOT_FOUND:{rowfield}={rowkey}")
        base=found
    else:raise RuntimeError(f"UNSUPPORTED_POINTER_KIND:{kind}")
    a=ptr.get("char_start");b=ptr.get("char_end");selected=base[int(a):int(b)] if a is not None and b is not None else base;data=selected.encode();actual=sha256_bytes(data);expected=ptr.get("selected_text_sha256")
    if expected and actual!=expected:raise RuntimeError(f"SELECTED_TEXT_SHA_MISMATCH expected={expected} actual={actual}")
    return data,{"selected_text_sha256":actual,"source_file_sha256_from_contract":ptr.get("source_file_sha256"),"bytes":len(data)}


def query(a)->dict[str,Any]:
    import pandas as pd
    root=Path(a.index_dir);nodes=pd.read_parquet(root/"nodes.parquet");edges=pd.read_parquet(root/"edges.parquet");idx=pd.read_parquet(root/"seed_index.parquet");questions=pd.read_parquet(root/"questions.parquet");build_receipt=json.loads((root/"BUILD_RECEIPT.json").read_text())
    if a.question_fco_id:
        qr=questions[questions.question_fco_id==a.question_fco_id]
        if qr.empty:raise KeyError(a.question_fco_id)
        qrow=qr.iloc[0];qtext=str(qrow.question_text);qid=str(qrow.question_fco_id);case_id=str(qrow.case_id);dataset=str(qrow.dataset);stratum=str(qrow.stratum)
    else:qtext=str(a.question_text);qid=typed_id("QUESTION_FCO",{"adhoc":sha256_bytes(qtext.encode())})[0];case_id="AD_HOC";dataset="AD_HOC";stratum="AD_HOC"
    t0=time.perf_counter();qkeys=sorted({x["canonical_key"] for x in seeds(qtext)});iby={str(r.canonical_key):r for _,r in idx.iterrows()};matched=[k for k in qkeys if k in iby];total_containers=max(1,int(nodes.object_type.isin(["DOCUMENT_FCO","TURN_FCO"]).sum()));idf={k:math.log((1+total_containers)/(1+int(iby[k].container_frequency)))+1 for k in matched};den=sum(idf.values()) or 1.0
    node={str(r.object_id):r for _,r in nodes.iterrows()};parents=defaultdict(list);children=defaultdict(list)
    for _,e in edges.iterrows():
        rel=str(e.relation);s,t=str(e.source),str(e.target)
        if rel in {"IN_SENTENCE","IN_PARAGRAPH","IN_PARENT","IN_SESSION","IN_SOURCE"}:parents[s].append(t);children[t].append(s)
    support=defaultdict(set);occ=set();traversed=0
    for key in matched:
        for oid in json.loads(str(iby[key].occurrence_ids_json)):
            occ.add(oid);front=[oid];seen={oid}
            while front:
                cur=front.pop();support[cur].add(key)
                for par in parents.get(cur,[]):
                    traversed+=1;support[par].add(key)
                    if par not in seen:seen.add(par);front.append(par)
    allowed={"SENTENCE_FCO","PARAGRAPH_FCO","TURN_FCO","DOCUMENT_FCO"};cand=[]
    for oid,keys in support.items():
        r=node.get(oid)
        if r is None or str(r.object_type) not in allowed:continue
        agg=json.loads(str(r.aggregate_scores_json) or "{}");meta=json.loads(str(r.metadata_json) or "{}");cov=sum(idf.get(k,0) for k in keys)/den;child_cov=0.0;child_mean=None
        for ch in children.get(oid,[]):
            if ch in support:child_cov=max(child_cov,sum(idf.get(k,0) for k in support[ch])/den)
            cr=node.get(ch)
            if cr is not None:
                ca=json.loads(str(cr.aggregate_scores_json) or "{}");cm=ca.get("context_mean")
                if isinstance(cm,(int,float)):child_mean=max(float(cm),child_mean if child_mean is not None else float(cm))
        cmean=agg.get("context_mean");cdelta=max(0.0,float(cmean)-float(child_mean)) if isinstance(cmean,(int,float)) and child_mean is not None else 0.0
        cand.append({"object_id":oid,"object_type":str(r.object_type),"depth":int(r.depth),"keys":sorted(keys),"coverage":cov,"coverage_delta":max(0.0,cov-child_cov),"context_mean":float(cmean) if isinstance(cmean,(int,float)) else None,"context_delta":cdelta,"context_variance":float(agg.get("context_variance")) if isinstance(agg.get("context_variance"),(int,float)) else None,"byte_size":int(meta.get("byte_size",0)),"pointer":json.loads(str(r.source_pointer_json) or "{}")})
    means=[x["context_mean"] for x in cand if x["context_mean"] is not None];deltas=[x["context_delta"] for x in cand];vars_=[x["context_variance"] for x in cand if x["context_variance"] is not None];bs=[float(x["byte_size"]) for x in cand];context_available=bool(means)
    for x in cand:
        nm=minmax(x["context_mean"],means);nd=minmax(x["context_delta"],deltas);nv=minmax(x["context_variance"],vars_);nb=minmax(float(x["byte_size"]),bs);x.update({"normalized_context_mean":nm,"normalized_context_delta":nd,"normalized_context_variance":nv,"normalized_marginal_byte_cost":nb})
        x["utility"]=0.50*x["coverage"]+0.20*x["coverage_delta"]+0.15*nm+0.10*nd-0.03*nv-0.02*nb if context_available else (0.50*x["coverage"]+0.20*x["coverage_delta"]-0.02*nb)/0.72
    cand.sort(key=lambda x:(-x["utility"],x["byte_size"],x["object_id"]));selected=[];covered=set();budget=int(a.max_evidence_bytes)
    for x in cand:
        new=set(x["keys"])-covered
        if not new:continue
        if sum(z["byte_size"] for z in selected)+x["byte_size"]>budget:continue
        selected.append(x);covered.update(x["keys"])
        if sum(idf.get(k,0) for k in covered)/den>=float(a.coverage_target) or len(selected)>=int(a.max_nodes):break
    graph_ms=(time.perf_counter()-t0)*1000;t1=time.perf_counter();evidence=[];source_bytes=0
    for x in selected:
        data,vr=deref(x["pointer"]);source_bytes+=len(data);evidence.append({"object_id":x["object_id"],"object_type":x["object_type"],"object_sha256":str(node[x["object_id"]].object_sha256),"selected_text_sha256":vr["selected_text_sha256"],"evidence_text":data.decode(errors="replace"),"evidence_bytes":len(data),"source_pointer":x["pointer"]})
    verify_ms=(time.perf_counter()-t1)*1000;packet_identity={"question_fco_id":qid,"evidence":[{"object_id":e["object_id"],"selected_text_sha256":e["selected_text_sha256"]} for e in evidence]};packet_id,packet_sha=typed_id("EVIDENCE_PACKET_FCO",packet_identity)
    rec={"schema":"hydradg.seedgraph.query_receipt.v1a","question_fco_id":qid,"case_id":case_id,"dataset":dataset,"stratum":stratum,"question_sha256":sha256_bytes(qtext.encode()),"build_receipt_sha256":build_receipt.get("receipt_sha256"),"question_seed_count":len(qkeys),"matched_seed_count":len(matched),"candidate_occurrence_count":len(occ),"hierarchy_nodes_scored":len(cand),"graph_edges_traversed":traversed,"selected_path_metrics":[{k:v for k,v in x.items() if k not in {"pointer","keys"}} for x in selected],"evidence_packet_fco_id":packet_id,"evidence_packet_object_sha256":packet_sha,"evidence":evidence,"idf_weighted_query_coverage":sum(idf.get(k,0) for k in covered)/den,"source_dereference_count":len(evidence),"source_bytes_read":source_bytes,"evidence_bytes_returned":source_bytes,"index_graph_wall_ms":round(graph_ms,3),"dereference_verify_wall_ms":round(verify_ms,3),"total_retrieval_wall_ms":round(graph_ms+verify_ms,3),"context_score_state":"AVAILABLE" if context_available else "UNAVAILABLE","source_identity_policy":"BUILD_TIME_FULL_FILE_SHA_PLUS_QUERY_TIME_SELECTED_TEXT_SHA","zero_model_calls":True,"zero_network_calls":True,"eval_only_leakage_gate":"PASS_BY_CONSTRUCTION"};rec["receipt_sha256"]=sha256_bytes(cjson(rec));
    if a.receipt:Path(a.receipt).write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    return rec


def cli():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True);b=s.add_parser("build");b.add_argument("--track01-questions",default="/Users/byron/.local/share/hydradg-datasets/track01/enterprise-rag-bench/data/questions/test.parquet");b.add_argument("--track01-documents",default="/Users/byron/.local/share/hydradg-datasets/track01/enterprise-rag-bench/data/documents/test.parquet");b.add_argument("--track03-json",default="/Users/byron/.local/share/hydradg-datasets/track03/longmemeval-cleaned/longmemeval_s_cleaned.json");b.add_argument("--atom-scores");b.add_argument("--output-dir",required=True);b.add_argument("--require-studio",action="store_true");q=s.add_parser("query");q.add_argument("--index-dir",required=True);g=q.add_mutually_exclusive_group(required=True);g.add_argument("--question-fco-id");g.add_argument("--question-text");q.add_argument("--coverage-target",type=float,default=.80);q.add_argument("--max-nodes",type=int,default=8);q.add_argument("--max-evidence-bytes",type=int,default=32768);q.add_argument("--receipt");a=p.parse_args();r=build(a) if a.cmd=="build" else query(a);print(json.dumps(r,indent=2,sort_keys=True))

if __name__=="__main__":cli()
