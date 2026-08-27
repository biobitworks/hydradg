/**
 * Tavily → EXTERNALLY_RETRIEVED_EVIDENCE adapter.
 * Uses tvly CLI OAuth auth; never persists API keys in repo.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import type { SponsorMissionResult } from "./types";

export function sha256Bytes(data: Buffer | string): string {
  return createHash("sha256").update(data).digest("hex");
}

export function tavilyCliStatus(): "PRESENT" | "MISSING" {
  const r = spawnSync("command", ["-v", "tvly"], { encoding: "utf8", shell: true });
  return r.status === 0 ? "PRESENT" : "MISSING";
}

export type TavilyExtractReceipt = {
  schema: "sponsor.tavily.extract_receipt.v1";
  mission_id: string;
  provider: "Tavily";
  operation: "extract";
  source_url: string;
  request_id: string | null;
  retrieval_timestamp: string;
  raw_artifact_path: string;
  raw_artifact_sha256: string;
  output_hash: string;
  evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE";
  fco_proposal: {
    action: "QUARANTINE_EXTERNAL_EVIDENCE";
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE";
    admit_decision: "PENDING_CUSTODY_REVIEW";
    note: "Tavily output must not write directly to canonical FCG state.",
  };
  status: "PASS" | "ERROR" | "NEGATIVE";
  prior_negative_cases_preserved: string[];
};

export function runTavilyExtractMission(params: {
  repoRoot: string;
  sourceUrl: string;
  missionId?: string;
}): { receipt: TavilyExtractReceipt; mission: SponsorMissionResult } {
  const mission_id = params.missionId || "ANB-SP-TAVILY-EXTRACT-001";
  const started = new Date().toISOString();
  const outDir = path.join(
    params.repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "tavily",
    "raw",
  );
  mkdirSync(outDir, { recursive: true });

  if (tavilyCliStatus() === "MISSING") {
    const completed = new Date().toISOString();
    const receiptPath = path.join(
      params.repoRoot,
      "eval",
      "agent_native_sponsors_20260827",
      "tavily",
      "TAVILY_MISSION_RECEIPT.json",
    );
    const mission: SponsorMissionResult = {
      mission_id,
      provider: "Tavily",
      operation: "extract",
      started_at: started,
      completed_at: completed,
      evidence_class: "NONE",
      source_identity: null,
      external_execution_id: null,
      raw_artifact_sha256: null,
      output_hash: null,
      status: "BLOCKED",
      error_code: "TVLY_CLI_MISSING",
      error_summary: "tvly CLI not on PATH",
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
      secret_state: "NOT_APPLICABLE",
      secret_ref: null,
      required_env_names: [],
      discovery_state: "DISCOVERED",
      connectivity_state: "BLOCKED",
      empirical_state: "NOT_ATTEMPTED",
      receipt_path: receiptPath,
    };
    return { receipt: {} as TavilyExtractReceipt, mission };
  }

  const rawName = `TAVILY_EXTRACT_${Date.now()}.json`;
  const rawPath = path.join(outDir, rawName);
  const proc = spawnSync("tvly", ["extract", params.sourceUrl, "--json"], {
    encoding: "buffer",
    maxBuffer: 8 * 1024 * 1024,
  });

  if (proc.status !== 0 || !proc.stdout?.length) {
    const completed = new Date().toISOString();
    const receiptPath = path.join(
      params.repoRoot,
      "eval",
      "agent_native_sponsors_20260827",
      "tavily",
      "TAVILY_MISSION_RECEIPT.json",
    );
    const mission: SponsorMissionResult = {
      mission_id,
      provider: "Tavily",
      operation: "extract",
      started_at: started,
      completed_at: completed,
      evidence_class: "NONE",
      source_identity: params.sourceUrl,
      external_execution_id: null,
      raw_artifact_sha256: null,
      output_hash: null,
      status: "ERROR",
      error_code: "TVLY_EXTRACT_FAILED",
      error_summary: String(proc.stderr?.toString("utf8") || "extract failed").slice(0, 200),
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
      secret_state: "NOT_APPLICABLE",
      secret_ref: null,
      required_env_names: [],
      discovery_state: "CONFIGURED",
      connectivity_state: "ERROR",
      empirical_state: "ERROR",
      receipt_path: receiptPath,
    };
    return { receipt: {} as TavilyExtractReceipt, mission };
  }

  writeFileSync(rawPath, proc.stdout);
  const rawSha = sha256Bytes(proc.stdout);
  let parsed: Record<string, unknown> = {};
  try {
    parsed = JSON.parse(proc.stdout.toString("utf8"));
  } catch {
    /* keep hash only */
  }
  const request_id =
    typeof parsed.request_id === "string" ? parsed.request_id : null;
  const results = Array.isArray(parsed.results) ? parsed.results : [];
  const hasContent = results.some(
    (r: { raw_content?: string }) => typeof r?.raw_content === "string" && r.raw_content.length > 0,
  );
  const status = hasContent ? "PASS" : "NEGATIVE";
  const completed = new Date().toISOString();
  const receiptRel = "eval/agent_native_sponsors_20260827/tavily/TAVILY_MISSION_RECEIPT.json";
  const receiptPath = path.join(params.repoRoot, receiptRel);

  const receipt: TavilyExtractReceipt = {
    schema: "sponsor.tavily.extract_receipt.v1",
    mission_id,
    provider: "Tavily",
    operation: "extract",
    source_url: params.sourceUrl,
    request_id,
    retrieval_timestamp: completed,
    raw_artifact_path: path.relative(params.repoRoot, rawPath),
    raw_artifact_sha256: rawSha,
    output_hash: rawSha,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
    fco_proposal: {
      action: "QUARANTINE_EXTERNAL_EVIDENCE",
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
      admit_decision: "PENDING_CUSTODY_REVIEW",
      note: "Tavily output must not write directly to canonical FCG state.",
    },
    status,
    prior_negative_cases_preserved: [
      "eval/hydralamp_tavily_20260827/raw/TAVILY_SEARCH_RAW.json",
      "eval/hydralamp_tavily_20260827/raw/TAVILY_SEARCH_T1_DOMAIN_CONSTRAINED.json",
    ],
  };
  writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + "\n");

  const mission: SponsorMissionResult = {
    mission_id,
    provider: "Tavily",
    operation: "extract",
    started_at: started,
    completed_at: completed,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
    source_identity: params.sourceUrl,
    external_execution_id: request_id,
    raw_artifact_sha256: rawSha,
    output_hash: rawSha,
    status,
    error_code: status === "PASS" ? null : "EMPTY_EXTRACT",
    error_summary: status === "PASS" ? null : "Extract returned no raw_content",
    claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
    secret_state: "NOT_APPLICABLE",
    secret_ref: "tvly_cli_oauth",
    required_env_names: [],
    discovery_state: "CONFIGURED",
    connectivity_state: status === "PASS" ? "PASS" : status,
    empirical_state: status === "PASS" ? "PASS" : status,
    receipt_path: receiptRel,
  };
  return { receipt, mission };
}

/** Load existing extract artifact without re-running CLI. */
export function loadTavilyExtractFromFile(
  repoRoot: string,
  relPath: string,
): TavilyExtractReceipt | null {
  const abs = path.join(repoRoot, relPath);
  if (!existsSync(abs)) return null;
  const raw = readFileSync(abs);
  const rawSha = sha256Bytes(raw);
  let parsed: Record<string, unknown> = {};
  try {
    parsed = JSON.parse(raw.toString("utf8"));
  } catch {
    return null;
  }
  const results = Array.isArray(parsed.results) ? parsed.results : [];
  const url =
    results[0] && typeof (results[0] as { url?: string }).url === "string"
      ? (results[0] as { url: string }).url
      : "unknown";
  const hasContent = results.some(
    (r: { raw_content?: string }) => typeof r?.raw_content === "string" && r.raw_content.length > 0,
  );
  return {
    schema: "sponsor.tavily.extract_receipt.v1",
    mission_id: "ANB-SP-TAVILY-EXTRACT-001",
    provider: "Tavily",
    operation: "extract",
    source_url: url,
    request_id: typeof parsed.request_id === "string" ? parsed.request_id : null,
    retrieval_timestamp: new Date().toISOString(),
    raw_artifact_path: relPath,
    raw_artifact_sha256: rawSha,
    output_hash: rawSha,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
    fco_proposal: {
      action: "QUARANTINE_EXTERNAL_EVIDENCE",
      claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
      admit_decision: "PENDING_CUSTODY_REVIEW",
      note: "Tavily output must not write directly to canonical FCG state.",
    },
    status: hasContent ? "PASS" : "NEGATIVE",
    prior_negative_cases_preserved: [
      "eval/hydralamp_tavily_20260827/raw/TAVILY_SEARCH_RAW.json",
      "eval/hydralamp_tavily_20260827/raw/TAVILY_SEARCH_T1_DOMAIN_CONSTRAINED.json",
    ],
  };
}
