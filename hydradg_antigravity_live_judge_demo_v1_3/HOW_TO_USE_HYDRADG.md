# How to Use HydraDG — Judge & Operator Guide v1

## 1. Start at Overview

Open:
`/`

What to do:
- drag the Context Iceberg to rotate;
- use the mouse wheel to zoom;
- use the time slider to move across states;
- click a node to inspect it;
- point to Hit@K / Recall@K separately from ΔG* / Cloud Drift.

What it proves:
- the visible graph is interactive;
- state changes are navigable;
- empirical retrieval outcomes are separate from information-state diagnostics.

## 2. Run the Judge Demo

Click:
`Start Judge Walkthrough`

Route:
`/judge`

What to do:
- click Reference;
- click Poison;
- click Antidote.

What it proves:
- prior state is retained;
- perturbation is not overwritten;
- restoration is represented as a new governed state.

## 3. Inspect the Executed Result

Click:
`See Executed Result`

Route:
`/track03`

What to inspect:
- cases;
- sessions;
- entities;
- facts;
- Hit@K;
- Recall@K;
- ΔHit@K;
- ΔRecall@K;
- null/negative interpretation.

What it proves:
- HydraDG keeps the actual outcome even when it is not a win.

## 4. Trace an FCO

Click:
`Trace One Result`

Route:
`/graph`

What to do:
- click the highlighted FCO;
- inspect ID, type, relationships, claim ceiling;
- inspect FCG root and HydraDB projection/readback state.

Then click:
`Open Full FCO`

## 5. Read the provenance

Route:
`/fco/<id>`

Trace:

source
→ transformation
→ derived evidence
→ claim
→ artifact

Check:
- SHA-256 identity;
- evidence class;
- claim ceiling;
- current/superseded relationships;
- signature/Merkle states.

## 6. Use the Knowledge Base

Click:
`Knowledge`

Route:
`/knowledge`

Use it when:
- a judge does not know a term;
- you need to explain FCO/FCG;
- you need to distinguish Cloud Drift from ΔG*;
- you need to explain Hit@K vs Recall@K;
- you need to show what Track 01/02/03 mean.

Every term should link back to its relevant FCO/source where possible.

## 7. Check release/custody state

Click:
`Eligibility`

Route:
`/eligibility`

Show:
- current Git commit;
- project FCG root;
- hash state;
- signature state;
- Merkle/MMR state;
- push state;
- public/live/static state.

## 8. Switch to the fallback

Click:
`Open Static Fallback`

Route:
`/backup/hydradg.html`

State clearly:
`STATIC FALLBACK — NOT LIVE HYDRADB`

Use only if:
- live Next.js fails;
- local service fails;
- judge needs a portable offline artifact.

Then click:
`Return to Live Demo`

## 9. Local model advisory

If available, use:
- `/api/local-model/status`
- `/api/local-model/explain`

The model output must remain:
`PROBABILISTIC_MODEL_OUTPUT_ONLY`

It may explain evidence but must not promote claims or mutate scientific state.

## 10. What not to say

Do not say:
- lower ΔG* causes better recall;
- Hit@K is end-to-end QA accuracy;
- null results are failures;
- the toy DRM-free key proves authenticity;
- signed/Merkle committed unless receipts establish it.

## Operator close

The operator should be able to complete the full judge flow without typing another URL after opening `/`.
