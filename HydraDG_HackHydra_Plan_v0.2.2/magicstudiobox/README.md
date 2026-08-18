# magicstudiobox execution lane

## Current access state

No verified SSH endpoint, private API endpoint, Ollama URL, or `ollarma` remote-control endpoint
is available to this ChatGPT runtime. Therefore no remote training run has been launched.

## Ollama versus training

Ollama is appropriate for model inference/evaluation. Its local API normally listens on
`http://localhost:11434`. The Vithia/Pythia training experiment should run through Python/PyTorch
(or a local MLX training implementation), not through Ollama itself.

`ollarma` is treated as the project's gated local-model harness. No public network endpoint is
assumed.

## Local run commands

From this package root on magicstudiobox:

```bash
python3 -m venv .venv-hydradg
source .venv-hydradg/bin/activate
pip install torch transformers numpy
export PYTHONHASHSEED=314159
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

python scripts/vithia_divergence_core.py \
  --run-id magic_cpu_1t_a \
  --outdir runs/magic

python scripts/vithia_divergence_core.py \
  --run-id magic_cpu_1t_b \
  --outdir runs/magic
```

For the thread/concurrency perturbation, launch fresh processes with different thread settings:

```bash
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 \
python scripts/vithia_divergence_core.py \
  --run-id magic_cpu_4t \
  --outdir runs/magic
```

On Apple Silicon, record `system_profiler`, macOS version, PyTorch version and MPS availability.
A future MPS adapter should explicitly select MPS rather than silently falling back to CPU.

## Secure remote access

Do not bind unauthenticated Ollama directly to a public interface. If remote evaluation is needed,
put it behind a private network or authenticated reverse-proxy boundary and retain the endpoint
configuration as a private FCO.
