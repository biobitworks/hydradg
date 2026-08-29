# NewInML Requirement Drift Case Study

**Mode:** POST_V3 evidence reconciliation  
**Green submission HEAD (immutable):** `cfee4ee7a6a8c418f9c71a37ca96031518d895bc`  
**V3 PDF SHA256 (unchanged):** `0b096ccec7c6c1a630e4308abacea89a59620e410bfaff705409ce884a93c1ad`

## Purpose

Demonstrate that submission requirements are temporal, source-bound evidence objects.
Byte identity (SHA-256) is necessary but insufficient without freshness and supersession.

## Key finding

Earliest divergence: `STALE_OR_INCORRECT_SOURCE_STATE_PROMOTED_AS_CURRENT_REQUIREMENT`

- Transform math: `CORRECT_GIVEN_INPUT`
- Input freshness: `FAILED`
- Earlier `2026-08-29T08:59:00Z` derivation: `SUPERSEDED_INCORRECT_SOURCE_INPUT`
- Active operational deadline: `2026-08-30T07:59:00Z` (OpenReview human transcription)

## Artifacts

| File | Role |
|------|------|
| `SOURCE_UNIVERSE.jsonl` | All sources with hashes and freshness |
| `SEEDGRAPH_TRIAGE_RECEIPT.json` | Router + import outcomes |
| `NEWINML_REQUIREMENT_DRIFT_FCO_MANIFEST.jsonl` | FCO objects |
| `NEWINML_REQUIREMENT_DRIFT_FCG.jsonl` | Derivation/supersession edges |
| `DEADLINE_DIVERGENCE_ANALYSIS.json` | Mechanical divergence analysis |
| `REQUIREMENT_DRIFT_SEAL.json` | Hash-frozen packet root |
| `tests/test_requirement_freshness.py` | Regression test |

## Claim boundary

**Allowed:** Requirements change; provenance + temporal validity + supersession matter.  
**Not allowed:** "HydraDG prevented this failure."

## Rebuild

```bash
python3 scripts/newinml_requirement_drift_build.py
python3 paper/newinml2026_solo/requirement_drift/tests/test_requirement_freshness.py
```
