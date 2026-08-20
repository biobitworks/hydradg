# HydraDG Licensing

HydraDG uses different licenses for different classes of material. This file defines the intended scope so the repository is not misread as a single-license work.

## 1. Software and reproducibility tooling — Apache License 2.0

Unless a file states otherwise, participant-authored software and machine-executable reproducibility tooling in this repository are licensed under the **Apache License, Version 2.0** (`Apache-2.0`).

This includes participant-authored:

- Python source code;
- TypeScript / JavaScript / React / Next.js source code;
- shell scripts;
- GitHub Actions workflows;
- configuration and build files;
- schemas used as software interfaces;
- HydraDB projection/import/readback utilities;
- test and verification code.

The full Apache-2.0 text is in [`LICENSE`](LICENSE).

## 2. Preprints, manuscripts, and authored research-content artifacts — CC BY-NC-ND 4.0

Unless an individual artifact states otherwise, Byron P. Lee / Biobitworks authored **preprint, manuscript, narrative research text, publication-style figure, and explicitly designated research-content artifacts** are licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License** (`CC BY-NC-ND 4.0`).

Under that license, the material may be shared with attribution for noncommercial purposes; adapted material may not be distributed under the license.

Canonical license page:

`https://creativecommons.org/licenses/by-nc-nd/4.0/`

This content license does **not** replace the Apache-2.0 license on software code and reproducibility tooling.

## 3. Canonical custody / evidence artifacts

FCO/FCG custody receipts, source hashes, evidence ledgers, graph snapshots, and other evidence objects preserve their own provenance and upstream rights. Where an artifact contains participant-authored research content, the CC BY-NC-ND 4.0 designation may apply; where it is executable software or software-interface material, Apache-2.0 applies unless otherwise marked.

A hash, FCO identifier, FCG edge, or custody receipt does not relicense the underlying source material.

## 4. Third-party materials

Third-party code, datasets, templates, papers, APIs, models, services, and other external materials retain their original licenses and terms. They are not relicensed under Apache-2.0 or CC BY-NC-ND 4.0 merely because HydraDG cites, hashes, references, or interoperates with them.

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## 5. Practical rule

If you are reproducing the HydraDG application:

- use the participant-authored code under **Apache-2.0**;
- preserve the license/attribution of any third-party dependency;
- treat explicitly identified preprints/manuscripts/research-content artifacts under **CC BY-NC-ND 4.0**;
- do not infer rights to an upstream dataset or paper from the HydraDG repository license.

This file is a project licensing statement, not legal advice.
