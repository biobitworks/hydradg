# HydraDG NewInML SOLO — Determinism, Hash, Table, and Figure Completeness Audit

## Scope

This audit compares the current SOLO successor-recovery generator and manuscript against the project's stated reproducibility contract and previously requested scientific visual inventory. It does not rerun Studio-bound model experiments. It distinguishes:

- frozen probabilistic experiment evidence;
- deterministic recomputation;
- generated publication artifacts;
- conceptual diagrams;
- requested but not yet admissible figures.

## Executive verdict

`FINAL_DETERMINISTIC_ARTIFACT_GATE=FAIL_PENDING_REPAIR`

The current package has a valid deterministic R1/R2/R3 gate for the statistical CSV payload, but it does **not** yet establish equivalent determinism or source derivation for every figure and table. Presence/count gates are not sufficient.

### What currently passes

1. The statistical recovery script reads frozen EXP-008/009 verdict receipts and Stage-2 summaries, writes deterministic scientific CSV outputs, and records identical R1/R2/R3 combined roots.
2. The recorded statistical root is identical across R1/R2/R3: `3e521a58917da1342746124b281580f5c24a982a546386624e731982618aa9a1`.
3. The ChatGPT V2 review package's own `SHA256SUMS.txt` verifies against its local files and the V2 ZIP hash recomputes.
4. Seven logical figure IDs and ten table artifacts exist in the predecessor recovery tree.

### What does not yet pass

#### Figures

- **FIG-001** is a deterministic conceptual schematic, but it has no scientific source files and is not the previously specified byte-to-claim reverse-trace figure.
- **FIG-002** hard-codes parse rates `0.907` and `0.883` and hard-codes approximate error bars `0.03`; it does not derive the plotted values/uncertainty from the declared source verdicts at render time.
- **FIG-003** hard-codes terminal-state counts `[2,4,3,3,2,2]` rather than counting the stated `EXPERIMENT_MASTER_LEDGER.tsv` source.
- **FIG-004** hard-codes `[100,8]` and declares only the core-stress receipt as a source even though the 8/8 tamper result belongs to a separate tamper artifact.
- **FIG-005** reads the Anticube trajectory source, but is only a 2-D pair of lines against z/time. It does not implement the previously requested X=SELF↔NON-SELF, Y=NON-SAFE↔SAFE, Z=time/state trajectory with ΔG* kept separate.
- **FIG-006** hard-codes `[18555,12,18567]` instead of reading them from its declared source JSON.
- **FIG-007** does not actually visualize all three roots. It constructs an unused `roots` list from R1 three times and renders three unit bars based only on the aggregate PASS flag.
- Figure receipts hash the PNG derivative only. The PDF derivative is not recorded in `FIGURE_RECEIPTS.json`.
- PDF byte determinism is not established: the renderer does not explicitly normalize PDF metadata/timestamps and there is no R1/R2/R3 PDF hash comparison.
- The current verifier only counts PNG figures; it does not regenerate and compare figure bytes or validate source-hash coverage.

#### Tables

- **T2** is copied from the deterministic statistical output and is the strongest table path.
- **T3** is programmatically filtered from the experiment ledger, but inherits any ledger provenance defects.
- **T4** contains hard-coded HydraLamp outcome rows rather than computing them from exact source receipts.
- **T7** states `figures = deterministic` despite no R1/R2/R3 figure-byte gate.
- **T9** hard-codes claim ceilings instead of deriving them from the authoritative claim/evidence ledger.
- There is no table receipt manifest binding each table to source hashes, generator hash, output hash, and R1/R2/R3 roots.

#### Experiment ledger provenance

The predecessor `EXPERIMENT_MASTER_LEDGER.tsv` is generated from a static `EXPERIMENT_SPECS` list. Historical rows are stamped with the build-time `git_head()` and directory hashing may select the first JSON rather than the experiment's authoritative terminal receipt. Therefore the ledger cannot yet serve as a universal source of truth for empirical figure counts.

#### Environment and byte-level determinism

The predecessor reproduction requirements list package names without pinned versions. This is insufficient for byte-identical publication derivatives across hosts. A deterministic publication build needs a frozen environment/lock plus normalized output metadata.

## Statistical-code caution

The statistical R1/R2/R3 byte-equivalence gate is real for the six combined CSV outputs, but inferential interpretation remains separately reviewable. In particular, the current `power_analysis()` uses an explicit rule-of-thumb about discordant pairs rather than a formal powered-design calculation. It must be described as a heuristic diagnostic, not a powered proof.

## Current manuscript/appendix visual completeness

The predecessor main manuscript includes only the EXP-008/009 parse-validity figure. The LaTeX appendix contains a simple boxed custody-text diagram but does not include the requested complete figure suite.

Therefore:

`REQUESTED_FIGURE_COVERAGE=INCOMPLETE`

## Mandatory repair standard

A quantitative figure/table becomes `ADMITTED_DETERMINISTIC` only if all apply:

1. exact admitted source bytes are identified;
2. source SHA-256 recomputes;
3. every numeric/textual scientific value is loaded/derived from those source bytes, not repeated as a renderer literal;
4. generator source SHA-256 is recorded;
5. exact environment/lock identity is recorded;
6. R1/R2/R3 clean builds execute in isolated output directories;
7. canonical scientific spec/text/layout roots match;
8. SVG hash matches R1=R2=R3 where SVG is used;
9. PNG hash matches R1=R2=R3 or is explicitly classified as a noncanonical derivative;
10. PDF is normalized and hash-identical R1=R2=R3, or PDF is explicitly noncanonical and a deterministic canonical source (e.g. SVG) is designated;
11. output receipt records SHA-256 for **every distributed derivative**;
12. table receipts bind table bytes to sources and generator;
13. reverse trace from visible scientific value/text to source succeeds;
14. blind/anonymization scan passes;
15. Protein Hinge/team primary admission remains zero.

## Required status changes before final review

- downgrade predecessor `figures deterministic` to `NOT_ESTABLISHED` until repaired;
- retain `STATISTICS_R123=PASS` separately;
- do not call count-only `R5/R6` gates correctness gates;
- repair stale licensing statements before upload;
- do not state that OpenReview itself universally requires CC BY 4.0 unless the live venue's submission configuration actually requires that article license;
- preserve `SIGNATURE_STATE=NOT_SIGNED` unless actual authorized signing occurs;
- preserve `MERKLE_MMR_STATE=NOT_COMMITTED` unless an actual ordered commitment and verification receipt exist.
