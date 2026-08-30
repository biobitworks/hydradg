# What IC Actually Received — HydraLamp Submission

**Deadline cutoff:** `2026-08-27T22:39:24Z`  
**Payload SHA-256:** `230bd00a6d95e57d423dd26d2be18512c2041030f1b7007bdb0374a85722611d`  
**Machine-readable:** `WHAT_WE_SENT.json`

## Summary

IC received exactly **six text fields** via `ic_hack_submit`. No vault folder, no attached media, no machine-readable receipts, no origin comparison, no signed request.

| Dimension | What IC received | Status |
| --- | --- | --- |
| Title | `HydraLamp` | SUBMITTED |
| Blurb | Agent-native zero-trust control plane; 46-event golden lane | SUBMITTED |
| Repo | `https://github.com/biobitworks/hydradg` | SUBMITTED |
| Demo | `https://hydralamp.vercel.app/` | SUBMITTED |
| Agent surface | HTTP API enumeration (6 endpoints) | SUBMITTED |
| Vault folder | `null` | NOT_SUBMITTED |
| Screenshots | None via IC | AVAILABLE_BUT_NOT_SUBMITTED (69 PNGs) |
| Video | None via IC | AVAILABLE_BUT_NOT_SUBMITTED (demo.mp4/webm) |
| Hero image | Not in vault; on demo `/submission` only | DESCRIBED_NOT_ATTACHED |
| Text evidence pack | None | AVAILABLE_BUT_NOT_SUBMITTED |
| Benchmark/eval receipts | None | AVAILABLE_BUT_NOT_SUBMITTED |
| Sponsor evidence | Named in agent_surface only | DESCRIBED_NOT_ATTACHED |
| Origin/time proof | None | AVAILABLE_BUT_NOT_SUBMITTED |
| Signed request | Bearer only | NOT_USED |
| Origin MMR | None | NOT_COMMITTED at submit time |

## Critical gaps for judges

1. **Repo points to HydraDG (Aug 18)** — not the standalone HydraLamp repo, not the hackathon branch path.
2. **No `folder_id`** — despite IC schema explicitly supporting slides/video/screenshots in vault.
3. **Blurb does not state** when HydraLamp work began or how it differs from Hack Hydra.
4. **Agent surface is prose** — no curl one-liners, no MCP discovery proof, no evidence that HydraLamp used IC's own agent surface.
