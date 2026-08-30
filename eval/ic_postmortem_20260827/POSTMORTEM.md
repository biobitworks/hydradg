# Executive finding

HydraLamp submitted **six text fields** to Immersive Commons with `folder_id: null`. The payload SHA-256 `230bd00a6d95e57d423dd26d2be18512c2041030f1b7007bdb0374a85722611d` matches the sealed artifact. IC acknowledged at `2026-08-27T22:39:24Z`.

By the submission deadline we had **69 images, 3 videos, 85+ text/receipt artifacts, and a complete origin timeline** — none attached to IC. Judges received a working demo link and a repo that looks like a month-old Hack Hydra project. **Both verbal-feedback hypotheses are confirmed:** origin confusion was inevitable from the submitted fields alone, and multimodal evidence delivery failed.

**Earliest causal divergence:** We executed `ic_hack_submit` as a text form without populating `folder_id`, then planned vault upload 33 minutes after acknowledgement (`IC_VAULT_UPLOAD_PACKET` at 23:12 UTC).

---

## What IC actually received

| Field | Value |
| --- | --- |
| title | HydraLamp |
| blurb | Agent-native zero-trust control plane; 46-event golden lane |
| repo_url | https://github.com/biobitworks/hydradg |
| demo_url | https://hydralamp.vercel.app/ |
| agent_surface | HTTP API enumeration (6 endpoints) |
| folder_id | **null** |

Evidence: `eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json`, `IC_SUBMIT_RECEIPT.json`.

## What existed but IC did not receive

- 69 PNG screenshots + contact sheet (all pre-deadline)
- demo.mp4 / demo.webm / demo.webp
- Submission hero PNG (`HYDRALAMP_SUBMISSION_HERO.png`)
- 42+ machine-readable receipts (Runtype, Cortex, Vercel, Tavily, etc.)
- Origin timeline and Hack-Hydra vs HydraLamp comparison
- `00_START_HERE` judge path (existed in operator packet, not in IC)
- Standalone `biobitworks/hydralamp` repo link
- RFC9421 signed submission request

## What was created only after submission

| Artifact | Timestamp |
| --- | --- |
| `IC_VAULT_UPLOAD_PACKET.json` | 2026-08-27T23:12:00Z |
| Post-submit Vercel closeout receipts | 2026-08-27T16:57–17:04 PDT (local) / after platform submit |
| This postmortem | 2026-08-28 |

Note: Some local closeout commits predate IC ack in local timezone but postdate platform `submitted_at` (22:13 UTC).

## What the official rubric rewarded

**100 points**, five bands (30/25/20/15/10). Track 01 (external): cold-start success scores via `agent_surface` + live demo. **"It runs" is a gate** — cannot place if judge cannot trigger live.

Source: `ic_hack_get` rubric_url + https://www.immersivecommons.com/events/hackathon#judging

HydraLamp did not declare a track in the submission. Diagnostic assumption: Track 01.

## Actual vs counterfactual rubric estimate

| Track 01 dimension | Max | Actual range | Counterfactual range |
| --- | ---: | --- | --- |
| Cold-start success | 30 | 12–20 | 22–28 |
| It runs | 25 | 18–23 | 20–25 |
| Surface quality | 20 | 10–16 | 14–18 |
| Lands in product | 15 | 8–13 | 12–15 |
| Demo | 10 | 5–8 | 8–10 |
| **Total** | **100** | **53–80** | **72–92** |

See `IC_RUBRIC_ACTUAL_SCORE_ESTIMATE.json` and `IC_RUBRIC_COUNTERFACTUAL_SCORE_ESTIMATE.json`. Ranges only — not fabricated exact scores.

## Why the difference matters

Judges score **what they can see in 90 seconds**. We optimized product/demo quality and internal custody receipts but delivered almost no judge-visible evidence through IC's designed channel (`folder_id` vault). The repo URL actively misled about project age.

## Earliest divergent dependency

**C — Media generated but not placed in IC Vault before submit.**

Secondary: **D** — provenance not exposed. Tertiary: **B** — IC treated as text form, not agent-native evidence surface.

See `EARLIEST_DIVERGENCE.json`.

## What we should have done differently

1. Retrieve rubric via `ic_hack_get` on day 1 (done Aug 27 05:29 — late but before submit).
2. Build vault package **before** product freeze; attach `folder_id` at submit.
3. Blurb + repo URL must state origin date and hackathon branch.
4. Run 90-second red-team gate before `ic_hack_submit`.
5. Demonstrate IC MCP logistics as meta-proof (agent submits its own evidence).
6. Use signed request mode if operator key registered.

## Origin/provenance proof

| Claim | Evidence |
| --- | --- |
| First HydraLamp commit | `757f3fa7` 2026-08-26 14:36 PDT |
| HydraDG substrate | `e4558026` 2026-08-18 |
| Payload hash | Verified match |
| IC ack | `IC_SUBMIT_RECEIPT.json` |
| Origin MMR (audit domain) | `ORIGIN_MMR_COMMITMENT.json` |

## What cannot be proven retroactively

- Contemporaneous prompt bytes for most build turns
- Exact production SHA at ack second without Vercel API replay
- Judge actual scores (estimates only)

## Reusable protocol for the next hackathon

See `docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md`.

---

## Rubric dimension table

| Rubric dimension | Actual judge-visible evidence | Evidence we had but hid | Best deadline-realistic package | Likely impact |
| --- | --- | --- | --- | --- |
| Cold-start (30) | agent_surface prose + demo URL | START_HERE, curl examples, golden URL | Vault `00_START_HERE.md` + blurb with /golden | High |
| It runs (25) | demo URL | BACKUP_RECEIPT browser verify | Demo link + verify receipt in vault | Medium |
| Surface quality (20) | Long API text | MCP manifest, evidence gateway schema | Structured API table in vault | Medium |
| Lands in product (15) | hydradg repo (Aug 18) | 39-commit timeline, standalone repo | `02_WHAT_IS_NEW_VS_HACK_HYDRA.md` | **High** |
| Demo (10) | Link only | demo.mp4, contact sheet, hero | Vault video + 5 key frames | **High** |

## Evidence coverage table

| Evidence class | Available at deadline | Directly submitted | Coverage |
| --- | ---: | ---: | ---: |
| Text | 85 | 6 fields | 7.1% |
| Images | 69 | 0 | 0% |
| Video | 3 | 0 | 0% |
| Machine receipts | 42 | 0 | 0% |
| Sponsor evidence | 15 | 0 (described only) | 0% |
| Origin provenance | 1 timeline | 0 | 0% |
| **Judge-relevant (curated)** | **24** | **2** | **8.3%** |

---

**Audit orchestration:** Bounded RED_TEAM reviewer under GSD contract (no named gsigmad red-team skill found; instantiated per AGENTS.md).  
**Claim ceiling:** `IDENTITY_AND_SUBMISSION_FORENSICS_ONLY` — not a claim of deserved higher score.  
**SIGNATURE_STATE:** `NOT_SIGNED`  
**MERKLE_MMR_STATE:** `COMMITTED_AUDIT_DOMAIN_ONLY` (origin MMR separate from scientific MMR)
