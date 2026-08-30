# HYDRADG / NEWINML 2026 SOLO — CURSOR INDEPENDENT APPENDIX/FEDERATION REVIEW

MODE=`POST_CHATGPT_DEEP_DIVE_INDEPENDENT_REVIEW`

You are Cursor acting as the **independent implementation and submission reviewer** for the SOLO HydraDG / NewInML paper.

Do not rubber-stamp ChatGPT's proposed appendix. Recompute/check its source claims from the exact repositories, files and SHAs.

## 0. Absolute scope boundary

SOLO project only.

`Protein Hinge` and the TEAM submission are separate. Do not import TEAM experimental results, TEAM authorship, TEAM claims, or Protein Hinge primary evidence into this manuscript. Shared pre-existing infrastructure may be mentioned only after explicit classification and anonymity/licensing review.

## 1. Pull the ChatGPT review branch

On the authoritative working machine/repo:

```bash
cd /Users/byron/projects/active/hydradg

git fetch origin

git switch chatgpt/newinml-appendix-federation-review-20260829
git pull --ff-only origin chatgpt/newinml-appendix-federation-review-20260829

git branch --show-current
git rev-parse HEAD
git status --porcelain=v1 -uall
```

This branch was forked from:

`cursor/newinml-solo-full-repro-recovery-20260829`

at:

`38cdb62e72bd26a48b42e286b86303a949a545fa`

Read in full:

- `paper/newinml2026_solo/chatgpt_appendix_review_20260829/README.md`
- `APPENDIX_E_ANON_REVIEWER.md`
- `APPENDIX_E_SOURCE_MAP_INTERNAL.md`
- `APPENDIX_RESTRUCTURE_PLAN.md`
- `FEDERATION_IMPLEMENTATION_MATRIX.tsv`
- `ML_COMPLEMENT_MATRIX.tsv`

Also inspect the existing PR #38 recovery package, especially:

- `paper/newinml2026_solo/successor_recovery/EXPERIMENT_MASTER_LEDGER.tsv`
- `CHECKLIST_EVIDENCE_MATRIX.tsv`
- `CITATION_LEDGER.tsv`
- `DATASET_BOM.tsv`
- `NOVELTY_MATRIX.tsv`
- `IP_NAME_AUDIT.tsv`
- `HYDRADG_HYDRALAMP_BOUNDARY.md`
- every current appendix A–Q
- current manuscript source and PDF build inputs.

## 2. First prove the documentary gap

Verify, do not assume, that current PR #38 Appendix E and F are materially thin.

Expected predecessor observations:

- `appendices/E_antigence.md` is effectively a one-line `RELATED_IMPLEMENTATION` admission label;
- `appendices/F_anticube_states.md` is effectively a pointer to a figure.

If current origin has changed, report the new contents and use the actual current state.

Set:

`APPENDIX_DOCUMENTATION_GAP=PASS|NOT_REPRODUCED`

## 3. Independently audit actual implementation work

Use exact Git state. Do not rely only on the ChatGPT prose.

### A. GettingScienceDone / mechanical scientific method

Expected source:

`biobitworks/gettingsciencedone`

Observed review SHA:

`484e42c865c9af947d7bcc34bb86468a5d8f83c3`

Verify:

- `specs/run-experiment.yaml`
- `specs/negative-results.yaml`
- specs directory for ablation, claim/output audit, prompt creation, data contract, FAIR, experiment discovery, handoff, export.

Confirm exactly which gates are implemented for CONFIRMATORY / EXPLORATORY / REPLICATION.

Confirm that the negative-result contract distinguishes:

`NULL_RESULT`
`UNDERPOWERED`
`TRUE_NEGATIVE`

and that underpowered non-rejection cannot silently become `TRUE_NEGATIVE`.

Do not claim this governance framework proves an empirical treatment effect.

### B. FCO / FCG

Expected source:

`biobitworks/fractal-custody-objects`

Observed review SHA:

`2431dd98178ef49b0cd0e28fde39826b98f69b71`

Check canonical governance/specification first.

Reverify bounded mechanism experiments before including numbers, including where present:

- model escalation/recompute experiment;
- fractal/Merkle divergence localization;
- continuous/provenance-vs-variance controlled example;
- real scientific-file/mzML admission experiment;
- any additional FMO experiment listed in Appendix G only if its summary is actually inspected.

Do not call SHA-256 truth, a signature, or a Merkle/MMR commitment.

### C. Antigence

Expected source:

`biobitworks/antigence`

Observed review SHA:

`060dba881293c226ee26b78d93780ef1ed9b2ba4`

Inspect:

- `README.md`
- `BENCHMARKS.md`
- benchmark JSONs if needed to recompute the table.

Verify the implemented AIS roles and interfaces.

Recompute/check the exact synthetic, curated and Devign numbers. Preserve the Devign near-chance/high-FPR result prominently. Do not present Antigence as generally effective.

Check whether the repo's proposal for embedding-based features / CodeBERT / VulBERTa / local Ollama embeddings is **future work** or executed evidence. It must remain future/proposed unless an actual frozen successor result exists.

### D. SeedGraph

Expected source:

`biobitworks/seedgraph`

Observed review SHA:

`f2f5d7ebf3914b4e167a28a5eee84c31e5970f5d`

Verify deterministic-first atomization/source custody design and exact HydraDG bounded readback evidence.

Preserve:

- bounded 25-source / 312-atom real-evidence positive result if exact receipt verifies it;
- any 163/163 traceability result only if exact receipt verifies it;
- whole-project V1A hierarchy build = PARTIAL/NONTERMINAL unless a successor terminal readback receipt now exists.

### E. Ollarma

Expected source:

`biobitworks/ollarma`

Observed review SHA:

`d0cf78d4a1c68fdd6e2cd6e17075da6e0f4c399b`

Verify bounded local execution/orchestration, receipts, model identity/config capture, recovery gates and MCP/HTTP surfaces relevant to this paper.

Any byte-identical LLM test is configuration/host/model bounded. Never generalize it to universal model determinism.

### F. HydraLamp

Expected source:

`biobitworks/hydralamp`

Observed latest in ChatGPT review:

`0799e94e87e43359180b28b2e9cc51232a50b116`

Verify exact systems evidence independently:

- 4×25 perturbation matrix;
- tamper suite;
- concurrency;
- replay/restart;
- provider/Runtype repair ladder and quota-blocked states.

Do not allow these systems results to promote EXP-008/009.

Keep future biological/biopharma HydraLamp use as PLANNED unless independently executed.

Also preserve any name/IP caution in operator-only material; do not turn a preliminary trademark review into legal advice.

### G. Vitaology

Expected source:

`biobitworks/vitaology`

Observed review SHA:

`0efab4aa3859cebf53df8bcb4b90083a1a88beb4`

Verify from actual repo/receipts, not ChatGPT summary:

- EXP-001 toolchain proof;
- EXP-002 22,096 sentence atoms;
- EXP-004 50 atoms / 100% coverage / 1,792 annotations / 4 OBO ontologies;
- EXP-005 75 atoms / 7/7 MESI / 89 logic-map edges;
- EXP-006 anti-feature lints;
- EXP-003 classifier calibration and the exact human-rating gate.

This is RELATED_IMPLEMENTATION only. It cannot become HydraDG primary scientific evidence.

### H. Vithia companion

Resolve exact current public/custody sources.

Expected references include:

- Zenodo DOI `10.5281/zenodo.21829929`
- gated HF artifact `biobitworks/fco-vithia-fmo-076`

Do not invent a standalone Vithia GitHub repository if none resolves.

Do not reuse any historical hard-coded/synthetic Vithia matrix as empirical evidence.

Do not describe model scale/base lineage unless the model card/receipt proves it.

Treat gated/CC-BY-NC-ND material as citation/reference evidence unless redistribution rights are independently satisfied.

## 4. ML complement doctrine

Audit and, if supported, retain this architectural statement:

> Probabilistic ML components may expand representation, retrieval, hypothesis generation, or interpretation; deterministic controls establish source identity, experimental contracts, scoring/verifiability, and claim promotion.

For each component produce a row:

`COMPONENT`
`DETERMINISTIC_CORE`
`ML_COMPLEMENT`
`ACTUALLY_EXECUTED_OR_PROPOSED`
`VERIFIER/GATE`
`CLAIM_CEILING`

Do not blur "uses an ML component" with "the ML output is authoritative."

## 5. Federation terminology

Use **governed component federation**, **cross-project implementation federation**, or similar.

Do NOT call it federated learning unless there is an actual distributed/federated training protocol.

A federation-wide signature/root must remain NOT_ESTABLISHED unless one was actually constructed across the admitted components.

## 6. Appendix E integration target

Create a successor branch from the current authoritative solo recovery lineage, e.g.:

`cursor/newinml-solo-appendix-federation-v4-20260829`

Do not merge directly into main.

Replace/expand the existing Appendix E with a verified version containing:

E.1 evidence boundary
E.2 mechanical scientific governance
E.3 FCO/FCG shared custody interface
E.4 Antigence/AIS architecture
E.5 actual Antigence mixed benchmarks
E.6 ML-complement contract
E.7 implementation federation topology
E.8 bounded transfer examples (including Vitaology and Vithia companion if admitted)
E.9 licensing/double-blind boundary
E.10 explicit claim ceiling

Also strengthen Appendix F only after resolving the **canonical Anticube source**. Do not reconstruct Anticube from chat memory. Preserve the canonical `SELF/NON-SELF × SAFE/NON-SAFE` semantics and any time/context dependence actually specified by the source. If canonical semantics cannot be resolved, leave Appendix F blocked rather than inventing them.

Create or update Appendix G/I as needed so Appendix E does not become an unstructured catalogue.

## 7. Double-blind split

Maintain two versions:

### Reviewer-facing anonymous projection

- functional labels instead of identifying sibling project names where necessary;
- no private GitHub URLs;
- no author-identifying model/repo links unless self-citation audit explicitly permits third-person citation;
- no private source snippets;
- no personal paths/hostnames in visible paper/supplement;
- sanitized PDF metadata.

### Operator/internal source map

Retain:

- actual repository/project names;
- commit SHAs;
- file paths;
- DOIs/model IDs;
- license states;
- evidence admission decisions;
- exact reverse traces.

Never upload the internal source map as the blind supplement.

## 8. Licensing / OpenReview risk gate

Build a file-level supplemental BOM.

For every file/asset classify:

`OWNED_OR_AUTHORED`
`APACHE_2_0`
`CC_BY_4_0`
`CC_BY_NC_ND_4_0`
`PUBLIC_DOMAIN`
`UPSTREAM_OTHER`
`PRIVATE`
`UNKNOWN`

and:

`REDISTRIBUTION_ALLOWED=YES|NO|UNKNOWN`
`DERIVATIVE_ALLOWED=YES|NO|UNKNOWN`
`ANONYMOUS_UPLOAD_ALLOWED=YES|NO|UNKNOWN`
`OPENREVIEW_INCLUDE=YES|NO`

Default rules:

- derived numeric summaries and our original anonymous diagrams: include if source/evidence is valid;
- private repo code: do not bundle merely for reproducibility;
- gated model weights: do not bundle;
- CC-BY-NC-ND research artifact: cite/reference, do not silently repackage or adapt;
- third-party datasets: do not rebundle unless upstream redistribution permission is verified;
- third-party figures/screenshots: cite rather than reproduce unless rights are clear;
- secrets/private keys/tokens: never include.

Do not assert that OpenReview/non-archival status removes licensing obligations.

## 9. Venue / NeurIPS requirement gate

Fresh-check official NewInML + NeurIPS/OpenReview requirements before final build.

At minimum verify:

- NewInML main paper = 2–8 pages excluding references;
- NeurIPS 2026 workshop template / `dblblindworkshop`;
- double-blind anonymity covers paper, supplement and linked materials;
- checklist is included and answers are truthful;
- exact commands/environment for main results are provided where feasible;
- statistical uncertainty/power limitations are explicit;
- code/data access answer is truthful, not forced YES;
- compute-resource accounting remains truthful if incomplete.

**Do not assume technical appendix pages are excluded from NewInML's workshop-specific 2–8-page limit.**

Preferred release topology:

- main PDF within 2–8 non-reference pages;
- expanded A–Q appendix as a separate anonymous supplement only if the live OpenReview venue permits supplementary files;
- otherwise compress to fit the workshop rule and retain full internal/camera-ready dossier.

## 10. Primary scientific invariants

These are non-negotiable unless exact successor evidence proves otherwise:

- EXP-008 = UNDERPOWERED; effect not established.
- EXP-009 primary = UNDERPOWERED; ordering/treatment effect not established.
- EXP-009 exploratory/directional secondary not promoted.
- HydraLamp systems positives do not alter those primary conclusions.
- Qwen3.8 successor nonterminal unless exact completed successor receipt now exists.
- SGLang/CUDA/Cloudflare OS not primary evidence unless actually executed and verified.
- SeedGraph whole-project large build not complete without terminal readback-safe receipt.
- SHA-256 = byte identity, not signature/truth/privacy.
- `SIGNATURE_STATE=SIGNED` only after actual authorized signing.
- `MERKLE_MMR_STATE=COMMITTED` only after actual construction + verification receipt.

## 11. Reproduce/build

Run the existing deterministic reproduction path first:

```bash
make newinml-reproduce
# and/or
python3 scripts/reproduce_newinml.py --verify
```

Do not rerun model science merely to improve the appendix. This task is source/evidence reconciliation and publication construction unless a deterministic verification artifact is missing.

Build the candidate anonymous PDF/supplement.

Record:

- main PDF page count;
- content pages excluding references;
- supplement files;
- PDF SHA-256;
- supplement ZIP SHA-256;
- source commit SHA;
- build environment;
- exact command;
- anonymity scan;
- link scan;
- license BOM result;
- reverse-trace result;
- human-review-needed items.

## 12. Required outputs

Write at minimum:

`paper/newinml2026_solo/successor_recovery/appendices/E_gsd_antigence_federation.md`

`paper/newinml2026_solo/successor_recovery/APPENDIX_ADMISSION_MATRIX.tsv`

`paper/newinml2026_solo/successor_recovery/ML_COMPLEMENT_MATRIX.tsv`

`paper/newinml2026_solo/successor_recovery/FEDERATION_IMPLEMENTATION_MATRIX.tsv`

`paper/newinml2026_solo/successor_recovery/LICENSE_REDISTRIBUTION_MATRIX.tsv`

`paper/newinml2026_solo/successor_recovery/APPENDIX_SOURCE_MAP_INTERNAL.md`

`paper/newinml2026_solo/successor_recovery/ANON_APPENDIX_SOURCE_MAP.md`

`paper/newinml2026_solo/successor_recovery/APPENDIX_REQUIREMENTS_GATE.json`

`paper/newinml2026_solo/successor_recovery/CHATGPT_REVIEW_RECONCILIATION.json`

and updated manuscript/supplement/checklist files only when the corresponding gate passes.

## 13. Final independent questions

Answer explicitly:

1. Did Appendix E materially document implemented work rather than names/future ideas?
2. Which statements from ChatGPT were unsupported or overstated?
3. Did any actual repository SHA move since ChatGPT's review?
4. Does every quantitative Appendix E claim reverse-trace?
5. Are primary/system/related/development/planned evidence classes separated?
6. Is ML consistently treated as complementary/probabilistic where appropriate?
7. Is Vitaology now admissible as a related implementation at a bounded ceiling?
8. Is Vithia still only companion/gated evidence, or did you resolve stronger executable evidence?
9. Is canonical Anticube semantics resolved?
10. Does the anonymous supplement leak any project/author identity?
11. Are all supplemental assets redistribution-safe for OpenReview?
12. Does the final main PDF obey the workshop 2–8-page rule?
13. Does the NeurIPS checklist remain truthful?
14. Did Protein Hinge/team admission remain zero?
15. What is the exact earliest remaining divergence/blocker?

## 14. Commit/push

Commit the verified successor on the new Cursor branch.

Push it to origin.

Do not merge to main automatically.

Open/update a draft PR for independent human review.

Report exact:

`CURSOR_REVIEW_BRANCH`
`CURSOR_REVIEW_SHA`
`SOURCE_PR=38`
`SOURCE_SHA=38cdb62e72bd26a48b42e286b86303a949a545fa`
`PDF_SHA256`
`SUPPLEMENT_SHA256`
`ANONYMITY_GATE`
`LICENSE_GATE`
`PAGE_LIMIT_GATE`
`REVERSE_TRACE_GATE`
`CHECKLIST_GATE`
`PROTEIN_HINGE_ADMISSION_COUNT`

Then end with:

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
