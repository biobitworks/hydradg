# Hack Hydra 2026 — Official Submission Document

## 1. Project Information
- **Project Name**: HydraDG — Graph-Native Governed Context Engine
- **Track**: Track 03 (HydraMemory / Memory + Context Retrieval) & Track 01 (HydraOntology) & Track 02 (HydraBlast)
- **Repository**: [https://github.com/biobitworks/hydradg](https://github.com/biobitworks/hydradg)
- **Release Branch**: `hack-hydra/public-product-final-20260819`
- **Release Commit**: `25326727165f0d3f6eefac54425fa1e7042dea8f`

---

## 2. Problem Statement
Ordinary AI memory and context retrieval systems overwrite, flatten, or silently mutate historical state over time. When context updates occur, un-governed systems obscure contradictions, lose provenance, and swallow negative or null experimental outcomes.

---

## 3. Solution Overview
HydraDG introduces a governed context engine built on top of **HydraDB**. Immutable evidence units are stored as **First-Class Objects (FCOs)** in a directed acyclic **First-Class Graph (FCG)** custody graph. Every state change preserves complete historical provenance, supersession edges, contradiction links, and experimental outcomes.

---

## 4. Meaningful HydraDB Usage
HydraDB is the load-bearing query, vector, and relational projection substrate behind HydraDG. It executes real-time graph traversals across:
```text
Session ─NEXT/PREV→ Session
Session ─ASSERTS→ Fact
Fact ─DERIVED_FROM→ Session
Fact ─ABOUT→ Entity
Fact ─SUPERSEDED_BY→ Fact
Fact ─CONTRADICTS→ Fact
```
Without HydraDB, the system loses the traversable relationship state used to reconstruct chronology, provenance, current state, contradiction, and blast radius.

---

## 5. Measured Results (Track 03 Benchmark)
- **Dataset**: `xiaowu0162/longmemeval-cleaned` (500 full cases, 23,867 sessions, 4,776 entities, 3,506 facts).
- **Determinism Gate**: 100% bit-for-bit replicate equality across $2 \times 2$ matrix cells ($H_{0,\text{rep}}$ PASS).
- **Prospective Depth ($K=15$)**: $G^* = -0.3448$, $\text{Hit}@15 = 0.9851$, $\text{Recall}@15 = 0.9582$ ($\Delta \text{Recall} = +11.2\text{ pp}$).
- **Claim Discipline**: Original full500 negative/neutral retrieval baseline preserved without claim inflation.

---

## 6. Live Product & Judge Walkthrough
- **Local / Developer Demo**: `http://127.0.0.1:3012/`
- **Judge Flow**: `/` (Overview) $\to$ `/judge` (Poison/Antidote) $\to$ `/track03` (Results) $\to$ `/graph` (Lineage) $\to$ `/evidence` (FCO Inspector) $\to$ `/knowledge` (KB) $\to$ `/how-to` (Guide) $\to$ `/eligibility` (Custody)
- **Static Presentation Fallback**: `http://127.0.0.1:3012/backup/hydradg.html`

---

## 7. Custody Roots & Claim Boundaries
- **Project FCG Root**: `experiment:fa170ab51cdfba46f9a24979c9be9b90fdc4ccedcdb292f313aa4439a92b08d8`
- **HydraDB Projection Root**: `projected_nodes=9,projected_edges=8`
- **Chrome Screenshot Manifest SHA-256**: `55adcc1df04dd8e9a6a1fdc7b24f0654e8f3a68dd005c09e25d49425f79d7734`
- **Claim Ceiling**: `PUBLIC_PRODUCT_DEPLOYMENT_AND_HYDRADB_TRACEABILITY_ONLY`
