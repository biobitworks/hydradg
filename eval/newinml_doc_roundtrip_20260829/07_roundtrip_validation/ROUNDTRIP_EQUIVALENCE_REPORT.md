# ROUNDTRIP_EQUIVALENCE_REPORT — NEWINML-DOC-ROUNDTRIP-001

**Verdict:** `ROUNDTRIP_EXACT_PASS` / `H_D2=PASS_EXACT`

## Pre/post comparison

| Invariant | Pre | Post | Loss |
|---|---|---|---|
| Structural objects | 175 | 175 | 0 |
| Content IDs | 175 unique | 175 unique | 0 |
| Occurrence IDs | 175 unique | 175 unique | 0 |
| Provenance edges | — | — | 0 |
| Contradiction edges | — | — | 0 |
| Abstention states | — | — | 0 |
| Terminal states | 8 synthetic | 8 synthetic | 0 |

## Method

Independent readback reconstruction via cold deterministic decomposer (10/10 hash identity on structural manifest). Pre-ingest and post-readback manifests compared on sorted canonical keys.

## Claim ceiling

`DETERMINISTIC_STRUCTURAL_ROUNDTRIP` — does not establish semantic composition advantage.
