# Anonymous Reviewer Verification Bundle

This package provides DRM-free, hash-frozen verification of the anonymous NewInML submission artifacts.

**Seal mode:** content-addressable hashing only. No encryption, no secret keys, no access control.

## Contents

- `paper/main.pdf` — submission PDF
- `paper/main.tex` — manuscript source
- `tables/` — deterministic table source and rendered LaTeX
- `evidence/` — public-safe derived systems-validation records
- `references/PUBLIC_REFERENCE_LEDGER.jsonl` — external scholarly references
- `PUBLIC_SUBMISSION_FCO_MANIFEST.jsonl` — typed object manifest
- `PUBLIC_SUBMISSION_FCG.jsonl` — derivation edges
- `PUBLIC_SUBMISSION_ROOT.json` — hash-frozen submission root
- `verify_submission.py` — local verifier (Python 3, stdlib only)
- `VERIFY.md` — step-by-step instructions
- `SHA256SUMS.txt` — per-file checksums

## Quick verify

```bash
python3 verify_submission.py
```

Expected: all gates `PASS`.
