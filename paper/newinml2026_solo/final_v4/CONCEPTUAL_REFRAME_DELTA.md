# NewInML SOLO — Conceptual Reframe Textual Delta

**Scope:** Conceptual hierarchy reframe only. EXP-008/009 numeric results unchanged. Upload candidate **not** promoted.

**Successor PDF:** `paper/newinml2026_solo/final_v4/manuscript/build/successor_conceptual_reframe/main.pdf`

**Successor PDF SHA256:** `ec49367983fd5c2d6dd315c49939dd348dc8d5573d38c21dde06943c0670bb88` (15 pages)

**Frozen predecessors preserved:** `manuscript/build/main.pdf`, `manuscript/build/successor_citation/main.pdf`, `comprehensive_v2/FINAL_COMPREHENSIVE_SUCCESSOR_V2.pdf`

## Intellectual hierarchy (new)

```text
Mechanical Scientific Method
→ FCO / FCG custody substrate
→ proposed Mechanical Scientific Model class
→ HydraDG (primary experimentally evaluated implementation)
→ Vithia (companion exemplar; ZERO_PRIMARY_WEIGHT for EXP-008/009)
→ SeedGraph / Ollarma / HydraLamp (execution & systems validation)
→ EXP-008 / EXP-009 (UNDERPOWERED; EFFECT_NOT_ESTABLISHED)
```

## Exact `main.tex` delta

### Title

| Before | After |
| --- | --- |
| `HydraDG: Governed Context Interventions with Fractal Custody for Agent Experiments` | `Toward Mechanical Scientific Models: Fractal Custody and Governed Agent Experiments` |

### Abstract (replaced in full)

**Removed opening:** agent evaluations / “We present HydraDG…” framework-first framing.

**Added opening:** Mechanical Scientific Method → proposed Mechanical Scientific Model class with eight required properties → FCO/FCG custody substrate → HydraDG as primary evaluated implementation → EXP-008/009 underpowered → explicit disclaimer that MSM is **not** established external terminology.

### Introduction

**Added** five-layer itemized separation: Method (MSM), Model class (proposed MSM), Custody (FCO/FCG), Primary implementation (HydraDG), Systems validation + Vithia companion (zero primary weight for EXP-008/009).

**Changed** “This paper describes the HydraDG framework…” → “reports terminal results … executed in HydraDG” with explicit *underpowered / effect not established* and Vithia non-promotion sentence.

### Framework — new subsection `Mechanical Scientific Models`

**Added:**

- Proposal language: “We propose the term Mechanical Scientific Model…”
- Formal transition: \(S_t \xrightarrow[\;E_t\;]{T_t} S_{t+1}\)
- Enumerated transition bindings (source → transform → derived evidence → bounded claim → successor delta)
- Required-property list (failure-complete outcomes, claim ceilings, traceability, no silent rewrite)
- Figure~\ref{fig:msm-hierarchy} + `figures/F1_msm_hierarchy.png`

**Custody objects subsection:** HydraDG reframed as one implementation atop FCO/FCG substrate (not methodology identity).

### Discussion

**Replaced** HydraDG-as-contribution framing with:

- Principal contribution is **not** structured-retrieval efficacy (effect not established)
- Broader proposition: mechanically exposable evidence-state transitions
- HydraLamp = systems validation only; Vithia = companion exemplar, not primary evidence

### Conclusion

**Replaced** “We presented HydraDG…” with MSM proposal + HydraDG as one implementation + underpowered EXP-008/009 + recommendation without claiming retrieval efficacy.

## Sections intentionally unchanged

- Related Work (citations / prior-art boundaries)
- Experimental Setup (conditions, models, power gates)
- Results table and EXP-008/009 terminal wording (UNDERPOWERED counts unchanged)
- Systems-validation table
- Limitations / Future directions
- Bibliography / appendix / checklist

## Figure 1

**New asset:** `manuscript/figures/F1_msm_hierarchy.png`

**Labels on figure:** Vithia `COMPANION_IMPLEMENTATION | ZERO_PRIMARY_WEIGHT_EXP008_009`; EXP-008/009 `UNDERPOWERED | EFFECT_NOT_ESTABLISHED`.

**v2 rebuild script:** `scripts/newinml_comprehensive_v2_visual_rebuild.py` F1 renderer aligned to same hierarchy (not rerun for upload candidate in this pass).

## Preserved claim gates

```text
EXP008=UNDERPOWERED
EXP009=UNDERPOWERED
CLAIM_CEILING=CUSTODY_MECHANICS
PROTEIN_HINGE_PRIMARY_EVIDENCE_COUNT=0
SIGNATURE_STATE=NOT_SIGNED
MERKLE_MMR_STATE=NOT_COMMITTED
FINAL_COMPREHENSIVE_UPLOAD_CANDIDATE=NO  (unchanged)
HUMAN_VISUAL_REVIEW=REQUIRED
```

## Full unified diff

See `git diff paper/newinml2026_solo/final_v4/manuscript/main.tex` on branch `cursor/comprehensive-v2-visual-rebuild-fb0f`.
