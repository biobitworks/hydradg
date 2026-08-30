# FCG Model Rooting Recommendation (Ollarma Parallel Review A)

**Claim ceiling:** ARCHITECTURAL_RECOMMENDATION_ONLY — not signed, not FCG-appended.

## Identity summary

| Concept | Canonical representation | NOT equivalent to |
|---|---|---|
| Role/gateway actor | `fco:actor:ROLE`, `runtime_model=ollarma/role` | Ollama weight digest |
| Ollama model identity | `actor_class=OLLAMA_MODEL`, `actor_id=approved_name`, `model.runtime_digest` | FCG root |
| Invocation | `agent_model_handoff` receipt (`handoff_id`, receipt SHA-256) | FCG root_after |
| Orchestration envelope | `orchestration_work_unit` + `parent_receipt_sha256[]` | Scientific verification |
| FCG state | `fcg_root_before` / `fcg_root_after` on append | Model root |
| MMR | `merkle_mmr.root` on receipt | SHA-256 of model weights |

## Answers

1. **Persistent MODEL ACTOR identity:** Stable tuple `(bridge=OLLARMA, approved_name, runtime_digest)` plus, for gateway lanes, role actor `fco:actor:*`.
2. **One MODEL INVOCATION:** One `hydradg.agent_model_handoff.v1` receipt per material call; optional work-unit wrapper.
3. **Parent of invocation:** `parent_handoff_sha256` (delegating receipt), with `input_dependencies[]` binding prompt/case bytes.
4. **Graph shape:** Reuse handoff parent chain + FCG append fields; **do not** add MODEL_ACTOR_ROOT / INVOCATION_ROOT Merkle nodes.
5. **Existing equivalents:** `MODEL_ACTOR` ≈ handoff `model{}` + `actor_id`; `INVOCATION` ≈ handoff receipt; `EXECUTION` ≈ work_unit (orchestration only, not a root).

## UI hierarchy (projection)

```
HYDRALAMP_RUN (work_unit / run receipt)
  ├─ role actors (fco:actor:*)
  ├─ handoff receipts (OLLAMA_MODEL invocations)
  ├─ gateway events (HYDRALAMP_EVENTS.jsonl)
  ├─ deterministic verifiers (DETERMINISTIC_TOOL handoffs)
  └─ media evidence (derived from EVENT / verification work_unit)
```

This is **HydraDB/query + deterministic UI layout**, not new canonical FCO edges.

## Media custody

- **RAW MEDIA FCO:** exact capture bytes (screenshot/video).
- **PROVENANCE MEDIA FCO:** metadata linking to triggering `event_hash` or verification scope.
- **VERIFICATION RECEIPT:** deterministic gate output (e.g. browser verify JSON).
- Parent: verification **work_unit** or **event**, not the model visible in the frame.

## Panel disagreement (resolved)

- **Earliest divergent assumption:** conflating HydraLamp **role actors** with **Ollama model tags**.
- **Resolution:** keep layers separate; same Ollama model across runs keeps stable identity tuple, **new handoff per invocation**.

## Schema change

**Not required** for minimum viable lineage. **Defer** optional FCO types until upstream `FCO_SCHEMA.json` is present in checkout.

See `FCG_ROOTING_COMPARISON.json` and `FCG_ROOTING_RECOMMENDATION.json` for machine-readable reconciliation.
