# magicSTUDIObox Local-Private HydraDG Appliance v1

## Decision

Do not depend on the discontinued macOS Server application.

Use current macOS server primitives:

- `launchd` / LaunchAgent for durable user-level service supervision;
- Bonjour local hostname (`magicstudiobox.local`) for LAN discovery;
- macOS Application Firewall for inbound controls;
- built-in SSH / Remote Login for private remote tunneling when needed;
- Next.js production server for the HydraDG web surface;
- local HydraDG Best-Use/HydraDB services on loopback;
- local Ollama API on loopback;
- HydraDG server-side API as the only browser-facing inference bridge.

No public hosting is required for the local demo.

## Network boundary

Preferred ports:

- `127.0.0.1:11434` — Ollama; NEVER expose directly to LAN in v1.
- `127.0.0.1:8787` — HydraDG Best-Use scientific API.
- HydraDB endpoint — retain current loopback/private configuration.
- `0.0.0.0:3010` — Next.js judge site when LAN demo mode is explicitly enabled.
- `127.0.0.1:3010` — Next.js when private-on-box mode is selected.

LAN judge address:
`http://magicstudiobox.local:3010`

Remote private mode:
use SSH port forwarding rather than exposing Ollama/HydraDB.

Example:
`ssh -L 3010:127.0.0.1:3010 -L 8787:127.0.0.1:8787 <user>@magicstudiobox.local`

## Truth flow

Canonical custody
→ canonical FCG
→ HydraDB projection
→ deterministic Iceberg state artifact
→ HydraDG server
→ browser UI.

For local-model interpretation:

Frozen diagnostic packet
→ HydraDG server-side route
→ Ollama localhost API
→ structured probabilistic output
→ SHA-256 prompt/response/config/model metadata
→ FCO/FCG append
→ UI.

The browser must not call `localhost:11434` directly.

## Local analyst model

Role:
bounded explanation and prospective hypothesis generation only.

The model may:
- summarize the currently selected FCO/context state;
- name a mechanism from a preregistered enum;
- identify supporting/counterevidence;
- state a falsification test;
- predict the direction of the NEXT Daisy run;
- abstain.

The model may NOT:
- mutate HydraDB;
- change G* weights;
- change the distribution vocabulary;
- promote a scientific claim;
- write directly to the canonical custody store without the governed writer.

Output class:
`PROBABILISTIC_MODEL_OUTPUT_ONLY`.

## Model ladder

Reverify `ollama list` locally before admitting any model.

Candidate ladder for the efficiency experiment:
- tiny: `qwen3:0.6b`
- small: `qwen3:1.7b`
- medium-local: `qwen3:4b`
- established local reference: current approved `qwen2.5:7b`
- established local code reference: current approved `qwen2.5-coder:7b`

Do not automatically replace the already-approved 7B model. The smallest model becomes
the UI analyst only after the same structured-output canary and prospective prediction gate passes.

## Tiny-vs-large evaluation

Do not use a vague "smaller is cheaper and just as good" claim.

For every model, record:

Scientific/prospective:
- structured JSON validity rate;
- abstention rate;
- mechanism exact agreement;
- prospective direction accuracy on held-out Run N+1;
- Brier score if valid probabilities are emitted;
- false unsupported-claim rate under a frozen checker.

Operational:
- model artifact/digest;
- model bytes on disk;
- load duration;
- prompt evaluation tokens and duration;
- generated tokens and duration;
- tokens/sec;
- end-to-end wall time;
- process memory if actually measured.

Optional energy:
- record only if measured using a declared macOS measurement procedure.
- do not infer watt-hours from model size.

Cost:
- local marginal API fee is zero, but hardware/electricity are not zero.
- do not call local inference "free."
- external cloud-price comparison is a separate current-price evidence lane.

## Pareto frontier

Do not create an arbitrary one-number winner for the first release.

A model is `LOCAL_EFFICIENCY_FRONTIER` if no admitted competitor is simultaneously:
- better/equal prospective quality,
- faster/equal,
- and smaller/equal,
with at least one strict improvement.

This lets a 0.6B/1.7B model legitimately "compete" by being non-dominated for the bounded task
without claiming it is generally equivalent to a frontier model.

## Two drift layers

Preserve the existing Context Iceberg score:

`StructuralCloudDrift = 100 × JSD(structural_context_distribution_t || structural_reference)`

Add a NEW preregistered lane rather than changing the old score after seeing K5/K10:

`RetrievalCloudDrift = 100 × JSD(retrieved_evidence_distribution_t || retrieved_reference)`

Possible frozen retrieval buckets:
- relevant vs irrelevant evidence;
- rank bucket 1–5 / 6–10 / >10;
- evidence type;
- question type;
- contradiction/supersession state.

The hero may expose:
- outer halo = StructuralCloudDrift;
- inner halo / pulse width = RetrievalCloudDrift;
- hue = signed ΔG*.

Do not imply either halo causes the observed accuracy change.

## Correction to the current K5→K10 interpretation

Current evidence supports a descriptive aggregate change:
- ΔG* observed;
- Δ hit@K observed;
- Δ recall@K observed.

One aggregate K5→K10 comparison does NOT by itself establish a statistically significant
association between lower G* and higher recall.

Require one of:
- paired per-case G* contributions with preregistered association test; or
- multiple preregistered independent conditions/runs providing enough observations.

Until then:
`H0_GA = NOT_REJECTED / INFERENCE_PENDING`.

Likewise, if all model outputs are the same single class, report:
`EXACT_AGREEMENT = 100%`
and only report Cohen's kappa if the category distribution makes kappa mathematically defined
and informative.

## Demo story

"This Mac is the server."

Judges see:
1. the site served by magicSTUDIObox;
2. HydraDB retained state on the same machine;
3. local FCG/custody projection;
4. live 4D Context Iceberg;
5. a small local model explaining one selected object;
6. the same small model scored prospectively against the larger approved local model;
7. no public cloud dependency for the core loop.

Claim ceiling:
`LOCAL_PRIVATE_APPLIANCE_DEMONSTRATION`.
