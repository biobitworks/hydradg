# Daisy Overnight Train — Status

**Branch:** `hack-hydra/daisy-exp008-overnight-20260828` @ `033686ab`  
**Worktree:** `/Users/byron/projects/active/hydradg-daisy-exp008-overnight-20260828`  
**Parent SHA:** `d8166ae41f68c2d082eaf3d5380af0ea4e9b6bda`  
**Host:** magicSTUDIObox.local

## Bootstrap — COMPLETE

| Artifact | State |
|----------|-------|
| WORKTREE_GATE | PASS |
| MODEL_INVENTORY_FREEZE | qwen3:1.7b, qwen2.5-coder:7b |
| DAISY_COMMON_FREEZE | 25 cases, 3 replicates, 8000-char budget |
| Runtime | DIRECT_OLLAMA_API (Ollarma NOT_IN_PATH) |

## EXP-008 — COMPLETE

**Result class:** `UNDERPOWERED`  
**Primary (E06 prevents-C):** n_paired=2, rd=0.0, no discordant pairs  
**Conclusion:** effect not established  
**Next (Daisy):** `EXP-009` causal ordering ablation  

Cells: 300/300 (25×2 models×2 conditions×3 replicates)  
Valid parse rate: 90.7% | UNKNOWN: 50% | MALFORMED: 9.3%

Resume/closeout:
```bash
cd /Users/byron/projects/active/hydradg-daisy-exp008-overnight-20260828
python3 scripts/run_daisy_overnight_train.py --repo . --phase exp008-execute   # missing cells only
python3 scripts/run_daisy_overnight_train.py --repo . --phase exp008-closeout
```

## Pending (preregistered train)

- EXP-009 causal FCG ordering
- EXP-010 governed decision schema
- EXP-011 retrieval neighborhood breadth
- EXP-012 maximal admissible context / local capacity
- FRONTIER_ESCALATION_PACKET (human gate; no auto API)

## Monitor

`eval/ic_failure_learning_20260827/daisy_overnight_20260828/DAISY_TRAIN.jsonl`
