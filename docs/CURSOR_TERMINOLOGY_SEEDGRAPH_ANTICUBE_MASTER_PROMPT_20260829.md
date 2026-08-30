# HydraDG — Terminology Matrix + Total SeedGraph Ingest + Dynamic Anticube/Context Priority

Date: 2026-08-29

Execution host: `magicSTUDIObox.local`

Repository: `biobitworks/hydradg`

Mode: governed successor / no historical rewrite

## Objective

Extend the terminology/prior-art red-team lane into the full HydraDG state-transition thesis:

`governance invariant -> source/input delta -> deterministic analysis -> evidence/atom delta -> FCG delta -> CFMO/context-score delta -> optional verified MMR append -> next state`

This run must do four things together without conflating them:

1. build and execute the terminology/search matrix, including MeSH/GO/ECO and named prior art;
2. continue **total import and ingest** through the SeedGraph framework in bounded, read-back-verified batches;
3. deconstruct the first admitted publication document into atoms of knowledge, including prose, citations, figures, tables, captions, and reported values, then classify candidate Seeds of Truth;
4. maintain a **time-varying priority queue** in which secrets, blockers, Anticube state, HydraDG context scores, and scientific relevance are recomputed after every bounded action and every agent response.

Do not assume Anticube classification is permanent. It may change as context, requirements, source authority, contradictions, or evidence change.

Do not assume a Seed of Truth is permanent. Preserve its history and supersession/counterevidence rather than rewriting it.

---

## 0. Authority and hard rules

Before doing substantive work, read in authority order:

1. current explicit human instruction;
2. `PROJECT_CONTROL.yaml`;
3. `FCO_FCG_CANONICAL_SPEC.md`;
4. `CLAIM_CEILINGS.md`;
5. `EVIDENCE_LEVELS.md`;
6. `FCO_SCHEMA.json` / `FCG_SCHEMA.json`;
7. `SIGNING_AND_KEYS.md`;
8. current versioned implementations;
9. prior conversation/history.

Preserve:

- positive;
- null;
- negative;
- underpowered;
- failed;
- timeout;
- blocked;
- abstention;
- contradictory;
- superseded outcomes.

Never promote a probabilistic model output directly into canonical truth.

SHA-256 establishes byte identity only.

`SIGNATURE_STATE=SIGNED` only after an actual authorized private-key signing operation.

`MERKLE_MMR_STATE=COMMITTED` only after actual leaves, ordering, algorithm, root, append, and verification receipt exist.

Historical SeedGraph V1 identities must not be silently rewritten.

---

## 1. Mandatory priority header after every bounded action or response

Every Cursor/agent status response, every batch report, and every actionable table must begin with these three sections:

```text
OPERATOR_ACTION_QUEUE
SECRET_QUEUE
EXECUTION_QUEUE
```

Every actionable row must contain at least:

```text
row_id
priority_before
priority_after
anticube_before
anticube_after
hydradg_context_score_before
hydradg_context_score_after
context_score_delta
scientific_goal_alignment
blocking_dependency
actionable
secret_requirement
secret_state
next_action
```

If the canonical HydraDG context scorer exists, call it and record its exact version/config/root.

If it is not resolvable or not applicable:

```text
HYDRADG_CONTEXT_SCORE=NOT_COMPUTED
```

Do not invent a scalar.

### Priority policy

Use the canonical scorer if one exists. Otherwise preserve the following deterministic priority vector and do not collapse it into an unsupported scalar:

- `P0`: human secret or authorization blocks an otherwise-ready material lane;
- `P0`: custody/integrity defect can invalidate evidence or a selected artifact;
- `P1`: submission/deadline/source-authority conflict;
- `P1`: prior art invalidates or materially narrows a manuscript novelty claim;
- `P1`: missing source bytes/hash prevents evidence admission;
- `P2`: high-information scientific experiment/search or missing comparator;
- `P2`: first-document atomization gap preventing claim reverse trace;
- `P2`: total-ingest coverage gap for an admitted source family;
- `P3`: recall expansion, optional provider, secondary modality;
- `P4`: cosmetic/convenience/non-blocking work.

### Secret handling

For every required secret/credential record only:

```text
provider
secret_name
state=PRESENT|ABSENT|EXPIRED|UNKNOWN
safe_to_disclose=NO
value=NEVER_CAPTURED
blocks_row_id
priority
```

Never print, hash into public artifacts, copy, or commit the secret value.

A credential may be `SELF + NON_SAFE_TO_DISCLOSE + SAFE_TO_USE_IN_AUTHORIZED_RUNTIME`; run the canonical Anticube classifier instead of hard-coding that state.

If a secret becomes the earliest blocker of a ready lane, it moves to the top of `OPERATOR_ACTION_QUEUE` and `SECRET_QUEUE` in the **next response**.

---

## 2. Dynamic Anticube and context-score ledger

Create:

```text
paper/newinml2026_solo/federated_evidence/ANTICUBE_CONTEXT_TIMELINE.jsonl
paper/newinml2026_solo/federated_evidence/PRIORITY_TIMELINE.jsonl
```

For every material object/occurrence/context transition record:

```text
event_id
observed_at
content_identity
occurrence_id
context_fingerprint
object_type
source_fco
parent_fco
actor/tool/runtime
anticube_before
anticube_after
classification_reason_before
classification_reason_after
context_score_before
context_score_after
context_score_delta
new_evidence_ids
contradiction_ids
supersession_ids
claim_ceiling_before
claim_ceiling_after
priority_before
priority_after
```

Anticube is contextual. Do not attach one timeless safety/self label to content identity when occurrence/context is the real classification surface.

At minimum preserve the canonical 2x2 dimensions:

- SELF / NON_SELF
- SAFE / NON_SAFE

If the canonical implementation has additional dimensions, use them exactly.

Examples of legitimate state movement over time include:

- `SELF+SAFE -> SELF+NON_SAFE` when a once-correct object becomes unsafe under a submission requirement;
- `NON_SELF+SAFE -> SELF+SAFE` after an external source is admitted into governed project custody;
- `AMBIGUOUS -> SELF+SAFE` after authoritative provenance is resolved.

Never rewrite the earlier state. Append the transition.

---

## 3. Terminology matrix and red-team search

Create/recompute:

```text
research/terminology/TERM_UNIVERSE.jsonl
research/terminology/TERM_AXIS_MATRIX.json
research/terminology/TERM_PROVENANCE.jsonl
research/search/QUERY_MATRIX.jsonl
research/search/SEARCH_RUN_LEDGER.jsonl
research/search/RED_TEAM_PRIOR_ART_MATRIX.jsonl
research/search/CLAIM_PRIOR_ART_IMPACT_LEDGER.jsonl
```

Controlled/search axes must include:

- provenance / chain of custody / source lineage / derivation lineage;
- reproducibility / repeatability / scientific experimental error / negative/null/underpowered;
- AI / LLM / generative AI / agentic AI / multi-agent / agent memory / RAG;
- knowledge bases / biological ontologies / Gene Ontology / knowledge graph / nanopublication / research object;
- citation provenance / citation entailment / bibliographic identity / hallucinated references;
- versioning / state transition / state delta / requirement drift / temporal provenance / contradiction / supersession;
- SHA-256 / content addressing / Merkle/MMR / hash chain / in-toto / SLSA;
- evidence semantics / ECO / direct vs derived vs inference / counterevidence / claim ceiling;
- GO biological process / molecular function / cellular component and relation types;
- MeSH controlled terms mapping information science and biological domains.

Generate bounded deterministic combinations and named prior-art probes. Avoid uncontrolled Cartesian explosion.

Search at minimum:

- PubMed;
- Europe PMC;
- Crossref;
- OpenAlex;
- arXiv;
- GitHub;
- Hugging Face;
- OLS4;
- frozen/local GO/ECO/MeSH snapshots where available;
- local portfolio repositories.

PyPI/npm are implementation discovery surfaces, not novelty proof.

Each search response must be frozen, hashed, normalized, and admitted through SeedGraph before it can affect a manuscript claim.

Search snippets are `DISCOVERY_ONLY` until authoritative source identity is verified.

---

## 4. Total source universe — total import means terminal accounting, not all-success

Create/maintain one authoritative source universe:

```text
paper/newinml2026_solo/federated_evidence/TOTAL_SOURCE_UNIVERSE.jsonl
```

Enumerate every source relevant to the paper and its FCG, including:

- every paper/manuscript/PDF version;
- LaTeX/template/style/checklist sources;
- NewInML website, countdown, OpenReview, organizer/team requirement captures;
- all cited publications and citation-verification sources;
- experiment preregistrations, case manifests, raw results, terminal verdicts;
- HydraLamp, Cloudflare OS, Q38, SGLang, Vithia, HydraDB receipts used by the paper;
- datasets and dataset manifests;
- code/config/lockfiles materially affecting deterministic outputs;
- notebooks/protocols/lab notebook templates;
- figures, tables, images, screenshots, audio/media used as evidence;
- model/revision/tokenizer/runtime manifests;
- canonical GSD/FCO/FCG/SeedGraph governance sources;
- red-team prior-art sources admitted to related-work/novelty evaluation.

Every source universe row must eventually have exactly one terminal ingestion state:

```text
INGESTED_VERIFIED
PARTIAL
CORRUPT
UNREADABLE
NOT_READBACK_SAFE
EXCLUDED_WITH_REASON
EVAL_ONLY
UNVERIFIED_EXTERNAL
```

`TOTAL_IMPORT_COMPLETE=YES` means **terminal accounting across the declared universe**, not that every source succeeded.

Require:

```text
terminal_state_count == declared_source_universe_count
```

and for every admitted readable source:

- exact source SHA-256;
- parser/toolchain identity;
- source pointer/readback contract;
- zero unaccounted/orphan atoms;
- segment root verification.

Continue in bounded batches of <=25 sources unless memory/resource evidence requires smaller batches.

Do not restart a monolithic hierarchy build merely to claim total import.

---

## 5. Per-source SeedGraph daisy unit

For each source, execute:

```text
DISCOVER
-> FREEZE exact bytes
-> SHA-256
-> classify source/evidence role
-> deterministic triage
-> parse/atomize
-> validate source-byte and logical-record coverage where applicable
-> build source pointers
-> canonical FCO binding
-> FCG delta
-> Anticube/context classification
-> CFMO/context-score recomputation
-> segment root
-> readback
-> terminal receipt
```

Required per-source artifacts:

```text
SOURCE_MANIFEST.json
ATOMS.jsonl
EDGES.jsonl
INGEST_RECEIPT.json
SEGMENT_ROOT.json
TOOLCHAIN_MANIFEST.json
COVERAGE_REPORT.json
FAILURES.jsonl
```

If historical V1 hash profiles are encountered, preserve their profile and auditor result. Do not migrate IDs in place.

---

## 6. First-document deep deconstruction — prose + citations + figures + tables

Resolve `FIRST_DOCUMENT` deterministically:

1. use the currently selected NewInML submission PDF if a successor has been selected and frozen;
2. otherwise use the frozen green NewInML PDF;
3. record the exact selection reason, Git SHA, PDF SHA-256, and manuscript source SHA(s).

Create:

```text
paper/newinml2026_solo/first_document_seedgraph/
```

### Required hierarchy

Atomize the document at minimum as:

```text
Document
-> Page
-> Section/Subsection
-> Paragraph
-> Sentence
-> WordOccurrence / token-derived occurrence where useful
-> Proposition
-> ReportedValue
-> CitationCallsite
-> Figure
   -> figure image bytes
   -> panel
   -> caption
   -> label/legend text
   -> referenced manuscript sentence(s)
-> Table
   -> table
   -> row
   -> column
   -> cell
   -> caption
   -> footnote
   -> referenced manuscript sentence(s)
```

Do not use OCR when direct text/layout extraction is available and verifiable. OCR is a fallback derived transformation and must preserve engine/model/version/config/page-image hash/bbox lineage.

For figures and tables, require exact object-level links to the source(s) from which each visible claim/value is derived.

For every visible numeric value in a figure/table/manuscript sentence, create a reverse trace:

```text
visible value
-> occurrence
-> proposition/result atom
-> deterministic derivation/scorer
-> case/aggregate evidence
-> exact source bytes/hash
```

For every citation callsite:

```text
sentence/proposition
-> citation callsite
-> bibkey
-> bibliographic identity
-> authoritative publication identity
-> supported proposition
```

Do not count mere DOI existence as entailment.

### Required first-document gates

Report:

```text
SOURCE_BYTE_COVERAGE
LOGICAL_STRUCTURE_COVERAGE
MATERIAL_SENTENCE_TRACE_COVERAGE
REPORTED_NUMERIC_TRACE_COVERAGE
FIGURE_OBJECT_COVERAGE
TABLE_OBJECT_COVERAGE
CITATION_IDENTITY_COVERAGE
CITATION_ENTAILMENT_COVERAGE
ORPHAN_ATOMS
UNRESOLVED_POINTERS
```

Any denominator must be frozen and auditable.

---

## 7. Atoms of Knowledge and Seeds of Truth

Do not equate a hash, parsed sentence, or model classification with truth.

Use the canonical FCO/FCG representations if defined. Otherwise use governed sidecars and mark them non-canonical.

Suggested lifecycle states, only where compatible with canonical governance:

```text
CANDIDATE_ATOM
EVIDENCE_BOUND_ATOM
CANDIDATE_SEED_OF_TRUTH
VERIFIED_SEED_OF_TRUTH
CONTESTED_SEED_OF_TRUTH
SUPERSEDED_SEED_OF_TRUTH
RETRACTED_OR_INVALIDATED
```

A candidate Seed of Truth should record:

```text
seed_id
proposition
source_atom_ids
derivation_ids
counterevidence_ids
contradiction_ids
scope
valid_from
valid_until/superseded_at where applicable
evidence_class
verification_method
claim_ceiling
anticube_state_at_admission
context_score_at_admission
```

Requirements/source states may legitimately change the Anticube state or applicability of a Seed of Truth over time. Append a successor state; never mutate historical evidence silently.

Examples to test include:

- NewInML deadline/source reconciliation;
- OpenReview vs website workshop-date contradiction;
- style-file parity divergence and repair;
- reference/citation verification;
- EXP-008/EXP-009 `UNDERPOWERED` result state;
- bounded positive HydraLamp/SeedGraph systems-validation results;
- SeedGraph V1 hash-profile defects found by the custody auditor.

---

## 8. CFMO / context scoring over time

For every admitted batch and every material state transition compute, if the actual canonical implementation exists:

```text
CFMO_BEFORE
FCG_DELTA_ROOT
CFMO_AFTER
CFMO_DELTA
HYDRADG_CONTEXT_SCORE_BEFORE
HYDRADG_CONTEXT_SCORE_AFTER
CONTEXT_SCORE_DELTA
```

Context-score movement must be explainable by admitted evidence deltas.

Do not interpret a context-score change as an accuracy improvement unless a separate experiment establishes that relationship.

Keep `CloudDrift`, `Delta G*`, retrieval scores, Anticube classification, and claim ceilings separate unless their frozen scoring contract explicitly combines them.

---

## 9. Search/prior-art outputs become source candidates for total ingest

Every verified prior-art source discovered by the terminology matrix must enter `TOTAL_SOURCE_UNIVERSE.jsonl` with provenance from:

```text
query_id
-> search response SHA
-> discovered identifier
-> authoritative fetch
-> authoritative source SHA
-> SeedGraph source
-> mechanism/proposition atoms
-> claim-impact relation
```

Red-team conclusion states:

```text
NOT_NOVEL
PARTIALLY_OVERLAPPING
ORTHOGONAL
POSSIBLE_NOVEL_DELTA
UNRESOLVED
```

`POSSIBLE_NOVEL_DELTA` is not a novelty proof.

Any strong comparator that materially narrows a paper claim becomes `P1` immediately in the next queue update.

---

## 10. Deterministic replay and custody auditor

Run the delivered cross-project custody auditor over:

- terminology matrices;
- raw search responses;
- ontology snapshots;
- source-universe manifests;
- first-document atoms;
- figure/table atoms;
- citation ledgers;
- Seeds-of-Truth ledgers;
- Anticube/context timelines;
- FCG deltas.

Preserve findings such as:

```text
HASH_NOT_SPECIFIED
PREIMAGE_SERIALIZATION_AMBIGUOUS
SOURCE_HASH_MISMATCH
POINTER_UNVERIFIABLE
ORPHAN
PARSER_CONTRADICTION
PROBABILISTIC_DERIVATION
CORRUPT_PREDECESSOR
```

Run R1/R2/R3 on frozen source bytes for deterministic stages.

Separate:

- query-generation determinism;
- frozen-response normalization determinism;
- atomization determinism;
- live-search result drift.

Live web search sets need not remain identical over time. Their changes are new evidence deltas.

---

## 11. Bounded writeback / cross-project governance

After each verified batch:

```text
source batch
-> FCO/FCG delta
-> CFMO/context update
-> claim-impact update
-> Git commit/push
-> origin parity
```

Update GettingScienceDone with reusable contracts for:

- terminology/prior-art gate;
- source-universe/total-ingest terminal accounting;
- dynamic priority queue;
- secret escalation without secret disclosure;
- contextual Anticube transition ledger;
- first-document material-semantic coverage;
- Seeds-of-Truth lifecycle;
- FCG/CFMO delta contract.

Do not fork canonical FCO/FCG identity schemas.

SeedGraph owns deterministic source/atom/provenance transformation.

HydraDG is the reference state-transition implementation.

HydraDB remains projection/query/context graph, not source custody.

Ollarma may assist only unresolved semantic cases and remains probabilistic until deterministic verification promotes a derived result.

---

## 12. Required reporting cadence

After **every** bounded batch or meaningful agent response, report the priority header first, then:

```text
BATCH_ID=
NEW_SOURCE_COUNT=
TERMINAL_SOURCE_COUNT=
NEW_ATOM_COUNT=
NEW_AOK_COUNT=
NEW_SEED_OF_TRUTH_COUNT=
CONTESTED_SEED_COUNT=
SUPERSEDED_SEED_COUNT=
FIGURE_OBJECTS_ATOMIZED=
TABLE_OBJECTS_ATOMIZED=
CITATION_CALLSITES_VERIFIED=
ORPHAN_ATOMS=
UNRESOLVED_POINTERS=

CFMO_BEFORE=
CFMO_AFTER=
CFMO_DELTA=
HYDRADG_CONTEXT_SCORE_BEFORE=
HYDRADG_CONTEXT_SCORE_AFTER=
CONTEXT_SCORE_DELTA=

TOP_PRIORITY_CHANGE=
TOP_ANTICUBE_CHANGE=
TOP_CLAIM_CEILING_CHANGE=
```

If a secret/authorization need appears, stop only the affected lineage and move the human action to P0 in the **very next response** while continuing independent safe lanes.

---

## 13. Final closeout

Return:

```text
OPERATOR_ACTION_QUEUE=
SECRET_QUEUE=
EXECUTION_QUEUE=

TERM_COUNT=
QUERY_COUNT=
VERIFIED_PRIOR_ART_SOURCES=
PRIOR_ART_ATOMS=
HYDRADG_CLAIMS_TESTED=
NOT_NOVEL=
PARTIAL_OVERLAP=
POSSIBLE_NOVEL_DELTA=
UNRESOLVED_NOVELTY=

TOTAL_SOURCE_UNIVERSE_COUNT=
TOTAL_TERMINAL_SOURCE_COUNT=
TOTAL_VERIFIED_INGEST_COUNT=
TOTAL_PARTIAL_OR_FAILED_COUNT=
TOTAL_IMPORT_COVERAGE=
TOTAL_IMPORT_COMPLETE=

FIRST_DOCUMENT_ID=
FIRST_DOCUMENT_SHA256=
FIRST_DOCUMENT_ATOMS=
FIRST_DOCUMENT_AOK=
FIRST_DOCUMENT_SEEDS_OF_TRUTH=
FIRST_DOCUMENT_FIGURES=
FIRST_DOCUMENT_TABLES=
MATERIAL_SENTENCE_TRACE_COVERAGE=
REPORTED_NUMERIC_TRACE_COVERAGE=
FIGURE_OBJECT_COVERAGE=
TABLE_OBJECT_COVERAGE=
CITATION_ENTAILMENT_COVERAGE=
ORPHAN_ATOMS=

ANTICUBE_TRANSITIONS=
HYDRADG_CONTEXT_SCORE_INITIAL=
HYDRADG_CONTEXT_SCORE_FINAL=
CONTEXT_SCORE_DELTA=
CFMO_INITIAL=
CFMO_FINAL=
CFMO_DELTA=

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

## Final thesis boundary

The intended thesis to test—not assume—is:

> Governance is the invariant backbone. Data, requirements, actors, model outputs, results, failures, and source interpretations are deltas to a versioned FCG. Deterministic analysis governs admission and replay; CFMO/context scoring describes the resulting governed state; Anticube classification is contextual and may change as evidence changes; MMR commits history only when a real append is performed.

The experiment succeeds scientifically even when specific model/performance hypotheses are null or negative, provided the evidence transition is valid, complete, and replayable.
