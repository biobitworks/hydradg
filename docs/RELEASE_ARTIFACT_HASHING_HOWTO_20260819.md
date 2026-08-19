# Release artifact hashing how-to — 2026-08-19

From the release branch root:

```bash
python3 scripts/hash_release_artifacts.py
```

Expected outputs:

```text
docs/RELEASE_ARTIFACT_SHA256_20260819.json
HASH_MANIFEST_SHA256=<64 hex characters>
```

Then independently recompute one entry with macOS `shasum`:

```bash
shasum -a 256 docs/PROJECT_FCG_UPDATE_20260819.md
```

and compare it to the corresponding JSON entry:

```bash
jq -r '.artifacts[] | select(.path=="docs/PROJECT_FCG_UPDATE_20260819.md") | .sha256' \
  docs/RELEASE_ARTIFACT_SHA256_20260819.json
```

The two 64-hex digests must be exactly equal.

For the static fallback:

```bash
shasum -a 256 apps/hydradg-web/public/backup/hydradg.html
jq -r '.artifacts[] | select(.path=="apps/hydradg-web/public/backup/hydradg.html") | .sha256' \
  docs/RELEASE_ARTIFACT_SHA256_20260819.json
```

Again, equality establishes identical bytes under SHA-256 only.

Do not use the word `signed` unless the project signing process actually signs a declared digest and a verification receipt exists.
