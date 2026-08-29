# HydraDG — Portfolio Reference Recovery + Appendix Expansion Gate

Date: 2026-08-29

## Problem statement

The current NewInML manuscript bibliography is a narrow 10-entry projection of the current 4-page main paper, while the wider Biobitworks scientific portfolio contains much larger citation/evidence corpora in FCO/FCG, Xenodisorder, Antigence and related knowledge graphs. This is a projection/coverage disconnect, not evidence that the wider literature does not exist.

The submission should not dump thousands of citations into the bibliography. It should deterministically recover the portfolio evidence universe, deduplicate and verify it, map it to actual manuscript/appendix claims, and admit the strongest relevant references. Appendix space should be used for detailed figures, tables, methods, statistical analyses, provenance diagrams, claim-evidence maps and supplemental citation tables that do not belong in the <=8-page main content.

## 1. Correct STAGE-001 terminology

Current STAGE-001 reported:

- source universe = 973
- terminal accounting = 973
- INGESTED_VERIFIED = 307
- PARTIAL = 666
- verified coverage = 31.55%

Do not use `TOTAL_IMPORT_COMPLETE=YES` without qualification.

Use:

```text
TOTAL_SOURCE_ACCOUNTING_COMPLETE=YES
TOTAL_SOURCE_UNIVERSE_COUNT=973
VERIFIED_INGEST_COUNT=307
PARTIAL_TERMINAL_COUNT=666
VERIFIED_INGEST_COVERAGE=31.55%
TOTAL_VERIFIED_INGEST_COMPLETE=NO
```

Terminal accounting is complete; verified ingest is not.

## 2. Build portfolio citation source universe

Enumerate citation-bearing sources across at minimum:

- biobitworks/fractal-custody-objects
- biobitworks/xenodisorder
- biobitworks/antigence
- hydradg admitted sources
- SeedGraph source manifests
- local Ollarma/knowledge-graph citation stores when governed and readable
- publication/preprint source trees

Known examples to inspect rather than rediscover blindly:

- fractal-custody-objects/CITATIONS_VALIDATED.jsonl
- fractal-custody-objects/CLAIM_EVIDENCE_MAP.jsonl
- xenodisorder/.ollarma/kb/documents.jsonl
- xenodisorder/.ollarma/kb/chunks.jsonl
- xenodisorder/.ollarma/kb/search.sqlite (read-only extraction through deterministic adapter)
- antigence/CITATIONS.bib
- antigence/.antigence/training_data/citation_verifications.jsonl
- all preprint/manuscript bibliographies found by deterministic tree traversal

Create:

```text
paper/newinml2026_solo/portfolio_references/PORTFOLIO_CITATION_SOURCE_UNIVERSE.jsonl
paper/newinml2026_solo/portfolio_references/PORTFOLIO_REFERENCE_LEDGER.jsonl
paper/newinml2026_solo/portfolio_references/PORTFOLIO_REFERENCE_DEDUP.jsonl
paper/newinml2026_solo/portfolio_references/PORTFOLIO_CLAIM_REFERENCE_MAP.jsonl
paper/newinml2026_solo/portfolio_references/REFERENCE_ADMISSION_DECISIONS.jsonl
```

For each reference preserve:

```text
source_repository
source_file
source_sha256
citation_occurrence_pointer
reference_identity
DOI/PMID/arXiv/URL if present
verification_state
self_prior_work_state
independent_external_state
claims_supported
manuscript_relevance
appendix_relevance
admission_state
reason
```

Do not count repeated occurrences as unique references.

## 3. Separate four citation counts

Report independently:

```text
PORTFOLIO_CITATION_OCCURRENCES
PORTFOLIO_UNIQUE_REFERENCE_IDENTITIES
PORTFOLIO_EXTERNALLY_VERIFIED_REFERENCES
CURRENT_MANUSCRIPT_REFERENCES
```

These are not interchangeable.

A knowledge graph may contain thousands of citation occurrences while the manuscript contains tens of unique references.

## 4. Reference admission policy

A source enters the NewInML bibliography only if it supports an actual main-paper or appendix proposition.

Classify:

- DIRECTLY_CITED_MAIN
- DIRECTLY_CITED_APPENDIX
- BACKGROUND_SUPPORT_NOT_CITED
- SELF_PRIOR_WORK
- INDEPENDENT_EXTERNAL_PRIOR_ART
- DISCOVERY_ONLY
- DUPLICATE
- OUT_OF_SCOPE
- UNVERIFIED

Prefer independent external literature for novelty/context claims.

FCO/FCG, Xenodisorder and Antigence preprints may be cited as SELF_PRIOR_WORK where relevant, but they must not be presented as independent external validation of HydraDG.

If double-blind rules prohibit named self-citation, use the exact venue-compliant anonymized treatment and retain the private identity mapping in custody.

## 5. Expand the related-work audit

The existing 7 external scholarly references are not sufficient to establish a serious prior-art boundary for provenance/governance/agent-science claims.

At minimum evaluate and, when proposition-relevant, admit verified references covering:

- W3C PROV / PROV-O
- CWLProv
- Workflow Run RO-Crate / RO-Crate
- BioCompute Objects / IEEE 2791
- DataLad provenance/re-execution
- Nextflow
- Snakemake
- FAIR workflows
- nanopublications
- agent provenance / sentence-level provenance
- citation hallucination/fabrication literature
- reproducibility/meta-science literature
- relevant current agent-evaluation and retrieval literature

Use the red-team search results only after independent verification/SeedGraph admission.

## 6. Appendix should carry the detailed evidence

Main content remains <=8 pages and should contain the central thesis and the most decision-relevant results.

Build a substantive appendix if evidence exists.

Candidate appendix sections:

```text
Appendix A — Complete Experimental and Statistical Results
Appendix B — Deterministic Systems-Validation Matrix
Appendix C — FCO/FCG State-Transition and CFMO Delta Examples
Appendix D — SeedGraph Atomization / Hash / Reproducibility Audit
Appendix E — Citation and Reference Chain-of-Custody Audit
Appendix F — Requirement Drift / OpenReview / Template Provenance
Appendix G — Prior-Art and Terminology Red-Team Matrix
Appendix H — Nonterminal / Blocked / Null / Negative Successor Lanes
```

No filler sections.

## 7. Figures and tables

Inventory all existing governed figures/tables across the portfolio before making new ones.

Create:

```text
FIGURE_SOURCE_UNIVERSE.jsonl
TABLE_SOURCE_UNIVERSE.jsonl
FIGURE_ADMISSION_LEDGER.jsonl
TABLE_ADMISSION_LEDGER.jsonl
```

For every candidate figure/table record:

```text
origin_repository
origin_file
origin_sha256
publication/preprint origin
self_prior_work
source data roots
analysis script SHA
render script SHA
visible value reverse-trace state
current claim ceiling
MAIN | APPENDIX | REJECTED
reason
```

Preferred appendix figures if fully governed:

1. FCO/FCG state-transition architecture
2. source -> atom -> proposition -> Seed of Truth -> manuscript claim trace
3. requirement-drift timeline
4. CFMO/FCG delta over a bounded experiment
5. deterministic custody auditor / tamper canary summary
6. first-document figure/table atomization example

Preferred appendix tables if source-supported:

1. full EXP-008/009 statistics
2. Stage-2 M0/M1/M2 results
3. HydraLamp perturbation/tamper/concurrency/replay matrix
4. SeedGraph batch/source coverage and terminal states
5. prior-art comparison matrix
6. reference/citation verification ledger summary
7. planned/nonterminal lane matrix

Do not transplant biological results from Xenodisorder/Antigence into HydraDG empirical results. Those projects can contribute prior work, methods lineage, figures illustrating shared governance concepts, or future-domain examples only when explicitly labeled.

## 8. Statistical analysis recovery

Search the portfolio and current HydraDG evidence for actual computed statistical artifacts before declaring analyses absent.

Create:

```text
STATISTICAL_ANALYSIS_UNIVERSE.jsonl
STATISTICAL_RESULT_ADMISSION_LEDGER.jsonl
```

Each analysis:

```text
experiment_id
source artifact
script SHA
input root
n/raw denominator
paired denominator if applicable
endpoint
estimate
effect size
CI
p-value/test if actually computed
multiplicity rule
power/MESI state
result class
claim ceiling
```

Never invent CI/p-values/effects that were not computed.

## 9. First-document gap

STAGE-001 reports:

- 34 first-document atoms
- 2 Seeds of Truth
- 0 figure objects atomized
- 2 table objects atomized

Therefore first-document material coverage is not complete.

Before claiming document-level deconstruction complete:

- atomize every figure object/panel/caption
- atomize every table/row/cell/caption/footnote
- reverse-trace every displayed result value
- bind citation callsites to reference identities
- produce material-semantic coverage denominator

## 10. Final manuscript/reference projection

After portfolio recovery, regenerate the NewInML bibliography as a deterministic projection:

```text
PORTFOLIO_REFERENCE_LEDGER
  -> dedup
  -> authoritative verification
  -> claim relevance
  -> double-blind/self-prior-work rules
  -> manuscript/appendix callsites
  -> FINAL_REFERENCES
```

Do not use an arbitrary target count.

A larger bibliography is expected if the expanded related-work/appendix propositions require it, but every listed reference must have an actual callsite or explicit venue-permitted bibliography rationale.

## 11. Required report

Return:

```text
PORTFOLIO_CITATION_SOURCE_FILES=
PORTFOLIO_CITATION_OCCURRENCES=
PORTFOLIO_UNIQUE_REFERENCE_IDENTITIES=
PORTFOLIO_EXTERNALLY_VERIFIED_REFERENCES=
SELF_PRIOR_WORK_REFERENCE_IDENTITIES=
DUPLICATE_REFERENCE_OCCURRENCES=
UNVERIFIED_REFERENCE_IDENTITIES=

CURRENT_MANUSCRIPT_REFERENCES_BEFORE=
CURRENT_MANUSCRIPT_REFERENCES_AFTER=
MAIN_CITATION_CALLSITES=
APPENDIX_CITATION_CALLSITES=

MAIN_FIGURES=
APPENDIX_FIGURES=
MAIN_TABLES=
APPENDIX_TABLES=

STATISTICAL_ANALYSES_FOUND=
STATISTICAL_ANALYSES_ADMITTED=
STATISTICAL_ANALYSES_NOT_COMPUTED=

FIRST_DOCUMENT_FIGURES_ATOMIZED=
FIRST_DOCUMENT_TABLE_CELLS_ATOMIZED=
FIRST_DOCUMENT_MATERIAL_SEMANTIC_COVERAGE=

TOTAL_SOURCE_ACCOUNTING_COMPLETE=
TOTAL_VERIFIED_INGEST_COMPLETE=
VERIFIED_INGEST_COVERAGE=

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
