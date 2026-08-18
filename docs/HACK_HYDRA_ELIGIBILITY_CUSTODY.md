# Hack Hydra 2026 eligibility custody

Status: EVIDENCE_BUILDING
Claim ceiling: `AUDIT_EVIDENCE_SUPPORTS_ATTESTATION_NOT_INDEPENDENT_PROOF`

HydraDG uses the same FCO/FCG custody pattern for submission eligibility evidence that it uses for research/context provenance. The goal is to make the submission chronology and dependency boundaries inspectable without overstating what cryptographic custody can establish.

## What custody can support

For Hack Hydra-specific development, retain and link:
- Git branch, commit, issue, and pull-request chronology;
- FCO/FCG identities for requirements, source inputs, transformations, experiments, claims, and artifacts;
- script/notebook/lab-note execution receipts;
- model, agent, and tool invocation metadata;
- host/software/runtime manifests and hashes where available;
- final team roster, submission manifest, tested commit SHA, and artifact hashes;
- explicit inventory of pre-existing components reused as dependencies.

This supports an auditable account of what was newly created for HydraDG during the hackathon versus what existed previously and was reused.

## What custody does not prove by itself

- It does not independently prove first authorship or that a wall-clock timestamp could never have been manipulated.
- It does not determine whether reuse of a pre-existing component is permitted under hackathon rules; it exposes the boundary so judges can evaluate it.
- It cannot independently observe whether every team member appears on another Hack Hydra submission.
- It cannot replace the human/team attestation agreeing to the rules and code of conduct.

## Required confirmations and evidence state

### Originality confirmation
Form statement: participant-authored development on this project began on or after August 12, 2026.

Evidence target:
- first Hack-Hydra-specific HydraDG branch/commit chronology;
- Hack-Hydra-specific issue and execution-plan lineage;
- FCO/FCG receipts generated during implementation;
- explicit pre-existing dependency inventory.

State: `EVIDENCE_BUILDING`.

### Submission eligibility
Form statement: project was built for Hack Hydra and is not a substantially pre-built or previously completed project.

Evidence target:
- requirement -> implementation -> experiment -> demo dependency chain;
- new-vs-reused component manifest;
- final diff/commit range used for submission.

State: `EVIDENCE_BUILDING`.

### HydraDB requirement
Form statement: submission makes meaningful use of the HydraDB open-source repository.

Evidence target:
- pinned HydraDB source revision;
- executed HydraDB graph write/read/current/history/provenance tests;
- retained backend receipts and query outputs;
- demo path showing HydraDB on the load-bearing memory path.

State: `ACTIVE_TESTING` until executed backend tests are retained.

### Link accessibility
Form statement: repository, demo video, and submitted links are judge-accessible.

Evidence target:
- public GitHub accessibility check from logged-out session;
- YouTube unlisted/public accessibility check;
- deployed-app off-session check if a live app is submitted.

State: `BLOCKED_PENDING_PUBLICATION` until those links exist and are tested.

### One submission rule
Form statement: every listed team member is part of only one Hack Hydra submission.

Evidence target:
- final hashed team roster and submission-candidate receipt.

State: `HUMAN_ATTESTATION_REQUIRED`. HydraDG cannot independently inspect every submission by each person.

### Final confirmation
Form statement: submission information is accurate and the team agrees to the Hack Hydra rules and code of conduct.

Evidence target:
- final submission manifest;
- claim -> experiment -> artifact -> hash table;
- exact tested commit SHA;
- team attestation receipt.

State: `HUMAN_ATTESTATION_REQUIRED`.

## Release rule

The MVP may display eligibility evidence and custody receipts, but must not label the submission `ELIGIBILITY_VERIFIED` or `ORIGINALITY_PROVEN`. Suitable states are bounded labels such as `EVIDENCE_BUILDING`, `BACKEND_VERIFIED`, `LINKS_VERIFIED`, and `TEAM_ATTESTED` only after the corresponding operation actually occurs.
