# ANTIGRAVITY — HYDRADG CUSTODY REPAIR + PERMANENT IN-TURN FCO/FCG PROTOCOL v1
# Date: 2026-08-19
# Priority: HARD GATE before further release/scientific promotion
# Scope: local/canonical project custody. Do not rerun science unless a later gate explicitly requires it.

## WHY THIS IS REQUIRED

A citation-lineage regression occurred: the Enßlin & Weig 2010 source paper that motivated the
information-theoretic Gibbs-free-energy analogy was present in project evidence, but the release/UI
retained the derived G*/ΔG* implementation while dropping the load-bearing upstream source relation.

This is not merely a bibliography bug. It means the source should have been:

source bytes
→ hashed
→ atomized
→ materialized as canonical FCOs
→ connected through the canonical FCG
→ inherited by derived mathematical-design FCOs
→ projected to HydraDB
→ surfaced in KB/docs/UI citations.

Repair the custody chain mechanically and restore this behavior for every substantive turn.

---

# 0. AUTHORITY AND FAIL-CLOSED RULE

Before any custody mutation, locate and read in this order:

1. `FCO_FCG_CANONICAL_SPEC.md`
2. `CLAIM_CEILINGS.md`
3. `EVIDENCE_LEVELS.md`
4. `FCO_SCHEMA.json`
5. `FCG_SCHEMA.json`
6. `SIGNING_AND_KEYS.md`
7. current versioned canonical FCO/FCG implementation
8. current project custody/FCG store

Canonical/versioned files outrank chat recollection.

Do NOT invent:
- predicate names;
- FCO types that violate schema;
- prior turn hashes;
- signatures;
- Merkle/MMR commitments;
- "verified" status.

If a requested relationship has no canonical predicate, use the canonical extension mechanism or
record `PENDING_SCHEMA_RELATION` rather than inventing a relation.

A custody validation failure is a HARD GATE FAILURE.

---

# 1. CHECKPOINT CURRENT WORK BEFORE REPAIR

Do not discard current local/public-product work.

Record:

- current branch
- current HEAD
- worktree state
- latest canonical project FCG root
- latest valid turn-record root
- latest signature receipt, if any
- latest Merkle/MMR receipt, if any
- current HydraDB projection root/receipt
- current public-product branch state

Write:

`custody/CUSTODY_REPAIR_PRECHECK_20260819.json`

If working tree is dirty, create a normal checkpoint commit first.
Do not force push.
Do not reset away Antigravity or ChatGPT public-lane changes.

---

# 2. FIND THE LAST VALID IN-TURN CUSTODY ROOT

Locate the most recent turn where all of the following are actually evidenced:

- exact HUMAN input bytes or exact retained human-turn artifact;
- exact AI response bytes or retained AI-turn artifact;
- SHA-256 for each material turn object;
- canonical FCO materialization;
- canonical FCG append;
- parent turn root relation;
- project FCG validation;
- signature state explicitly recorded;
- Merkle/MMR state explicitly recorded.

Call it:

`LAST_VALID_TURN_RECORD_SHA256`
and
`LAST_VALID_PROJECT_FCG_ROOT`.

Do not infer these from prose alone if the actual object/receipt is absent.

---

# 3. RETROACTIVE GAP AUDIT — DO NOT FAKE "IN-TURN"

Audit all substantive project material after the last valid turn root up to the present.

For every recoverable object, classify:

- `DIRECT_HUMAN_INPUT`
- `AI_GENERATED_RESPONSE`
- `TOOL_RESULT`
- `EXTERNALLY_RETRIEVED_EVIDENCE`
- `DIRECTLY_SUPPLIED_FILE`
- `DETERMINISTIC_TRANSFORMATION`
- `PROBABILISTIC_MODEL_OUTPUT`
- `GIT_ARTIFACT`
- `DEPLOYMENT_ARTIFACT`
- `SCREENSHOT_ARTIFACT`
- `RECEIPT`
- `SUMMARY_ONLY`

For each exact byte-for-byte object that still exists:
1. hash exact bytes with SHA-256;
2. record actor/source;
3. record original or best-known chronology separately from scientific identity;
4. bind through canonical FCO implementation;
5. validate;
6. append using canonical FCG relationships;
7. retain parent/dependency references.

If only a summary or paraphrase exists:
- hash only the bytes that actually exist;
- mark:
  `RETROACTIVE_CUSTODY_RECONSTRUCTION_FROM_AVAILABLE_RECORD`
- add:
  `PENDING_ORIGINAL_TURN_CAPTURE`
- NEVER manufacture the missing original hash;
- NEVER label the reconstruction as the original in-turn record.

Create:

`custody/CUSTODY_GAP_AUDIT_20260819.json`
`custody/CUSTODY_GAP_REPAIR_RECEIPT_20260819.json`

The gap audit must explicitly identify the citation-lineage failure as an earliest divergent dependency.

---

# 4. RE-INGEST THE ENSSLIN–WEIG PAPER AS A CANONICAL SOURCE

Locate the exact local project copy of:

Torsten A. Enßlin and Cornelius Weig
"Inference with minimal Gibbs free energy in information field theory"
Physical Review E 82, 051112 (2010)
DOI: 10.1103/PhysRevE.82.051112

Use the exact supplied PDF bytes, not a newly downloaded replacement, as the directly supplied source
when available.

Required source object metadata:

- exact local source path (private/local receipt only if path is not public-safe)
- SHA-256 of exact PDF bytes
- DOI
- title
- authors
- journal
- year
- supplied-by = HUMAN
- evidence class = DIRECTLY_SUPPLIED_SOURCE
- rights/publication metadata
- source version / byte identity

If multiple duplicate PDF copies exist:
- hash each;
- if byte-identical, connect them through canonical duplicate/equivalence handling;
- select one canonical source byte identity;
- do not create independent scientific sources for byte-identical copies.

Create a source-ingestion receipt.

---

# 5. STRUCTURAL ATOMIZATION OF THE PAPER

Atomize only propositions actually supported by the supplied paper.
Preserve page/section/equation/span locators.

At minimum create bounded evidence/knowledge atoms for:

### EW-A1 — IFT introduction
The paper introduces minimal Gibbs free energy as an inference principle in information field theory
and uses it to construct approximate posterior/knowledge states.

### EW-A2 — energy/entropy combination
The paper argues that entropy alone is not an adequate inference criterion and combines an
internal-energy term with entropy in a free-energy functional.

### EW-A3 — approximate Gibbs form
For its Gaussian approximation, the paper writes an approximative Gibbs free energy of the form
`G~ = U~ - T S~` (paper Eq. 28; preserve exact equation locator in the atom).

### EW-A4 — inference role
The paper treats Gibbs free energy as an "information energy" whose minimization over the
approximating distribution identifies an optimized knowledge/posterior approximation.

### EW-A5 — cross-information / KL relation
At T=1, the paper relates the Gibbs-free-energy optimization to cross information /
Kullback-Leibler divergence between the Gaussian surrogate and the posterior.

### EW-A6 — scope limitation
These claims concern the paper's information-field-theory inference construction.
They do NOT by themselves establish that HydraDG's application-defined G* is physical
thermodynamic Gibbs free energy or identical to the paper's functional.

For every atom:
- exact source FCO dependency;
- page/section/equation locator;
- exact evidence class;
- source-support claim ceiling;
- canonical atom/FCO ID;
- no model-generated claim promotion.

Use deterministic extraction/atomization where possible.
If semantic boundaries require model judgment, label that transformation accordingly and preserve
the source span separately.

---

# 6. SEPARATE SOURCE CLAIMS FROM HYDRADG DESIGN CHOICES

Create distinct derived/design FCOs for HydraDG.

Do NOT encode these as claims made by Enßlin & Weig.

### HDG-G1 — analogy/design rationale
HydraDG adopts an information-state/free-cost analogy motivated in part by the information-theoretic
Gibbs/free-energy literature, including Enßlin & Weig.

### HDG-G2 — HydraDG G*
HydraDG's `G*` is an APPLICATION-DEFINED, DIMENSIONLESS governed information-state diagnostic.

Current project formula must be read from the canonical preregistration/config rather than guessed.
Where the currently authoritative definition is:

`G* = U* - tau*S_useful + gamma*S_irrelevant`

bind the exact formula/config root and weights/config source.

### HDG-G3 — delta definition
`ΔG*_t = G*_t - G*_reference`
only if this remains the canonical current definition.

### HDG-G4 — nonphysical boundary
HydraDG G*/ΔG*:
- is not measured in joules;
- is not measured in kcal/mol;
- does not assert a physical temperature;
- is not literal thermodynamic Gibbs free energy;
- is not identical to Enßlin & Weig's IFT functional.

### HDG-G5 — empirical independence
Lower G* does NOT automatically mean higher Hit@K, Recall@K, or end-to-end QA accuracy.
Those outcomes remain separate empirical measurements/null hypotheses.

### HDG-G6 — citation partition
Maintain separate upstream roles:
- Enßlin & Weig → primary information-field/Gibbs inference analogy;
- Shannon → entropy/information theory where used;
- Lin → Jensen-Shannon divergence / Cloud Drift lineage where used;
- Friston or other variational-free-energy references → secondary background only where actually relevant.

Do not let one citation substitute for another dependency.

---

# 7. BUILD THE FCG DEPENDENCY CHAIN

Using only predicates allowed by the canonical schema, represent the conceptual dependency:

Enßlin–Weig PDF Source FCO
→ exact Evidence/Span FCOs
→ EW KnowledgeAtoms
→ HydraDG mathematical-design/rationale FCO
→ canonical G* scorer/config FCO
→ ΔG* derived-state/result FCOs
→ Context Iceberg visualization FCO
→ Knowledge Base entry
→ documentation
→ public website artifact
→ screenshots/video/submission artifact

Also preserve:

Lin source
→ JSD atom
→ Cloud Drift scorer
→ Context Iceberg

and other valid source branches.

The final graph must make it mechanically impossible for a `G*`/`ΔG*` public artifact to resolve
without the upstream design-source dependency being discoverable.

If the graph already has a wrong/missing edge:
- do not rewrite history silently;
- append a correction/supersession/repair object using canonical predicates;
- identify the earliest divergent dependency.

---

# 8. HYDRADB IS A PROJECTION, NOT CUSTODY TRUTH

After canonical FCG append succeeds:

1. project the new/updated FCO/FCG delta to local HydraDB;
2. record project FCG root before/after;
3. record expected projected nodes/edges;
4. record observed nodes/edges;
5. select the G*/ΔG* Knowledge/Design FCO as a traceability canary;
6. traverse HydraDB back to the Enßlin–Weig source FCO / source SHA;
7. compare exact canonical IDs;
8. PASS only if identity matches.

Write:

`custody/GIBBS_LINEAGE_HYDRADB_PROJECTION_RECEIPT_20260819.json`

Required:
`HYDRADB_GIBBS_LINEAGE_CANARY=PASS`

HydraDB must not become the source of canonical identity.

---

# 9. UPDATE KB / DOCS / UI FROM THE FCG, NOT BY HAND ONLY

Update all current project/public surfaces that mention:

- G*
- ΔG*
- information-state free energy/free cost
- Context Iceberg
- Cloud Drift vs G*
- Gibbs abstraction

Required behavior:

### Knowledge Base
The `G*` and `ΔG*` entries must expose:
- definition;
- nonphysical claim boundary;
- Enßlin & Weig source;
- related source FCO;
- related HydraDG design FCO;
- scorer/config root;
- related null hypotheses;
- separate Hit@K/Recall@K metrics.

### Mathematical documentation
Add a source-lineage section showing:

Enßlin & Weig 2010
→ information-theoretic Gibbs/free-energy inference precedent
→ HydraDG design analogy
→ application-defined G*
→ ΔG*

and separately:

Lin
→ JSD
→ Cloud Drift.

### Public UI
A judge must be able to click from `G*` or `ΔG*`:
`What is this?`
→ KB
→ source/reference
→ FCO/FCG lineage
→ claim boundary.

Do not claim the source paper validates HydraDG's empirical metric.

---

# 10. RESTORE PERMANENT IN-TURN CUSTODY

From this point forward, EVERY SUBSTANTIVE HUMAN/AI/TOOL TURN in this project must execute or
produce a canonical handoff for this sequence:

### A. HUMAN INPUT
- capture exact user bytes when available;
- SHA-256;
- actor = HUMAN;
- canonical FCO validation/materialization.

### B. SOURCE/TOOL RESULTS
For every material source/file/tool result:
- exact retained payload or exact source identity;
- SHA-256 where bytes are available;
- evidence class;
- source/version metadata;
- FCO materialization.

### C. ATOMIZATION
If a new source materially changes reasoning/design:
- structurally/semantically atomize;
- preserve exact span locator;
- bind atoms to source FCO;
- no detached citations.

### D. AI TRANSFORMATION
- capture exact AI artifact/response bytes when available;
- SHA-256;
- actor = AI;
- transformation type;
- input dependencies;
- evidence/claim ceiling.

### E. FCG APPEND
Canonical order:

source/input FCOs
→ transformation FCO
→ derived evidence/design FCO
→ claim FCO
→ artifact/response FCO

Append to canonical project FCG and connect to prior turn root.

### F. HYDRADB PROJECTION
Only after canonical append:
- project required public/query fields;
- deterministic traceability canary.

### G. HASH RECEIPT
Every substantive turn gets:
- HUMAN_TURN_SHA256
- SOURCE/TOOL roots
- AI_RESPONSE/ARTIFACT_SHA256
- TURN_RECORD_SHA256
- PARENT_TURN_RECORD_SHA256
- PROJECT_FCG_ROOT_BEFORE
- PROJECT_FCG_ROOT_AFTER
- HYDRADB_PROJECTION_RECEIPT
- claim ceiling
- signature state
- Merkle/MMR state.

### H. SIGNATURE
Read `SIGNING_AND_KEYS.md`.

If the authorized project private key is available in the authorized signing environment:
- sign only the canonical object/root scope specified by the spec;
- verify signature;
- record public key ID / signature receipt.

If the private key is NOT available:
- DO NOT sign with a toy/example key;
- write `PENDING_EXTERNAL_PRIVATE_KEY_OPERATION`;
- generate the canonical signing handoff;
- preserve the unsigned hash/root being handed off.

Hashing is not signing.
Signing is not Merkle commitment.
Merkle commitment is not scientific verification.

### I. MERKLE/MMR
Only report committed if the actual project operation occurs and receipt exists.
Otherwise record:
`NOT_PROJECT_COMMITTED`.

No substantive turn may silently omit this state.

---

# 11. AUTOMATED CUSTODY LINTER / HARD GATE

Add or repair a deterministic checker, e.g.:

`scripts/check_turn_custody_completeness.py`

It should fail if a substantive turn/artifact has:
- missing actor label;
- missing exact-byte hash where bytes exist;
- missing source dependency;
- missing evidence class;
- missing claim ceiling;
- missing FCO validation receipt;
- missing FCG append receipt;
- broken parent turn root;
- public G*/ΔG* artifact with no Enßlin–Weig lineage;
- public Cloud Drift artifact with no JSD lineage;
- signature described as complete without signature receipt;
- Merkle/MMR described as committed without receipt.

Release gate must include this checker.

Required:
`TURN_CUSTODY_COMPLETENESS=PASS`
`GIBBS_SOURCE_LINEAGE=PASS`

---

# 12. RETROACTIVE STATUS MUST REMAIN VISIBLE

The repaired interval must not be relabeled as though custody happened in-turn originally.

For every reconstructed historical object use an explicit state such as:

`RETROACTIVE_CUSTODY_RECONSTRUCTION`

and when original bytes are unavailable:

`PENDING_ORIGINAL_TURN_CAPTURE`.

Add one project-level repair artifact documenting:
- when the gap was discovered;
- why it mattered;
- earliest divergent dependency;
- what was recovered exactly;
- what could not be recovered;
- what new hard gate prevents recurrence.

This repair artifact itself must be hashed, FCO-bound and added to the FCG.

---

# 13. GIT CHECKPOINT / TOKEN-EXHAUSTION RULE

After each completed phase:
1. validate canonical FCO/FCG;
2. hash receipts;
3. commit;
4. push safe branch;
5. update `CUSTODY_REPAIR_RESUME.md`.

Never leave multiple completed phases unpushed.

If context/tokens become low:
STOP.
Do not start another phase.

Write and push:

`CUSTODY_REPAIR_RESUME.md`

with:

LAST_COMPLETED_PHASE=
BRANCH=
LOCAL_HEAD=
REMOTE_HEAD=
LAST_VALID_TURN_RECORD_SHA256=
PROJECT_FCG_ROOT_BEFORE=
PROJECT_FCG_ROOT_AFTER=
GIBBS_SOURCE_FCO=
GIBBS_ATOM_ROOT=
GIBBS_DESIGN_FCO=
HYDRADB_GIBBS_LINEAGE_CANARY=
TURN_CUSTODY_COMPLETENESS=
SIGNATURE_STATE=
SIGNING_HANDOFF=
MERKLE_MMR_STATE=
CURRENT_BLOCKER=
NEXT_COMMAND=

---

# 14. FINAL ACCEPTANCE GATE

Do not report PASS until:

ENSSLIN_WEIG_SOURCE_HASHED=PASS
ENSSLIN_WEIG_SOURCE_FCO=PASS
ENSSLIN_WEIG_ATOMIZATION=PASS
HYDRADG_GSTAR_DESIGN_SEPARATED_FROM_SOURCE_CLAIMS=PASS
GSTAR_FCG_LINEAGE=PASS
DELTAGSTAR_FCG_LINEAGE=PASS
JSD_CLOUDDRIFT_LINEAGE=PASS
HYDRADB_GIBBS_LINEAGE_CANARY=PASS
KB_CITATION_LINEAGE=PASS
PUBLIC_UI_CITATION_LINEAGE=PASS
RETROACTIVE_GAP_AUDIT=PASS
NO_FAKE_PRIOR_TURN_HASHES=PASS
TURN_CUSTODY_COMPLETENESS=PASS
CANONICAL_FCG_VALIDATION=PASS
GIT_PUSH=PASS

Signature may be:
PASS
or
PENDING_EXTERNAL_PRIVATE_KEY_OPERATION

but must never be omitted or falsely promoted.

Merkle/MMR may be:
PASS
or
NOT_PROJECT_COMMITTED

but must never be omitted or falsely promoted.

Final claim ceiling:
`CUSTODY_LINEAGE_REPAIR_AND_GSTAR_SOURCE_BINDING_ONLY`

This operation does not itself validate G* as a predictor of retrieval quality.

---

# 15. FINAL CONSOLE OUTPUT

Print:

CUSTODY_REPAIR:
BRANCH:
COMMIT:
LAST_VALID_TURN_ROOT:
RETROACTIVE_GAP:
ENSSLIN_WEIG_PDF_SHA256:
ENSSLIN_WEIG_SOURCE_FCO:
ENSSLIN_WEIG_ATOM_ROOT:
HYDRADG_GSTAR_DESIGN_FCO:
GSTAR_CONFIG_ROOT:
PROJECT_FCG_ROOT_BEFORE:
PROJECT_FCG_ROOT_AFTER:
HYDRADB_GIBBS_LINEAGE_CANARY:
KB_LINEAGE:
PUBLIC_UI_LINEAGE:
TURN_CUSTODY_COMPLETENESS:
SIGNATURE:
SIGNING_HANDOFF:
MERKLE_MMR:
GIT_PUSH:
CLAIM_CEILING:
BLOCKER:
NEXT:

If all required gates pass:
`NEXT=RESUME_RELEASE_WITH_PERMANENT_IN_TURN_CUSTODY`
