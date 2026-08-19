# Public export delta — 2026-08-19

The fresh public export must include the FCG/website release documentation and verification scripts introduced in the current Hack Hydra work window.

Required additions to the public allowlist:

```text
docs/PROJECT_FCG_UPDATE_20260819.md
docs/PROJECT_FCG_CHANGELOG_20260819.json
docs/WHY_FCG_UPDATED_20260819.md
docs/WEBSITE_MVP_AND_FALLBACK_20260819.md
docs/KNOWLEDGE_LINK_CONTRACT_20260819.md
docs/HASHING_PROOF_20260819.md
docs/RELEASE_ARTIFACT_HASHING_HOWTO_20260819.md
docs/LIVE_AND_STATIC_RELEASE_POLICY_20260819.md
docs/MVP_RELEASE_DELIVERABLES_20260819.md
docs/TURN_HASHING_POLICY_20260819.md
scripts/hash_release_artifacts.py
scripts/check_term_knowledge_coverage.py
scripts/check_static_fallback.py
```

The static fallback itself is already under `apps/hydradg-web/` and is included when that Hack-Hydra web tree is exported.
