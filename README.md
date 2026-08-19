# HydraDG — Graph-Native Governed Context Engine

HydraDG is a governed memory and context engine that uses **HydraDB** to represent changing state as typed graph projections, preserve complete evidence lineage behind an answer, and make state divergence, contradiction, and recovery mechanically inspectable.

---

### Why HydraDG Exists

Ordinary AI memory systems overwrite, flatten, or silently mutate context over time. HydraDG prevents context corruption by storing immutable **First-Class Objects (FCOs)** in a **First-Class Graph (FCG)** custody graph. Every state change retains its complete historical provenance, supersession links, contradiction edges, and null/negative experimental outcomes.

---

### Key System Architecture

```text
LOCAL / DEVELOPMENT                     PUBLIC / JUDGES
magicSTUDIObox                          GitHub Public Repo
  ├─ local HydraDB                        ↓
  ├─ local FCG                            Vercel Next.js
  └─ local Next.js                        ↓ (server-side API)
       ↓                                  HydraDB Hosted API
reproducibility / video                   ↓
                                          public-safe FCG projection
                                          ↓
                                          interactive judge demo
```

- **HydraDB**: The load-bearing graph database used as the high-performance query, vector, and relational projection substrate.
- **FCO / FCG**: Canonical custody and provenance layer ensuring zero silent state mutations.
- **Context Iceberg**: Interactive 4D state-space visualization tracking structural Cloud Drift ($JSD$) and governed Gibbs free-cost deltas ($\Delta G^*$).
- **Hit@K & Recall@K**: Strict retrieval performance metrics, evaluated independently from $G^*$ diagnostic abstractions.

---

### What Was Actually Measured (Track 03 Benchmark)

- **Dataset**: `xiaowu0162/longmemeval-cleaned` (500 full cases, 23,867 sessions, 4,776 entities, 3,506 facts).
- **Matrix Determinism**: 100% bit-for-bit replicate equality across $2 \times 2$ matrix cells ($H_{0,\text{rep}}$ PASS).
- **Prospective Depth ($K=15$)**: $G^* = -0.3448$, $\text{Hit}@15 = 0.9851$, $\text{Recall}@15 = 0.9582$ ($\Delta \text{Recall} = +11.2\text{ pp}$).
- **Historical Claim Discipline**: Preserved original full500 negative/neutral retrieval baseline without overwriting or claim inflation.

---

### How to Try HydraDG

- **Public Live Demo**: [http://127.0.0.1:3012/](http://127.0.0.1:3012/) (Local Next.js + HydraDB)
- **Judge Walkthrough Flow**: `/` $\to$ `/judge` $\to$ `/track03` $\to$ `/graph` $\to$ `/evidence` $\to$ `/knowledge` $\to$ `/how-to` $\to$ `/eligibility`
- **Static Presentation Fallback**: [http://127.0.0.1:3012/backup/hydradg.html](http://127.0.0.1:3012/backup/hydradg.html)
- **Local Developer Setup**:
  ```bash
  npm ci
  npm run build
  HYDRADG_ROOT=. HYDRADG_VIDEO_MODE=live bash scripts/start_video_demo.sh
  ```

---

### Verification & Custody Roots

- **Release Commit**: `25326727165f0d3f6eefac54425fa1e7042dea8f`
- **Project FCG Root**: `experiment:fa170ab51cdfba46f9a24979c9be9b90fdc4ccedcdb292f313aa4439a92b08d8`
- **HydraDB Projection Root**: `projected_nodes=9,projected_edges=8`
- **Chrome Screenshot Manifest SHA-256**: `55adcc1df04dd8e9a6a1fdc7b24f0654e8f3a68dd005c09e25d49425f79d7734`
- **Signature State**: `PENDING_EXTERNAL_PRIVATE_KEY_OPERATION` (Handed off for signature on magicPRObox)
- **Claim Ceiling**: `PUBLIC_PRODUCT_DEPLOYMENT_AND_HYDRADB_TRACEABILITY_ONLY`
