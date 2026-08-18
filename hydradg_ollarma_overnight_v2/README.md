# HydraDG Ollarma Overnight Daisy v2

This revision fixes the SSH preflight failure mode from v1.

Changes:
- Ollarma is explicitly addressed on `magicstudiobox` loopback (`127.0.0.1:8484`).
- The launcher no longer uses `curl -f` for Ollarma `/health`; degraded non-2xx JSON health is preserved as reachable, matching the semantics of Ollarma's zero-dependency client.
- Each remote preflight gate prints its own PASS/FAIL result.
- Ollama (`127.0.0.1:11434/api/tags`) is checked separately and installed model names are shown without secrets.
- The orchestrator prefers an installed `ollarma_client.py` but has a zero-dependency embedded localhost HTTP fallback.
- The background queue remains sequential: train -> write/hash receipt -> Ollarma local annotation -> next train.
- Existing completed run receipts are preserved with `--resume`.

Execution remains local to magicstudiobox; this package does not expose Ollama/Ollarma publicly.
