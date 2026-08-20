# HydraDG — Graph-Native Governed Context Engine

[![Hack Hydra 2026](https://img.shields.io/badge/Hack%20Hydra-2026-blue.svg)](https://github.com/biobitworks/hydradg)
[![Track 03](https://img.shields.io/badge/Track%2003-Memory%20%2B%20Context%20Retrieval-green.svg)](https://github.com/biobitworks/hydradg)
[![HydraDB](https://img.shields.io/badge/HydraDB-Native%20Graph%20Projection-orange.svg)](https://hydradb.com)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE)

HydraDG is a graph-native memory and context engine built on **HydraDB** for **Hack Hydra 2026 (Track 03 — Memory + Context Retrieval)**. It represents evolving conversational state as typed graph projections, preserves immutable evidence lineage behind every answer, and makes state divergence, contradiction, and recovery mechanically inspectable.

---

## 📋 Table of Contents
1. [Overview & Problem Statement](#-overview--problem-statement)
2. [Key Architecture & Principles](#-key-architecture--principles)
3. [Quick Start: Replicating the Web Application](#-quick-start-replicating-the-web-application)
4. [HydraDB Data & Schemas](#-hydradb-data--schemas)
5. [Interactive Demo & Page Guide (How-To)](#-interactive-demo--page-guide-how-to)
6. [Track 03 Benchmark Evidence](#-track-03-benchmark-evidence)
7. [Theoretical Foundations ($G^*$ & Cloud Drift)](#-theoretical-foundations-g-amp-cloud-drift)
8. [Submission & Verification Links](#-submission--verification-links)

---

## 💡 Overview & Problem Statement

### The Problem
Ordinary AI memory systems flatten, overwrite, or silently mutate context over time. When user facts change, are contradicted, or are later restored, traditional vector or text memory stores lose historical provenance. Null/negative experimental outcomes disappear, and state corruption goes undetected.

### The Solution: HydraDG
HydraDG solves context corruption by storing immutable **First-Class Objects (FCOs)** in a **First-Class Graph (FCG)** custody structure projected directly into **HydraDB**.
- **Immutable Provenance**: Every state change retains its complete origin lineage, supersession links, and contradiction edges.
- **Governed Recovery**: Correcting a poisoned state does not delete the past; it creates an explicit antidote transition link.
- **4D Context Iceberg Visualizer**: Real-time tracking of structural Cloud Drift ($JSD$) and governed Gibbs free-cost deltas ($\Delta G^*$).

---

## 🏗️ Key Architecture & Principles

```text
LOCAL / DEVELOPMENT                     PUBLIC / JUDGES
magicSTUDIObox                          GitHub Public Repo
  ├─ local HydraDB                        ↓
  ├─ local FCG                            Vercel Next.js Web App
  └─ local Next.js                        ↓ (server-side API)
       ↓                                  HydraDB Hosted API / Built-in Fixture
reproducibility / video                   ↓
                                          public-safe FCG projection
                                          ↓
                                          interactive judge demo
```

- **HydraDB**: High-performance graph database engine used as the query, temporal traversal, vector, and relational projection substrate.
- **FCO (First-Class Object)**: Bounded custody object carrying cryptographic identity (SHA-256), provenance, evidence class, and claim boundaries.
- **FCG (First-Class Graph)**: The dependency graph connecting source data, transformations, derived facts, and claims.
- **Context Iceberg**: Interactive state-space visualization tracking $JSD$ drift and $\Delta G^*$ cost deltas.

---

## 🚀 Quick Start: Replicating the Web Application

Anyone cloning this repository can replicate and run the entire web application locally in seconds!

### Prerequisites
- Node.js v18+ (v20 recommended)
- npm v9+

### 1. Install & Launch
```bash
# Clone the repository
git clone https://github.com/biobitworks/hydradg.git
cd hydradg

# Install all web application dependencies
npm run install:all

# Launch the development server
npm run dev
```

Open your browser and navigate to:
👉 **`http://localhost:3000`**

### 2. Verify Production Build
```bash
# Build the Next.js production bundle
npm run build

# Start the production server
npm run start
```

### 3. Static Fallback Presentation
If Node.js is not available, you can view the static standalone presentation:
- **Local file**: `apps/hydradg-web/public/backup/hydradg.html`
- **Browser URL**: `http://localhost:3000/backup/hydradg.html`

For comprehensive replication details, see [`HOW_TO.md`](HOW_TO.md).

---

## 🗄️ HydraDB Data & Schemas

HydraDG provides full access to its graph schemas, seed datasets, and projection scripts:

- **Data Manual**: Detailed specification in [`HYDRADB_DATA.md`](HYDRADB_DATA.md).
- **Node Schemas**: `HydraDG_DaisyTrain_v0.3.1/hydra/schema_nodes.json` (`Session`, `Fact`, `Entity`, `KnowledgeAtom`).
- **Edge Schemas**: `HydraDG_DaisyTrain_v0.3.1/hydra/schema_edges.json` (`NEXT`, `ASSERTS`, `DERIVED_FROM`, `ABOUT`, `SUPERSEDES`, `CONTRADICTS`).
- **SeedGraph Dataset**: `PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json` (500-case raw SeedGraph dataset for LongMemEval).
- **HydraDB Projection Script**: `python3 scripts/project_website_knowledge_to_hydradb.py`.

---

## 🗺️ Interactive Demo & Page Guide (How-To)

The web application contains 8 interactive pages built for judge inspection:

| Route | Page Name | Key Features & What to Look For |
|---|---|---|
| `/` | **Overview Dashboard** | Executive summary, track indicators, architecture diagram, and verification status. |
| `/judge` | **Live Judge Memory Demo** | Interactive **Reference $\to$ Poison $\to$ Antidote** state perturbation tool. Visualizes live graph recovery without state loss. |
| `/track03` | **Track 03 Results** | Full evaluation matrix on `xiaowu0162/longmemeval-cleaned` (500 cases, 23,867 sessions). Displays $K=5$ ablation tables and $K=15$ recall metrics. |
| `/graph` | **4D FCG & Context Iceberg** | 4D state-space visualizer tracking Cloud Drift ($JSD$) and governed Gibbs free-cost deltas ($\Delta G^*$). |
| `/evidence` | **FCO Lineage Inspector** | Provenance inspector for First-Class Objects, academic foundations (Enßlin & Weig 2010, Lin 1991), and cryptographic SHA-256 receipts. |
| `/knowledge` | **Knowledge Base FCO Index** | Searchable directory of atomized knowledge FCOs, claim boundaries, and custody certificates. |
| `/how-to` | **Replicability Guide** | Detailed command cheatsheet, environment configurations, and static fallback options. |
| `/eligibility` | **Submission Eligibility** | Hack Hydra Track 03 checklist and rule compliance verification. |

---

## 📊 Track 03 Benchmark Evidence

HydraDG was evaluated on the **Track 03 Benchmark** using `xiaowu0162/longmemeval-cleaned`:

### Benchmark Scale
- **Cases**: 500 total cases
- **Sessions**: 23,867 total sessions
- **Entities**: 4,776 entities
- **Facts**: 3,506 facts
- **Scored Subset**: 470 cases (30 abstentions excluded)

### Completed K=5 Ablation Results

| Route | Hit@5 | Recall@5 | Interpretation |
|---|---:|---:|---|
| **Route A (Reference/Flat)** | **0.9638** | **0.9066** | Flat reference baseline |
| **Route B** | 0.9468 | 0.8538 | Null/negative hit-rate signal |
| **Route C** | 0.9468 | 0.8526 | Null/negative hit-rate signal |
| **Route D** | 0.9447 | 0.8460 | Null/negative hit-rate signal |

> **Scientific Discipline**: HydraDG preserves null/negative results honestly in evidence lineage rather than inflating claims or overwriting baselines.

---

## 🔬 Theoretical Foundations ($G^*$ & Cloud Drift)

HydraDG defines an application-specific, dimensionless information diagnostic $G^*$ and Cloud Drift ($JSD$):

- **Enßlin & Weig (2010)**: Information field theory analogy mapping graph uncertainty to an information-free-cost diagnostic $G^*$.
- **Lin (1991)**: Jensen-Shannon Divergence ($JSD$) measuring structural probability cloud drift across graph perturbations.

*Note: $G^*$ is an application-defined diagnostic metric, not physical thermodynamic energy.*

---

## 📜 Submission & Verification Links

- **Submission Summary**: [`SUBMISSION.md`](SUBMISSION.md)
- **Demo Video URL**: [https://youtu.be/7EDb6q-loPA](https://youtu.be/7EDb6q-loPA)
- **Repository**: [https://github.com/biobitworks/hydradg](https://github.com/biobitworks/hydradg)
- **Release Branch**: `hack-hydra/public-product-final-20260819`
- **License**: CC-BY-NC-ND-4.0 ([LICENSE](LICENSE))
