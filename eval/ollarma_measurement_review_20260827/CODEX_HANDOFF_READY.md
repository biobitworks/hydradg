# Codex Independent Review Handoff

**Branch:** `cursor/hydralamp-submission-closeout-20260827`  
**Parent SHA:** `4c066a1863cc453321a11ba837a8b27c0212a0a6` (before this delta)  
**Frozen source SHA:** `44e9d3dc7014b9b2c410a9e1e2c9b35a72cd269e4e561eba40414081ca81690d` (46 events — **must not change**)

## Review prompt (paste to Codex)

```
Audit this HydraLamp submission-freeze delta as an adversarial release reviewer.
The frozen 46-event source may not change.

Read:
- eval/ollarma_measurement_review_20260827/SUBMISSION_FREEZE_RECONCILIATION_DELTA.json
- eval/ollarma_measurement_review_20260827/JUDGE_METRIC_SURFACE.json
- eval/ollarma_measurement_review_20260827/OPERATOR_SUBMISSION_CLOSEOUT.md
- eval/hydralamp_20260826/SUBMISSION_OPERATOR_PACKET.json
- apps/hydradg-web/components/hydralamp/JudgeMetricStrip.tsx
- apps/hydradg-web/public/demo/judge-metric-surface.json
- git diff cursor/hydralamp-submission-closeout-20260827

Identify earliest divergent dependency for every defect.
Reject any UI claim not supported by exact scoped evidence.
Audit: CloudDrift, ΔG*, restoration_gain, PASS@3, media custody, FCG root,
signature state, Merkle/MMR state.

Fix only release/product defects; do not alter the scientific experiment.
```

## Expected Codex outputs

- `CODEX_REVIEW_RECEIPT.json` with findings severity
- Optional minimal fixes only if release-blocking
- Re-run: typecheck, build, `scripts/local_website_stress.mjs`, gitleaks staged

## Cursor delta in this commit

- Eight-metric frozen judge strip on `/hydralamp`
- Engineering diagnostics disclosure (expandable)
- Local server supervisor + website stress receipts
- IC submission candidate (schema validated, no production write)
