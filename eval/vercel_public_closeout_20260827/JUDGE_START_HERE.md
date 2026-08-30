# START HERE — Public judge links

Canonical anonymous entry points (no localhost, no Vercel SSO, no `_vercel_share`):

| Surface | URL |
| --- | --- |
| **START HERE** | https://hydralamp.vercel.app/ |
| **INTERACTIVE THREE-PANE CONSOLE** | https://hydralamp.vercel.app/ |
| **GOLDEN PATH** | https://hydralamp.vercel.app/golden |
| **20 SECOND VIDEO** | https://hydralamp.vercel.app/submission_media/HYDRALAMP_DEMO_20S.mp4 |
| **3 MINUTE VIDEO** | https://hydralamp.vercel.app/submission_media/HYDRALAMP_DEMO_3MIN.mp4 |
| **STATIC FALLBACK** | https://hydralamp.vercel.app/demo/index.html |
| **AGENT DISCOVERY** | https://hydralamp.vercel.app/.well-known/agent.json |
| **HEALTH / DEPLOYED SHA** | https://hydralamp.vercel.app/api/health |
| **FULL SUBMISSION + FCO/FCG EVIDENCE** | https://hydradg.vercel.app/submission |
| **SOURCE** | https://github.com/biobitworks/hydradg |

**Version gate:** `GET /api/health` on HydraLamp must report  
`sha=c6dcadfeff0fa31e63e7865b04e1bef07511edaf` for production parity.

Redeployment anomalies (wrong project, SHA UNKNOWN until env binding) are preserved in  
`eval/vercel_public_closeout_20260827/VERCEL_REDEPLOYMENT_FCG_NOTE.json` — FCG append remains `NOT_APPENDED`.

Verification receipt: `eval/vercel_public_closeout_20260827/PUBLIC_LINKS_E2E_RECEIPT.json`  
Prerequisite for Hacker Bob: all links HTTP 200 + media SHA match manifest.
