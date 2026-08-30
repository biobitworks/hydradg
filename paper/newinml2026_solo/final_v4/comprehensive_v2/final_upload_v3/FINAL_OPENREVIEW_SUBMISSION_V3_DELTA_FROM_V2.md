# V3 delta from V2 (editorial successor only)

**Immutable preserved:** `FINAL_OPENREVIEW_SUBMISSION_V2.pdf` (SHA-256 `98d98cbd23fb90de6b6b431ffbf71678b9ed24c448a834cc4e54b32153529760`, 346798 bytes)

## Blocker repairs

### A — Double-blind anonymity
- Removed template residue `Affiliation` / `Address` / `email` from anonymous author block in `neurips_2026.sty`.
- Removed identity-bearing repository names (`vitaology`, `fractal-custody-objects`), internal paths (`eval/track_model_k_...`), host/checkout locators (`NOT_IN_CHECKOUT`), and machine tokens (`ZERO_PRIMARY_WEIGHT`, `BUILD_RECEIPT`).
- Regenerated F1 hierarchy figure with anonymous companion labels.

### B — Anticube
- Removed incorrect Anticube subsection (established/exploratory × positive/negative conflation).
- **ANTICUBE_GATE=PASS_REMOVED** (canonical SELF/NON-SELF × SAFE/NON-SAFE definition not retained in main paper).

### C — Supplement dependencies
- Removed references to bundled supplement figures/tables (F4–F5, F11–F12, A4, A7) and “bundled with this submission” language.
- Main PDF is self-contained for reviewer reading.
- **SUPPLEMENT_DEPENDENCY_GATE=PASS**

### D — Checklist truthfulness
- Compute resources: **Yes → No** (hardware reported; wall-time accounting incomplete).
- Licenses for existing assets: **Yes → No** (bibliography credits prior work; per-asset license enumeration insufficient).

## Small scientific clarifications (no statistic changes)
- Added sentence explaining 300 raw cells vs `n_paired=2` confirmatory aggregation unit.
- Replaced HydraLamp F6 “Chain OK (sample)” row (misleading partial counts) with aggregate chain verification in title; matrix shows per-condition cell counts and integrity dimensions only.

## Unchanged
- Title, MSM/MSModel framing, FCO/FCG hierarchy, HydraDG primary implementation, EXP-008/009 UNDERPOWERED verdicts, systems-vs-treatment separation, limitations, LLM disclosure, deterministic figures/tables F2 and Table values.
