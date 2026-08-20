# v0.2.6 phase-localized reproducibility run

The quick v3 receipts established:
- T4↔T4: no divergence across all recorded quick steps.
- reference T4↔perturbed T4: first recorded divergence exactly at declared perturbation step 2.
- cross-SKU pairs: first recorded divergence at step 0.

The v5 launcher improves the resolution of the experiment by recording:

`INITIAL_MODEL_STATE`
→ `INPUT_BATCH`
→ `PRE_STEP_MODEL_STATE`
→ `FORWARD_LOSS_FLOAT32`
→ `BACKWARD_GRADIENTS`
→ `POST_OPTIMIZER_MODEL_STATE`

Both PyTorch intra-op and inter-op thread pools remain pinned to 1.

Run:

```bash
modal run modal/modal_vithia_divergence_v5.py
modal volume get hydradg-vithia-runs-v5 /runs modal_runs_v5
python scripts/analyze_phase_divergence.py modal_runs_v5   --out eval/modal_phase_divergence_v5.json
```

This is designed to identify the earliest divergent computational phase, not merely
the earliest divergent training step.
