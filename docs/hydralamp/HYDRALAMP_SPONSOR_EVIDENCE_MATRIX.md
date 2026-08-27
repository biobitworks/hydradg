# HydraLamp Sponsor Evidence Matrix

| Sponsor | Integration point | Implemented? | Real call? | Receipt? | Creds | Fallback | Demo value | Failure behavior | Claim ceiling |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cloudflare | `workers/hydralamp-run-state` + `cloudflareProjection.ts` | Stub + local projection | NOT LIVE deploy | CLOUDFLARE_BLOCKER / projection transport | HYDRALAMP_CF_WORKER_URL | LOCAL_DURABLE_PROJECTION | Outer execution framing | Show READY / NOT LIVE | NOT LIVE |
| Runtype | `@runtypelabs/sdk` in coordinator | Yes | ERROR preserved | RUNTYPE_FOUNDER_REPRO / mission receipts | RUNTYPE_API_KEY | Deterministic agent in golden path | Agent execution/handoff | Visible ERROR, no CONNECTED | PROBABILISTIC / ERROR |
| Mitosis / Cortex | `cortexAdapter.ts` / mi CLI | Yes | trial_expired | MITOSIS_FOUNDER_REPRO | Office + plan | UI shows BLOCKED | Memory/verify continuity | BLOCKED_TRIAL_EXPIRED | NOT canonical custody |
| Cotal | `cotalAdapter.ts` | Yes | Prior deterministic tx | sponsor closeout | Cotal env | N/A for primary demo | Mesh optional | Bounded | Deterministic test bounded |
| Nebius | — | NOT FOUND in web adapters | No | — | — | — | — | UNKNOWN | UNKNOWN |
| Tavily | `tavilyAdapter.ts` | Yes | Prior PASS | sponsor tavily receipts | TAVILY_API_KEY | Skip | Retrieval optional | Fail closed | EXTERNALLY_RETRIEVED |
| Tenki | `tenkiAdapter.ts` | Yes | Prior PASS | sponsor tenki | TENKI | Skip | Sandbox optional | Fail closed | Tool output |
| Mistral | — | FUTURE/OPTIONAL | No | — | — | — | — | NOT IN CRITICAL PATH | FUTURE_OPTIONAL |

Never display CONNECTED/VERIFIED without a current real test.
