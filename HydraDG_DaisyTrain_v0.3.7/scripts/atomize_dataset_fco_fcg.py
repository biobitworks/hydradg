#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Iterator

SCHEMA = "hydradg.full_dataset_fco_fcg_atomization.v1"
ADAPTER_VERSION = "hydradg-full-atomizer-0.1.0"
CLAIM_CEILING = "FULL_DATASET_FCO_FCG_CUSTODY_PROJECTION_ONLY_NOT_BENCHMARK_PERFORMANCE"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def make_fco(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = {"type": kind, "payload": payload}
    digest = sha256_bytes(canonical_json(body))
    return {"id": f"fco:{digest}", "object_sha256": digest, "type": kind, "payload": payload}


def merkle_root_hex(leaves: Iterable[str]) -> str:
    level = [bytes.fromhex(x) for x in leaves]
    if not level:
        return sha256_bytes(b"hydradg.empty_merkle.v1")
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(hashlib.sha256(b"hydradg.merkle.node.v1\0" + level[i] + level[i + 1]).digest())
        level = nxt
    return level[0].hex()


def scalar_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        if not math.isfinite(value):
            return "float_nonfinite"
        return "float"
    if isinstance(value, str):
        return "string"
    return type(value).__name__


def flatten_scalars(value: Any, path: str = "$") -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key in sorted(value, key=lambda x: str(x)):
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            yield from flatten_scalars(value[key], f"{path}/{escaped}")
        return
    if isinstance(value, (list, tuple)):
        for idx, item in enumerate(value):
            yield from flatten_scalars(item, f"{path}/{idx}")
        return
    yield path, value


def field_leaf_hash(path: str, value: Any) -> str:
    st = scalar_type(value)
    if st == "float_nonfinite":
        encoded = repr(value).encode("utf-8")
    else:
        encoded = canonical_json(value)
    preimage = b"hydradg.field_leaf.v1\0" + path.encode("utf-8") + b"\0" + st.encode("ascii") + b"\0" + encoded
    return sha256_bytes(preimage)


def record_fco(*, dataset_id: str, source_file_fco: str, source_file_sha256: str, logical_pointer: str, record: Any, raw_record_sha256: str | None, record_kind: str) -> tuple[dict[str, Any], int]:
    leaves = [field_leaf_hash(path, value) for path, value in flatten_scalars(record)]
    field_root = merkle_root_hex(leaves)
    canonical_record_sha = sha256_bytes(canonical_json(record))
    payload = {
        "dataset_id": dataset_id,
        "source_file_fco": source_file_fco,
        "source_file_sha256": source_file_sha256,
        "logical_pointer": logical_pointer,
        "record_kind": record_kind,
        "canonical_record_sha256": canonical_record_sha,
        "raw_record_sha256": raw_record_sha256,
        "field_leaf_count": len(leaves),
        "field_leaf_merkle_root": field_root,
        "adapter_version": ADAPTER_VERSION,
        "claim_ceiling": CLAIM_CEILING,
    }
    return make_fco("DatasetRecordFCO", payload), len(leaves)


def parse_sha_manifest(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise ValueError(f"invalid SHA256SUMS row: {line[:200]!r}")
        rows.append((parts[0], parts[1]))
    return rows


def first_non_ws(path: Path) -> str:
    with path.open("rb") as f:
        while True:
            b = f.read(1)
            if not b:
                return ""
            c = b.decode("utf-8", errors="ignore")
            if c and not c.isspace():
                return c


def iter_json_records(path: Path) -> Iterator[tuple[str, Any, str | None, str]]:
    first = first_non_ws(path)
    try:
        import ijson  # type: ignore
    except Exception as exc:
        raise RuntimeError("JSON atomization requires ijson. Run with: uv run --with ijson ...") from exc

    if first == "[":
        with path.open("rb") as f:
            for idx, item in enumerate(ijson.items(f, "item")):
                yield f"$/[{idx}]", item, None, "json_array_item"
        return

    if first == "{":
        leaves: list[dict[str, Any]] = []
        occurrence: dict[str, int] = {}
        with path.open("rb") as f:
            for prefix, event, value in ijson.parse(f):
                if event not in {"string", "number", "boolean", "null"}:
                    continue
                key = prefix or "$"
                n = occurrence.get(key, 0)
                occurrence[key] = n + 1
                leaves.append({"path": f"$/{key}#{n}", "type": event, "value": value})
        yield "$", {"__streamed_scalar_events__": leaves}, None, "json_object_stream"
        return

    raise RuntimeError(f"unsupported JSON top-level token {first!r} in {path}")


def iter_jsonl_records(path: Path) -> Iterator[tuple[str, Any, str | None, str]]:
    with path.open("rb") as f:
        for idx, raw in enumerate(f):
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"invalid JSONL record at line {idx + 1} in {path}: {exc}") from exc
            yield f"$/line/{idx + 1}", value, sha256_bytes(raw), "jsonl_line"


def iter_csv_records(path: Path, delimiter: str) -> Iterator[tuple[str, Any, str | None, str]]:
    with path.open("r", newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise RuntimeError(f"CSV/TSV header could not be resolved: {path}")
        for idx, row in enumerate(reader, start=1):
            yield f"$/row/{idx}", dict(row), None, "tabular_row"


def iter_parquet_records(path: Path) -> Iterator[tuple[str, Any, str | None, str]]:
    try:
        import pyarrow.parquet as pq  # type: ignore
    except Exception as exc:
        raise RuntimeError("Parquet atomization requires pyarrow. Run with: uv run --with pyarrow ...") from exc
    pf = pq.ParquetFile(path)
    ordinal = 0
    for batch in pf.iter_batches(batch_size=2048):
        for row in batch.to_pylist():
            yield f"$/row/{ordinal}", row, None, "parquet_row"
            ordinal += 1


def semantic_iterator(path: Path) -> Iterator[tuple[str, Any, str | None, str]] | None:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return iter_jsonl_records(path)
    if suffix == ".json":
        return iter_json_records(path)
    if suffix == ".csv":
        return iter_csv_records(path, ",")
    if suffix == ".tsv":
        return iter_csv_records(path, "\t")
    if suffix == ".parquet":
        return iter_parquet_records(path)
    return None


def write_jsonl(handle, obj: dict[str, Any]) -> None:
    handle.write(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


def atomize_dataset(dataset: dict[str, Any], out_root: Path) -> dict[str, Any]:
    repo_id = dataset["repo_id"]
    dataset_id = repo_id.replace("/", "__")
    source_root = Path(dataset["local_path"]).expanduser().resolve()
    manifest = Path(dataset["sha256_manifest"]).expanduser().resolve()
    expected_manifest_sha = dataset["sha256_manifest_sha256"]
    actual_manifest_sha = sha256_file(manifest)
    if actual_manifest_sha != expected_manifest_sha:
        raise RuntimeError(f"manifest SHA mismatch for {repo_id}: {actual_manifest_sha} != {expected_manifest_sha}")

    droot = out_root / dataset_id
    droot.mkdir(parents=True, exist_ok=True)
    nodes_path = droot / "fco_nodes.jsonl"
    edges_path = droot / "fcg_edges.jsonl"

    base_hashes: list[str] = []
    file_fcos: list[str] = []
    record_fcos: list[str] = []
    source_files_total = 0
    source_files_byte_bound = 0
    structured_files = 0
    structured_records = 0
    field_leaves_total = 0
    blob_files = 0
    edge_count = 0

    with nodes_path.open("w", encoding="utf-8") as nodes, edges_path.open("w", encoding="utf-8") as edges:
        previous_record_by_file: dict[str, str] = {}
        for expected_sha, rel in parse_sha_manifest(manifest):
            source_files_total += 1
            path = source_root / rel
            if not path.is_file():
                raise RuntimeError(f"manifest member missing: {path}")
            actual_sha = sha256_file(path)
            if actual_sha != expected_sha:
                raise RuntimeError(f"file SHA mismatch {path}: {actual_sha} != {expected_sha}")
            source_files_byte_bound += 1
            file_fco = make_fco("SourceFileFCO", {
                "dataset_id": dataset_id,
                "relative_path": rel,
                "source_sha256": actual_sha,
                "bytes": path.stat().st_size,
                "adapter_version": ADAPTER_VERSION,
                "claim_ceiling": CLAIM_CEILING,
            })
            write_jsonl(nodes, file_fco)
            base_hashes.append(file_fco["object_sha256"])
            file_fcos.append(file_fco["id"])

            it = semantic_iterator(path)
            if it is None:
                blob_files += 1
                blob = make_fco("BlobFCO", {
                    "dataset_id": dataset_id,
                    "source_file_fco": file_fco["id"],
                    "source_sha256": actual_sha,
                    "relative_path": rel,
                    "bytes": path.stat().st_size,
                    "semantic_state": "OPAQUE_OR_NON_BENCHMARK_FILE_BYTE_BOUND",
                    "adapter_version": ADAPTER_VERSION,
                    "claim_ceiling": CLAIM_CEILING,
                })
                write_jsonl(nodes, blob)
                base_hashes.append(blob["object_sha256"])
                write_jsonl(edges, {"src": blob["id"], "rel": "DERIVED_FROM", "dst": file_fco["id"]})
                edge_count += 1
                continue

            structured_files += 1
            for pointer, record, raw_record_sha, kind in it:
                rec, leaf_count = record_fco(
                    dataset_id=dataset_id,
                    source_file_fco=file_fco["id"],
                    source_file_sha256=actual_sha,
                    logical_pointer=pointer,
                    record=record,
                    raw_record_sha256=raw_record_sha,
                    record_kind=kind,
                )
                write_jsonl(nodes, rec)
                base_hashes.append(rec["object_sha256"])
                record_fcos.append(rec["id"])
                structured_records += 1
                field_leaves_total += leaf_count
                write_jsonl(edges, {"src": rec["id"], "rel": "DERIVED_FROM", "dst": file_fco["id"]})
                edge_count += 1
                previous = previous_record_by_file.get(file_fco["id"])
                if previous:
                    write_jsonl(edges, {"src": previous, "rel": "NEXT", "dst": rec["id"]})
                    edge_count += 1
                previous_record_by_file[file_fco["id"]] = rec["id"]

        atom_set_root = merkle_root_hex(sorted(base_hashes))
        dataset_fco = make_fco("UpstreamDatasetFCO", {
            "dataset_id": dataset_id,
            "repo_id": repo_id,
            "revision": dataset["revision"],
            "license_declared_upstream": dataset["license_declared_upstream"],
            "source_manifest_sha256": expected_manifest_sha,
            "atom_set_merkle_root": atom_set_root,
            "source_files_total": source_files_total,
            "structured_records_total": structured_records,
            "adapter_version": ADAPTER_VERSION,
            "claim_ceiling": CLAIM_CEILING,
        })
        write_jsonl(nodes, dataset_fco)
        for fid in file_fcos:
            write_jsonl(edges, {"src": fid, "rel": "MEMBER_OF", "dst": dataset_fco["id"]})
            edge_count += 1

        bundle = make_fco("AtomBundleFCO", {
            "dataset_id": dataset_id,
            "dataset_fco": dataset_fco["id"],
            "atom_set_merkle_root": atom_set_root,
            "base_object_count": len(base_hashes),
            "adapter_version": ADAPTER_VERSION,
            "claim_ceiling": CLAIM_CEILING,
        })
        write_jsonl(nodes, bundle)
        write_jsonl(edges, {"src": bundle["id"], "rel": "COMMITS", "dst": dataset_fco["id"]})
        edge_count += 1

    nodes_sha = sha256_file(nodes_path)
    edges_sha = sha256_file(edges_path)
    science = {
        "dataset_id": dataset_id,
        "repo_id": repo_id,
        "revision": dataset["revision"],
        "source_manifest_sha256": expected_manifest_sha,
        "source_files_total": source_files_total,
        "source_files_byte_bound": source_files_byte_bound,
        "structured_files": structured_files,
        "structured_records_atomized": structured_records,
        "field_leaves_total": field_leaves_total,
        "blob_files": blob_files,
        "base_object_count": len(base_hashes),
        "record_fco_count": len(record_fcos),
        "fcg_edge_count": edge_count,
        "atom_set_merkle_root": atom_set_root,
        "nodes_jsonl_sha256": nodes_sha,
        "edges_jsonl_sha256": edges_sha,
        "adapter_version": ADAPTER_VERSION,
        "claim_ceiling": CLAIM_CEILING,
    }
    result = {
        "schema": SCHEMA,
        **science,
        "status": "PASS" if source_files_total == source_files_byte_bound else "FAIL",
        "byte_coverage": source_files_byte_bound / source_files_total if source_files_total else 0.0,
        "orphan_count": 0,
        "signature_state": "NOT_SIGNED",
        "hydradb_merkle_state": "NOT_MERKLE_COMMITTED",
        "cfmo_state": "NOT_IMPLEMENTED_BY_THIS_RUN",
        "deterministic_payload_sha256": sha256_bytes(canonical_json(science)),
        "nodes_jsonl": str(nodes_path),
        "edges_jsonl": str(edges_path),
    }
    summary_path = droot / "ATOMIZATION_RECEIPT.json"
    summary_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    result["receipt_path"] = str(summary_path)
    result["receipt_file_sha256"] = sha256_file(summary_path)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-receipt", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    receipt = args.dataset_receipt.expanduser().resolve()
    out = args.out_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    source = json.loads(receipt.read_text())
    datasets = source.get("datasets", [])
    if not datasets:
        raise SystemExit("dataset receipt contains no datasets")

    results = [atomize_dataset(item, out) for item in datasets]
    overall_science = {
        "dataset_receipt_file_sha256": sha256_file(receipt),
        "datasets": [
            {k: r[k] for k in (
                "dataset_id", "revision", "source_manifest_sha256", "source_files_total",
                "source_files_byte_bound", "structured_files", "structured_records_atomized",
                "field_leaves_total", "blob_files", "base_object_count", "record_fco_count",
                "fcg_edge_count", "atom_set_merkle_root", "deterministic_payload_sha256"
            )}
            for r in results
        ],
        "adapter_version": ADAPTER_VERSION,
        "claim_ceiling": CLAIM_CEILING,
    }
    overall = {
        "schema": "hydradg.full_dataset_fco_fcg_atomization_batch.v1",
        **overall_science,
        "status": "PASS" if all(r["status"] == "PASS" and r["byte_coverage"] == 1.0 for r in results) else "FAIL",
        "deterministic_payload_sha256": sha256_bytes(canonical_json(overall_science)),
        "signature_state": "NOT_SIGNED",
        "hydradb_merkle_state": "NOT_MERKLE_COMMITTED",
        "cfmo_state": "NOT_IMPLEMENTED_BY_THIS_RUN",
    }
    batch_path = out / "FULL_ATOMIZATION_BATCH_RECEIPT.json"
    batch_path.write_text(json.dumps(overall, indent=2, sort_keys=True) + "\n")
    print(json.dumps(overall, indent=2, sort_keys=True))
    print(f"FULL_ATOMIZATION_COMPLETE={'YES' if overall['status'] == 'PASS' else 'NO'}")
    print(f"RECEIPT={batch_path}")
    print(f"RECEIPT_FILE_SHA256={sha256_file(batch_path)}")
    if overall["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
