export type EligibilityState =
  | "EVIDENCE_BUILDING"
  | "ACTIVE_TESTING"
  | "BLOCKED_PENDING_PUBLICATION"
  | "HUMAN_ATTESTATION_REQUIRED";

export type EligibilityItem = {
  key: string;
  label: string;
  state: EligibilityState;
  evidence: string[];
  limitation: string;
};

export const eligibilityClaimCeiling =
  "AUDIT_EVIDENCE_SUPPORTS_ATTESTATION_NOT_INDEPENDENT_PROOF";

export const hackHydraEligibility: EligibilityItem[] = [
  {
    key: "originality",
    label: "Originality confirmation",
    state: "EVIDENCE_BUILDING",
    evidence: [
      "Hack-Hydra-specific Git branch/commit chronology",
      "FCO/FCG object and transformation receipts",
      "experiment and lab-notebook timestamps/hashes",
      "host/software/model/tool execution receipts as they are produced",
      "explicit inventory of pre-existing components reused as dependencies",
    ],
    limitation:
      "Custody can show an auditable development chronology and distinguish reused dependencies from Hack-Hydra-specific work; it is not independent proof of first authorship or wall-clock truth.",
  },
  {
    key: "submission_eligibility",
    label: "Built for Hack Hydra",
    state: "EVIDENCE_BUILDING",
    evidence: [
      "Hack-Hydra-specific architecture and execution schedule",
      "branch-scoped implementation receipts",
      "issue/experiment lineage from requirement to implementation",
      "pre-existing dependency boundary declarations",
    ],
    limitation:
      "The graph supports the team attestation by exposing what was newly built versus reused; the eligibility judgment remains governed by the hackathon rules and team confirmation.",
  },
  {
    key: "hydradb_requirement",
    label: "Meaningful HydraDB use",
    state: "ACTIVE_TESTING",
    evidence: [
      "pinned hydra-db/hydradb source revision",
      "HydraDB HTTP graph adapter",
      "current/history/provenance query path",
      "backend write/read/replay tests and receipts once executed",
    ],
    limitation:
      "Do not mark verified until the backend graph tests execute against the selected HydraDB runtime and receipts are retained.",
  },
  {
    key: "link_accessibility",
    label: "Judge-accessible links",
    state: "BLOCKED_PENDING_PUBLICATION",
    evidence: [
      "public GitHub repository check",
      "YouTube demo accessibility check",
      "optional deployed app off-session accessibility check",
    ],
    limitation:
      "The repository is not yet public and the final video does not yet exist, so this confirmation is intentionally blocked.",
  },
  {
    key: "one_submission_rule",
    label: "One submission per team member",
    state: "HUMAN_ATTESTATION_REQUIRED",
    evidence: [
      "hashed final team roster",
      "submission-candidate receipt",
    ],
    limitation:
      "HydraDG cannot independently observe every hackathon submission by each person; this remains a human/team attestation.",
  },
  {
    key: "final_confirmation",
    label: "Accuracy, rules, and code-of-conduct confirmation",
    state: "HUMAN_ATTESTATION_REQUIRED",
    evidence: [
      "final submission manifest",
      "claim-to-evidence table",
      "tested commit SHA and artifact hashes",
      "team attestation receipt",
    ],
    limitation:
      "Custody can make the submitted state and evidence inspectable, but agreement to rules and accuracy of the final attestation remain human responsibilities.",
  },
];
