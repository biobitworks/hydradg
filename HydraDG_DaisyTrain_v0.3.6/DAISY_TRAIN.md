# FCO/FCG Daisy Train

This is an **execution train**, not a claim that scientific dependencies are linear.
The FCG remains a DAG.

```text
CAR 0 — Authority freeze
  source paths / commits / hashes / claim ceilings
       |
       +--> CAR 1A — historical FCO ECA source recovery only
       |
       +--> CAR 1B — NEW ECA-EXT80 Modal conformance
       |
       +--> CAR 2  — XenoDisorder frozen-assets local -> Modal replay
       |
       +--> CAR 3  — import existing Vithia/Pythia Modal evidence
                         |
                         v
CAR 4 — Normalize each lane into FCO objects + typed FCG edges
                         |
                         v
CAR 5 — Pin HydraDB commit/API, then ingest
                         |
                         v
CAR 6 — LongMemEval-S smoke80
                         |
                         v
CAR 7 — LongMemEval-S full500 + separate injected perturbation/recovery suite
                         |
                         v
CAR 8 — A-D ablations + scorecard + figures + three-minute demo
```

## Receipt rule

Every executed car emits a `daisy_stage_receipt` with:
- stage id
- input artifact hashes
- output artifact hashes
- environment note
- parent receipt hash
- claim ceiling
- execution state

The receipt chain establishes application-level lineage/order for the receipt bytes.
It is:
- `HASH_LINKED`
- `NOT_SIGNED`
- `NOT_MERKLE_COMMITTED`

## Merge semantics

ECA, XenoDisorder, and Vithia/Pythia do not scientifically depend on one another.
Their outputs become parents of the normalization/ingest stage. This avoids inventing a
scientific dependency merely because the jobs were executed in sequence.
