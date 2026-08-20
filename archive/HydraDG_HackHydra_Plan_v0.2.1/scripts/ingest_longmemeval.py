"""Convert LongMemEval JSON into portable SeedGraph JSONL.

Usage:
  python scripts/ingest_longmemeval.py --input data/longmemeval_s_cleaned.json --out seedgraph/lme

This script does not call an LLM. It preserves sessions, turns, timestamps,
question metadata, evidence-session labels, and `has_answer` turn labels.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def dump_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, separators=(",",":")) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = Path(args.out)
    nodes, edges = [], []
    for item in data:
        qid = item["question_id"]
        qnode = f"question:{qid}"
        nodes.append({
            "id":qnode,"type":"Claim","evidence_class":"DIRECTLY_SUPPLIED_EVIDENCE",
            "claim_ceiling":"BENCHMARK_GROUND_TRUTH","visibility":"PUBLIC",
            "metadata":{"question":item["question"],"answer":item["answer"],
                        "question_type":item["question_type"],"question_date":item.get("question_date")}
        })
        answer_sessions = set(item.get("answer_session_ids", []))
        for sid, date, session in zip(item["haystack_session_ids"], item["haystack_dates"], item["haystack_sessions"]):
            sn = f"{qid}:session:{sid}"
            nodes.append({"id":sn,"type":"Session","evidence_class":"DIRECTLY_SUPPLIED_EVIDENCE",
                          "claim_ceiling":"BENCHMARK_INPUT","visibility":"PUBLIC",
                          "metadata":{"session_id":sid,"date":date,"gold_evidence_session":sid in answer_sessions}})
            edges.append({"src":qnode,"rel":"DEPENDS_ON","dst":sn,"metadata":{}})
            for ti, turn in enumerate(session):
                tn = f"{sn}:turn:{ti}"
                nodes.append({"id":tn,"type":"Turn","evidence_class":"DIRECTLY_SUPPLIED_EVIDENCE",
                              "claim_ceiling":"BENCHMARK_INPUT","visibility":"PUBLIC",
                              "metadata":{"role":turn["role"],"content":turn["content"],
                                          "has_answer":bool(turn.get("has_answer", False))}})
                edges.append({"src":sn,"rel":"CONTAINS","dst":tn,"metadata":{}})
    dump_jsonl(out.with_suffix(".nodes.jsonl"), nodes)
    dump_jsonl(out.with_suffix(".edges.jsonl"), edges)
    print(json.dumps({"questions":len(data),"nodes":len(nodes),"edges":len(edges)}, indent=2))

if __name__ == "__main__":
    main()
