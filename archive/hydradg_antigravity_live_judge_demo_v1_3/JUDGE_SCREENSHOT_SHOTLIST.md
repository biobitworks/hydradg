# Judge screenshot shot list

1. `01-live-context-iceberg.png`
   Homepage; rotated 4D graph, live badge, FCG/HydraDB roots.
   MUST visibly include: ΔG*, Cloud Drift, Hit@K, Recall@K, ΔHit@K, ΔRecall@K.

2. `02-reference-poison-antidote.png`
   Judge Lab; retained history.

3. `03-track03-results.png`
   Actual full500 result and negative/null retention.
   MUST visibly include the selected comparison's absolute Hit@K and Recall@K plus
   ΔHit@K and ΔRecall@K. Label K explicitly.

4. `04-fco-live-lineage.png`
   Selected FCO in live graph with readback/provenance.

5. `05-fco-provenance.png`
   FCO → source → transformation → claim ceiling.

6. `06-local-model-advisory.png`
   Approved local model, probabilistic-output label, hashes.

7. `07-custody-eligibility.png`
   FCG root, signature/Merkle/push state.

Primary screenshots must come from the live Next.js app, not `/backup/hydradg.html`.


## Metric screenshot rule

At least one screenshot must make all six values legible at the same time:

- ΔG*
- Cloud Drift
- Hit@K
- Recall@K
- ΔHit@K
- ΔRecall@K

If Retrieval Cloud Drift is available, include it as a seventh value.

Use `Hit@K` rather than an unqualified `Accuracy` label unless the UI explicitly says
`Accuracy proxy: Hit@K`.


## Navigation screenshots

Also capture:
- `07-static-fallback.png` with static badge and `Return to Live Demo`
- `08-return-live.png` after clicking back to `/`

The final screenshot set must prove both directions:
`LIVE → STATIC`
and
`STATIC → LIVE`.

At least one live screenshot must show the persistent navigation bar and active-route highlight.


9. `09-knowledge-base.png`
   `/knowledge`; show declared terms and at least one term with FCO/source/claim-ceiling linkage.

10. `10-how-to-use.png`
    `/how-to`; show the judge/operator step-by-step flow and links back to live demo.
