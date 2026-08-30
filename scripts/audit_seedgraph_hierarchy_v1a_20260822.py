#!/usr/bin/env python3
"""Audit SeedGraph v1a construction/query mechanics on magicSTUDIObox.

This is a zero-model, zero-network validation. It may validate structural
navigation without context scores, but score-guided navigation remains BLOCKED
unless an explicitly bound normalized score JSONL is supplied.
"""
from __future__ import annotations
import argparse, hashlib, json, os, socket, subprocess, sys, time
from pathlib import Path
from typing import Any

EXPECTED_HOST="magicSTUDIObox.local"
EXPECTED_SOURCE_HASHES={
 "track01_questions":"e25066f4eff3843dd0f3df0d1348113471e072e75007ffe390a0aa83f2a80af2",
 "track01_documents":"6b0747bf160af9427b12101537d53056ac592ada9831c1a98ae01fa50a8d2a9f",
 "track03_json":"d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442",
}
PROHIBITED=("gold_answer","answer_facts","expected_doc_ids","target_answer","eval_reference")

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def shafile(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
 return h.hexdigest()
def norm_id(v:str)->str:
 v=str(v)
 for p in ("LongMemEval-S_","LongMemEval-S-full500_","longmemeval_s_"):
  if v.startswith(p):return v[len(p):]
 return v
def recursive_ids(x:Any)->set[str]:
 out=set()
 if isinstance(x,dict):
  for k,v in x.items():
   if k in {"question_id","case_id","source_question_id","id"} and isinstance(v,(str,int)):out.add(norm_id(str(v)))
   out|=recursive_ids(v)
 elif isinstance(x,list):
  for v in x:out|=recursive_ids(v)
 return out
def run(cmd:list[str])->subprocess.CompletedProcess[str]:
 return subprocess.run(cmd,capture_output=True,text=True,check=False)
def stable_query_projection(r:dict[str,Any])->dict[str,Any]:
 return {
  "question_fco_id":r.get("question_fco_id"),"case_id":r.get("case_id"),"dataset":r.get("dataset"),"stratum":r.get("stratum"),
  "question_sha256":r.get("question_sha256"),"question_seed_count":r.get("question_seed_count"),"matched_seed_count":r.get("matched_seed_count"),
  "candidate_occurrence_count":r.get("candidate_occurrence_count"),"hierarchy_nodes_scored":r.get("hierarchy_nodes_scored"),"graph_edges_traversed":r.get("graph_edges_traversed"),
  "selected_object_ids":[x.get("object_id") for x in r.get("selected_path_metrics",[])],
  "selected_object_types":[x.get("object_type") for x in r.get("selected_path_metrics",[])],
  "evidence_hashes":[x.get("selected_text_sha256") for x in r.get("evidence",[])],
  "coverage":r.get("idf_weighted_query_coverage"),"source_dereference_count":r.get("source_dereference_count"),"source_bytes_read":r.get("source_bytes_read"),
  "evidence_bytes_returned":r.get("evidence_bytes_returned"),"context_score_state":r.get("context_score_state")
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--engine",default="/Users/byron/projects/active/hydradg/scripts/seedgraph_hierarchy_v1a.py");ap.add_argument("--output-dir",default="/Volumes/magicBLACKbox/hydradg/seedgraph/v1a_validation");ap.add_argument("--receipt-dir",default="/Users/byron/projects/active/hydradg/eval/studio_daisy_20260821/seedgraph_v1a_validation");ap.add_argument("--atom-scores-jsonl");ap.add_argument("--historical-secondary",default="/Users/byron/projects/active/hydradg/eval/studio_daisy_20260821/dataset_audit/TRACK03_SECONDARY_30_MANIFEST.jsonl");a=ap.parse_args()
 receipt_dir=Path(a.receipt_dir);receipt_dir.mkdir(parents=True,exist_ok=True);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);engine=Path(a.engine)
 host=socket.gethostname();host_gate="PASS" if host==EXPECTED_HOST else "FAIL"
 if host_gate!="PASS":raise RuntimeError(f"HOST_IDENTITY_MISMATCH expected={EXPECTED_HOST} actual={host}")
 src=engine.read_text();network_terms=[t for t in ("urllib","requests.","http://","https://","OLLAMA_URL","/api/generate") if t in src];zero_network_static="PASS" if not network_terms else "FAIL"
 model_terms=[t for t in ("ollama","transformers","openai","anthropic") if t.lower() in src.lower()];zero_model_static="PASS" if not model_terms else "FAIL"
 compile_rc=run([sys.executable,"-m","py_compile",str(engine)])
 if compile_rc.returncode!=0:raise RuntimeError("PY_COMPILE_FAILED:"+compile_rc.stderr)
 build_cmd=[sys.executable,str(engine),"build","--output-dir",str(out),"--require-studio"]
 if a.atom_scores_jsonl:build_cmd.extend(["--atom-scores",a.atom_scores_jsonl])
 b=run(build_cmd)
 if b.returncode!=0:raise RuntimeError("BUILD_FAILED:"+b.stderr+"\n"+b.stdout[-4000:])
 br=json.loads((out/"BUILD_RECEIPT.json").read_text());source_gates={k:("PASS" if br.get("source_hashes",{}).get(k)==v else "FAIL") for k,v in EXPECTED_SOURCE_HASHES.items()}
 import pandas as pd
 nodes=pd.read_parquet(out/"nodes.parquet");edges=pd.read_parquet(out/"edges.parquet");idx=pd.read_parquet(out/"seed_index.parquet");questions=pd.read_parquet(out/"questions.parquet");qseeds=pd.read_parquet(out/"question_seeds.parquet")
 # Source prose must not be in graph/index tables. Questions may carry the query text itself.
 metadata_only_gate="PASS" if "display_text" not in nodes.columns and not any(c in nodes.columns for c in ("content","text","evidence_text")) and not any(c in idx.columns for c in ("content","text","evidence_text")) else "FAIL"
 leak_cols=sorted(set(PROHIBITED)&(set(nodes.columns)|set(idx.columns)|set(questions.columns)|set(qseeds.columns)));eval_leak_gate="PASS" if not leak_cols else "FAIL"
 q_t1=questions[questions.dataset=="EnterpriseRAG-Bench"];q_t3=questions[questions.dataset=="LongMemEval-S-full500"];sec=q_t3[q_t3.stratum=="SECONDARY_30"];pri=q_t3[q_t3.stratum=="PRIMARY_470"]
 count_gate="PASS" if (len(q_t1),len(pri),len(sec))==(300,470,30) else "FAIL"
 hist_path=Path(a.historical_secondary);hist_ids=set()
 if hist_path.exists():
  for line in hist_path.read_text().splitlines():
   if line.strip():hist_ids|=recursive_ids(json.loads(line))
 current_sec={norm_id(x) for x in sec.case_id.astype(str)}
 stratum_gate="PASS" if len(hist_ids)==30 and current_sec==hist_ids else "FAIL"
 stratum_diff={"historical_count":len(hist_ids),"current_count":len(current_sec),"missing":sorted(hist_ids-current_sec),"extra":sorted(current_sec-hist_ids)}
 # Core hierarchy/type gates.
 types=set(nodes.object_type.astype(str));required={"SOURCE_FILE_FCO","DOCUMENT_FCO","SESSION_FCO","PARAGRAPH_FCO","TURN_FCO","SENTENCE_FCO","SEED_ATOM_FCO","ATOM_OCCURRENCE_FCO"};hierarchy_gate="PASS" if required<=types else "FAIL"
 relation_set=set(edges.relation.astype(str));relation_gate="PASS" if {"INSTANCE_OF","IN_SENTENCE","IN_PARAGRAPH","IN_PARENT","IN_SESSION","IN_SOURCE"}<=relation_set else "FAIL"
 # Query deterministic samples: 3 Track01, 3 Track03 primary, 1 Track03 secondary. Each is run twice.
 samples=list(q_t1.question_fco_id.astype(str).head(3))+list(pri.question_fco_id.astype(str).head(3))+list(sec.question_fco_id.astype(str).head(1));qresults=[];det_gate="PASS";pointer_gate="PASS"
 for i,qid in enumerate(samples):
  p1=out/f"query_sample_{i}_a.json";p2=out/f"query_sample_{i}_b.json"
  for p in (p1,p2):
   rr=run([sys.executable,str(engine),"query","--index-dir",str(out),"--question-fco-id",qid,"--receipt",str(p)])
   if rr.returncode!=0:raise RuntimeError("QUERY_FAILED:"+rr.stderr+"\n"+rr.stdout[-3000:])
  r1=json.loads(p1.read_text());r2=json.loads(p2.read_text());s1=stable_query_projection(r1);s2=stable_query_projection(r2)
  if s1!=s2:det_gate="FAIL"
  if not all(e.get("selected_text_sha256") and e.get("source_pointer") for e in r1.get("evidence",[])):pointer_gate="FAIL"
  qresults.append({"sample":i,"question_fco_id":qid,"stable_projection_sha256":sha(json.dumps(s1,sort_keys=True,separators=(",",":")).encode()),"deterministic":s1==s2,"selected_object_ids":s1["selected_object_ids"],"selected_object_types":s1["selected_object_types"],"evidence_hashes":s1["evidence_hashes"],"coverage":s1["coverage"],"source_bytes_read":s1["source_bytes_read"],"index_graph_wall_ms_observed":[r1.get("index_graph_wall_ms"),r2.get("index_graph_wall_ms")],"dereference_verify_wall_ms_observed":[r1.get("dereference_verify_wall_ms"),r2.get("dereference_verify_wall_ms")]})
 # Score contract: structural validation may pass without it; score-guided cannot.
 score_state=br.get("atom_score_state","UNAVAILABLE");score_guided_gate="PASS" if score_state=="AVAILABLE" and any(str(x) not in {"{}","nan"} for x in nodes.score_bundle_json.astype(str)) else "BLOCKED_SCORE_SOURCE_NOT_BOUND"
 audit={"schema":"hydradg.seedgraph.validation_audit.v1a","execution_host":host,"engine_path":str(engine),"engine_sha256":shafile(engine),"build_receipt_sha256":br.get("receipt_sha256"),"build_artifact_hashes":br.get("artifact_hashes"),"PY_COMPILE_GATE":"PASS","ZERO_MODEL_CALL_STATIC_GATE":zero_model_static,"ZERO_NETWORK_CALL_STATIC_GATE":zero_network_static,"HOST_BINDING_GATE":host_gate,"SOURCE_SHA_GATES":source_gates,"METADATA_ONLY_GRAPH_GATE":metadata_only_gate,"EVAL_ONLY_LEAKAGE_GATE":eval_leak_gate,"leaked_columns":leak_cols,"HIERARCHY_OBJECT_TYPE_GATE":hierarchy_gate,"HIERARCHY_RELATION_GATE":relation_gate,"TRACK_COUNTS":{"track01_primary":len(q_t1),"track03_primary":len(pri),"track03_secondary":len(sec)},"TRACK_COUNT_GATE":count_gate,"TRACK03_EXACT_SECONDARY_SET_GATE":stratum_gate,"TRACK03_SECONDARY_DIFF":stratum_diff,"LAZY_POINTER_DEREFERENCE_GATE":pointer_gate,"DETERMINISTIC_QUERY_PATH_GATE":det_gate,"ATOM_SCORE_STATE":score_state,"SCORE_GUIDED_NAVIGATION_GATE":score_guided_gate,"QUERY_SAMPLES":qresults,"generated_parquet_location":str(out),"generated_parquets_git_eligible":False,"zero_model_calls":True,"zero_network_calls":True,"signature_state":"NOT_SIGNED","merkle_mmr_state":"NOT_COMMITTED","timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
 structural_required=[host_gate,zero_model_static,zero_network_static,*source_gates.values(),metadata_only_gate,eval_leak_gate,hierarchy_gate,relation_gate,count_gate,stratum_gate,pointer_gate,det_gate];audit["STRUCTURAL_VALIDATION_GATE"]="PASS" if all(x=="PASS" for x in structural_required) else "FAIL";audit["SEEDGRAPH_V1A_READY_FOR_MODEL_EXPERIMENT"]="YES" if audit["STRUCTURAL_VALIDATION_GATE"]=="PASS" and score_guided_gate=="PASS" else "NO";audit["claim_ceiling"]="DETERMINISTIC_HIERARCHICAL_LOOKUP_POINTER_DEREFERENCE_VALIDATED" if audit["STRUCTURAL_VALIDATION_GATE"]=="PASS" else "SEEDGRAPH_V1A_STRUCTURAL_VALIDATION_NOT_ESTABLISHED";audit["receipt_sha256"]=sha(json.dumps(audit,sort_keys=True,separators=(",",":")).encode());(receipt_dir/"SEEDGRAPH_V1A_VALIDATION_AUDIT.json").write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n");(receipt_dir/"QUERY_SAMPLE_RECEIPTS_COMPACT.json").write_text(json.dumps(qresults,indent=2,sort_keys=True)+"\n");print(json.dumps(audit,indent=2,sort_keys=True))
if __name__=="__main__":main()
