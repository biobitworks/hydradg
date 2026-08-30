#!/usr/bin/env python3
"""HydraDG SeedGraph v1: deterministic content-addressed hierarchy builder/query engine.

No model calls. SHA-256 is used for byte/object identity; semantic lookup uses
frozen canonical seed keys. Large source payloads stay in Parquet/JSON sources
or a deterministic Track03 turn projection. Gold/reference fields are not
written to model-visible tables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import socket
import statistics
import time
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "hydradg.seedgraph.hierarchy.v1"
EXPECTED_HOST = "magicSTUDIObox.local"
STOPWORDS = frozenset(
    "a an and are as at be been by for from has have he her hers him his i in is it its of on or our she that the their them they this to was we were what when where which who why will with you your".split()
)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[._:/-][A-Za-z0-9]+)*")
SENTENCE_BREAK_RE = re.compile(r"(?<=[.!?])\s+|\n+")
PARAGRAPH_BREAK_RE = re.compile(r"\n\s*\n+")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def normalized_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def typed_object_id(object_type: str, identity: dict[str, Any]) -> tuple[str, str]:
    digest = sha256_bytes(b"hydradg.seedgraph.object.v1\0" + canonical_json({"type": object_type, **identity}))
    return f"{object_type.lower()}:{digest}", digest


def seed_id_for_key(key: str) -> tuple[str, str]:
    digest = sha256_bytes(b"hydradg.seedgraph.seed.v1\0" + key.encode("utf-8"))
    return f"seed_atom_fco:{digest}", digest


def split_with_spans(text: str, breaker: re.Pattern[str]) -> list[tuple[int, int, str]]:
    if not text:
        return []
    out: list[tuple[int, int, str]] = []
    start = 0
    for m in breaker.finditer(text):
        end = m.start()
        if text[start:end].strip():
            left = start
            right = end
            while left < right and text[left].isspace(): left += 1
            while right > left and text[right - 1].isspace(): right -= 1
            out.append((left, right, text[left:right]))
        start = m.end()
    if text[start:].strip():
        left, right = start, len(text)
        while left < right and text[left].isspace(): left += 1
        while right > left and text[right - 1].isspace(): right -= 1
        out.append((left, right, text[left:right]))
    return out


def seed_occurrences(text: str, max_n: int = 3) -> list[dict[str, Any]]:
    text = normalized_text(text)
    toks = []
    for m in TOKEN_RE.finditer(text):
        raw = m.group(0)
        key = raw.lower()
        if key in STOPWORDS:
            continue
        toks.append((key, m.start(), m.end(), raw))
    out: list[dict[str, Any]] = []
    for n in range(1, max_n + 1):
        for i in range(0, len(toks) - n + 1):
            window = toks[i:i+n]
            key = " ".join(x[0] for x in window)
            out.append({"canonical_key": key, "char_start": window[0][1], "char_end": window[-1][2]})
    return out


def population_variance(values: list[float]) -> float | None:
    if not values:
        return None
    return statistics.pvariance(values) if len(values) > 1 else 0.0


class GraphBuilder:
    def __init__(self, score_map: dict[str, dict[str, Any]] | None = None):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.seed_occ_index: dict[str, list[str]] = defaultdict(list)
        self.seed_key_by_id: dict[str, str] = {}
        self.question_rows: list[dict[str, Any]] = []
        self.question_seed_rows: list[dict[str, Any]] = []
        self.score_map = score_map or {}
        self.desc_scores: dict[str, list[float]] = defaultdict(list)
        self.source_seed_df: dict[str, int] = defaultdict(int)

    def add_node(self, row: dict[str, Any]) -> str:
        oid = row["object_id"]
        if oid not in self.nodes:
            self.nodes[oid] = row
        return oid

    def add_edge(self, source: str, target: str, relation: str, metadata: dict[str, Any] | None = None):
        edge_identity = {"source": source, "target": target, "relation": relation, "metadata": metadata or {}}
        self.edges.append({
            "source": source,
            "target": target,
            "relation": relation,
            "edge_sha256": sha256_bytes(b"hydradg.seedgraph.edge.v1\0" + canonical_json(edge_identity)),
            "metadata_json": json.dumps(metadata or {}, sort_keys=True),
        })

    def source_node(self, dataset: str, source_path: Path, source_sha: str) -> str:
        oid = f"source_file_fco:{source_sha}"
        return self.add_node({
            "schema": SCHEMA, "object_id": oid, "object_sha256": source_sha,
            "object_type": "SOURCE_FILE_FCO", "visibility": "MODEL_VISIBLE_SAFE", "depth": 5,
            "canonical_key": None, "display_text": source_path.name, "source_sha256": source_sha,
            "source_pointer_json": json.dumps({"dataset_id": dataset, "source_path": str(source_path), "source_file_sha256": source_sha}, sort_keys=True),
            "score_bundle_json": "{}", "aggregate_scores_json": "{}",
            "metadata_json": json.dumps({"byte_size": source_path.stat().st_size}, sort_keys=True),
        })

    def add_text_node(self, object_type: str, visibility: str, depth: int, parent_id: str,
                      relation: str, text: str, pointer: dict[str, Any], metadata: dict[str, Any]) -> str:
        content_sha = sha256_bytes(text.encode("utf-8"))
        identity = {"content_sha256": content_sha, "pointer": pointer, "metadata_identity": metadata}
        oid, obj_sha = typed_object_id(object_type, identity)
        self.add_node({
            "schema": SCHEMA, "object_id": oid, "object_sha256": obj_sha,
            "object_type": object_type, "visibility": visibility, "depth": depth,
            "canonical_key": None, "display_text": text, "source_sha256": pointer.get("source_file_sha256"),
            "source_pointer_json": json.dumps(pointer, sort_keys=True), "score_bundle_json": "{}",
            "aggregate_scores_json": "{}", "metadata_json": json.dumps({**metadata, "content_sha256": content_sha, "byte_size": len(text.encode("utf-8"))}, sort_keys=True),
        })
        self.add_edge(oid, parent_id, relation)
        return oid

    def add_seed_occurrences(self, text: str, sentence_id: str, sentence_pointer: dict[str, Any], ancestor_ids: list[str], visibility: str = "MODEL_VISIBLE"):
        seen_in_sentence: set[str] = set()
        for occ in seed_occurrences(text):
            key = occ["canonical_key"]
            seed_id, seed_sha = seed_id_for_key(key)
            score_bundle = self.score_map.get(key, {})
            self.add_node({
                "schema": SCHEMA, "object_id": seed_id, "object_sha256": seed_sha,
                "object_type": "SEED_ATOM_FCO", "visibility": visibility, "depth": 0,
                "canonical_key": key, "display_text": key, "source_sha256": None,
                "source_pointer_json": "{}", "score_bundle_json": json.dumps(score_bundle, sort_keys=True),
                "aggregate_scores_json": "{}", "metadata_json": "{}",
            })
            self.seed_key_by_id[seed_id] = key
            ptr = dict(sentence_pointer)
            base_start = int(ptr.get("char_start") or 0)
            ptr["char_start"] = base_start + occ["char_start"]
            ptr["char_end"] = base_start + occ["char_end"]
            selected = text[occ["char_start"]:occ["char_end"]]
            ptr["selected_text_sha256"] = sha256_bytes(selected.encode("utf-8"))
            occ_identity = {"seed_atom_id": seed_id, "sentence_id": sentence_id, "pointer": ptr}
            occ_id, occ_sha = typed_object_id("ATOM_OCCURRENCE_FCO", occ_identity)
            self.add_node({
                "schema": SCHEMA, "object_id": occ_id, "object_sha256": occ_sha,
                "object_type": "ATOM_OCCURRENCE_FCO", "visibility": visibility, "depth": 0,
                "canonical_key": key, "display_text": selected, "source_sha256": ptr.get("source_file_sha256"),
                "source_pointer_json": json.dumps(ptr, sort_keys=True), "score_bundle_json": json.dumps(score_bundle, sort_keys=True),
                "aggregate_scores_json": "{}", "metadata_json": json.dumps({"seed_atom_id": seed_id}, sort_keys=True),
            })
            self.add_edge(occ_id, seed_id, "INSTANCE_OF")
            self.add_edge(occ_id, sentence_id, "IN_SENTENCE")
            self.seed_occ_index[seed_id].append(occ_id)
            if key not in seen_in_sentence:
                self.source_seed_df[key] += 1
                seen_in_sentence.add(key)
            score = score_bundle.get("context_score")
            if isinstance(score, (int, float)):
                for aid in [sentence_id, *ancestor_ids]:
                    self.desc_scores[aid].append(float(score))

    def add_hierarchy_for_text(self, text: str, parent_id: str, parent_type: str, base_pointer: dict[str, Any], metadata: dict[str, Any]):
        # Paragraph/turn parents may already represent the smallest container. Build paragraphs if text has multiple paragraphs.
        paragraphs = split_with_spans(text, PARAGRAPH_BREAK_RE) or [(0, len(text), text)]
        for p_idx, (p_start, p_end, p_text) in enumerate(paragraphs):
            p_ptr = dict(base_pointer); p_ptr.update({"char_start": p_start, "char_end": p_end, "selected_text_sha256": sha256_bytes(p_text.encode("utf-8"))})
            para_id = self.add_text_node("PARAGRAPH_FCO", "MODEL_VISIBLE", 2, parent_id, "IN_PARENT", p_text, p_ptr, {**metadata, "paragraph_index": p_idx})
            sentences = split_with_spans(p_text, SENTENCE_BREAK_RE) or [(0, len(p_text), p_text)]
            for s_idx, (s0, s1, s_text) in enumerate(sentences):
                abs0, abs1 = p_start + s0, p_start + s1
                s_ptr = dict(base_pointer); s_ptr.update({"char_start": abs0, "char_end": abs1, "selected_text_sha256": sha256_bytes(s_text.encode("utf-8"))})
                sent_id = self.add_text_node("SENTENCE_FCO", "MODEL_VISIBLE", 1, para_id, "IN_PARAGRAPH", s_text, s_ptr, {**metadata, "paragraph_index": p_idx, "sentence_index": s_idx})
                self.add_seed_occurrences(s_text, sent_id, s_ptr, [para_id, parent_id], "MODEL_VISIBLE")

    def finalize_aggregates(self):
        for oid, vals in self.desc_scores.items():
            node = self.nodes.get(oid)
            if not node: continue
            agg = {
                "context_count": len(vals), "context_mean": (sum(vals)/len(vals)) if vals else None,
                "context_variance": population_variance(vals), "context_min": min(vals) if vals else None,
                "context_max": max(vals) if vals else None,
            }
            node["aggregate_scores_json"] = json.dumps(agg, sort_keys=True)

    def add_question(self, dataset: str, case_id: str, text: str, source_pointer: dict[str, Any]):
        q_identity = {"dataset": dataset, "case_id": case_id, "question_sha256": sha256_bytes(text.encode("utf-8"))}
        q_id, q_sha = typed_object_id("QUESTION_FCO", q_identity)
        self.question_rows.append({
            "schema": SCHEMA, "question_fco_id": q_id, "object_sha256": q_sha,
            "dataset": dataset, "case_id": case_id, "question_text": text,
            "question_sha256": sha256_bytes(text.encode("utf-8")),
            "visibility": "EVAL_QUERY", "source_pointer_json": json.dumps(source_pointer, sort_keys=True),
        })
        for occ in seed_occurrences(text):
            seed_id, _ = seed_id_for_key(occ["canonical_key"])
            occ_identity = {"question_fco_id": q_id, "seed_atom_id": seed_id, "char_start": occ["char_start"], "char_end": occ["char_end"]}
            qo_id, qo_sha = typed_object_id("QUESTION_ATOM_OCCURRENCE_FCO", occ_identity)
            self.question_seed_rows.append({
                "question_fco_id": q_id, "question_atom_occurrence_id": qo_id,
                "object_sha256": qo_sha, "seed_atom_id": seed_id,
                "canonical_key": occ["canonical_key"], "char_start": occ["char_start"], "char_end": occ["char_end"],
                "visibility": "EVAL_QUERY",
            })


def load_score_map(path: Path | None) -> tuple[dict[str, dict[str, Any]], str]:
    if path is None:
        return {}, "UNAVAILABLE"
    score_map: dict[str, dict[str, Any]] = {}
    with path.open() as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            key = obj.get("canonical_key")
            if key:
                score_map[str(key)] = {k: v for k, v in obj.items() if k != "canonical_key"}
    return score_map, "AVAILABLE" if score_map else "UNAVAILABLE"


def flatten_longmemeval_turns(source_json: Path, output_parquet: Path) -> tuple[str, list[dict[str, Any]]]:
    import pandas as pd
    source_sha = sha256_file(source_json)
    raw = json.loads(source_json.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for item_idx, item in enumerate(raw):
        case_id = str(item.get("question_id"))
        sessions = item.get("haystack_sessions", [])
        for s_idx, session in enumerate(sessions):
            turns = session if isinstance(session, list) else [session]
            for t_idx, turn in enumerate(turns):
                if isinstance(turn, dict):
                    role, content = str(turn.get("role", "user")), str(turn.get("content", ""))
                else:
                    role, content = "unknown", str(turn)
                pointer_key = f"{case_id}|{s_idx}|{t_idx}"
                rows.append({"pointer_key": pointer_key, "case_id": case_id, "item_index": item_idx, "session_index": s_idx, "turn_index": t_idx, "role": role, "content": content, "content_sha256": sha256_bytes(content.encode("utf-8")), "origin_json_sha256": source_sha})
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(output_parquet, index=False)
    return sha256_file(output_parquet), rows


def build(args: argparse.Namespace) -> dict[str, Any]:
    if args.require_studio and socket.gethostname() != EXPECTED_HOST:
        raise RuntimeError(f"HOST_IDENTITY_MISMATCH expected={EXPECTED_HOST} actual={socket.gethostname()}")
    import pandas as pd
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    q_path = Path(args.track01_questions); d_path = Path(args.track01_documents); lme_path = Path(args.track03_json)
    for p in (q_path, d_path, lme_path):
        if not p.exists(): raise FileNotFoundError(p)
    scores, score_state = load_score_map(Path(args.atom_scores) if args.atom_scores else None)
    gb = GraphBuilder(scores)
    source_hashes = {"track01_questions": sha256_file(q_path), "track01_documents": sha256_file(d_path), "track03_json": sha256_file(lme_path)}

    # Track01 source documents. Load only model-visible columns.
    src_doc = gb.source_node("EnterpriseRAG-Bench", d_path, source_hashes["track01_documents"])
    docs = pd.read_parquet(d_path, columns=["doc_id", "content"])
    for _, row in docs.iterrows():
        doc_id, content = str(row["doc_id"]), str(row["content"])
        ptr = {"dataset_id":"EnterpriseRAG-Bench","source_path":str(d_path),"source_file_sha256":source_hashes["track01_documents"],"storage_kind":"PARQUET","row_key_field":"doc_id","row_key":doc_id,"field_path":"content","char_start":0,"char_end":len(content),"selected_text_sha256":sha256_bytes(content.encode("utf-8"))}
        doc_node = gb.add_text_node("DOCUMENT_FCO","MODEL_VISIBLE",3,src_doc,"IN_SOURCE",content,ptr,{"doc_id":doc_id})
        gb.add_hierarchy_for_text(content, doc_node, "DOCUMENT_FCO", ptr, {"doc_id":doc_id})

    # Track01 questions. Deliberately load no gold/reference/expected-doc columns.
    questions = pd.read_parquet(q_path, columns=["question_id", "question"]).head(300)
    for _, row in questions.iterrows():
        qid, text = str(row["question_id"]), str(row["question"])
        ptr = {"dataset_id":"EnterpriseRAG-Bench","source_path":str(q_path),"source_file_sha256":source_hashes["track01_questions"],"storage_kind":"PARQUET","row_key_field":"question_id","row_key":qid,"field_path":"question","char_start":0,"char_end":len(text),"selected_text_sha256":sha256_bytes(text.encode("utf-8"))}
        gb.add_question("EnterpriseRAG-Bench", f"EnterpriseRAG-Bench_{qid}", text, ptr)

    # Track03 deterministic turn projection from real source JSON.
    projection_path = out / "track03_turn_projection.parquet"
    projection_sha, turn_rows = flatten_longmemeval_turns(lme_path, projection_path)
    src_t3 = gb.source_node("LongMemEval-S-full500", projection_path, projection_sha)
    raw_lme = json.loads(lme_path.read_text(encoding="utf-8"))
    for item in raw_lme:
        qid, qtext = str(item.get("question_id")), str(item.get("question"))
        qptr = {"dataset_id":"LongMemEval-S-full500","source_path":str(lme_path),"source_file_sha256":source_hashes["track03_json"],"storage_kind":"JSON","row_key_field":"question_id","row_key":qid,"field_path":"question","selected_text_sha256":sha256_bytes(qtext.encode("utf-8"))}
        gb.add_question("LongMemEval-S-full500", f"LongMemEval-S_{qid}", qtext, qptr)
    by_case_session: dict[tuple[str,int], list[dict[str,Any]]] = defaultdict(list)
    for r in turn_rows: by_case_session[(r["case_id"], int(r["session_index"]))].append(r)
    for (case_id, s_idx), turns in by_case_session.items():
        session_identity = {"case_id":case_id,"session_index":s_idx,"projection_sha256":projection_sha}
        session_id, session_sha = typed_object_id("SESSION_FCO", session_identity)
        gb.add_node({"schema":SCHEMA,"object_id":session_id,"object_sha256":session_sha,"object_type":"SESSION_FCO","visibility":"MODEL_VISIBLE","depth":4,"canonical_key":None,"display_text":None,"source_sha256":projection_sha,"source_pointer_json":"{}","score_bundle_json":"{}","aggregate_scores_json":"{}","metadata_json":json.dumps(session_identity,sort_keys=True)})
        gb.add_edge(session_id, src_t3, "IN_SOURCE")
        for r in sorted(turns, key=lambda x: int(x["turn_index"])):
            content = r["content"]
            ptr = {"dataset_id":"LongMemEval-S-full500","source_path":str(projection_path),"source_file_sha256":projection_sha,"origin_source_sha256":source_hashes["track03_json"],"storage_kind":"PARQUET","row_key_field":"pointer_key","row_key":r["pointer_key"],"field_path":"content","char_start":0,"char_end":len(content),"selected_text_sha256":r["content_sha256"]}
            turn_id = gb.add_text_node("TURN_FCO","MODEL_VISIBLE",3,session_id,"IN_SESSION",content,ptr,{"case_id":case_id,"session_index":s_idx,"turn_index":int(r["turn_index"]),"role":r["role"]})
            gb.add_hierarchy_for_text(content, turn_id, "TURN_FCO", ptr, {"case_id":case_id,"session_index":s_idx,"turn_index":int(r["turn_index"])})

    gb.finalize_aggregates()
    nodes = pd.DataFrame(gb.nodes.values()); edges = pd.DataFrame(gb.edges)
    seed_rows = []
    for seed_id, occs in gb.seed_occ_index.items():
        key = gb.seed_key_by_id[seed_id]
        seed_rows.append({"seed_atom_id":seed_id,"canonical_key":key,"occurrence_count":len(occs),"document_frequency":gb.source_seed_df.get(key,0),"occurrence_ids_json":json.dumps(sorted(occs))})
    nodes_path=out/"nodes.parquet"; edges_path=out/"edges.parquet"; index_path=out/"seed_index.parquet"; questions_path=out/"questions.parquet"; qseeds_path=out/"question_seeds.parquet"
    nodes.to_parquet(nodes_path,index=False); edges.to_parquet(edges_path,index=False); pd.DataFrame(seed_rows).to_parquet(index_path,index=False); pd.DataFrame(gb.question_rows).to_parquet(questions_path,index=False); pd.DataFrame(gb.question_seed_rows).to_parquet(qseeds_path,index=False)
    artifact_hashes={p.name:sha256_file(p) for p in [nodes_path,edges_path,index_path,questions_path,qseeds_path,projection_path]}
    receipt={"schema":"hydradg.seedgraph.build_receipt.v1","execution_host":socket.gethostname(),"source_hashes":source_hashes,"artifact_hashes":artifact_hashes,"context_score_state":score_state,"counts":{"nodes":len(nodes),"edges":len(edges),"seeds":len(seed_rows),"questions":len(gb.question_rows),"question_seed_occurrences":len(gb.question_seed_rows)},"track02_state":"BLOCKED_REAL_CASE_CONTRACT_NOT_ESTABLISHED","zero_model_calls":True,"signature_state":"NOT_SIGNED","merkle_mmr_state":"NOT_COMMITTED","timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    receipt["receipt_sha256"]=sha256_bytes(canonical_json(receipt))
    (out/"BUILD_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    (out/"SHA256SUMS.txt").write_text("\n".join(f"{v}  {k}" for k,v in sorted(artifact_hashes.items()))+"\n")
    return receipt


def _minmax(value: float | None, values: list[float]) -> float:
    if value is None or not values: return 0.0
    lo, hi=min(values),max(values)
    return 0.0 if hi==lo else (value-lo)/(hi-lo)


def query(args: argparse.Namespace) -> dict[str, Any]:
    import pandas as pd
    root=Path(args.index_dir)
    nodes=pd.read_parquet(root/"nodes.parquet"); edges=pd.read_parquet(root/"edges.parquet"); idx=pd.read_parquet(root/"seed_index.parquet"); questions=pd.read_parquet(root/"questions.parquet")
    if args.question_fco_id:
        qrow=questions.loc[questions.question_fco_id==args.question_fco_id]
        if qrow.empty: raise KeyError(args.question_fco_id)
        question_text=str(qrow.iloc[0].question_text); question_id=str(qrow.iloc[0].question_fco_id)
    else:
        question_text=str(args.question_text); question_id=typed_object_id("QUESTION_FCO",{"ad_hoc_question_sha256":sha256_bytes(question_text.encode())})[0]
    t0=time.perf_counter(); qseeds=seed_occurrences(question_text); unique_q=sorted({x["canonical_key"] for x in qseeds})
    idx_by_key={str(r.canonical_key):r for _,r in idx.iterrows()}; matched=[k for k in unique_q if k in idx_by_key]
    total_docs=max(1,int(nodes.object_type.isin(["DOCUMENT_FCO","TURN_FCO"]).sum()))
    idf={k:math.log((1+total_docs)/(1+int(idx_by_key[k].document_frequency)))+1.0 for k in matched}
    total_idf=sum(idf.values()) or 1.0
    node_by_id={str(r.object_id):r for _,r in nodes.iterrows()}; parent_of=defaultdict(list)
    for _,e in edges.iterrows():
        if str(e.relation) in {"IN_SENTENCE","IN_PARAGRAPH","IN_PARENT","IN_SESSION","IN_SOURCE"}: parent_of[str(e.source)].append(str(e.target))
    support:dict[str,set[str]]=defaultdict(set); candidate_occurrences:set[str]=set(); edge_traversals=0
    for key in matched:
        for occ_id in json.loads(str(idx_by_key[key].occurrence_ids_json)):
            candidate_occurrences.add(occ_id); frontier=[occ_id]; seen={occ_id}
            while frontier:
                cur=frontier.pop(); support[cur].add(key)
                for par in parent_of.get(cur,[]):
                    edge_traversals+=1
                    if par not in seen:
                        seen.add(par); frontier.append(par)
                    support[par].add(key)
    candidates=[]
    allowed={"SENTENCE_FCO","PARAGRAPH_FCO","TURN_FCO","DOCUMENT_FCO"}
    for oid,keys in support.items():
        row=node_by_id.get(oid)
        if row is None or str(row.object_type) not in allowed: continue
        weighted=sum(idf.get(k,0.0) for k in keys)/total_idf
        agg=json.loads(str(row.aggregate_scores_json) or "{}")
        meta=json.loads(str(row.metadata_json) or "{}")
        candidates.append({"object_id":oid,"object_type":str(row.object_type),"depth":int(row.depth),"query_seed_keys":sorted(keys),"idf_weighted_query_coverage":weighted,"context_mean":agg.get("context_mean"),"context_variance":agg.get("context_variance"),"byte_size":int(meta.get("byte_size",0)),"pointer":json.loads(str(row.source_pointer_json) or "{}")})
    means=[float(c["context_mean"]) for c in candidates if isinstance(c["context_mean"],(int,float))]; vars_=[float(c["context_variance"]) for c in candidates if isinstance(c["context_variance"],(int,float))]; bytes_=[float(c["byte_size"]) for c in candidates]
    context_available=bool(means)
    for c in candidates:
        cmean=_minmax(float(c["context_mean"]) if c["context_mean"] is not None else None,means); cvar=_minmax(float(c["context_variance"]) if c["context_variance"] is not None else None,vars_); bcost=_minmax(float(c["byte_size"]),bytes_)
        # Coverage delta is measured against the best direct child candidate support when available.
        child_cov=0.0
        for _,e in edges.iterrows():
            if str(e.target)==c["object_id"] and str(e.source) in support:
                sk=support[str(e.source)]; child_cov=max(child_cov,sum(idf.get(k,0.0) for k in sk)/total_idf)
        cov_delta=max(0.0,c["idf_weighted_query_coverage"]-child_cov)
        c["positive_coverage_delta"]=cov_delta; c["normalized_context_mean"]=cmean; c["normalized_context_variance"]=cvar; c["normalized_marginal_byte_cost"]=bcost
        if context_available:
            c["utility"]=0.50*c["idf_weighted_query_coverage"]+0.20*cov_delta+0.15*cmean-0.03*cvar-0.02*bcost
        else:
            # Renormalized 0.50/0.20/-0.02 over available terms.
            c["utility"]=(0.50*c["idf_weighted_query_coverage"]+0.20*cov_delta-0.02*bcost)/0.72
    candidates.sort(key=lambda c:(-c["utility"],c["byte_size"],c["object_id"]))
    selected=[]; covered=set(); budget=int(args.max_evidence_bytes)
    for c in candidates:
        new=set(c["query_seed_keys"])-covered
        if not new: continue
        if sum(x["byte_size"] for x in selected)+c["byte_size"]>budget: continue
        selected.append(c); covered.update(c["query_seed_keys"])
        current=sum(idf.get(k,0.0) for k in covered)/total_idf
        if current>=float(args.coverage_target) or len(selected)>=int(args.max_nodes): break
    lookup_ms=(time.perf_counter()-t0)*1000.0
    receipt={"schema":"hydradg.seedgraph.query_receipt.v1","question_fco_id":question_id,"question_sha256":sha256_bytes(question_text.encode()),"question_seed_count":len(unique_q),"matched_seed_count":len(matched),"candidate_occurrence_count":len(candidate_occurrences),"hierarchy_nodes_scored":len(candidates),"graph_edges_traversed":edge_traversals,"selected_evidence_nodes":[{k:v for k,v in c.items() if k!="pointer"} for c in selected],"selected_pointers":[c["pointer"] for c in selected],"idf_weighted_coverage":sum(idf.get(k,0.0) for k in covered)/total_idf,"evidence_bytes_planned":sum(c["byte_size"] for c in selected),"context_score_state":"AVAILABLE" if context_available else "UNAVAILABLE","index_and_graph_wall_ms":round(lookup_ms,3),"zero_model_calls":True,"visibility_contract":"QUESTION_EVAL_QUERY__SOURCE_MODEL_VISIBLE__GOLD_ABSENT"}
    receipt["receipt_sha256"]=sha256_bytes(canonical_json(receipt))
    if args.receipt: Path(args.receipt).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt


def cli():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("build"); b.add_argument("--track01-questions",default="/Users/byron/.local/share/hydradg-datasets/track01/enterprise-rag-bench/data/questions/test.parquet"); b.add_argument("--track01-documents",default="/Users/byron/.local/share/hydradg-datasets/track01/enterprise-rag-bench/data/documents/test.parquet"); b.add_argument("--track03-json",default="/Users/byron/.local/share/hydradg-datasets/track03/longmemeval-cleaned/longmemeval_s_cleaned.json"); b.add_argument("--atom-scores"); b.add_argument("--output-dir",required=True); b.add_argument("--require-studio",action="store_true")
    q=sub.add_parser("query"); q.add_argument("--index-dir",required=True); g=q.add_mutually_exclusive_group(required=True); g.add_argument("--question-fco-id"); g.add_argument("--question-text"); q.add_argument("--coverage-target",type=float,default=0.80); q.add_argument("--max-nodes",type=int,default=8); q.add_argument("--max-evidence-bytes",type=int,default=32768); q.add_argument("--receipt")
    a=p.parse_args(); result=build(a) if a.cmd=="build" else query(a); print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__": cli()
