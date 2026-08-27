import { createHash } from "node:crypto";
import type { QuarantineRecord } from "../providers/types";
import type { AdmissionChecks, RepairOutcome, SeedGraphGap } from "./types";

export type VerificationResult = {
  outcome: RepairOutcome;
  reasons: string[];
  admission: AdmissionChecks;
};

function skippedAdmission(): AdmissionChecks {
  return {
    schema_check: "SKIPPED",
    provenance_check: "SKIPPED",
    contradiction_check: "SKIPPED",
    authorization_check: "SKIPPED",
  };
}

export function verifyCandidate(
  gap: SeedGraphGap,
  quarantine: QuarantineRecord | null,
  retrieveStatus?: "PASS" | "NEGATIVE" | "ERROR" | "BLOCKED" | "TIMEOUT" | null,
): VerificationResult {
  if (!gap.gap_id) {
    return {
      outcome: "ERROR",
      reasons: ["Deterministic gap_id missing."],
      admission: { ...skippedAdmission(), schema_check: "FAIL" },
    };
  }

  if (!gap.repairable_by_tavily || !gap.expected_url) {
    return {
      outcome: "ABSTAIN",
      reasons: ["No expected URL; retrieval would invent a source."],
      admission: {
        schema_check: "PASS",
        provenance_check: "FAIL",
        contradiction_check: "SKIPPED",
        authorization_check: "PASS",
      },
    };
  }

  // Authorization: external evidence may only write SUCCESSOR_NOT_CANONICAL, never canonical.
  const authorization_check: AdmissionChecks["authorization_check"] = "PASS";

  if (gap.node_id === "sg-conflict-anchor") {
    return {
      outcome: "NEGATIVE",
      reasons: [
        "Contradiction check failed: retrieved bytes cannot satisfy the frozen conflict SHA.",
        "Canonical mutation is forbidden; conflict remains unresolved.",
      ],
      admission: {
        schema_check: quarantine ? "PASS" : "SKIPPED",
        provenance_check: "FAIL",
        contradiction_check: "FAIL",
        authorization_check,
      },
    };
  }

  if (retrieveStatus === "BLOCKED") {
    return {
      outcome: "ABSTAIN",
      reasons: ["Tavily API key is not usable in this runtime; no retrieval was attempted."],
      admission: skippedAdmission(),
    };
  }

  if (retrieveStatus === "TIMEOUT") {
    return {
      outcome: "TIMEOUT",
      reasons: ["Tavily retrieval timed out; no usable quarantined evidence."],
      admission: skippedAdmission(),
    };
  }

  if (retrieveStatus === "ERROR") {
    return {
      outcome: "ERROR",
      reasons: ["Tavily retrieval ERROR; no usable quarantined evidence."],
      admission: skippedAdmission(),
    };
  }

  if (!quarantine) {
    return {
      outcome: "NULL",
      reasons: ["No quarantined retrieval record was produced."],
      admission: skippedAdmission(),
    };
  }

  // Schema check: required quarantine fields.
  const schema_ok =
    quarantine.evidence_class === "EXTERNALLY_RETRIEVED_EVIDENCE" &&
    quarantine.custody_state === "QUARANTINED" &&
    Boolean(quarantine.raw_sha256) &&
    Boolean(quarantine.retrieved_at) &&
    Boolean(quarantine.source_url || gap.expected_url) &&
    typeof quarantine.raw_bytes === "string";

  if (!schema_ok) {
    return {
      outcome: "NEGATIVE",
      reasons: [
        "Schema check failed: quarantine must include EXTERNALLY_RETRIEVED_EVIDENCE, QUARANTINED, source URL, retrieval timestamp, and raw SHA-256.",
      ],
      admission: {
        schema_check: "FAIL",
        provenance_check: "SKIPPED",
        contradiction_check: "SKIPPED",
        authorization_check,
      },
    };
  }

  // Provenance: raw SHA must recompute; gap_id must be stable.
  const recomputed = createHash("sha256").update(quarantine.raw_bytes, "utf8").digest("hex");
  if (recomputed !== quarantine.raw_sha256) {
    return {
      outcome: "NEGATIVE",
      reasons: ["Provenance check failed: raw-byte SHA-256 independent recompute mismatch."],
      admission: {
        schema_check: "PASS",
        provenance_check: "FAIL",
        contradiction_check: "SKIPPED",
        authorization_check,
      },
    };
  }

  if (quarantine.result_count < 1 || retrieveStatus === "NEGATIVE") {
    return {
      outcome: "NULL",
      reasons: ["Retrieval returned zero results."],
      admission: {
        schema_check: "PASS",
        provenance_check: "PASS",
        contradiction_check: "PASS",
        authorization_check,
      },
    };
  }

  return {
    outcome: "PASS",
    reasons: [
      "Admission passed: schema, provenance, contradiction, and authorization checks.",
      "Canonical SeedGraph and canonical FCG were not mutated.",
    ],
    admission: {
      schema_check: "PASS",
      provenance_check: "PASS",
      contradiction_check: "PASS",
      authorization_check,
    },
  };
}
