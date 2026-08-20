# HydraDG — Hack Hydra 2026 Judge Review Details

## Project

- **Name:** HydraDG — Graph-Native Governed Context Engine
- **Primary track:** Track 03 — Memory + Context Retrieval
- **Public repository:** https://github.com/biobitworks/hydradg
- **Demo video:** https://youtu.be/7EDb6q-loPA
- **Final integration branch:** `hack-hydra/final-hosted-fcg-20260820`
- **Current curated Vercel branch alias:** https://hydradg-git-hack-hydra-curated-vercel-lineag-4ff6ad-biobitworks.vercel.app
- **Curated deployment commit:** `3ff1245d8a7bb5f49e60d30f3005c2ed9127a475`

## Short description

HydraDG is a governed AI memory and context system built on HydraDB. It keeps temporal state, provenance, contradictions, supersessions, experimental outcomes, and FCO/FCG custody traversable instead of flattening changing context into one latest answer. The judge interface shows what changed, why it changed, and whether a repair restored the reference state while preserving positive, null, negative, and abstaining evidence.

## HydraDB use

HydraDG uses HydraDB as the hosted query and context-graph projection layer. The hosted path for the judge app is:

```text
GitHub repository
  -> HydraDB GitHub connector
  -> database: hydradg
  -> Vercel server-only HydraDB v2 adapter
  -> graph_context readback
  -> curated judge UI
```

The Vercel browser never receives the HydraDB credential value. Canonical FCO/FCG identity remains distinct from the hosted projection so local-to-hosted parity and service/retrieval drift can be measured separately.

## Executed Track 03 result

The completed LongMemEval-S full500 retrieval ablation produced a real negative/null result rather than a manufactured performance claim:

- 500 cases processed
- 23,867 sessions
- 4,776 entities
- 3,506 facts
- 470 retrieval-scored cases
- 30 abstentions
- K=5 graph treatments B/C/D did not establish a positive Hit@5 advantage over reference route A
- evidence-path coverage increased while retrieval recall declined

**Claim ceiling:** `LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA`

HydraDG does not claim to beat LongMemEval or establish end-to-end QA superiority from this result.

## Judge walkthrough

Recommended review order:

1. `/` — Overview / Context Iceberg
2. `/judge` — Reference -> Poison -> Antidote walkthrough
3. `/results/context-vs-entropy` — Context vs Entropy Secret Benchmark (99.94% coverage)
4. `/track03` — bounded Track 03 results
5. `/graph` — FCG/context graph exploration
6. `/knowledge` — project terminology and claim boundaries
7. `/evidence` — custody evidence ledger
8. `/eligibility` — submission and evidence boundaries
9. `/how-to` — judge/reproduction guide
10. `/evolution` — presentation supersession lineage
11. `/backup/hydradg.html` — static emergency fallback

## Current hosted-deployment gate

The curated Vercel build is `READY` and includes the full judge route set plus:

- `/api/graph/status`
- `/api/hydradb-v2/collections`
- `/api/hydradb-v2/query`

Before the Vercel URL is entered as the final judge link, two environment/access checks must pass:

1. Preview/production runtime must expose server-side `HYDRA_DB_API_KEY` and `HYDRADB_DATABASE=hydradg` to the deployment. No secret value is committed to GitHub.
2. The judge URL must be accessible without the submitter's Vercel login; Vercel Authentication must not block judges.

Only after an actual hosted HydraDB readback succeeds should the public UI claim `HYDRADB CONNECTED`.

## Licensing and custody

- HydraDG software/site/scripts/tooling: Apache-2.0 where declared.
- FCO/FCG research publications and designated Byron P. Lee / Biobitworks research content: CC BY-NC-ND 4.0.
- Third-party materials retain upstream rights.
- Hash identity is not correctness.
- Signature state is not promoted unless an authorized private-key signing operation actually occurred.
- Merkle/MMR commitment is not claimed unless actually performed.
