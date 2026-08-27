/**
 * Agent-Native Evidence Gateway — bounded A2A/MCP surface for Cotal/IC discovery.
 * Does not make Cotal or IC canonical state.
 */
import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

export type GatewayToolName =
  | "discover_capabilities"
  | "query_evidence"
  | "propose_external_evidence"
  | "verify_custody_receipt";

export type GatewayCapability = {
  tool: GatewayToolName;
  description: string;
  claim_ceiling: string;
  evidence_class: string;
};

const CAPABILITIES: GatewayCapability[] = [
  {
    tool: "discover_capabilities",
    description: "List supported gateway tools, claim ceilings, and custody boundaries.",
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
  },
  {
    tool: "query_evidence",
    description: "Typed retrieval over quarantined external evidence receipts (read-only).",
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
  },
  {
    tool: "propose_external_evidence",
    description: "Submit external evidence candidate under quarantine; never direct FCG append.",
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
  },
  {
    tool: "verify_custody_receipt",
    description: "Verify SHA-256 of a custody receipt file against declared hash.",
    claim_ceiling: "RECOMPUTED_RESULT",
    evidence_class: "RECOMPUTED_RESULT",
  },
];

function sha256File(absPath: string): string | null {
  if (!existsSync(absPath)) return null;
  const h = createHash("sha256");
  h.update(readFileSync(absPath));
  return h.digest("hex");
}

export function discoverCapabilities(): {
  gateway: "HydraDG Agent-Native Evidence Gateway";
  version: "20260827";
  tools: GatewayCapability[];
  custody_note: string;
} {
  return {
    gateway: "HydraDG Agent-Native Evidence Gateway",
    version: "20260827",
    tools: CAPABILITIES,
    custody_note: "External agents may discover and propose; FCG remains canonical HydraDG custody.",
  };
}

export function queryEvidence(repoRoot: string, receiptPath: string) {
  const abs = path.isAbsolute(receiptPath) ? receiptPath : path.join(repoRoot, receiptPath);
  if (!existsSync(abs)) {
    return { status: "NULL" as const, receipt_path: receiptPath, sha256: null };
  }
  const sha256 = sha256File(abs);
  let schema: string | null = null;
  try {
    const j = JSON.parse(readFileSync(abs, "utf8"));
    schema = typeof j.schema === "string" ? j.schema : null;
  } catch {
    /* malformed */
  }
  return {
    status: "PASS" as const,
    receipt_path: receiptPath,
    sha256,
    schema,
    claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
  };
}

export function proposeExternalEvidence(params: {
  source_url: string;
  raw_artifact_sha256: string;
  evidence_class: string;
}) {
  const proposal_id = createHash("sha256")
    .update(JSON.stringify(params))
    .digest("hex")
    .slice(0, 16);
  return {
    status: "PASS" as const,
    proposal_id,
    quarantine_state: "PENDING_CUSTODY_REVIEW",
    fcg_append: "NOT_APPENDED",
    claim_ceiling: params.evidence_class,
    ...params,
  };
}

export function verifyCustodyReceipt(repoRoot: string, receiptPath: string, declaredSha256: string) {
  const abs = path.isAbsolute(receiptPath) ? receiptPath : path.join(repoRoot, receiptPath);
  const computed = sha256File(abs);
  if (!computed) {
    return { status: "NULL" as const, verified: false, computed: null, declared: declaredSha256 };
  }
  const verified = computed === declaredSha256;
  return {
    status: verified ? ("PASS" as const) : ("FAIL" as const),
    verified,
    computed,
    declared: declaredSha256,
    claim_ceiling: "RECOMPUTED_RESULT",
  };
}

export function executeGatewayTool(
  tool: GatewayToolName,
  repoRoot: string,
  args: Record<string, unknown> = {},
) {
  switch (tool) {
    case "discover_capabilities":
      return discoverCapabilities();
    case "query_evidence":
      return queryEvidence(repoRoot, String(args.receipt_path || ""));
    case "propose_external_evidence":
      return proposeExternalEvidence({
        source_url: String(args.source_url || ""),
        raw_artifact_sha256: String(args.raw_artifact_sha256 || ""),
        evidence_class: String(args.evidence_class || "EXTERNALLY_RETRIEVED_EVIDENCE"),
      });
    case "verify_custody_receipt":
      return verifyCustodyReceipt(
        repoRoot,
        String(args.receipt_path || ""),
        String(args.declared_sha256 || ""),
      );
    default:
      return { status: "ERROR", error: "UNKNOWN_TOOL" };
  }
}
