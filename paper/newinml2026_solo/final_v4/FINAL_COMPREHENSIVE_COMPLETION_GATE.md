# HydraDG SOLO — Final Comprehensive Completion Gate

Status: BLOCKING REVIEW CONTRACT

This file converts the independent review findings into a fail-closed definition of `FINAL_COMPREHENSIVE_UPLOAD_CANDIDATE=YES`.

The current citation-only successor `ee8347969827f0296b16e934590c6efd24fb3ecc6fc090f7251f58d30a096b81` is NOT the final comprehensive upload candidate.

## Immutable scientific boundaries

- `EXP-008=UNDERPOWERED`.
- `EXP-009=UNDERPOWERED`.
- No structured-retrieval treatment effect is established.
- `CLAIM_CEILING=CUSTODY_MECHANICS` unless a separately governed experiment changes it.
- `PROTEIN_HINGE_PRIMARY_EVIDENCE_COUNT=0`.
- Do not rerun or alter scientific experiments merely to repair publication artifacts.
- Preserve positive, null, negative, failed, blocked, timeout, abstention, contradictory, and superseded states.
- Hash identity is not a digital signature.
- `SIGNATURE_STATE=SIGNED` and `MERKLE_MMR_STATE=COMMITTED` require actual operations and receipts.

## A. Bibliography and citation correctness — MUST PASS

1. Exactly one bibliography authority for the compiled paper/supplement surface.
2. No duplicate citation keys.
3. Build until there are no `multiply defined citations`, `undefined citation`, or `Citation(s) may have changed` warnings.
4. Correct bibliographic metadata from authoritative sources. At minimum repair/verify:
   - Chow 1970: DOI `10.1109/TIT.1970.1054406`, IEEE TIT 16(1):41–46.
   - El-Yaniv & Wiener 2010: JMLR 11:1605–1641.
   - DataLad JOSS: 6(63):3262, DOI `10.21105/joss.03262`.
   - Wang et al. 2026 exact title: `From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents`.
   - CWLProv canonical title: `Sharing interoperable workflow provenance: A review of best practices and their practical application in CWLProv`, GigaScience 8(11):giz095, DOI `10.1093/gigascience/giz095`.
5. Every callsite must be entailed by the cited source. Do not cite provenance papers as evidence of citation-fabrication prevalence; split those claims.
6. Replace the stale universal wording `OpenReview license requirement CC BY 4.0` with venue/form-specific language. Preserve software/research-content/upstream license separation.
7. Correct predecessor page delta against the selected `c16be09e...` Submission B candidate: references 2→successor count, not 1→successor count.
8. Preserve the conservative novelty boundary: HydraDG does not invent provenance graphs, Merkle hashing, research-object packaging, experiment tracking, or abstention as isolated concepts.

Required machine outputs:

- `SINGLE_BIBLIOGRAPHY_GATE=PASS`
- `CITATION_METADATA_GATE=PASS`
- `CITATION_CALLSITE_ENTAILMENT=PASS`
- `LATEX_CITATION_WARNING_COUNT=0`
- `CITATION_SOURCE_VERIFICATION_COVERAGE=1.0`

## B. Prior/shared preprint lineage — MUST PASS

Include verified HydraDG-adjacent prior/shared research in third-person/blind-safe form, with zero primary empirical weight. At minimum independently verify and classify:

- FCO v1 — DOI `10.5281/zenodo.21210575`.
- FCO v3 — DOI `10.5281/zenodo.21420906`.
- FCO/FCG registered protocol — DOI `10.5281/zenodo.21382831`.
- FCO v4/v5 + Vithia companion — DOI `10.5281/zenodo.21829929`.

Do not cite an Anticube DOI or other record until the canonical source identity resolves.

For each prior/shared work record:

- canonical title;
- authors;
- DOI/version;
- license;
- role in current paper;
- Anticube state relative to SOLO evidence graph;
- primary evidentiary weight (must be 0 unless explicitly admitted by the solo experiment contract).

Required machine output:

- `PRIOR_SHARED_WORK_IDENTITY_COVERAGE=1.0`
- `BLIND_SELF_CITATION_GATE=PASS`

## C. Software / model / dataset BOM — MUST PASS

Do not bind independent repositories to one HydraDG SHA.

Create the final machine-readable BOM with at least:

`component_id, canonical_repository_or_source, exact_revision_used, version_or_tag, digest_if_model, role, license, license_source, experimental_or_supporting, distribution_state, anticube_state, claim_ceiling, evidence_reference`.

Resolve the exact identities actually used for the submitted evidence, including as applicable:

- HydraDG;
- Fractal Custody Objects / FCG;
- GettingScienceDone / Mechanical Scientific Method;
- SeedGraph;
- Ollarma;
- HydraLamp (systems-only evidence; keep naming/trademark analysis outside blind manuscript unless needed);
- HydraDB;
- Antigence (related implementation, mixed/negative evidence preserved);
- Vithia companion;
- Vitaology only if source/experiment admission is verified;
- Python;
- pandas;
- SciPy;
- matplotlib;
- Ollama;
- every evaluated model by exact model identity/digest where evidence depends on it;
- NeurIPS 2026 style/template;
- every dataset/source required by the submitted experiments with upstream rights state.

External prior-art software such as MLflow/DataLad/SLSA/in-toto/RO-Crate/CWLProv belongs in the prior-art comparator table, not as if it executed the HydraDG experiment.

Required machine outputs:

- `SOFTWARE_IDENTITY_COVERAGE=1.0`
- `SOFTWARE_LICENSE_COVERAGE=1.0`
- `MODEL_IDENTITY_COVERAGE=1.0`
- `DATASET_IDENTITY_RIGHTS_COVERAGE=1.0`

## D. Required tables — MUST BE GENERATED AND TRACEABLE

Main/compact:

1. `T1_PRIMARY_EXPERIMENT_OUTCOMES`.
2. `T2_SYSTEMS_VALIDATION_VS_CLAIM_CEILING`.

Appendix/supplement:

3. `A1_COMPLETE_EXPERIMENT_STATE_LEDGER`.
4. `A2_STATISTICAL_EFFECT_DELTA_MATRIX`.
5. `A3_NULL_NEGATIVE_FAILED_BLOCKED_REGISTRY`.
6. `A4_CITATION_PRIOR_ART_COMPARATOR_MATRIX`.
7. `A5_SOFTWARE_MODEL_DATASET_BOM`.
8. `A6_PRIOR_SHARED_PREPRINT_LINEAGE`.
9. `A7_ANTICUBE_SOT_DELTA_LEDGER`.
10. `A8_FIGURE_TABLE_SOURCE_HASH_LEDGER`.
11. `A9_CLAIM_EVIDENCE_REVERSE_TRACE`.
12. `A10_RIGHTS_LICENSE_REDISTRIBUTION_MATRIX`.

No evidence-bearing numerical row may be typed into the renderer/table builder when it can be obtained from a declared source receipt/statistical output. A table row may be hand-authored only when it is explicitly qualitative/governance metadata and its provenance is recorded.

Required machine outputs:

- `REQUIRED_TABLE_COVERAGE=1.0`
- `TABLE_SOURCE_TRACE_COVERAGE=1.0`
- `TABLE_NUMERIC_REVERSE_TRACE_COVERAGE=1.0`

## E. Required figures — MUST BE GENERATED AND TRACEABLE

Required publication figure set:

1. custody-first experiment pipeline;
2. EXP-008/009 terminal result figure sourced from exact statistical/receipt values;
3. terminal-state landscape generated from experiment census;
4. HydraLamp bounded systems-validation panel sourced from exact receipts;
5. Mechanical Scientific Method / GettingScienceDone governance figure;
6. governed federation + deterministic/ML-complement map;
7. canonical Anticube 2×2;
8. Anticube 3-D trajectory only if canonical state history exists: X=self/non-self, Y=non-safe/safe, Z=time/governed state; ΔG* is separate and MUST NOT substitute for Z;
9. FCO/FCG evidence→claim→artifact graph;
10. SeedGraph hierarchy with the interrupted/full-project boundary explicitly shown;
11. prior-art topology / novelty-boundary figure;
12. source→transform→artifact/hash/reproduction lineage figure.

Optional Context-Iceberg / CFMO / ΔG* panels remain `BLOCKED_NOT_COMPUTED` unless their exact underlying metrics are actually computed under a frozen contract.

Every visible empirical value/text element must map through a figure source ledger to exact source bytes/receipt/statistical output.

Required machine outputs:

- `REQUESTED_FIGURE_COVERAGE=1.0` OR individual figures explicitly `BLOCKED_<reason>` where publication-safe omission is justified;
- `FIGURE_SOURCE_TRACE_COVERAGE=1.0` for every admitted figure;
- `FIGURE_NUMERIC_REVERSE_TRACE_COVERAGE=1.0`;
- derivative SHA-256 for every distributed SVG/PNG/PDF figure artifact.

## F. Determinism — MUST BE ESTABLISHED, NOT ASSERTED

Statistics already have an R1/R2/R3 gate. Figures and tables need equivalent gates.

For every evidence-bearing table and figure:

1. separate canonical data/spec/text/layout from rendering code;
2. run in a pinned environment from clean output directories for R1/R2/R3;
3. compare canonical scientific payload roots;
4. compare rendered artifact hashes where exact-byte determinism is claimed;
5. if renderer metadata prevents byte equality, do not call derivative bytes deterministic: instead fix the renderer/environment or bound the claim to a canonical deterministic source/spec root and record derivative hashes separately;
6. no timestamps/random UUIDs/unseeded randomness may enter canonical scientific roots;
7. fail closed on any unexplained divergence.

Required outputs:

- `STATISTICS_R123=PASS`
- `FIGURES_R123=PASS`
- `TABLES_R123=PASS`
- `SOURCE_HASH_RECOMPUTE_GATE=PASS`
- `DERIVATIVE_HASH_COVERAGE=1.0`

## G. SOT / Anticube delta ledger — MUST PASS

Treat SOT/delta documents as reference/evidence maps, not automatic truth.

Every admitted row must contain:

- source/SOT state;
- validation state;
- evidence class;
- Anticube state at t0;
- Anticube state at t1 when a transition is claimed;
- measured delta if actually recomputed;
- otherwise `NOT_COMPUTED`;
- claim ceiling;
- source pointer/hash.

Anticube is submission-relative:

- `SELF+SAFE` = SOLO object admitted at bounded ceiling;
- `SELF+NON_SAFE` = SOLO object incomplete, failed, superseded, unverified, or unsafe to promote;
- `NON_SELF+SAFE` = external/pre-existing/shared work valid to cite/use at zero primary weight;
- `NON_SELF+NON_SAFE` = external/shared material unverified, inappropriate, rights-blocked, or scope-contaminating.

`Z=time/governed state`. ΔG* is not the Z axis.

Preserve known bounded states including EXP-008/009 UNDERPOWERED, interrupted whole-project SeedGraph, historical LongMem retrieval deltas only at their verified/recomputed level, bounded HydraDB edge parity, HydraLamp systems-only results, and nonterminal/failed provider/runtime lanes.

Required outputs:

- `ANTICUBE_CLASSIFICATION_COVERAGE=1.0`
- `SOT_DELTA_COVERAGE=1.0`
- `UNMEASURED_DELTA_NOT_COMPUTED_GATE=PASS`

## H. Final PDF / supplement gate — MUST PASS AFTER ALL ABOVE

Do not overwrite predecessor PDFs. Build a new final comprehensive successor and record its lineage.

Required:

- content pages within NewInML 2–8 page body limit;
- references separated/count recorded;
- checklist present;
- one bibliography authority;
- no LaTeX citation warnings;
- fonts embedded;
- anonymous PDF text and metadata;
- anonymous supplement/notebook/log/path scan;
- no Protein Hinge primary evidence;
- no prohibited promoted claims;
- exact title/TLDR/keywords consistency;
- exact PDF SHA-256;
- supplement manifest + SHA-256;
- security/Gitleaks result for exact final commit;
- rights/redistribution gate;
- exact Git branch/SHA bound into the final receipt;
- correct predecessor/successor page-count delta.

Required outputs:

- `CONTENT_PAGE_GATE=PASS`
- `SINGLE_BIBLIOGRAPHY_GATE=PASS`
- `FONT_EMBEDDING_GATE=PASS`
- `ANONYMITY_GATE=PASS`
- `SECURITY_GATE=PASS`
- `LICENSE_RIGHTS_GATE=PASS`
- `CLAIM_CEILING_GATE=PASS`
- `PROTEIN_HINGE_PRIMARY_EVIDENCE_COUNT=0`
- `FINAL_PDF_SHA256=<exact>`
- `FINAL_SUPPLEMENT_SHA256=<exact or NOT_APPLICABLE>`

## I. Human-only final gate

Machine agents may inspect render geometry/screenshots, but the venue operator must still perform the final human visual review of every submission page.

Machine output before handoff:

- `MACHINE_VISUAL_QA=PASS` if automated visual checks/screenshots find no clipping/overflow/unreadable figures.
- `HUMAN_VISUAL_REVIEW=REQUIRED` until the operator explicitly approves.

Do not convert `HUMAN_VISUAL_REVIEW=REQUIRED` to PASS autonomously.

## J. Completion definition

Do not use `REPAIRED`, `CONDITIONAL_PASS`, `READY_EXCEPT`, or `NOT_ESTABLISHED` for machine-verifiable gates in the final completion packet.

The machine-complete state requires:

```text
PRIOR_ART_CONCEPT_GATE=PASS
NOVELTY_BOUNDARY_GATE=PASS
SINGLE_BIBLIOGRAPHY_GATE=PASS
CITATION_METADATA_GATE=PASS
CITATION_CALLSITE_ENTAILMENT=PASS
CITATION_SOURCE_VERIFICATION_COVERAGE=1.0
PRIOR_SHARED_WORK_IDENTITY_COVERAGE=1.0
SOFTWARE_IDENTITY_COVERAGE=1.0
SOFTWARE_LICENSE_COVERAGE=1.0
MODEL_IDENTITY_COVERAGE=1.0
DATASET_IDENTITY_RIGHTS_COVERAGE=1.0
REQUIRED_TABLE_COVERAGE=1.0
TABLE_SOURCE_TRACE_COVERAGE=1.0
REQUESTED_FIGURE_COVERAGE=1.0_OR_EXPLICIT_BLOCKED_ROWS
FIGURE_SOURCE_TRACE_COVERAGE=1.0
ANTICUBE_CLASSIFICATION_COVERAGE=1.0
SOT_DELTA_COVERAGE=1.0
STATISTICS_R123=PASS
FIGURES_R123=PASS
TABLES_R123=PASS
SOURCE_HASH_RECOMPUTE_GATE=PASS
DERIVATIVE_HASH_COVERAGE=1.0
CONTENT_PAGE_GATE=PASS
FONT_EMBEDDING_GATE=PASS
ANONYMITY_GATE=PASS
SECURITY_GATE=PASS
LICENSE_RIGHTS_GATE=PASS
CLAIM_CEILING_GATE=PASS
PROTEIN_HINGE_PRIMARY_EVIDENCE_COUNT=0
MACHINE_VISUAL_QA=PASS
HUMAN_VISUAL_REVIEW=REQUIRED
```

Only after the human operator reviews all pages may the final operator receipt set:

`HUMAN_VISUAL_REVIEW=PASS`

and then:

`FINAL_COMPREHENSIVE_UPLOAD_CANDIDATE=YES`.

## Required closeout

Report exact:

```text
CURRENT_BRANCH=
CURRENT_SHA=
PR=
WORKTREE_STATE=

PREDECESSOR_PDF_SHA256=
FINAL_SUCCESSOR_PDF_SHA256=
FINAL_SUPPLEMENT_SHA256=
CONTENT_PAGES=
REFERENCE_PAGES=
CHECKLIST_PAGES=
TOTAL_PAGES=

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

Do not merge this PR merely because the completion contract was added. The implementation and verification must satisfy the contract first.
