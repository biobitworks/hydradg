# HydraDG — Video & Judge Demo Walkthrough Script (2:40 Target)

> **Recording Setup**: Screen resolution **1920x1080 (16:9 full screen)**. Open local application surface: [http://127.0.0.1:3012/](http://127.0.0.1:3012/).
> **Time Limit**: Keep total video duration under 3 minutes (recommended **2:20–2:40**).

---

## ⏱️ Section-by-Section Timing & Click Sequence

```mermaid
timeline
    title 2:40 Video Walkthrough Flow
    0:00 - 0:20 : 1. Problem & Hero Overview
                : Open http://127.0.0.1:3012/
                : Highlight live 4D Context Iceberg
    0:20 - 0:55 : 2. Interactive 4D State Field
                : Open /graph
                : Rotate x/y/z, scrub time t0->t2, click heat tabs
    0:55 - 1:25 : 3. Golden Path Judge Lab
                : Open /judge
                : Click Load Fixture -> Inject Poison -> Antidote
    1:25 - 1:55 : 4. Executed Track 03 Evidence
                : Open /track03
                : Show 500 cases / 23,867 sessions & null baseline
    1:55 - 2:20 : 5. Deep FCO Lineage & KB
                : Open /evidence & /knowledge
                : Trace FCO source -> atom -> claim ceiling & citations
    2:20 - 2:40 : 6. Claim Boundary & Closing
                : Show eligibility & conclusion
```

---

### 1. Problem & Hero Overview (0:00 – 0:20)
- **URL / Screen**: [http://127.0.0.1:3012/](http://127.0.0.1:3012/)
- **Action**: Hover cursor over the interactive 4D Context Iceberg hero on the home page.
- **Narration Cue**:
  > *"Long-lived AI memory systems often flatten or overwrite state updates. When a fact changes, prior context and null evidence disappear. HydraDG turns chain of custody into a navigable, governed 4D state field."*

---

### 2. Interactive 4D State Field & Context Iceberg (0:20 – 0:55)
- **URL / Screen**: Click **"Open full 4D FCG"** or navigate to [http://127.0.0.1:3012/graph](http://127.0.0.1:3012/graph).
- **Actions**:
  1. Click and drag on the 3D canvas to rotate spatial dimensions ($x \cdot y \cdot z$).
  2. Drag the **Time slider** from $t0 \to t1 \to t2$.
  3. Click the heat layer tabs: `mutation`, `restoration`, and `|ΔG*|`.
  4. Click on node `StateSnapshot · t1` (`mutation`).
- **Narration Cue**:
  > *"Here on the 4D canvas, we rotate spatial dimensions and scrub history from reference to mutation to restoration. Hovering or clicking a node reveals its node-level Shannon entropy H, G*, and relative ΔG* delta against baseline t0, without collapsing accuracy into a single arbitrary score."*

---

### 3. Golden Path: Reference → Poison → Antidote (0:55 – 1:25)
- **URL / Screen**: Click **"Try the guided demo"** or navigate to [http://127.0.0.1:3012/judge](http://127.0.0.1:3012/judge).
- **Actions**:
  1. **Step 1**: Click **"Load deterministic fixture"**.
  2. **Step 2**: Click **"Refresh cases"** $\to$ select case `gpt4_4edbafa2` $\to$ click **"Load case into HydraDB"**.
  3. **Step 3**: Click **"Run retrieval"**.
  4. **Step 4**: Click **"Inject poison"** $\to$ note `SUPERSEDED_BY` & `CONTRADICTS` graph edges.
  5. **Step 4**: Click **"Apply antidote"** $\to$ verify reference recovery without erasing divergent history.
- **Narration Cue**:
  > *"In Judge Lab, we start with a reference fact, inject a non-safe poison perturbation, and observe how HydraDG creates explicit SUPERSEDED_BY and CONTRADICTS edges. When antidote restoration is applied, the declared current state recovers while the divergent history remains fully inspectable."*

---

### 4. Executed Track 03 Evidence & Benchmark Preservation (1:25 – 1:55)
- **URL / Screen**: Navigate to [http://127.0.0.1:3012/track03](http://127.0.0.1:3012/track03).
- **Actions**: Highlight the executed metrics table (**500 cases / 23,867 sessions / 4,776 entities / 3,506 facts**). Point out `Hit@5` and `Recall@5` columns.
- **Narration Cue**:
  > *"Across 500 LongMemEval benchmark cases and 23,867 sessions, HydraDG constructed and queried the typed temporal graph. Crucially, the completed ablation showed that graph-native routes did not outperform the flat baseline at the tested configuration. Rather than optimizing away this null result, HydraDG preserves null and negative evidence as governed custody."*

---

### 5. Deep FCO Lineage & Knowledge Base Citations (1:55 – 2:20)
- **URL / Screen**: Navigate to [http://127.0.0.1:3012/evidence](http://127.0.0.1:3012/evidence) and [http://127.0.0.1:3012/knowledge](http://127.0.0.1:3012/knowledge).
- **Actions**:
  1. Click an FCO node to view SHA-256 hash, evidence class, and claim ceiling.
  2. In Knowledge Base, highlight the **Enßlin & Weig (2010)** citation for $G^*$ and **Lin (1991)** citation for $JSD$ Cloud Drift.
- **Narration Cue**:
  > *"Every result resolves backward from claim to evidence, transformation, and source FCO. G* is grounded as an application-defined dimensionless diagnostic, citing Enßlin & Weig 2010 for its theoretical free-energy analogy, and Lin 1991 for Jensen-Shannon Cloud Drift."*

---

### 6. Claim Boundary & Closing Statement (2:20 – 2:40)
- **URL / Screen**: Navigate to [http://127.0.0.1:3012/eligibility](http://127.0.0.1:3012/eligibility) or return to Home page.
- **Actions**: Show submission custody status: `PUBLIC_GITHUB=PASS`, `SUBMISSION_READY=YES`.
- **Closing Sentence (Mandatory)**:
  > *"HydraDG is not a leaderboard claim. It is a governed memory experiment: change state, observe the first divergence, preserve custody, test recovery, and keep positive, null, negative, and abstaining results in the same graph."*

---

### 📋 Key Checklist Before Hitting Record
- ✅ Local Next.js server active on `http://127.0.0.1:3012/`
- ✅ Local Best-Use server active on `http://127.0.0.1:8787/`
- ✅ Browser in full-screen 1920x1080 resolution (Google Chrome)
- ✅ All 4 steps in `/judge` tested and responsive
