# E2E Acceptance Checklist

## Hard gates

- [ ] Git histories inspected and preserved
- [ ] canonical FCO/FCG specs located
- [ ] latest project FCG root resolved
- [ ] source freeze independent + expected hash
- [ ] byte coverage = 1.0
- [ ] logical record coverage = 1.0
- [ ] orphan count = 0
- [ ] SeedGraph governed mutation route
- [ ] HydraDB isolation/reset gate
- [ ] current Iceberg receipts found
- [ ] K5→K10 interpretation correction receipt written
- [ ] Structural Cloud Drift definition unchanged
- [ ] Retrieval Cloud Drift vocabulary frozen
- [ ] M1 installed: qwen2.5-coder:7b
- [ ] M2 installed: qwen2.5:7b
- [ ] M1 3× structured replay
- [ ] M2 3× structured replay
- [ ] prompt/response/model/config hashes
- [ ] model comparison claim ceiling correct
- [ ] prospective K15 state is PENDING until preregistration/prediction roots verified
- [ ] Best-Use health
- [ ] Iceberg headline/full endpoints
- [ ] model comparison endpoint
- [ ] Next.js typecheck
- [ ] Next.js build
- [ ] site `/api/iceberg`
- [ ] static fallback
- [ ] secret scan
- [ ] E2E receipt
- [ ] canonical FCG append
- [ ] signature state explicit
- [ ] no fake Merkle state

## Green-state wording

Use:
`LOCAL_E2E_VERIFICATION_PASS`

Only if the local hard gates actually ran and passed.

Do not use:
`VERIFIED_SCIENTIFIC_SUCCESS`
or
`VERIFIED_MODEL_SUPERIORITY`
unless separate evidence supports those claims.
