# Release next commands — 2026-08-19

On magicSTUDIObox after syncing the release branch:

```bash
python3 scripts/check_term_knowledge_coverage.py
python3 scripts/check_static_fallback.py
python3 scripts/hash_release_artifacts.py
bash scripts/run_hackhydra_release_batches_magicstudio.sh
```

Do not promote the live or static release state beyond the actual receipts from these commands.
