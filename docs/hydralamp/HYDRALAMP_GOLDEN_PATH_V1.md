# HydraLamp Golden Path V1

**Claim ceiling:** `DEMO_SESSION_MECHANISM_CANARY_NOT_EMPIRICAL_CLAIM`  
**Canonical science:** unchanged unless governed promotion gate runs.

## Flow

`UNLOCK → REFERENCE → POISON → AGENT → VERIFY → ANTIDOTE → RESTORATION → RECEIPT`

Each material step appends a **session FCG** root (`fcg_root_before → fcg_root_after`). Poison remains visible.

## Judge unlock

- UI: **ENTER JUDGE KEY**
- Demo codes include `JUDGE-HYDRA-2026` (capability, **not** a signing key)
- Materializes `JudgeSessionAuthorizationFCO` in an isolated namespace
- Display: `JUDGE SESSION — AUTHORIZED` (never “cryptographically signed” unless a real signing op occurred)

## Controls

| Control | Behavior |
| --- | --- |
| RUN | Advance remaining phases autonomously |
| PAUSE | Preserve session/FCG; stop before next material step |
| STEP | Exactly one phase transition |
| RESET | New session from reference; prior sessions retained |
| CENTER / focus buttons | Current, poison, divergence, restoration, fit |
| FOLLOW CURRENT | Default ON during Run |

## Evidence classes (kept separate)

- Historical executed LongMemEval K5/K10
- Current judge demo session
- Development/incomplete (Daisy 1020, Vithia LME)
- Future (Mistral, BEAM-10M, undeployed CF)

## Local URLs

- `/hydralamp` — judge golden path
- `/api/hydralamp/golden` — unlock/run/pause/step/reset/focus

## Non-goals

- Do not promote demo PASS to VERIFIED_EMPIRICAL_RESULT
- Do not mutate canonical scientific FCG from isolated demo
- Do not show CONNECTED/VERIFIED without a live test
