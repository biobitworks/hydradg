# Judge Links — 2026-08-27

## Primary demo (anonymous public)

| Label | URL |
|-------|-----|
| **HydraLamp production** | https://hydralamp.vercel.app/ |
| Health | https://hydralamp.vercel.app/api/health |

Note: Production alias may trail exact-SHA preview deployments. Exact-SHA preview deployments on Vercel may require SSO for anonymous judges.

## Secondary evidence (HydraDG)

| Label | URL |
|-------|-----|
| GitHub (immutable commit) | https://github.com/biobitworks/hydradg/commit/82981cfcf98f0c9d06ec06007f24570d2471efc7 |
| HydraLamp repo (standalone) | https://github.com/biobitworks/hydralamp/commit/d9f824e2d69804a374da5abd159f742d6846177d |
| Reconciliation delta | https://github.com/biobitworks/hydradg/blob/82981cfc/eval/ollarma_measurement_review_20260827/SUBMISSION_FREEZE_RECONCILIATION_DELTA.json |
| Judge metric surface | https://github.com/biobitworks/hydradg/blob/82981cfc/eval/ollarma_measurement_review_20260827/JUDGE_METRIC_SURFACE.json |
| Offline backup | https://github.com/biobitworks/hydradg/tree/82981cfc/eval/hydralamp_20260826/backup |
| Backup video | `eval/hydralamp_20260826/backup/demo.mp4` (in repo) |

## Notion (operator KB)

| Page | ID |
|------|-----|
| How to Use | 3c958ec7-1eb2-81f1-91a6-de78193266bc |
| Golden Path | 3c958ec7-1eb2-810b-b14f-e45f7b735af5 |
| Evidence | 3c958ec7-1eb2-81ec-bba6-c60afe7c893e |
| Knowledge Hub | 3c358ec7-1eb2-8133-a167-e69f033f0516 |

## Agent surface

| Label | URL |
|-------|-----|
| Evidence Gateway (HydraDG) | `/api/agent-native/evidence-gateway` on deployed HydraDG |
| Immersive Commons MCP | https://www.immersivecommons.com/api/mcp |

## Do not use in public judge packet

- `localhost`, `magicSTUDIObox.local`, `file://`
- Temporary Vercel share URLs with `_vercel_share`
- SSO-gated preview URLs as primary demo without anonymous verification
