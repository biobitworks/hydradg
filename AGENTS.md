# HydraDG Agent and Model Custody Contract

This repository uses the FCO/FCG custody framework for every substantive human, AI-agent, model, tool, and cross-host handoff.

## Authority

Read and obey, in order:

1. `FCO_FCG_CANONICAL_SPEC.md` when present in the canonical project source set.
2. `CLAIM_CEILINGS.md`.
3. `EVIDENCE_LEVELS.md`.
4. `FCO_SCHEMA.json` / `FCG_SCHEMA.json`.
5. `SIGNING_AND_KEYS.md` or the canonical signing instructions.
6. `ANTIGRAVITY_HYDRADG_CUSTODY_REPAIR_IN_TURN_PROTOCOL_V1.md`.
7. `docs/AGENT_MODEL_HANDOFF_CUSTODY_CONTRACT.md`.
8. Current versioned reference implementations.

If a named authority file is not present in this checkout, do not invent its contents. Resolve the canonical source or record the dependency as unresolved.

## Mandatory handoff rule

Every substantive actor must emit or be represented by a custody handoff receipt before its output is promoted to the next stage. This includes:

- HUMAN/operator turns;
- ChatGPT/Codex;
- Antigravity/Gemini;
- Claude or other frontier agents;
- Watchtower;
- Ollarma;
- every Ollama model invocation used as evidence;
- deterministic scripts/tools;
- HydraDB projection/readback operations;
- Git/GitHub synchronization checkpoints.

The canonical machine-readable shape is defined in `schemas/agent_model_handoff_receipt.schema.json`.

Each handoff must bind, where applicable:

- actor class and exact actor/model identity;
- execution host and hardware identity;
- repo, branch, and Git commit;
- parent handoff/turn hash;
- exact input/dependency hashes;
- prompt/request hash for model calls;
- raw output/artifact hash;
- evidence class and transformation class;
- FCO identity/materialization receipt;
- FCG root before/after or explicit `NOT_APPENDED` state;
- HydraDB projection/readback receipt when applicable;
- claim ceiling;
- signature state;
- Merkle/MMR state.

No actor may silently omit negative, null, failed, timeout, abstention, malformed, or contradictory outputs.

## Ollarma / Ollama

Ollarma is the governed local bridge/runtime-receipt layer. Ollama models are probabilistic execution actors, not authorities.

For every scientific Ollama invocation preserve at minimum:

`HydraDG preregistration -> Ollarma-approved model identity -> Ollama runtime model/digest -> prompt/request SHA-256 -> raw response SHA-256 -> deterministic parser/scorer -> case result -> FCG append`.

Do not use an auto-degrading helper for a frozen scientific model call. Missing/unresolved models fail closed; they are not silently substituted.

## Hashing, signatures, and commitments are different

SHA-256 hashing is mandatory where exact bytes are available.

A hash is **not** a signature.

A handoff may state `SIGNED` only when an actual authorized private-key operation occurred and the signature verifies against the declared public key. Agents and models must never fabricate, print, commit, or substitute private keys.

If the authorized private key is unavailable or the signing policy does not authorize signing that handoff, record `NOT_SIGNED` or `PENDING_EXTERNAL_PRIVATE_KEY_OPERATION` as appropriate.

Likewise, `MERKLE/MMR_COMMITTED` may only be stated when the actual commitment operation and receipt exist.

## Cross-host / GitHub handoff

For the Studio Daisy lane:

- `magicSTUDIObox.local` is the scientific execution host.
- `magicPRObox.local` is controller/mirror only.
- GitHub/origin is the Git synchronization arbiter.

After each bounded scientific block, the Studio commits and pushes compact receipts/manifests/FCG deltas. The Pro checkout then fetches and fast-forwards. Do not begin the next block until Studio HEAD = origin HEAD = Pro HEAD and required worktree gates pass.

Heavy raw model outputs may remain in the verified durable bank with hashes/pointers in Git; Git synchronization does not require duplicating all raw bytes onto the controller machine.

## Enforcement

Run:

```bash
python3 scripts/check_agent_model_handoff_receipt.py <receipt.json> [<receipt2.json> ...]
```

A missing required custody field is a hard gate failure for promotion, writeback, release, or claim elevation.

## Current repair note

Earlier project conversation turns did not consistently emit the full in-turn receipt sequence. Do not retroactively pretend they did. Recoverable prior material must be marked `RETROACTIVE_CUSTODY_RECONSTRUCTION_FROM_AVAILABLE_RECORD` or `PENDING_ORIGINAL_TURN_CAPTURE` according to the existing repair protocol. From this contract onward, omission is a custody failure rather than an implicit pass.
