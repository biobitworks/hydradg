# Deterministic Publication Artifact Gate — Required Successor Contract

## Canonical source-first architecture

For each quantitative figure/table:

`source bytes -> source SHA-256 -> deterministic extraction -> canonical data/spec -> render/table transform -> artifact bytes -> artifact SHA-256 -> manuscript inclusion`

The renderer is not an evidence source.

## Required file set per figure

- `FIGURE_TEXT.json` — visible scientific text/numbers only
- `FIGURE_DATA.json` or canonical TSV/CSV — exact derived values
- `FIGURE_LAYOUT.json` — geometry/style only
- `FIGURE_EVIDENCE_MAP.jsonl` — each visible element/value -> source/derivation
- `FIGURE_BUILD_ENV.json` — exact versions/platform/fonts/backend
- `FIGURE_BUILD_RECEIPT.json` — source/generator/spec/output hashes
- `FIGURE_ROUNDTRIP_RECEIPT.json` — forward/reverse trace status
- canonical `figure.svg` where possible
- distributed `figure.png` and `figure.pdf` derivatives

The render code must not contain scientific literals except stable schema/IDs and visual constants.

## Required file set per table

- canonical table source/derivation spec
- exact source file list and SHA-256s
- generator SHA-256
- canonical CSV/TSV output SHA-256
- LaTeX/Markdown derivative SHA-256 where distributed
- R1/R2/R3 combined table root
- row/value reverse-trace map for material quantitative rows

## R1/R2/R3 protocol

1. start from the same Git SHA and frozen source hash set;
2. create three clean temporary output roots;
3. run generators independently;
4. compare canonical scientific spec roots;
5. compare canonical SVG/CSV/TSV bytes;
6. compare PNG/PDF after metadata normalization;
7. on divergence, identify earliest dependency (source bytes, environment, generator, layout, metadata, font, compression, PDF backend);
8. do not choose one output and discard disagreement.

## Required verifier behavior

`verify` must fail on any of:

- missing source;
- source SHA mismatch;
- missing generator SHA;
- empirical renderer literal;
- generated value != source-derived value;
- R1/R2/R3 mismatch;
- missing PNG/PDF/SVG/table hash for distributed artifact;
- receipt source coverage incomplete;
- stale/historical Git SHA represented as current experiment SHA;
- figure/table caption exceeds claim ceiling;
- anonymization leak;
- Protein Hinge primary evidence admission > 0.

A file count is only an inventory gate, never a scientific correctness gate.
