# Antigravity Handoff — Apply Agent/Model Custody Contract

Run this from the operator/controller environment, but perform project custody mutation and scientific execution on `magicSTUDIObox.local` only.

## 1. Synchronize the policy commit

Target branch:

`hack-hydra/studio-ollarma-daisy-20260821`

Current GitHub policy/audit commit after this handoff series:

`05552628201b9a55f6f0d3ec302e04c1a54e721e`

On Studio:

```bash
ssh magicstudiobox 'zsh -lc "
  set -euo pipefail
  test \"\$(hostname)\" = magicSTUDIObox.local
  cd /Users/byron/projects/active/hydradg
  git status --porcelain=v1
  git fetch origin
  git switch hack-hydra/studio-ollarma-daisy-20260821
  git merge --ff-only origin/hack-hydra/studio-ollarma-daisy-20260821
  git rev-parse HEAD
"'
```

Do not reset/clean/stash away unexpected work. If dirty or divergent, preserve/report before reconciliation.

On MagicPro after Studio is synchronized:

```bash
cd /Users/byron/projects/active/hydradg
git status --porcelain=v1
git fetch origin
git switch hack-hydra/studio-ollarma-daisy-20260821
git merge --ff-only origin/hack-hydra/studio-ollarma-daisy-20260821
```

Require:

`STUDIO_HEAD == ORIGIN_HEAD == MAGICPRO_HEAD`.

## 2. Read the new binding files

Every agent involved in HydraDG must read:

- `AGENTS.md`
- `ANTIGRAVITY_HYDRADG_CUSTODY_REPAIR_IN_TURN_PROTOCOL_V1.md`
- `docs/AGENT_MODEL_HANDOFF_CUSTODY_CONTRACT.md`
- `schemas/agent_model_handoff_receipt.schema.json`
- `custody/reviews/STUDIO_DAISY_STATUS_CLAIM_AUDIT_20260821.md`

## 3. Recompute exact SHA-256 on Studio

Compute exact file hashes on `magicSTUDIObox.local` for:

```text
AGENTS.md
docs/AGENT_MODEL_HANDOFF_CUSTODY_CONTRACT.md
schemas/agent_model_handoff_receipt.schema.json
scripts/check_agent_model_handoff_receipt.py
custody/turns/20260821T0910_CHATGPT_AGENT_MODEL_HANDOFF_POLICY_RECEIPT.json
custody/reviews/STUDIO_DAISY_STATUS_CLAIM_AUDIT_20260821.md
```

Do not treat Git blob IDs as SHA-256.

Update the ChatGPT policy receipt or append a successor receipt with the recomputed SHA-256 values. Preserve the original receipt as historical custody evidence rather than silently rewriting its epistemic state.

## 4. Materialize the current correction into canonical FCO/FCG

Use the existing canonical HydraDG FCO/FCG implementation. Do not invent a parallel graph format.

Represent:

```text
DIRECT_HUMAN_INPUT
 -> CHATGPT policy transformation
 -> GitHub policy artifacts
 -> Antigravity synchronization/application handoff
 -> canonical FCO materialization
 -> canonical FCG append
 -> HydraDB projection/readback
```

The current human directive SHA-256 already recorded is:

`5d95df8c5dd096c977f3fffa604fa800568cd66620757d4c666b3befc64a7904`

Where exact prior conversation response bytes are missing, preserve `PENDING_ORIGINAL_TURN_CAPTURE` / retroactive reconstruction status. Do not fabricate missing roots.

## 5. Every agent/model invocation now emits a handoff receipt

Applies to:

- operator/HUMAN
- ChatGPT/Codex
- Antigravity/Gemini
- Claude
- Watchtower
- Ollarma
- every Ollama scientific model invocation
- deterministic parser/scorer/tool
- HydraDB writeback/readback
- GitHub synchronization

Use `hydradg.agent_model_handoff.v1` receipts.

Run the structural linter on every new receipt:

```bash
python3 scripts/check_agent_model_handoff_receipt.py <receipt.json>
```

A linter PASS is necessary but not sufficient for cryptographic/scientific verification.

## 6. Ollarma -> Ollama receipt rule

For each scientific model case or bounded batch bind:

```text
HydraDG preregistration/case FCO
 -> outgoing Antigravity/Ollarma handoff
 -> Ollarma approved model identity
 -> exact Ollama runtime model + digest
 -> prompt SHA-256
 -> request SHA-256
 -> raw response SHA-256
 -> deterministic parser/scorer
 -> scientific outcome
 -> result/counterevidence FCO
 -> FCG append
```

The receiving Ollama-model receipt references the outgoing Ollarma handoff hash.

Do not silently substitute models/routes/hosts.

Keep infrastructure outcome separate from scientific correctness.

## 7. Hash chaining versus signatures

Every routine handoff must be content-hashed and parent-linked.

Do NOT mark routine receipts `SIGNED` unless the canonical signing policy authorizes that scope and an actual private-key operation occurs.

The FCO reference design uses an operator Ed25519 signature over a recomputable FCG root with the private key outside the repo. Agents/models must never generate a toy key or expose the private key.

If no signing operation occurred:

`SIGNATURE_STATE=NOT_SIGNED`.

If the authorized signing step is required but unavailable:

`SIGNATURE_STATE=PENDING_EXTERNAL_PRIVATE_KEY_OPERATION`.

Likewise, do not call a SHA-256 or an atomization Merkle root a project-level Merkle/MMR commitment unless the actual commitment operation and receipt exist.

## 8. Current Daisy status ceiling

Do not use the prior supplied completion wording while the full matrix is still active/incompletely accounted.

Until final accounting exists use:

`CLAIM_CEILING=STUDIO_OLLARMA_GOVERNED_CANARY_PASS_FULL_MATRIX_IN_PROGRESS_NOT_FINAL`

The prior supplied state included:

- full matrix launched;
- PID present;
- 9180 expected model-case executions;
- only 2/9 bounded blocks committed/pushed.

Therefore final completion is not yet established by that evidence.

## 9. Continue the Daisy chain with custody after each bounded block

For each model x dataset block:

1. execute on Studio only;
2. retain raw outputs, including negative/null/failure/timeout/abstention evidence;
3. compute hashes;
4. write agent/model/tool handoff receipts;
5. materialize/append canonical FCO/FCG result/counterevidence;
6. perform authorized HydraDB writeback/readback;
7. run custody linter;
8. commit explicit paths on Studio;
9. push to GitHub;
10. fast-forward MagicPro;
11. require Studio/origin/Pro SHA parity;
12. return status including latest handoff hash/root and signature/Merkle state.

## 10. Required status after every bounded block

```text
RUN_ID
CURRENT_STAGE
CURRENT_MODEL
CURRENT_DATASET

LATEST_HANDOFF_ID
LATEST_HANDOFF_RECEIPT_SHA256
PARENT_HANDOFF_SHA256

MODEL_RUNTIME_DIGEST
PROMPT_SHA256
REQUEST_SHA256
RAW_RESPONSE_SHA256

FCO_STATE
FCG_ROOT_BEFORE
FCG_ROOT_AFTER
HYDRADB_WRITEBACK_STATE
HYDRADB_READBACK_STATE

STUDIO_HEAD
ORIGIN_HEAD
MAGICPRO_HEAD
DUAL_HOST_SYNC_GATE

MODEL_CASE_EXECUTIONS_EXPECTED
MODEL_CASE_EXECUTIONS_ACCOUNTED
BLOCKS_EXPECTED
BLOCKS_COMPLETED
BLOCKS_FAILED

EARLIEST_DIVERGENCE
CLAIM_CEILING
SIGNATURE_STATE
MERKLE_MMR_STATE
NEXT_SAFE_ACTION
```

## 11. Final seal

Only after the full run is complete, all evidence is accounted, canonical FCG reconstruction passes, and the project signing policy authorizes the scope may the operator perform the real signing operation.

Verify the signature against the declared public key and retain the verification receipt.

Signing does not convert null/negative evidence into a positive result; it only binds the authorized identity to the declared recomputable root.
