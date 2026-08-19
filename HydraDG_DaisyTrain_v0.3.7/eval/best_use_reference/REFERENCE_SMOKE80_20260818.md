# Hack Hydra Best Use — reference-graph smoke80 result

Status: `RECOMPUTED_REFERENCE_GRAPH_ONLY`

This result was executed in a remote Linux workspace against the official cleaned LongMemEval-S artifact. It is a **design calibration**, not a HydraDB benchmark: the same relation/ranking logic was evaluated in memory because a runnable HydraDB engine was not available in that execution environment. Do not cite these numbers as HydraDB performance.

## Source / custody

- Dataset: `xiaowu0162/longmemeval-cleaned`, `longmemeval_s_cleaned.json`
- Source SHA-256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- Source N: 500
- Deterministic smoke selection: category-proportional + SHA-256 stable rank
- Smoke N: 80
- Retrieval-scored N: 77 non-abstention cases
- Streaming reference script SHA-256: `5cc9eaae6b34c3f13176d62e07d610c59fbeb3bf67912e9eb0d9a652e24f1cff`
- K=10 cases SHA-256: `87740aaffdf0ff89a15948d50369ba7e1dfaa9dd7cb268fb602a90965c5e1ec6`
- K=10 stats SHA-256: `56bcd25513a3cebdf74cd94c0af1ee36556a8117dfdcdeafd949024cac2f4cc3`
- K=5 stats SHA-256: `1ccab3cd13f90cc808fff5c504d4811f35795ccfe1c0480f4265b385a273fb3b`
- K=3 stats SHA-256: `26352dde5045be7a96e821e1b56101b89360e5a7806eef8afc4ec7701534318b`

Signature: `NOT_SIGNED`

Merkle/MMR: `NOT_MERKLE_COMMITTED`

## Ablation

- A: flat BM25 session retrieval.
- B: A lexical seeds + temporal `NEXT/PREV` relation expansion.
- C: B + explicit Case→CONTAINS→Session provenance path.
- D: C + deterministic lexical `RELATED` and directed `SUPERSEDES` relation expansion.

Ground-truth `answer_session_ids` were used only for evaluation, never graph construction or ranking.

## K=10 result

| Method | Hit@10 | Wilson 95% CI | Mean session recall@10 | Path coverage |
|---|---:|---:|---:|---:|
| A | 98.70% | 93.00–99.77% | 95.76% | 0% |
| B | 98.70% | 93.00–99.77% | 94.03% | 64.29% |
| C | 98.70% | 93.00–99.77% | 94.03% | 100% |
| D | 98.70% | 93.00–99.77% | 96.97% | 100% |

D versus A:

- Δ hit@10: `0.00 pp`
- Δ mean recall@10: `+1.21 pp`
- paired discordance: A-only `1`, D-only `1`
- exact paired McNemar p: `1.0`

**Decision:** no evidence of a hit-rate advantage at K=10. The flat baseline is nearly saturated on this deterministic smoke sample. D shows a small recall signal, but the paired hit test does not support superiority.

## Context-budget stress test

The same predeclared relation logic was evaluated at smaller K to test whether graph traversal could recover evidence under a tighter context budget.

| K | A hit | D hit | A mean recall | D mean recall | A-only / D-only | McNemar p |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 97.40% | 88.31% | 91.49% | 80.41% | 7 / 0 | 0.015625 |
| 5 | 98.70% | 94.81% | 93.81% | 91.26% | 3 / 0 | 0.25 |
| 10 | 98.70% | 98.70% | 95.76% | 96.97% | 1 / 1 | 1.0 |

**Decision:** the naive temporal/lexical relation expansion is not a winning Best Use design. At small K it displaces stronger lexical evidence; at K=10 the baseline is saturated.

## Earliest divergent dependency

The problem is not HydraDB. The unvalidated dependency is the **relationship-construction model**:

`session text -> deterministic lexical signatures -> RELATED/SUPERSEDES edges -> graph traversal -> ranked context`

The reference evaluation rejects the hypothesis that these simple lexical relations materially improve LongMemEval retrieval.

## Next experiment

Replace heuristic lexical relations with typed memory relations extracted before retrieval:

- `Entity`
- `Fact(subject, predicate, object)`
- `MENTIONS`
- `ASSERTED_IN`
- `SUPERSEDES`
- `CONTRADICTS`
- `VALID_AT / OBSERVED_AT`
- `DERIVED_FROM`

Use Ollarma locally to extract bounded JSON facts/relations with exact model/config receipts, then use HydraDB for multi-hop traversal and current-state reconstruction. Preserve A as the same flat retrieval baseline.

The Best Use claim should be tested on two separate surfaces:

1. LongMemEval full500: retrieval/QA quality and context cost.
2. HydraDG structural suite: context binding, supersession, evidence-path reconstruction, perturbation impact, and recovery.

Claim ceiling for this file: `REFERENCE_GRAPH_DESIGN_CALIBRATION_ONLY`.
