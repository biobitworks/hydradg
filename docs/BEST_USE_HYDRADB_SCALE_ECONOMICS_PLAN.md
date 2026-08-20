# HydraDG — Best Use of HydraDB: Scale Economics and Fail-Closed Evidence Plan

License: CC BY-NC-ND 4.0 for this research/documentation artifact. Software implementations referenced here remain Apache-2.0. Third-party datasets/models retain upstream rights.

## Current claim boundary

`REPOSITORY_ARTIFACT_CHAIN_AND_DEDUP_ACCOUNTING_PRESENT; LONGMEMEVAL_EXECUTED_EVIDENCE_RETAINED; ENERGY_SAVINGS_THEORETICAL_ONLY; ACTUAL_SEEDGRAPH_ADMISSION_FULL_LOCAL_HYDRADB_WRITEBACK_AND_EXPANDED_HOSTED_PARITY_NOT_YET_ESTABLISHED; ROOT_SCOPES_REQUIRE_RECONCILIATION`

This document is deliberately fail-closed. A generated receipt is not evidence that a network write, model run, SeedGraph admission, or hosted readback occurred.

## Why this is a strong HydraDB use case

HydraDG uses HydraDB for a graph problem that becomes increasingly awkward if reduced to nearest-neighbor vectors or flat relational rows: the same evidence can be referenced across many documents, times, models, experiments and releases while retaining one canonical content identity and many contextual locations.

The judge-facing fit maps to four properties:

1. **Strong graph data model.** Content-addressed FCOs are nodes; typed FCG edges preserve `DERIVED_FROM`, `MEMBER_OF`, supersession, state transitions, source relationships and spatiotemporal pointers. A canonical atom can be reused without copying its content identity.
2. **Novel retrieval/reasoning.** Retrieval can combine lexical/vector candidates with graph context, custody state, time, source, contradiction/abstention state and exact content identity. Similarity is not treated as provenance.
3. **Relationships/traversal/context.** A judge can traverse source bytes → KnowledgeAtom → SeedOfTruth → evidence/claim → experiment state → release, or follow one shared hash into every place/time where it was referenced.
4. **Harder in vector/relational-only systems.** Vector similarity does not prove exact identity, and a conventional relational design can represent the edges but requires more application-level machinery to preserve recursive content-addressed custody, version roots, supersession and multi-scale context. HydraDG does not claim those systems are incapable; it demonstrates why a graph-native context layer is operationally useful.

## Three savings lanes — never collapse them

### Lane A — byte-level download/storage deduplication

Required input is a hashed byte manifest with one record per acquired object:

```json
{"path":"...","size_bytes":123,"sha256":"<64 hex>"}
```

Deterministic calculations:

- `raw_download_bytes = Σ size_bytes(all records)`
- `unique_content_bytes = Σ size_bytes(one record per distinct SHA-256)`
- `duplicate_download_bytes = raw_download_bytes - unique_content_bytes`
- `byte_dedup_ratio_pct = 100 × duplicate_download_bytes / raw_download_bytes`

If two records have the same SHA-256 but conflicting sizes, the calculator **FAILS**. If there is no full byte manifest, the output is `BYTE_DOWNLOAD_SAVINGS=NOT_MEASURED`; no GB-saved headline is permitted.

The existing receipt declares two canonical Parquet outputs totaling 1,101,473,790 bytes, but this is a declared canonical footprint, not proof of original download-byte savings.

### Lane B — canonical atom/key reuse

Retained count inputs currently declare:

| Lane | Raw occurrences | Unique keys | Duplicate occurrences | Reuse |
|---|---:|---:|---:|---:|
| Word | 28,458,677 | 8,992,941 | 19,465,736 | 68.400003% |
| Sentence | 3,214,299 | 1,861,079 | 1,353,220 | 42.100004% |
| Combined | 31,672,976 | 10,854,020 | 20,818,956 | 65.730975% |

These values are deterministic arithmetic over the retained accounting inputs. They are **not** a claim that all source corpora have been independently re-enumerated in this release.

The graph-economic interpretation is that many contextual occurrences can point to one canonical content key while retaining distinct provenance/time/location edges.

### Lane C — theoretical model compute avoidance

A scenario may estimate:

`theoretical_flops_avoided = FLOPs_per_parameter_per_token × N_params × assumed_delta_tokens`

For the explicitly hypothetical dense 7B scenario with 2 FLOPs/parameter/token and one tokenizer token assumed per duplicate atom occurrence:

`2 × 7,000,000,000 × 20,818,956 = 291,465,384,000,000,000 FLOPs`

At the separately declared efficiency assumption of `100,000,000,000,000 FLOP/s/W`:

`291,465,384,000,000,000 / 100,000,000,000,000 / 3600 = 0.809626 Wh`

This is a **theoretical energy-equivalent scenario**, not measured electricity and not an Ollama benchmark. Actual model-specific estimates require the exact tokenizer and model snapshot.

## Deterministic calculator contract

The calculator lives at `scripts/calculate_information_savings.py` and consumes canonical JSON. It must:

- use integer arithmetic for counts/bytes;
- use decimal arithmetic for ratios/energy-equivalent formatting;
- canonicalize JSON by UTF-8 + sorted keys + compact separators;
- SHA-256 the exact canonical input;
- SHA-256 the declared calculation contract;
- produce a deterministic receipt with no wall-clock timestamp;
- SHA-256 the receipt payload before adding `receipt_sha256`;
- support `--verify` and exit non-zero if recomputation differs;
- fail on impossible counts (`unique > raw`), negative values, malformed hashes, same-hash/different-size byte records, or output digest mismatch.

The deterministic chain is:

`input bytes/hash → fixed calculator contract/hash → deterministic calculation → output receipt/hash`

A mismatch is an evidence object, not something to normalize away.

## Production evidence states

| Evidence lane | Current state | Production wording |
|---|---|---|
| Repository artifact chain | PRESENT | Hash-addressed artifacts and FCO/FCG lineage exist in GitHub. |
| LongMemEval full500 | EXECUTED | 500 cases; 470 scored; 30 abstentions; no positive B/C/D Hit@5 signal. |
| Atom/key dedup accounting | PRESENT | Deterministic arithmetic over declared retained counts. |
| Download-byte savings | NOT_MEASURED | Await full `{path,size_bytes,sha256}` acquisition manifest. |
| Energy savings | THEORETICAL_ONLY | Scenario output only; measured Wh remains null. |
| SeedGraph admission | NOT_ESTABLISHED | Do not call generated local receipt an executed admission. |
| Full local HydraDB writeback/readback | NOT_ESTABLISHED | Existing accounting script does not perform the network operation. |
| Expanded hosted HydraDB parity | NOT_ESTABLISHED | Historical 36-node/24-edge bounded receipt remains historical only. |
| Root scopes | RECONCILIATION_REQUIRED | Historical T3 roots and expanded conversation/project roots must remain explicitly scoped. |

## Root scope rule

Do not overwrite historical roots.

- Historical bounded T3 FCO root: `d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1`
- Historical 24-edge root: `7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab`
- Reviewed expanded computed project root at the prior branch state: `bb0adb5a6453a6493e51363f33e7782b3d79dd82b27ceb8678173ce53f1ce72b` over the scope recorded in `UPDATED_FCG_MERKLE_ROOT.json`.

A computed root is not automatically an externally committed Merkle root. Preserve `NOT_MERKLE_COMMITTED` unless a commitment operation actually occurs.

## Future calculator family

Each important claim should eventually have a deterministic, separately versioned calculator:

- `calculate_information_savings.py`
- `calculate_context_state.py`
- `calculate_graph_root.py`
- `calculate_local_hosted_parity.py`
- `calculate_tokenizer_dedup.py`
- `calculate_retrieval_metrics.py`

Every calculator follows the same custody contract: canonical inputs, versioned algorithm, deterministic output, independent verification mode, and fail-closed state.

## Promotion gate

Production may highlight this work only if the exact release SHA passes build/typecheck/security/link tests and the rendered copy preserves the states above. New SeedGraph, local HydraDB, hosted HydraDB, byte-savings, tokenizer or energy claims can move from `NOT_ESTABLISHED`/`NOT_MEASURED` only after their underlying operation executes and produces a readback/measurement receipt.