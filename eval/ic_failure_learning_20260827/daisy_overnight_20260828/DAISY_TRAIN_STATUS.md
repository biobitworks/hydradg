# Daisy Overnight Train — Status

**Branch:** `hack-hydra/daisy-exp008-overnight-20260828`  
**Worktree:** `/Users/byron/projects/active/hydradg-daisy-exp008-overnight-20260828`  
**Parent SHA:** `d8166ae41f68c2d082eaf3d5380af0ea4e9b6bda`  
**Host:** magicSTUDIObox.local

## Bootstrap — COMPLETE

- WORKTREE_GATE: PASS
- MODEL_INVENTORY_FREEZE: qwen3:1.7b, qwen2.5-coder:7b (exact digests frozen)
- DAISY_COMMON_FREEZE: 23 cases, 3 replicates, 8000-char context budget
- Ollarma: NOT_IN_PATH → DIRECT_OLLAMA_API with receipts

## EXP-008 — IN_PROGRESS

Structured FCG retrieval (C1) vs flat prose (C0).  
276 cells = 23 cases × 2 models × 2 conditions × 3 replicates.

Log: `eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP008_RUN.log`

## Pending (decision-gated)

- EXP-008R_CONFIRMATION (if SUPPORTED_POSITIVE)
- EXP-009 causal ordering
- EXP-010 decision schema
- EXP-011 retrieval neighborhood
- EXP-012 maximal admissible context / local capacity diagnostic
- FRONTIER_ESCALATION_PACKET (human required; no auto API)

Monitor: `tail -f eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP008_RUN.log`
