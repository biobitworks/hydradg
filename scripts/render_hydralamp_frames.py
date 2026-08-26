#!/usr/bin/env python3
"""Render HydraLamp replay frames from HYDRALAMP_EVENTS.jsonl."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = REPO_ROOT / ".venv-hydralamp" / "bin" / "python"

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    subprocess.check_call([str(VENV_PYTHON), "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

DEFAULT_EVENTS = REPO_ROOT / "eval" / "hydralamp_20260826" / "HYDRALAMP_EVENTS.jsonl"
DEFAULT_FRAMES = REPO_ROOT / "eval" / "hydralamp_20260826" / "replay" / "frames"

STATE_COLORS = {
    "UNKNOWN": (128, 128, 128),
    "AUTHENTICATED": (0, 100, 255),
    "CAPABILITY_GRANTED": (0, 200, 255),
    "EVIDENCE_ACCESSED": (0, 200, 255),
    "PROPOSAL_CREATED": (255, 220, 0),
    "QUARANTINED": (255, 50, 50),
    "VERIFIED": (0, 200, 100),
    "PROMOTED": (160, 0, 200),
    "DENIED": (255, 80, 80),
    "REVOKED": (0, 0, 0),
}

ACTOR_POSITIONS = {
    "HUMAN_CONTROLLER": (120, 200),
    "RESEARCH_AGENT": (320, 120),
    "VERIFIER_AGENT": (520, 120),
    "REPAIR_AGENT": (320, 320),
    "POISON_AGENT": (520, 320),
}


def load_events(path: Path) -> list[dict]:
    events = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def render_frame(
    events: list[dict],
    frame_index: int,
    width: int = 800,
    height: int = 480,
) -> Image.Image:
    img = Image.new("RGB", (width, height), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    visible = events[: frame_index + 1]
    actor_states = {a: "UNKNOWN" for a in ACTOR_POSITIONS}

    for ev in visible:
        actor_states[ev["actor_id"]] = ev["msm_state_after"]

    draw.text((20, 15), "HydraLamp Replay", fill=(255, 255, 255), font=font)
    if visible:
        last = visible[-1]
        draw.text(
            (20, 40),
            f"Event {last['event_index']}: {last['event_type']} | FCG {last['fcg_root_after'][:16]}...",
            fill=(180, 180, 200),
            font=font_sm,
        )

    for actor_id, (x, y) in ACTOR_POSITIONS.items():
        state = actor_states.get(actor_id, "UNKNOWN")
        color = STATE_COLORS.get(state, (128, 128, 128))
        r = 35
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=(255, 255, 255))
        draw.text((x - 50, y + r + 5), actor_id.replace("_", "\n"), fill=(220, 220, 220), font=font_sm)
        draw.text((x - 30, y - 8), state[:4], fill=(255, 255, 255), font=font_sm)

    # Pulse ring on latest event actor
    if visible:
        latest = visible[-1]
        pos = ACTOR_POSITIONS.get(latest["actor_id"])
        if pos:
            pulse = 40 + 5 * math.sin(frame_index * 0.5)
            draw.ellipse(
                [pos[0] - pulse, pos[1] - pulse, pos[0] + pulse, pos[1] + pulse],
                outline=(255, 255, 100),
                width=2,
            )

    draw.text((20, height - 30), f"Frame {frame_index + 1}/{max(len(events), 1)}", fill=(150, 150, 150), font=font_sm)
    return img


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--frames-dir", type=Path, default=DEFAULT_FRAMES)
    parser.add_argument("--fps", type=int, default=2)
    args = parser.parse_args()

    if not args.events.exists():
        print(f"Events not found: {args.events}", file=sys.stderr)
        return 1

    events = load_events(args.events)
    args.frames_dir.mkdir(parents=True, exist_ok=True)

    hashes = []
    for i in range(len(events)):
        frame = render_frame(events, i)
        frame_path = args.frames_dir / f"frame_{i:04d}.png"
        frame.save(frame_path)
        h = hashlib.sha256(frame_path.read_bytes()).hexdigest()
        hashes.append(f"{h}  {frame_path.name}")

    manifest_path = args.frames_dir.parent / "FRAME_SHA256SUMS.txt"
    manifest_path.write_text("\n".join(hashes) + "\n")

    meta = {
        "frame_count": len(events),
        "fps": args.fps,
        "renderer": "render_hydralamp_frames.py",
        "layout_frozen": True,
    }
    (args.frames_dir.parent / "RENDER_META.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
