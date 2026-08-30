#!/usr/bin/env python3
"""NewInML full SeedGraph traceability pipeline.

Stages:
  S1  Tex/PDF atom extraction with seedgraph.merkle.atoms leaf hashing
  S2  Ledger-backed GraphWriter.write_canonical_node() per atom (source_seed_id bound)
  S3  PROMPT-020 STEP1 seed-of-truth assembly (refuse without Merkle leaves)
  S4  Phase 73 intra-atom S-P-O + logic map + sentence diagram
  S5  Transformation ID binding (code SHA + data SHA)
  S6  Traceability gate (blocks OpenReview/AntiCube public upload until GREEN)

Does NOT claim draft->publication traceability unless S6 gate passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEEDGRAPH_ROOT = Path(os.environ.get("SEEDGRAPH_ROOT", "/Users/byron/projects/active/seedgraph"))
GSD_ROOT = Path(os.environ.get("GSD_ROOT", "/Users/byron/projects/active/gettingsciencedone"))

MANUSCRIPT = ROOT / "paper/newinml2026_solo/final_v4/manuscript"
MAIN_TEX = MANUSCRIPT / "main.tex"
APPENDIX_TEX = MANUSCRIPT / "appendix.tex"
PDF_PATH = MANUSCRIPT / "build/main.pdf"

OUT = ROOT / "paper/newinml2026_solo/seedgraph_traceability"
ATOMS_DIR = OUT / "atoms"
SOT_DIR = OUT / "seeds_of_truth"
MAPS_DIR = OUT / "maps"
LEDGER_PATH = OUT / "ledger/provenance.sqlite"

TRANSFORMATION_SCRIPT = Path(__file__)
EXTRACTOR_VERSION = "hydradg.seedgraph_traceability.v1"
AGENT = "hydradg-newinml-seedgraph-traceability/1.0.0"


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cjson(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + ("\n" if rows else ""))


def transformation_id(script_sha: str, data_sha: str, stage: str) -> str:
    return sha256_bytes(cjson({"script_sha": script_sha, "data_sha": data_sha, "stage": stage}))


@dataclass
class AtomRecord:
    atom_type: str
    seed_id: str
    merkle_leaf_hash: str
    source_seed_id: str
    source_pointer: str
    normalized_type: str
    properties: dict[str, Any] = field(default_factory=dict)
    text: str | None = None
    raw_seed: dict[str, Any] | None = None


def _import_seedgraph():
    sys.path.insert(0, str(SEEDGRAPH_ROOT / "src"))
    from seedgraph.canonical import canonical_hash
    from seedgraph.merkle.atoms import (
        hash_citation_leaf,
        hash_figure_leaf,
        hash_sentence_leaf,
        hash_table_leaf,
    )
    from seedgraph.schema.identity import canonical_seed_id

    return canonical_hash, canonical_seed_id, hash_citation_leaf, hash_figure_leaf, hash_sentence_leaf, hash_table_leaf


def parse_bibliography(tex: str) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for m in re.finditer(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})", tex, re.S):
        key = m.group(1).strip()
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        year_m = re.search(r"\b(19|20)\d{2}\b", body)
        year = int(year_m.group(0)) if year_m else 0
        title = body.split(".")[0].strip() if body else key
        entries[key] = {"bibkey": key, "title": title, "year": year, "authors": [], "doi": None, "pmid": None, "body": body}
    return entries


def extract_sentences(tex: str, source_pointer: str, source_seed_id: str, hash_sentence_leaf, canonical_seed_id) -> list[AtomRecord]:
    atoms: list[AtomRecord] = []
    sections = list(re.finditer(r"\\section\{([^}]+)\}", tex))
    section_spans: list[tuple[str, int, int]] = []
    for i, sm in enumerate(sections):
        start = sm.end()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(tex)
        section_spans.append((sm.group(1), start, end))

    def section_for(pos: int) -> str:
        for title, start, end in section_spans:
            if start <= pos < end:
                return title
        return "preamble"

    # Abstract
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if abstract:
        text = re.sub(r"\s+", " ", abstract.group(1)).strip()
        offset = abstract.start(1)
        for si, sent in enumerate(re.split(r"(?<=[.!?])\s+", text)):
            sent = sent.strip()
            if len(sent) < 5:
                continue
            byte_start, byte_end = offset, offset + len(sent)
            leaf = hash_sentence_leaf(sent, (byte_start, byte_end))
            sid = canonical_seed_id(content_hash=leaf)
            atoms.append(
                AtomRecord(
                    atom_type="sentence",
                    seed_id=sid,
                    merkle_leaf_hash=leaf,
                    source_seed_id=source_seed_id,
                    source_pointer=f"{source_pointer}:abstract:sent:{si}",
                    normalized_type="sentence",
                    text=sent,
                    properties={"section": "abstract", "byte_range": [byte_start, byte_end]},
                )
            )
            offset = byte_end + 1

    # Body sentences (skip abstract, bibliography, figures, tables)
    skip_ranges = []
    if abstract:
        skip_ranges.append((abstract.start(), abstract.end()))
    for pat in (r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", r"\\begin\{table\}.*?\\end\{table\}", r"\\begin\{figure\}.*?\\end\{figure\}"):
        for m in re.finditer(pat, tex, re.S):
            skip_ranges.append((m.start(), m.end()))

    def in_skip(pos: int) -> bool:
        return any(a <= pos < b for a, b in skip_ranges)

    sent_idx = 0
    for m in re.finditer(r"[^.!?]+[.!?]", tex):
        if in_skip(m.start()):
            continue
        sent = re.sub(r"\s+", " ", m.group(0)).strip()
        sent = re.sub(r"\\cite\{[^}]+\}", "", sent)
        sent = re.sub(r"\\[a-zA-Z]+\{?[^}]*\}?", "", sent).strip()
        if len(sent) < 20:
            continue
        byte_start, byte_end = m.start(), m.end()
        leaf = hash_sentence_leaf(sent, (byte_start, byte_end))
        sid = canonical_seed_id(content_hash=leaf)
        atoms.append(
            AtomRecord(
                atom_type="sentence",
                seed_id=sid,
                merkle_leaf_hash=leaf,
                source_seed_id=source_seed_id,
                source_pointer=f"{source_pointer}:body:sent:{sent_idx}",
                normalized_type="sentence",
                text=sent,
                properties={"section": section_for(byte_start), "byte_range": [byte_start, byte_end]},
            )
        )
        sent_idx += 1
    return atoms


def extract_citations(tex: str, bib: dict[str, dict], source_pointer: str, source_seed_id: str, hash_citation_leaf, canonical_seed_id) -> list[AtomRecord]:
    atoms: list[AtomRecord] = []
    cite_occ: dict[str, int] = {}
    for m in re.finditer(r"\\cite\{([^}]+)\}", tex):
        line = tex[: m.start()].count("\n") + 1
        keys = [k.strip() for k in m.group(1).split(",")]
        for key in keys:
            meta = bib.get(key, {"bibkey": key, "title": key, "year": 0, "authors": [], "doi": None, "pmid": None})
            leaf = hash_citation_leaf(meta["authors"], meta["title"], meta["year"], meta.get("doi"), meta.get("pmid"))
            idx = cite_occ.get(key, 0)
            cite_occ[key] = idx + 1
            sid = canonical_seed_id(content_hash=leaf)
            atoms.append(
                AtomRecord(
                    atom_type="citation",
                    seed_id=sid,
                    merkle_leaf_hash=leaf,
                    source_seed_id=source_seed_id,
                    source_pointer=f"{source_pointer}:L{line}:cite:{key}",
                    normalized_type="entity",
                    properties={"bibkey": key, "occurrence_index": idx, "line": line, "ontological_subtype": "citation"},
                )
            )
    return atoms


def extract_tables(tex: str, source_pointer: str, source_seed_id: str, hash_table_leaf, canonical_hash, canonical_seed_id) -> list[AtomRecord]:
    atoms: list[AtomRecord] = []
    for ti, block in enumerate(re.finditer(r"\\begin\{table\}.*?\\end\{table\}", tex, re.S)):
        body = block.group(0)
        label_m = re.search(r"\\label\{([^}]+)\}", body)
        caption_m = re.search(r"\\caption\{([^}]+)\}", body)
        label = label_m.group(1) if label_m else f"tab_{ti}"
        caption = caption_m.group(1) if caption_m else ""
        rows: list[list[str]] = []
        for row in [ln for ln in body.splitlines() if "&" in ln and "rule" not in ln]:
            cells = [re.sub(r"\\\\\s*$", "", c).strip() for c in row.split("&")]
            rows.append(cells)
        columns = rows[0] if rows else []
        table_leaf = hash_table_leaf(rows, columns, caption)
        table_sid = canonical_seed_id(content_hash=table_leaf)
        atoms.append(
            AtomRecord(
                atom_type="table",
                seed_id=table_sid,
                merkle_leaf_hash=table_leaf,
                source_seed_id=source_seed_id,
                source_pointer=f"{source_pointer}:table:{label}",
                normalized_type="table",
                properties={"label": label, "caption": caption, "row_count": len(rows), "col_count": len(columns)},
            )
        )
        for ri, row in enumerate(rows):
            for ci, cell in enumerate(row):
                cell_leaf = canonical_hash({"table_label": label, "row": ri, "col": ci, "value": cell})
                cell_sid = canonical_seed_id(content_hash=cell_leaf)
                atoms.append(
                    AtomRecord(
                        atom_type="table_cell",
                        seed_id=cell_sid,
                        merkle_leaf_hash=cell_leaf,
                        source_seed_id=source_seed_id,
                        source_pointer=f"{source_pointer}:table:{label}:r{ri}:c{ci}",
                        normalized_type="table",
                        properties={"label": label, "row": ri, "col": ci, "value": cell, "parent_table_seed_id": table_sid},
                    )
                )
    return atoms


def extract_figures(tex: str, source_pointer: str, source_seed_id: str, hash_figure_leaf, canonical_seed_id) -> list[AtomRecord]:
    atoms: list[AtomRecord] = []
    for fi, block in enumerate(re.finditer(r"\\begin\{figure\}.*?\\end\{figure\}", tex, re.S)):
        body = block.group(0)
        label_m = re.search(r"\\label\{([^}]+)\}", body)
        caption_m = re.search(r"\\caption\{([^}]+)\}", body)
        label = label_m.group(1) if label_m else f"fig_{fi}"
        caption = caption_m.group(1) if caption_m else ""
        include_m = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body)
        image_bytes = b""
        if include_m:
            img_path = MANUSCRIPT / include_m.group(1)
            if img_path.is_file():
                image_bytes = img_path.read_bytes()
        leaf = hash_figure_leaf(image_bytes, caption)
        sid = canonical_seed_id(content_hash=leaf)
        atoms.append(
            AtomRecord(
                atom_type="figure",
                seed_id=sid,
                merkle_leaf_hash=leaf,
                source_seed_id=source_seed_id,
                source_pointer=f"{source_pointer}:figure:{label}",
                normalized_type="figure",
                properties={"label": label, "caption": caption, "image_sha256": sha256_bytes(image_bytes) if image_bytes else None},
            )
        )
    return atoms


def extract_all_atoms(source_seed_id: str, data_sha: str) -> list[AtomRecord]:
    canonical_hash, canonical_seed_id, hash_citation_leaf, hash_figure_leaf, hash_sentence_leaf, hash_table_leaf = _import_seedgraph()
    main_tex = MAIN_TEX.read_text()
    appendix_tex = APPENDIX_TEX.read_text() if APPENDIX_TEX.is_file() else ""
    bib = parse_bibliography(main_tex)

    atoms: list[AtomRecord] = []
    atoms.extend(extract_sentences(main_tex, "main.tex", source_seed_id, hash_sentence_leaf, canonical_seed_id))
    atoms.extend(extract_citations(main_tex, bib, "main.tex", source_seed_id, hash_citation_leaf, canonical_seed_id))
    atoms.extend(extract_tables(main_tex, "main.tex", source_seed_id, hash_table_leaf, canonical_hash, canonical_seed_id))
    atoms.extend(extract_figures(main_tex, "main.tex", source_seed_id, hash_figure_leaf, canonical_seed_id))
    if appendix_tex:
        atoms.extend(extract_sentences(appendix_tex, "appendix.tex", source_seed_id, hash_sentence_leaf, canonical_seed_id))
        atoms.extend(extract_citations(appendix_tex, bib, "appendix.tex", source_seed_id, hash_citation_leaf, canonical_seed_id))
        atoms.extend(extract_tables(appendix_tex, "appendix.tex", source_seed_id, hash_table_leaf, canonical_hash, canonical_seed_id))
        atoms.extend(extract_figures(appendix_tex, "appendix.tex", source_seed_id, hash_figure_leaf, canonical_seed_id))

    # Deduplicate by seed_id (keep first occurrence)
    seen: set[str] = set()
    unique: list[AtomRecord] = []
    for a in atoms:
        if a.seed_id in seen:
            continue
        seen.add(a.seed_id)
        unique.append(a)
    return unique


def _load_or_create_signing_key():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        load_pem_private_key,
    )

    key_path = SEEDGRAPH_ROOT / ".config" / "signing_key.pem"
    if key_path.is_file():
        return load_pem_private_key(key_path.read_bytes(), password=None)
    # Ephemeral lane key for traceability ledger (NOT_SIGNED at custody layer)
    key = Ed25519PrivateKey.generate()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(
        key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    )
    return key


def setup_ledger_and_writer():
    sys.path.insert(0, str(SEEDGRAPH_ROOT / "src"))
    from sqlalchemy import create_engine

    from seedgraph.graph.writer import GraphWriter
    from seedgraph.ledger.ledger import ProvenanceLedger
    from seedgraph.ledger.models import Base

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{LEDGER_PATH}")
    Base.metadata.create_all(engine)
    signing_key = _load_or_create_signing_key()
    ledger = ProvenanceLedger(engine=engine, signing_key=signing_key)

    neo4j_uri = os.environ.get("SEEDGRAPH_NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("SEEDGRAPH_NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("SEEDGRAPH_NEO4J_PASSWORD", "")
    graph_mode = "neo4j"
    try:
        from seedgraph.graph.connection import GraphConnection

        conn = GraphConnection(uri=neo4j_uri, auth=(neo4j_user, neo4j_password))
        conn._driver.verify_connectivity()
        session = conn._driver.session()
        writer = GraphWriter(session, ledger_engine=engine)
    except Exception as exc:
        from seedgraph.graph.json_fallback import JsonGraphFallbackSession

        fallback_root = OUT / "neo4j_fallback"
        session = JsonGraphFallbackSession(fallback_root, reason=str(exc), neo4j_uri=neo4j_uri)
        writer = GraphWriter(session, ledger_engine=engine)
        graph_mode = "json_fallback"

    return ledger, writer, graph_mode


def write_atoms_to_graph(atoms: list[AtomRecord], ledger, writer, transform_id: str) -> dict[str, Any]:
    sys.path.insert(0, str(SEEDGRAPH_ROOT / "src"))
    from seedgraph.normalize.models import CanonicalNode

    written = 0
    errors: list[str] = []
    for atom in atoms:
        node = CanonicalNode(
            seed_id=atom.seed_id,
            normalized_type=atom.normalized_type,
            extraction_method=f"{EXTRACTOR_VERSION}:{atom.atom_type}",
            source_seed_id=atom.source_seed_id,
            source_seed_ids=[atom.source_seed_id],
            ontological_type="evidence",
            properties={
                "atom_type": atom.atom_type,
                "merkle_leaf_hash": atom.merkle_leaf_hash,
                "source_pointer": atom.source_pointer,
                "transformation_id": transform_id,
                **atom.properties,
            },
            body_text=atom.text,
        )
        try:
            ledger.append(
                entity_id=atom.seed_id,
                activity="extract",
                agent=AGENT,
                method=node.extraction_method,
            )
            writer.write_canonical_node(node)
            written += 1
        except Exception as exc:
            errors.append(f"{atom.seed_id}: {exc}")

    return {"written": written, "total": len(atoms), "errors": errors}


def compose_seeds_of_truth(atoms: list[AtomRecord], source_seed_id: str, transform_id: str) -> list[dict]:
    sys.path.insert(0, str(SEEDGRAPH_ROOT / "src"))
    from seedgraph.seeds_of_truth.assembler import SeedOfTruthAssembler

    assembler = SeedOfTruthAssembler(source_seed_id, transformation_id=transform_id)
    sots: list[dict] = []

    sentence_atoms = [a for a in atoms if a.atom_type == "sentence"]
    table_cell_atoms = [a for a in atoms if a.atom_type == "table_cell"]

    # SOT from abstract sentence 4 (EXP underpowered claim)
    exp_sents = [a for a in sentence_atoms if a.text and "EXP-008" in a.text and "underpowered" in a.text.lower()]
    if exp_sents:
        sot = assembler.assemble(
            assertion=exp_sents[0].text or "EXP-008/009 underpowered",
            supporting_atoms=[{"seed_id": a.seed_id, "merkle_leaf_hash": a.merkle_leaf_hash} for a in exp_sents],
            claim_ceiling="PREREGISTERED_TERMINAL_EVIDENCE",
            state="VERIFIED",
        )
        if sot:
            sots.append(sot.model_dump(mode="json"))

    # SOT from custody sentence
    custody_sents = [a for a in sentence_atoms if a.text and "handoff receipt" in a.text.lower()]
    if custody_sents:
        sot = assembler.assemble(
            assertion=custody_sents[0].text or "Custody handoff required",
            supporting_atoms=[{"seed_id": a.seed_id, "merkle_leaf_hash": a.merkle_leaf_hash} for a in custody_sents[:1]],
            claim_ceiling="CUSTODY_MECHANICS",
            state="VERIFIED",
        )
        if sot:
            sots.append(sot.model_dump(mode="json"))

    # SOT from table cells (EXP-008/009 verdict row)
    exp_cells = [a for a in table_cell_atoms if a.properties.get("value") in {"EXP-008", "EXP-009", "UNDERPOWERED"}]
    if len(exp_cells) >= 2:
        sot = assembler.assemble(
            assertion="Terminal study verdicts: EXP-008 and EXP-009 UNDERPOWERED",
            supporting_atoms=[{"seed_id": a.seed_id, "merkle_leaf_hash": a.merkle_leaf_hash} for a in exp_cells],
            claim_ceiling="PREREGISTERED_TERMINAL_EVIDENCE",
            state="VERIFIED",
        )
        if sot:
            sots.append(sot.model_dump(mode="json"))

    write_json(SOT_DIR / "SEEDS_OF_TRUTH.json", {"seeds": sots, "refusals": assembler.refusals})
    write_jsonl(SOT_DIR / "SEEDS_OF_TRUTH.jsonl", sots)
    return sots


def build_phase73_maps(atoms: list[AtomRecord], sots: list[dict], transform_id: str) -> dict[str, Any]:
    sys.path.insert(0, str(SEEDGRAPH_ROOT / "src"))
    from seedgraph.extract.logic import SpoExtractor
    from seedgraph.maps.models import MapEdge, MapNode
    from seedgraph.maps.query import build_logic_map, build_sentence_map
    from seedgraph.schema.seeds import SentenceSeed

    sentence_atoms = [a for a in atoms if a.atom_type == "sentence" and a.text]
    sentence_seeds: list[SentenceSeed] = []
    for a in sentence_atoms:
        br = a.properties.get("byte_range", [0, len(a.text or "")])
        sentence_seeds.append(
            SentenceSeed(
                seed_type="sentence",
                seed_id=a.seed_id,
                source_seed_id=a.source_seed_id,
                text=a.text or "",
                extraction_method=EXTRACTOR_VERSION,
                extractor_version="1.0.0",
                page=1,
                anchor={"byte_start": br[0], "byte_end": br[1]},
                section=a.properties.get("section"),
                text_quality="PASS",
                text_class="body",
            )
        )

    spo_applied = False
    spo_errors: list[str] = []
    try:
        import spacy

        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            nlp = spacy.blank("en")
        if "parser" not in nlp.pipe_names:
            try:
                nlp.add_pipe("sentencizer")
            except Exception:
                pass
        extractor = SpoExtractor(nlp)
        sentence_seeds = extractor.extract(sentence_seeds)
        spo_applied = True
    except Exception as exc:
        spo_errors.append(str(exc))

    # Build MapNodes
    nodes: list[MapNode] = []
    for ss in sentence_seeds:
        nodes.append(
            MapNode(
                seed_id=ss.seed_id,
                normalized_type="sentence",
                ontological_type="evidence",
                title=None,
                text=ss.text,
                extraction_method=ss.extraction_method,
                source_seed_ids=[ss.source_seed_id],
                properties={"spo": ss.spo, "merkle_leaf_hash": next((a.merkle_leaf_hash for a in sentence_atoms if a.seed_id == ss.seed_id), None)},
            )
        )
    for sot in sots:
        nodes.append(
            MapNode(
                seed_id=sot["seed_of_truth_id"],
                normalized_type="seed_of_truth",
                ontological_type="evidence",
                title=sot["assertion"][:80],
                text=sot["assertion"],
                source_seed_ids=[sot["source_seed_id"]],
                properties={"claim_ceiling": sot.get("claim_ceiling"), "state": sot.get("state")},
            )
        )

    edges: list[MapEdge] = []
    for sot in sots:
        for atom_id in sot["supporting_atom_seed_ids"]:
            edges.append(
                MapEdge(
                    source_seed_id=sot["seed_of_truth_id"],
                    target_seed_id=atom_id,
                    edge_type="SUPPORTS",
                    properties={"transformation_id": transform_id},
                )
            )

    logic_map = build_logic_map(nodes, edges)
    sentence_map = build_sentence_map(nodes, edges)

    # Sentence diagram: SPO triples per sentence
    sentence_diagram: list[dict] = []
    for ss in sentence_seeds:
        if ss.spo:
            for triple in ss.spo:
                sentence_diagram.append(
                    {
                        "sentence_seed_id": ss.seed_id,
                        "subject": triple.get("subject"),
                        "predicate": triple.get("predicate"),
                        "predicate_class": triple.get("predicate_class"),
                        "object": triple.get("object"),
                        "transformation_id": transform_id,
                    }
                )

    result = {
        "spo_applied": spo_applied,
        "spo_errors": spo_errors,
        "sentence_count": len(sentence_seeds),
        "sot_count": len(sots),
        "logic_edge_count": len(logic_map.get("edges", [])),
        "sentence_diagram_count": len(sentence_diagram),
    }
    write_json(MAPS_DIR / "LOGIC_MAP.json", logic_map)
    write_json(MAPS_DIR / "SENTENCE_MAP.json", sentence_map)
    write_jsonl(MAPS_DIR / "SENTENCE_DIAGRAM.jsonl", sentence_diagram)
    write_json(MAPS_DIR / "PHASE73_RECEIPT.json", result)
    return result


def evaluate_traceability_gate(
    atoms: list[AtomRecord],
    graph_result: dict,
    sots: list[dict],
    phase73: dict,
    graph_mode: str,
) -> dict[str, Any]:
    checks = {
        "atoms_extracted": len(atoms) > 0,
        "all_atoms_have_merkle_leaf": all(a.merkle_leaf_hash for a in atoms),
        "graph_nodes_written": graph_result["written"] == graph_result["total"],
        "graph_errors_empty": len(graph_result["errors"]) == 0,
        "sots_composed": len(sots) > 0,
        "all_sots_have_supporting_atoms": all(s.get("supporting_atom_seed_ids") for s in sots),
        "phase73_logic_map": phase73.get("logic_edge_count", 0) > 0,
        "phase73_sentence_diagram": (MAPS_DIR / "SENTENCE_DIAGRAM.jsonl").is_file(),
        "ledger_exists": LEDGER_PATH.is_file(),
    }

    # Public upload requires live Neo4j, not JSON fallback
    draft_to_publication = all(checks.values()) and graph_mode == "neo4j"
    openreview_anticube = draft_to_publication

    return {
        "checks": checks,
        "graph_mode": graph_mode,
        "DRAFT_TO_PUBLICATION_TRACEABILITY": "GREEN" if draft_to_publication else "BLOCKED",
        "OPENREVIEW_ANTICUBE_PUBLIC_UPLOAD": "GREEN" if openreview_anticube else "BLOCKED",
        "claim_ceiling": "CUSTODY_MECHANICS" if draft_to_publication else "NOT_COMPUTED",
        "earliest_divergence": next((k for k, v in checks.items() if not v), None),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="NewInML SeedGraph full traceability pipeline")
    parser.add_argument("--skip-graph", action="store_true", help="Skip GraphWriter (atoms only)")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    script_sha = sha256_file(TRANSFORMATION_SCRIPT)
    data_sha = sha256_file(PDF_PATH) if PDF_PATH.is_file() else sha256_bytes((MAIN_TEX.read_text() + (APPENDIX_TEX.read_text() if APPENDIX_TEX.is_file() else "")).encode())
    source_seed_id = f"doc:{data_sha}"
    transform_id = transformation_id(script_sha, data_sha, "full_traceability")

    git_sha = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()

    # S1: Extract atoms with merkle leaf hashing
    atoms = extract_all_atoms(source_seed_id, data_sha)
    atom_rows = [
        {
            "atom_type": a.atom_type,
            "seed_id": a.seed_id,
            "merkle_leaf_hash": a.merkle_leaf_hash,
            "source_seed_id": a.source_seed_id,
            "source_pointer": a.source_pointer,
            "normalized_type": a.normalized_type,
            "properties": a.properties,
            "text": a.text,
            "transformation_id": transform_id,
        }
        for a in atoms
    ]
    write_jsonl(ATOMS_DIR / "ATOMS.jsonl", atom_rows)
    write_json(
        ATOMS_DIR / "ATOM_EXTRACTION_RECEIPT.json",
        {
            "schema": "hydradg.seedgraph_traceability.atom_extraction.v1",
            "recorded_at": utc(),
            "source_seed_id": source_seed_id,
            "data_sha256": data_sha,
            "script_sha256": script_sha,
            "transformation_id": transform_id,
            "git_commit": git_sha,
            "counts": {
                "total": len(atoms),
                "sentence": sum(1 for a in atoms if a.atom_type == "sentence"),
                "citation": sum(1 for a in atoms if a.atom_type == "citation"),
                "table": sum(1 for a in atoms if a.atom_type == "table"),
                "table_cell": sum(1 for a in atoms if a.atom_type == "table_cell"),
                "figure": sum(1 for a in atoms if a.atom_type == "figure"),
            },
            "merkle_module": "seedgraph.merkle.atoms",
            "hash_profile": "seedgraph.merkle.atoms.D10",
        },
    )

    # S2: Ledger + GraphWriter
    graph_result = {"written": 0, "total": len(atoms), "errors": ["skipped"]}
    graph_mode = "skipped"
    if not args.skip_graph:
        ledger, writer, graph_mode = setup_ledger_and_writer()
        # Source document node
        sys.path.insert(0, str(SEEDGRAPH_ROOT / "src"))
        from seedgraph.normalize.models import CanonicalNode

        doc_node = CanonicalNode(
            seed_id=source_seed_id,
            normalized_type="document",
            extraction_method=EXTRACTOR_VERSION,
            source_seed_id=source_seed_id,
            ontological_type="evidence",
            properties={"data_sha256": data_sha, "pdf_path": str(PDF_PATH.relative_to(ROOT)) if PDF_PATH.is_file() else None},
        )
        ledger.append(entity_id=source_seed_id, activity="ingest", agent=AGENT, method="source_document")
        writer.write_canonical_node(doc_node)
        graph_result = write_atoms_to_graph(atoms, ledger, writer, transform_id)

    # S3: Seeds of truth
    sots = compose_seeds_of_truth(atoms, source_seed_id, transform_id)

    # S4: Phase 73 maps
    phase73 = build_phase73_maps(atoms, sots, transform_id)

    # S5/S6: Gate
    gate = evaluate_traceability_gate(atoms, graph_result, sots, phase73, graph_mode)

    closeout = {
        "schema": "hydradg.seedgraph_traceability.closeout.v1",
        "recorded_at": utc(),
        "git_commit": git_sha,
        "source_seed_id": source_seed_id,
        "data_sha256": data_sha,
        "script_sha256": script_sha,
        "transformation_id": transform_id,
        "seedgraph_root": str(SEEDGRAPH_ROOT),
        "atom_extraction": str(ATOMS_DIR / "ATOM_EXTRACTION_RECEIPT.json"),
        "graph_result": graph_result,
        "graph_mode": graph_mode,
        "sot_count": len(sots),
        "phase73": phase73,
        "traceability_gate": gate,
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
    }
    write_json(OUT / "SEEDGRAPH_TRACEABILITY_CLOSEOUT.json", closeout)
    write_json(OUT / "TRANSFORMATION_BINDING.json", {
        "transformation_id": transform_id,
        "script_path": str(TRANSFORMATION_SCRIPT.relative_to(ROOT)),
        "script_sha256": script_sha,
        "data_sha256": data_sha,
        "code_roots": {
            "hydradg_script": script_sha,
            "seedgraph_merkle_atoms": sha256_file(SEEDGRAPH_ROOT / "src/seedgraph/merkle/atoms.py"),
            "seedgraph_sot_assembler": sha256_file(SEEDGRAPH_ROOT / "src/seedgraph/seeds_of_truth/assembler.py"),
            "gsigmad_hash_contract": sha256_file(GSD_ROOT / "src/gsigmad/longitudinal/hash_contract.py") if (GSD_ROOT / "src/gsigmad/longitudinal/hash_contract.py").is_file() else None,
        },
        "git_commit": git_sha,
    })

    print(json.dumps({
        "state": gate["DRAFT_TO_PUBLICATION_TRACEABILITY"],
        "openreview_anticube": gate["OPENREVIEW_ANTICUBE_PUBLIC_UPLOAD"],
        "atoms": len(atoms),
        "sots": len(sots),
        "graph_written": graph_result["written"],
        "graph_mode": graph_mode,
        "out": str(OUT),
    }, indent=2))

    return 0 if gate["DRAFT_TO_PUBLICATION_TRACEABILITY"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
