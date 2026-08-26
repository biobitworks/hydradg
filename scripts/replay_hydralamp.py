#!/usr/bin/env python3
"""Deterministic HydraLamp event replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = REPO_ROOT / "eval" / "hydralamp_20260826" / "HYDRALAMP_EVENTS.jsonl"
DEFAULT_OUT = REPO_ROOT / "eval" / "hydralamp_20260826" / "replay" / "REPLAY_MANIFEST.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def replay_events(events_path: Path) -> dict:
    events = []
    for line in events_path.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            events.append(json.loads(line))

    replay = {
        "schema": "hydradg.hydralamp.replay.v1",
        "event_count": len(events),
        "ordering": "event_index",
        "events": events,
        "fcg_roots": [e["fcg_root_after"] for e in events],
        "msm_transitions": [
            {"event_index": e["event_index"], "from": e["msm_state_before"], "to": e["msm_state_after"]}
            for e in events
        ],
    }
    replay["replay_hash"] = hashlib.sha256(
        json.dumps(replay["events"], sort_keys=True).encode()
    ).hexdigest()
    return replay


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.events.exists():
        print(f"Events not found: {args.events}", file=sys.stderr)
        return 1

    replay = replay_events(args.events)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(replay, indent=2))
    print(json.dumps({"event_count": replay["event_count"], "replay_hash": replay["replay_hash"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
