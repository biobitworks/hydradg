# HydraLamp Golden Path

## Sequence

```
REFERENCE
  → POISON (proposed)
  → DENIAL / QUARANTINE (not canonicalized)
  → REPAIR / ANTIDOTE (authorized promotion)
  → RESTORATION (PASS)
  → MEDIA CUSTODY (standalone lane)
  → RECOMPUTE / DELTA INSPECTION
  → VERIFY (judge strip + custody receipt)
```

## Reconciliation delta (after RESTORATION)

1. Frozen 46-event stream (`44e9d3dc…1690d`) — **source, not modified**
2. Deterministic recompute (`reconcile_measurements.py`)
3. Reconciliation delta JSON — **derived evidence**
4. Judge projection — eight metrics + claim ceiling
5. Public projection — `PROJECTION_ONLY_DERIVED_EVIDENCE`

Models propose. Custody decides.

## Separate lanes (do not merge)

- **46-event golden lane** — HydraDG frozen events + judge strip
- **Authorization gauntlet** — 15×R1/R2/R3 LOCAL_PASS_AT_3=1.0 (standalone HydraLamp)
- **Standalone media** — BYTE_IDENTITY/Pixel seal PASS at HydraLamp `d9f824e`
