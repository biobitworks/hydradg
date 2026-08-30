# Cursor Prompt — Immersive Commons Final Submission (Human-Gated)

**Work unit:** `HYDRALAMP_IC_FINAL_SUBMIT_AFTER_OPERATOR_APPROVAL`  
**State:** `READY_FOR_OPERATOR_REVIEW` — do **not** call `ic_hack_submit` until operator writes `APPROVE IMMERSIVE COMMONS SUBMISSION`

---

## Copy-paste prompt for Cursor

```
You are finishing the Immersive Commons Agent Native Builders submission for HydraLamp on magicSTUDIObox.local.

AUTHORITY (read first):
- AGENTS.md, LICENSING.md, eval/immersive_commons_submission_20260827/IMMERSIVE_COMMONS_SUBMISSION_REVIEW.md
- eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json (exact bytes — do not rewrite)
- eval/immersive_commons_submission_20260827/OPERATOR_APPROVAL_PACKET.json

REPOS / SHAs (verify parity before submit):
- hydradg: hack-hydra/hydralamp-20260826 @ HEAD after this commit
- hydralamp: prototype/deterministic-local-20260826 @ d3d928aae47e12afa99c25bd5d1cd94ef74c3da7
- immersivecommons-integration: main @ 8cc82a2 (update after hydradg push if pointers drift)

LICENSE (must appear in any submission-facing surface):
- Software / website / scripts: Apache-2.0 (LICENSE)
- FCO/FCG research content + submission hero image: CC BY-NC-ND 4.0 (LICENSING.md)
- Historical CC BY 4.0 metadata: SUPERSEDED_METADATA_ERROR only — never relicense bytes

PRE-FLIGHT (all must PASS or be explicitly preserved as negative evidence):
1. source ~/.config/immersivecommons/env (mode 600) — FLOOR10_AGENT_TOKEN present
2. ic_hack_me → registered=true, team assigned, submission window open
3. curl -sI https://hydralamp.vercel.app/ → 200
4. curl -sI https://github.com/biobitworks/hydradg → 200
5. Local /submission page renders hero FCO + golden path (http://127.0.0.1:3000/submission)
6. python3 scripts/check_agent_model_handoff_receipt.py eval/immersive_commons_submission_20260827/assets/SUBMISSION_HERO_MATERIALIZATION_RECEIPT.json (if schema applies)
7. gitleaks on staged submission paths — zero secrets

KNOWLEDGE GRAPH:
- Confirm SubmissionHeroMediaFCO appears in /knowledge#hydralamp-submission-hero and /fco/{id}
- Confirm site FCG includes /submission route (lib/siteFcg.ts)
- Record NOT_APPENDED for canonical FCG — website projection only

SUBMIT (only after operator approval string in chat):
- Use exact payload from seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json
- event_id: anb-hack-01
- title: HydraLamp
- repo_url: https://github.com/biobitworks/hydradg
- demo_url: https://hydralamp.vercel.app/
- folder_id: null (omit)
- agent_surface: copy verbatim from payload file

POST-SUBMIT:
- Write eval/immersive_commons_submission_20260827/IC_SUBMIT_RECEIPT.json with raw MCP response hash
- Push hydradg + immersivecommons-integration pointer update
- Set SUBMISSION_WRITE_STATE=SIGNED_BY_OPERATOR in OPERATOR_APPROVAL_PACKET.json

STOP if: registration false, team null, token missing, payload hash mismatch, or operator has not approved.
```

---

## Operator approval strings (exact)

- `APPROVE IMMERSIVE COMMONS SUBMISSION` — proceed with ic_hack_submit using sealed payload
- `SUBMIT THIS EXACT PAYLOAD` — same; verify SHA256 matches review doc
- Any other text → remain AWAITING_HUMAN_APPROVAL

---

## Judge path (8 steps — link in submission blurb if asked)

1. Reference → `/judge#golden-reference`
2. Poison → `/judge#golden-poison`
3. Antidote → `/judge#golden-antidote`
4. HydraDB → `/judge#hydradb-status`
5. Results → `/track03`
6. Evidence → `/evidence`
7. Future → `/beam-1m`
8. Claim → `/eligibility`

Submission hero entry: `/submission`
