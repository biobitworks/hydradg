# Citation Gap Audit — Final (HydraDG SOLO / NewInML 2026)

**Branch:** `cursor/newinml-solo-citation-priorart-final-20260829`  
**Base:** `origin/cursor/newinml-solo-full-repro-recovery-20260829` @ `38cdb62e72bd26a48b42e286b86303a949a545fa`  
**Audit mode:** `FINAL_CITATION_GAP_REPAIR_AND_SUBMISSION_DECISION`  
**Claim ceiling:** `CUSTODY_MECHANICS`  
**Protein Hinge primary evidence imported:** `NO`

## Executive verdict

| Gate | Verdict |
|------|---------|
| `CITATION_GAPS_SUBMISSION_BLOCKING` | **YES** (predecessor PDF) |
| `FROZEN_PDF_DECISION` | **SUCCESSOR** (predecessor preserved) |
| `NOVELTY_BOUNDARY_GATE` | **PASS** (after successor patch) |
| `PROTEIN_HINGE_PRIMARY_EVIDENCE_IMPORTED` | **NO** |

The predecessor frozen upload PDF (`c16be09e…`) discussed hash-linked FCG roots and provenance lineage without citing established Merkle/audit-log or main-text PROV/workflow-provenance foundations, and omitted high-priority negative-results and agent-provenance comparators. These gaps are **submission-blocking for prior-art correctness** on a custody-first paper.

A **successor PDF** was built from patched `main.tex` without modifying the frozen predecessor bytes.

## Predecessor gaps (frozen `c16be09e…`)

1. **Merkle / tamper-evident prior art** — Framework text used “hash-linked roots” and systems validation referenced tamper detection without citing Certificate Transparency / Merkle audit-tree foundations (`laurie2013ct`).
2. **PROV / workflow provenance in main text** — PROV-O, CWLProv, and RO-Crate appeared only in appendix prior-art prose; Related Work discussed provenance without main-text grounding.
3. **Negative ML results** — Introduction/Related Work motivated null retention but lacked Karl et al. (ICML 2024) citation.
4. **Agent execution provenance** — No adjacent comparator to Wang et al. (arXiv:2606.04990) survey on evidence tracing / execution provenance in LLM agents.
5. **Prior-art matrix inconsistency** — `MLflow` named in `PRIOR_ART_MATRIX.tsv` without a citation-ledger entry (`zaharia2018mlflow` added in reconciliation ledger).

## Successor repairs

### Related Work (replaced provenance paragraph)

Added verified citations and explicit non-novelty boundary for Merkle/audit logs, PROV-O, CWLProv, agent provenance survey, and negative-results position paper. Rewrote integration sentence to match conservative novelty statement.

### Framework (single callsite)

Added `\cite{laurie2013ct}` to hash-linked FCG roots sentence.

### Bibliography additions (main text)

- `laurie2013ct` — RFC 6962 Certificate Transparency (Laurie, Langley, Kasper, 2013)
- `lebo2013provo` — W3C PROV-O (2013)
- `khan2019cwlprov` — CWLProv, GigaScience 2019
- `karl2024negative` — ICML 2024 position, arXiv:2406.03980
- `wang2026agentprovenance` — arXiv:2606.04990 (Yiqi Wang et al., 2026)

## Protein Hinge citation probe — rejections

| Candidate | Decision | Reason |
|-----------|----------|--------|
| Chow 1970 | **REJECT main** (optional appendix) | Model reject tradeoff ≠ HydraDG typed terminal states |
| El-Yaniv & Wiener 2010 | **REJECT main** | Selective classification theory; appendix comparator only |
| Geifman & El-Yaniv 2017 | **APPENDIX optional** | Canonical selective-prediction comparator; not main-text |
| Laurie et al. 2013 (CT) | **ADMIT** | Independently verified; HydraDG uses hash-linked roots |
| Rubin 1976 | **REJECT** | No MCAR/MAR/MNAR analysis in SOLO |
| Huang et al. 2024 | **REJECT** | Repurposing / TEAM lane; no independent SOLO justification |

## Novelty boundary (conservative)

HydraDG does **not** introduce provenance graphs, Merkle hashing, research-object packaging, experiment tracking, or abstention as isolated concepts. Its contribution is the **integration** of these ideas into a custody-first experimental contract for probabilistic agent science, in which substantive transformations, failures, malformed outputs, null results, underpowered terminations, and cross-actor handoffs remain typed evidence objects with explicit claim-promotion ceilings.

## Scientific state unchanged

| Item | State |
|------|-------|
| EXP-008 | `UNDERPOWERED` |
| EXP-009 | `UNDERPOWERED` |
| Numeric results in tables | **unchanged** (0.907, 0.883 parse rates; 300 cells) |
| Protein Hinge empirical import | **NO** |

## Reproducibility package limitations (unchanged)

Per ChatGPT appendix federation audit (not repaired by this citation-only lane):

| Gate | State |
|------|-------|
| `STATISTICS_R123` | `PASS` |
| `FIGURES_R123` | `NOT_ESTABLISHED` |
| `TABLES_R123` | `NOT_ESTABLISHED` |
| `REQUESTED_FIGURE_COVERAGE` | `INCOMPLETE` |

Do **not** claim all publication artifacts are deterministic.

## OpenReview / license note

- **Venue form field:** Submission B metadata records `License=CC BY 4.0` for the article upload.
- **OpenReview platform terms** are separate from article license selection.
- **Repository code** remains Apache-2.0 per appendix note; FCO/FCG source-lineage restrictions (e.g., CC BY-NC-ND where applicable) remain a separate layer.
- OpenReview does **not** universally require CC BY 4.0 for all venues; this is the **current NewInML form field**, not a platform-wide rule.

## Upload recommendation

| Artifact | Recommendation |
|----------|----------------|
| Predecessor `c16be09e…` | **Do not upload** (citation gaps blocking) |
| Successor `ee834796…` | **Preferred upload candidate** for prior-art correctness |
| Full package safety | **CONDITIONAL** — human visual review still required; figure/table determinism unresolved |

## Final review answers (summary)

1. **Already covered:** RAG, GraphRAG, agent benchmarks, preregistration, FAIR, nanopublications.
2. **Genuinely missing (predecessor):** Merkle/CT, main-text PROV/CWLProv, Karl negative-results, Wang agent-provenance survey, MLflow ledger entry.
3. **Protein Hinge rejected:** Rubin, Huang; Chow/El-Yaniv/Geifman kept appendix-only.
4. **Overstatement risk (predecessor):** YES for hash-linked roots without Merkle cite; mitigated in successor.
5. **Changed sentences:** Related Work provenance paragraph; FCG hash-linked roots cite.
6. **Scientific numbers changed:** NO.
7. **EXP-008/009 verdicts changed:** NO.
8. **Protein Hinge results imported:** NO.
9. **PDF hash changed:** YES (new successor); predecessor preserved.
10. **Reopen justified:** YES — prior-art correctness outweighs deadline risk of a short Related Work patch.
11. **Safe to upload:** Successor PDF for citations; full artifact package still has figure/table gaps.
12. **Unresolved:** Figure/table R1/R2/R3 gates, requested appendix figure suite, human visual inspection, inventory baseline drift for expanded bibliography counts.
