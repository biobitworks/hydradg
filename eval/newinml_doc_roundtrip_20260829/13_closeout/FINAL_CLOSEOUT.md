# FINAL_CLOSEOUT — NEWINML-DOC-ROUNDTRIP-001

## Deterministic core: GREEN

- **H-D1:** `PASS_EXACT` (10 cold runs, 1 unique structural hash)
- **H-D2:** `PASS_EXACT` (0 content/occurrence loss)

## Statistical semantic lane: NOT POSITIVE

- **H-S1:** `NO_SIGNIFICANT_DIFFERENCE` (N=12, both conditions 0% correct)
- **H-S2:** `NOT_COMPUTED`

## Protein Hinge transfer: PARTIAL

- Structural decomposition exact (3 cold runs)
- Biological mechanism **not** claimed

## Paper promotion allowed

- `DETERMINISTIC_DOCUMENT_DECOMPOSITION`
- `EXACT_SEEDGRAPH_ROUNDTRIP` (structural manifest level)
- `FAILURE/ABSTENTION/CONTRADICTION_PRESERVATION` (synthetic canaries)

## Paper promotion NOT allowed without further work

- `STRUCTURED_SEMANTIC_COMPOSITION_ADVANTAGE`
- `PROTEIN_HINGE_MECHANISM_VALIDATED`
