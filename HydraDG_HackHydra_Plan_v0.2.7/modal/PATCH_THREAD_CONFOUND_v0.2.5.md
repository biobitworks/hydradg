# v0.2.5 clean cross-SKU rerun patch

The completed quick matrix showed different PyTorch inter-op thread counts before
training: T4=17, L4=9, A10G=8.

Because FCO/FCG requires the earliest divergent dependency to be identified, the
cross-SKU final-state mismatch cannot yet be attributed solely to GPU architecture.

`modal_vithia_divergence_v4.py` explicitly executes:

```python
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
```

before model initialization and training.

Use v4 for the next 24-step/full experiment.

```bash
modal run modal/modal_vithia_divergence_v4.py
```

The new evidence goes to Modal Volume `hydradg-vithia-runs-v4`.

After completion:

```bash
modal volume get hydradg-vithia-runs-v4 /runs modal_runs_v4
python scripts/analyze_modal_receipts.py modal_runs_v4   --out eval/modal_full_analysis_v4.json   --seedgraph-out seedgraph/modal_full_v4
```
