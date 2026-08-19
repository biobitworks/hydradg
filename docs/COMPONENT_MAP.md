# HydraDG System Component Map

This document maps all core components of HydraDG, explaining why each exists, its inputs and outputs, and its formal claim boundary.

| Component | What It Does | Why It Exists | Input | Output | Claim Boundary |
|---|---|---|---|---|---|
| **FCO (First-Class Object)** | Immutable typed evidence entity | Prevents silent state mutation & data loss | Raw evidence / transformation | Content-addressed FCO JSON | Canonical custody object |
| **FCG (First-Class Graph)** | Governed directed acyclic graph of FCOs | Reconstructs state evolution & provenance | FCO nodes & edges | Project FCG root hash | Canonical custody graph |
| **SeedGraph** | Deterministic atomization substrate | Binds raw artifacts to immutable atom locators | Binary / text artifacts | AtomLocator IDs | Deterministic atomization only |
| **HydraDB** | Graph database & vector query substrate | Provides high-performance graph traversal & retrieval | FCG projections / vectors | Cypher / graph query results | Query projection substrate |
| **HydraDG Graph Adapter** | Server-side data access layer | Connects UI cleanly to local or remote HydraDB | FCG / HydraDB API | Standardized DTOs | Server-only data translation |
| **Context Iceberg** | 4D interactive state visualization | Visualizes context evolution over time | FCG timeline states | Interactive Three.js canvas | Diagnostic state visualization |
| **Cloud Drift** | Jensen-Shannon Divergence metric ($JSD$) | Quantifies context distribution shifts | 8-bucket context vectors | Score ($0 \to 100$) | Distribution shift metric |
| **$\Delta G^*$** | Gibbs free-cost abstraction ($\Delta G^* = -0.0547$) | Balances usefulness vs burden in context | Energy ($U^*$) & Entropy ($S$) | Free-cost delta score | Free-cost diagnostic abstraction |
| **Hit@K** | Fraction of queries with target in top-$K$ | Evaluates retrieval coverage | Query & Ground truth | Score ($0.0 \to 1.0$) | Retrieval coverage metric |
| **Recall@K** | Fraction of relevant facts retrieved | Evaluates retrieval completeness | Query & Ground truth | Score ($0.0 \to 1.0$) | Retrieval completeness metric |
| **Judge Walkthrough** | Interactive guided demo flow (`/judge`) | Demonstrates Reference $\to$ Poison $\to$ Antidote | User navigation | Step-by-step state view | Presentation walkthrough |
| **Knowledge Base** | Linked terminology & FCO directory (`/knowledge`) | Resolves terms to definitions & source FCOs | Declared project terms | Knowledge FCO view | Terminology projection |
| **How-To Guide** | Step-by-step operator guide (`/how-to`) | Instructs judges/operators on system use | Markdown documentation | Interactive guide page | Operator documentation |
| **Eligibility View** | Custody & signature status page (`/eligibility`) | Verifies build-window eligibility & hashes | Repository state | Signed custody status | Eligibility verification |
| **Static Fallback** | Standalone single-file HTML presentation | Ensures demo availability if server is offline | Frozen HTML export | Rendered backup page | Offline presentation fallback |
| **Local Model Advisory** | Structured LLM diagnostic explanation | Explains state shifts via local Ollarma models | FCG state summary | Structured explanation DTO | Probabilistic model output only |
| **Screenshot Custody** | Hashed Chrome screenshot manifest | Audits UI rendering across all pages | Chrome headless browser | `SCREENSHOT_SHA256SUMS.txt` | Operator-view presentation artifact |
