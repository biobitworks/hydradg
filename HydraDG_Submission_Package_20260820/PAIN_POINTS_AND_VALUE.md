# HydraDG — Pain Points and Value Proposition

## Headline

**HydraDB makes context stateful; HydraDG makes changing context auditable, perturbable, and economically measurable.**

## The pain points

1. **Similarity is not relevance.** A close vector match can still be stale, superseded, contradictory, or from the wrong session.
2. **State confusion looks like hallucination.** A model can reason correctly over the wrong historical state.
3. **Multi-session reasoning remains difficult.** Correct answers may require combining evidence distributed across many sessions and state changes.
4. **Multi-agent systems amplify upstream mistakes.** One bad extraction or stale state can contaminate downstream reasoning and decision agents.
5. **Repeated context costs money.** Duplicate identities, repeated prompt context, repeated retrieval and repeated model calls all compound cost.
6. **Evaluation often hides failure modes.** Null, negative, timeout, blocked and abstaining outcomes are frequently collapsed or discarded.

## What HydraDB gives us

- Versioned temporal graph memory.
- Dense + sparse + graph + temporal retrieval.
- Cross-session structure and entity resolution.
- Agent/context traces and relationship-aware retrieval.
- Tiered storage and storage-based pricing.

## What HydraDG adds

- Content-addressed FCO identity + typed FCG lineage.
- Reference → Poison → Antidote perturbation/recovery experiment.
- First-divergence localization.
- Model/agent touch lineage and error inheritance.
- Claim ceilings and evidence-state separation.
- Atom/state scoring: G*, ΔG*, Cloud Drift, Context-vs-Entropy, identity reuse, Anticube governance.
- Economic instrumentation roadmap: serialized bytes, tokens, avoided calls, latency, energy abstraction and Cost per Correct Governed Answer.

## Current economics

- Retained occurrence identities: 31,672,976.
- Unique identities: 10,854,020.
- Duplicate occurrences: 20,818,956.
- Identity reuse: **65.730975%**.

This is an **upper-bound identity-reuse opportunity**, not measured database byte savings or a billing reduction. Real storage savings require serialized byte measurements including graph edges, metadata, compression and storage tier residency.

HydraDB's public pricing is storage-based, making real byte reduction commercially relevant once measured.

## Time + energy abstractions

- **Semantic time:** valid-time / commit-time plus T0 Reference → T1 Poison → T2 Antidote chronology.
- **Operational time:** future retrieval latency, model wall time, recovery time and avoided downstream wall time.
- **Theoretical energy scenario:** 2.91465384×10^17 FLOPs and 0.809626 Wh theoretical equivalent for the declared 7B duplicate-work abstraction; NOT measured electrical energy.

## The judge question we want to answer

> What changed, when did it change, which evidence and agent caused the change, where did an error first enter, can we recover without deleting history, and what did that context cost?
