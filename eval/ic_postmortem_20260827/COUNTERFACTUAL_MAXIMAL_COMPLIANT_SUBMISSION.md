# Counterfactual Maximal Compliant Submission

**Constraint:** Only assets available before `2026-08-27T22:39:24Z`. IC schema only. No overclaim.

Machine-readable: `WHAT_WE_COULD_HAVE_SENT.json`

## Top-level `ic_hack_submit`

| Field | Counterfactual value | Why |
| --- | --- | --- |
| title | `HydraLamp — custody control plane (built Aug 26–27)` | Signals novelty immediately |
| blurb | 3 sentences: judge path, origin split, claim ceiling | 90-second comprehension |
| repo_url | `.../hydradg/tree/hack-hydra/hydralamp-20260826` | Points judge to hackathon branch |
| demo_url | `https://hydralamp.vercel.app/golden` | Direct golden-lane entry |
| agent_surface | API table + 3 curl one-liners | Scores 30pt cold-start band |
| folder_id | `d_<vault>` | Attaches curated evidence pack |

## Vault package (~20 files)

```
00_START_HERE.md           — 90-second judge path
01_JUDGE_SCORECARD_MAP.md  — rubric dimension → evidence location
02_WHAT_IS_NEW_VS_HACK_HYDRA.md — falsifiable origin comparison
03_ORIGIN_TIMELINE.md      — commit dates, not "hours worked"
04_ARCHITECTURE.md           — HydraDG substrate vs HydraLamp layer
05_NEGATIVE_AND_NULL_RESULTS.md — Runtype ERROR, preserved failures
06_SPONSOR_INTEGRATIONS.md — LIVE_VERIFIED vs ERROR per sponsor
07_REPRODUCE.md              — deterministic fixture lane
08_CLAIM_CEILINGS.md         — what we do not claim
HYDRALAMP_SUBMISSION_HERO.png
contact-sheet.png
02_reference.png, 05_poison.png, 07_denied.png, 17_antidote.png, 20_pass.png
demo.mp4
events.jsonl
BACKUP_RECEIPT.json
```

## Agent-native proof (meta)

The strongest compliant submission would also **demonstrate** IC agent logistics:

1. `ic_hack_get` → retrieve rubric
2. `ic_folder_create` + `ic_files_put` → upload vault
3. `ic_hack_submit` with `folder_id`
4. `ic_hack_me` → verify locked state

We submitted via operator-driven text form only. The logistics were not the demo.
