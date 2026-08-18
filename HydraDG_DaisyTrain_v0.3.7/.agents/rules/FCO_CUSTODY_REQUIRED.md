# FCO/FCG custody is mandatory in this Project

@../../AGENT_MODEL_TURN_FCO_POLICY.md
@../../SEEDGRAPH_SUBMISSION_REVIEW.md

For every substantive task:

1. Use the installed FCO/FCG skill. If its exact skill identity/path is unavailable,
   stop and report `FCO_SKILL_NOT_LOADED`; do not silently approximate it.
2. Maintain the durable graph configured by
   `/Users/byron/projects/active/hydradg-knowledge-graph/env.sh`.
3. Material Agent, Model, visible Turn, ToolAction, and KnowledgeUpdate objects must be
   emitted to the FCO/FCG journal.
4. A task is not custody-complete until `scripts/verify_live_custody.py` passes.
5. Do not call local JSONL `HYDRADB_INGESTED`.
6. Hashing is not signing and is not Merkle/MMR commitment.
7. Do not record private chain-of-thought. Preserve visible input/output and tool/evidence
   artifacts only.
8. Before concluding, report the new Turn ID, current nodes/edges SHA-256, and whether a
   KnowledgeUpdate was emitted.

If custody emission fails, report the failure rather than claiming FCO/FCG compliance.
