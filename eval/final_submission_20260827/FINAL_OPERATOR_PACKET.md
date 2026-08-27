# Final Operator Packet — 2026-08-27

**TITLE:** HydraLamp  
**BLURB:** Agent-native governed control plane on HydraDG. Models propose; deterministic custody decides.

| Field | Value |
|-------|-------|
| FINAL_BRANCH | `cursor/hydralamp-submission-closeout-20260827` |
| BASE_SHA | `82981cfcf98f0c9d06ec06007f24570d2471efc7` |
| PRIMARY_REPO | https://github.com/biobitworks/hydralamp |
| PRIMARY_DEMO_URL | https://hydralamp.vercel.app/ |
| SECONDARY_EVIDENCE | https://github.com/biobitworks/hydradg/commit/82981cfc |

## Gates

| Gate | Status |
|------|--------|
| LOCAL_STRESS | PASS (typecheck/build/API projection) |
| PUBLIC_BROWSER (prod hydralamp) | PASS anonymous |
| Codex exact-SHA preview | SSO BLOCKED anonymous |
| GITLEAKS (staged candidate) | PASS 0 |
| DELTA_USE_CASE | PASS projection |

## Frozen + judge

- Events: 46 · SHA `44e9d3dc…1690d`
- Judge strip: 8 metrics per `JUDGE_METRIC_SURFACE.json`
- PASS@3 46-event lane: NOT_ESTABLISHED

## Media

| Lane | State |
|------|-------|
| HydraDG 46-event PIXEL_SEAL | NOT_RUN |
| Standalone d9f824e | BYTE_IDENTITY/Pixel seal PASS |
| ONE_PIXEL_TAMPER | PASS_REJECTED |
| VIDEO_BYTE_IDENTICAL | NOT_ESTABLISHED |

## Providers (preserved)

Runtype=ERROR · Mitosis/Cortex=ERROR · Cloudflare=BLOCKED · Tavily=LIVE · Cotal=LOCAL_PASS · Daytona/Tenki=LIVE · Ollarma=LOCAL · Kaggle=NOT_RUN

## Agent surface

`/api/agent-native/evidence-gateway` on HydraDG — discover_capabilities cold-start supported when deployed.

## IC

- Credentials: not available in Cursor lane → `ic_hack_me` BLOCKED
- See EXACT payload in closeout output

## What Byron does next

1. Approve exact Immersive Commons payload below  
2. Promote hydralamp.vercel.app production to d9f824e OR accept prod SHA lag with immutable Git link  
3. Submit IC after human approval — deadline 16:00 PDT
