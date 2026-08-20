# FCO/FCG Publication and Source Lineage

This document prevents **object-identity, version, licensing, and claim-boundary collisions** when HydraDG cites the Fractal Custody Object / Fractal Custody Graph work.

**FCO = Fractal Custody Object.**  
**FCG = Fractal Custody Graph.**

## 1. Citation rule

Do not cite a DOI, rendered-PDF digest, manuscript/content digest, package digest, `paper_cid`, FCG root, signature, or Merkle/MMR root as though those identifiers name the same byte object.

Each identifier must retain:

```text
object type
exact version
source/deposit
hash algorithm
full digest where available
what operation produced/attested it
claim ceiling
supersession state
```

A SHA-256 digest establishes identity/fixity of the declared bytes. It does not by itself establish authorship, truth, scientific validity, signature verification, Merkle/MMR commitment, or current license authority.

## 2. Version 1 public preprint

**Title:** *Fractal Custody Objects: route-comparable chain-of-custody for deterministic computational biology and AI-agent provenance*  
**Version:** v1  
**DOI:** `10.5281/zenodo.21210575`  
**Public record date:** 2026-07-05

The public Zenodo record is the external bibliographic authority for the DOI/version/file listing. Project publication manifests/handoffs preserve SHA-256 identities and historical custody state. Where historical handoff metadata conflicts with a later authoritative metadata correction, the historical value remains evidence of the prior state but does not remain current authority.

### v1 object identities

| Object | Identity / state | Evidence class | Use |
|---|---|---|---|
| Zenodo record | DOI `10.5281/zenodo.21210575` | external publication metadata | Bibliographic citation |
| `FMO-FCO-submission.fco.zip` | SHA-256 `916bf4c448368bcc4b11d817b87ca8aee7f76db4047359ebfdc674b6f0f6428a` | publication-handoff / manifest attestation | Signed publication bundle identity |
| `MANUSCRIPT_PUBLIC_v1.pdf` | SHA-256 `0da582aca55597c16f14f15fa31a648d842de54d0b6a980b91c43c738593f6c5` | canonical upload-manifest attestation | Human-readable v1 PDF identity |
| `MANUSCRIPT_PUBLIC_v1.pdf` on Zenodo | MD5 `ec9299f0eee62a83b370075a3a711034` | external Zenodo metadata | External file-listing cross-reference; **not** interchangeable with SHA-256 |
| stale pre-signing PDF build | SHA-256 prefix `06aa9427...` | superseded historical outbox | **Do not cite as the canonical uploaded v1 PDF** |
| `manuscript_sha256` field in signed-build handoff | SHA-256 `ced4878c1a1fd7f271b4c5075c1fe05c95095e1d1164fc27f39f312119492cba` | internal signed-build handoff field | Keep separate from the rendered PDF hash until the exact underlying object/serialization is explicitly mapped |
| `paper_cid` | `291f33644398a15f16437e69190110f6ebd0fbee8e0c777fd5399e85f23abdd3` | publication custody identity | Publication/canonical-content identity; not the PDF file SHA |
| signed FCG root | prefix `741d12de...` in public record/handoff | signed publication graph root | Graph/signature lineage; not a file hash |
| public-key SHA-256 fingerprint | `f496a067808026d45fbbad785bf83c6acd66429c2d257d246cc103c6d7ff460d` | signing-key fingerprint | Verify the publication-signing key identity, not manuscript bytes |

### Supersession notes

The canonical v1 publication handoff explicitly supersedes an older upload instruction that carried the pre-signing identities `d9608acd...`, `9308b43c...`, `ac6ed957...`, and `06aa9427...`. Those values are historical evidence and should remain preserved, but must not be promoted as the current signed-build/public-upload identities.

A second `0da582ac...` full digest previously appearing only in conversational summaries was **not located in the publication manifests audited for this document**. It is therefore `UNRESOLVED_SUMMARY_ONLY` and must not be cited as an exact object identity unless its source manifest or exact bytes are recovered.

The v1 handoff also contains a historical `CC BY 4.0` license field. That field is now classified as:

```text
SUPERSEDED_METADATA_ERROR
```

The authoritative corrected license for the FCO/FCG research publication is:

```text
CC BY-NC-ND 4.0
CURRENT_AUTHORITATIVE_METADATA
```

The historical handoff must remain preserved as evidence of the metadata error. It must **not** be interpreted as a valid version-specific licensing exception and must not be rewritten in place.

Because this is a metadata correction rather than a change to the historical publication/package bytes, the correction does **not** itself change or require recomputation of the PDF SHA-256, package SHA-256, `paper_cid`, signed FCG root, or public-key fingerprint listed above.

## 3. Version 3 public preprint

**Title:** *Fractal Custody Objects: route-comparable chain-of-custody for deterministic computational biology and AI-agent provenance*  
**Version:** v3  
**DOI:** `10.5281/zenodo.21420906`  
**Public record date:** 2026-07-17

The v3 public record describes FCOs as content-addressed research objects preserving exact identity, recursive provenance, and chain of custody, and describes v3 as adding custodian actions and canonical successors in an FCG.

This HydraDG audit has externally confirmed the DOI/version metadata, but has **not recomputed an exact SHA-256 over the v3 Zenodo download in this runtime**. Therefore use the DOI/version as the bibliographic identity unless a v3 package/sidecar manifest is separately admitted into the HydraDG custody graph.

## 4. Canonical semantic boundaries carried into HydraDG

HydraDG should preserve these distinctions from the FCO/FCG publications and current project specification:

1. **Custody is not correctness.** A valid lineage can preserve a wrong claim.
2. **Hash identity is not scientific verification.** A digest can bind/reidentify bytes; the stronger recompute-or-reject admission rule requires the named computation/evidence conditions.
3. **FCO identity is not producer identity.** Authorship/origin requires the applicable signature/witness layer.
4. **A project signature is not inherited from a cited preprint.** A publication may have its own signed FCG while HydraDG's project/turn signature remains pending unless a HydraDG signature receipt exists.
5. **Merkle/MMR roots are not ordinary file hashes.** Keep content digests, Merkle roots, MMR state, and signed graph roots typed separately.
6. **FCG is a governed custody/provenance graph.** Do not globally describe the complete HydraDG application graph as a DAG merely because a particular content-addressed evidence structure is acyclic; HydraDG also carries temporal inverse, contradiction, and supersession relations.
7. **Historical objects are preserved, not silently overwritten.** Corrections/successors should be explicit graph objects/relations.
8. **Probabilistic model output has a smaller claim ceiling than deterministic recomputation.** Preserve the exact realized model input/output/configuration; do not label a stochastic output mathematically inevitable.
9. **Metadata correction does not imply byte mutation.** Do not recompute historical content hashes merely because authoritative external metadata changed.

## 5. HydraDG-specific citation partition

Do not use the FCO preprint as a substitute citation for unrelated mathematical dependencies.

```text
FCO/FCG publications
  -> custody, provenance, recursive recompute-or-reject architecture

Ensslin & Weig (2010)
  -> information-theoretic Gibbs/free-energy inference analogy used in G* design rationale

Lin / Jensen-Shannon-divergence lineage
  -> Cloud Drift mathematics

LongMemEval source + HydraDG experiment receipts
  -> Hit@K / Recall@K and Track 03 empirical results
```

HydraDG's `G*` remains an **application-defined dimensionless diagnostic**, not physical Gibbs free energy and not a direct reproduction of Ensslin & Weig's functional.

## 6. Authoritative licensing correction

The authoritative licensing invariant for the FCO/FCG research publications and designated Byron P. Lee / Biobitworks research content is:

```text
CC BY-NC-ND 4.0
```

Any earlier FCO/FCG `CC BY 4.0` entry is retained only as a hash-preserved historical metadata object with state:

```text
SUPERSEDED_METADATA_ERROR
```

It is **not** a valid version-specific exception.

Correct custody treatment:

```text
original publication bytes / package
        |
        +--> original handoff metadata
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

Corrections are made through successor commits/metadata records, not history rewriting or force-pushing altered historical objects.

See [`LICENSING.md`](../LICENSING.md) for repository scope. Third-party material continues to retain its upstream rights.

## 7. Current HydraDG custody status of this mapping

This document is a **deterministic documentation correction/source-lineage map** based on project publication manifests/handoffs plus the authoritative licensing correction supplied for this project. Its presence in Git does not itself mean the mapping has been signed, Merkle/MMR committed, independently verified, or canonically appended to the local project FCG.

Claim ceiling:

```text
PUBLICATION_SOURCE_LINEAGE_IDENTIFIER_DISAMBIGUATION_AND_METADATA_SUPERSESSION_ONLY
```
