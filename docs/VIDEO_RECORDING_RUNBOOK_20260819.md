# HydraDG video recording runbook — 2026-08-19

## Scope freeze

Tonight's video demonstrates the MVP that is already supported by evidence. Do not delay recording for K15, challenger-model admission, additional datasets, or new scientific optimization.

Supported story:

1. HydraDG built and queried a substantial LongMemEval-S graph through local HydraDB.
2. The completed full500 retrieval ablation retained a negative/neutral result rather than manufacturing a win.
3. FCO/FCG preserves the evidence route, state transitions, hashes, claim ceilings, and null/counterevidence.
4. The Context Iceberg presents changing graph state as x/y/z/time with Cloud Drift and signed delta-G* while keeping hit/recall separate.
5. Reference -> poison -> antidote is the judge-facing golden-path concept.

Do not claim:
- LongMemEval end-to-end QA improvement;
- retrieval superiority;
- independent replication unless a current receipt establishes it;
- signature if state is NOT_SIGNED;
- live Merkle/MMR commitment if state is NOT_PROJECT_COMMITTED;
- that lower delta-G* means better accuracy;
- that an inherited per-node halo means that node caused the full state-level drift.

## 1. Isolate the video build from active Daisy work

Do **not** switch or hard-reset the active scientific checkout. Create/update the dedicated video worktree instead:

```bash
cd /Users/byron/projects/active/hydradg
bash scripts/prepare_video_worktree.sh
```

Required output:

```text
VIDEO_WORKTREE_READY=YES
```

The helper checks out the exact remote reconciliation branch in detached mode under:

```text
/Users/byron/projects/active/hydradg-video
```

without changing the active HydraDG worktree.

## 2. Video readiness gate

```bash
VIDEO_ROOT=/Users/byron/projects/active/hydradg-video
command -v gitleaks >/dev/null 2>&1 || brew install gitleaks
HYDRADG_ROOT="$VIDEO_ROOT" bash "$VIDEO_ROOT/scripts/video_ready_gate.sh"
```

Record the live local application after:

```text
VIDEO_READY_LIVE=YES
```

If this gate fails only because the live Next.js build cannot be made green tonight, do not invent a pass. Run the static check in the video worktree and use the fallback only if it passes:

```bash
VIDEO_ROOT=/Users/byron/projects/active/hydradg-video
cd "$VIDEO_ROOT"
python3 scripts/check_static_fallback.py
HYDRADG_ROOT="$VIDEO_ROOT" bash scripts/start_video_demo.sh
```

If the launcher reports `VIDEO_DEMO_MODE=STATIC_FALLBACK`, describe it as an offline presentation fallback, not as a running live HydraDB experiment.

## 3. Start the recording surface

After a successful live gate:

```bash
VIDEO_ROOT=/Users/byron/projects/active/hydradg-video
HYDRADG_ROOT="$VIDEO_ROOT" bash "$VIDEO_ROOT/scripts/start_video_demo.sh"
```

Preferred output:

```text
VIDEO_DEMO_MODE=LIVE_LOCAL_NEXTJS
```

Fallback output:

```text
VIDEO_DEMO_MODE=STATIC_FALLBACK
```

## 4. Recording route

Preferred live route order:

1. `/` — Context Iceberg hero and value proposition.
2. `/judge` — reference / poison / antidote.
3. `/evidence` or `/track03` — full500 result and retained null/negative evidence.
4. `/graph` — rotate/scrub the 4D FCG.
5. `/knowledge` — open one project term and follow its FCO/source route.
6. `/eligibility` — close on explicit claim/signature/Merkle boundaries.

Do not spend recording time on every track page.

## 5. 100-second narration

### 0-15 seconds — problem

"AI memory systems usually give you an answer, but not a mechanically inspectable history of why that answer is current. HydraDG represents changing memory as a graph in HydraDB and preserves the evidence route with Fractal Custody Objects and a Fractal Custody Graph."

### 15-35 seconds — Context Iceberg

"This is the Context Iceberg. I can rotate the FCG in three spatial dimensions and move through time. Halo width is Cloud Drift, defined as one hundred times Jensen-Shannon divergence from a frozen reference distribution. Hue is the signed delta-G-star direction. Neither is an accuracy score, so hit and recall remain separate."

If the UI says deterministic synthetic fixture, add:

"This hero is currently using the deterministic demonstration fixture; the same read-only contract accepts validated Daisy state receipts."

### 35-55 seconds — golden path

"The judge-facing experiment is simple: reference, poison, antidote. I read the current fact, change one load-bearing state, preserve the old state using explicit supersession or contradiction relationships, then restore the valid state without deleting the perturbation history."

### 55-75 seconds — actual evidence

"We ran the full LongMemEval-S set. The graph contained 500 cases, 23,867 sessions, 4,776 entities and 3,506 facts. The tested graph retrieval treatments did not establish a positive hit-rate advantage over the flat baseline. HydraDG keeps that negative result as evidence instead of tuning it away."

### 75-90 seconds — custody

"Every result can resolve backward through the FCG: source, deterministic or probabilistic transformation, derived evidence, claim, and artifact. Hashes establish byte identity, not truth, and the UI keeps the current claim ceiling visible."

### 90-100 seconds — close

"So the product is not a leaderboard claim. It is a governed memory experiment: change state, observe the first divergence, preserve custody, test recovery, and keep positive, null, negative and abstaining results in the same graph."

## 6. Recording checklist

Before pressing record:
- browser zoom 90-100%;
- notifications/do-not-disturb on;
- terminal windows with secrets closed;
- no `.env`, bearer token, local auth token or private-key path visible;
- use a clean browser tab with only HydraDG;
- verify the top of `/` states whether the Iceberg source is synthetic or live;
- keep the video focused on one path rather than browsing every page.

## 7. Minimum acceptable recording

The video is acceptable for the MVP if it clearly shows:
- HydraDG homepage/value proposition;
- Context Iceberg interaction or static representation;
- reference -> poison -> antidote concept;
- actual full500 result with negative/null retention;
- one custody/FCO/FCG trace;
- explicit claim boundaries.

A current Vercel deployment is desirable for submission/public access but is not required to record the local demo. The self-contained static fallback exists specifically so presentation continuity does not depend on Vercel.

## Claim ceiling

`VIDEO_RECORDING_RUNBOOK_AND_RELEASE_PRESENTATION_ONLY`

This runbook does not establish that the live build, scientific golden path, signing, or Merkle/MMR gates have passed. Those states must come from their own receipts.
