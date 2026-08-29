#!/usr/bin/env python3
"""Emit SHA-256 manifest receipt for Pro←Studio rebuild bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SKIP_NAMES = {
    "hydradb-auth-token",
    ".env",
    ".pem",
    ".key",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(repo: Path) -> str | None:
    if not repo.is_dir():
        return None
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", required=True)
    p.add_argument("--studio", default="magicSTUDIObox.local")
    args = p.parse_args()
    bundle = Path(args.bundle).resolve()
    files: list[dict] = []
    for path in sorted(bundle.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_NAMES for part in path.parts):
            continue
        if path.suffix in {".pem", ".key", ".secret"}:
            continue
        rel = path.relative_to(bundle).as_posix()
        files.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})

    receipt = {
        "schema": "hydradg.pro_studio_sync_receipt.v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pro_host": socket.gethostname(),
        "studio_host": args.studio,
        "bundle_path": str(bundle),
        "file_count": len(files),
        "total_bytes": sum(f["bytes"] for f in files),
        "git_heads": {
            "hydradg": git_head(bundle.parent),
            "overwatch": git_head(bundle.parent.parent / "overwatch"),
            "seedgraph": git_head(bundle.parent.parent / "seedgraph"),
            "watchtower": git_head(bundle.parent.parent / "watchtower"),
            "gettingsciencedone": git_head(bundle.parent.parent / "gettingsciencedone"),
        },
        "files": files,
        "excluded_by_policy": [
            "hydradb-auth-token",
            "FLOOR10_AGENT_TOKEN",
            "live OrbStack DB volumes (query Studio instead)",
        ],
    }
    out = bundle / "SYNC_RECEIPT.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    sums = bundle / "SHA256SUMS"
    sums.write_text(
        "\n".join(f"{f['sha256']}  {f['path']}" for f in files) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"receipt": str(out), "file_count": len(files), "total_bytes": receipt["total_bytes"]}))


if __name__ == "__main__":
    main()
