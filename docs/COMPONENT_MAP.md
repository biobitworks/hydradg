# HydraDG System Component Map

This document maps the judge-facing HydraDG components, their inputs/outputs, and the maximum claim each component supports.

**FCO = Fractal Custody Object.**  
**FCG = Fractal Custody Graph.**

| Component | What It Does | Why It Exists | Input | Output | Claim Boundary |
|---|---|---|---|---|---|
| **FCO (Fractal Custody Object)** | Bounded, content-addressed custody object whose identity is bound to declared evidence/metadata under the canonical project rules | Preserves exact object identity and explicit provenance/claim limits | Source bytes, declared transformation, receipt, or bounded derived object | Canonical FCO identity / payload | Custody and identity only; a valid FCO does not establish that its payload is scientifically true |
| **FCG (Fractal Custody Graph)** | Governed graph connecting FCOs through provenance, custody, supersession, contradiction, and other canonical relations | Reconstructs how sources, transformations, evidence, claims, and artifacts relate over time | Canonical FCO nodes and schema-valid edges | Inspectable custody/provenance graph and project roots/receipts where actually computed | Do not assume the whole application graph is a DAG; HydraDG may contain temporal inverse, contradiction, or supersession relationships |
| **SeedGraph** | Deterministic atomization / source-location substrate | Binds raw artifacts to reproducible atom locators before canonical FCO binding | Binary / text artifacts | Atom locators / governed source identities | Deterministic atomization only unless a canonical FCO/FCG binding receipt exists |
| **HydraDB** | Operational graph-query and retrieval substrate | Makes the public FCO/FCG projection traversable and queryable | FCG projection, graph nodes/edges, optional vectors | Graph/query/readback results | Query projection substrate; successful readback is not independent scientific replication |
| **HydraDG Graph Adapter** | Server-side data-access layer | Connects the web application to HydraDB without exposing secrets to the browser | HydraDB API / graph projection | Standardized application DTOs | Server-side data translation |
| **Context Iceberg** | Interactive 4D state visualization | Visualizes context evolution across graph state and time | FCG timeline / presentation states | Native browser-canvas visualization | Diagnostic/presentation visualization, not a causal model |
| **Structural Cloud Drift** | Jensen-Shannon-divergence-based context-shift diagnostic | Quantifies change in the frozen structural context distribution | Frozen structural context vectors | `100 × JSD` score in `[0,100]` | Distribution-shift magnitude only; does not imply retrieval degradation or improvement |
| **Retrieval Cloud Drift** | Separate retrieval-distribution diagnostic where a frozen retrieval vocabulary/receipt exists | Keeps retrieval-state shift distinct from structural graph drift | Frozen retrieval context distributions | `100 × JSD` score where implemented/receipted | Retrieval-distribution shift only |
| **G* / Delta G*** | Application-defined dimensionless information-state / free-cost diagnostic | Provides a compact diagnostic combining the project’s frozen information-state terms | Frozen G* configuration and state measurements | G* and delta-from-reference value | Nonphysical design abstraction; not joules, kcal/mol, physical temperature, QA accuracy, or a direct reproduction of Ensslin & Weig’s IFT functional |
| **Hit@K** | Fraction of scored queries with the target represented in top-K under the frozen retrieval definition | Measures retrieval hit coverage | Query, target/ground truth, ranked retrieval | Score in `[0,1]` | Retrieval metric, not end-to-end QA accuracy |
| **Recall@K** | Fraction of relevant target evidence retrieved under the frozen retrieval definition | Measures retrieval completeness | Query, relevant evidence set, ranked retrieval | Score in `[0,1]` | Retrieval metric, not end-to-end QA accuracy |
| **Judge Walkthrough** | Guided `/judge` demo | Demonstrates Reference -> Poison -> Antidote state evolution without erasing prior state | User interaction + frozen/local demo state | Stepwise presentation | Demonstration surface only |
| **Knowledge Base** | Linked terminology and FCO/source directory (`/knowledge`) | Resolves project terms to definitions, source references, evidence classes, and claim boundaries | Declared project concepts and public-safe source references | Knowledge view / optional HydraDB projection | Explanation/traceability surface; does not create scientific verification |
| **How-To Guide** | Reproduction/operator guide (`/how-to`) | Gives a clean-machine web + HydraDB reconstruction path | Public repository | Reproduction instructions | Documentation |
| **Eligibility View** | Custody, release, signature, and submission-state display (`/eligibility`) | Makes actual release states inspectable | Repository/receipt state | Current recorded status | Must display actual status; a hash is not a signature, and HydraDG project signing/Merkle state must remain pending/not committed unless receipts establish otherwise |
| **Static Fallback** | Standalone HTML presentation | Keeps the demonstration inspectable if the live local stack is unavailable | Frozen HTML export | Rendered backup page | Offline presentation only; not a live HydraDB control surface |
| **Local Model Advisory** | Structured probabilistic diagnostic/explanation | Generates hypotheses/explanations after deterministic evidence is frozen | FCG/state summary | Structured model output | Probabilistic/model output only; not deterministic evidence |
| **Screenshot Custody** | Hash manifest for captured UI screenshots where generated | Preserves exact presentation artifact identity | Screenshot bytes | SHA-256 manifest / receipt | Presentation artifact identity only |

## Source-lineage notes

- The public FCO preprint defines a **Fractal Custody Object** as a bounded content-addressed custody object whose root also functions as a knowledge-graph identity, with explicit provenance/custody edges and a claim ceiling. The preprint also explicitly treats the work as an integration/proof-of-concept rather than a new hash, Merkle tree, or provenance primitive.
- The preprint’s stronger admission language includes recomputation from named bytes and an external oracle/threshold. HydraDG should therefore avoid calling a bare hash check or byte-fixity check “full FCO admission” unless the canonical admission conditions for that object were actually applied.
- HydraDG’s `G*` lineage uses Ensslin & Weig (2010) as an information-theoretic Gibbs/free-energy analogy only. The project diagnostic is application-defined and dimensionless.
- Structural/Retrieval Cloud Drift uses Jensen-Shannon divergence; the JSD source should remain distinct from the G* source lineage.

For exact source/version/hash lineage, use the custody receipts and publication/source index rather than copying short hash prefixes into narrative documentation.
