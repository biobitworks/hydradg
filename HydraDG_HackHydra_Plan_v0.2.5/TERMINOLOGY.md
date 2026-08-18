# Terminology matrix

| Term | Use in project | Boundary |
|---|---|---|
| Repeatability | Same bounded environment rerun | Do not imply cross-machine reproduction |
| Reproducibility | Re-execution under declared changed environment | Must state comparator/tolerance |
| Bitwise reproducibility | Canonical bytes/tensor bits identical | Strongest numeric identity claim |
| Numerical reproducibility | Results within declared numeric comparator | Not bit identity |
| First divergence | Earliest aligned object/operation that differs | Difference is not automatically causal mechanism |
| Downstream impact set / blast radius | Descendants whose relevant state changes | Evaluate against known injected perturbations where possible |
| Temporal supersession | New fact/version supersedes old without erasing it | Already established in HydraDB/SodaMem-like systems |
| Evidence provenance | Source/evidence dependency lineage | Provenance is not correctness |
| Claim ceiling | Strongest supported interpretation of a claim | Distinct from access control/trust score |
| Recovery equivalence | BYTE_EXACT / STATE_EXACT / FUNCTIONALLY_EQUIVALENT / BASIN_EQUIVALENT / PARTIAL / NONE | Never use unqualified "restored" |
| FCO | Material custody object | Hash only when actually computed |
| FCG | Typed dependency graph of FCOs | Graph lineage does not prove truth |
| SeedGraph | Context-bearing evidence/claim graph | Public and PHI-private twins share schema, not data |
| CFMO | Continuous/dynamic state trajectory with discrete custody checkpoints | Not literally a continuously recomputed Merkle root |
| HydraDG | Project working name for HydraDB-native divergence/evidence layer | Do not imply official HydraDB branding |
