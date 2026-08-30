# HydraDG Judge Backup Deployment — 2026-08-20

This record identifies the temporary judge-facing backup deployment to use while the production site cannot yet be redeployed.

## Pinned backup application

- Vercel project: `hydradg`
- Deployment ID: `dpl_ZYaqRFe5k9FpLsG6SoSuHX1cisoV`
- Deployment state: `READY`
- Deployment target: preview / non-production
- Git branch: `hack-hydra/final-hosted-fcg-20260820`
- Source commit: `60120da604f3bb6f30edfadc1d609018089beaef`
- Source commit message: `fix(final): verify hosted FCG readback and enforce parity claim ceiling`
- GitHub/Vercel commit verification: `unverified` — this is not a cryptographic Git signature.
- Pinned deployment URL: `https://hydradg-4u209xn67-biobitworks.vercel.app/`

## Temporary judge access

The preview is currently protected by Vercel Authentication. The following explicitly shareable Vercel access URL was generated for judge review:

`https://hydradg-4u209xn67-biobitworks.vercel.app/?_vercel_share=B5GJZ77ZGBvnnTPP3G6xalyCEs4vzYMT`

Expiry: **2026-08-21 21:16 UTC / 2026-08-21 14:16 PDT**, approximately 23 hours after creation.

This access URL is intentionally temporary. It must not be treated as the permanent production URL. If judging occurs after expiry, use the redeployed production site or generate a fresh Vercel share URL for the same pinned deployment.

## Current hosted HydraDB claim boundary

At source commit `60120da...`, the judge UI correctly represents the current BYOG state as:

`UPLOAD_ACCEPTED_INDEXING_PENDING`

The current 653-FCO / 1,692-edge canonical hosted readback parity must **not** be called established until the readback/canonicalization gate verifies it. A historical `default`-collection parity receipt is preserved as custody evidence but is not evidence of current `hydradg-judge-demo` canonical BYOG parity.

## Scientific claim boundary

The executed Daisy Train cross-track family retains:

- 9 co-primary K=10 model-vs-control tests;
- Holm-Bonferroni significant results: `0 / 9` at alpha 0.05;
- overall claim ceiling: `NO_MODEL_BENEFIT_OBSERVED`.

The backup deployment is a delivery surface for the governed evidence. Its availability does not change the scientific claim ceiling.

## Cryptographic state

- FCO/file hashes: content identity where recorded.
- Signature state: `NOT_SIGNED` unless a later authorized signing receipt exists.
- Merkle/MMR state: `NOT_MERKLE_COMMITTED` unless a later commitment receipt exists.

A hash is not a signature, and neither is evidence of scientific correctness.