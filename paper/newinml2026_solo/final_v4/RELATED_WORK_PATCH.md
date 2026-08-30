# Related Work Patch — Successor PDF

**Target file:** `paper/newinml2026_solo/final_v4/manuscript/main.tex`  
**Section:** `\section{Related Work}` — provenance subsection  
**Framework callsite:** FCG hash-linked roots sentence

## Replacement paragraph (as committed)

```latex
\textbf{Provenance, integrity, and reproducibility.}
W3C PROV-O and workflow provenance systems represent process and research-object lineage \cite{lebo2013provo,khan2019cwlprov}, while append-only Merkle audit logs provide established tamper-evident integrity mechanisms \cite{laurie2013ct}; HydraDG does not claim to invent these primitives.
Recent work surveys evidence tracing and execution provenance for LLM agents \cite{wang2026agentprovenance}, and separate work argues for preserving negative ML results rather than selective omission \cite{karl2024negative}.
Preregistration, FAIR principles, and nanopublication-style lineage further support reproducibility \cite{nosek2018prereg,wilkinson2016fair,groth2010nano}.
HydraDG integrates rather than replaces these foundations: probabilistic outputs, deterministic transforms, malformed cells, failures, abstentions, blocked states, and underpowered terminations remain typed evidence with explicit claim-promotion ceilings enforced via FCO/FCG handoff receipts.
Companion custody-framework preprints (deferred to camera-ready de-anonymization) define FCO/FCG formally; they establish framework provenance, not the HydraDG empirical results reported here.
```

## Framework addition

```latex
An \textbf{FCG} (\emph{Fractal Custody Graph}) append records directed edges between FCOs with hash-linked roots \cite{laurie2013ct}.
```

## New bibliography entries

| Key | Verified identifier |
|-----|---------------------|
| `laurie2013ct` | RFC 6962, IETF, June 2013 |
| `lebo2013provo` | W3C PROV-O Recommendation, 2013 |
| `khan2019cwlprov` | GigaScience 8(11):giz095, doi:10.1093/gigascience/giz095 |
| `karl2024negative` | ICML 2024, PMLR 235:23256–23265, arXiv:2406.03980 |
| `wang2026agentprovenance` | arXiv:2606.04990, 2026 |

## Rationale

- Credits Merkle/audit-tree prior art where HydraDG uses hash-linked integrity language.
- Grounds provenance discussion with PROV-O + workflow provenance without claiming generic provenance as novel.
- Adds negative-results and agent-provenance comparators aligned with custody-first motivation.
- Preserves compact workshop scope (~one paragraph); selective-prediction citations deferred to appendix/matrix.

## Page impact (successor build)

- Main content pages: **4** (unchanged)
- Reference pages: **3** (was 1 on predecessor)
- Checklist pages: **7**
- Total pages: **14** (was 12)
