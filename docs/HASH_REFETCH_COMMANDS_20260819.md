# Repository refetch hash verification commands — 2026-08-19

After syncing the release branch locally, verify the retained repository bytes against the in-runtime write-payload hashes:

```bash
cd /Users/byron/projects/active/hydradg
git fetch origin
git switch hack-hydra/submission-eligible-20260819
git pull --ff-only origin hack-hydra/submission-eligible-20260819

shasum -a 256 docs/WHY_FCG_UPDATED_20260819.md
shasum -a 256 docs/PROJECT_FCG_CHANGELOG_20260819.json
```

Expected if the repository bytes equal the exact write payloads:

```text
7735f1198ac5834aca6312de719a9d0ca666bd60816d5560aeebd13968ffc05b  docs/WHY_FCG_UPDATED_20260819.md
886731d5fb0ae6a05de307a102cef1207b032fc945d298c91fcebe8f4ab5a719  docs/PROJECT_FCG_CHANGELOG_20260819.json
```

Then generate the complete artifact hash manifest:

```bash
python3 scripts/hash_release_artifacts.py
```
