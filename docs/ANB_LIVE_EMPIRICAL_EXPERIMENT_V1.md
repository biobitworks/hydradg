# HydraDG Agent Native Builders — Live Empirical Experiment V1

**Status:** PREREGISTERED — NOT EXECUTED — NOT FOR SUBMISSION  
**Branch:** `hack-hydra/agent-native-builders-20260826`  
**Base SHA:** `2e4522c09922b7c323f8ebecae28aaca9bbc9f6a`  
**Scientific controller/scorer:** `magicSTUDIObox.local`  
**Successor lane:** `eval/agent_native_builders_live_20260826/`  
**Prior synthetic lane (preserved):** `eval/agent_native_builders_20260826/` → `DEVELOPMENT_SYNTHETIC_FIXTURE_SIMULATION`

---

## Synthetic lane disqualification (load-bearing)

`scripts/agent_native_builders_runner.py` and its 20-fixture CONTROL/TREATMENT output are **not empirical evidence**.

Reason (see `eval/agent_native_builders_20260826/LANE_CLASSIFICATION.json`):

- TREATMENT assigns `actual_class = exp_class` and `actual_ceiling = exp_ceiling` from fixtures
- `class_correct` / `ceiling_correct` hard-coded `True` for TREATMENT
- `primary_effect` hard-coded `HYDRADG_EVIDENCE_CUSTODY_SUPERIORITY_ESTABLISHED`
- `zero_model_calls: true` — no live agent/MCP/runtime

Do **not** overwrite the synthetic lane. Use it only for fixture/scorer development.

---

## Three preregistered work units

| Track | Work unit | Input packet |
|-------|-----------|--------------|
| Track 01 — Cold start | `work_units/ANB_TRACK01_COLD_START_V1_OFFER.json` | `input_packets/TRACK01_COLD_START_INPUT.json` |
| Track 02 — Resumable boundary | `work_units/ANB_TRACK02_RESUMABLE_BOUNDARY_V1_OFFER.json` | `input_packets/TRACK02_RESUMABLE_BOUNDARY_INPUT.json` |
| Runtype product eval | `work_units/ANB_RUNTYPE_PRODUCT_EVAL_V1_OFFER.json` | `input_packets/RUNTYPE_PRODUCT_EVAL_INPUT.json` |

Validate before execution:

```bash
python3 scripts/check_orchestration_work_unit.py eval/agent_native_builders_live_20260826/work_units/<OFFER>.json
```

Lifecycle per `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md`:

`OFFER → ACCEPT → PLAN → PLAN_CHECK → EXECUTE → VERIFY → SCIENCE_CLOSEOUT → CUSTODY_APPEND → commit/push`

---

## Track 01 — ANB_TRACK01_COLD_START_V1

- **10** independent fresh starts
- Initial input = **public HydraDG domain only** (no preconfigured HydraDG MCP endpoint)
- Agent discovers machine surface → scoped auth → tools → benign evidence-proposal write
- Proposal **must remain quarantined**; return and verify custody receipt
- Test unauthorized private read and canonical write **denial**
- Tenki disposable environments when event credit available; score deterministically on Studio

---

## Track 02 — ANB_TRACK02_RESUMABLE_BOUNDARY_V1

- **5** real public evidence-review work items
- Chain: **GitHub → Runtype → Tavily → HydraDG → GitHub**
- Deliberate interruption at each major workflow stage; resume from persistent state
- No duplicate canonical writes; external evidence quarantined until governed verification
- Preserve all null / failure / timeout outcomes

---

## Runtype — ANB_RUNTYPE_PRODUCT_EVAL_V1

- Create HydraDG Runtype Product (Agent + deterministic Flow)
- Authenticated MCP Surface + API/Web trigger for judge
- Attach HydraDG tools/capabilities
- **12–20** case eval suite **as code**
- Compare exactly **two frozen** model/config variants
- Measure success, latency, cost, tool use, HydraDG deterministic grade
- Preserve Runtype execution IDs / log references; **no selective reruns**

Runtype is a **simultaneous sponsor-bounty target**, not the main-track selector.

---

## Sponsor credits (names only — no keys in repo)

Use before personal/paid resources:

| Sponsor | Credit class | Env/config name (presence only) |
|---------|--------------|----------------------------------|
| Tavily | coupon `26HACK` | `TAVILY_API_KEY` |
| Tenki | event $100 | `TENKI_API_KEY` / event credit account |
| Runtype | $50 | `RUNTYPE_API_KEY` |
| Nebius | $75 | `NEBIUS_API_KEY` |
| AIsa | $100 | `AISA_API_KEY` |
| Immersive Commons | workshop model key | `IMMERSIVE_COMMONS_MODEL_KEY` |

**Do not print or commit keys.**

External Runtype/Tenki/model activity = `EXTERNAL_PROBABILISTIC_EVIDENCE` until bound to receipts on Studio.

---

## Official rubric (computed after execution — not pre-selected)

Score **Track 01** and **Track 02** separately. Do **not** choose the main track in advance.

### Track 01 rubric (100 pts)

| Criterion | Points |
|-----------|--------|
| Cold-start success | 30 |
| It runs | 25 |
| Surface quality | 20 |
| Lands in product | 15 |
| Demo | 10 |

### Track 02 rubric (100 pts)

| Criterion | Points |
|-----------|--------|
| Real work across real boundary | 30 |
| It runs | 25 |
| Coordination design | 20 |
| Lands in product | 15 |
| Demo | 10 |

Template: `eval/agent_native_builders_live_20260826/RUBRIC_SCORECARD_TEMPLATE.json`

Recommend Track 01 or Track 02 **only from executed evidence** after both scorecards are complete.

---

## Hard gates (all tracks)

- `POLICY_UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE = 0`
- `POLICY_UNAUTHORIZED_CANONICAL_WRITES = 0`

---

## Explicit non-actions

- Do **not** submit yet
- Do **not** merge to `main`
- Do **not** spend beyond free/event credits
- Do **not** overwrite synthetic lane artifacts
