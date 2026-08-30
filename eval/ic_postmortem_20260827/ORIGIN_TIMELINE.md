# Origin Timeline — HydraDG / Hack Hydra vs HydraLamp

**Evidence class:** Git timestamps are `DETERMINISTIC_TOOL_OUTPUT`. Elapsed windows are Git-visible, not active human hours.

## Verified boundaries

| Milestone | Timestamp (verified) | SHA / note |
| --- | --- | --- |
| HydraDG first Git commit | 2026-08-18 07:58:55 PDT | `e4558026` |
| Hack Hydra intensive window start | 2026-08-19 00:19:53 PDT | Best Use v2 suite |
| Hack Hydra window end (last Aug 18–20 commit) | 2026-08-21 22:20:44 PDT | — |
| Commits in Hack Hydra window | 513 | Git-visible |
| Git-visible Hack Hydra envelope | ≈59h 46m | first→last commit in window |
| **First HydraLamp-specific HydraDG commit** | **2026-08-26 14:36:09 PDT** | `757f3fa7` |
| HydraLamp PR #27 merge | 2026-08-26 15:16:48 PDT | `2e4522c0` |
| Standalone hydralamp repo first commit | ≈2026-08-26 14:47 PDT | per operator packet `d3d928a` |
| Media backup complete | 2026-08-27 11:37:46 UTC | `BACKUP_RECEIPT.json` |
| Submission seal created | 2026-08-27 15:02:10 UTC | seal provenance |
| IC platform `submitted_at` | 2026-08-27 22:13:37 UTC | IC ack |
| IC ack recorded | 2026-08-27 22:39:24 UTC | `IC_SUBMIT_RECEIPT.json` |
| Vault upload packet (post-submit) | 2026-08-27 23:12:00 UTC | **after deadline** |
| HydraLamp integration commits (757f3fa7→b337e60f) | 39 | counted at audit time |

## What judges could infer from submitted fields alone

| Question | Answer from submission alone |
| --- | --- |
| HydraLamp origin date? | **No** — not in blurb |
| Standalone hydralamp repo? | **No** — repo is biobitworks/hydradg |
| 39 + 20 commit split? | **No** |
| HydraDG = pre-existing substrate? | **No** — repo looks like one continuous project since Aug 18 |
| Hack Hydra vs RunType window? | **No** |
| Branch ancestry? | **No** — must inspect Git manually |

**Verdict:** Origin distinction required manual Git archaeology. This is a submission communication defect even though provenance existed internally.
