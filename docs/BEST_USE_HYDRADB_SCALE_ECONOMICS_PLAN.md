# HydraDG — Best Use of HydraDB: Scale Economics + Fail-Closed Evidence

License: CC BY-NC-ND 4.0 for this research/documentation artifact. Software implementations remain Apache-2.0. Third-party data/models retain upstream rights.

## Current claim ceiling

`REPOSITORY_ARTIFACT_CHAIN_AND_DEDUP_ACCOUNTING_PRESENT; LONGMEMEVAL_EXECUTED_EVIDENCE_RETAINED; ENERGY_SAVINGS_THEORETICAL_ONLY; ACTUAL_SEEDGRAPH_ADMISSION_FULL_LOCAL_HYDRADB_WRITEBACK_AND_EXPANDED_HOSTED_PARITY_NOT_YET_ESTABLISHED; ROOT_SCOPES_REQUIRE_RECONCILIATION`

A generated receipt is not evidence that an external operation happened. Network write/readback, SeedGraph admission, model execution and measured energy require their own executed receipts.

## Why HydraDB fits the problem

1. **Strong graph data model.** FCO identities are canonical nodes while FCG edges preserve source, time, supersession, contradiction, membership and spatiotemporal context.
2. **Novel retrieval/reasoning.** Similarity can be combined with provenance, custody state, temporal state, contradiction/abstention and claim ceilings instead of being treated as provenance itself.
3. **Relationships/traversal/context.** Judges can traverse source bytes → KnowledgeAtom → SeedOfTruth → evidence/state → release, or follow one shared content identity into every retained place/time where it is referenced.
4. **Graph-native fit at scale.** Vector similarity does not prove exact identity, and relational systems require additional application machinery for recursive content-addressed custody and multi-scale traversal. This is a fit claim, not a claim that vectors or relational databases are incapable.

## Deterministic identity-reuse accounting

Retained inputs:

| Lane | Raw occurrences | Unique keys | Duplicate occurrences | Reuse |
|---|---:|---:|---:|---:|
| Word | 28,458,677 | 8,992,941 | 19,465,736 | 68.400003% |
| Sentence | 3,214,299 | 1,861,079 | 1,353,220 | 42.100004% |
| Combined | 31,672,976 | 10,854,020 | 20,818,956 | 65.730975% |

These values are deterministic arithmetic over retained accounting inputs. They are not a new claim that every third-party source record was independently re-enumerated in this release.

The retained canonical Parquet outputs declare 1,101,473,790 bytes total. That is a declared canonical footprint, **not** whole-corpus download-byte savings.

## Byte-level download/storage savings

The measured byte lane requires one exact record per acquired file/object:

```json
{"path":"...","size_bytes":123,"sha256":"<64 lowercase hex>"}
```

Calculations:

- `raw_download_bytes = Σ size_bytes(all records)`
- `unique_content_bytes = Σ size_bytes(one record per distinct SHA-256)`
- `duplicate_download_bytes = raw_download_bytes - unique_content_bytes`
- `byte_dedup_ratio_pct = 100 × duplicate_download_bytes / raw_download_bytes`

If the same SHA-256 is paired with conflicting sizes, calculation fails. Without a complete byte manifest the state is `NOT_MEASURED`; no GB-saved headline is permitted.

Use `scripts/build_download_byte_manifest.py` against actual downloaded corpus roots, then feed its `files` array into the savings calculator.

## Theoretical compute scenario

For a deliberately hypothetical dense 7B model, 2 FLOPs/parameter/token, and one assumed tokenizer token per duplicate atom occurrence:

`2 × 7,000,000,000 × 20,818,956 = 291,465,384,000,000,000 theoretical FLOPs avoided`

At a separately declared `100,000,000,000,000 FLOP/s/W` efficiency assumption:

`291,465,384,000,000,000 / 100,000,000,000,000 / 3600 = 0.809626 Wh`

This is a theoretical energy-equivalent scenario. `measured_energy_wh = null`. Real model-level estimates require exact tokenizer/model identity and tokenizer-specific `ΔN_tokens`.

## Deterministic calculation custody

`scripts/calculate_information_savings.py` uses:

`canonical input JSON → input_sha256`

`versioned calculation contract → calculation_contract_sha256`

`deterministic analysis → receipt payload → receipt_sha256`

Current retained hashes:

- input SHA-256: `e32e89eaf2035a6ade0646d3f782b32e0b96e628c13f42cf23d095b911a931b5`
- contract SHA-256: `5ab14c2c3b24f1603795bb521b2747f0e475f3a2afd358b4dd19e72eea6b5846`
- receipt SHA-256: `8d60ab68f989e88aec9446fc06739d2c52f4af911b673af058889c9f52afdf36`

`--verify` must reproduce the exact retained receipt. A mismatch returns non-zero. `scripts/verify_information_savings.sh` also checks a negative case in which the same SHA-256 is deliberately assigned conflicting byte sizes; acceptance of that invalid input fails the release gate.

Hash identity is not a digital signature and not correctness. Current state remains `NOT_SIGNED` and `NOT_MERKLE_COMMITTED` unless actual operations establish otherwise.

## Infrastructure evidence states

| Lane | State |
|---|---|
| Repository artifact chain | PRESENT |
| LongMemEval full500 | EXECUTED |
| Atom/key dedup accounting | PRESENT |
| Whole-corpus byte savings | NOT_MEASURED |
| Energy savings | THEORETICAL_ONLY |
| Actual SeedGraph admission | NOT_ESTABLISHED |
| Full local HydraDB write/readback | NOT_ESTABLISHED |
| Expanded hosted HydraDB parity | NOT_ESTABLISHED |
| Root scopes | RECONCILIATION_REQUIRED |

Historical 36-FCO/24-edge hosted parity remains valid only for its bounded historical projection scope. Expanded graph states must earn new write/readback and parity evidence rather than inheriting old green values.

## Future deterministic calculators

Use the same fail-closed contract for:

- `calculate_context_state.py`
- `calculate_graph_root.py`
- `calculate_local_hosted_parity.py`
- `calculate_tokenizer_dedup.py`
- `calculate_retrieval_metrics.py`

Each should pin canonical inputs, algorithm/version, output receipt, hashes, evidence class and claim ceiling. A calculation that stops reproducing is itself a retained failure/contradiction object.
