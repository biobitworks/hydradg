#!/usr/bin/env python3
"""Isolated-namespace matrix cell runner for the existing typed LongMemEval machinery."""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path

def canon(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)

ap=argparse.ArgumentParser()
ap.add_argument("data")
ap.add_argument("--scripts-dir", default="HydraDG_DaisyTrain_v0.3.7/scripts")
ap.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
ap.add_argument("--namespace", required=True)
ap.add_argument("--token-file", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--representation", choices=("raw","seedgraph"), required=True)
ap.add_argument("--extractor", choices=("none","heuristic"), required=True)
ap.add_argument("--cache-dir", default=None)
ap.add_argument("--k", type=int, choices=(5,10), required=True)
args=ap.parse_args()

sys.path.insert(0,str(Path(args.scripts_dir).resolve()))
from best_use_typed_graph import HydraHTTP, evaluate_retrieval, ingest_typed_case, prepare_typed_case, rank_method

METHODS=("A","B","C","D")
source=Path(args.data); source_bytes=source.read_bytes(); data=json.loads(source_bytes)
if len(data)!=500: raise SystemExit(f"expected 500 rows, got {len(data)}")
token=Path(args.token_file).read_text().strip()
hydra=HydraHTTP(args.endpoint,token,namespace=args.namespace)
cache=Path(args.cache_dir) if args.cache_dir else None
out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
aggregate={"cases":0,"sessions":0,"entities":0,"facts":0,"edges":{}}
canonical_rows=[]
started=time.perf_counter()

with out.open("w") as fh:
    for ordinal,case in enumerate(data,1):
        prepared=prepare_typed_case(case,args.extractor,cache,None)
        graph=ingest_typed_case(hydra,prepared)
        aggregate["cases"]+=graph["case_nodes"]; aggregate["sessions"]+=graph["session_nodes"]
        aggregate["entities"]+=graph["entity_nodes"]; aggregate["facts"]+=graph["fact_nodes"]
        for rel,count in graph["edges"].items():
            aggregate["edges"][rel]=aggregate["edges"].get(rel,0)+count
        qid=str(case["question_id"])
        row={"schema":"hydradg.matrix_case.v1","question_id":qid,
             "question_type":str(case.get("question_type","UNKNOWN")),
             "is_abstention":qid.endswith("_abs"),"k":args.k,
             "representation":args.representation,"extractor":args.extractor,
             "namespace":args.namespace,"graph":graph,"methods":{}}
        q=str(case.get("question",""))
        for m in METHODS:
            chosen,reasons,latency,path_cov=rank_method(prepared,hydra,m,q,args.k)
            retrieved,hit,recall=evaluate_retrieval(chosen,prepared,args.k)
            row["methods"][m]={
                "retrieved_session_ids":retrieved,"hit_at_k":hit,
                "session_recall_at_k":recall,"latency_ms":latency,
                "context_sessions":len(retrieved),"evidence_path_coverage":path_cov,
                "retrieval_reasons":{f"{prepared['sids'][i]}@{i}":reasons.get(i,[]) for i in chosen[:args.k]},
            }
        fh.write(json.dumps(row,sort_keys=True)+"\n")
        deterministic={
            "question_id":qid,"question_type":row["question_type"],"is_abstention":row["is_abstention"],
            "k":args.k,"representation":args.representation,"extractor":args.extractor,
            "graph":graph,
            "methods":{m:{
                "retrieved_session_ids":row["methods"][m]["retrieved_session_ids"],
                "hit_at_k":row["methods"][m]["hit_at_k"],
                "session_recall_at_k":row["methods"][m]["session_recall_at_k"],
                "context_sessions":row["methods"][m]["context_sessions"],
                "evidence_path_coverage":row["methods"][m]["evidence_path_coverage"],
                "retrieval_reasons":row["methods"][m]["retrieval_reasons"],
            } for m in METHODS},
        }
        canonical_rows.append(deterministic)
        print(json.dumps({"case":ordinal,"question_id":qid,"representation":args.representation,"k":args.k},sort_keys=True))

canonical_path=Path(str(out)+".canonical.jsonl")
canonical_path.write_text("".join(canon(x)+"\n" for x in canonical_rows))
canonical_sha=hashlib.sha256(canonical_path.read_bytes()).hexdigest()
receipt={
 "schema":"hydradg.matrix_run_receipt.v1","source":str(source),
 "source_sha256":hashlib.sha256(source_bytes).hexdigest(),"rows":len(data),
 "representation":args.representation,"extractor":args.extractor,"k":args.k,
 "namespace":args.namespace,"aggregate_graph":aggregate,
 "canonical_result_path":str(canonical_path),"canonical_result_sha256":canonical_sha,
 "elapsed_ms":(time.perf_counter()-started)*1000,
 "ground_truth_use":"answer_session_ids used only after retrieval for evaluation",
 "claim_ceiling":"MATRIX_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
 "signature_state":"NOT_SIGNED","merkle_state":"NOT_MERKLE_COMMITTED",
}
Path(str(out)+".receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps(receipt,indent=2,sort_keys=True))
