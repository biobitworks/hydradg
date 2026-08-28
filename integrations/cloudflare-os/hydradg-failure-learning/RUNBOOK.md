# Cloudflare OS + local Ollama failure-learning runbook

This runbook executes the preregistered HydraLamp × Immersive Commons postmortem experiments on `magicSTUDIObox.local`.

Cloudflare OS is the local agent workspace/control plane. Ollama provides the probabilistic model runtime. Deterministic HydraDG scripts build cases, record exact model-response bytes, score results, and construct FCO/FCG/MMR custody.

## Hard boundaries

- Run scientific/model work only on `magicSTUDIObox.local`.
- Do not modify `hack-hydra/hydralamp-20260826`.
- Use successor branch `hack-hydra/ic-failure-learning-20260827`.
- Do not silently install/replace an Ollama model during a frozen run.
- Blind cases E01–E04 must not have postmortem/EVAL_ONLY evidence in their Cloudflare OS conversation/context.
- Cloudflare OS/model output is `PROBABILISTIC_MODEL_OUTPUT`; deterministic scripts score it.
- Do not call the predecessor origin audit linear chain a full MMR.

## 0. Host and Git gate

```bash
hostname
uname -a
cd /Users/byron/projects/active/hydradg

git fetch origin
git switch hack-hydra/ic-failure-learning-20260827
git pull --ff-only origin hack-hydra/ic-failure-learning-20260827

git status --short
git rev-parse HEAD
```

Require:

```text
HOST=magicSTUDIObox.local
WORKTREE=CLEAN
BRANCH=hack-hydra/ic-failure-learning-20260827
```

If not, stop.

## 1. Freeze runtime identities

```bash
python3 --version
ollama --version
ollama list
curl -sS http://127.0.0.1:11434/api/version
curl -sS http://127.0.0.1:11434/api/ps
```

For every admitted model, record the strongest exact local identity available from `ollama show`, local manifest metadata, or equivalent.

Candidate tags are in `eval/ic_failure_learning_20260827/PREREGISTRATION.json`.

Missing candidate tags remain `BLOCKED_MODEL_UNAVAILABLE`. Do not substitute another tag.

## 2. Build deterministic cases

```bash
python3 scripts/build_ic_failure_learning_cases.py
shasum -a 256 \
  eval/ic_failure_learning_20260827/cases/CASES.jsonl \
  eval/ic_failure_learning_20260827/cases/CASE_MANIFEST.json
```

Review the manifest. Blind case payloads must not contain the postmortem answer.

## 3. Build the pre-model failure FCG/MMR

This commits the frozen forensic failure objects/control relationships in a new failure-learning domain. It does not include future model results yet.

```bash
python3 scripts/build_ic_failure_learning_fcg.py
cat eval/ic_failure_learning_20260827/custody/FAILURE_LEARNING_MMR_VERIFICATION_RECEIPT.json
```

Require:

```text
root_match=true
SIGNATURE_STATE=NOT_SIGNED
MERKLE_MMR_STATE=COMMITTED_FAILURE_LEARNING_DOMAIN
```

The predecessor `eval/ic_postmortem_20260827/ORIGIN_MMR_COMMITMENT.json` remains unchanged and remains `COMMITTED_AUDIT_DOMAIN_ONLY` using its stated simplified linear-chain algorithm.

## 4. Start / verify Cloudflare OS locally

First locate the existing checkout; do not clone a duplicate if one already exists.

```bash
find /Users/byron/projects/active -maxdepth 2 -type d -name 'cloudflare-os' -print
```

If present:

```bash
cd /Users/byron/projects/active/cloudflare-os
git status --short
git remote -v
git rev-parse HEAD
```

Record exact Cloudflare OS commit in the execution receipt.

For a clean local launch, use the repository's current local command:

```bash
pnpm run-local
```

Cloudflare OS local mode is expected at:

```text
http://localhost:8787
```

Do not change Cloudflare OS source code during a frozen model block. If a local patch is required, create a successor execution environment and record its exact Git diff/SHA.

## 5. Configure local Ollama in Cloudflare OS

In Cloudflare OS:

1. Add/select an Ollama model provider.
2. API URL: `http://localhost:11434` unless the local checkout requires another explicit format.
3. Select exactly one preregistered admitted model tag.
4. Record the selected tag and exact runtime identity.
5. Do not use a cloud model or AI Gateway fallback for this experiment.

Current Cloudflare OS source contains an Ollama provider route; the exact Cloudflare OS commit must be recorded because provider compatibility behavior can change.

## 6. Load the HydraDG Agent Skill

Use a Cloudflare OS context collection/resource containing this branch and invoke:

`integrations/cloudflare-os/hydradg-failure-learning/SKILL.md`

For blind cases, start a fresh Cloudflare OS conversation that contains only:

- the Agent Skill;
- the selected case JSON;
- no postmortem/EVAL_ONLY source.

If the conversation already contains postmortem material, discard it for the blind lane and start a fresh isolated conversation.

## 7. Stage 1 canary

Run one case per family per admitted model before the full screen.

Suggested first canary set:

```text
E01-T0
E02-0
E03-0
E04-0
E05-T0
E06-T0
E06-T1
```

For each case:

1. read the exact case row from `CASES.jsonl`;
2. invoke the `hydradg-failure-learning` skill with that case as `$ARGUMENT`;
3. copy the exact raw JSON response bytes to a temporary file;
4. record them with the recorder.

Example:

```bash
python3 scripts/record_ic_failure_learning_output.py \
  --model 'qwen2.5:1.5b' \
  --model-identity '<exact-local-identity>' \
  --case-id 'E01-T0' \
  --replicate 1 \
  --raw-file /tmp/E01-T0-qwen2.5-1.5b-r1.json \
  --cloudflare-os-commit '<exact-cloudflare-os-sha>' \
  --ollama-version '<exact-ollama-version>'
```

Malformed JSON is retained; do not repair it manually.

## 8. Canary scoring gate

```bash
python3 scripts/score_ic_failure_learning.py
```

Review:

```text
eval/ic_failure_learning_20260827/scored/SCORE_SUMMARY.json
```

Canary promotion requires:

- zero duplicate model/case/replicate keys;
- zero unknown case IDs;
- no blind-lane label leakage;
- model identity recorded;
- raw response hash recorded;
- scorer executes without changing its contract.

Incorrect diagnoses, null effects, abstentions and malformed outputs are scientific outcomes and do not by themselves invalidate the experiment.

## 9. Stage 2 screen

After canary PASS, run all generated conditions × every admitted model × 3 preregistered replicates.

Do not selectively rerun unfavorable cells.

If a process fails, preserve the cell as FAILED/TIMEOUT/MALFORMED and continue when the execution-integrity gate permits.

## 10. Post-model FCO/FCG append

After scoring, materialize each model invocation and deterministic score as successor objects conceptually:

```text
ExperimentCaseFCO
  ↓ READ_BY
ModelRunFCO
  ↓ PRODUCES
ModelDiagnosisFCO
  ↓ SCORED_BY
DeterministicFailureScorerFCO
  ↓ PRODUCES
ExperimentResultFCO
```

Then extend the failure-learning MMR with the exact model/scorer artifacts using the same canonical MMR recipe and emit a new verification receipt. Do not overwrite the pre-model commitment; create a successor commitment with explicit predecessor root.

## 11. What we are testing

The key hypotheses are:

- **H0-origin:** exposing origin/delta evidence does not reduce HydraDG/Hack-Hydra reuse confusion.
- **H0-vault:** surfacing the curated vault does not improve model-perceived evidence completeness.
- **H0-agent:** structured machine discovery does not improve cold-agent first-action accuracy.
- **H0-diagnosis:** local models cannot recover the audit's earliest divergence above chance/naive ordering.
- **H0-protocol:** the learned submission protocol does not increase the rate at which generated plans place media+vault before submit.

Retain the null if retained.

## 12. Closeout

Required closeout fields:

```text
CURRENT_BRANCH=
CURRENT_SHA=

EVIDENCE_STATE=
EXPERIMENT_STATE=

FCO_STATE=
FCG_STATE=

HYDRADB_STATE=

EARLIEST_DIVERGENCE=

CLAIM_CEILING=

SIGNATURE_STATE=
MERKLE_MMR_STATE=

NEXT_SAFE_ACTION=

FINAL_REVIEW_GATE=
```
