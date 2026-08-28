On `magicSTUDIObox.local`, start a new isolated EXP-010 Daisy worktree/branch from canonical HydraDG SHA `825964f49e730d951e9199d8386334d8083448b9`. Do not modify EXP-008, EXP-009, or the Q38 replay lane.

First read `AGENTS.md`, `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md`, the canonical EXP-008/009 preregs/closeouts, schemas, and existing Daisy examples. Preserve OFFER → ACCEPT → PLAN → PLAN_CHECK → EXECUTE → VERIFY → SCIENCE_CLOSEOUT → FCO/FCG → commit/push.

Create discrete T010-A–F work units:

A. Build a deterministic paired-binary power assessment. Treat CASE as the independent unit; 3 replicates are nested and must never inflate N. Use α=.05, target power=.80, primary MDE=15 pp, sensitivity at 10/15/20 pp, and a preregistered discordance/attrition sensitivity grid. Use exact/small-sample appropriate methods; no observed/post-hoc power. Emit required paired N and raw case-bank N.

B. Build/freeze an outcome-blind independent EXP-010 case bank of whatever size the power gate requires. Hash every source/case and prove no selection from Q38 outcomes.

C. Preregister EXP-010 as a governed-decision-schema ablation: identical evidence atoms, models/runtime/parser/scorer frozen, only decision governance changed. Define primary estimand, exclusions, parse accounting, falsifiers, and claim ceiling before inference.

D. Independently review/recompute the prereg and power calculation. STOP on any pseudoreplication, leakage, undefined estimand, or inadequate power.

E. Hash artifacts, validate custody/orchestration, commit only the prereg/power/case-bank block, push, and prove ORIGIN_PARITY=PASS. `SIGNATURE_STATE=NOT_SIGNED` unless a real authorized private-key operation occurs; MMR only if actually constructed.

F. Check the active Q38/Ollama scientific-runtime lease. If Q38 is still running, stop cleanly with `BLOCKED_RUNTIME_LEASE` after the prereg push—do not contend, change model, or fall back. If free, execute EXP-010 exactly as preregistered, preserve every null/malformed/timeout, close out statistics and FCO/FCG/MMR, atomic commit/push, and report final SHA plus next EXP-011 recommendation.

Before doing anything, save this operator prompt verbatim as a versioned PROMPT provenance artifact, SHA-256 it, and link it to the EXP-010 work unit. Do not silently choose or change any scientific variable beyond the values locked above.
