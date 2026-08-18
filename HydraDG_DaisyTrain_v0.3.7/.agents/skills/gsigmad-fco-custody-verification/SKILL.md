---
name: gsigmad-fco-custody-verification
description: "Deterministic FCO custody/verification workflow: prose-mode custody-traceability probe (fixes numbered-list hijack), RECOMPUTE/leaf recompute, ollarma workflow manifest registration + deterministic-lane execution, gsigmad/antigence evaluation. Use before sealing an FCO manuscript or when h4-style traceability is blocked, stale, or measured by the wrong lens."
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# FCO Custody Verification ($gsigmad-fco-custody-verification)

Deterministic FCO custody/verification for a draft manuscript/package before the
operator deposition gate. Turns a *blocked* h4-style traceability item into a
measurable, honest verdict with a reproducible leaf.

**Thesis:** measure what the manuscript actually binds — custody atoms
(hex leaf/root/sha256 digests, DOIs, custody SPEC terms, and the manuscript's own
four-level claim stamps) — not `[Author Year]` citations. Report the honest number
against a pre-declared gate; never tune the lens until it passes.

## When to use

- h4 / traceability item is blocked or measured by the wrong lens
- Before sealing a manuscript into an FCO (dossier becomes FCO only when sealed)
- Before registering or re-running an ollarma workflow manifest on the deterministic lane
- When an existing `SENTENCE_LOGIC_REPORT.json` used the numbered-list hijack path

## Hard rules

1. Probe output is the source of truth — do not edit the report to hit the gate.
2. The gate (0.80) and the binding lens are pre-declared; changing either is an
   operator decision, not a probe edit.
3. `llm_in_science_leaf: false` on all probe receipts.
4. Deterministic lane only: register via ollarma workflow manifest
   (`validated-script`), validate with `ValidatedWorkflowManifest.model_validate`.
5. No SeedGraph / Overwatch live write — receipts only.
6. Back up the prior report before overwriting (`/tmp/` or a named backup).
7. RECOMPUTE must verify the manuscript anchor sha256 before traceability is trusted.

## Command

```bash
# 1. Corrected prose-mode probe (always prose mode; records tokenizer)
python3 gtm-cellico/scripts/prose_custody_traceability.py \
  <MANUSCRIPT.md> <OUT_DIR>        # writes <OUT_DIR>/SENTENCE_LOGIC_REPORT.json

# 2. Register + validate the workflow manifest (execution under artifacts/ollarma/...)
python3 -c "import json,sys; from pydantic import ValidationError; from ollarma.workflow_manifest import ValidatedWorkflowManifest; d=json.load(open('ollarma_workflows/<name>.json')); ValidatedWorkflowManifest.model_validate(d); print('VALID')"

# 3. Run on magicstudio deterministic lane
~/projects/active/ollarma/.venv/bin/ollarma workflow \
  --project gtm-cellico --manifest-ref <name> --step-id <step>
```

## Outputs

- `scripts/prose_custody_traceability.py` — corrected deterministic probe
- `<OUT_DIR>/SENTENCE_LOGIC_REPORT.json` — full report incl. per-sentence bindings + report_leaf
- `ollarma_workflows/<name>.json` — validated workflow manifest
- Run receipts on the custody spine (connect_push_to_studio / connect_receive)

## After report

- PASS → record verdict + report_leaf in the handoff; proceed to h5 operator gate.
- FAIL → report the honest ratio and the binding breakdown; list which block types
  (tables/headings/code) were skipped; operator decides whether to bind more prose
  sentences or re-scope the gate. Do NOT mark the h4 item clear by lowering the gate.

## Related

- `$gsigmad-fco-fcg-universal-bootstrap` — intake-first FCO/FCG/credibility bootstrap
- `$gsigmad-claim-ceiling-review` — statement classification before promotion/export
- `$gsigmad-audit-output` — AI-output audit before KG promotion
- Probe home: `gtm-cellico/scripts/prose_custody_traceability.py`
