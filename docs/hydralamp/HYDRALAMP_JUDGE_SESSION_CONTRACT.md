# HydraLamp Judge Session Contract

## Capability

`JudgeSessionAuthorizationFCO` is a **demo capability**, not:

- project private key
- author signing key
- authenticity proof
- Merkle key

UI after unlock: **JUDGE SESSION — AUTHORIZED**

Never: CRYPTOGRAPHICALLY SIGNED (unless a separate real signing operation occurred).

## Isolation

- Each unlock creates `session_id` + `demo_overlay:<session_id>` namespace
- RESET starts a **new** session; prior sessions retained on disk under `eval/hydralamp_golden_path_20260827/sessions/`
- Two simultaneous sessions must not share mutable overlay state
- Session FCG appends are **not** canonical science promotion

## API

`POST /api/hydralamp/golden`

Actions: `unlock | run | pause | step | reset | status | follow | focus`

## Claim ceiling

`DEMO_SESSION_CAPABILITY_NOT_PROJECT_SIGNING_KEY` for auth FCO  
`DEMO_SESSION_MECHANISM_CANARY_NOT_EMPIRICAL_CLAIM` for golden-path run
