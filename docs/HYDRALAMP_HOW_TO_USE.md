# HydraLamp — How to Use (Hack Hydra 2026)

**Primary public demo:** https://hydralamp.vercel.app/  
**Integrated evidence surface:** https://github.com/biobitworks/hydradg (HydraDG `/hydralamp`, Evidence, Knowledge Base)  
**Offline fallback:** `eval/hydralamp_20260826/backup/index.html` in the HydraDG repo (46/46 events, no external network)

## What is HydraLamp?

HydraLamp is an agent-native governed control plane: models and agents **propose** work; deterministic authorization **decides** what may change. Poison, denial, repair, failure, and restoration remain inspectable as governed evidence.

## Judge click path

1. **OPEN** — https://hydralamp.vercel.app/ (or HydraDG `/hydralamp` when deployed)
2. **REFERENCE** — scrub to event 0 / jump Reference
3. **POISON** — jump Poison or scrub to poison stage
4. **DENIAL / QUARANTINE** — adversarial proposals stay quarantined (`POISON_CANONICALIZED_COUNT=0`)
5. **REPAIR / ANTIDOTE** — jump Repair; REPAIR_AGENT promotes authorized state
6. **RESTORATION** — final PASS stage; judge strip shows `RESTORATION_PASS=true`
7. **0D–4D GRAPH** — mode buttons 0D/1D/2D/3D/4D; rotate, zoom, reset, play/pause, scrub
8. **MEDIA FCO** — standalone lane: capture → hash → pixel seal (see HydraLamp repo media custody eval)
9. **VERIFY MEDIA** — one-pixel tamper test rejects tampered bytes (`PASS_REJECTED`)

## Eight judge metrics (frozen 46-event lane)

| # | Metric | Frozen value |
|---|--------|--------------|
| 1 | PRIVATE_LEAK_COUNT | 0 |
| 2 | UNAUTHORIZED_WRITE_COUNT | 0 |
| 3 | REPLAY_ACCEPTED_COUNT | 0 (5 rejected) |
| 4 | POISON_CANONICALIZED_COUNT | 0 |
| 5 | RESTORATION_PASS | true |
| 6 | QUARANTINE_RESOLVED | true |
| 7 | fcg_root_after | informational |
| 8 | BROWSER_VERIFY_PASS | true |

**Not on judge strip:** CloudDrift 75.3349 (gateway MSM proxy), ΔG* (engineering diagnostic), PASS@3 on 46-event lane (NOT_ESTABLISHED).

## Inspecting a reconciliation delta

Frozen source → `reconcile_measurements.py` → `SUBMISSION_FREEZE_RECONCILIATION_DELTA.json` → claim ceiling → public projection.

- Source SHA: `44e9d3dc7014b9b2c410a9e1e2c9b35a72cd269e4e561eba40414081ca81690d` (46 events, **do not modify**)
- Projection: `/demo/reconciliation-delta-use-case.json` on HydraDG
- Evidence class: **DERIVED_RECONCILIATION_EVIDENCE** (not empirical experiment)

## Provider states (actual, not forced green)

| Provider | Typical class |
|----------|----------------|
| Tavily | LIVE_PASS (retrieve) |
| Cotal | LOCAL_PASS (bounded tx) |
| Tenki / Daytona | LIVE_PASS (sandbox) |
| Immersive Commons | DISCOVERED (MCP manifest) |
| Runtype | ERROR / BLOCKED |
| Mitosis/Cortex | ERROR / BLOCKED |
| Cloudflare OS | BLOCKED / REPLAY_ONLY |
| Ollarma | LOCAL_PASS (Studio host) |

## Claim boundaries

- `SIGNATURE_STATE=NOT_SIGNED` — no authorized project signature on this lane
- `FCG_MEMBERSHIP` for standalone media FCO — **BLOCKED** (schema authority unavailable)
- `HYDRADG_46_EVENT_PIXEL_SEAL=NOT_RUN` — separate from standalone media `PIXEL_SEAL=PASS`
- `VIDEO_BYTE_IDENTICAL=NOT_ESTABLISHED` unless independently verified

## Backup video / offline

- Repo path: `eval/hydralamp_20260826/backup/demo.mp4` (SHA in `BACKUP_RECEIPT.json`)
- Offline HTML: `eval/hydralamp_20260826/backup/index.html` — 46 events, 0D–4D PASS, no external network
