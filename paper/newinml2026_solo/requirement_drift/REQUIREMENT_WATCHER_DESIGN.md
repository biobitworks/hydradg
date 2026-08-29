# Future Requirement Watcher (Design Only — Not Deployed)

## Scope

Bounded polling of public requirement surfaces:

| Surface | URL | Poll interval (proposed) |
|---------|-----|--------------------------|
| Official CFP | `https://newinml.github.io/NewInML2026NeurIPS/` | 6h |
| Countdown | `https://newinml.github.io/NewInML2026NeurIPS/countdown.html` | 1h |
| OpenReview venue | `https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/NewInML` | 6h |

**Not monitored:** private Discord, email, or other non-authorized channels.

## Protocol

1. `fetch` → hash bytes (`sha256`)
2. Compare to last frozen hash in `SOURCE_UNIVERSE.jsonl`
3. If changed:
   - freeze new bytes under `source_freeze/`
   - atomize changed requirement sentences via SeedGraph
   - emit `REQUIREMENT_CHANGED` FCO
   - append FCG edge `SUPERSEDES` / `CONTRADICTS` as appropriate
   - **block** automatic submission-plan mutation
   - require operator review receipt

## Fail-closed rules

- Latest URL does **not** automatically win
- Authority ranking: submission platform config > official policy text > operational UI > organizer ephemera > derived
- Conflicts → `CONFLICT_REQUIRES_RECONCILIATION` until human `DecisionFCO`

## Outputs

- `REQUIREMENT_WATCHER_DELTA.jsonl` (per poll)
- `REQUIREMENT_DRIFT_ALERT.json` (on hash change)

## Deployment status

`NOT_DEPLOYED` — design artifact only for this case study.
