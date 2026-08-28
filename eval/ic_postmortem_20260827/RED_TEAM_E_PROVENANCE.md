# RED TEAM E — Provenance Skeptic

**Goal:** Break the chain human intent → prompt → tool → artifact → commit → production → IC submission.

## Chain audit

| Link | State | Earliest break? |
| --- | --- | --- |
| Human intent | PARTIAL | Operator approval packet exists |
| Prompt bytes | **BROKEN** | Most build turns: `RETROACTIVE_CUSTODY_RECONSTRUCTION` |
| Agent turn receipt | PARTIAL | Seal provenance chain incomplete pre-approval |
| Tool access | VERIFIED | IC submit receipt |
| Artifact hash | VERIFIED | `230bd00a...` matches seal |
| Git commit | VERIFIED | `b337e60f` records receipt |
| Push / remote | VERIFIED | GitHub sync |
| Production deploy | PARTIAL | SHA pinned in operator packet; not re-verified from Vercel at ack |
| IC submission | VERIFIED | Platform ack `2026-08-27T22:39:24Z` |
| IC ack receipt | VERIFIED | `IC_SUBMIT_RECEIPT.json` |

## Earliest divergent dependency

**Contemporaneous prompt capture** for HydraLamp build turns (Aug 26–27). Without prompt hashes, origin MMR leaves after `first_hydralamp_commit` are reconstruction, not contemporaneous custody.

## Signature audit

| Claim | Actual |
| --- | --- |
| Payload SHA-256 | Hash only — **not signature** |
| `SIG-*` legacy labels | Receipt labels — **not signature** |
| GitHub Verified commit | Commit attestation only |
| IC RFC9421 signed submit | **NOT_USED** |
| `SIGNATURE_STATE` | `NOT_SIGNED` |

## Origin MMR (audit domain)

Separate from scientific/demo MMR. Constructed in this audit with linear SHA-256 chain — see `ORIGIN_MMR_COMMITMENT.json`. Domain separator: `hydradg.origin_evidence.v1`.

## Cannot prove retroactively

- Exact prompt bytes for most Aug 26–27 agent turns
- That all model calls used frozen identities without substitution
- Production Vercel SHA at exact ack second without external API replay
