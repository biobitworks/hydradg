#!/usr/bin/env python3
"""Hack-Hydra release wrapper for the local Best Use server.

The pinned HydraDB runtime rejected the original standalone `MERGE ... SET`
write shape during the fresh Track-02 CI canary. This release wrapper keeps the
existing local HTTP surface but replaces only the live perturbation writer with
one-row UNWIND writes already demonstrated by the structural/Track-01 canaries.

It also resolves a selected injected Fact directly from HydraDB when the target
vertex is not part of the immutable prepared benchmark fixture. That is required
for the judge golden path: original Fact -> poison Fact -> antidote Fact.

This is a runtime compatibility correction, not a claim that the older write
shape executed successfully.
"""
from __future__ import annotations

import argparse
import time

import best_use_local_server as base
from best_use_typed_graph import clean, norm, stable_id


class ReleaseState(base.State):
    def _one_row_node(self, label: str, row: dict, set_clause: str) -> None:
        self.hydra.query(
            f"UNWIND $rows AS row MERGE (n {{id:row.id}}) SET n:{label}, {set_clause}",
            {"rows": [row]},
        )

    def _live_fact(self, vertex: object, qid: str) -> dict | None:
        """Resolve an injected/live Fact from HydraDB by exact vertex.

        Prepared LongMemEval facts are immutable source transforms. Later poison
        and antidote facts are graph state, so an antidote may legitimately
        target a vertex that is absent from prepared["fact_rows"].
        """
        try:
            vertex_id = int(vertex)
        except (TypeError, ValueError):
            return None
        response = self.hydra.query(
            "MATCH (f:Fact {id:$id}) WHERE f.qid=$qid "
            "RETURN f.id AS vertex, f.qid AS qid, f.subject AS subject, "
            "f.predicate AS predicate, f.object AS object, f.polarity AS polarity, "
            "f.valid_time AS valid_time, f.confidence_bp AS confidence_bp, "
            "f.position AS position, f.source_session_vertex AS source_session_vertex, "
            "f.source_sha256 AS source_sha256, f.evidence_class AS evidence_class, "
            "f.observed_at AS observed_at LIMIT 2",
            {"id": vertex_id, "qid": qid},
        )
        columns = response.get("columns", [])
        rows = response.get("rows", [])
        if not rows:
            return None
        row = rows[0]
        decoded = {}
        for index, column in enumerate(columns):
            if index >= len(row):
                continue
            value = row[index]
            decoded[column] = value.get("value") if isinstance(value, dict) and "value" in value else value
        if not decoded.get("vertex"):
            return None
        return decoded

    def perturb(self, req):
        qid = str(req.get("question_id", "")).strip()
        mode = str(req.get("extractor") or self.default)
        if qid not in self.by:
            raise ValueError("unknown question_id")
        prepared, _ = self.prep(qid, mode)

        target = req.get("target_fact_vertex")
        subject = clean(req.get("subject"), 80)
        predicate = clean(req.get("predicate"), 80)
        new_object = clean(req.get("object"), 160)
        candidates = []
        for row in prepared["fact_rows"]:
            if target is not None and str(row.get("vertex")) == str(target):
                candidates.append(row)
                continue
            if subject and predicate and norm(row.get("subject")) == norm(subject) and norm(row.get("predicate")) == norm(predicate):
                candidates.append(row)

        # Golden-path antidote: the target may be the poison Fact injected by a
        # preceding live event, not one of the original prepared benchmark rows.
        if not candidates and target is not None:
            live = self._live_fact(target, qid)
            if live is not None:
                candidates.append(live)

        if not candidates:
            raise ValueError("no matching source/live fact; load the case and provide target_fact_vertex or matching subject/predicate")

        old = max(candidates, key=lambda row: int(row.get("position", 0) or 0))
        if not new_object:
            raise ValueError("object is required")
        subject = clean(old.get("subject"), 80)
        predicate = clean(old.get("predicate"), 80)

        identity = str(req.get("identity_class") or "UNKNOWN").upper()
        safety = str(req.get("safety_class") or "UNKNOWN").upper()
        if identity not in {"SELF", "NONSELF", "UNKNOWN"}:
            raise ValueError("identity_class must be SELF/NONSELF/UNKNOWN")
        if safety not in {"SAFE", "NONSAFE", "UNKNOWN"}:
            raise ValueError("safety_class must be SAFE/NONSAFE/UNKNOWN")
        decision = "ADMIT" if safety == "SAFE" else ("QUARANTINE" if safety == "NONSAFE" else "CHALLENGE")

        observed = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        event_payload = {
            "qid": qid,
            "source_fact_vertex": int(old["vertex"]),
            "subject": subject,
            "predicate": predicate,
            "old_object": clean(old.get("object"), 160),
            "new_object": new_object,
            "identity_class": identity,
            "safety_class": safety,
            "decision": decision,
            "observed_at": observed,
            "operator_scope": "HACK_HYDRA_DEMO_DECLARATION",
        }
        event_sha = base.chash(event_payload)
        new_vertex = stable_id("live_fact_update", qid, event_sha)
        perturb_vertex = stable_id("perturbation", qid, event_sha)
        class_vertex = stable_id("classification_event", qid, event_sha)
        delta_payload = {
            "before_fact_vertex": int(old["vertex"]),
            "after_fact_vertex": new_vertex,
            "perturbation_vertex": perturb_vertex,
            "classification_vertex": class_vertex,
            "event_sha256": event_sha,
        }
        delta_sha = base.chash(delta_payload)
        delta_vertex = stable_id("fcg_delta", qid, delta_sha)

        self._one_row_node(
            "Fact",
            {
                "id": new_vertex,
                "qid": qid,
                "subject": subject,
                "predicate": predicate,
                "object": new_object,
                "polarity": "affirmed",
                "valid_time": observed,
                "confidence_bp": 10000,
                "position": int(old.get("position", 0) or 0) + 1,
                "source_session_vertex": int(old.get("source_session_vertex", 0) or 0),
                "source_sha256": event_sha,
                "evidence_class": "LIVE_OPERATOR_PERTURBATION",
                "observed_at": observed,
            },
            "n.qid=row.qid,n.subject=row.subject,n.predicate=row.predicate,n.object=row.object,n.polarity=row.polarity,n.valid_time=row.valid_time,n.confidence_bp=row.confidence_bp,n.position=row.position,n.source_session_vertex=row.source_session_vertex,n.source_sha256=row.source_sha256,n.evidence_class=row.evidence_class,n.observed_at=row.observed_at",
        )
        self._one_row_node(
            "Perturbation",
            {
                "id": perturb_vertex,
                "qid": qid,
                "event_sha256": event_sha,
                "observed_at": observed,
                "kind": "FACT_VALUE_UPDATE",
                "claim_ceiling": "LIVE_DEMO_PERTURBATION_ONLY",
            },
            "n.qid=row.qid,n.event_sha256=row.event_sha256,n.observed_at=row.observed_at,n.kind=row.kind,n.claim_ceiling=row.claim_ceiling",
        )
        self._one_row_node(
            "ClassificationEvent",
            {
                "id": class_vertex,
                "qid": qid,
                "identity_class": identity,
                "safety_class": safety,
                "decision": decision,
                "observed_at": observed,
                "delta_sha256": delta_sha,
                "claim_ceiling": "OPERATOR_DECLARED_ANTICUBE_CLASSIFICATION_ONLY",
            },
            "n.qid=row.qid,n.identity_class=row.identity_class,n.safety_class=row.safety_class,n.decision=row.decision,n.observed_at=row.observed_at,n.delta_sha256=row.delta_sha256,n.claim_ceiling=row.claim_ceiling",
        )
        self._one_row_node(
            "FCGDelta",
            {
                "id": delta_vertex,
                "qid": qid,
                "delta_sha256": delta_sha,
                "event_sha256": event_sha,
                "observed_at": observed,
                "claim_ceiling": "HASHED_GRAPH_DELTA_IDENTITY_ONLY",
            },
            "n.qid=row.qid,n.delta_sha256=row.delta_sha256,n.event_sha256=row.event_sha256,n.observed_at=row.observed_at,n.claim_ceiling=row.claim_ceiling",
        )

        edges = [
            (int(old["vertex"]), "SUPERSEDED_BY", new_vertex),
            (perturb_vertex, "TARGETS", int(old["vertex"])),
            (perturb_vertex, "PRODUCES", new_vertex),
            (class_vertex, "CLASSIFIES", new_vertex),
            (delta_vertex, "RECORDS", perturb_vertex),
        ]
        if norm(old.get("object")) != norm(new_object):
            edges.extend([
                (int(old["vertex"]), "CONTRADICTS", new_vertex),
                (new_vertex, "CONTRADICTS", int(old["vertex"])),
            ])
        for src, relation, dst in edges:
            self.hydra.query(
                f"MATCH (a {{id:$src}}),(b {{id:$dst}}) MERGE (a)-[:{relation}]->(b)",
                {"src": src, "dst": dst},
            )

        return {
            "schema": "hydradg.live_fcg_delta.v3",
            "question_id": qid,
            "extractor": mode,
            "before": old,
            "after": {
                "vertex": new_vertex,
                "subject": subject,
                "predicate": predicate,
                "object": new_object,
                "observed_at": observed,
            },
            "perturbation": {"vertex": perturb_vertex, "event_sha256": event_sha},
            "fcg_delta": {"vertex": delta_vertex, "delta_sha256": delta_sha},
            "anticube": {
                "vertex": class_vertex,
                "identity_class": identity,
                "safety_class": safety,
                "decision": decision,
                "scope": "OPERATOR_DECLARED_HACKATHON_DEMO_POLICY",
            },
            "edges": [{"src": src, "rel": relation, "dst": dst} for src, relation, dst in edges],
            "target_resolution": "PREPARED_OR_LIVE_HYDRADB_FACT",
            "hydradb_write_shape": "ONE_ROW_UNWIND_MERGE_SET_COMPATIBLE_WITH_PINNED_RUNTIME",
            "claim_ceiling": "LIVE_HYDRADB_FCG_PERTURBATION_DEMO_ONLY",
            "signature_state": "NOT_SIGNED",
            "merkle_state": "NOT_MERKLE_COMMITTED",
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8443/v1/graphs/default/query")
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--default-extractor", dest="extractor", default="heuristic")
    parser.add_argument("--ollarma-url", default="http://127.0.0.1:8484")
    parser.add_argument("--model", default="")
    parser.add_argument("--cache-dir", default=str(base.Path.home() / ".local/share/hydradg-best-use/extract-cache"))
    parser.add_argument("--receipts", default=str(base.Path.home() / ".local/share/hydradg-best-use/receipts/server_events.jsonl"))
    args = parser.parse_args()

    server = base.ThreadingHTTPServer((args.bind, args.port), base.app(args))
    print(f"HydraDG Best Use release server http://{args.bind}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
