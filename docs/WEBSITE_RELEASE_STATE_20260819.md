# Website release state — 2026-08-19

Current preferred release branch:

```text
hack-hydra/submission-eligible-20260819
```

Current platform observation:

```text
Vercel hydradg production deployment = READY
source branch = hack-hydra/webapp-mvp-20260818
source commit = e84afb8fafa3494d274edb0bfbfa9ab02b800a96
```

Therefore:

```text
PLATFORM_HEALTH=READY_FOR_OLDER_DEPLOYMENT
CURRENT_RELEASE_LIVE=NO
STATIC_FALLBACK_PRESENT=YES
```

The project should not conflate Vercel platform readiness with deployment of the current release candidate.
