#!/usr/bin/env python3
"""Local localhost-only test server for Hack Hydra Best Use v2."""
from __future__ import annotations
import argparse,hashlib,json,threading,time,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from best_use_typed_graph import HydraHTTP,OllarmaExtractor,evaluate_retrieval,graph_stats,hydra_health,ingest_typed_case,prepare_typed_case,rank_method

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
HTML='''<!doctype html><meta charset="utf-8"><title>HydraDG Best Use v2</title><style>body{font:14px system-ui;background:#0e1116;color:#e8edf2;max-width:1100px;margin:30px auto}input,select,button,textarea{background:#171d25;color:#e8edf2;border:1px solid #3b4655;padding:8px;margin:4px}textarea{width:98%;height:80px}pre{white-space:pre-wrap;background:#121720;padding:14px;border:1px solid #2c3541}button{cursor:pointer}</style><h1>HydraDG — Best Use v2</h1><p>Typed memory graph: Session → Entity/Fact → SUPERSEDED_BY / CONTRADICTS.</p><div><button onclick="get('/health')">Health</button><button onclick="get('/graph/stats')">Graph stats</button><button onclick="get('/cases?limit=20')">Cases</button></div><div><input id=qid placeholder="question_id"><select id=ext><option>heuristic</option><option>ollarma</option><option>none</option></select><button onclick="post('/case/load',{question_id:qid.value,extractor:ext.value})">Load case</button></div><div><textarea id=q placeholder="optional query override"></textarea><select id=m><option>A</option><option>B</option><option>C</option><option>D</option></select><input id=k value=5 size=3><button onclick="post('/retrieve',{question_id:qid.value,question:q.value,method:m.value,k:+k.value,extractor:ext.value})">Retrieve</button></div><pre id=o>Ready.</pre><script>async function get(u){show(await fetch(u).then(r=>r.json()))}async function post(u,b){show(await fetch(u,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(b)}).then(r=>r.json()))}function show(x){o.textContent=JSON.stringify(x,null,2)}</script>'''
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
    if u.path=='/cases':
     lim=max(1,min(100,int(qs.get('limit',['20'])[0])));return self.sendj({'cases':[{'question_id':str(x['question_id']),'question_type':x.get('question_type'),'question':x.get('question')} for x in state.data[:lim]]})
    if u.path=='/graph/stats':return self.sendj(graph_stats(state.hydra))
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
