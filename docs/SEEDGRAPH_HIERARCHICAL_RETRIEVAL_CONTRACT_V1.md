# HydraDG SeedGraph Hierarchical Retrieval Contract v1

## Status

This contract defines a new experimental retrieval lane. It does not mutate, reinterpret, or replace V11 or the earlier K5/K10 retrieval evidence.

V11 remains a direct/oracle/full-context baseline lineage. Prior null/negative results remain valid only for the exact configurations that produced them.

## Objective

Reduce the amount of source prose a model must repeatedly read by navigating a content-addressed hierarchy of increasingly informative evidence objects.

The architecture separates:

1. **semantic/structural lookup** — find candidate object IDs;
2. **context enrichment** — rank candidate paths using atom-level context scores, score deltas, variance, coverage gain, and dereference cost;
3. **cryptographic identity** — SHA-256 verifies canonical object/source bytes;
4. **lazy source retrieval** — source pointers dereference only the evidence selected by the path;
5. **custody/governance** — FCO/FCG lineage records source, transform, query, retrieval path, response, and evaluator boundaries.

A SHA-256 digest is never treated as a semantic similarity function.

## Core hierarchy

Source evidence is represented by nested FCOs:

```text
SOURCE_FILE_FCO
  -> DOCUMENT_OR_SESSION_FCO
     -> PARAGRAPH_OR_TURN_FCO
        -> SENTENCE_FCO
           -> ATOM_OCCURRENCE_FCO
              -> SEED_ATOM_FCO
```

A query is also an FCO:

```text
QUESTION_FCO
  -> QUESTION_ATOM_OCCURRENCE_FCO
     -> SEED_ATOM_FCO
```

A model answer becomes a later derived FCO:

```text
QUESTION_FCO
  -> RETRIEVAL_PATH_FCO
     -> EVIDENCE_PACKET_FCO
        -> MODEL_RESPONSE_FCO
           -> DETERMINISTIC_EVALUATION_FCO
```

Gold/reference labels remain EVAL_ONLY and are never included in the model-visible graph/index.

## Why separate atom identity from atom occurrence

The same canonical seed can occur in many source locations.

`SEED_ATOM_FCO` identifies the canonical seed content once.

`ATOM_OCCURRENCE_FCO` identifies a specific occurrence and contains the source pointer and parent hierarchy location.

This preserves deduplication without losing provenance.

## Canonical object identity

Every FCO has:

- `object_id` — stable typed ID, normally `<type>:<sha256>`;
- `object_sha256` — SHA-256 of canonical bytes for the object identity contract;
- `object_type`;
- `visibility` — `MODEL_VISIBLE`, `MODEL_VISIBLE_SAFE`, `EVAL_QUERY`, or `EVAL_ONLY`;
- `source_sha256` when derived from source bytes;
- source pointer when the object is a source occurrence;
- parent/child FCG edges.

SHA-256 establishes byte identity only. It does not establish a digital signature.

## Source pointers

Large source payloads remain in their canonical source files. The graph stores compact pointers.

A pointer MAY include:

- dataset ID;
- source path;
- source file SHA-256;
- storage kind (`PARQUET`, `JSON`, `JSONL`, etc.);
- row-group index when available;
- row index or stable row key;
- field path;
- nested item/turn index;
- character span within the field;
- expected selected-text SHA-256.

For Parquet, a logical row key is authoritative for portability; row-group/row-in-group fields are optional optimization metadata.

Dereference verification requires:

```text
source file SHA-256 matches frozen source
AND
selected bytes SHA-256 matches pointer receipt
```

## Deterministic seed atomization v1

The v1 zero-model implementation uses deterministic lexical/structural seeds so that graph construction is reproducible without a probabilistic extractor.

For each sentence/question:

1. Unicode NFKC normalization;
2. lowercase for lookup key only;
3. tokenize alphanumeric words plus internal `_`, `-`, `/`, `.`, and `:` where meaningful;
4. remove a frozen minimal stopword set from seed generation;
5. emit deterministic 1-, 2-, and 3-token contiguous seed keys from remaining tokens;
6. retain original source spans in occurrence objects;
7. deduplicate canonical seed identities globally while preserving every occurrence.

This lexical seed layer is an indexing substrate, not a semantic-claim extractor. Later typed entity/relation atoms may be added as a separate derived layer with their own evidence class and frozen extractor contract.

## Context score attachment

Context scores enrich navigation; they do not determine custody identity.

Each seed/occurrence may carry an optional score bundle:

- `context_score`;
- `g_star`;
- `delta_g_star`;
- `cloud_drift_0_100`;
- `shannon_entropy`;
- `normalized_entropy`;
- `mutation_distance`;
- `restoration_gain`;
- `burden`;
- score source/contract SHA-256;
- evidence class.

No missing score is silently synthesized as empirical evidence.

For hierarchy parents, deterministic aggregates may be computed from descendant atom scores:

- mean;
- variance;
- minimum;
- maximum;
- count.

These aggregates are `RECOMPUTED_RESULT`.

## Question FCO

Every evaluation question is itself an FCO containing only model-eligible query data.

Required boundaries:

- question text: `EVAL_QUERY`;
- question seed atoms: `EVAL_QUERY`;
- answer/gold/reference fields: `EVAL_ONLY`;
- expected document IDs: `EVAL_ONLY`;
- scorer metadata: `EVAL_ONLY`.

The retrieval engine receives only the `QUESTION_FCO` and the model-visible source projection.

## Candidate lookup

Lookup operates on canonical seed keys and graph indexes, not SHA similarity.

The deterministic v1 index maps:

```text
canonical_seed_key -> seed_atom_id -> occurrence_ids
```

Optional future indexes may include entity/relation indexes, vector indexes, temporal indexes, and HydraDB graph indexes, but their contracts must be frozen separately.

## Hierarchical path navigation

For a question Q:

1. atomize Q using the same frozen atomizer;
2. retrieve matching seed IDs;
3. retrieve source atom occurrences;
4. score candidate occurrence paths;
5. expand upward only when the expected marginal information gain is positive under the frozen path policy;
6. stop at the smallest evidence object set satisfying the configured query coverage or expansion budget;
7. dereference only selected source pointers;
8. verify source/object hashes;
9. return a bounded evidence packet and complete retrieval-path receipt.

The model does not need to reread the full dataset.

## Path enrichment metrics

For every candidate hierarchy node N and question Q, compute deterministic metrics when inputs exist:

- `query_seed_coverage(N,Q)` — fraction of unique query seeds represented among descendants;
- `idf_weighted_query_coverage(N,Q)` — weighted query-seed coverage;
- `context_mean(N)` — mean descendant atom context score;
- `context_variance(N)` — population variance of descendant atom context score;
- `context_delta(child,parent)` — parent mean minus child mean;
- `coverage_delta(child,parent,Q)` — parent coverage minus child coverage;
- `source_bytes_if_dereferenced(N)`;
- `marginal_bytes(child,parent)`;
- `depth`;
- `path_length`.

## Frozen v1 path utility

The first deterministic implementation records all components separately and uses the following ranking utility only when the corresponding score inputs exist:

```text
utility =
    0.50 * idf_weighted_query_coverage
  + 0.20 * positive_coverage_delta
  + 0.15 * normalized_context_mean
  + 0.10 * positive_normalized_context_delta
  - 0.03 * normalized_context_variance
  - 0.02 * normalized_marginal_byte_cost
```

If context scores are unavailable, their terms are omitted and remaining weights are renormalized. The receipt must state `CONTEXT_SCORE_STATE=UNAVAILABLE`; it may not claim score-guided navigation.

These weights are an initial engineering contract, not a scientifically established optimum. Any later tuning creates a successor experiment.

## Expansion and stop policy v1

Candidate atoms begin at depth 0.

The deterministic engine may expand:

```text
ATOM_OCCURRENCE -> SENTENCE -> PARAGRAPH/TURN -> DOCUMENT/SESSION -> SOURCE_FILE
```

Expansion stops for a path when any of the following is true:

- query seed coverage reaches the configured threshold;
- marginal utility is non-positive;
- maximum hierarchy depth is reached;
- evidence byte budget would be exceeded;
- maximum graph-expansion count would be exceeded.

Default validation settings:

- coverage target: `0.80`;
- maximum selected evidence nodes: `8`;
- maximum graph expansions: `128`;
- maximum dereferenced evidence bytes: `32768`;
- maximum hierarchy depth: `4`.

These are frozen for SeedGraph v1 validation only.

## Speed and efficiency are first-class outcomes

Every retrieval receipt must record:

- index lookup count;
- seed IDs matched;
- occurrence IDs considered;
- graph edges traversed;
- hierarchy nodes scored;
- source dereference count;
- source bytes read;
- evidence bytes returned;
- full-context comparison bytes;
- byte reduction ratio;
- retrieval wall time;
- source verification wall time;
- total retrieval wall time;
- model input bytes/tokens later, when inference is executed.

The goal is to determine whether the same graph/index can reduce navigation burden for models across parameter scales without changing the evidence contract.

## Storage layout

The zero-model builder writes local generated artifacts under a dedicated external or ignored run namespace, not as canonical source custody.

Recommended tables:

- `nodes.parquet` — hierarchy FCO metadata;
- `edges.parquet` — FCG relationships;
- `seed_index.parquet` — canonical seed -> seed ID -> occurrence IDs;
- `pointers.parquet` — occurrence/hierarchy source pointers;
- `questions.parquet` — question FCOs without gold/reference fields;
- `score_aggregates.parquet` — optional context-score aggregates;
- `BUILD_RECEIPT.json`;
- `SHA256SUMS.txt`.

Large generated Parquet tables are not committed to Git. Git stores code, schemas, compact manifests, hashes, and receipts.

## Initial source scope

SeedGraph v1 may ingest only currently verified real sources:

### Track 01 — EnterpriseRAG-Bench

- real questions Parquet;
- real documents Parquet;
- first 300 admitted question IDs under the frozen ordered-first-300 contract;
- question/gold fields separated before graph construction;
- expected document IDs remain EVAL_ONLY and cannot influence retrieval.

### Track 03 — LongMemEval-S-full500

- real cleaned source JSON;
- 470 primary cases and 30 secondary cases remain distinct;
- source session/turn content is model-visible evidence;
- answers and scorer fields remain EVAL_ONLY.

### Track 02 — HydraBlast

Track 02 is not ingested into the v1 primary SeedGraph until its real-case contract is admitted. Previously generated synthetic 250-case manifests are prohibited from the primary SeedGraph lane.

## Experimental lanes after deterministic validation

### Lane A — V11 direct/oracle/full context

Preserved baseline. No mutation.

### Lane B — flat retrieval

Question-only retrieval over the same permitted source corpus with a frozen conventional retriever.

### Lane C — SeedGraph deterministic hierarchy

Question FCO -> query seeds -> graph/index path scoring -> lazy source dereference -> bounded evidence packet -> same model/scorer contract.

### Lane D — Ollarma interactive SeedGraph navigation

Same graph and evidence boundaries, but the model may call a frozen tool vocabulary such as:

- `search_seeds`;
- `expand_parent`;
- `follow_edge`;
- `inspect_scores`;
- `fetch_pointer`;
- `verify_source`.

Lane D is secondary to the causal A/B/C comparison.

## Nulls

Primary retrieval null:

```text
H0_seedgraph:
answer quality under deterministic SeedGraph retrieval
is not better than the frozen flat/direct comparator.
```

Efficiency null:

```text
H0_efficiency:
SeedGraph does not reduce source bytes/model-context burden or retrieval latency
at equivalent evaluation quality.
```

Interactive-navigation null:

```text
H0_interactive:
Ollarma interactive navigation does not improve over deterministic SeedGraph
under the same source, model, scorer, and evidence boundaries.
```

## Evidence and claim boundaries

- Building the hierarchy proves construction only.
- A deterministic query validation proves lookup/path/dereference mechanics only.
- Speed measurements are valid only for the measured host/configuration.
- Model benefit is not established until frozen comparative inference runs complete.
- Prior null/negative/failed experiments are preserved.
- No signing claim without actual authorized private-key signing.
- No Merkle/MMR commitment claim without actual commitment receipts.
