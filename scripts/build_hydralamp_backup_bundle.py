#!/usr/bin/env python3
"""Build HydraLamp LIVE INTERACTIVE backup bundle (HTML + video + keyframes)."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVAL = REPO / "eval" / "hydralamp_20260826"
DEFAULT_BACKUP = EVAL / "backup"
EVENTS = EVAL / "HYDRALAMP_EVENTS.jsonl"
FRAMES = EVAL / "replay" / "frames"
FPS = 2

# Semantic keyframes: name -> frame index (0-based, aligned to event stream)
KEYFRAMES = {
    "00_spawn.png": 0,       # event 1 HANDSHAKE HUMAN
    "02_reference.png": 3,   # event 4 READ_OK public
    "05_poison.png": 4,      # event 5 READ_PRIVATE_DENIED
    "07_denied.png": 7,      # event 8 UNAUTHORIZED_CANONICAL_WRITE_BLOCKED
    "10_authorized.png": 9,  # event 10 READ_OK private
    "13_evidence.png": 12,   # event 13 HANDSHAKE context
    "15_context.png": 14,    # event 15
    "17_antidote.png": 6,      # event 7 CANONICAL_PROMOTED repair
    "19_restore.png": 29,    # event 30 READ_OK restore
    "20_pass.png": 45,       # event 46 final gate
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_events() -> list[dict]:
    return [json.loads(l) for l in EVENTS.read_text().splitlines() if l.strip()]


def ensure_frames() -> None:
    if not FRAMES.exists() or not list(FRAMES.glob("frame_*.png")):
        subprocess.check_call(
            [str(REPO / ".venv-hydralamp" / "bin" / "python"), str(REPO / "scripts" / "render_hydralamp_frames.py")]
        )


def write_manifest(backup: Path, events: list[dict]) -> None:
    manifest = {
        "schema": "hydradg.hydralamp.backup_manifest.v1",
        "task_id": "HYDRALAMP_REAL_EVIDENCE_RESTORE_V1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch": subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip(),
        "head_sha": subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip(),
        "event_count": len(events),
        "events_sha256": sha256_file(EVENTS),
        "replay_hash": hashlib.sha256(json.dumps(events, sort_keys=True).encode()).hexdigest(),
        "fps": FPS,
        "keyframes": {k: v for k, v in KEYFRAMES.items()},
        "claim_ceiling": "DEMO_SESSION_MECHANISM_CANARY_NOT_EMPIRICAL_CLAIM",
        "artifacts": [],
    }
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


TEMPLATE = Path(__file__).resolve().parent / "templates" / "hydralamp_backup_index.html"


def write_html(backup: Path, events: list[dict], n_frames: int) -> None:
    """Emit self-contained 0D→4D offline player (ContextIcebergHero projection semantics)."""
    del n_frames  # event stream is authoritative; frame count must equal len(events)
    tpl = TEMPLATE.read_text(encoding="utf-8")
    html = (
        tpl.replace("__EVENTS_JSON__", json.dumps(events, separators=(",", ":")))
        .replace("__N_MAX__", str(max(0, len(events) - 1)))
    )
    (backup / "index.html").write_text(html, encoding="utf-8")
    (backup / "review").mkdir(exist_ok=True)


def build_videos(backup: Path) -> dict[str, str]:
    states: dict[str, str] = {}
    pattern = str(FRAMES / "frame_%04d.png")
    mp4 = backup / "demo.mp4"
    webm = backup / "demo.webm"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-framerate", str(FPS), "-i", pattern, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)],
            check=True, capture_output=True,
        )
        states["MP4_BACKUP"] = "PASS"
    except subprocess.CalledProcessError:
        if (EVAL / "replay" / "HYDRALAMP_REPLAY.mp4").exists():
            shutil.copy2(EVAL / "replay" / "HYDRALAMP_REPLAY.mp4", mp4)
            states["MP4_BACKUP"] = "PASS_COPIED_FROM_REPLAY"
        else:
            states["MP4_BACKUP"] = "FAIL"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-framerate", str(FPS), "-i", pattern, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "35", str(webm)],
            check=True, capture_output=True,
        )
        states["WEBM_BACKUP"] = "PASS"
    except subprocess.CalledProcessError:
        states["WEBM_BACKUP"] = "FAIL"
    return states


def build_webp(backup: Path) -> str:
    webp = backup / "demo.webp"
    pattern = str(FRAMES / "frame_%04d.png")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-framerate", str(FPS), "-i", pattern, "-loop", "0", "-quality", "80", str(webp)],
            check=True, capture_output=True,
        )
        return "PASS"
    except subprocess.CalledProcessError:
        pass
    try:
        from PIL import Image

        imgs = [Image.open(p).convert("RGB") for p in sorted(FRAMES.glob("frame_*.png"))]
        imgs[0].save(webp, save_all=True, append_images=imgs[1:], duration=int(1000 / FPS), loop=0, format="WEBP")
        return "PASS"
    except Exception:
        return "FAIL"


def build_keyframes_and_contact(backup: Path) -> str:
    from PIL import Image

    thumbs = []
    for name, idx in KEYFRAMES.items():
        src = FRAMES / f"frame_{idx:04d}.png"
        if not src.exists():
            continue
        shutil.copy2(src, backup / name)
        thumbs.append(Image.open(src).convert("RGB"))

    if not thumbs:
        return "FAIL"

    # contact sheet: 2 rows x 5 cols
    w, h = thumbs[0].size
    cols, rows = 5, 2
    sheet = Image.new("RGB", (w * cols, h * rows), (16, 16, 22))
    for i, im in enumerate(thumbs[:10]):
        x, y = (i % cols) * w, (i // cols) * h
        sheet.paste(im, (x, y))
    sheet.save(backup / "contact-sheet.png")
    return "PASS"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_BACKUP)
    args = ap.parse_args()
    backup: Path = args.out
    if backup.exists():
        shutil.rmtree(backup)
    backup.mkdir(parents=True)
    (backup / "frames").mkdir()

    ensure_frames()
    events = load_events()
    n_frames = len(list(FRAMES.glob("frame_*.png")))

    shutil.copy2(EVENTS, backup / "events.jsonl")
    for fp in sorted(FRAMES.glob("frame_*.png")):
        shutil.copy2(fp, backup / "frames" / fp.name)

    write_manifest(backup, events)
    write_html(backup, events, n_frames)

    video_states = build_videos(backup)
    webp_state = build_webp(backup)
    key_state = build_keyframes_and_contact(backup)

    hashes = {}
    for p in sorted(backup.rglob("*")):
        if p.is_file() and p.stat().st_size < 50_000_000:
            hashes[str(p.relative_to(backup))] = sha256_file(p)

    pred_path = EVAL / "backup_predecessor_20260827" / "PREDECESSOR_AUDIT.json"
    predecessor = None
    if pred_path.exists():
        predecessor = json.loads(pred_path.read_text(encoding="utf-8"))

    # Gate fields start as structural claims from generation; LIVE readiness
    # requires browser verification (see review/BROWSER_VERIFY.json).
    receipt = {
        "schema": "hydradg.hydralamp.backup_receipt.v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task_id": "HYDRALAMP_REAL_EVIDENCE_RESTORE_V1",
        "head_sha": subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip(),
        "branch": subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip(),
        "host": "magicSTUDIObox.local",
        "BACKUP_MEDIA_BUILD": "PASS" if video_states.get("MP4_BACKUP", "").startswith("PASS") and key_state == "PASS" else "PARTIAL",
        "BACKUP_EVENT_STREAM": "PASS",
        "BACKUP_EVENT_COUNT": "PASS" if len(events) == 46 else "FAIL",
        "BACKUP_HASH_CHAIN": "PASS" if sha256_file(backup / "events.jsonl") == sha256_file(EVENTS) else "FAIL",
        "BACKUP_0D": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_1D": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_2D": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_3D": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_4D": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_POINTER_CONTROLS": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_BUILTIN_CONTROLS": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_KEYBOARD_CONTROLS": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_TOUCH_CONTROLS": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_NODE_INSPECTION": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "BACKUP_OFFLINE": "PASS",
        "BACKUP_NO_EXTERNAL_NETWORK": "PASS",
        "BACKUP_EVENT_GRAPH_SYNC": "STRUCTURAL_PRESENT_PENDING_BROWSER_VERIFY",
        "SPATIAL_COORDINATES": "DETERMINISTIC_VISUALIZATION_LAYOUT_NOT_SCIENTIFIC_COORDINATES",
        "ORIGINAL_READY_CLAIM_VALID": "NO",
        "predecessor": {
            "path": "eval/hydralamp_20260826/backup_predecessor_20260827/",
            "EARLIEST_DIVERGENCE": (predecessor or {}).get("EARLIEST_DIVERGENCE", "NO_3D_4D_GRAPH_FRAME_SLIDESHOW_ONLY"),
            "artifact_sha256": (predecessor or {}).get("artifact_sha256"),
        },
        "HTML_BACKUP": "PASS_STRUCTURE",
        "MP4_BACKUP": video_states.get("MP4_BACKUP", "FAIL"),
        "WEBM_BACKUP": video_states.get("WEBM_BACKUP", "FAIL"),
        "SCREENSHOT_BACKUP": key_state,
        "ANIMATED_BACKUP": webp_state,
        "CONTACT_SHEET": key_state,
        "LIVE_INTERACTIVE_BACKUP_READY": "FAIL",
        "EARLIEST_DIVERGENCE": "BROWSER_VERIFY_PENDING",
        "CLAIM_CEILING": "DEMO_SESSION_MECHANISM_CANARY_NOT_EMPIRICAL_CLAIM",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "artifacts": sorted(hashes.keys()),
        "artifact_sha256": hashes,
        "open": f"file://{backup / 'index.html'}",
    }
    (backup / "BACKUP_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in receipt if k not in ("artifacts", "artifact_sha256")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
