# HydraDG Antigravity + Gemini E2E Verification Kit v1

This package is the handoff for running and verifying the HydraDG MVP end to end on
`magicSTUDIObox` using the currently approved Ollarma/Ollama-compatible local models:

- M1: `qwen2.5-coder:7b`
- M2: `qwen2.5:7b`

Tiny Qwen3 models are challenger candidates only and MUST pass an admission canary before
they can become the default analyst.

## What "end to end" means here

1. preserve/reconcile Git lineage without hard-resetting either scientific or Release Watch work;
2. locate canonical FCO/FCG specs and custody store;
3. verify the LongMemEval source identity/freeze;
4. verify total-atomization / canonical FCO-FCG / HydraDB receipts already established;
5. verify HydraDB and Best-Use local services;
6. verify the Context Iceberg APIs and live read-only projection;
7. verify both approved local models exist;
8. run structured-output smoke/replay tests for both approved models;
9. verify model prompt/response/config hashes;
10. verify Iceberg math and corrected claim language;
11. typecheck/build the local Next.js site;
12. run the local release batch if and only if the local branch/custody gates allow it;
13. produce a machine-readable E2E receipt;
14. append that receipt/turn to the canonical project FCG;
15. create an Ed25519 signing handoff when the authorized private key is not available.

## Scientific guardrails

- `CloudDrift = 100 × JSD` remains a deterministic distributional diagnostic.
- `ΔG*` is a dimensionless information-system abstraction, not physical Gibbs free energy.
- K5→K10 aggregate deltas are DESCRIPTIVE. They do not by themselves reject `H0_GA`.
- 100% exact model agreement is reportable; Cohen's kappa is only reportable when it is
  mathematically defined/informative given category variation.
- Model explanations are `PROBABILISTIC_MODEL_OUTPUT_ONLY`.
- Model superiority is not established until prospective held-out predictions are scored.
- Candidate next held-out run is K15 only after the prior prediction root and preregistration
  are frozen/verified.
- Structural Cloud Drift and Retrieval Cloud Drift are separate diagnostics.

## Start

Give both agents:

`prompts/ANTIGRAVITY_GEMINI_E2E_MASTER_PROMPT.md`

Then on `magicSTUDIObox`:

```bash
cd /path/to/this/package
./scripts/run_e2e.sh --verify
```

After branch reconciliation and scientific-state review:

```bash
./scripts/run_e2e.sh --full
```

To test the harness without HydraDG/Ollama:

```bash
./scripts/run_e2e.sh --mock
```

A `PASS` from `--mock` validates this package's orchestration/math/parser logic only.
It does not validate the real HydraDG stack.
