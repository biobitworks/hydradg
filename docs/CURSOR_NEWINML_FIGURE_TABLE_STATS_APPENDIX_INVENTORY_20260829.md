# HydraDG NewInML — Figure/Table/Statistics/Citation/Appendix Inventory Gate

Date: 2026-08-29

Execution host: `magicSTUDIObox.local`

This is an addendum to:

- `docs/CURSOR_TERMINOLOGY_SEEDGRAPH_ANTICUBE_MASTER_PROMPT_20260829.md`

It does not replace the master prompt. It adds a mandatory submission-artifact inventory and appendix/reference gate.

## 0. Core rule

Before changing the manuscript, mechanically inventory **everything already present** and **everything supported by current evidence but not yet represented**.

Do not add a figure/table/statistic merely because space is available.

Every item must be classified as one of:

- `ADMITTED_MAIN`
- `ADMITTED_APPENDIX`
- `REFERENCE_ONLY`
- `PLANNED_NOT_EXECUTED`
- `DEFERRED_NOT_NEEDED`
- `BLOCKED_MISSING_EVIDENCE`
- `OMITTED_CLAIM_CEILING`

The latest direct-human workshop guidance says the main paper must remain within 8 pages and that references/appendix do not consume that main-content budget. Preserve that guidance as a RequirementFCO and still re-check the exact current NeurIPS/NewInML template/order before final build.

The checklist remains required under the current audit and must remain outside the main-content count.

## 1. Recompute the current manuscript inventory

Inspect the exact selected/successor manuscript, not a stale copy.

Create:

```text
paper/newinml2026_solo/final_inventory/
  SUBMISSION_ARTIFACT_INVENTORY.json
  SUBMISSION_ARTIFACT_INVENTORY.md
  FIGURE_INVENTORY.jsonl
  TABLE_INVENTORY.jsonl
  STATISTICAL_ANALYSIS_INVENTORY.jsonl
  COMPARISON_INVENTORY.jsonl
  CITATION_REFERENCE_INVENTORY.jsonl
  APPENDIX_CONTENT_PLAN.jsonl
  APPENDIX_CONTENT_PLAN.md
  INVENTORY_REVERSE_TRACE.jsonl
```

For the current `final_v4` manuscript, use these only as **expected baseline checks**, then recompute from source:

- main figures expected: `0`
- main tables expected: `2`
- main content pages expected: `4`
- reference pages expected: `1`
- appendix pages expected: `0`
- checklist pages expected: `7`
- bibliography entries expected: `10`
- citation callsites expected: `9`
- unique bibkeys used expected: `7`

If observed values differ, report the difference and identify the earliest divergent dependency.

## 2. Current main-table inventory

Mechanically verify these currently present tables.

### Table 1 — Terminal preregistered studies

Expected label:

```text
tab:terminal
```

Expected scientific role:

`PRIMARY_EXPERIMENT_SUMMARY`

Expected rows:

- EXP-008 — `UNDERPOWERED`, raw cells `300`, valid parse rate approximately `0.907`
- EXP-009 — `UNDERPOWERED`, raw cells `300`, valid parse rate approximately `0.883`

Reverse-trace every displayed value to the admitted terminal verdict/statistics source.

Do not infer statistical significance from this table.

### Table 2 — Systems-validation outcomes

Expected label:

```text
tab:systems
```

Expected scientific role:

`BOUNDED_SYSTEMS_VALIDATION_NOT_PRIMARY_TREATMENT_EFFECT`

Expected rows currently include:

- perturbation matrix — 100 cells — 100/100 chain verification
- synthetic tamper suite — 8 modes — 8/8 detected
- concurrent execution — 10 runs — 10 unique run IDs / PASS
- replay/restart recovery — 44 events — PASS
- live provider ladder — R0–R6 — bounded external failure preserved

Verify each against source receipts. Synthetic cases must remain explicitly labeled synthetic.

## 3. Figure inventory

Current manuscript is expected to contain **no admitted figure**.

Do not silently claim that the deterministic figure protocol is already in the paper.

Create one row for every candidate figure with:

```text
figure_id
status
intended_location=MAIN|APPENDIX
scientific_question
source_fcos
source_shas
numeric_values
reverse_trace_state
renderer
renderer_sha
reproducibility_state
claim_ceiling
reason_for_admit_or_defer
```

At minimum evaluate these candidates:

### FIG-001 — Deterministic evidence-to-claim custody figure

Candidate content:

```text
source bytes
→ atoms of knowledge
→ proposition
→ Seed of Truth state
→ manuscript sentence/visible number
```

Use the existing deterministic Figure/SeedGraph/FCO/FCG protocol.

Preferred minimal empirical example:

`EXP-008 closed UNDERPOWERED; effect not established.`

This figure is admitted only if full source-to-visible-text roundtrip and R1/R2/R3 rendering gates PASS.

Otherwise:

```text
FIG-001=PLANNED_NOT_EXECUTED or DEFERRED_NOT_NEEDED
```

### Optional appendix figure candidates

Only admit when source-supported and mechanically generated:

- requirement-drift timeline: organizer/website/OpenReview requirement states and supersession/contradiction;
- citation custody chain: sentence → proposition → citation callsite → bibliographic identity → authoritative publication → supported proposition;
- FCG/CFMO state-delta schematic over time.

Do not add decorative or image-generated figures as scientific evidence.

## 4. Statistical-analysis inventory

Create one row per experiment/comparison, including analyses that were **not** computable.

Required fields:

```text
analysis_id
experiment_id
comparison
unit_of_analysis
raw_n
valid_n
paired_n
failed_n
timeout_n
abstention_n
primary_endpoint
statistical_test
alternative
multiplicity_rule
effect_estimate
confidence_interval
p_value
result_state
claim_ceiling
source_artifact
source_sha256
recomputed
```

Use `NOT_COMPUTED`, `NOT_APPLICABLE`, or `UNDERPOWERED` rather than inventing a value.

### EXP-008

Expected bounded facts to reverify:

- raw cells = 300
- valid parse rate = 0.906666... (~0.907)
- primary paired n = 2
- discordant pairs = 0
- result = `UNDERPOWERED`
- bounded conclusion = effect not established

If exact McNemar p-value/CI was not validly computed in the admitted receipt, record `NOT_COMPUTED`/`NOT_INFORMATIVE_UNDER_FROZEN_N`; do not backfill a favorable statistic.

### EXP-009

Expected bounded facts to reverify:

- raw cells = 300
- valid parse rate = 0.883333... (~0.883)
- primary paired n = 2
- discordant pairs = 0
- primary result = `UNDERPOWERED`
- secondary = directional/descriptive only
- ordering established = false

Primary and secondary analyses must remain separate rows.

### Stage-2 predecessor

Reverify:

- total rows = 432
- proper Stage-2 rows = 414
- canary rows = 18
- M0 = 132
- M1 = 132
- M2 = 150
- pairwise improvement claims retained null / improvement not established

If exact tests/effect estimates are available in canonical receipts, include them in the appendix inventory. If they are not, explicitly plan deterministic recomputation from frozen row-level evidence and do not invent inferential statistics.

### HydraLamp systems validation

Treat deterministic pass/fail counts as systems-validation statistics, not powered treatment-effect statistics.

Report exact binomial/count denominators where useful, but do not label deterministic conformance counts as causal model-performance evidence.

## 5. Comparison inventory

Create a matrix that separates:

```text
PRIMARY_TREATMENT_COMPARISON
SECONDARY_EXPLORATORY_COMPARISON
SYSTEMS_CONFORMANCE_COMPARISON
RUNTIME/PROVIDER_COMPARISON
PLANNED_NOT_EXECUTED_COMPARISON
```

At minimum include:

- flat prose vs structured FCG — EXP-008
- flat prose vs structured FCG — EXP-009
- Stage-2 M0 vs M1 vs M2
- HydraLamp control vs perturbation/tamper/replay conditions
- Qwen3.8 successor — only if terminal evidence exists; otherwise `PLANNED/PARTIAL_NOT_ADMITTED`
- Cloudflare OS canary — only as bounded integration/system evidence if current receipts verify it
- SGLang/CUDA and cross-environment lanes — `PLANNED/BLOCKED` until real terminal receipts exist

No comparison may appear as a result merely because it appears in a preregistration or plan.

## 6. Appendix plan

Because the direct-human workshop guidance permits appendix material outside the 8-page main-content limit, use the appendix for **auditability and full statistical detail**, not for burying limitations.

Use explicit LaTeX labels and titles.

Recommended structure, only when material exists:

```tex
\appendix
\section{Detailed Statistical Analyses}\label{app:statistics}
\section{Systems-Validation Receipts and Comparisons}\label{app:systems}
\section{Citation and Reference Custody Audit}\label{app:citations}
\section{Requirement and Template Provenance}\label{app:requirements}
\section{SeedGraph/FCO/FCG Evidence Trace}\label{app:custody}
\section{Planned or Nonterminal Successor Experiments}\label{app:planned}
```

Do not create empty sections. If no admissible material exists, mark the candidate section `DEFERRED_NOT_NEEDED` in `APPENDIX_CONTENT_PLAN.jsonl`.

### Required appendix tables when evidence supports them

Candidate `Table A1`:

`Full EXP-008/EXP-009 statistical audit`

Include raw n, valid n, aggregation scope, paired n, discordant count, primary verdict, effect estimate/test/CI/p only where actually established.

Candidate `Table A2`:

`Stage-2 M0/M1/M2 analysis and retained-null comparisons`

Candidate `Table A3`:

`HydraLamp systems-validation matrix with exact condition counts and terminal states`

Candidate `Table A4`:

`Citation/reference verification ledger`

Candidate `Table A5`:

`Planned/nonterminal lanes and why they are not admitted as results`

Each appendix table must have a `\label{tab:app_*}` and be referenced from text or the appendix introduction.

## 7. Citation/reference list

Recompute the bibliography rather than trusting the previous count.

Current audit expected state:

- reference entries = 10
- external scholarly verified = 7
- internal anonymous = 2
- venue requirement = 1
- hallucinated references = 0
- unresolved references = 0
- unsupported citation sentences = 0
- partially supported citation sentences = 0
- used-but-undefined = []
- defined-but-unused = `prereg2026`, `stage2`, `neurips2026`

Create a citation/reference table containing:

```text
bibkey
classification
used_in_main
used_in_appendix
callsite_count
verified_identity
verified_metadata
entailment_state
source_of_verification
source_sha256
manuscript_claim_ids
```

Do not add references merely to inflate related work.

Every new bibliography entry must independently pass identity and entailment audit before final PDF selection.

References remain explicitly outside the main-content page budget under the current workshop requirement evidence.

## 8. Labeling/order in the PDF

The final PDF must make section boundaries visually and structurally explicit.

Required order unless the exact current official template/NewInML instructions prove otherwise:

```text
MAIN PAPER (2–8 pages)
REFERENCES
APPENDIX (if any; explicitly labeled)
NEURIPS CHECKLIST
```

Recompute page partition mechanically and output:

```text
MAIN_CONTENT_PAGES=
REFERENCE_PAGES=
APPENDIX_PAGES=
CHECKLIST_PAGES=
TOTAL_PDF_PAGES=
```

Never infer appendix/reference exclusion merely from total PDF page count.

## 9. Decide what belongs in main vs appendix

Main paper should retain only the smallest material set needed to support the thesis:

- core framework;
- primary EXP-008/009 terminal result table;
- bounded systems-validation table;
- at most one high-information deterministic figure if fully verified;
- explicit limitations.

Move reproducibility/audit detail to appendix when doing so does not hide a material limitation or change interpretation.

Do not move the words `UNDERPOWERED`, the primary null boundary, or major claim limitations out of the main paper.

## 10. SeedGraph/FCO/FCG custody of the inventory itself

Every inventory item is itself governed evidence.

Create relationships conceptually equivalent to:

```text
SOURCE_RESULT
→ REPORTED_AS
→ TABLE_CELL / FIGURE_ELEMENT / MANUSCRIPT_SENTENCE

STATISTICAL_ANALYSIS
→ DERIVED_FROM
→ FROZEN_CASE_RESULTS

REFERENCE
→ SUPPORTS
→ MANUSCRIPT_PROPOSITION

PLANNED_ANALYSIS
→ NOT_YET_EVIDENCE_FOR
→ CLAIM
```

Use canonical FCG relations where defined; do not invent canonical edge vocabulary silently.

The final inventory should be SeedGraph-ingested and custody-audited with zero silent missing items.

## 11. Final gate

Before any successor PDF replaces the currently green artifact, require:

```text
FIGURE_INVENTORY_COMPLETE=PASS
TABLE_INVENTORY_COMPLETE=PASS
STATISTICAL_ANALYSIS_INVENTORY_COMPLETE=PASS
COMPARISON_INVENTORY_COMPLETE=PASS
CITATION_REFERENCE_INVENTORY_COMPLETE=PASS
APPENDIX_PLAN_COMPLETE=PASS
NUMERIC_REVERSE_TRACE=PASS
ZERO_HALLUCINATED_REFERENCES=PASS
MAIN_CONTENT_PAGES<=8=PASS
APPENDIX_EXPLICITLY_LABELED_IF_PRESENT=PASS
CHECKLIST_PRESENT=PASS
ANONYMIZATION=PASS
OFFICIAL_TEMPLATE_PARITY=PASS
```

If a proposed figure/table/statistical analysis cannot be independently verified in time, leave it out of the selected PDF and record it in the appendix plan as `PLANNED_NOT_EXECUTED` or `DEFERRED_NOT_NEEDED`.

## 12. Return report

Return at minimum:

```text
MAIN_FIGURES=
APPENDIX_FIGURES=
PLANNED_FIGURES=

MAIN_TABLES=
APPENDIX_TABLES=
PLANNED_TABLES=

STATISTICAL_ANALYSES_ESTABLISHED=
STATISTICAL_ANALYSES_NOT_COMPUTED=
STATISTICAL_ANALYSES_PLANNED=

PRIMARY_COMPARISONS=
SECONDARY_COMPARISONS=
SYSTEMS_COMPARISONS=
PLANNED_COMPARISONS=

REFERENCE_ENTRY_COUNT=
EXTERNAL_SCHOLARLY_VERIFIED=
INTERNAL_ANONYMOUS_REFERENCES=
VENUE_REQUIREMENT_REFERENCES=
HALLUCINATED_REFERENCE_COUNT=

MAIN_CONTENT_PAGES=
REFERENCE_PAGES=
APPENDIX_PAGES=
CHECKLIST_PAGES=

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
```
