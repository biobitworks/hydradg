# NewInML License + Anticube Audit Gate — 2026-08-29

## Objective

Add deterministic license/right-to-use tracking to the NewInML submission audit and the portfolio-wide SeedGraph/FCO/FCG custody model.

This gate is operational/compliance evidence, not legal advice and not a legal determination.

## Current governing submission evidence

Treat the current human-captured OpenReview venue form as DIRECT_HUMAN_EVIDENCE that the submission license field is:

- `CC BY 4.0`

Preserve the exact captured form text/source in the requirement corpus and independently re-check the live OpenReview form at human submission time.

Do not infer that selecting CC BY 4.0 for the paper relicenses repositories, software, datasets, model weights, third-party figures, or source documents.

Current HydraDG repository code license is Apache-2.0; keep code-license and paper-license layers distinct.

## Required license layers

For every admitted object, record independently:

1. `submission_license_requirement`
2. `artifact_license_observed`
3. `rights_holder_or_source`
4. `license_source_pointer`
5. `license_source_sha256`
6. `use_context`
7. `publication_action`
8. `attribution_required`
9. `redistribution_allowed`
10. `derivative_allowed`
11. `license_compatibility_state`
12. `anticube_before`
13. `anticube_after`
14. `context_score_before`
15. `context_score_after`
16. `context_score_delta`

Never infer a license merely from repository visibility or availability.

## License compatibility states

Use terminal states:

- `PASS_SELF_OWNED_CC_BY`
- `PASS_COMPATIBLE_WITH_ATTRIBUTION`
- `PASS_CODE_LICENSE_SEPARATE_FROM_PAPER`
- `CITE_ONLY_NO_REPRODUCTION`
- `RECREATE_FROM_VERIFIED_FACTS`
- `PERMISSION_REQUIRED`
- `LICENSE_UNKNOWN`
- `LICENSE_CONFLICT`
- `EXCLUDED_FROM_SUBMISSION`
- `NOT_APPLICABLE`

A missing/unknown license must never silently become permission to reproduce.

## Anticube use

Anticube classification is occurrence/context specific and may change over time.

Examples to verify with the canonical classifier rather than hard-code:

- own manuscript submitted under CC BY 4.0: publication occurrence may be `SELF+SAFE`;
- own Apache-2.0 code in its repository: code occurrence may be `SELF+SAFE` while the manuscript remains CC BY 4.0;
- third-party CC BY figure with required attribution satisfied: publication occurrence may be `NON_SELF+SAFE`;
- third-party figure with unknown or incompatible rights: direct-reproduction occurrence should be `NON_SELF+NON_SAFE` until resolved;
- secret credential: disclosure occurrence is `SELF+NON_SAFE`, while authorized runtime use may be separately permissible.

Do not collapse `NON_SAFE_TO_DISCLOSE` into `NON_SAFE_TO_USE`.

Every state change appends a successor FCG delta; never overwrite the earlier classification.

## Submission artifact classes to audit

Audit at minimum:

- manuscript text;
- bibliography/reference metadata;
- appendix;
- generated figures;
- reproduced/adapted external figures;
- generated tables;
- reproduced/adapted external tables;
- screenshots/UI captures;
- datasets/data excerpts;
- code snippets;
- repository code;
- template/style/checklist assets;
- model weights/model cards;
- Hugging Face datasets/models;
- Kaggle datasets/notebooks;
- npm/PyPI dependencies;
- fonts/media if embedded;
- source PDFs and supplementary documents retained as audit evidence.

Audit evidence storage and permission to publish are distinct states.

## Deterministic implementation

Implement a reusable core in GettingScienceDone and a HydraDG wrapper:

- `gettingsciencedone/src/gsigmad/license_audit/`
- `hydradg/scripts/newinml_license_audit.py`

The implementation must be deterministic for frozen inputs.

### Discovery sources

For each local repository/artifact inspect, where present:

- `LICENSE`, `LICENSE.*`, `COPYING`, `NOTICE`;
- SPDX headers;
- `CITATION.cff`;
- `pyproject.toml`, `setup.cfg`, `setup.py`;
- `package.json`, lockfiles;
- model/dataset cards and their frozen metadata;
- source-page license metadata;
- DOI/Crossref/PMC/open-access license metadata when relevant.

Do not use package-manager metadata as the sole authority when a primary license file/source exists.

### Outputs

Write:

- `LICENSE_REQUIREMENT_SOURCE_MANIFEST.jsonl`
- `ARTIFACT_LICENSE_LEDGER.jsonl`
- `FIGURE_TABLE_RIGHTS_LEDGER.jsonl`
- `DEPENDENCY_LICENSE_LEDGER.jsonl`
- `MODEL_DATA_LICENSE_LEDGER.jsonl`
- `LICENSE_ANTICUBE_TIMELINE.jsonl`
- `LICENSE_CONFLICTS.jsonl`
- `LICENSE_AUDIT_RECEIPT.json`

Each source file/metadata response must be SHA-256 frozen.

## Deterministic canaries

Run R1/R2/R3 over the frozen license corpus.

Add synthetic copies only:

1. remove a LICENSE file -> `LICENSE_UNKNOWN`/FAIL;
2. change SPDX ID -> successor license root must change;
3. insert a third-party image with unknown rights -> direct publication must block;
4. insert CC BY image without attribution -> compatibility gate must fail;
5. mark an Apache code dependency as CC BY without evidence -> provenance mismatch must fail;
6. move a secret file into publication bundle -> Anticube disclosure gate must fail.

Synthetic cases must never be represented as real submission defects.

## OpenReview versus repository license gate

Explicitly report:

- `OPENREVIEW_PAPER_LICENSE_REQUIREMENT=CC-BY-4.0`
- `HYDRADG_REPOSITORY_LICENSE=Apache-2.0`
- `PAPER_REPO_LICENSE_CONFLATION=NO`

The paper may be submitted under the required OpenReview license while the repository code remains under its own software license, subject to rights actually held for each included artifact.

Do not claim compatibility for third-party material without evidence.

## Existing deterministic audit tooling to inventory and demonstrate

Build `DETERMINISTIC_AUDIT_TOOLING_LEDGER.jsonl` with exact Git SHA, script SHA-256, inputs, outputs, execution receipt, and gate state for each tool.

At minimum inspect:

- `scripts/newinml_requirement_citation_seedgraph_audit.py`
- `scripts/custody_audit.py`
- `scripts/gum_doctor_v2.py`
- `scripts/cursor_terminology_seedgraph_anticube_execute.py`
- `scripts/newinml_final_v3_submission.py`
- `.github/workflows/newinml-final-verification.yml`
- `scripts/newinml_final_inventory_gate.py` if present in the local working tree

Classify each as:

- `DETERMINISTIC_VERIFIED`
- `DETERMINISTIC_WITH_IMPLEMENTATION_SPECIFIC_PROFILE`
- `SCAFFOLDING_NOT_SCIENTIFICALLY_VALIDATED`
- `LOCAL_UNCOMMITTED_NOT_ORIGIN_VERIFIED`
- `PROBABILISTIC_COMPONENT_PRESENT`
- `NOT_TESTED`

Important red-team requirement: inspect implementation semantics, not only whether a script exits 0.

Specifically audit the terminology/prior-art executor for placeholder or synthetic hit counts/heuristic conclusions. Any such logic must remain `DISCOVERY_ONLY`/scaffolding and must not be used as scientific evidence or novelty proof.

## Inventory/PDF rule

Do not mutate the current selected PDF while building this license audit.

First produce license and tooling ledgers. Then decide whether any appendix material, figure, table, citation, screenshot, or code excerpt is publication-safe.

## Queue priority

Every response begins with:

- `OPERATOR_ACTION_QUEUE`
- `SECRET_QUEUE`
- `EXECUTION_QUEUE`

A license conflict that blocks a planned published artifact is at least P1; a conflict that would invalidate the selected submission artifact is P0.

A secret requirement blocking an otherwise-ready material lane remains P0.

For every actionable row include priority and Anticube/context-score before and after.

## Final report

Return:

`OPENREVIEW_PAPER_LICENSE_REQUIREMENT=`
`HYDRADG_REPOSITORY_LICENSE=`
`PAPER_REPO_LICENSE_CONFLATION=`
`ARTIFACTS_AUDITED=`
`LICENSE_PASS=`
`LICENSE_UNKNOWN=`
`LICENSE_CONFLICT=`
`PERMISSION_REQUIRED=`
`EXCLUDED_FROM_SUBMISSION=`
`FIGURES_PUBLICATION_SAFE=`
`TABLES_PUBLICATION_SAFE=`
`APPENDIX_PUBLICATION_SAFE=`
`DEPENDENCIES_AUDITED=`
`MODELS_DATASETS_AUDITED=`
`LICENSE_R1_ROOT=`
`LICENSE_R2_ROOT=`
`LICENSE_R3_ROOT=`
`LICENSE_REPRODUCIBILITY_GATE=`
`DETERMINISTIC_AUDIT_TOOLS_VERIFIED=`
`DETERMINISTIC_AUDIT_TOOLS_SCAFFOLDING=`
`LOCAL_UNCOMMITTED_AUDIT_TOOLS=`

and the standard HydraDG checkpoint.
