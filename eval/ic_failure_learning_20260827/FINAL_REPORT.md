# IC Failure Learning — Final Report

**Host:** magicSTUDIObox.local
**Branch:** hack-hydra/ic-failure-learning-20260827 @ `94059bbd0990`

## Answers

1. **Earliest poison object:** `folder_id=null` at submit (C); README poison is contributing (D-layer).
2. **README Anticube:** SELF_NON_SAFE
3. **Criteria violated:** R_VAULT_FOLDER, R_ORIGIN_LEGIBILITY, R_NO_UNSURFACED_JUDGE_EVIDENCE
4. **README downstream dependents:** 4
5. **Missing vault earlier than README in causal chain:** YES (C primary per forensic audit)
6. **SeedGraph rule ingestion:** PASS
7. **Anticube discrimination:** Quadrant adds context-bound safety beyond provenance
8. **Blind C recovery without EVAL_ONLY label:** measured in E05 scores
9. **M1 vs M0:** see MODEL_BEHAVIOR_DELTA.json
10. **M2 vs M1:** see MODEL_BEHAVIOR_DELTA.json
11. **Model weights changed:** NO
12. **Protocol blocks repeat:** measured in E06 prevents_C rate
13. **Poison preserved:** YES
14. **Recovery (antidote):** fixture created; E07 measures classification shift
15. **FCG root:** `08267db2a56b96155db46a06d334d9ed27a7a09dc43cd276923d32b56167131e`
16. **MMR root:** `08267db2a56b96155db46a06d334d9ed27a7a09dc43cd276923d32b56167131e`
17. **MMR verification:** PASS

## Evidence classes
- DIRECT_HUMAN_EVIDENCE: submission, postmortem, protocol
- DETERMINISTIC_TOOL_OUTPUT: cases, FCG, scorer
- PROBABILISTIC_MODEL_OUTPUT: all Ollama responses
- INFERENCE_HYPOTHESIS: README poison causal chain

**Claim ceiling:** FAILURE_LEARNING_EXPERIMENT_RESULTS_ONLY
