# HydraDG Daisy Train v0.3.1

Status: `EXECUTION_READY_WITH_EXTERNAL_ASSET_GATES`

Purpose: prepare a bounded Hack Hydra Track 03 evidence package that combines four independent lanes:

1. `ECA-EXT80` — new deterministic cellular-automata perturbation/recovery conformance run.
2. `XenoDisorder-CAFA6` — same-frozen-assets local -> Modal replay, gated on exact historical assets and an explicit run contract.
3. `Vithia/Pythia` — import existing Modal replay/divergence evidence; do not rerun it merely to make a new package.
4. `LongMemEval-S` — Track 03-facing memory evaluation: deterministic smoke80 during development, then all 500 cases after the HydraDB graph/query path is frozen.

The Daisy Train is an execution order. The scientific FCG remains a DAG: ECA, XenoDisorder, and Vithia are independent evidence lanes that merge only at FCO/FCG normalization and HydraDB ingestion.

## Hard evidence boundaries

- A SHA-256 digest proves content identity for the hashed bytes; it does not prove correctness.
- Daisy stage receipts are a hash-linked application chain. They are NOT an MMR and NOT a signature.
- This package does not claim an MMR root, signature, independent replication, or HydraDB benchmark result.
- XenoDisorder is not called a historical reproduction unless the historical evaluator, checkpoint, table, and command contract are all pinned and matched.
- ECA-EXT80 is a NEW conformance extension, not a reconstruction of the historical three-arm ECA detector.
- LongMemEval scores are never combined with ECA/Xeno/Vithia denominators.
- HydraDB API calls are not fabricated here. Pin the HydraDB repository/API revision before implementing the adapter in `hydra/`.

## First command

```bash
shasum -a 256 -c SHA256SUMS.txt
python scripts/verify_package.py
```

Then follow `RUNBOOK_MAGICPROBOX_MODAL.md`.
