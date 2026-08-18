# Modal execution

## Authentication boundary

Run this on a machine you control:

```bash
python3 -m pip install -U modal
python3 -m modal setup
modal token info
```

`modal setup` authenticates through a web session and stores a local Modal profile.
Do not paste Modal token secrets into the project repository or public chat.

## First run

From the package root:

```bash
modal run modal/modal_vithia_divergence.py
```

The default bounded matrix requests:

- T4 reference A
- T4 reference B in a fresh single-use container
- L4
- A10
- T4 controlled perturbation

The run receipt records actual `nvidia-smi` UUID/name/driver metadata. Only call two runs
"two different physical GPUs" if those receipts establish that fact.

## Cost posture

This is a ~14M-parameter, 24-step fixture. It is designed to consume minutes, not hours.
Use Modal workspace/environment budgets as an additional guard. Increase steps only after
the smoke matrix is frozen.

## Later expansion

1. repeat each GPU type N=5;
2. compare within-GPU-type versus cross-GPU-type divergence;
3. replace synthetic batches with the frozen Vithia corpus adapter;
4. save aligned intermediate gradients/activations at selected steps;
5. ingest receipts into HydraDB.
