# HydraDG Licensing & Scope Declaration

HydraDG separates software licensing from research-content licensing and preserves upstream/deposited rights **per exact object and version**.

| Category | Licensing Scope |
|---|---|
| **HydraDG software / website / scripts** | **Apache License, Version 2.0** ([`LICENSE`](LICENSE)) |
| **Repository-native Byron P. Lee / Biobitworks research content not already governed by a deposited-version license** | **CC BY-NC-ND 4.0 where explicitly designated** |
| **Previously deposited preprints / manuscripts** | **Version-specific license attached to that deposited object/record; do not retroactively narrow it** |
| **HydraDB** | **Upstream HydraDB license** |
| **LongMemEval / other datasets** | **Respective upstream dataset licenses** |
| **External papers / templates / APIs** | **Respective upstream rights** |

## 1. Software and reproducibility tooling — Apache-2.0

Participant-authored software in this repository—including the Next.js application, TypeScript/Python utilities, shell scripts, build configuration, GitHub Actions workflows, and software schemas—is licensed under the **Apache License, Version 2.0** unless a file or third-party notice states otherwise.

See [`LICENSE`](LICENSE).

## 2. Research content — preserve the license of the exact version

Repository-native Byron P. Lee / Biobitworks narrative research text, publication-style figures, and explicitly designated research-content artifacts may be released under **CC BY-NC-ND 4.0** where that license is attached to the relevant repository object.

That repository policy does **not** retroactively alter a license already granted on an earlier deposited/publication version.

For example, the canonical project handoff for **Fractal Custody Objects v1**, DOI `10.5281/zenodo.21210575`, records **CC BY 4.0** for the manuscript. That deposited v1 object should therefore be cited and reused under the rights attached to that version rather than under a later blanket repository label.

Because publication versions can have different file sets, hashes, signatures, and rights, always bind:

```text
publication/version
-> DOI / record
-> exact file or package identity
-> applicable deposited license
```

See [`docs/FCO_FCG_SOURCE_LINEAGE.md`](docs/FCO_FCG_SOURCE_LINEAGE.md) for the current FCO/FCG identifier/version map.

## 3. Software license does not absorb research or third-party content

The Apache-2.0 repository software license does not relicense:

- deposited preprint/manuscript content governed by its own version-specific rights;
- upstream HydraDB code or services;
- LongMemEval or other third-party datasets;
- external papers, figures, templates, APIs, or other third-party material.

Likewise, a Creative Commons research-content license does not alter the Apache-2.0 grant on HydraDG software.

## 4. Upstream and third-party rights

- **HydraDB:** subject to the upstream HydraDB license and applicable terms.
- **LongMemEval and other datasets:** subject to their respective upstream dataset licenses.
- **External papers, APIs, templates, and figures:** retain their respective upstream rights.

For third-party details, see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## 5. Custody boundary

A license statement is metadata governing permitted use; it is not interchangeable with an FCO hash, signature, FCG root, DOI, or scientific-verification state. Where a rights statement materially affects a released object, the exact license/version should be represented in that object's lineage rather than inferred from repository-wide prose.
