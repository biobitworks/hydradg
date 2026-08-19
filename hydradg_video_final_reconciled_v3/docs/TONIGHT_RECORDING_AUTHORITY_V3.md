# HydraDG Tonight Recording Authority v3

## Authority for tonight

This file supersedes the previous video-finalizer execution order.

Use the Release Watch recording lane from the other conversation as the authoritative
tonight path:

- branch: `hack-hydra/context-iceberg-reconcile-20260819`
- isolated recording worktree: `/Users/byron/projects/active/hydradg-video`
- PR #17 remains draft/mergeable until local video receipt exists
- supplied PR head: `25326727165f0d3f6eefac54425fa1e7042dea8f`
- do NOT wait for Vercel
- do NOT require K15/challenger-model/extra-dataset work to record
- do NOT require real signing or Merkle/MMR to record
- preserve the full500 negative/neutral result as the core scientific story

The newer E2E/K15/model-comparison artifacts remain preserved as next-phase evidence.
They are not deleted, but they are not a VIDEO_READY prerequisite tonight.

## Required live path

Run the remote branch's own scripts:

1. `scripts/prepare_video_worktree.sh`
2. `scripts/video_ready_gate.sh`

Record live only if:

`VIDEO_READY_LIVE=YES`

Then launch:

`HYDRADG_VIDEO_MODE=live bash scripts/start_video_demo.sh`

Expected:
- `VIDEO_DEMO_MODE=LIVE_LOCAL_NEXTJS`
- `VIDEO_DEMO_URL=http://127.0.0.1:3012/`

## Required fallback path

If the live gate fails, do not fake it.

Run:
`scripts/static_video_gate.sh`

Use static mode only if:

`STATIC_VIDEO_READY=YES`

Then launch:
`HYDRADG_VIDEO_MODE=static bash scripts/start_video_demo.sh`

In the recording explicitly label this:
`OFFLINE PRESENTATION FALLBACK — NOT LIVE HYDRADB CONTROL SURFACE`

## Chrome screenshots

After either live or static gate passes, run the bundled:
`scripts/capture_chrome_screenshots.sh`

The screenshots are derived presentation artifacts and must be hashed.

## Toy DRM-free seal

The toy Ed25519 key is intentionally public and distributed through the demo FCO/FCG.
It demonstrates reproducible/open sealing only.

It does not establish authenticity.

Real project signing remains separate and pending unless a real signature receipt exists.
