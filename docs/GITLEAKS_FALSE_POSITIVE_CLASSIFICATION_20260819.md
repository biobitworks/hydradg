# HydraDG Full-History Gitleaks Classification — 2026-08-19

## Scope

This record classifies the findings from the fail-closed full-history Gitleaks run over the PR #19 merge candidate.

- Workflow run: `32327357514`
- Scanned commits: `419`
- Approximate bytes scanned: `301,379,026`
- Gitleaks version: `v8.28.0`
- Docker image digest observed by the workflow: `sha256:cdbb7c955abce02001a9f6c9f602fb195b7fadc1e812065883f695d1eeaba854`
- Initial findings: `18,608`
- Initial rule IDs: `generic-api-key` only
- Redacted report artifact ID: `9391964005`
- Uploaded artifact ZIP SHA-256 reported by GitHub Actions: `e475b96a6fbfe9ae1b0b925ce0bc1399c02b34ed563ea3adbec192ec8cb26119`

The redacted report was classified by rule, path, match form, and source role. Raw credential values are not reproduced in this document.

## Classification

| Class | Count | Classification basis |
|---|---:|---|
| SeedGraph deterministic `cache_key` SHA-256 values | 18,428 | Every finding is on the `cache_key` field in the content-addressed Track 03 SeedGraph cache; inspected sample shows a 64-hex deterministic cache identifier and separate `source_sha256`. |
| Deliberately public toy-signature objects | 124 | The package policy explicitly states that the toy Ed25519 private key is intentionally distributed and provides reproducible mechanics only, with claim ceiling `TOY_DRM_FREE_SIGNATURE_MECHANISM_ONLY_NO_AUTHENTICITY`. |
| Vendored upstream Transformers/Numpy source identifiers | 53 | Generic-key heuristic fires on source identifiers/forms including `AutoTokenizer`, `key_sha256`, `key_layer`, `num_keypoints_0`, `new_num_tokens`, and `key.dtype`; these are constrained to the vendored dependency tree. |
| Upstream Transformers staging test token fixture | 1 | `transformers/testing_utils.py` contains the same staging-only test token in the upstream Hugging Face Transformers source, explicitly described upstream as non-critical and sandboxed-CI-only. |
| Historical SHA-256 manifest entry | 1 | `LOW_TOKEN_POLICY.json` is the manifest key; the detected value is a 64-hex SHA-256 checksum. |
| Historical Modal API token identifier | 1 | The historical log prints an `ak-...` API token ID. Modal documents API token IDs with `ak-` and API token secrets with distinct `as-` prefixes. No `as-...` value is allowlisted by the release policy. |
| **Total** | **18,608** |  |

## Allowlist design

The release configuration does **not** disable the `generic-api-key` rule.

Each exemption is constrained by:

1. `targetRules = ["generic-api-key"]`;
2. an exact/narrow path expression;
3. a content/match expression; and
4. `condition = "AND"`.

The policy intentionally does not allowlist generic `token`, `secret`, API-key, `.env`, or credential paths globally.

The Modal exemption accepts only the documented `ak-` identifier form in one historical log. It does not accept the `as-` secret prefix.

The toy-key exemption covers only the named historical toy-seal artifact files whose own policy states that the key is deliberately public and non-authenticating. It does not cover the real HydraDG project signing key.

## Claim ceiling

This classification supports only:

```text
GITLEAKS_FINDING_CLASSIFICATION_AND_NARROW_FALSE_POSITIVE_POLICY
```

It does not establish `GITLEAKS_RELEASE=PASS`. That state requires a fresh full-history Gitleaks execution using the admitted configuration and a zero-finding/zero-exit result.

It does not establish that any external account credential has been rotated, that the project is signed, that the project is Merkle/MMR committed, or that scientific claims are verified.
