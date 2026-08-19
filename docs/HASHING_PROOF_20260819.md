# HydraDG hashing proof — 2026-08-19

Purpose: record a reproducible hashing procedure for Hack Hydra release artifacts. This document does not substitute hashing claims for signing or scientific verification.

## Reproducible SHA-256 command

macOS:

```bash
shasum -a 256 <file>
```

Portable Python:

```bash
python3 - <<'PY'
import hashlib
from pathlib import Path
p = Path("<file>")
print(hashlib.sha256(p.read_bytes()).hexdigest())
PY
```

Two independent implementations should return the same digest for identical bytes.

## Required artifact hashes

The release process should compute and retain SHA-256 for at least:

- `docs/PROJECT_FCG_UPDATE_20260819.md`
- `docs/WEBSITE_MVP_AND_FALLBACK_20260819.md`
- `apps/hydradg-web/public/backup/hydradg.html`
- current public-export receipt
- current release execution receipt
- final public repository export manifest
- final video file before upload when locally retained

The exact digests are populated from the retrieved repository bytes after each file is frozen. If any byte changes, the digest changes and the custody record must be updated rather than reusing an older value.

## Interpretation

```text
SHA256_MATCH = byte identity match
SHA256_MISMATCH = bytes differ somewhere
```

Neither state establishes correctness, originality, authorship, scientific validity, or independent verification.

## Signing boundary

A project signature requires an authorized project private key to sign a declared digest and a corresponding public key/key ID and verification receipt.

Until that operation occurs:

```text
SIGNATURE_STATE=NOT_SIGNED
```

Hashing an artifact is not signing it.
