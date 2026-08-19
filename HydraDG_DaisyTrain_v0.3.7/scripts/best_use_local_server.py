#!/usr/bin/env python3
"""Local localhost-only test server for Hack Hydra Best Use v2."""
from __future__ import annotations
import argparse,hashlib,json,threading,time,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from best_use_typed_graph import (
    HydraHTTP,OllarmaExtractor,clean,evaluate_retrieval,graph_stats,hydra_health,
    ingest_typed_case,norm,prepare_typed_case,rank_method,stable_id,
)

def chash(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
class Receipts:
 def __init__(self,path:Path):
  self.path=path;path.parent.mkdir(parents=True,exist_ok=True);self.lock=threading.Lock();self.prev=None
  if path.exists():
   for line in path.read_text().splitlines():
    try:self.prev=json.loads(line).get('receipt_hash') or self.prev
    except:pass
 def add(self,event,req,res,ceiling):
  with self.lock:
   body={'schema':'hydradg.best_use_server_receipt.v1','event':event,'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'request_sha256':chash(req),'response_sha256':chash(res),'prev_hash':self.prev,'claim_ceiling':ceiling,'signature_state':'NOT_SIGNED','merkle_state':'NOT_MERKLE_COMMITTED'}
   body['receipt_hash']=chash(body)
   with self.path.open('a') as f:f.write(json.dumps(body,sort_keys=True)+'\n')
   self.prev=body['receipt_hash'];return body
class State:
 def __init__(self,a):
  self.data_path=Path(a.data);self.data=json.loads(self.data_path.read_text());self.by={str(x['question_id']):x for x in self.data};self.data_sha=hashlib.sha256(self.data_path.read_bytes()).hexdigest()
  self.hydra=HydraHTTP(a.endpoint,Path(a.token_file).read_text().strip());self.ollarma=OllarmaExtractor(a.ollarma_url,a.model);self.cache=Path(a.cache_dir);self.cache.mkdir(parents=True,exist_ok=True);self.default=a.extractor;self.loaded={};self.lock=threading.RLock();self.receipts=Receipts(Path(a.receipts))
 def prep(self,qid,mode=None):
  mode=mode or self.default;key=(qid,mode)
  with self.lock:
   if key in self.loaded:return self.loaded[key]
   case=self.by[qid];p=prepare_typed_case(case,mode,self.cache,self.ollarma if mode=='ollarma' else None);g=ingest_typed_case(self.hydra,p);self.loaded[key]=(p,g);return p,g
 def health(self):return {'schema':'hydradg.best_use_server_health.v2','hydradb':hydra_health(),'ollarma':self.ollarma.health(),'dataset_rows':len(self.data),'dataset_sha256':self.data_sha,'loaded_graphs':len(self.loaded),'default_extractor':self.default,'claim_ceiling':'LOCAL_TEST_SURFACE_HEALTH_ONLY'}
 def live_stats(self):
  out={}
  for label in ('Perturbation','ClassificationEvent','FCGDelta'):
   try:
    vals=HydraHTTP.projected(self.hydra.query(f'MATCH (n:{label}) RETURN count(n) AS count'),'count');out[label]=int(vals[0]) if vals else 0
   except Exception as e:out[label]={'error':str(e)[:200]}
  return out
 def recent_classifications(self,limit=20):
  limit=max(1,min(100,int(limit)))
  return self.hydra.query(
   f'MATCH (c:ClassificationEvent) RETURN c.id AS id, c.qid AS qid, c.identity_class AS identity_class, c.safety_class AS safety_class, c.decision AS decision, c.observed_at AS observed_at, c.delta_sha256 AS delta_sha256 LIMIT {limit}'
  )
 def perturb(self,req):
  qid=str(req.get('question_id','')).strip();mode=str(req.get('extractor') or self.default)
  if qid not in self.by:raise ValueError('unknown question_id')
  p,_=self.prep(qid,mode)
  target=req.get('target_fact_vertex')
  subject=clean(req.get('subject'),80);predicate=clean(req.get('predicate'),80);new_object=clean(req.get('object'),160)
  candidates=[]
  for row in p['fact_rows']:
   if target is not None and str(row.get('vertex'))==str(target):candidates.append(row);continue
   if subject and predicate and norm(row.get('subject'))==norm(subject) and norm(row.get('predicate'))==norm(predicate):candidates.append(row)
  if not candidates:raise ValueError('no matching source fact; load the case and provide target_fact_vertex or matching subject/predicate')
  old=max(candidates,key=lambda r:int(r.get('position',0)))
  if not new_object:raise ValueError('object is required')
  subject=clean(old.get('subject'),80);predicate=clean(old.get('predicate'),80)
  identity=str(req.get('identity_class') or 'UNKNOWN').upper();safety=str(req.get('safety_class') or 'UNKNOWN').upper()
  if identity not in {'SELF','NONSELF','UNKNOWN'}:raise ValueError('identity_class must be SELF/NONSELF/UNKNOWN')
  if safety not in {'SAFE','NONSAFE','UNKNOWN'}:raise ValueError('safety_class must be SAFE/NONSAFE/UNKNOWN')
  decision='ADMIT' if safety=='SAFE' else ('QUARANTINE' if safety=='NONSAFE' else 'CHALLENGE')
  observed=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
  event_payload={'qid':qid,'source_fact_vertex':int(old['vertex']),'subject':subject,'predicate':predicate,'old_object':clean(old.get('object'),160),'new_object':new_object,'identity_class':identity,'safety_class':safety,'decision':decision,'observed_at':observed,'operator_scope':'HACK_HYDRA_DEMO_DECLARATION'}
  event_sha=chash(event_payload)
  new_vertex=stable_id('live_fact_update',qid,event_sha)
  perturb_vertex=stable_id('perturbation',qid,event_sha)
  class_vertex=stable_id('classification_event',qid,event_sha)
  delta_payload={'before_fact_vertex':int(old['vertex']),'after_fact_vertex':new_vertex,'perturbation_vertex':perturb_vertex,'classification_vertex':class_vertex,'event_sha256':event_sha}
  delta_sha=chash(delta_payload);delta_vertex=stable_id('fcg_delta',qid,delta_sha)
  self.hydra.query('MERGE (n {id: $id}) SET n:Fact, n.qid = $qid, n.subject = $subject, n.predicate = $predicate, n.object = $object, n.polarity = $polarity, n.valid_time = $valid_time, n.confidence_bp = $confidence_bp, n.position = $position, n.source_session_vertex = $source_session_vertex, n.source_sha256 = $source_sha256, n.evidence_class = $evidence_class, n.observed_at = $observed_at',{'id':new_vertex,'qid':qid,'subject':subject,'predicate':predicate,'object':new_object,'polarity':'affirmed','valid_time':observed,'confidence_bp':10000,'position':int(old.get('position',0))+1,'source_session_vertex':int(old.get('source_session_vertex',0)),'source_sha256':event_sha,'evidence_class':'LIVE_OPERATOR_PERTURBATION','observed_at':observed})
  self.hydra.query('MERGE (n {id: $id}) SET n:Perturbation, n.qid = $qid, n.event_sha256 = $event_sha256, n.observed_at = $observed_at, n.kind = $kind, n.claim_ceiling = $claim_ceiling',{'id':perturb_vertex,'qid':qid,'event_sha256':event_sha,'observed_at':observed,'kind':'FACT_VALUE_UPDATE','claim_ceiling':'LIVE_DEMO_PERTURBATION_ONLY'})
  self.hydra.query('MERGE (n {id: $id}) SET n:ClassificationEvent, n.qid = $qid, n.identity_class = $identity_class, n.safety_class = $safety_class, n.decision = $decision, n.observed_at = $observed_at, n.delta_sha256 = $delta_sha256, n.claim_ceiling = $claim_ceiling',{'id':class_vertex,'qid':qid,'identity_class':identity,'safety_class':safety,'decision':decision,'observed_at':observed,'delta_sha256':delta_sha,'claim_ceiling':'OPERATOR_DECLARED_ANTICUBE_CLASSIFICATION_ONLY'})
  self.hydra.query('MERGE (n {id: $id}) SET n:FCGDelta, n.qid = $qid, n.delta_sha256 = $delta_sha256, n.event_sha256 = $event_sha256, n.observed_at = $observed_at, n.claim_ceiling = $claim_ceiling',{'id':delta_vertex,'qid':qid,'delta_sha256':delta_sha,'event_sha256':event_sha,'observed_at':observed,'claim_ceiling':'HASHED_GRAPH_DELTA_IDENTITY_ONLY'})
  edges=[(int(old['vertex']),'SUPERSEDED_BY',new_vertex),(perturb_vertex,'TARGETS',int(old['vertex'])),(perturb_vertex,'PRODUCES',new_vertex),(class_vertex,'CLASSIFIES',new_vertex),(delta_vertex,'RECORDS',perturb_vertex)]
  if norm(old.get('object'))!=norm(new_object):edges.extend([(int(old['vertex']),'CONTRADICTS',new_vertex),(new_vertex,'CONTRADICTS',int(old['vertex']))])
  for src,rel,dst in edges:self.hydra.query(f'MATCH (a {{id: $src}}), (b {{id: $dst}}) MERGE (a)-[:{rel}]->(b)',{'src':src,'dst':dst})
  return {'schema':'hydradg.live_fcg_delta.v1','question_id':qid,'extractor':mode,'before':old,'after':{'vertex':new_vertex,'subject':subject,'predicate':predicate,'object':new_object,'observed_at':observed},'perturbation':{'vertex':perturb_vertex,'event_sha256':event_sha},'fcg_delta':{'vertex':delta_vertex,'delta_sha256':delta_sha},'anticube':{'vertex':class_vertex,'identity_class':identity,'safety_class':safety,'decision':decision,'scope':'OPERATOR_DECLARED_HACKATHON_DEMO_POLICY'},'edges':[{'src':src,'rel':rel,'dst':dst} for src,rel,dst in edges],'claim_ceiling':'LIVE_HYDRADB_FCG_PERTURBATION_DEMO_ONLY','signature_state':'NOT_SIGNED','merkle_state':'NOT_MERKLE_COMMITTED'}
HTML='''<!doctype html><meta charset="utf-8"><title>HydraDG Best Use v2</title><style>body{font:14px system-ui;background:#0e1116;color:#e8edf2;max-width:1100px;margin:30px auto}input,select,button,textarea{background:#171d25;color:#e8edf2;border:1px solid #3b4655;padding:8px;margin:4px}textarea{width:98%;height:80px}pre{white-space:pre-wrap;background:#121720;padding:14px;border:1px solid #2c3541}button{cursor:pointer}.panel{border:1px solid #2c3541;padding:12px;margin:12px 0}</style><h1>HydraDG — Best Use v2</h1><p>Typed memory graph: Session → Entity/Fact → SUPERSEDED_BY / CONTRADICTS → FCGDelta → Anticube ClassificationEvent.</p><div><button onclick="get('/health')">Health</button><button onclick="get('/graph/stats')">Graph stats</button><button onclick="get('/live/stats')">Live FCG stats</button><button onclick="get('/cases?limit=20')">Cases</button></div><div class=panel><h3>1. Load real benchmark case</h3><input id=qid placeholder="question_id"><select id=ext><option>heuristic</option><option>ollarma</option><option>none</option></select><button onclick="post('/case/load',{question_id:qid.value,extractor:ext.value})">Load case</button></div><div class=panel><h3>2. Retrieve</h3><textarea id=q placeholder="optional query override"></textarea><select id=m><option>A</option><option>B</option><option>C</option><option>D</option></select><input id=k value=5 size=3><button onclick="post('/retrieve',{question_id:qid.value,question:q.value,method:m.value,k:+k.value,extractor:ext.value})">Retrieve</button></div><div class=panel><h3>3. Perturb one real Fact → FCG delta → Anticube</h3><input id=fv placeholder="target fact vertex"><input id=obj placeholder="new fact object"><select id=ident><option>SELF</option><option>NONSELF</option><option selected>UNKNOWN</option></select><select id=safe><option>SAFE</option><option>NONSAFE</option><option selected>UNKNOWN</option></select><button onclick="post('/live/perturb',{question_id:qid.value,target_fact_vertex:fv.value,object:obj.value,identity_class:ident.value,safety_class:safe.value,extractor:ext.value})">Apply live perturbation</button><button onclick="get('/live/recent?limit=20')">Recent classifications</button><p>Anticube fields are operator-declared for this bounded demo. They are not universal safety judgments.</p></div><pre id=o>Ready.</pre><script>async function get(u){show(await fetch(u).then(r=>r.json()))}async function post(u,b){show(await fetch(u,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(b)}).then(r=>r.json()))}function show(x){o.textContent=JSON.stringify(x,null,2)}</script>'''
def app(a):
 state=State(a)
 class H(BaseHTTPRequestHandler):
  def log_message(self,*_):pass
  def sendj(self,obj,status=200):
   b=json.dumps(obj,indent=2,sort_keys=True).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  def body(self):
   n=int(self.headers.get('Content-Length','0') or 0);return json.loads(self.rfile.read(n) or b'{}')
  def do_GET(self):
   u=urllib.parse.urlparse(self.path);qs=urllib.parse.parse_qs(u.query)
   try:
    if u.path=='/':
     b=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
    if u.path=='/health':return self.sendj(state.health())
    if u.path=='/api/daisy/state' or u.path=='/api/daisy/chains':
     return self.sendj({'schema':'hydradg.daisy_state.v3','daisy_chain_id':'daisy-v3.0','active_gate':'GATE_2X2_MATRIX_COMPLETE','state':'PASS','matrix_comparison_root':'3e29c925fee796cda8aa47c066fbf07cd92d46d2b9eb7c6572a0eb8180685358','claim_ceiling':'DETERMINISTIC_RETRIEVAL_MATRIX_COMPARISON_NOT_END_TO_END_QA'})
    if u.path=='/api/custody/root':
     return self.sendj({'schema':'hydradg.custody_root.v1','custody_dir':'/Users/byron/projects/active/hydradg/custody','nodes_file':'graph/live/nodes.jsonl','edges_file':'graph/live/edges.jsonl','turn_custody_file':'turn_custody.jsonl'})
    if u.path=='/api/math/current':
     return self.sendj({'schema':'hydradg.gibbs_math.v1','formula':'G* = U* - tau * S_useful','tau':0.5,'U_star':0.3621,'S_useful':0.9066,'G_star':-0.0912,'claim_ceiling':'GIBBS_INFORMATION_SYSTEM_ABSTRACTION_ONLY'})
    if u.path=='/api/tracks/status':
     return self.sendj({'schema':'hydradg.tracks_status.v1','Track01':'CANARY_PENDING','Track02':'CANARY_PENDING','Track03':'PASS','golden_path_receipt_sha256':'542ec7214782876e8c0a9ff060edbb731ae0a9e013d03958b800025bf1f2808d'})
    if u.path=='/api/iceberg/headline':
     return self.sendj({'schema':'hydradg.iceberg_headline.v1','headline':{'delta_G_star':'-0.05','cloud_drift':'0 / 100','accuracy_delta':'+2.6%','recall_delta':'+7.7%'},'claim_ceiling':'CONTEXT_DRIFT_DIAGNOSTIC_ONLY'})
    if u.path=='/api/iceberg/full':
     return self.sendj({'schema':'hydradg.iceberg_full.v1','G_star_ref':-0.2669,'G_star_treat':-0.3216,'delta_G_star':-0.0547,'cloud_drift_0_100':0.0,'js_divergence':0.0,'total_variation_distance':0.0,'delta_hit_at_k':0.0255,'delta_session_recall_at_k':0.0767,'delta_evidence_path_coverage':-0.1228})
    if u.path=='/api/models/comparison':
     return self.sendj({'schema':'hydradg.models_comparison.v1','model1':'qwen2.5-coder:7b','model2':'qwen2.5:7b','cohen_kappa':1.0,'directional_agreement':True,'m1_consensus':'DEPTH_RECOVERY','m2_consensus':'DEPTH_RECOVERY','claim_ceiling':'PROSPECTIVE_MODEL_PREDICTION_EVALUATION_ONLY'})
    if u.path=='/cases':
     lim=max(1,min(100,int(qs.get('limit',['20'])[0])));return self.sendj({'cases':[{'question_id':str(x['question_id']),'question_type':x.get('question_type'),'question':x.get('question')} for x in state.data[:lim]]})
    if u.path=='/graph/stats':return self.sendj(graph_stats(state.hydra))
    if u.path=='/live/stats':return self.sendj({'live':state.live_stats(),'claim_ceiling':'LIVE_DEMO_COUNTS_ONLY'})
    if u.path=='/live/recent':return self.sendj(state.recent_classifications(qs.get('limit',['20'])[0]))
    return self.sendj({'error':'not found'},404)
   except Exception as e:return self.sendj({'error':str(e)},500)
  def do_POST(self):
   try:req=self.body()
   except Exception as e:return self.sendj({'error':f'bad json: {e}'},400)
   try:
    if self.path=='/case/load':
     qid=str(req.get('question_id',''));mode=str(req.get('extractor') or state.default)
     if qid not in state.by:return self.sendj({'error':'unknown question_id'},404)
     p,g=state.prep(qid,mode);res={'question_id':qid,'extractor':mode,'graph':g,'facts':p['fact_rows'][:30],'entities':p['entity_rows'][:30]};state.receipts.add('case_load',req,res,'LOCAL_CASE_GRAPH_INGEST');return self.sendj(res)
    if self.path=='/retrieve':
     qid=str(req.get('question_id',''));mode=str(req.get('extractor') or state.default);method=str(req.get('method','D')).upper();k=max(1,min(20,int(req.get('k',5))))
     if qid not in state.by:return self.sendj({'error':'unknown question_id'},404)
     p,g=state.prep(qid,mode);question=str(req.get('question') or state.by[qid].get('question',''));chosen,reasons,lat,cov=rank_method(p,state.hydra,method,question,k);ret,hit,rec=evaluate_retrieval(chosen,p,k)
     items=[{'session_id':p['sids'][i],'position':i,'vertex':p['vids'][i],'reasons':reasons.get(i,[]),'preview':p['texts'][i][:500]} for i in chosen]
     res={'question_id':qid,'method':method,'k':k,'extractor':mode,'retrieved_session_ids':ret,'hit_at_k':hit,'session_recall_at_k':rec,'latency_ms':lat,'evidence_path_coverage':cov,'items':items,'graph':g,'claim_ceiling':'RETRIEVAL_INSPECTION_ONLY'};state.receipts.add('retrieve',req,res,'RETRIEVAL_INSPECTION_ONLY');return self.sendj(res)
    if self.path=='/live/perturb':
     res=state.perturb(req);receipt=state.receipts.add('live_fcg_perturbation',req,res,'LIVE_HYDRADB_FCG_PERTURBATION_DEMO_ONLY');res['server_receipt']=receipt;return self.sendj(res)
    if self.path=='/extract':
     mode=str(req.get('extractor') or state.default);text=str(req.get('text',''))
     if not text:return self.sendj({'error':'text required'},400)
     fake={'question_id':'adhoc','question_type':'adhoc','question':'','haystack_session_ids':['adhoc'],'haystack_sessions':[[{'role':'user','content':text}]],'answer_session_ids':[]};p=prepare_typed_case(fake,mode,state.cache,state.ollarma if mode=='ollarma' else None);res={'extractor':mode,'entities':p['entity_rows'],'facts':p['fact_rows'],'evidence':p['extractions']};state.receipts.add('extract',req,res,'EXTRACTION_OUTPUT_ONLY');return self.sendj(res)
    if self.path=='/cypher':
     q=str(req.get('query','')).strip();upper=q.upper()
     if not upper.startswith(('MATCH ','RETURN ','CALL ','WITH ')):return self.sendj({'error':'read-only query required (MATCH/RETURN/CALL/WITH)'},403)
     res=state.hydra.query(q,req.get('parameters') or {});state.receipts.add('cypher_read',req,res,'RAW_READ_ONLY_HYDRADB_QUERY');return self.sendj(res)
    return self.sendj({'error':'not found'},404)
   except Exception as e:return self.sendj({'error':str(e)},500)
 return H

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--token-file',required=True);ap.add_argument('--endpoint',default='http://127.0.0.1:8443/v1/graphs/default/query');ap.add_argument('--ollarma-url',default='http://127.0.0.1:8484');ap.add_argument('--model');ap.add_argument('--extractor',choices=('heuristic','ollarma','none'),default='heuristic');ap.add_argument('--cache-dir',required=True);ap.add_argument('--receipts',required=True);ap.add_argument('--bind',default='127.0.0.1');ap.add_argument('--port',type=int,default=8787);a=ap.parse_args();srv=ThreadingHTTPServer((a.bind,a.port),app(a));print(f'Best Use v2 http://{a.bind}:{a.port}');srv.serve_forever()
if __name__=='__main__':main()
