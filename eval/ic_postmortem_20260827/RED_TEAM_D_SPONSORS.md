# RED TEAM D — Sponsor Judge

**Source:** `eval/agent_native_sponsors_20260827/SPONSOR_INTEGRATION_CLOSEOUT_V2.json`  
**Rule:** Do not convert logos into integration evidence.

## Sponsor lanes (independent assessment)

| Sponsor | Status | Evidence | Judge-visible at submit? |
| --- | --- | --- | --- |
| **Runtype** | ERROR | `RUNTYPE_MISSION_RECEIPT.json`; execution_id null | Mentioned in agent_surface only |
| **Cloudflare / Vercel** | LIVE_VERIFIED | `VERCEL_CONTROL_PLANE_RECEIPT.json`; production deploy | Demo URL only |
| **Mitosis Cortex** | LIVE_VERIFIED (external memory) | `CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json` | Not in submission |
| **Tavily** | LIVE_VERIFIED | `TAVILY_MISSION_RECEIPT.json` | Not in submission |
| **Cotal** | DETERMINISTIC_FIXTURE | `COTAL_MISSION_RECEIPT.json` bounded tx PASS | Not in submission |
| **Tenki** | DETERMINISTIC_FIXTURE | `TENKI_SANDBOX_MISSION_RECEIPT.json` | Not in submission |
| **AIsa** | PROBABILISTIC_MODEL_OUTPUT | `AISA_PROPOSAL_RECEIPT.json` chat PASS | Not in submission |
| **Immersive Commons** | DISCOVERED | MCP manifest snapshot; submit via operator | Partial — we used IC to submit but didn't prove it |
| **Mitosis Yappy** | BLOCKED | MI_NO_AGENTS | Not surfaced |
| **Hacker Bob** | SKIPPED | scan not executed | Not surfaced |
| **Nebius** | See closeout v2 | — | Not surfaced |

## Runtype bounty ($500)

Judged alongside main rubric. Our state: **ERROR** on live lane. Counterfactual vault must include `05_NEGATIVE_AND_NULL_RESULTS.md` with Runtype ERROR preserved — not hidden.

## Sponsor judge verdict

Strong **configured** integrations; weak **judge-visible** sponsor story. Runtype ERROR is an honesty asset if surfaced; liability if judges assume live Runtype from blurb.
