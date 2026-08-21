# Hack Hydra 2026 — HydraDG Updated Judge Submission

## Headline

**HydraDB makes context stateful; HydraDG makes changing context auditable, perturbable, and economically measurable.**

HydraDG uses HydraDB as the graph-native context substrate and adds FCO/FCG custody around sources, atoms, transformations, model/agent decisions, state changes, evidence, claims, and release artifacts.

## Why this matters

HydraDB already addresses major production-memory failures: similarity is not relevance, stale facts are dangerous, time is part of relevance, and multi-session context needs graph structure. HydraDG adds four additional properties:

1. **First-divergence localization** — show exactly where a poisoned or wrong state entered.
2. **Recovery without erasure** — Reference → Poison → Antidote preserves the contradiction and the restoration path.
3. **Model/agent custody** — record which model or agent read, transformed, produced, inherited, contradicted, or restored a state.
4. **Economic measurement** — separate identity reuse, stored bytes, context tokens, model calls, latency, and energy abstractions instead of collapsing them into one “savings” claim.

## Golden Path

01 Reference → 02 Poison → 03 Antidote → 04 HydraDB → 05 Results → 06 Evidence/FCG → 07 Future Work → 08 Claim Boundary

## Current established evidence

- Historical LongMemEval-S full500 K=5 retrieval ablation: 500 total cases; 470 retrieval-scored; 30 abstentions. B/C/D did not establish a positive Hit@5 advantage over Route A.
- Hosted HydraDB connectivity: PASS to `hydradg` / `hydradg-judge-demo`; request-level canary relation readback succeeded. Full 653-FCO / 1,692-edge canonical parity remains `NOT_ESTABLISHED`.
- Deterministic retained identity accounting: 31,672,976 word/sentence occurrences → 10,854,020 unique keys → 20,818,956 duplicate occurrences → **65.730975% identity reuse**.
- Context-vs-Entropy classification: 18,567 raw findings; 18,555 classified; 12 abstentions; 99.9354% coverage. This does not replace Gitleaks.

## Novel scoring / state abstractions

- `G*` — declared synthetic state score for T0/T1/T2 only.
- `ΔG*` — change between declared synthetic states.
- `Cloud Drift` — 100 × base-2 Jensen-Shannon divergence from the frozen reference state.
- Context-vs-Entropy — contextual classification of high-entropy findings with explicit abstention.
- Anticube — self/non-self × safe/unsafe governance classification; future/preregistered signal, not an assumed ranking boost.
- FirstDivergenceAccuracy, ErrorPropagationRate and RecoveryRate — future multi-agent perturbation metrics.

### T0–T2 synthetic perturbation scores

| State | G* | ΔG* | Cloud Drift |
|---|---:|---:|---:|
| T0 Reference | -0.061230 | 0 | 0 |
| T1 Poison | 0.572956 | +0.634186 | 40.3629 |
| T2 Antidote | -0.027496 | -0.600452 | 1.8729 |

T3–T5 use `N/A` by contract when no explicit scoring distribution is declared or frozen.

## Economics

### Deterministic today

- 65.730975% identity reuse over retained word/sentence occurrence accounting.
- Canonical Parquet output footprint: 1,101,473,790 bytes. This is **not** a measured savings number.

### Theoretical abstraction

Hypothetical 7B model duplicate-work scenario:

`2 × 7,000,000,000 × 20,818,956 = 2.91465384×10^17 FLOPs`

Under the stated 100 TFLOP/s/W assumption this corresponds to `0.809626 Wh` theoretical energy equivalent.

This is **not measured electrical energy** and **not a measured inference-cost saving**.

### Next measurement gates

1. Serialized storage bytes: naive vs canonical objects + edges + metadata.
2. Context tokens: repeated context before/after canonical evidence assembly.
3. Avoided downstream calls: model/agent calls blocked after invalid/superseded/unsupported state.
4. Latency overhead and recovery latency.
5. **Cost per Correct Governed Answer**.

## Multi-agent extension

Every agent/model that touches data becomes an FCG participant:

`Evidence → Retriever → Extractor → Reasoner → Decision → Answer`

Wrong decisions remain perturbation evidence. Future experiments will introduce controlled extraction poison, stale-state poison, contradiction poison, provenance loss, and inherited bad-agent decisions.

Primary future metrics:

- ErrorPropagationRate
- FirstDivergenceAccuracy
- RecoveryRate
- CurrentStateAccuracy
- HistoricalStateRetention
- CompleteEvidencePathRecovery
- ContextTokenReduction
- SerializedByteReduction
- AvoidedDownstreamInferenceCalls
- CostPerCorrectGovernedAnswer

## What judges should remember

HydraDG is not a leaderboard claim. It is a governed-memory experiment that asks:

> What changed, when did it change, which evidence and agent caused the change, where did an error first enter, can we recover without deleting history, and what did that context cost?

## Claim boundaries

- SHA-256 establishes content identity, not correctness.
- Connectivity/canary readback does not establish full hosted parity.
- Identity reuse does not equal byte savings.
- FLOP/Wh scenarios are theoretical, not measured energy.
- BEAM 1M is future work until official rows are revision-pinned and hashed.
- Signature: `NOT_SIGNED` unless a real private-key signing/verification operation occurs.
- Merkle/MMR: `NOT_MERKLE_COMMITTED` unless a real commitment occurs.
