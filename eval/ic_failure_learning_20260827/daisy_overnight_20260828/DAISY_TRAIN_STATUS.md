# Daisy Overnight Train — Status

**Branch:** `hack-hydra/daisy-exp008-overnight-20260828` @ `407e04ce`  
**Worktree:** `/Users/byron/projects/active/hydradg-daisy-exp008-overnight-20260828`  
**Host:** magicSTUDIObox.local

## EXP-008 — CLOSED

- Result: `UNDERPOWERED` (E06 n_paired=2)
- Decision: → EXP-009

## EXP-009 — CLOSED

**Intervention:** Causal FCG ordering vs neutral canonical ID ordering (ATOM_ORDER_ONLY)  
**Cells:** 300/300  
**Atom-set gate:** PASS (identical FCO sets C0/C1 per case)  
**Ordering isolation gate:** PASS  

| Field | Value |
|-------|-------|
| **EXPERIMENT_PRIMARY_VERDICT** | `UNDERPOWERED` |
| **MECHANISTIC_EXPLORATORY_PATTERN** | `DIRECTIONALLY_POSITIVE_SECONDARY` |
| **E06 n_paired** | 2 |
| **E06 rd** | 0.0 |
| **ordering_established** | **NO** |
| **Valid parse rate** | 88.3% |
| **Daisy next** | `EXP-010` (queued, NOT started) |

Bounded conclusion: causal FCG ordering effect **not established** on confirmatory E06 endpoint. Exploratory secondary signal recorded; not promoted to SUPPORTED_POSITIVE.

## Pending

- EXP-010 governed decision schema ablation
- EXP-011 retrieval neighborhood
- EXP-012 maximal admissible context diagnostic
- FRONTIER_ESCALATION_PACKET (human gate)

## Resume

```bash
cd /Users/byron/projects/active/hydradg-daisy-exp008-overnight-20260828
python3 scripts/run_daisy_overnight_train.py --repo . --phase exp010-prereg  # when implemented
```
