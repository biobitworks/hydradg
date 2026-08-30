# SGLang Breakable CUDA Graph Replay — Final Report

## Status

- **REPLAY_EQUIVALENCE**: BLOCKED_CUDA_UNAVAILABLE
- **MODEL_EQUIVALENCE_STATE**: NOT_EQUIVALENT
- **G0/G1/G2/G2A**: All blocked pending CUDA host

## Historical baseline (verified, not SGLang)

- **RUNTYPE_HISTORICAL_MATRIX**: 4x25=100 CONTROL/INVALID_PROOF/REPLAYED_PROOF/BROKEN_AUTHORIZATION_EDGE
- **RUNTYPE_HISTORICAL_RESULT**: CORE_STRESS=PASS per frozen receipt; LIVE_RUNTYPE probe lane_status=ERROR

## Daisy question

WHERE SHOULD THE GRAPH BREAK? — Preregistered candidates at dynamic custody boundaries
(verify_actor_proof, FCG mutation, quarantine). Measured BCG evidence pending GPU lane.

## Claim ceiling


