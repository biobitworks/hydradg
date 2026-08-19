#!/usr/bin/env python3
"""Typed-memory graph primitives for Hack Hydra Best Use v2.

Evidence boundaries:
- Case/session/temporal/provenance structure: deterministic source transform.
- heuristic extractor: deterministic software output, not factual validation.
- Ollarma extractor: probabilistic model output, cached with prompt/response hashes.
- LongMemEval answer_session_ids: evaluation only; never graph construction/ranking.
"""
from __future__ import annotations
import hashlib,json,math,re,time,urllib.error,urllib.request
from collections import Counter,defaultdict
from pathlib import Path

TOKEN_RE=re.compile(r"[A-Za-z0-9][A-Za-z0-9_'-]+")
STOP=set("the a an and or but if then than to of in on for with at by from is are was were be been being it this that these those i you he she we they my your his her our their me him them what when where who why how do did does have has had can could would should will just about as not so up out now".split())
PATTERNS=[
 (re.compile(r"\bI\s+(?:currently\s+|now\s+)?live\s+in\s+([^.!?\n]{1,100})",re.I),"user","lives_in"),
 (re.compile(r"\bI\s+(?:currently\s+|now\s+)?work\s+(?:at|for)\s+([^.!?\n]{1,100})",re.I),"user","works_at"),
 (re.compile(r"\bI\s+(?:currently\s+|now\s+)?study\s+at\s+([^.!?\n]{1,100})",re.I),"user","studies_at"),
 (re.compile(r"\bI\s+(?:currently\s+|now\s+)?use\s+([^.!?\n]{1,100})",re.I),"user","uses"),
 (re.compile(r"\bI\s+(?:currently\s+|now\s+)?prefer\s+([^.!?\n]{1,100})",re.I),"user","prefers"),
 (re.compile(r"\bI\s+(?:currently\s+|now\s+)?like\s+([^.!?\n]{1,100})",re.I),"user","likes"),
]

def sha256_text(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def stable_id(kind:str,*parts:object)->int:return int(hashlib.sha256((kind+'|'+'|'.join(map(str,parts))).encode()).hexdigest()[:15],16)
def norm(x:object)->str:return ' '.join(str(x or '').strip().lower().split())
def clean(x:object,n:int=120)->str:return ' '.join(str(x or '').strip().split()).strip(' ,;:')[:n]
def toks(s:str)->list[str]:return [t.lower() for t in TOKEN_RE.findall(s or '') if len(t)>1 and t.lower() not in STOP]
def session_text(sess:object)->str:
 if not isinstance(sess,list):return str(sess or '')
 out=[]
 for t in sess:
  if isinstance(t,dict):
   role=str(t.get('role','')).strip(); c=str(t.get('content','')); out.append(f'{role}: {c}' if role else c)
  else: out.append(str(t))
 return '\n'.join(out)

class BM25:
 def __init__(self,docs:list[str]):
  self.docs=[toks(d) for d in docs];self.n=len(self.docs);self.avg=sum(map(len,self.docs))/self.n if self.n else 0
  self.tf=[];self.df=Counter()
  for d in self.docs:
   c=Counter(d);self.tf.append(c);self.df.update(c.keys())
 def idf(self,t):
  df=self.df.get(t,0);return math.log(1+(self.n-df+.5)/(df+.5))
 def scores(self,q):
  out=[]
  for d,c in zip(self.docs,self.tf):
   s=0.;dl=len(d)
   for t in toks(q):
    f=c.get(t,0)
    if f:s+=self.idf(t)*(f*2.5/(f+1.5*(.25+.75*dl/(self.avg or 1))))
   out.append(s)
  return out

class HydraHTTP:
 def __init__(self,endpoint:str,token:str,namespace='default',cell_id='cell-0',timeout=45):self.endpoint=endpoint;self.token=token;self.namespace=namespace;self.cell_id=cell_id;self.timeout=timeout
 def query(self,query:str,parameters:dict|None=None)->dict:
  data=json.dumps({'cell_id':self.cell_id,'query':query,'parameters':parameters or {}}).encode()
  req=urllib.request.Request(self.endpoint,data=data,method='POST',headers={'Authorization':f'Bearer {self.token}','X-Graph-Namespace':self.namespace,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=self.timeout) as r:return json.loads(r.read())
  except urllib.error.HTTPError as e:
   detail=e.read().decode(errors='replace');raise RuntimeError(f'HydraDB HTTP {e.code}: {detail[:1600]} query={query[:500]}') from e
 @staticmethod
 def projected(resp:dict,col:str)->list[object]:
  cs=resp.get('columns',[])
  if col not in cs:return []
  j=cs.index(col);out=[]
  for row in resp.get('rows',[]):
   if j>=len(row):continue
   v=row[j];out.append(v.get('value') if isinstance(v,dict) and 'value' in v else v)
  return out
 @staticmethod
 def projected_ints(resp:dict,col='id')->list[int]:
  out=[]
  for v in HydraHTTP.projected(resp,col):
   try:out.append(int(v))
   except (TypeError,ValueError):pass
  return out

def hydra_health(base_url='http://127.0.0.1:8443',timeout=3)->dict:
 try:
  with urllib.request.urlopen(base_url.rstrip('/')+'/healthz',timeout=timeout) as r:return {'ok':200<=r.status<300,'status':r.status}
 except Exception as e:return {'ok':False,'error':str(e)[:240]}

def batch(h:HydraHTTP,q:str,rows:list[dict],size=100):
 for i in range(0,len(rows),size):h.query(q,{'rows':rows[i:i+size]})

def heuristic_extract(text:str)->dict:
 ents={};facts=[]
 def ent(name,typ='value'):
  c=clean(name,80);k=norm(c)
  if k:ents.setdefault(k,{'name':c,'type':typ})
 for p,sub,pred in PATTERNS:
  for m in p.finditer(text):
   obj=clean(m.group(1),100)
   if not obj:continue
   ent(sub,'person');ent(obj);facts.append({'subject':sub,'predicate':pred,'object':obj,'polarity':'affirmed','valid_time':'','confidence':.55})
   if len(facts)>=12:break
  if len(facts)>=12:break
 return {'entities':list(ents.values())[:24],'facts':facts,'evidence_class':'DETERMINISTIC_HEURISTIC_EXTRACTION','extractor':'heuristic_v2'}

class OllarmaExtractor:
 def __init__(self,base_url='http://127.0.0.1:8484',model=None,timeout=180):self.base_url=base_url.rstrip('/');self.model=model;self.timeout=timeout
 def health(self):
  try:
   with urllib.request.urlopen(self.base_url+'/health',timeout=4) as r:return {'ok':True,'payload':json.loads(r.read())}
  except Exception as e:return {'ok':False,'error':str(e)[:240]}
 def extract(self,text:str)->dict:
  prompt=('Return strict JSON only with keys entities and facts. Max 24 entities and 12 facts. '
   'Each entity: {name,type}. Each fact: {subject,predicate,object,polarity,valid_time,confidence}. '
   'Extract only explicit statements; do not infer. confidence 0..1. Text:\n'+text[:12000])
  payload={'message':prompt}
  if self.model:payload['model']=self.model
  req=urllib.request.Request(self.base_url+'/chat',data=json.dumps(payload).encode(),method='POST',headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=self.timeout) as r:outer=json.loads(r.read())
  raw=str(outer.get('response','')).strip();body=raw
  if body.startswith('```'):body=re.sub(r'^```(?:json)?\s*','',body,flags=re.I);body=re.sub(r'\s*```$','',body)
  try:obj=json.loads(body)
  except json.JSONDecodeError:
   lo,hi=body.find('{'),body.rfind('}');obj=json.loads(body[lo:hi+1]) if lo>=0 and hi>lo else {'entities':[],'facts':[]}
  ents=[]
  for e in obj.get('entities',[])[:24]:
   if isinstance(e,dict) and clean(e.get('name')):ents.append({'name':clean(e.get('name'),80),'type':clean(e.get('type') or 'unknown',40)})
  facts=[]
  for f in obj.get('facts',[])[:12]:
   if not isinstance(f,dict):continue
   s,p,o=clean(f.get('subject'),80),clean(f.get('predicate'),80),clean(f.get('object'),120)
   if not(s and p and o):continue
   try:conf=float(f.get('confidence',.5))
   except:conf=.5
   facts.append({'subject':s,'predicate':p,'object':o,'polarity':clean(f.get('polarity') or 'affirmed',24),'valid_time':clean(f.get('valid_time') or '',64),'confidence':max(0,min(1,conf))})
  return {'entities':ents,'facts':facts,'evidence_class':'PROBABILISTIC_MODEL_EXTRACTION','extractor':'ollarma_chat_v1','model':outer.get('model') or self.model,'prompt_sha256':sha256_text(prompt),'raw_response_sha256':sha256_text(raw),'status':outer.get('status'),'reason_code':outer.get('reason_code')}

def extract_cached(text:str,mode:str,cache_dir:Path|None,ollarma:OllarmaExtractor|None)->dict:
 source=sha256_text(text);model=ollarma.model if ollarma else '';key=sha256_text(f'{mode}|{model}|{source}')
 path=cache_dir/f'{key}.json' if cache_dir else None
 if path and path.exists():
  obj=json.loads(path.read_text());obj['cache_hit']=True;return obj
 if mode=='none':obj={'entities':[],'facts':[],'evidence_class':'NO_SEMANTIC_EXTRACTION','extractor':'none'}
 elif mode=='heuristic':obj=heuristic_extract(text)
 elif mode=='ollarma':
  if not ollarma:raise ValueError('Ollarma extractor not configured')
  obj=ollarma.extract(text)
 else:raise ValueError('extractor must be none/heuristic/ollarma')
 obj.update({'source_sha256':source,'cache_key':key,'cache_hit':False})
 if path:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
 return obj

def prepare_typed_case(case:dict,mode:str='heuristic',cache_dir:Path|None=None,ollarma:OllarmaExtractor|None=None)->dict:
 qid=str(case['question_id']);sids=[str(x) for x in case['haystack_session_ids']];sessions=case['haystack_sessions']
 if len(sids)!=len(sessions):raise ValueError(f'{qid}: session id/content mismatch')
 texts=[session_text(s) for s in sessions];vids=[stable_id('session_occurrence',qid,sid,i) for i,sid in enumerate(sids)]
 cid=stable_id('case',qid);project=stable_id('project','hackhydra-longmemeval');bm=BM25(texts)
 session_rows=[];entities={};facts={};rels=defaultdict(set);history=defaultdict(list);extractions=[]
 rels['HAS_CASE'].add((project,cid))
 for i,(sid,vid,text) in enumerate(zip(sids,vids,texts)):
  ext=extract_cached(text,mode,cache_dir,ollarma);extractions.append(ext)
  session_rows.append({'vertex':vid,'qid':qid,'session_id':sid,'position':i,'source_sha256':sha256_text(text),'extractor':ext.get('extractor','unknown'),'evidence_class':ext.get('evidence_class','UNKNOWN')})
  rels['CONTAINS'].add((cid,vid))
  if i+1<len(vids):rels['NEXT'].add((vid,vids[i+1]));rels['PREV'].add((vids[i+1],vid))
  local={}
  for e in ext.get('entities',[]):
   name=clean(e.get('name'),80);key=norm(name)
   if not key:continue
   eid=stable_id('entity',qid,key);local[key]=eid;entities.setdefault(eid,{'vertex':eid,'qid':qid,'name':name,'entity_type':clean(e.get('type') or 'unknown',40)});rels['MENTIONS'].add((vid,eid))
  for j,f in enumerate(ext.get('facts',[])[:12]):
   sub,pred,obj=clean(f.get('subject'),80),clean(f.get('predicate'),80),clean(f.get('object'),120)
   if not(sub and pred and obj):continue
   pol=clean(f.get('polarity') or 'affirmed',24);fid=stable_id('fact',qid,vid,j,norm(sub),norm(pred),norm(obj),norm(pol))
   try:conf=int(round(float(f.get('confidence',.5))*10000))
   except:conf=5000
   row={'vertex':fid,'qid':qid,'subject':sub,'predicate':pred,'object':obj,'polarity':pol,'valid_time':clean(f.get('valid_time') or '',64),'confidence_bp':max(0,min(10000,conf)),'position':i,'source_session_vertex':vid,'source_sha256':sha256_text(text),'evidence_class':ext.get('evidence_class','UNKNOWN')}
   facts[fid]=row;rels['ASSERTS'].add((vid,fid));rels['DERIVED_FROM'].add((fid,vid))
   for endpoint in (sub,obj):
    key=norm(endpoint);eid=local.get(key) or stable_id('entity',qid,key);entities.setdefault(eid,{'vertex':eid,'qid':qid,'name':endpoint,'entity_type':'fact_endpoint'});rels['ABOUT'].add((fid,eid));rels['MENTIONS'].add((vid,eid))
   history[(norm(sub),norm(pred))].append((i,fid,row))
 for rows in history.values():
  rows.sort()
  for (_,old_id,old),(_,new_id,new) in zip(rows,rows[1:]):
   if norm(old['object'])!=norm(new['object']) or norm(old['polarity'])!=norm(new['polarity']):
    rels['SUPERSEDED_BY'].add((old_id,new_id));rels['CONTRADICTS'].add((old_id,new_id));rels['CONTRADICTS'].add((new_id,old_id))
 return {'qid':qid,'question_type':str(case.get('question_type','UNKNOWN')),'case_id':cid,'project_id':project,'sids':sids,'vids':vids,'texts':texts,'bm25':bm,'vid_to_idx':{v:i for i,v in enumerate(vids)},'session_rows':session_rows,'entity_rows':list(entities.values()),'fact_rows':list(facts.values()),'rels':{k:sorted(v) for k,v in rels.items()},'extractions':extractions,'answer_session_ids':[str(x) for x in case.get('answer_session_ids',[])]}

def _dedupe(rows):
 out={}
 for row in rows:
  k=int(row['vertex'])
  if k in out and out[k]!=row:raise ValueError(f'conflicting local vertex metadata {k}')
  out[k]=row
 return list(out.values())

def ingest_typed_case(h:HydraHTTP,p:dict)->dict:
 projects=[{'vertex':p['project_id'],'name':'hackhydra-longmemeval'}];cases=[{'vertex':p['case_id'],'qid':p['qid'],'question_type':p['question_type']}];sessions=_dedupe(p['session_rows']);entities=_dedupe(p['entity_rows']);facts=_dedupe(p['fact_rows'])
 batch(h,'UNWIND $rows AS row MERGE (n {id: row.vertex}) SET n:Project, n.name = row.name',projects)
 batch(h,'UNWIND $rows AS row MERGE (n {id: row.vertex}) SET n:Case, n.qid = row.qid, n.question_type = row.question_type',cases)
 batch(h,'UNWIND $rows AS row MERGE (n {id: row.vertex}) SET n:Session, n.qid = row.qid, n.session_id = row.session_id, n.position = row.position, n.source_sha256 = row.source_sha256, n.extractor = row.extractor, n.evidence_class = row.evidence_class',sessions)
 if entities:batch(h,'UNWIND $rows AS row MERGE (n {id: row.vertex}) SET n:Entity, n.qid = row.qid, n.name = row.name, n.entity_type = row.entity_type',entities)
 if facts:batch(h,'UNWIND $rows AS row MERGE (n {id: row.vertex}) SET n:Fact, n.qid = row.qid, n.subject = row.subject, n.predicate = row.predicate, n.object = row.object, n.polarity = row.polarity, n.valid_time = row.valid_time, n.confidence_bp = row.confidence_bp, n.position = row.position, n.source_session_vertex = row.source_session_vertex, n.source_sha256 = row.source_sha256, n.evidence_class = row.evidence_class',facts)
 labels={'HAS_CASE':('Project','Case'),'CONTAINS':('Case','Session'),'NEXT':('Session','Session'),'PREV':('Session','Session'),'MENTIONS':('Session','Entity'),'ASSERTS':('Session','Fact'),'DERIVED_FROM':('Fact','Session'),'ABOUT':('Fact','Entity'),'SUPERSEDED_BY':('Fact','Fact'),'CONTRADICTS':('Fact','Fact')};counts={}
 for rel,pairs in p['rels'].items():
  if not pairs:counts[rel]=0;continue
  sl,dl=labels[rel];rows=[{'source_vertex':int(s),'destination_vertex':int(d),'relationship_vertex':stable_id('rel',p['qid'],rel,s,d)} for s,d in sorted(set(pairs))]
  batch(h,f'UNWIND $rows AS row MATCH (s:{sl} {{id: row.source_vertex}}), (d:{dl} {{id: row.destination_vertex}}) MERGE (s)-[r:{rel} {{id: row.relationship_vertex}}]->(d)',rows);counts[rel]=len(rows)
 return {'project_nodes':1,'case_nodes':1,'session_nodes':len(sessions),'entity_nodes':len(entities),'fact_nodes':len(facts),'edges':counts}

def ids(h,q,params):return HydraHTTP.projected_ints(h.query(q,params),'id')
def provenance_set(h,case_id,limit=2000):return set(ids(h,f'MATCH (c:Case {{id: $case_id}})-[:CONTAINS]->(s:Session) RETURN DISTINCT s.id AS id LIMIT {int(limit)}',{'case_id':int(case_id)}))
def relation_candidates(h,seed,method,limit=120):
 out=[]
 if method in {'B','C','D'}:
  for rel in ('NEXT','PREV'):out += [(v,.22,f'{rel}:1') for v in ids(h,f'MATCH (s:Session {{id: $seed}})-[:{rel}]->(v:Session) RETURN DISTINCT v.id AS id LIMIT {limit}',{'seed':seed})]
 if method in {'C','D'}:out += [(v,.34,'MENTIONS:shared_entity') for v in ids(h,f'MATCH (s:Session {{id: $seed}})-[:MENTIONS]->(e:Entity)<-[:MENTIONS]-(v:Session) RETURN DISTINCT v.id AS id LIMIT {limit}',{'seed':seed})]
 if method=='D':
  out += [(v,.85,'SUPERSEDED_BY:current_state') for v in ids(h,f'MATCH (s:Session {{id: $seed}})-[:ASSERTS]->(f:Fact)-[:SUPERSEDED_BY*1..4]->(cur:Fact)<-[:ASSERTS]-(v:Session) RETURN DISTINCT v.id AS id LIMIT {limit}',{'seed':seed})]
  out += [(v,.62,'CONTRADICTS:counterevidence') for v in ids(h,f'MATCH (s:Session {{id: $seed}})-[:ASSERTS]->(f:Fact)-[:CONTRADICTS]->(g:Fact)<-[:ASSERTS]-(v:Session) RETURN DISTINCT v.id AS id LIMIT {limit}',{'seed':seed})]
 return out

def rank_method(p,h,method,question,k=5,seed_k=None):
 t=time.perf_counter();raw=p['bm25'].scores(question);mx=max(raw) if raw else 0;norms=[x/mx if mx else 0 for x in raw];order=sorted(range(len(raw)),key=lambda i:(-raw[i],p['sids'][i],i))
 if method=='A':
  c=order[:k];return c,{i:['flat_bm25'] for i in c},(time.perf_counter()-t)*1000,0.
 seed_k=max(1,min(2,k)) if seed_k is None else seed_k;seeds=order[:seed_k];scores={i:max(norms[i],.05) for i in seeds};reasons={i:['lexical_seed'] for i in seeds}
 for r,i in enumerate(seeds):
  sw=max(norms[i],.08)/(1+.15*r)
  for vid,boost,reason in relation_candidates(h,p['vids'][i],method):
   j=p['vid_to_idx'].get(vid)
   if j is None:continue
   scores[j]=max(scores.get(j,0),.30*norms[j]+boost*sw);reasons.setdefault(j,[]).append(reason)
 for i in order:
  if len(scores)>=max(k+4,seed_k+8):break
  scores.setdefault(i,.28*norms[i]);reasons.setdefault(i,['flat_fallback'])
 if p['question_type']=='knowledge-update' and method=='D':
  for i,rs in reasons.items():
   if any('SUPERSEDED_BY' in x for x in rs):scores[i]+=.25
 chosen=sorted(scores,key=lambda i:(-scores[i],p['sids'][i],i))[:k];prov=provenance_set(h,p['case_id']) if method in {'C','D'} else set()
 for i in chosen:
  if p['vids'][i] in prov:reasons.setdefault(i,[]).append('Case-CONTAINS-Session')
 graph=sum(any(x not in {'lexical_seed','flat_fallback','Case-CONTAINS-Session'} for x in reasons.get(i,[])) for i in chosen)
 return chosen,reasons,(time.perf_counter()-t)*1000,graph/len(chosen) if chosen else 0.

def evaluate_retrieval(chosen,p,k):
 ret=[p['sids'][i] for i in chosen[:k]];gold=set(p.get('answer_session_ids') or [])
 if not gold:return ret,None,None
 return ret,1 if gold.intersection(ret) else 0,len(gold.intersection(ret))/len(gold)

def graph_stats(h):
 out={'labels':{},'relations':{}}
 for label in ('Project','Case','Session','Entity','Fact'):
  try:
   v=HydraHTTP.projected(h.query(f'MATCH (n:{label}) RETURN count(n) AS count'),'count');out['labels'][label]=int(v[0]) if v else None
  except Exception as e:out['labels'][label]={'error':str(e)[:200]}
 for rel in ('HAS_CASE','CONTAINS','NEXT','PREV','MENTIONS','ASSERTS','DERIVED_FROM','ABOUT','SUPERSEDED_BY','CONTRADICTS'):
  try:
   v=HydraHTTP.projected(h.query(f'MATCH ()-[r:{rel}]->() RETURN count(r) AS count'),'count');out['relations'][rel]=int(v[0]) if v else None
  except Exception as e:out['relations'][rel]={'error':str(e)[:200]}
 return out
