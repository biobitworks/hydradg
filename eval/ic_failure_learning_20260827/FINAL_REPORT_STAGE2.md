# IC Failure Learning — Stage 2 Closeout

**Host:** magicSTUDIObox.local  
**Branch:** `hack-hydra/ic-failure-learning-20260827` @ `94059bbd0990`

## Execution lineage

| SHA | Role |
|-----|------|
| `a7941dc3…` | Original preregistered infrastructure |
| `f613bcd0…` | Stage-1 experiment execute |
| `94059bbd…` | Scorer generation-key fix |
| `94059bbd0990…` | Post-Stage2 custody closeout |

## Stage 2 result

- **432** raw/scored rows verified (0 unknown IDs, 0 duplicate keys)
- **414** Stage2-proper rows (`qwen3:1.7b`, `qwen2.5-coder:7b`)
- **18** canary partial rows quarantined (`qwen2.5:1.5b`, ABORTED_EXECUTION_SETUP)

## Verdict

**STAGE2_EXECUTION_COMPLETE**  
**FAILURE_LEARNING_BEHAVIOR_IMPROVEMENT_NOT_ESTABLISHED**

Preserved nulls: E05 top1=0/7, E06 prevents-C=0/13, cold-start detection=0.

## MMR

- Predecessor: `08267db2a56b96155db46a06d334d9ed27a7a09dc43cd276923d32b56167131e`
- Post-model: `c1134aa670e0cb5fcd1602f055223619ea8afa0d539087618bcaaebbed3b01bf`
- Verification: COMMITTED_FAILURE_LEARNING_POST_MODEL_DOMAIN

## Total ingest

- FCG root: `27ba2a47a1bf2570b71d1d2acf9ddd7941094c2509466a73e1383a6c6c116bbe`
- 32 sources atomized; structural coverage 1.0

## Next Daisy

Structured FCG retrieval vs flat rule prose (EXP-008) — see `NEXT_DAISY_FALSIFICATION.json`.
