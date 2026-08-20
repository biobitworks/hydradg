# Hack Hydra 2026 — Resubmission Copy

Use this file as the copy-paste source for the resubmission form. Replace the video placeholder only after the replacement video is uploaded and publicly verified.

## Project name

HydraDG — Graph-Native Governed Context Engine

## Primary track

Track 03 — Memory + Context Retrieval

## GitHub repository

https://github.com/biobitworks/hydradg

## Temporary judge backup

Pinned preview build:

https://hydradg-4u209xn67-biobitworks.vercel.app/

Temporary public judge-access link:

https://hydradg-4u209xn67-biobitworks.vercel.app/?_vercel_share=B5GJZ77ZGBvnnTPP3G6xalyCEs4vzYMT

This share URL expires 2026-08-21 21:16 UTC / 14:16 PDT. It is a temporary bridge while the production site is awaiting redeployment.

Pinned backup source SHA:

`60120da604f3bb6f30edfadc1d609018089beaef`

## Demo video

`PENDING_REPLACEMENT_VIDEO_URL`

Do not submit the placeholder. Until the replacement is uploaded, the previously submitted video remains:

https://youtu.be/7EDb6q-loPA

## One-sentence project summary

HydraDG is a HydraDB-backed governed memory system that preserves changing facts, contradictions, provenance, recovery, and null results as a queryable Fractal Custody Graph instead of silently overwriting context.

## Short description

HydraDG treats long-lived AI context as a governed graph rather than a flat memory buffer. Fractal Custody Objects preserve bounded content identity, provenance, evidence class, and claim ceilings; Fractal Custody Graph edges preserve how sources, transformations, contradictions, supersession, derived evidence, and claims depend on one another. HydraDB is the operational graph/query layer used to traverse this state over time.

The judge golden path demonstrates a reference state, a controlled poison/contradiction, and an antidote/restoration while retaining the divergent history. The project also includes executed LongMemEval evidence and a cross-track dataset × model × K=5/10/100 Daisy Train. The co-primary K=10 family produced 0 of 9 significant model-vs-control tests after Holm-Bonferroni correction, so the project explicitly retains the claim ceiling `NO_MODEL_BENEFIT_OBSERVED` rather than converting the experiment into a model-superiority claim.

## Why HydraDB is load-bearing

HydraDB is not used as a decorative storage layer. The submission projects governed FCO/FCG state into HydraDB so the application can query chronology, provenance, contradiction, supersession, current-state selection, and evidence paths. Representative relationships include `NEXT/PREV`, `ASSERTS`, `DERIVED_FROM`, `ABOUT`, `SUPERSEDED_BY`, and `CONTRADICTS`. The judge application has no Neo4j fallback.

The current canonical BYOG upload has been accepted, but canonical hosted readback parity for the later 653-FCO / 1,692-edge scope remains bounded as indexing/readback pending. The UI intentionally exposes that uncertainty instead of claiming parity before the hosted readback gate passes.

## What changed since the original submission

Since the earlier submission, HydraDG added a clearer golden-path walkthrough, the K=5/10/100 cross-track Daisy Train matrix, an atom-level local-vs-hosted FCO heat map, and stricter hosted-parity claim ceilings. The project now makes the negative result easier for judges to inspect: 0 of 9 co-primary model-vs-control tests were significant after Holm-Bonferroni correction.

## Judge walkthrough

1. Home — problem and governed-context thesis.
2. Judge Lab — Reference → Poison → Antidote.
3. Track 03 — executed LongMemEval evidence and historical K=5 null result.
4. Eligibility — cross-track K=5/10/100 matrix and `0/9` Holm result.
5. Atom Heat Map — canonical local FCOs versus hosted status, with indexing/readback boundary.
6. Evidence / Knowledge — trace a claim back through FCO/FCG lineage and source citations.
7. Eligibility — final claim ceiling and custody state.

## Results / evidence summary

Historical Track 03 LongMemEval full500:

- 500 cases
- 23,867 sessions
- 4,776 entities
- 3,506 facts
- 470 K=5 retrieval-scored cases, with 30 abstentions excluded
- graph-native B/C/D routes did not establish a positive Hit@5 advantage over the flat reference route

Later cross-track co-primary K=10 family:

- Track 01 EnterpriseRAG-Bench, N=300
- Track 02 HydraBlast-Real-Deps, N=250
- Track 03 LongMemEval-S, N=470
- heuristic control plus Qwen2.5-Coder 7B, Qwen2.5 7B, and DeepSeek-R1 14B
- 9 co-primary model-vs-control tests
- Holm-Bonferroni significant: `0 / 9`
- overall claim ceiling: `NO_MODEL_BENEFIT_OBSERVED`

## Claim boundary

HydraDG is not a leaderboard claim and does not claim end-to-end QA superiority. Hit@K and Recall@K are retrieval metrics. `G*` / `ΔG*` is an application-defined dimensionless information-state diagnostic, not physical Gibbs free energy and not an accuracy metric. Jensen-Shannon divergence is used separately for Cloud Drift.

Current cryptographic wording:

- hashes establish content identity where recorded;
- signature state is `NOT_SIGNED` unless a later signing receipt exists;
- Merkle/MMR state is `NOT_MERKLE_COMMITTED` unless a later commitment receipt exists;
- GitHub/Vercel currently reports the pinned preview source commit as unsigned/unverified.

## Suggested final closing sentence

HydraDG is a governed memory experiment: change state, find the first divergence, preserve custody, test recovery, and keep positive, null, negative, and abstaining evidence in the same graph.

## Before resubmitting

- Replace `PENDING_REPLACEMENT_VIDEO_URL` with the verified public video URL.
- Confirm the temporary preview access URL still works; if expired, use the production URL after redeploy or create a fresh share URL.
- Do not change `NO_MODEL_BENEFIT_OBSERVED` unless new executed evidence justifies a different claim ceiling.
- Do not state canonical hosted parity unless the 653-FCO / 1,692-edge readback gate actually passes.
- Prefer the permanent production URL once it is redeployed and smoke-tested.