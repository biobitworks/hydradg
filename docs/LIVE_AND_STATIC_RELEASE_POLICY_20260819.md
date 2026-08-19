# HydraDG live + static release policy — 2026-08-19

HydraDG maintains two judge-facing artifact routes so hosting availability is not a single point of failure.

## Route A — live release

Preferred artifact:

```text
current release branch
→ Next.js production build
→ Vercel deployment
→ route/link/browser E2E
→ public URL
```

Required checks:

- `/` returns 200;
- `/demo` returns 200;
- `/judge` returns 200;
- `/evidence` returns 200;
- `/graph` returns 200;
- `/knowledge` returns 200;
- `/track01`, `/track02`, `/track03` return 200;
- `/backup/hydradg.html` returns 200;
- local-only graph actions fail closed when the local Best Use server is unavailable;
- no credential is exposed to the browser;
- mobile and desktop navigation are usable.

## Route B — static fallback

Fallback artifact:

```text
apps/hydradg-web/public/backup/hydradg.html
```

It must remain backend-independent and should be hash-identified in the release artifact manifest.

The static artifact is allowed to describe executed evidence but must not claim that local HydraDB controls are live in that page.

## Submission fallback

If Vercel promotion remains blocked:

```text
fresh public GitHub repo
+ static fallback
+ local execution video
+ retained evidence receipts
```

becomes the presentation package.

The local execution shown in the video and the static/public artifact remain distinct FCO/FCG nodes linked by `PRESENTS` / `DERIVED_FROM`-style application relationships where allowed by the canonical schema.

## Current observed Vercel state

Connected Vercel inspection on 2026-08-19 shows a production deployment in state `READY` for project `hydradg`, sourced from the older branch `hack-hydra/webapp-mvp-20260818` at commit `e84afb8fafa3494d274edb0bfbfa9ab02b800a96`.

Therefore the current release branch is not yet established as the live production artifact.

State:

```text
VERCEL_PLATFORM_AVAILABLE=YES
OLDER_PRODUCTION_DEPLOYMENT=READY
CURRENT_RELEASE_DEPLOYED=NO
STATIC_FALLBACK_IMPLEMENTED=YES
```
