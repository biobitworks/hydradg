# HydraDG Video-Ready Finalizer v1

This is the last local gate before recording the Hack Hydra demo.

## Give to Antigravity + Gemini

Read first:

`prompts/VIDEO_READY_MASTER_PROMPT.md`

Do not run another scientific perturbation.

## Intended order on magicSTUDIObox

1. Place/extract this package anywhere.
2. Antigravity/Gemini generate and validate the real:
   `context_iceberg_state.json`
3. Export:
   `HYDRADG_ICEBERG_STATE_PATH=<that file>`
4. Build the site.
5. Start the local stack:
   `./scripts/start_video_stack.sh`
6. Run:
   `./scripts/video_ready_gate.sh`
7. Record only when output contains:
   `VIDEO_READY=YES`
   `NEXT=RECORD_VIDEO_NOW`

The gate does not require GitHub push, Vercel, or Ed25519 signing.
Those states must remain accurately labeled pending/deferred if not performed.

## Video script

`docs/VIDEO_SCRIPT_90S.md`

## Claim boundaries

`docs/VIDEO_CLAIM_BOUNDARIES.md`


## Chrome/screenshots

After `VIDEO_READY=YES`:

```bash
./scripts/capture_chrome_screenshots.sh
```

This creates:
- deterministic `agent-browser` full-page screenshots when available;
- actual Google Chrome/macOS screen captures;
- a SHA-256 screenshot manifest.

## Toy DRM-free package seal

The v2 package contains a deliberately public Ed25519 demonstration private/public key pair.

Verify:

```bash
python3 scripts/verify_toy_seal.py
```

Expected:

```text
TOY_SEAL_SIGNATURE=PASS
AUTHENTICITY=NOT_ESTABLISHED_BY_TOY_KEY
PRIVATE_KEY_DISCLOSURE=INTENTIONAL
```

The toy key demonstrates/reproduces the seal mechanism only. Because the private key is public,
anyone can forge it. The real project signature remains external and pending.
