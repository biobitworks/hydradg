#!/usr/bin/env python3
"""Measure exact local downloaded-file bytes and SHA-256 identities.

SPDX-License-Identifier: Apache-2.0

The manifest can be copied into `download_files` for
`scripts/calculate_information_savings.py`. Missing files are never estimated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    roots = [p.expanduser().resolve() for p in args.roots]
    for root in roots:
        if not root.exists():
            print(f"BYTE_MANIFEST=FAIL missing root: {root}", file=sys.stderr)
            return 2

    records: list[dict[str, Any]] = []
    for index, root in enumerate(roots):
        label = f"root_{index:03d}:{root.name}"
        files = [root] if root.is_file() else sorted(
            (p for p in root.rglob("*") if p.is_file() and p.name != ".DS_Store"),
            key=lambda p: p.relative_to(root).as_posix(),
        )
        for path in files:
            relative = path.name if root.is_file() else path.relative_to(root).as_posix()
            records.append({
                "path": f"{label}/{relative}",
                "size_bytes": int(path.stat().st_size),
                "sha256": file_sha256(path),
            })

    records.sort(key=lambda x: (x["path"], x["sha256"], x["size_bytes"]))
    sizes_by_hash: dict[str, int] = {}
    raw_bytes = 0
    for record in records:
        raw_bytes += record["size_bytes"]
        prior = sizes_by_hash.get(record["sha256"])
        if prior is not None and prior != record["size_bytes"]:
            print(f"BYTE_MANIFEST=FAIL same SHA-256 with conflicting sizes: {record['sha256']}", file=sys.stderr)
            return 3
        sizes_by_hash[record["sha256"]] = record["size_bytes"]

    unique_bytes = sum(sizes_by_hash.values())
    payload = {
        "schema": "hydradg.download_byte_manifest.v1",
        "measurement_state": "MEASURED_FROM_LOCAL_FILES",
        "root_count": len(roots),
        "file_count": len(records),
        "unique_content_hash_count": len(sizes_by_hash),
        "raw_download_bytes": raw_bytes,
        "unique_content_bytes": unique_bytes,
        "duplicate_download_bytes": raw_bytes - unique_bytes,
        "files": records,
        "signature_state": "NOT_SIGNED",
        "license": "CC-BY-NC-ND-4.0",
        "claim_ceiling": "LOCAL_FILE_BYTE_IDENTITY_AND_DUPLICATION_ACCOUNTING_ONLY",
    }
    manifest_sha256 = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    output = {**payload, "manifest_sha256": manifest_sha256}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("BYTE_MANIFEST=PASS")
    print(f"file_count={len(records)}")
    print(f"raw_download_bytes={raw_bytes}")
    print(f"unique_content_bytes={unique_bytes}")
    print(f"duplicate_download_bytes={raw_bytes - unique_bytes}")
    print(f"manifest_sha256={manifest_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
