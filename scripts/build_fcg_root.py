#!/usr/bin/env python3
"""Build and verify the resumed HydraDG FCG custody root.

Root convention: HYDRADG-FCG-RFC6962-v1
- FCO nodes are independently recomputed from canonical {type,payload} JSON.
- FCG edges are independently recomputed from canonical {src,rel,dst,payload} JSON.
- Live custody may be split across append-only `nodes*.jsonl` and `edges*.jsonl` fragments.
- Objects are sorted globally by canonical object id before Merkle construction.
- Leaf hash = SHA256(0x00 || canonical leaf bytes).
- Parent hash = SHA256(0x01 || left || right), RFC-6962 recursive split.
- If PUBLIC_KEY.ed25519.pub exists, its exact bytes are committed as a tagged leaf.
- FCG_ROOT.sig is deliberately excluded from the root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "hydradg.fcg_manifest.v1"
ROOT_CONVENTION = "HYDRADG-FCG-RFC6962-v1"
EXPECTED_AUTHOR_KEY_DER_SHA256 = "f496a067808026d45fbbad785bf83c6acd66429c2d257d246cc103c6d7ff460d"


def normalize(value: Any) -> Any:
    if isinstance(value, dict): return {key: normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list): return [normalize(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(normalize(value), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip(): continue
        try: row = json.loads(raw)
        except json.JSONDecodeError as exc: raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict): raise SystemExit(f"{path}:{lineno}: expected JSON object")
        rows.append(row)
    return rows


def verify_node(row: dict[str, Any]) -> None:
    expected = sha256_hex(canonical_bytes({"type": row.get("type"), "payload": row.get("payload", {})}))
    if row.get("object_sha256") != expected or row.get("id") != f"fco:{expected}":
        raise SystemExit(f"node hash mismatch: id={row.get('id')} expected=fco:{expected}")


def verify_edge(row: dict[str, Any]) -> None:
    body = {"src": row.get("src"), "rel": row.get("rel"), "dst": row.get("dst"), "payload": row.get("payload", {})}
    expected = sha256_hex(canonical_bytes(body))
    if row.get("object_sha256") != expected or row.get("id") != f"fcg:{expected}":
        raise SystemExit(f"edge hash mismatch: id={row.get('id')} expected=fcg:{expected}")


def leaf_hash(payload: bytes) -> bytes: return hashlib.sha256(b"\x00" + payload).digest()
def node_hash(left: bytes, right: bytes) -> bytes: return hashlib.sha256(b"\x01" + left + right).digest()


def merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves: return hashlib.sha256(b"").digest()
    if len(leaves) == 1: return leaf_hash(leaves[0])
    split = 1 << ((len(leaves) - 1).bit_length() - 1)
    return node_hash(merkle_root(leaves[:split]), merkle_root(leaves[split:]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--custody-dir", default="custody/live")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    custody_dir = Path(args.custody_dir)
    node_paths = sorted(custody_dir.glob("nodes*.jsonl"))
    edge_paths = sorted(custody_dir.glob("edges*.jsonl"))
    if not node_paths or not edge_paths: raise SystemExit("missing nodes*.jsonl or edges*.jsonl custody fragments")
    output_path = Path(args.output) if args.output else custody_dir / "manifest.json"
    public_key_path = custody_dir / "PUBLIC_KEY.ed25519.pub"
    signature_path = custody_dir / "FCG_ROOT.sig"

    nodes = [row for path in node_paths for row in load_jsonl(path)]
    edges = [row for path in edge_paths for row in load_jsonl(path)]
    for node in nodes: verify_node(node)
    for edge in edges: verify_edge(edge)

    node_ids = [str(node["id"]) for node in nodes]
    if len(node_ids) != len(set(node_ids)): raise SystemExit("duplicate FCO id across live node fragments")
    edge_ids = [str(edge["id"]) for edge in edges]
    if len(edge_ids) != len(set(edge_ids)): raise SystemExit("duplicate FCG id across live edge fragments")
    node_id_set = set(node_ids)
    missing = sorted({str(endpoint) for edge in edges for endpoint in (edge.get("src"), edge.get("dst")) if str(endpoint) not in node_id_set})
    if missing: raise SystemExit(f"FCG edges reference unknown FCO endpoints: {missing}")

    records: list[tuple[str, bytes, dict[str, Any]]] = []
    for node in nodes: records.append((str(node["id"]), canonical_bytes(node), {"kind": "fco_node", "id": node["id"]}))
    for edge in edges: records.append((str(edge["id"]), canonical_bytes(edge), {"kind": "fcg_edge", "id": edge["id"]}))

    public_key_leaf = None
    if public_key_path.exists():
        key_bytes = public_key_path.read_bytes()
        public_key_leaf = {"kind": "public_key_leaf", "path": str(public_key_path), "file_sha256": sha256_hex(key_bytes), "bytes": len(key_bytes)}
        records.append(("zz:PUBLIC_KEY.ed25519.pub", b"PUBLIC_KEY.ed25519.pub\x00" + key_bytes, public_key_leaf))

    records.sort(key=lambda row: row[0])
    root = merkle_root([payload for _, payload, _ in records]).hex()
    signature_state = "PENDING_PUBLIC_KEY_LEAF_AND_AUTHOR_KEY"
    if public_key_path.exists() and not signature_path.exists(): signature_state = "PUBLIC_KEY_LEAF_PRESENT_SIGNATURE_PENDING"
    elif public_key_path.exists() and signature_path.exists(): signature_state = "SIGNATURE_FILE_PRESENT_NOT_VERIFIED_BY_BUILDER"

    def file_record(path: Path) -> dict[str, Any]:
        return {"path": str(path), "sha256": sha256_hex(path.read_bytes()), "bytes": path.stat().st_size}

    manifest = {
        "schema": SCHEMA,
        "root_convention": ROOT_CONVENTION,
        "fcg_root": root,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "leaf_count": len(records),
        "node_files": [file_record(path) for path in node_paths],
        "edge_files": [file_record(path) for path in edge_paths],
        "public_key_leaf": public_key_leaf,
        "expected_author_public_key_der_sha256": EXPECTED_AUTHOR_KEY_DER_SHA256,
        "author_signature_state": signature_state,
        "signature_is_root_leaf": False,
        "custody_gap_state": "DECLARED_GAP_NOT_RETROACTIVELY_BACKFILLED",
        "claim_ceiling": "CONTENT_INTEGRITY_ROOT_NOT_CORRECTNESS_OR_AUTHOR_IDENTITY_UNLESS_SIGNATURE_AND_OUT_OF_BAND_KEY_ANCHOR_VERIFY",
        "objects": [meta for _, _, meta in records],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"fcg_root": root, "manifest": str(output_path), "signature_state": signature_state, "node_count": len(nodes), "edge_count": len(edges)}))
    return 0


if __name__ == "__main__": raise SystemExit(main())
