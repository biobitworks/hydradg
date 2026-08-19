# Local Model Efficiency Frontier Protocol v1

## Primary question

For HydraDG's bounded Context-Iceberg diagnostic task, can a tiny/small local model produce
prospective predictions that are not dominated by larger local models when quality, latency
and memory/model size are considered together?

## Model admission

Discover exact installed model identifiers/digests first.

Candidate additions, if operator approves download:
`qwen3:0.6b`, `qwen3:1.7b`, `qwen3:4b`.

Existing approved references:
`qwen2.5:7b`, `qwen2.5-coder:7b`.

## Every evaluation item

Input:
the same frozen diagnostic packet and JSON schema.

Output:
- mechanism_label from frozen enum;
- next_run_direction;
- probabilities if supported;
- supporting evidence roots;
- counterevidence roots;
- next falsification test;
- abstain.

Run 3 replay-stability repeats per model/packet for the hackathon lane.

## Nulls

H0_TINY_QUALITY:
tiny/small model prospective accuracy is not better than the preregistered trivial null.

H0_TINY_VS_REFERENCE:
tiny/small and 7B reference have equal paired prospective correctness.

H0_LATENCY:
tiny/small has no lower median wall-clock latency than 7B reference.

H0_OUTPUT_VALIDITY:
structured-output validity rates do not differ.

Do not test superiority to an external frontier/cloud model unless an admitted external lane exists.

## Endpoints / UI

Local appliance should expose read-only:
- GET `/api/local-model/status`
- POST `/api/local-model/explain`
- GET `/api/local-model/frontier`

The explain result must expose:
- model;
- model digest if available;
- prompt SHA;
- response SHA;
- structured-output state;
- Ollama token/duration counters;
- claim ceiling.

## Promotion

Promote a tiny model to the interactive UI analyst when:
- JSON validity gate passes;
- no unsupported-claim hard failure;
- replay-stability requirement passes;
- prospective accuracy is at least the frozen minimum;
- it is on the local Pareto frontier or has an explicitly justified UX role.

The 7B models remain comparison/reference lanes even if a tiny model becomes the default UI analyst.
