#!/usr/bin/env python3
"""Build a deterministic hashed byte manifest for acquired HydraDG corpus files.

SPDX-License-Identifier: Apache-2.0

The output can populate `download_files` for calculate_information_savings.py.
This script measures files that actually exist under explicitly supplied roots; it does
not estimate missing downloads or infer dataset sizes from metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def rel_label(path: Path, root: Path, root_label: str) -> str:
    relative = path.relative_to(root).as_posix()
    return f"{root_label}/{relative}" if relative else root_label


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="+",
        type=Path,
        help="One or more downloaded corpus directories/files to hash exactly.",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--exclude-name",
        action="append",
        default=[".DS_Store"],
        help="Exact basename to exclude; may be repeated.",
    )
    args = parser.parse_args()

    roots = [root.expanduser().resolve() for root in args.roots]
    for root in roots:
        if not root.exists():
            print(f"BYTE_MANIFEST=FAIL missing root: {root}", file=sys.stderr)
            return 2

    records: list[dict[str, Any]] = []
    excluded = set(args.exclude_name)

    for index, root in enumerate(roots):
        root_label = f"root_{index:03d}:{root.name}"
        candidates = [root] if root.is_file() else sorted(
            (p for p in root.rglob("*") if p.is_file()),
            key=lambda p: p.relative_to(root).as_posix(),
        )
        for path in candidates:
            if path.name in excluded:
                continue
            stat = path.stat()
            records.append(
                {
                    "path": rel_label(path, root.parent if root.is_file() else root, root_label),
                    "size_bytes": int(stat.st_size),
                    "sha256": sha256_file(path),
                }
            )

    records.sort(key=lambda item: (item["path"], item["sha256"], item["size_bytes"]))
    total_bytes = sum(int(item["size_bytes"]) for item in records)
    hashes: dict[str, int] = {}
    for item in records:
        previous = hashes.get(item["sha256"])
        if previous is not None and previous != item["size_bytes"]:
            print(
                f"BYTE_MANIFEST=FAIL same SHA-256 with conflicting sizes: {item['sha256']}",
                file=sys.stderr,
            )
            return 3
        hashes[item["sha256"]] = int(item["size_bytes"])

    unique_bytes = sum(hashes.values())
    payload = {
        "schema": "hydradg.download_byte_manifest.v1",
        "measurement_state": "MEASURED_FROM_LOCAL_FILES",
        "root_count": len(roots),
        "file_count": len(records),
        "unique_content_hash_count": len(hashes),
        "raw_download_bytes": total_bytes,
        "unique_content_bytes": unique_bytes,
        "duplicate_download_bytes": total_bytes - unique_bytes,
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
    print(f"raw_download_bytes={total_bytes}")
    print(f"unique_content_bytes={unique_bytes}")
    print(f"duplicate_download_bytes={total_bytes - unique_bytes}")
    print(f"manifest_sha256={manifest_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
