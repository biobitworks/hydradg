# Verification Instructions

## 1. Unpack

Unzip the anonymous reviewer artifact to a local directory.

## 2. Run verifier

```bash
python3 verify_submission.py
```

## 3. Expected gates

| Gate | Meaning |
|------|---------|
| `BYTE_HASH_GATE` | Every listed file matches its SHA-256 |
| `FCO_MANIFEST_GATE` | Manifest objects are well-formed |
| `FCG_EDGE_GATE` | Derivation edges present |
| `PDF_HASH_GATE` | PDF hash bound in manifest |
| `TABLE_PROVENANCE_GATE` | Table LaTeX reflects source JSON |

## 4. Inspect root

Open `PUBLIC_SUBMISSION_ROOT.json` and confirm:

- `SEAL_MODE` = `DRM_FREE_CONTENT_ADDRESSABLE`
- `SEAL_STATE` = `HASH_FROZEN`
- `SIGNATURE_STATE` = `NOT_SIGNED` (unless a real signing operation occurred)
- `MERKLE_MMR_STATE` = `NOT_COMMITTED` (unless canonical MMR receipt exists)

## 5. Optional table regeneration

Compare `tables/TABLE_001_TERMINAL_SOURCE.json` row values with `tables/TABLE_001_TERMINAL.tex`.

## 6. What verification establishes

Passing verification establishes **byte identity** and **declared derivation consistency**.

It does **not** independently establish:

- scientific truth
- causal validity
- model correctness
- digital signature
- author identity

unless corresponding evidence exists outside this bundle.

## Seal / unseal semantics

**SEAL** = canonicalize bytes → hash each object → record FCO identity → record FCG edges → freeze public root → verify listed bytes.

**UNSEAL** = read manifest → recompute hashes → verify graph references → confirm PDF hash.

No decryption is involved. Ordinary local tooling suffices; no internet required.
