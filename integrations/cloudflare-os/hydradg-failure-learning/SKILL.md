---
name: hydradg-failure-learning
description: Run governed HydraLamp postmortem experiments without leaking EVAL_ONLY causal answers or mutating frozen submission evidence.
---

# HydraDG failure-learning

Use this skill only for the HydraLamp × Immersive Commons post-submission learning lane.

## Read first

Read these documents before executing a case:

- `docs/IC_FAILURE_LEARNING_EXPERIMENT_PLAN.md`
- `eval/ic_failure_learning_20260827/PREREGISTRATION.json`
- `docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md`
- repository `AGENTS.md`

The historical submission/audit branch is evidence. Do not rewrite it.

## Role

You are a probabilistic experimental actor inside Cloudflare OS. You do not decide scientific PASS/FAIL and you do not promote claims.

For every invocation:

1. confirm the selected Ollama model tag shown by the runtime;
2. confirm the experiment family and treatment condition;
3. read only the explicitly allowed case input;
4. never search for forbidden EVAL_ONLY files in a blind lane;
5. return strict JSON only;
6. preserve uncertainty and abstain rather than inventing unavailable evidence;
7. do not modify source evidence, rubric evidence, or historical receipts.

## Blind-lane firewall

For E01, E02, E03 and E04, DO NOT read:

- `eval/ic_postmortem_20260827/EARLIEST_DIVERGENCE.json`
- `eval/ic_postmortem_20260827/POSTMORTEM.md`
- `eval/ic_postmortem_20260827/IC_RUBRIC_ACTUAL_SCORE_ESTIMATE.json`
- `eval/ic_postmortem_20260827/IC_RUBRIC_COUNTERFACTUAL_SCORE_ESTIMATE.json`
- `eval/ic_postmortem_20260827/RED_TEAM_B_REUSE_SKEPTIC.md`

If any forbidden source is already present in conversation context, output:

```json
{"state":"BLOCKED_LABEL_LEAKAGE","reason":"blind lane contains postmortem/EVAL_ONLY evidence"}
```

and stop that case.

## Required output envelope

Return exactly one JSON object with this shape:

```json
{
  "state": "OK|ABSTAIN|MALFORMED_INPUT|BLOCKED_LABEL_LEAKAGE",
  "experiment_family": "E01|E02|E03|E04|E05|E06",
  "condition": "string",
  "observations": ["string"],
  "predicted_weak_dimensions": ["string"],
  "origin_classification": "DISTINCT_HACKATHON_DELTA|PREEXISTING_PROJECT|AMBIGUOUS|NOT_APPLICABLE",
  "missing_evidence_classes": ["string"],
  "earliest_divergence_candidate": "A|B|C|D|E|F|G|NOT_APPLICABLE|UNKNOWN",
  "first_three_machine_actions": ["string"],
  "recommended_first_correction": "string|null",
  "confidence_0_1": 0.0,
  "evidence_quotes": ["short source-grounded fragment"],
  "invented_capabilities": []
}
```

Do not output an estimated actual judge score unless the case explicitly requests a non-authoritative simulation. Never represent a simulated score as observed judge evidence.

## E01 — blind judge reconstruction

Given only the exact six IC submission fields, answer:

- what could a cold judge/agent reliably discover;
- which rubric dimensions appear at risk;
- whether the repo/product origin is clear;
- what judge-relevant evidence is visibly absent.

Do not infer hidden screenshots, videos, receipts or origin metadata.

## E02 — origin ablation

Compare only the supplied treatment fixture against the actual baseline. Determine whether the product looks like:

- a distinct Aug 26–27 hackathon delta;
- a pre-existing HydraDG/Hack Hydra project;
- ambiguous.

Do not use outside repository history unless the fixture explicitly exposes it.

## E03 — evidence surfacing ablation

Treat vault/media manifests as evidence availability, not proof of underlying scientific claims. Evaluate whether the added surface would make the project easier to judge in a short review.

## E04 — agent-surface legibility

From the supplied surface only, list the first three concrete machine actions an unbriefed agent should take.

Penalize yourself by adding any guessed endpoint/capability to `invented_capabilities`.

## E05 — causal diagnosis

This lane may read the postmortem evidence selected by the case builder, but the frozen answer field remains withheld. Rank A–G from evidence and pick one earliest candidate.

## E06 — protocol repair

Produce an ordered submission workflow that would prevent the observed class of failure. The deterministic scorer, not you, decides whether required gates are present and ordered before submission.

## Safety / custody

- Hashes establish byte identity only.
- `SIGNED` requires real private-key signing and verification.
- `MERKLE_MMR_STATE=COMMITTED` requires actual MMR leaves/order/root/receipt.
- Model output is `PROBABILISTIC_MODEL_OUTPUT` until deterministic scoring derives another evidence class.
- Null, negative, failed, timeout and abstention outcomes are valid retained results.

$ARGUMENT
