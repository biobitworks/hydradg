# HydraDG — Judge Submission Links and Deployment Note

Hack Hydra 2026 · Track 3 — Memory + Context Retrieval

## Canonical links

- Public repository: https://github.com/biobitworks/hydradg
- Review branch / newest source: `hack-hydra/final-hosted-fcg-20260820`
- Public production URL: https://hydradg.vercel.app/
- Latest READY Vercel preview observed on August 20, 2026: https://hydradg-n2zzxl61d-biobitworks.vercel.app/
- Latest READY preview commit: `8dc3467a966b265fa37bb0efc8d946952f9def2c`
- 3-minute pitch/demo video: https://youtu.be/Cdb5vDF0vA0

## What judges should know

The public production URL remains accessible, but it is an older production release and does not yet contain the newest judge-navigation, hosted-HydraDB status, audit corrections, and continuing receipt-backed experiment updates present on the review branch.

During the final submission window, repeated preview builds reached Vercel's build-rate limit. This was a deployment-capacity/rate-limit issue rather than a scientific gate. The repository therefore remains the authoritative reconstruction and evidence surface for the newest source and receipts. The production URL is planned to be refreshed after the rate limit resets.

The demo video was recorded from the newer local live application. During recording, that application successfully connected to the hosted HydraDB API using database `hydradg` and collection `hydradg-judge-demo`. The observed status established backend connectivity, database binding, collection scope, and request-level canary relation readback. It did not by itself establish full expanded 653-FCO / 1,692-edge canonical parity; that remains a separate verification gate.

HydraDG is still running bounded experiments. New results are accepted only when tied to execution receipts and claim ceilings. Historical null/negative evidence is retained rather than overwritten. Development artifacts that fail execution audit remain preserved in lineage but are not promoted as empirical results.

The canonical judge path is:

`Reference → Poison → Antidote → HydraDB → Results → Evidence → Future Work → Claim Boundary`

The strongest currently established Track 3 benchmark evidence remains the historical LongMemEval-S full500 K=5 retrieval ablation. The tested graph-native B/C/D routes did not establish a positive Hit@5 advantage over the flat route; HydraDG intentionally preserves that null/negative result.

HydraDG also reports deterministic canonical-identity reuse accounting separately from measured storage savings, and theoretical compute/energy abstractions separately from measured wall-energy claims. Future work preregisters serialized-byte reduction, context-token reduction, avoided downstream inference calls, first-divergence localization, recovery rate, and cost per correct governed answer.

## Custody boundary

- SHA-256: content identity where actually computed
- Signature state: `NOT_SIGNED` unless an actual signing receipt exists
- Merkle/MMR state: `NOT_MERKLE_COMMITTED` unless an actual commitment receipt exists
- Hosted connectivity/readback: may be established independently of full canonical parity
- Git history: retained as custody evidence; unsupported prior claims are superseded rather than deleted

This note is intended to help judges reconcile the public production surface, newest preview, recorded local demo, and GitHub evidence state during the final submission window.
