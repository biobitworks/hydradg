# HydraLamp Sentinel / CFMO / MMR Successor — 2026-08-26

## Predecessor Located (Not Recreated)

Historical Sentinel is **Antigence host FIM**, not a HydraDG module. Full receipt:

`eval/hydralamp_20260826/SENTINEL_PREDECESSOR_RECEIPT.json`

| Field | Value |
|-------|-------|
| SENTINEL_SOURCE_REPO | biobitworks/antigence |
| SENTINEL_SOURCE_SHA | 1f12b3c2b2f7df90e11753f74443e4add48d5b46 |
| SENTINEL_IMPLEMENTATION_DATE | 2026-07-11 |
| Core files | `src/antigence/service/sentinel.py`, `scripts/sentinel_fco_bridge.py`, `src/antigence/security/ingress.py` |

HydraLamp **extends** federation authorization; Antigence Sentinel **remains** host/FIM predecessor.

---

## Successor Components

| Module | Role |
|--------|------|
| `hydralamp/sandbox.py` | Dual-world runner (SANDBOX + OPEN_WORLD); defense-in-depth, not trust root |
| `hydralamp/anticube.py` | Preregistered perturbations (`ANTICUBE_PERTURBATIONS.json`) |
| `hydralamp/context_score.py` | ContextScoreFCO — routing/diagnostic only; `authorizes_access=false` invariant |
| `hydralamp/cfmo.py` | Append-only version ledger; poison/quarantine/canonical never overwritten |
| `hydralamp/mmr.py` | Frozen HYDRALAMP_MMR_V1 with verification receipt |
| `hydralamp/toy_key.py` | TOY_DISTRIBUTED_PRIVATE_KEY mode (claim ceiling: no authenticity/confidentiality) |
| `hydralamp/self_safe.py` | SELF_SAFE = proof of possession + authorization (not context score) |
| `hydralamp/orchestrator.py` | Wires CFMO + MMR + context scores + toy key metadata |

---

## Dual-World Adversarial Fixtures

Every anticube perturbation runs in:
- **A. SANDBOX** — blocked ops: direct canonical write, FS escape, key exfil
- **B. OPEN_WORLD** — signed-capability gateway only

Hard gates unchanged:
- `UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE=0`
- `UNAUTHORIZED_CANONICAL_WRITES=0`
- False denials reported separately (`FALSE_DENIAL_COUNT`)

---

## MMR Commitment

MMR is **not** an ordinary event hash. Frozen spec in `hydralamp/mmr.py`:
- Leaf fields: `event_index`, `event_hash`, `cfmo_version_id`
- Encoding: canonical JSON UTF-8
- Ordering: event_index ascending
- Algorithm: HYDRALAMP_MMR_V1
- Receipt: `eval/hydralamp_20260826/MMR_COMMITMENT.json`

---

## Video

Multi-panel renderer v2 (`render_hydralamp_frames.py`):
- Sandbox world / open world / actor field / FCG poison-repair / CFMO trajectory / MMR progression
- No transition without real event in `HYDRALAMP_EVENTS.jsonl`

---

## Variance Policy

| Deterministic | Probabilistic |
|---------------|---------------|
| fixtures, policies, scorers, MSM, MMR, replay | model outputs, actions, trajectories |

Preserve R1/R2/R3 — do not force equality across probabilistic actors.
