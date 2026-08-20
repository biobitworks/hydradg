# HydraDB Experiment: Context vs. Entropy Secret Classification

## Summary Metrics

| Metric | Count | Percentage |
| :--- | :---: | :---: |
| **RAW_FINDINGS** | `18,567` | `100.00%` |
| **CONTEXT_CLASSIFIED_FINDINGS** | `18,555` | `99.94%` |
| **UNEXPLAINED_SECRET_CANDIDATES** | `12` | `0.06%` |
| **HISTORICAL_REVOKED_CREDENTIALS** | `1` | `--` |

### Classification Breakdown

- **`DETERMINISTIC_HASH`**: `18,428` findings (Content-addressed SeedGraph SHA-256 cache files)
- **`TOY_NON_AUTHENTICATING_KEY`**: `126` findings (Intentionally public DRM-free toy signature keys)
- **`VENDORED_TEST_FIXTURE`**: `0` findings (Upstream HuggingFace test fixtures)
- **`REVOKED_HISTORICAL_CREDENTIAL`**: `1` findings (Historical Modal `ak-*` token ID, `USER_ATTESTED_REVOKED`)

---

## Architectural Comparison

```
Raw Pattern/Entropy Detector (Gitleaks)
          ↓
  18,567 High-Entropy Flags
          ↓
  HydraDB Context Graph (Path, FCO/FCG Provenance, Object Type)
          ↓
  Deterministic Reviewed Classifications (99.9% Resolved, 0.01% Abstentions)
```

---

## Claim Boundaries
- Demonstrates provenance-aware false-positive disambiguation without global key allowlisting.
- Modal item classified as `REVOKED_HISTORICAL_CREDENTIAL` with evidence basis `USER_ATTESTED_REVOKED`.
