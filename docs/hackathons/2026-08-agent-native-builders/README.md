# Agent Native Builders Hackathon — HydraDG Workspace

**Event:** The Agent Native Builders Hackathon (`anb-hack-01`)  
**Dates:** August 26–27, 2026 · Cloudflare SF, San Francisco  
**Branch:** `hack-hydra/agent-native-builders-20260826`  
**Repository:** https://github.com/biobitworks/hydradg

## Terminal state

| Field | Value |
| --- | --- |
| Application ID | `a_74a64b4f0be8f50a` |
| IC application status | `applied` (pending review) |
| Participant seat | not claimed |
| NDA | `pending_roster_admission` |
| Terminal state | `APPLICATION_SUBMITTED_PENDING` |

## Document map

| File | Purpose |
| --- | --- |
| [FINAL_DRAFT_REVIEW.md](./FINAL_DRAFT_REVIEW.md) | Operator checklist before upload / host follow-up |
| [APPLICATION_ANSWERS.md](./APPLICATION_ANSWERS.md) | Submitted application field answers |
| [APPLICATION_STATUS.md](./APPLICATION_STATUS.md) | Post-submit IC application status |
| [HACKATHON_DOSSIER.md](./HACKATHON_DOSSIER.md) | Event metadata and applicant profile |
| [DEMO_GOLDEN_PATH.md](./DEMO_GOLDEN_PATH.md) | Two-day build and demo schedule |
| [REGISTRATION_STATUS.md](./REGISTRATION_STATUS.md) | Luma vs IC vs seat vs NDA state separation |
| [HOST_FOLLOWUP.md](./HOST_FOLLOWUP.md) | Draft host message while application is pending |
| [GUM_DOCTOR.md](./GUM_DOCTOR.md) | Full governed intake/runbook specification |

## Custody receipts

Machine-readable receipts live under:

`custody/hackathons/2026-08-agent-native-builders/`

Integrity hashes: `custody/hackathons/2026-08-agent-native-builders/SHA256SUMS`

## Live demo surface

Web route (after deploy): `/agent-native-builders-2026`

Source: `apps/hydradg-web/app/agent-native-builders-2026/page.tsx`

## Next experimental gate

Deterministic 20-fixture conformance suite: **PASS** (no live LLM calls).

Preregistered successor: 2-case real-agent canary — see
`eval/agent_native_builders_20260826/PREREGISTERED_2_CASE_REAL_CANARY_MANIFEST.json`
