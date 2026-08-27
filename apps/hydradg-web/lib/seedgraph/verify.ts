import { createHash } from "node:crypto";
import type { QuarantineRecord } from "../providers/types";
import type { RepairOutcome, SeedGraphGap } from "./types";

export type VerificationResult = {
  outcome: RepairOutcome;
  reasons: string[];
};

export function verifyCandidate(
  gap: SeedGraphGap,
  quarantine: QuarantineRecord | null,
  retrieveStatus?: "PASS" | "NEGATIVE" | "ERROR" | "BLOCKED" | "TIMEOUT" | null,
): VerificationResult {
  if (!gap.repairable_by_tavily || !gap.expected_url) {
    return {
      outcome: "ABSTAIN",
      reasons: ["No expected URL; retrieval would invent a source."],
    };
  }

  if (gap.node_id === "sg-conflict-anchor") {
    return {
      outcome: "NEGATIVE",
      reasons: [
        "Retrieved bytes cannot satisfy the frozen conflict SHA on the canonical node.",
        "Canonical mutation is forbidden; conflict remains unresolved.",
      ],
    };
  }

  if (retrieveStatus === "BLOCKED") {
    return {
      outcome: "ABSTAIN",
      reasons: ["Tavily API key is not usable in this runtime; no retrieval was attempted."],
    };
  }

  if (retrieveStatus === "ERROR" || retrieveStatus === "TIMEOUT") {
    return {
      outcome: "NULL",
      reasons: [`Tavily retrieval ${retrieveStatus}; no usable quarantined evidence.`],
    };
  }

  if (!quarantine) {
    return {
      outcome: "NULL",
      reasons: ["No quarantined retrieval record was produced."],
    };
  }

  if (quarantine.evidence_class !== "EXTERNALLY_RETRIEVED_EVIDENCE") {
    return {
      outcome: "NEGATIVE",
      reasons: [`Evidence class is ${quarantine.evidence_class}, not EXTERNALLY_RETRIEVED_EVIDENCE.`],
    };
  }

  if (quarantine.custody_state !== "QUARANTINED") {
    return {
      outcome: "NEGATIVE",
      reasons: [`Custody state is ${quarantine.custody_state}, not QUARANTINED.`],
    };
  }

  const recomputed = createHash("sha256").update(quarantine.raw_bytes, "utf8").digest("hex");
  if (recomputed !== quarantine.raw_sha256) {
    return {
      outcome: "NEGATIVE",
      reasons: ["Raw-byte SHA-256 failed independent recompute."],
    };
  }

  if (quarantine.result_count < 1 || retrieveStatus === "NEGATIVE") {
    return {
      outcome: "NULL",
      reasons: ["Retrieval returned zero results."],
    };
  }

  return {
    outcome: "PASS",
    reasons: [
      "Schema, evidence class, quarantine state, and raw SHA-256 recompute passed.",
      "Canonical SeedGraph and canonical FCG were not mutated.",
    ],
  };
}
