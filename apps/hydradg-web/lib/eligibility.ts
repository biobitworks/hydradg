export type EligibilityState =
  | "CUSTODY_SUPPORTED"
  | "EXECUTION_VERIFIED"
  | "CORE_LINKS_VERIFIED_DEPLOYED_LINK_PENDING"
  | "HUMAN_ATTESTATION_REQUIRED";

export type EligibilityItem = {
  key: string;
  label: string;
  formConfirmation: string;
  state: EligibilityState;
  evidence: string[];
  graphPath: string[];
  limitation: string;
};

export const eligibilityClaimCeiling =
  "AUDIT_EVIDENCE_SUPPORTS_ATTESTATION_NOT_INDEPENDENT_PROOF";

export const eligibilityProofDoc =
  "https://github.com/biobitworks/hydradg/blob/hack-hydra/curated-vercel-lineage-20260820/docs/HACK_HYDRA_ELIGIBILITY_CUSTODY_20260820.md";

export const hackHydraEligibility: EligibilityItem[] = [
  {
    key: "originality",
    label: "Originality confirmation",
    formConfirmation:
      "I confirm that participant-authored development on this project began on or after August 12, 2026.",
    state: "CUSTODY_SUPPORTED",
    evidence: [
      "Hack-Hydra-specific branch/commit chronology and dated release artifacts",
      "FCO/FCG object, transformation, experiment, and release receipts created during the event window",
      "Final release-hardening PR #20 created 2026-08-20T03:11Z and merged 2026-08-20T03:17Z",
      "Curated Vercel deployment lineage built from an event-window commit",
      "Pre-existing FCO/FCG research, SeedGraph concepts, HydraDB upstream, datasets, and papers are retained as dependencies rather than relabeled as hackathon-authored work",
    ],
    graphPath: [
      "Hack Hydra requirement",
      "participant-authored work item",
      "Git commit / implementation artifact",
      "FCO identity",
      "FCG provenance edge",
      "release/deployment artifact",
    ],
    limitation:
      "The custody graph supports the submitter's development chronology and distinguishes reused dependencies from event-specific implementation. Git/FCO history cannot independently prove that no undisclosed earlier private copy existed.",
  },
  {
    key: "submission_eligibility",
    label: "Built for Hack Hydra",
    formConfirmation:
      "I confirm that this project was built for Hack Hydra and is not a substantially pre-built or previously completed project.",
    state: "CUSTODY_SUPPORTED",
    evidence: [
      "Hack-Hydra-specific architecture, Track 03 experiment lane, judge UI, and release work are bound to event-window branches/commits",
      "Requirement -> implementation -> experiment -> result -> release lineage is preserved",
      "Pre-existing research concepts and third-party software/datasets remain explicit source/dependency nodes",
      "Scientific null/negative evidence is retained instead of being rewritten as a pre-existing success claim",
    ],
    graphPath: [
      "Hack Hydra requirement",
      "new HydraDG implementation",
      "experiment receipt",
      "ResultFCO",
      "FCG release edge",
      "judge artifact",
    ],
    limitation:
      "Custody supports the team's eligibility attestation by exposing what was newly built versus reused. The hackathon's final eligibility judgment and the attestation itself remain human/rules-governed.",
  },
  {
    key: "hydradb_requirement",
    label: "Meaningful HydraDB use",
    formConfirmation:
      "I confirm that this submission makes meaningful use of the HydraDB open-source repository.",
    state: "EXECUTION_VERIFIED",
    evidence: [
      "pinned hydra-db/hydradb source revision 6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219",
      "HydraDB HTTP graph adapter and HydraDB-only executable judge path",
      "HydraDB container digest sha256:db78309a233be54662db29744047e985a39b51c45a270d1a1f47c31a62cdb709",
      "GitHub Actions run 32187451568 / run #28",
      "direct HydraDB write/read round trip and current/history/provenance query proof",
      "LongMemEval-S full500 graph/evaluation lane: 23,867 sessions, 4,776 entities, 3,506 facts",
      "Hosted path: GitHub connector -> HydraDB database hydradg -> Vercel server-only HydraDB v2 adapter",
    ],
    graphPath: [
      "source / dataset",
      "FCO/FCG projection",
      "HydraDB write",
      "HydraDB readback",
      "query/result receipt",
      "judge UI",
    ],
    limitation:
      "Verified HydraDB execution establishes meaningful backend use and traceability, not LongMemEval superiority, end-to-end QA improvement, or verification of every deployment environment.",
  },
  {
    key: "link_accessibility",
    label: "Judge-accessible links",
    formConfirmation:
      "I confirm that the GitHub repository, demo video, and any submitted project links are accessible to the judging team.",
    state: "CORE_LINKS_VERIFIED_DEPLOYED_LINK_PENDING",
    evidence: [
      "GitHub repository metadata currently reports biobitworks/hydradg visibility=public",
      "Demo video URL is recorded in the submission manifest as user-attested complete: https://youtu.be/7EDb6q-loPA",
      "Curated Vercel branch build is READY and contains the judge route set",
      "The deployed Vercel URL must not be submitted until unauthenticated public access and hosted HydraDB environment/readback pass",
    ],
    graphPath: [
      "submission link",
      "deployment/video/repository artifact",
      "accessibility check",
      "release receipt",
      "submission manifest",
    ],
    limitation:
      "GitHub is public. The video completion is a directly supplied human attestation. The optional Vercel URL remains pending as a final submitted link until it is publicly accessible without Vercel authentication and the hosted HydraDB readback is established.",
  },
  {
    key: "one_submission_rule",
    label: "One submission per team member",
    formConfirmation:
      "I confirm that every team member listed above is part of only one Hack Hydra submission.",
    state: "HUMAN_ATTESTATION_REQUIRED",
    evidence: [
      "final team roster can be hashed as an FCO",
      "final submission-candidate receipt can bind the roster to this project",
    ],
    graphPath: [
      "team roster",
      "RosterFCO",
      "submission candidate",
      "human attestation",
    ],
    limitation:
      "HydraDG cannot independently observe every Hack Hydra submission made by every person. This checkbox remains a human/team attestation even when its final text and roster are hashed into custody.",
  },
  {
    key: "final_confirmation",
    label: "Accuracy, rules, and code-of-conduct confirmation",
    formConfirmation:
      "I confirm that the information in this submission is accurate and that our team agrees to the Hack Hydra rules and code of conduct.",
    state: "HUMAN_ATTESTATION_REQUIRED",
    evidence: [
      "final submission manifest and claim-to-evidence table",
      "tested commit SHA, deployment identity, and artifact hashes",
      "bounded claim ceilings for Track 03, custody, signatures, and Merkle/MMR state",
      "final human attestation receipt can be appended without converting it into independent proof",
    ],
    graphPath: [
      "submission manifest",
      "claim/evidence objects",
      "tested release artifact",
      "human final attestation",
    ],
    limitation:
      "Custody makes the submitted state inspectable. Agreement to rules/code of conduct and the truthfulness of the final confirmation are human responsibilities and are not inferred from a hash.",
  },
];
