export type EligibilityState =
  | "EVIDENCE_BUILDING"
  | "CI_BACKEND_VERIFIED"
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
    state: "CI_BACKEND_VERIFIED",
    evidence: [
      "pinned hydra-db/hydradb source revision 6a2fbb192f37f51a93690a2ae2d2f5e27e6e4219",
      "HydraDB HTTP graph adapter",
      "HydraDB container digest sha256:db78309a233be54662db29744047e985a39b51c45a270d1a1f47c31a62cdb709",
      "GitHub Actions run 32187451568 / run #28",
      "direct HydraDB write/read round trip",
      "HydraDG deterministic fixture admission",
      "current/history/provenance query proof",
      "E2E artifact sha256:5c3acbbef4f266f32b1ba59f36d525e326fe04c5e31b9e9b62f52db5087b939b",
    ],
    limitation:
      "This state means the declared backend path executed successfully in GitHub CI against the recorded HydraDB image. It is not a claim that magicstudiobox, every deployment environment, or every possible graph workload has been verified.",
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
      "The repository has not yet been independently rechecked as public and the final video does not yet exist, so this confirmation remains blocked.",
  },
  {
    key: "one_submission_rule",
    label: "One submission per team member",
    state: "HUMAN_ATTESTATION_REQUIRED",
    evidence: ["hashed final team roster", "submission-candidate receipt"],
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
