# Agent / Model / Turn FCO-FCG policy

**Status:** `PROPOSED_HYDRADG_EXTENSION`  
**Purpose:** apply the adopted FCO/FCG operating rules to multi-agent orchestration.

This policy does not modify the upstream FCO/FCG canonical specification.

## 1. First-class objects

Every material orchestration route SHOULD preserve separate logical objects for:

- `Agent` — one named/role-scoped executing agent identity;
- `Model` — exact provider/model/tag/version/digest when known;
- `AgentSession` — bounded execution session;
- `Turn` — visible input/output pair;
- `ModelInvocation` — model invocation parameters and model reference;
- `ToolAction` — command/API/tool action plus its receipt/log;
- `KnowledgeAtom` — smallest admitted addressable evidence unit;
- `KnowledgeUpdate` — proposed/add/supersede/contradict/reject update;
- `AdmissionDecision` — admission result and ceiling;
- `ContextEnvelope` — declared contextual/version boundary.

Do not store or request private chain-of-thought. A Turn consists only of visible/preserved
input/output artifacts plus declared action metadata.

## 2. New agent

When Antigravity spawns a subagent, create exactly one immutable `Agent` FCO using:

- `agent_key`
- role
- runtime/orchestrator
- parent agent if any
- authorship class
- declared permissions/scope
- claim ceiling
- custody state

Connect it with `SPAWNED_AGENT`.

Changing an agent role/scope materially creates a new Agent object; do not silently mutate the old identity.

## 3. New model

For each distinct model route create a `Model` FCO containing, when available:

- provider/runtime;
- exact model name/tag;
- version/digest/commit;
- quantization;
- context length;
- relevant generation parameters;
- local/cloud backend;
- model metadata source;
- claim ceiling.

Examples include an Antigravity-hosted model and an Ollama model tag.
Do not call two tags/versions the same Model object unless their declared identity is actually equal.

## 4. Turn identity

For each material visible turn:

1. preserve exact input bytes in a file;
2. preserve exact output bytes in a file;
3. SHA-256 both;
4. build a canonical Turn object;
5. connect it to Agent, AgentSession and Model;
6. connect to the previous Turn using `FOLLOWS_TURN`;
7. record tool logs as separate `ToolAction`/`Artifact` objects;
8. record any proposed knowledge update separately.

A hash establishes content identity only.

## 5. Knowledge updates

Never overwrite knowledge in place.

Use:
- `ADD`
- `SUPERSEDE`
- `CONTRADICT`
- `REJECT`
- `ABSTAIN`
- `REPAIR`

A knowledge update SHOULD carry:
- evidence atom IDs;
- source/provenance;
- evidence class;
- uncertainty;
- claim ceiling;
- admission state;
- prior object IDs when superseding/contradicting.

Until HydraDB is pinned and an actual write/read test succeeds, append to the local
API-neutral journal in `custody/live/`.

## 6. HydraDB boundary

`custody/live/nodes.jsonl` and `custody/live/edges.jsonl` are staging FCO/FCG objects.

They are **not evidence of HydraDB ingestion**.

After the exact HydraDB API/commit is pinned:
- ingest the same immutable IDs;
- perform a write/read round trip;
- record the HydraDB receipt as another FCO;
- only then use `HYDRADB_INGESTED`-type claims.

## 7. In-turn requirement

All material agent turns in the Antigravity daisy train MUST call
`scripts/record_agent_turn.py` after the visible output is finalized.

Tool actions SHOULD be registered with `scripts/record_tool_action.py`.

Knowledge changes MUST be passed through `scripts/record_knowledge_update.py`.

Failure to record custody does not invalidate the computation itself, but lowers the
custody/provenance claim ceiling and must be surfaced in the handoff.
