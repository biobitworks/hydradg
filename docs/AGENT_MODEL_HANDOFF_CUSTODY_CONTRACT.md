# Agent/Model Handoff Custody Contract

**Status:** binding operational contract for the HydraDG Studio Daisy branch.  
**Scope:** human/operator turns, frontier agents, Antigravity, Watchtower, Ollarma, every scientific Ollama model invocation, deterministic tools, HydraDB writeback/readback, Git/GitHub synchronization, and cross-repo handoffs.

## 1. Design lineage

This contract extends—not replaces—the existing HydraDG in-turn custody repair protocol.

It is deliberately aligned with two existing patterns:

1. **Ollarma model provenance / bridge receipts**: each model instance is content-addressed, task leaves bind prompt/result/verdict material, receipts are prev-linked, and a session root binds the run. Ollarma explicitly limits runtime trust to a provisional tier rather than allowing the runtime to self-certify into canonical truth.
2. **Fractal Custody Objects signing**: final identity binding is an Ed25519 operator signature over a recomputable FCG root. The private key remains outside the repo; the signature is meaningful only after root recomputation and public-key verification.

HydraDG therefore uses two distinct mechanisms:

- **always-on custody:** SHA-256/content-addressed handoffs + parent links + FCO/FCG lineage;
- **authorized signing:** actual private-key signature only where the canonical signing policy authorizes it.

Hashing must never be described as signing.

## 2. The handoff object

Every substantive handoff is a logical custody object with this dependency shape:

```text
source/input bytes
  -> actor/tool/model invocation
  -> exact output bytes
  -> deterministic evaluation/transformation
  -> derived evidence
  -> claim ceiling
  -> artifact/next handoff
```

The receipt must identify its parent handoff so the sequence cannot silently fork without being observable.

## 3. Actor classes

Use one of the following actor classes, or a schema-approved extension:

- `HUMAN`
- `CHATGPT`
- `ANTIGRAVITY`
- `CLAUDE`
- `WATCHTOWER`
- `OLLARMA`
- `OLLAMA_MODEL`
- `DETERMINISTIC_TOOL`
- `HYDRADB`
- `GIT_GITHUB`
- `OTHER_AGENT`

Human input and AI/model transformation must remain distinguishable.

## 4. Required identity fields

Every receipt records:

- `handoff_id`
- `timestamp_utc`
- `actor_class`
- `actor_id`
- `execution_host`
- `repo`
- `branch`
- `git_commit`
- `parent_handoff_sha256` or explicit genesis state
- `input_dependencies[]`
- `evidence_class`
- `transformation_class`
- `claim_ceiling`
- `signature`
- `merkle_mmr`

Model invocations additionally record:

- provider/bridge (`ollarma` where applicable)
- requested model name
- approved/canonical model name
- runtime model name
- runtime digest
- generation configuration hash
- prompt hash
- request hash
- raw response hash
- parser/scorer identity and hash where applicable
- scientific outcome separately from infrastructure outcome

## 5. Exact-byte rule

If exact bytes exist, hash the exact bytes.

Do not replace an exact byte hash with:

- a summary hash;
- a filename hash;
- a path hash;
- a Git blob SHA without stating that it is a Git object identifier;
- a model-reported hash that was not independently recomputed.

If original bytes are unavailable, hash only the material that actually exists and label the object `RETROACTIVE_CUSTODY_RECONSTRUCTION_FROM_AVAILABLE_RECORD` and/or `PENDING_ORIGINAL_TURN_CAPTURE`.

## 6. Ollarma and Ollama model calls

For every model call admitted into HydraDG scientific evidence, the minimum chain is:

```text
HydraDG case/source FCO
 -> frozen prompt/request FCO
 -> Ollarma-approved model identity
 -> Ollama runtime model + digest
 -> raw probabilistic response
 -> deterministic parser/scorer
 -> scientific result/counterevidence FCO
 -> FCG append
```

Rules:

- Model output is `PROBABILISTIC_MODEL_OUTPUT`, not verified evidence by itself.
- Model identity must resolve before execution.
- An absent model is an infrastructure failure, not a wrong scientific answer.
- A valid but incorrect model answer is retained as scientific negative evidence.
- No scientific call may silently fall back to a different model, host, route, or frontier provider.
- Watcher/model calls must not contend with the frozen experimental runtime unless explicitly preregistered.

## 7. Cross-agent handoffs

An agent that delegates to another agent/model must write a handoff receipt before the delegated output is promoted.

At minimum the outgoing handoff binds:

- current parent/root;
- exact task/prompt bytes or their SHA-256;
- allowed action scope;
- prohibited actions;
- current claim ceiling;
- expected output paths/types;
- expected next actor/model;
- current Git commit and execution host.

The receiving actor's receipt must reference the outgoing handoff hash.

This applies to:

- ChatGPT -> Antigravity
- Antigravity -> Ollarma
- Ollarma -> Ollama model
- model -> deterministic scorer
- Antigravity/Studio -> GitHub
- GitHub/origin -> MagicPro mirror
- any cross-repo handoff

## 8. GitHub as a handoff/synchronization surface

GitHub is not scientific custody truth, but it is the Git synchronization arbiter for the two-host Studio Daisy workflow.

For each bounded block:

1. Studio executes.
2. Raw/heavy outputs are banked durably and hashed.
3. Compact manifests/receipts/FCG deltas are committed on Studio.
4. Studio pushes to origin.
5. Origin SHA is independently resolved.
6. MagicPro fetches and fast-forwards.
7. Verify Studio HEAD = origin HEAD = MagicPro HEAD.
8. Record a `GIT_GITHUB` handoff receipt.

Do not use force reset/force push merely to obtain apparent parity. Preserve divergence first.

## 9. Signature policy

Every receipt contains an explicit signature state.

Allowed states include:

- `NOT_SIGNED`
- `PENDING_EXTERNAL_PRIVATE_KEY_OPERATION`
- `SIGNED`
- `SIGNATURE_VERIFIED`
- `SIGNATURE_FAILED`

`SIGNED` or `SIGNATURE_VERIFIED` requires evidence of an actual cryptographic operation.

The existing FCO reference pattern uses Ed25519 over a recomputable FCG root, with the private key outside the repo and the committed public key used for verification. Agents/models must never invent or expose the private key.

Routine model-call receipts are normally hash-chained and `NOT_SIGNED` unless the canonical signing policy explicitly authorizes a signature at that scope. A final/go-public FCG seal may be operator-signed when the real authorized key is available and verification succeeds.

## 10. Merkle/MMR policy

Every receipt also records the commitment state.

Do not call ordinary SHA-256 fields a Merkle/MMR commitment.

A receipt may state a Merkle/MMR root only when the actual tree/MMR construction was executed over declared leaves. A project-level commitment is only `COMMITTED` when the canonical operation and receipt exist.

## 11. HydraDB

HydraDB is a projection/query surface, not canonical custody truth.

Writeback occurs only after canonical FCO/FCG append. Readback must verify expected canonical IDs/edges. The HydraDB receipt is itself a downstream custody object.

## 12. Required handoff status block

Every substantive stage should expose:

```text
HANDOFF_ID
ACTOR_CLASS
ACTOR_ID
EXECUTION_HOST
GIT_COMMIT
PARENT_HANDOFF_SHA256
INPUT_ROOT_SHA256
OUTPUT_SHA256
FCO_STATE
FCG_ROOT_BEFORE
FCG_ROOT_AFTER
HYDRADB_PROJECTION_STATE
EVIDENCE_CLASS
TRANSFORMATION_CLASS
CLAIM_CEILING
SIGNATURE_STATE
MERKLE_MMR_STATE
NEXT_ACTOR
NEXT_HANDOFF_STATE
```

## 13. Enforcement

`scripts/check_agent_model_handoff_receipt.py` validates the baseline machine-readable contract.

The linter is a structural gate, not proof that the supplied hashes/signatures are truthful. Independent recomputation/verification remains required for claims such as `SIGNATURE_VERIFIED`, Merkle/MMR commitment, FCG validity, or HydraDB parity.

## 14. Conversation custody repair note

The operator identified that recent ChatGPT/Antigravity conversation turns were not consistently being persisted as the full handoff sequence. This contract records that gap.

Do not manufacture missing historical response hashes. Where exact historical bytes can be recovered, hash and append them as recovered evidence. Where they cannot, preserve only the available record and label it retroactive reconstruction.

From this contract onward, every substantive agent/model transition in the HydraDG Daisy workflow is expected to produce the handoff object above before claim promotion or the next bounded execution stage.
