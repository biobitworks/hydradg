#!/usr/bin/env python3
"""Render multi-panel HydraLamp replay frames from canonical event log."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = REPO_ROOT / ".venv-hydralamp" / "bin" / "python"
EVAL_ROOT = REPO_ROOT / "eval" / "hydralamp_20260826"

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    subprocess.check_call([str(VENV_PYTHON), "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

DEFAULT_EVENTS = EVAL_ROOT / "HYDRALAMP_EVENTS.jsonl"
DEFAULT_FRAMES = EVAL_ROOT / "replay" / "frames"

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
    "HUMAN_CONTROLLER": (60, 55),
    "RESEARCH_AGENT": (160, 30),
    "VERIFIER_AGENT": (260, 30),
    "REPAIR_AGENT": (160, 80),
    "POISON_AGENT": (260, 80),
}


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def load_events(path: Path) -> list[dict]:
    events = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def draw_panel(draw: ImageDraw.ImageDraw, x0: int, y0: int, w: int, h: int, title: str, lines: list[str], font, font_sm):
    draw.rectangle([x0, y0, x0 + w, y0 + h], outline=(80, 80, 100), fill=(24, 24, 32))
    draw.text((x0 + 8, y0 + 6), title, fill=(200, 200, 220), font=font_sm)
    for i, line in enumerate(lines[:8]):
        draw.text((x0 + 8, y0 + 24 + i * 14), line[:48], fill=(170, 170, 190), font=font_sm)


def render_frame(events: list[dict], frame_index: int, cfmo: dict, mmr: dict, width: int = 960, height: int = 540) -> Image.Image:
    img = Image.new("RGB", (width, height), (16, 16, 22))
    draw = ImageDraw.Draw(img)
    try:
        font_sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except OSError:
        font_sm = ImageFont.load_default()

    visible = events[: frame_index + 1]
    latest = visible[-1] if visible else None
    actor_states = {}
    for ev in visible:
        actor_states[ev["actor_id"]] = ev["msm_state_after"]

    # Panel 1: Sandbox world
    sandbox_lines = [
        f"Event {latest['event_index'] if latest else 0}",
        f"Type: {latest['event_type'] if latest else '—'}",
        "Mode: SANDBOX",
        "Trust: capability (not sandbox)",
    ]
    if latest:
        sandbox_lines.append(f"Access: {latest['access_decision'].get('reason', '—')}")
    draw_panel(draw, 8, 8, 300, 120, "Sandbox World", sandbox_lines, font_sm, font_sm)

    # Panel 2: Open world
    open_lines = [
        f"Actor: {latest['actor_id'] if latest else '—'}",
        f"MSM: {latest['msm_state_after'] if latest else '—'}",
        "Mode: OPEN_WORLD",
        "Defense-in-depth only",
    ]
    draw_panel(draw, 316, 8, 300, 120, "Open World Gateway", open_lines, font_sm, font_sm)

    # Panel 3: Actor cellular field
    draw.rectangle([624, 8, 952, 128], outline=(80, 80, 100), fill=(20, 20, 28))
    draw.text((632, 14), "Actor Field (real events)", fill=(200, 200, 220), font=font_sm)
    for actor_id, (ax, ay) in ACTOR_POSITIONS.items():
        state = actor_states.get(actor_id, "UNKNOWN")
        color = STATE_COLORS.get(state, (128, 128, 128))
        px, py = 624 + ax, 40 + ay
        draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=color, outline=(255, 255, 255))
        if latest and latest["actor_id"] == actor_id:
            pulse = 14 + 2 * math.sin(frame_index * 0.5)
            draw.ellipse([px - pulse, py - pulse, px + pulse, py + pulse], outline=(255, 255, 0), width=1)

    # Panel 4: FCG / poison-repair
    fcg_lines = [
        f"FCG: {(latest['fcg_root_after'][:20] + '…') if latest else '—'}",
        f"Drift: {latest.get('delta_g_star_drift_pointer', '—') if latest else '—'}",
    ]
    quarantine_count = sum(1 for e in visible if "QUARANTINE" in e.get("event_type", ""))
    poison_count = sum(1 for e in visible if "POISON" in e.get("event_type", ""))
    fcg_lines.extend([f"Quarantine events: {quarantine_count}", f"Poison events: {poison_count}"])
    draw_panel(draw, 8, 136, 460, 100, "FCG / Poison-Repair", fcg_lines, font_sm, font_sm)

    # Panel 5: CFMO trajectory
    cfmo_versions = cfmo.get("versions", [])[: frame_index + 1]
    cfmo_lines = [f"Versions: {len(cfmo_versions)}"]
    if cfmo_versions:
        last = cfmo_versions[-1]
        cfmo_lines.append(f"Latest: {last.get('state_type', '—')}")
        cfmo_lines.append(f"ID: {last.get('version_id', '—')[:28]}")
    draw_panel(draw, 476, 136, 476, 100, "CFMO Trajectory", cfmo_lines, font_sm, font_sm)

    # Panel 6: MMR progression
    mmr_state = mmr.get("mmr_state", {})
    mmr_lines = [
        f"Algorithm: {mmr_state.get('algorithm_id', '—')}",
        f"Leaves: {mmr_state.get('leaf_count', 0)}",
        f"Root: {(mmr_state.get('root_sha256', '')[:24] + '…') if mmr_state.get('root_sha256') else '—'}",
        "Committed: yes" if mmr.get("verification_receipt", {}).get("committed") else "pending",
    ]
    draw_panel(draw, 8, 244, 944, 80, "MMR Progression", mmr_lines, font_sm, font_sm)

    # Event rail
    draw.text((8, height - 24), f"Frame {frame_index + 1}/{max(len(events), 1)} | renderer v2 multi-panel", fill=(120, 120, 140), font=font_sm)
    return img


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--frames-dir", type=Path, default=DEFAULT_FRAMES)
    args = parser.parse_args()

    if not args.events.exists():
        print(f"Events not found: {args.events}", file=sys.stderr)
        return 1

    events = load_events(args.events)
    cfmo = load_json(EVAL_ROOT / "CFMO_TRAJECTORY.json")
    mmr = load_json(EVAL_ROOT / "MMR_COMMITMENT.json")
    args.frames_dir.mkdir(parents=True, exist_ok=True)

    hashes = []
    for i in range(len(events)):
        frame = render_frame(events, i, cfmo, mmr)
        frame_path = args.frames_dir / f"frame_{i:04d}.png"
        frame.save(frame_path)
        hashes.append(f"{hashlib.sha256(frame_path.read_bytes()).hexdigest()}  {frame_path.name}")

    manifest_path = args.frames_dir.parent / "FRAME_SHA256SUMS.txt"
    manifest_path.write_text("\n".join(hashes) + "\n")
    meta = {"frame_count": len(events), "fps": 2, "renderer": "render_hydralamp_frames.py", "layout": "multi_panel_v2", "layout_frozen": True}
    (args.frames_dir.parent / "RENDER_META.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
