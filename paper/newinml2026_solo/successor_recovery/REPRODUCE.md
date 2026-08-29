# REPRODUCE — HydraDG SOLO Successor Recovery

## One-command reproduction (magicPRObox.local)

```bash
make newinml-reproduce
# or
python3 scripts/reproduce_newinml.py --verify
```

## Frozen submission reference
- BASE_FROZEN_SUBMISSION_COMMIT: `780874042e78a414c57079ce4ec150754beb45f2`
- BASE_FROZEN_PDF_SHA256: `c16be09e6ade15bbe28afa4a41d028e76806c7ec4d86c525d20c97e006497c04` (custody evidence, not final candidate)

## Statistics (deterministic on PRO)
| Item | Hash |
|------|------|
| R1 output root | `3e521a58917da1342746124b281580f5c24a982a546386624e731982618aa9a1` |
| R2 output root | `3e521a58917da1342746124b281580f5c24a982a546386624e731982618aa9a1` |
| R3 output root | `3e521a58917da1342746124b281580f5c24a982a546386624e731982618aa9a1` |
| Gate | `PASS` |

## Studio-bound experiments (verify only — DO NOT rerun)
- EXP-008, EXP-009, Stage-2 model inference: verify frozen verdict JSON hashes
- Commands: compare `paper/newinml2026_solo/provenance/admitted/*VERDICT.json`

## Figures
| Figure | Command | Expected runtime |
|--------|---------|------------------|
| FIG-001–007 | `python3 scripts/build_successor_recovery.py --figures` | <30s |

## Host requirements
- Python 3.10+, numpy, scipy, pandas, matplotlib
- tectonic or pdflatex for PDF
- No magicSTUDIObox.local required for deterministic replay
