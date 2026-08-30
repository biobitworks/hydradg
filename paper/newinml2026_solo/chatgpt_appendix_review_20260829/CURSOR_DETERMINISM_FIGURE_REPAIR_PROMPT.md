# Cursor follow-up — repair publication determinism and complete requested appendix figures

Work on the SOLO HydraDG/NewInML lineage only. Do not import Protein Hinge TEAM evidence.

Start by reading:

- `paper/newinml2026_solo/chatgpt_appendix_review_20260829/DETERMINISM_AND_FIGURE_COMPLETENESS_AUDIT.md`
- `FIGURE_REQUIREMENTS_LEDGER.tsv`
- `DETERMINISTIC_ARTIFACT_GATE_SPEC.md`
- the existing deterministic figure/SeedGraph round-trip protocol already present in project history/repo if available.

## Required correction

Do not report `FIGURES_DETERMINISTIC=PASS` or `TABLES_DETERMINISTIC=PASS` from artifact counts.

Independently inspect `scripts/build_successor_recovery.py`, `scripts/reproduce_newinml.py`, `statistics/run_statistics.py`, figure receipts, tables, manuscript, appendix, and exact source receipts.

### 1. Repair empirical figure generation

Remove hard-coded scientific values from renderers.

At minimum repair:

- FIG-002: load parse rates and uncertainty from admitted verdict/statistics outputs;
- FIG-003: calculate terminal-state counts from a repaired authoritative experiment ledger;
- FIG-004: load perturbation, tamper, concurrency, replay and provider data from their exact receipts; declare every source used;
- FIG-006: load context-classification counts from the exact source JSON;
- FIG-007: use the actual R1, R2 and R3 roots and visibly/cryptographically verify equality.

Conceptual figure labels may be stable governed text, but must be separated from empirical values.

### 2. Repair experiment ledger provenance

For each historical experiment record actual experiment/source Git SHA or explicit UNKNOWN, not the current build branch SHA.
Bind the row to the authoritative terminal/preregistration source rather than an arbitrary first JSON in a directory.

### 3. Add figure/table receipts

Every distributed SVG/PNG/PDF/table derivative gets SHA-256.
Every receipt includes all source SHA-256s, generator SHA-256, environment root, exact command and claim ceiling.

### 4. R1/R2/R3 clean build

Run statistics, figures and tables independently in R1/R2/R3 clean output roots.
Require identical canonical scientific roots.
Prefer canonical SVG for vector figures. Normalize PDF metadata/timestamps and test byte equality. If a derivative cannot be byte-identical, label it noncanonical and retain a deterministic canonical source; do not silently call it deterministic.

Pin exact package versions and rendering backend/font dependencies.

### 5. Strengthen verifier

`python3 scripts/reproduce_newinml.py --verify` (or successor) must regenerate and compare outputs, not just count files.
Fail closed on source hash mismatch, missing receipt, hard-coded empirical value, R1/R2/R3 mismatch or missing derivative hash.

### 6. Complete the requested appendix figure set

Use the exact `FIGURE_REQUIREMENTS_LEDGER.tsv` as the completeness contract.
Priority figures:

- GettingScienceDone / Mechanical Scientific Method workflow (Appendix E);
- governed federation + ML complement architecture (E);
- canonical Anticube 2x2 (F);
- Anticube 3D trajectory X/Y/Z with Delta-G separate and NOT_COMPUTED where absent (F);
- FCO/FCG evidence-to-claim graph + FCO mechanism experiment summary (G);
- SeedGraph hierarchy and reverse-trace figure (H);
- HydraLamp systems/failure validation panels (D);
- corrected terminal-state/failure accounting (C/A);
- cross-domain evidence-tier map (I);
- claim/value -> source/hash reverse trace (P);
- submission/package custody manifest (Q).

Do not add Context Iceberg/Delta-G quantitative panels unless actual computed source values support them.

### 7. Figure text/source round trip

For the main deterministic evidence figure and all figures with scientific labels/numbers, implement the existing figure-evidence protocol:

visible element -> FigureText/data object -> FCO/FCG path -> source pointer -> exact source bytes

and reverse.

SVG text should be machine-addressable; no OCR is needed.

### 8. Table repair

T2 can remain sourced from deterministic stats after independent validation.
T3 must inherit repaired ledger provenance.
T4 must be generated from HydraLamp receipts.
T7 cannot say figures deterministic until the figure R1/R2/R3 gate passes.
T9 must derive claim ceilings from authoritative governance/claim artifacts.
Create `TABLE_RECEIPTS.json` or canonical equivalent.

### 9. Manuscript/appendix integration

The current main paper includes only the primary parse-validity figure and the appendix has only a simple text-box custody figure. Update the anonymous appendix/supplement so requested verified figures are actually included, subject to the NewInML page-limit/supplement rules.

Keep main text 2–8 content pages excluding references; do not assume long appendices are free under workshop-specific wording.

### 10. Correct stale non-figure statements discovered by this audit

Fresh-check and repair at minimum:

- software/research-content license split;
- any statement claiming OpenReview itself universally requires CC BY 4.0;
- HydraLamp name/IP risk language if present;
- any branch/source inventory that still marks verified related implementations UNKNOWN.

### 11. Final report

Return:

SOURCE_BRANCH=
SOURCE_SHA=
SUCCESSOR_BRANCH=
SUCCESSOR_SHA=

STATISTICS_R123=
FIGURES_R123=
TABLES_R123=
PDF_DERIVATIVE_R123=

FIGURE_COUNT=
REQUESTED_FIGURES_ADMITTED=
REQUESTED_FIGURES_BLOCKED=
FIGURE_COVERAGE=

TABLE_COUNT=
TABLE_SOURCE_COVERAGE=

NUMERIC_VALUE_REVERSE_TRACE_COVERAGE=
SOURCE_HASH_RECOMPUTE_GATE=
DERIVATIVE_HASH_COVERAGE=

MAIN_CONTENT_PAGES=
ANONYMITY_GATE=
LICENSE_GATE=
PROTEIN_HINGE_PRIMARY_ADMISSION_COUNT=

CURRENT_BRANCH=
CURRENT_SHA=
EVIDENCE_STATE=
EXPERIMENT_STATE=
FCO_STATE=
FCG_STATE=
HYDRADB_STATE=
EARLIEST_DIVERGENCE=
CLAIM_CEILING=
SIGNATURE_STATE=
MERKLE_MMR_STATE=
NEXT_SAFE_ACTION=
FINAL_REVIEW_GATE=
