# HydraDG Licensing & Scope Declaration

HydraDG separates software licensing, designated Byron P. Lee / Biobitworks research-content licensing, and third-party rights. License metadata is part of custody lineage, but it is not interchangeable with file identity, signatures, FCG roots, or scientific verification.

| Category | Licensing Scope |
|---|---|
| **HydraDG software / website / scripts** | **Apache License, Version 2.0** ([`LICENSE`](LICENSE)) |
| **FCO/FCG research publications and designated Byron P. Lee / Biobitworks research content** | **CC BY-NC-ND 4.0** |
| **Earlier FCO/FCG `CC BY 4.0` references** | **SUPERSEDED_METADATA_ERROR — historical custody evidence only; not a valid version-specific exception** |
| **HydraDB** | **Upstream HydraDB license** |
| **LongMemEval / other datasets** | **Respective upstream dataset licenses** |
| **External papers / templates / APIs** | **Respective upstream rights** |

## 1. Software and reproducibility tooling — Apache-2.0

Participant-authored software in this repository—including the Next.js application, TypeScript/Python utilities, shell scripts, build configuration, GitHub Actions workflows, and software schemas—is licensed under the **Apache License, Version 2.0** unless a file or third-party notice states otherwise.

See [`LICENSE`](LICENSE).

## 2. FCO/FCG research content — CC BY-NC-ND 4.0

The authoritative license for the FCO/FCG research publications and designated Byron P. Lee / Biobitworks research content is **CC BY-NC-ND 4.0**.

An earlier FCO v1 publication handoff recorded `CC BY 4.0`. That field is now treated as a **superseded historical metadata error**, not as a valid version-specific licensing exception. The historical handoff remains preserved as custody evidence of the error; it is not silently rewritten.

Canonical correction lineage:

```text
original publication/package bytes
        |
        +--> historical handoff metadata
        |      license = CC BY 4.0
        |      state = SUPERSEDED_METADATA_ERROR
        |
        +--> corrected authoritative metadata
               license = CC BY-NC-ND 4.0
               state = CURRENT_AUTHORITATIVE_METADATA
                       |
                       v
              downstream repository metadata
```

The metadata correction does **not** change historical file bytes. Therefore an unchanged PDF SHA-256, package SHA-256, `paper_cid`, signed FCG root, public-key fingerprint, or other byte/root identity must not be recomputed merely because external license metadata was corrected.

See [`docs/FCO_FCG_SOURCE_LINEAGE.md`](docs/FCO_FCG_SOURCE_LINEAGE.md) for the identifier/version map and supersession treatment.

## 3. Software license does not absorb research or third-party content

The Apache-2.0 repository software license does not relicense:

- FCO/FCG research publications or designated Byron P. Lee / Biobitworks research content governed by CC BY-NC-ND 4.0;
- upstream HydraDB code or services;
- LongMemEval or other third-party datasets;
- external papers, figures, templates, APIs, or other third-party material.

Likewise, CC BY-NC-ND 4.0 on designated research content does not alter the Apache-2.0 grant on HydraDG software.

## 4. Upstream and third-party rights

- **HydraDB:** subject to the upstream HydraDB license and applicable terms.
- **LongMemEval and other datasets:** subject to their respective upstream dataset licenses.
- **External papers, APIs, templates, and figures:** retain their respective upstream rights.

For third-party details, see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## 5. Custody boundary

A license statement is rights metadata. It is not an FCO hash, signature, FCG root, DOI, Merkle/MMR commitment, or scientific-verification result.

Corrections to license metadata must be represented as successor/supersession records. Do not rewrite a historical hash-bound or signed object and then claim it always contained the corrected value.

Current invariant:

```text
FCO/FCG research publications
+ designated Byron P. Lee / Biobitworks research content
-> CC BY-NC-ND 4.0

historical FCO/FCG CC BY 4.0 metadata
-> SUPERSEDED_METADATA_ERROR
-> preserved for custody/history only

HydraDG software
-> Apache-2.0 where declared

third-party material
-> upstream rights
```
