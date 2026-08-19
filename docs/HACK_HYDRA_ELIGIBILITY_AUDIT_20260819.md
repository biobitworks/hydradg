# Hack Hydra eligibility audit — 2026-08-19

Status: ACTIVE RELEASE GATE

## Official rule basis

Official Hack Hydra site checked 2026-08-19:

- Build period: 2026-08-12 through 2026-08-20.
- The HydraDB OSS repo goes live and the official build period begins on August 12.
- Projects must start on or after 2026-08-12.
- The official site states: **"Nothing you write before then can go into your submission."**
- Public repository requirement: no participant-authored commits before 2026-08-12.
- Existing open-source libraries, frameworks, APIs, public datasets, AI coding assistants, templates and infrastructure are allowed when attributed.
- Pre-existing commits from upstream repositories/templates/dependencies do not count against a team; judges may inspect the team's contribution history.
- The submitted project must still be original work substantially built during the hackathon.
- Multiple-track submissions must be meaningfully distinct projects.
- Submission deadline: **2026-08-20 11:59 PM PT**.

Canonical rule URL:
https://hackhydra.hydradb.com/

HydraDB upstream source:
https://github.com/hydra-db/hydradb

## Repository-history observation

Repository: biobitworks/hydradg

Observed participant repository initialization commit:
- e45580269275018b2824227ec1836bb1a082b9bd
- message: Initial complete HydraDG private repository snapshot
- timestamp: 2026-08-18T07:58:55-07:00

A repository commit search performed 2026-08-19 found no HydraDG commits matching a pre-2026-08-12 window.

Claim ceiling: REPOSITORY_VISIBLE_HISTORY_CHECK_ONLY.

This does not by itself prove every byte in the initial snapshot was authored after 2026-08-12. Therefore source-content eligibility is gated separately below.

## Submission-safe source policy

The public Hack Hydra submission must contain only:

1. Participant-authored implementation code created on/after 2026-08-12.
2. Upstream/open-source libraries, frameworks, templates and dependencies, clearly attributed.
3. Public datasets, clearly attributed and license-bounded.
4. Post-2026-08-12 reimplementations of pre-existing ideas/methods, with prior work cited only as conceptual/reference lineage.

The submission must not contain participant-authored implementation code written before 2026-08-12 merely because it was copied or committed later.

## Conservative exclusions

The following are not automatically submission-eligible merely because they were copied into the repository after August 12:

- pre-hackathon FCO/FCG implementation code;
- pre-hackathon Vithia/Pythia implementation code;
- pre-hackathon XenoDisorder implementation code;
- pre-hackathon Fractal Waves / ECA implementation code;
- any other Byron/team source authored before 2026-08-12.

Those may be cited as prior publications, design lineage, or external evidence. A post-August-12 clean-room/reimplementation may be included if its hackathon authorship is established.

## Currently eligible implementation scope

Current release candidate scope is restricted to implementation developed during Hack Hydra:

- apps/hydradg-web/* Judge Lab / 4D FCG / knowledge / evidence / custody surfaces created during Aug 18-19 work;
- HydraDG_DaisyTrain_v0.3.7 Best Use / local HydraDB / LongMemEval scripts created or materially implemented during Aug 18-19 work;
- Track 01 dataset adapters and ontology implementation created during the hackathon;
- Track 02 HydraBlast implementation created during the hackathon;
- Track 03 HydraMemory implementation created during the hackathon;
- Hack-Hydra-specific CI, tests, receipts, documentation and release tooling created during the hackathon.

Any file whose participant-authored pre-Aug-12 origin cannot be ruled out is EXCLUDED_PENDING_AUDIT.

## Upstream/template boundary

HydraDB is an allowed upstream dependency. Its historical commits do not count against participant contribution history.

The user-supplied COMPUTE template archive is treated as an allowed template dependency/reference, not participant-originated Hack Hydra code. Archive identity directly recomputed in the 2026-08-19 working session:

- filename: compute-the-platform-to-build-and-ship-ai-agents.zip
- SHA-256: b363081debc07af517cea73ed53b682b840a9e4c52e6658e7d35f18ca9922e4c
- file count after direct extraction: **102**
- standalone LICENSE file in supplied archive: **NOT OBSERVED**

Any reused template source must be attributed in the final README/third-party notices, and upstream terms remain controlling. HydraDG-specific data logic, FCO/FCG navigation, graph behavior, tests and copy remain hackathon implementation work.

## Dataset boundary

External public datasets are allowed by the rules. Current dataset lanes:

Track 01:
- onyx-dot-app/EnterpriseRAG-Bench — upstream license MIT
- Salesforce/HERB — upstream license CC-BY-NC-4.0

Track 03:
- xiaowu0162/longmemeval-cleaned — upstream license MIT
- xiaowu0162/longmemeval-v2 — upstream license Apache-2.0
- Mohammadta/BEAM — upstream license CC-BY-SA-4.0
- Mohammadta/BEAM-10M — upstream license CC-BY-SA-4.0, optional full tier

Upstream availability/license metadata was independently re-observed through Hugging Face during the 2026-08-19 audit. Only LongMemEval-S currently has an admitted completed local pull/execution receipt. Availability metadata for the other datasets must not be promoted to a local-download claim.

Dataset download receipts establish retrieved byte identity only, not correctness or benchmark verification.

## CI execution boundary

At release head `253f12da2b7e72ef5ebd47c36019bb75cbe783b5`, four GitHub Actions workflows concluded `failure`, but their jobs exposed no executed steps, logs, or artifacts through the connected GitHub interface. A Judge Lab rerun produced the same no-step failure.

Current classification: `GITHUB_ACTIONS_RUNNER_START_FAILURE / CAUSE_NOT_ESTABLISHED`.

This must not be described as either application-test failure or CI pass. Local/Vercel build evidence may independently establish their own narrower gates, while GitHub Actions remains unresolved.

## Mandatory release gates

A public submission is not eligible for release until all are true:

- [ ] All participant-authored submission implementation is established as post-2026-08-12 work.
- [ ] Any ambiguous legacy participant source is removed from the submission tree or rewritten cleanly during the hackathon.
- [x] Upstream HydraDB is attributed with exact pinned revision.
- [x] COMPUTE template archive identity and attribution are recorded.
- [x] Dataset source IDs and declared upstream licenses are documented.
- [ ] Repository is public.
- [x] Open-source license is present for original HydraDG code.
- [ ] README final review confirms setup/run instructions and explains what HydraDB does.
- [ ] Public links are tested immediately before submission.
- [ ] Demo video is <=3 minutes and viewable without access request.
- [ ] Submission form is complete by 2026-08-20 11:59 PM PT.

## FCO/FCG claim boundary

This audit establishes an eligibility policy and records observed repository/source state. It is not a legal opinion, organizer attestation, signature, Merkle commitment, or proof that every historical source byte has been independently dated.

Current state:
ELIGIBILITY_RULE_VERIFIED / REPOSITORY_VISIBLE_HISTORY_POST_AUG12 / CONTENT_ORIGIN_AUDIT_IN_PROGRESS / TEMPLATE_IDENTITY_RECOMPUTED / NOT_SIGNED / NOT_MERKLE_COMMITTED
