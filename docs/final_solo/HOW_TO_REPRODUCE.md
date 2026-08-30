# How To Reproduce — NewInML 2026 Solo HydraDG

## WHAT IS THIS?
Governed solo submission lane for HydraDG / NewInML 2026 on branch `cursor/newinml-daisy-execute-20260829` (PR #36).

## WHAT DO I RUN?
```bash
cd /Users/byron/projects/active/hydradg
git checkout cursor/newinml-daisy-execute-20260829
python3 scripts/newinml_doc_roundtrip_execute.py
python3 scripts/newinml_seedgraph_full_traceability_execute.py
python3 scripts/newinml_gpu_sglang_daisy_execute.py   # expect BLOCKED unless SGLang installs
```

## WHAT SHOULD HAPPEN?
- Doc roundtrip emits `eval/newinml_doc_roundtrip_20260829/13_closeout/FINAL_CLOSEOUT.json` with `deterministic_green: true`.
- SeedGraph traceability emits GREEN closeout under `paper/newinml2026_solo/seedgraph_traceability/`.
- GPU lane preserves BLOCKED terminal if SGLang install fails.

## WHERE IS THE RESULT?
- Runtime status: `eval/final_solo_closeout_20260829/EXPERIMENT_RUNTIME_STATUS_ML.json`
- Completion matrix: `eval/final_solo_closeout_20260829/SOLO_COMPLETION_MATRIX_ML.json`
- Paper PDF: `paper/newinml2026_solo/manuscript/build/main.pdf`

## HOW DO I VERIFY IT?
```bash
shasum -a 256 paper/newinml2026_solo/manuscript/build/main.pdf
python3 scripts/final_solo_closeout_20260829.py
gitleaks detect --source . --no-git
```

## WHAT DOES A FAILURE MEAN?
- **BLOCKED** — dependency missing; do not promote claims.
- **UNDERPOWERED** — historical terminal; do not recolor as PASS.
- **PARTIAL** — incomplete matrix (e.g., Q38); omit from primary results.
