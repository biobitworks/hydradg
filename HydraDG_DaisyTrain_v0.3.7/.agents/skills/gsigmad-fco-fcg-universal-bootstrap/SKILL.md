---
name: gsigmad-fco-fcg-universal-bootstrap
description: "Intake-first FCO/FCG/MSM/Anticube bootstrap + v1.1–1.3 credibility/governance plane (BioSimulations/OMEX vs claim-specific credibility; Ollarma connect patch; Vitaology future example). Copies package from fractal-custody-objects, scaffolds registries/credibility, writes BOOTSTRAP_REPORT.md, deferred portfolio FCG edges only."
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# FCO/FCG Universal Project Bootstrap ($gsigmad-fco-fcg-universal-bootstrap)

Canonical package owner: `active/fractal-custody-objects/packages/universal-project-bootstrap/`  
Version reflects current package state (e.g. `1.3.0+tree` when sealed ChatGPT zip missing).

**Thesis:** executable + reproducible biomodels, then **claim-specific credibility** — not generic governance theater. **Ollarma** (not raw Ollama) = execution witness; BioSimulations ≠ credibility score; no dimension averages. v1.3 banks a **Vitaology** future example under `examples/vitaology/` (scaffold only).

## When to use

- New project before first EXP / notebook / prompt / hackathon commit / analysis run
- Retrofit of an existing science/clinical/hackathon/hybrid project lacking `BOOTSTRAP_REPORT.md`
- Session start when `.fco_bootstrap/` or `BOOTSTRAP_REPORT.md` is missing
- After package major bumps (e.g. v1.1 credibility → v1.3 Vitaology example / governance kernel)

## Hard rules

1. Begin read-only relative to science leaves — do not rewrite custody-bearing evidence.
2. Fill `project_intake.yaml` (UNKNOWN allowed; do not invent rights/claims).
3. Produce `BOOTSTRAP_REPORT.md` with **exactly one** protocol status.
4. No SeedGraph / Overwatch live write — only `docs/deferred_writeback_candidates.jsonl`.
5. `llm_in_science_leaf: false` on receipts.
6. Large banks stay on magicBLACKbox when already configured; pointer-only inventory.
7. Execution/reproduction ≠ `VALIDATED_FOR_BOUNDED_CONTEXT` / `DECISION_QUALIFIED`.
8. Failed mandatory credibility gates cannot be compensated by high scores elsewhere.

## Command

```bash
python3 /Users/byron/projects/active/gettingsciencedone/scripts/fco_fcg_universal_bootstrap.py \
  --project-root "{{PROJECT_ROOT}}" \
  --project-type "hybrid_research_software" \
  --claim-ceiling "UNKNOWN" \
  --force
```

Optional: `--status "READY FOR LOCAL BUILD"` only when evidence supports an allowed status.

## Outputs

- `.fco_bootstrap/v1.3.0/` — frozen package copy (LATEST)
- `project_intake.yaml`
- `00_PROJECT_BOUNDARY.md`, `01_ANTICUBE_REGISTER.csv`, `02_ASSET_AND_SKILLS_INVENTORY.md`
- `registries/*`, `fco/`, `fcg/`, MSM seed, `credibility/`
- `examples/vitaology_future_pointer/` — future example only
- `BOOTSTRAP_REPORT.md`
- `.planning/FCO_FCG_UNIVERSAL_BOOTSTRAP_RECEIPT.json`
- Deferred portfolio edges in `docs/deferred_writeback_candidates.jsonl`

## After report

OPERATOR reviews report before implementation / train / claim language.  
Smallest next gate: fill UNKNOWN intake fields → one mechanically decisive gsigmad test.

## Related

- `$gsigmad-deterministic-project-bootstrap` — scaffold-only; call **this** skill when project class is science/hackathon/clinical/FCO/hybrid
- `$gsigmad-session-start` — routes here when bootstrap missing
- Package docs: `fractal-custody-objects/docs/UNIVERSAL_PROJECT_BOOTSTRAP.md`
