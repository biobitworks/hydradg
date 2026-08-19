#!/usr/bin/env python3
"""Compute reproducible SHA-256 identities for HydraDG release artifacts.

Hashing establishes byte identity only. This script does not sign, verify,
Merkle-commit, or scientifically validate an artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_PATHS = [
    "docs/PROJECT_FCG_UPDATE_20260819.md",
    "docs/WEBSITE_MVP_AND_FALLBACK_20260819.md",
    "docs/PROJECT_FCG_CHANGELOG_20260819.json",
    "docs/HASHING_PROOF_20260819.md",
    "apps/hydradg-web/public/backup/hydradg.html",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=DEFAULT_PATHS)
    parser.add_argument("--out", default="docs/RELEASE_ARTIFACT_SHA256_20260819.json")
    args = parser.parse_args()

    records = []
    for raw in args.paths:
        path = Path(raw)
        if not path.is_file():
            raise SystemExit(f"missing artifact: {path}")
        records.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)})

    obj = {
        "schema": "hydradg.release_artifact_hashes.v1",
        "algorithm": "SHA-256",
        "artifacts": records,
        "claim_ceiling": "BYTE_IDENTITY_ONLY",
        "signature_state": "NOT_SIGNED",
        "merkle_state": "NOT_PROJECT_COMMITTED",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(obj, indent=2, sort_keys=True))
    print(f"HASH_MANIFEST={out}")
    print(f"HASH_MANIFEST_SHA256={sha256_file(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
