# Hack Hydra 2026 Eligibility — Custody Evidence

Generated for the judge-facing `/eligibility` surface on 2026-08-20.

## Claim ceiling

`AUDIT_EVIDENCE_SUPPORTS_ATTESTATION_NOT_INDEPENDENT_PROOF`

HydraDG uses Git history, SHA-256 identities, FCO/FCG lineage, experiment receipts, CI/runtime receipts, and deployment metadata to make the submission chronology inspectable. This evidence supports the submitter's Hack Hydra confirmations; it does not independently prove first authorship, wall-clock truth, every team member's external submissions, or agreement to the rules/code of conduct.

## What is pre-existing versus Hack-Hydra-specific

Pre-existing inputs are preserved as dependencies rather than relabeled as hackathon-authored work:

- FCO/FCG research concepts and designated research publications;
- SeedGraph/source-custody concepts and prior reusable tooling where referenced;
- HydraDB upstream software/API;
- LongMemEval and other third-party datasets;
- external papers and third-party dependencies under their upstream rights.

Hack-Hydra-specific participant-authored implementation in this repository includes the HydraDG application, HydraDB graph adapter/query surfaces, Track 03 LongMemEval graph/evaluation lane, Reference -> Poison -> Antidote judge flow, Context Iceberg presentation, eligibility/release surfaces, hosted HydraDB/Vercel wiring, and hackathon release hardening.

The separation is deliberate: custody establishes lineage instead of pretending reused research/dependencies were created during the event.

## Confirmation map

| Form confirmation | Custody assessment | Evidence path | Human boundary |
|---|---|---|---|
| Originality — participant-authored development began on/after Aug 12, 2026 | `CUSTODY_SUPPORTED` | Hack-Hydra-specific branches/commits + dated FCO/FCG/release artifacts -> implementation receipts -> tested/deployed artifacts. Final-release PR #20 was created 2026-08-20T03:11Z and merged 2026-08-20T03:17Z; the current curated deployment lineage is also dated within the event window. Pre-existing FCO/FCG research and third-party inputs are explicitly treated as dependencies. | Custody supports the submitter's chronology; absence of an earlier hidden/private copy cannot be independently proven by Git history alone. |
| Submission eligibility — built for Hack Hydra, not substantially pre-built | `CUSTODY_SUPPORTED` | Hack-Hydra-specific requirement -> branch -> implementation -> experiment -> release chain; pre-existing dependency boundary above. | Final eligibility remains a submitter/rules attestation. |
| Meaningful HydraDB use | `EXECUTION_VERIFIED` | HydraDB HTTP graph adapter; pinned HydraDB revision/container evidence; direct write/read round trip; current/history/provenance query proof; LongMemEval graph construction/evaluation; hosted GitHub -> HydraDB `hydradg` -> Vercel server adapter path. | Successful HydraDB execution does not imply benchmark superiority. |
| Link accessibility | `CORE_LINKS_VERIFIED_DEPLOYED_LINK_PENDING` | GitHub repository metadata reports `visibility=public`; demo video is recorded in the submission manifest as user-attested complete; curated Vercel deployment builds successfully but must be public/unauthenticated before it is submitted as a judge URL. | If the Vercel URL remains protected, do not submit it as an accessible project link. |
| One submission per team member | `HUMAN_ATTESTATION_REQUIRED` | Final team roster/submission receipt can be hashed and linked into the FCG. | HydraDG cannot observe every external Hack Hydra submission by every person. |
| Final accuracy/rules/code-of-conduct confirmation | `HUMAN_ATTESTATION_REQUIRED` | Submission manifest -> claim/evidence table -> tested commit/deployment -> final attestation receipt. | Agreement to rules/code of conduct and final truthfulness are human responsibilities. |

## Concrete evidence anchors

- Public repository: `https://github.com/biobitworks/hydradg`
- Default judge authority: `main`
- Final release-hardening PR #20: `https://github.com/biobitworks/hydradg/pull/20`
- PR #20 created: `2026-08-20T03:11:00Z`
- PR #20 merged: `2026-08-20T03:17:52Z`
- Curated judge branch: `hack-hydra/curated-vercel-lineage-20260820`
- Curated Vercel build commit: `b0a6175cee12e6ff3676df7f271e686e2a2a8ce9`
- Vercel build/check state for that commit: `success`
- Demo video recorded in submission manifest: `https://youtu.be/7EDb6q-loPA`
- Track 03 claim ceiling: `LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA`

## Custody-graph interpretation

The intended graph path for each confirmation is:

```text
Hack Hydra requirement
  -> human confirmation / requirement object
  -> participant-authored work item
  -> Git commit / implementation artifact
  -> experiment or runtime receipt
  -> FCO identity
  -> FCG provenance/dependency edges
  -> HydraDB projection/readback where applicable
  -> judge-facing eligibility artifact
  -> final submission attestation
```

Pre-existing components attach through dependency/source edges, not `AUTHORED_DURING_HACKATHON` semantics.

## Cryptographic boundaries

- SHA-256/hash identity: supports byte/object identity and custody linkage.
- Git/Vercel timestamps: provide recorded service chronology, not an infallible independent clock oracle.
- FCO/FCG provenance: supports lineage, not scientific correctness.
- Signature: do not claim project authenticity unless an authorized private-key signing receipt exists.
- Merkle/MMR: do not claim commitment unless actually performed.
