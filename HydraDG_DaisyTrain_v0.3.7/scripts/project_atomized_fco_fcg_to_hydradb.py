#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, time, urllib.request, urllib.error
from pathlib import Path
from typing import Any

NODE_SCHEMA="hydradg.atomized_fco_hydradb_projection.v1"
CLAIM="FULL_DATASET_FCO_FCG_HYDRADB_PROJECTION_ONLY_NOT_BENCHMARK_PERFORMANCE"
RELATIONS={"DERIVED_FROM","NEXT","MEMBER_OF","COMMITS","ADMITS","PROJECTS"}

def sh_file(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def canon(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def shb(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def numeric(fco_id:str)->int:
 m=re.fullmatch(r'fco:([0-9a-f]{64})',fco_id)
 if not m: raise ValueError(f'not an FCO id: {fco_id}')
 v=int(m.group(1)[:13],16); return v or 1
class Hydra:
 def __init__(self,endpoint:str,token:str,ns:str):self.endpoint=endpoint;self.token=token;self.ns=ns
 def q(self,q:str,p:dict|None=None)->dict:
  req=urllib.request.Request(self.endpoint,data=json.dumps({'cell_id':'cell-0','query':q,'parameters':p or {}}).encode(),method='POST',headers={'Authorization':f'Bearer {self.token}','X-Graph-Namespace':self.ns,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=180) as r:return json.loads(r.read())
  except urllib.error.HTTPError as e:
   d=e.read().decode(errors='replace');raise RuntimeError(f'HydraDB HTTP {e.code}: {d[:2000]} query={q[:700]}') from e
 @staticmethod
 def scalar(resp:dict,col:str)->int:
  cols=resp.get('columns',[]);rows=resp.get('rows',[])
  if col not in cols or not rows:return 0
  v=rows[0][cols.index(col)];v=v.get('value') if isinstance(v,dict) and 'value' in v else v
  return int(v or 0)
def node_row(n:dict)->dict:
 p=n.get('payload') or {}
 return {'id':numeric(n['id']),'fco_id':n['id'],'object_sha256':n['object_sha256'],'fco_type':n['type'],'dataset_id':str(p.get('dataset_id','')),'relative_path':str(p.get('relative_path','')),'logical_pointer':str(p.get('logical_pointer','')),'record_kind':str(p.get('record_kind','')),'source_file_sha256':str(p.get('source_file_sha256') or p.get('source_sha256') or ''),'canonical_record_sha256':str(p.get('canonical_record_sha256','')),'field_leaf_merkle_root':str(p.get('field_leaf_merkle_root','')),'claim_ceiling':str(p.get('claim_ceiling',CLAIM))}
def chunks(lines,batch):
 buf=[]
 for x in lines:
  buf.append(x)
  if len(buf)>=batch:yield buf;buf=[]
 if buf:yield buf
def project_dataset(h:Hydra,d:Path,batch:int)->dict:
 nodes=d/'fco_nodes.jsonl';edges=d/'fcg_edges.jsonl';atom=d/'ATOMIZATION_RECEIPT.json'
 if not(nodes.is_file() and edges.is_file() and atom.is_file()):raise RuntimeError(f'incomplete atom bundle: {d}')
 a=json.load(open(atom));dataset_id=a['dataset_id']
 expected_nodes=sum(1 for _ in nodes.open())
 expected_edges=sum(1 for _ in edges.open())
 def node_iter():
  with nodes.open() as f:
   for line in f:
    if line.strip():yield node_row(json.loads(line))
 qn="UNWIND $rows AS row MERGE (n {id:row.id}) SET n:HydraDGFCO,n.fco_id=row.fco_id,n.object_sha256=row.object_sha256,n.fco_type=row.fco_type,n.dataset_id=row.dataset_id,n.relative_path=row.relative_path,n.logical_pointer=row.logical_pointer,n.record_kind=row.record_kind,n.source_file_sha256=row.source_file_sha256,n.canonical_record_sha256=row.canonical_record_sha256,n.field_leaf_merkle_root=row.field_leaf_merkle_root,n.claim_ceiling=row.claim_ceiling"
 projected_nodes=0
 for rows in chunks(node_iter(),batch):
  h.q(qn,{'rows':rows});projected_nodes+=len(rows)
 buckets={r:[] for r in RELATIONS};projected_edges=0
 def flush(rel:str):
  nonlocal projected_edges
  rows=buckets[rel]
  if not rows:return
  h.q(f"UNWIND $rows AS row MATCH (a {{id:row.src}}),(b {{id:row.dst}}) MERGE (a)-[:{rel}]->(b)",{'rows':rows});projected_edges+=len(rows);buckets[rel]=[]
 with edges.open() as f:
  for line in f:
   if not line.strip():continue
   e=json.loads(line);rel=e['rel']
   if rel not in RELATIONS:raise RuntimeError(f'undeclared FCG relation: {rel}')
   buckets[rel].append({'src':numeric(e['src']),'dst':numeric(e['dst'])})
   if len(buckets[rel])>=batch:flush(rel)
 for r in sorted(RELATIONS):flush(r)
 actual_nodes=Hydra.scalar(h.q("MATCH (n:HydraDGFCO {dataset_id:$d}) RETURN count(n) AS c",{'d':dataset_id}),'c')
 actual_edges=Hydra.scalar(h.q("MATCH (a:HydraDGFCO {dataset_id:$d})-[r]->(b:HydraDGFCO {dataset_id:$d}) RETURN count(r) AS c",{'d':dataset_id}),'c')
 ok=(projected_nodes==expected_nodes==actual_nodes and projected_edges==expected_edges==actual_edges)
 return {'dataset_id':dataset_id,'atomization_receipt_sha256':sh_file(atom),'nodes_jsonl_sha256':sh_file(nodes),'edges_jsonl_sha256':sh_file(edges),'objects_expected':expected_nodes,'objects_submitted':projected_nodes,'objects_observed':actual_nodes,'edges_expected':expected_edges,'edges_submitted':projected_edges,'edges_observed':actual_edges,'status':'PASS' if ok else 'FAIL'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--atom-root',type=Path,required=True);ap.add_argument('--endpoint',default='http://127.0.0.1:8443/v1/graphs/default/query');ap.add_argument('--token-file',type=Path,default=Path('~/.local/share/hydradg-best-use/hydradb-auth-token').expanduser());ap.add_argument('--namespace');ap.add_argument('--batch-size',type=int,default=128);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 root=a.atom_root.expanduser().resolve();batch_receipt=root/'FULL_ATOMIZATION_BATCH_RECEIPT.json';token=a.token_file.expanduser().read_text().strip()
 if not batch_receipt.is_file():raise SystemExit(f'missing {batch_receipt}')
 b=json.load(open(batch_receipt));ns=a.namespace or ('hydradg-fco-'+b['deterministic_payload_sha256'][:16]);h=Hydra(a.endpoint,token,ns)
 results=[]
 for d in sorted(p for p in root.iterdir() if p.is_dir() and (p/'ATOMIZATION_RECEIPT.json').is_file()):results.append(project_dataset(h,d,a.batch_size))
 science={'atomization_batch_receipt_sha256':sh_file(batch_receipt),'namespace':ns,'datasets':results,'batch_size':a.batch_size,'claim_ceiling':CLAIM}
 obj={'schema':NODE_SCHEMA,**science,'status':'PASS' if results and all(x['status']=='PASS' for x in results) else 'FAIL','result_sha256':shb(canon(science)),'signature_state':'NOT_SIGNED','hydradb_merkle_state':'NOT_MERKLE_COMMITTED','cfmo_state':'NOT_IMPLEMENTED_BY_THIS_RUN','timestamp_unix':int(time.time())}
 out=a.out.expanduser().resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');print(json.dumps(obj,indent=2,sort_keys=True));print('HYDRADB_FULL_ATOM_PROJECTION='+obj['status']);print('RECEIPT='+str(out));print('RECEIPT_FILE_SHA256='+sh_file(out))
 if obj['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
