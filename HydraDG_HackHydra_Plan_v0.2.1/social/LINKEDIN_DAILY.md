# Daily LinkedIn build-in-public plan

Do not publish benchmark claims before the corresponding result artifact exists.

## Aug 16 — Architecture / problem
**Draft**
I’m building for Hack Hydra Track 03: a HydraDB-native divergence graph for agent memory.

The idea is narrower than “better RAG.” Long-running agents need to know what changed, when it changed, what evidence supported the old and new states, and which downstream answers depend on the divergence.

The MVP connects versioned temporal memory with FCO/FCG custody: source → memory/evidence → perturbation → first divergence → affected claims → recovery.

Today: schema + LongMemEval import + reproducibility contract.

#HackHydra #HydraDB #AIAgents #Reproducibility

## Aug 17 — Data / SeedGraph
**Draft**
Hack Hydra day update: LongMemEval is becoming a SeedGraph.

Instead of treating 40+ sessions as flat text, I’m representing sessions, turns, evidence labels, changing facts, and benchmark questions as typed graph objects. The goal is to compare standard QA accuracy with a second question: can we show the exact evidence path that made an answer admissible?

Next: HydraDB temporal queries and first controlled perturbations.

#HackHydra #HydraDB #LongTermMemory #KnowledgeGraphs

## Aug 18 — Divergence microscope
**Draft**
Today’s Hack Hydra experiment asks a different reproducibility question:

Two model runs diverge. Where did the divergence first become observable — bits, tensors, activations, logits, answers, or evaluation?

I’m connecting that first-divergence receipt to HydraDB so we can traverse the downstream impact set rather than just say “the final checkpoints differ.”

No result claim yet until the paired runs are frozen.

#HackHydra #HydraDB #MLReproducibility #LLM

## Aug 19 — Recovery / negative results
**Draft**
A useful memory system should be able to say “unsupported” and preserve failed branches.

Today I’m testing recovery classes: byte-exact, state-exact, functionally equivalent, partial recovery, or no recovery. Old states remain queryable rather than being silently overwritten.

That lets a failed replay or rejected claim become a successful verification outcome.

#HackHydra #HydraDB #AISafety #Provenance

## Aug 20 — Final demo
**Template — fill only with executed results**
Hack Hydra final build: [PROJECT NAME].

What it does:
• versioned temporal agent memory in HydraDB
• evidence/provenance paths
• first-divergence localization
• downstream impact traversal
• abstention and claim admission
• typed recovery

Executed evaluation:
• LongMemEval-S: [score]
• Knowledge Update: [score]
• Temporal Reasoning: [score]
• First-divergence localization: [score]
• Impact-set exact match: [score]

Repo/demo: [links]

#HackHydra #HydraDB #AIAgents #OpenSource
