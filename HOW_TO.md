# How-To Guide — Replicating HydraDG & HydraDB Context Engine

This guide provides step-by-step instructions for judges, reviewers, and developers to replicate the **HydraDG** web application, inspect the **HydraDB** dataset and schema, run local verifications, and explore the interactive 4D FCG memory engine.

---

## 1. Quick Start: Replicating the Web Application

The HydraDG web application (`apps/hydradg-web`) is a Next.js 16 app built with React 19 and TypeScript. It includes self-contained mock/fixture data so it runs out-of-the-box without requiring an active external database connection.

### Prerequisites
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **npm**: v9.0.0 or higher

### Installation & Launch

```bash
# 1. Clone the repository
git clone https://github.com/biobitworks/hydradg.git
cd hydradg

# 2. Install dependencies (installs web app dependencies)
npm run install:all

# 3. Start the development server
npm run dev
```

Open your browser and navigate to:
👉 **`http://localhost:3000`** (or `http://127.0.0.1:3012` if launched via demo scripts)

### Production Build Verification

To test and verify the production build locally:

```bash
# Build the production bundle
npm run build

# Start the production server
npm run start
```

---

## 2. Navigating the Interactive Web Application

The web interface features 8 key routes designed for judge inspection:

| Route | Page Title | Description & Functionality |
|---|---|---|
| `/` | **Overview / Dashboard** | High-level summary of HydraDG, architecture overview, track selection, and verification seals. |
| `/judge` | **Live Judge Memory Demo** | Interactive demonstration of **Reference $\to$ Poison $\to$ Antidote** state transitions. Visualizes how poisoned state is corrected without overwriting historical FCO provenance. |
| `/track03` | **Track 03 Benchmark Results** | Full evaluation metrics on `xiaowu0162/longmemeval-cleaned` (500 cases, 23,867 sessions). Displays K=5 ablation table and K=15 depth metrics. |
| `/graph` | **4D FCG & Context Iceberg** | Interactive state-space visualizer tracking Cloud Drift ($JSD$) and governed Gibbs free-cost deltas ($\Delta G^*$). |
| `/evidence` | **FCO Lineage Inspector** | Deep-dive inspector for First-Class Objects (FCOs), mathematical foundations (Enßlin & Weig 2010, Lin 1991), and SHA-256 evidence digests. |
| `/knowledge` | **Knowledge Base FCO Index** | Searchable knowledge base of atomized FCO nodes, claim boundaries, and custody certificates. |
| `/how-to` | **Replicability Guide** | On-site replication steps, command cheatsheet, and configuration toggles. |
| `/eligibility` | **Submission Eligibility** | Formal Track 03 checklist and rule compliance verification. |

### Static Fallback Presentation
If Node.js is not available, open the static standalone HTML bundle:
- File path: `apps/hydradg-web/public/backup/hydradg.html`
- Local URL (when server is running): `http://localhost:3000/backup/hydradg.html`

---

## 3. HydraDB Data & Schema Replication

HydraDG uses **HydraDB** as its graph projection, retrieval, and vector query substrate.

### Graph Data Models & Schemas

1. **HydraDB Schema Definitions**:
   - `HydraDG_DaisyTrain_v0.3.1/hydra/schema_nodes.json`
   - `HydraDG_DaisyTrain_v0.3.1/hydra/schema_edges.json`

2. **Graph Entity Relationships**:
   ```text
   (Session:HydraDG) ──[:NEXT | :PREV]──> (Session:HydraDG)
   (Session:HydraDG) ──[:ASSERTS]───────> (Fact:HydraDG)
   (Fact:HydraDG)    ──[:DERIVED_FROM]──> (Session:HydraDG)
   (Fact:HydraDG)    ──[:ABOUT]─────────> (Entity:HydraDG)
   (Fact:HydraDG)    ──[:SUPERSEDES]────> (Fact:HydraDG)
   (Fact:HydraDG)    ──[:CONTRADICTS]───> (Fact:HydraDG)
   ```

3. **Raw SeedGraph Data**:
   - `PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json`: Preserved 500-case initial seedgraph dataset for $K=5$ and $K=10$ evaluation tracks.

4. **Projecting Knowledge FCOs into HydraDB**:
   To project the website knowledge base into a local or hosted HydraDB instance:
   ```bash
   python3 scripts/project_website_knowledge_to_hydradb.py \
     --knowledge-json custody/website_knowledge_fco_projection.json \
     --namespace hydradg-release-kb-demo \
     --allow-write \
     --out custody/hydradb_knowledge_projection_receipt.json
   ```

---

## 4. Benchmark Verification Scripts

You can execute python verification and release gate scripts to validate data integrity:

```bash
# Check website links and route integrity
python3 scripts/check_hydradg_web_links.py

# Verify static fallback file sha and content
python3 scripts/check_static_fallback.py

# Run static video gate check
bash scripts/static_video_gate.sh

# Run full release gate verification
bash scripts/release_gate.sh
```

---

## 5. Contact & Support

For questions regarding submission replication or dataset access, see [SUBMISSION.md](SUBMISSION.md) or open an issue on the GitHub repository: [https://github.com/biobitworks/hydradg](https://github.com/biobitworks/hydradg).
