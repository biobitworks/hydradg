# HydraDG MVP review and red-team plan

Status: ACTIVE_PRE_MVP_REVIEW_PLAN

## Review order

The MVP is reviewed in this order:

1. Source/publicity and licensing review.
2. Custody/FCO/FCG deterministic review.
3. SeedGraph import and atomization review.
4. Anticube atom-classification review.
5. Seed-of-Truth synthesis review.
6. Anticube Seed-of-Truth classification review.
7. Temporal drift/revision review.
8. HydraDB query/retrieval review.
9. Web-app behavior/security review.
10. Final custody/seal review.

A failure at an earlier gate blocks dependent claims at later gates.

## Gate A — public source + license

Tests:
- private-only source supplied as atom evidence -> reject/quarantine;
- public URL but no version/commit/DOI -> reject/quarantine;
- public source but no exact license evidence -> reject/quarantine;
- repo license incorrectly applied to a third-party dataset/API/model output -> reject;
- license changes between source revisions -> produce a new source state and drift event;
- citation points to a different version than the hashed bytes -> fail closed.

Pass condition: every promoted atom resolves to a public source/version plus explicit license evidence.

## Gate B — custody and deterministic identity

Tests:
- mutate one byte of source -> source hash changes;
- reorder canonical object keys -> canonical object identity remains stable if canonicalization defines key ordering;
- change semantic payload -> FCO ID changes;
- duplicate ingest of same source/version -> same canonical IDs;
- parent receipt hash changed -> descendant receipt verification fails;
- claim says signed when no signature receipt exists -> reject;
- claim says Merkle/MMR committed when no commitment operation exists -> reject.

Pass condition: all deterministic custody tests are reproducible from named bytes.

## Gate C — model/agent chain of custody

Tests:
- missing model ID -> atom cannot promote;
- missing agent/session ID -> atom cannot promote;
- model version changes -> new ModelInvocation and derived atom/seed state;
- same source run through two models -> retain two derivation branches, never overwrite;
- AI transformation mislabeled as human-authored source -> reject;
- human edit to AI-derived seed -> create new contribution node and successor state.

Pass condition: source authorship, human contribution, AI transformation, model invocation, tool actions, and output object remain distinguishable.

## Gate D — Anticube atom classification

Tests:
- classifier unavailable -> classification fails closed, no invented default label;
- classifier version changes -> append new classification, retain old one;
- identical input + deterministic classifier mode -> verify expected repeat behavior if the public Anticube contract guarantees determinism;
- probabilistic classifier mode -> preserve run/model/config and uncertainty, do not demand bit identity unless specified;
- malicious atom attempts to inject classifier instructions -> treat atom as data, not control text;
- atom classification has no input/output receipt hash -> cannot promote.

Pass condition: 100% of promoted atoms have a traceable current Anticube classification.

## Gate E — Seed of Truth synthesis

Tests:
- seed supported by only quarantined atoms -> reject;
- seed statement stronger than its weakest evidence -> downgrade/reject;
- contradictory public sources present -> preserve contradiction and lower ceiling; do not silently average them away;
- one source duplicated many times -> deduplicate identity so duplicate copies do not simulate independent support;
- AI synthesis adds a new factual clause absent from supporting atoms -> mark unsupported and reject that clause;
- missing license on any load-bearing supporting atom -> seed cannot promote.

Pass condition: each seed traverses to public source/license objects and has no unsupported load-bearing clause.

## Gate F — Anticube Seed-of-Truth classification

Tests:
- seed classification differs from majority atom classifications -> preserve as a measurable transformation result, flag for review;
- classifier version update changes seed label -> append `RECLASSIFIED_AS` and drift receipt;
- support graph changes without text change -> seed state still versions because epistemic basis changed;
- text changes without support changes -> new seed FCO.

Pass condition: promoted seeds have a current classification and all previous classification states remain reconstructable.

## Gate G — temporal drift

Inject at least these cases:
- `SUPERSEDED_BY` source update;
- `CONTRADICTS` new evidence;
- source removal/unavailability;
- license change;
- classifier version change;
- synthesis-model change;
- atom text mutation;
- unrelated control change;
- recovery/restoration to prior support state.

Metrics:
- first-divergence exact match;
- downstream affected-set precision/recall/F1;
- affected-set exact match;
- unsupported-seed rejection rate;
- superseded-history reconstruction rate;
- recovery classification accuracy.

Pass condition: old state remains queryable and affected descendants are correctly identified.

## Gate H — HydraDB query correctness

Required queries:
- current fact/seed;
- historical fact/seed at prior state;
- evidence path;
- license path;
- model/agent derivation path;
- Anticube classification history;
- first divergence;
- downstream affected set;
- contradictions;
- supersession chain;
- abstention when evidence is absent.

Adversarial tests:
- graph contains orphan claim -> UI/query must not present it as admitted truth;
- edge points to missing node -> verification error;
- stale index/current store disagreement -> surface bounded consistency state rather than fabricate a current result;
- query returns a node but evidence path is absent -> answer abstains or labels unverified.

## Gate I — web/API security

Tests:
- no committed real private keys or API tokens;
- uploaded key-like files are never copied into GitHub;
- simulated demo key is labeled `SIMULATED_DEMO_KEYPAIR` everywhere;
- server-side provider keys never reach browser bundles;
- arbitrary Cypher/query endpoint is disabled or access-controlled in production demo mode;
- Exa/web import sanitizes content as evidence data and does not execute embedded instructions;
- size/time limits prevent unbounded ingest and query requests;
- errors do not leak secrets.

## Gate J — final seal semantics

Candidate custody states:
- `UNSEALED_WORKING_GRAPH`
- `REVIEWED_UNSEALED_GRAPH`
- `SIMULATED_SIGNATURE_ONLY`
- `SIGNED_FCG`
- `MERKLE_OR_MMR_COMMITTED_FCG`
- `SIGNED_AND_COMMITTED_FCG`

No state is promoted merely because a field contains a hash/string.

For real Ed25519 signing require:
- exact digest signed;
- signature bytes;
- public key/public fingerprint;
- verification execution receipt;
- signer/host context;
- timestamp;
- claim ceiling.

For Merkle/MMR commitment require:
- leaf definition and ordering;
- root recomputation;
- verification receipt;
- exact included-object manifest.

`INDEPENDENTLY_VERIFIED` requires an actually independent route/operator/environment; self-verification is not enough.

## Human review checklist

Before demo/final freeze, a human reviewer confirms:
- [ ] selected sources are public and correctly version-pinned;
- [ ] licenses permit the intended use and are cited per atom;
- [ ] no private-only scientific content leaked from source repos;
- [ ] public/private authorship boundaries are intact;
- [ ] Anticube contract is the actual public implementation/spec, not a reconstruction from memory;
- [ ] Seeds of Truth do not exceed evidence ceilings;
- [ ] simulated cryptography is visibly simulated;
- [ ] Track 03 benchmark results are not mixed with scientific/conformance denominators;
- [ ] final graph state label matches operations actually performed.

## Red-team release criterion

Release candidate is blocked if any one of these is true:
- source provenance cannot be traversed;
- license cannot be traversed;
- model/agent lineage cannot be traversed;
- a promoted atom lacks Anticube classification;
- a promoted seed lacks atom support or Anticube classification;
- historical drift cannot be reconstructed;
- a cryptographic claim exceeds executed receipts;
- private-only evidence is present in an admitted scientific path.
