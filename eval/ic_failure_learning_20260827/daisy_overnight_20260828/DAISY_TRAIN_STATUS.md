# Daisy Overnight Train — Status

**Branch:** `hack-hydra/daisy-exp010-20260828` @ prereg commit pending  
**Worktree:** `/Users/byron/projects/active/hydradg-daisy-exp010-20260828`  
**Host:** magicSTUDIObox.local

## EXP-008 / EXP-009 — UNTOUCHED (canonical lane)

Closed on `hack-hydra/daisy-exp008-overnight-20260828` @ `825964f4`.

## EXP-010 — PREREG FROZEN (execute blocked)

| Field | Value |
|-------|-------|
| **Intervention** | `GOVERNED_DECISION_SCHEMA` vs `FREE_FORM` |
| **Changed variable** | `DECISION_GOVERNANCE_SCHEMA_ONLY` |
| **Required paired N (worst-case grid)** | 207 |
| **E06 primary cases in bank** | 244 |
| **Power gate** | PASS |
| **PLAN_CHECK** | PASS |
| **Runtime lease** | `BLOCKED_RUNTIME_LEASE` (Q38 replay active) |
| **Execute** | NOT STARTED |

## Resume (after Q38 lease clears)

```bash
cd /Users/byron/projects/active/hydradg-daisy-exp010-20260828
python3 scripts/run_exp010_prereg.py --repo . --phase exp010-lease-check
# when LEASE_AVAILABLE:
python3 scripts/run_daisy_overnight_train.py --repo . --phase exp010-execute
```
