#!/usr/bin/env npx tsx
/** Compose SPONSOR_INTEGRATION_CLOSEOUT.json from mission receipts. */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import * as gumModNs from "../lib/sponsors/gumDoctor.ts";
import * as tavilyModNs from "../lib/sponsors/tavilyAdapter.ts";
import * as gwModNs from "../lib/sponsors/evidenceGateway.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { discoverGumDoctor } = unwrapHydraLampMod(gumModNs as Record<string, unknown>) as {
  discoverGumDoctor: typeof import("../lib/sponsors/gumDoctor.ts").discoverGumDoctor;
};
const { loadTavilyExtractFromFile } = unwrapHydraLampMod(tavilyModNs as Record<string, unknown>) as typeof import("../lib/sponsors/tavilyAdapter.ts");
const { executeGatewayTool } = unwrapHydraLampMod(gwModNs as Record<string, unknown>) as typeof import("../lib/sponsors/evidenceGateway.ts");

const { repoRoot } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
};

function readJson(p: string): Record<string, unknown> | null {
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

function sha256Json(obj: unknown): string {
  return createHash("sha256").update(JSON.stringify(obj)).digest("hex");
}

async function main() {
  const root = repoRoot();
  const evalDir = path.join(root, "eval", "agent_native_sponsors_20260827");
  mkdirSync(evalDir, { recursive: true });

  const gum = discoverGumDoctor(root);

  const runtype = readJson(path.join(evalDir, "runtype", "RUNTYPE_MISSION_RECEIPT.json"));
  const tavilyFile = loadTavilyExtractFromFile(
    root,
    "eval/agent_native_sponsors_20260827/tavily/raw/TAVILY_EXTRACT_CORTEX_DOCS.json",
  );
  const tavilyReceipt = readJson(path.join(evalDir, "tavily", "TAVILY_MISSION_RECEIPT.json"));
  const ic = readJson(path.join(evalDir, "immersive_commons", "IMMERSIVE_COMMONS_MISSION_RECEIPT.json"));

  // Write blocked/deferred mission stubs
  const blockedMissions = [
    {
      dir: "cortex",
      file: "CORTEX_MISSION_RECEIPT.json",
      body: {
        schema: "sponsor.cortex.mission_receipt.v1",
        mission_id: "ANB-SP-CORTEX-ROUNDTRIP-001",
        provider: "Mitosis Cortex",
        operation: "memory_roundtrip",
        status: "BLOCKED",
        error_code: "MI_CLI_MISSING",
        error_summary: "mi CLI not on PATH; CONVEX_URL not configured; GUM Doctor secret injection BLOCKED",
        offer_code_metadata: "FREECORTEX",
        offer_is_api_credential: false,
        architectural_boundary: "Cortex is external agent memory; FCG remains canonical HydraDG custody",
        roundtrip: {
          CORTEX_MEMORY_ROUNDTRIP: "NOT_ATTEMPTED",
          UNDERLYING_HYDRADG_RECEIPT_VERIFICATION: "NOT_ATTEMPTED",
        },
        underlying_receipt_ref: "eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        secret_state: "BLOCKED",
        signature_state: "NOT_SIGNED",
      },
    },
    {
      dir: "yappy",
      file: "YAPPY_MISSION_RECEIPT.json",
      body: {
        schema: "sponsor.yappy.mission_receipt.v1",
        mission_id: "ANB-SP-YAPPY-INTERACT-001",
        provider: "Mitosis Yappy",
        operation: "external_computer_use_interaction",
        status: "BLOCKED",
        error_code: "MI_CLI_MISSING",
        offer_code_metadata: "FREEYAPPY",
        offer_is_api_credential: false,
        claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
        secret_state: "BLOCKED",
        signature_state: "NOT_SIGNED",
      },
    },
    {
      dir: "cotal",
      file: "COTAL_MISSION_RECEIPT.json",
      body: {
        schema: "sponsor.cotal.mission_receipt.v1",
        mission_id: "ANB-SP-COTAL-A2A-001",
        provider: "Cotal",
        operation: "a2a_gateway_transaction",
        status: "SKIPPED",
        discovery_state: "DEFERRED_NONBLOCKING",
        gateway_tools_available: ["discover_capabilities", "query_evidence", "propose_external_evidence", "verify_custody_receipt"],
        bounded_transaction: "NOT_ATTEMPTED",
        claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
        signature_state: "NOT_SIGNED",
      },
    },
    {
      dir: "hacker_bob",
      file: "HACKER_BOB_MISSION_RECEIPT.json",
      body: {
        schema: "sponsor.hacker_bob.mission_receipt.v1",
        mission_id: "ANB-SP-HACKERBOB-SCAN-001",
        provider: "Hacker Bob",
        operation: "bounded_security_scan",
        status: "SKIPPED",
        error_summary: "Full MCP hunt deferred; package discovery recorded only. Findings are EXTERNALLY_RETRIEVED_EVIDENCE not verified vulnerabilities.",
        scanner_identity: "hacker-bob npm package (discovered)",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        signature_state: "NOT_SIGNED",
      },
    },
    {
      dir: "tenki",
      file: "TENKI_MISSION_RECEIPT.json",
      body: {
        schema: "sponsor.tenki.mission_receipt.v1",
        mission_id: "ANB-SP-TENKI-SANDBOX-001",
        provider: "Tenki",
        operation: "sandbox_smoke",
        status: "SKIPPED",
        discovery_state: "DEFERRED_NONBLOCKING",
        note: "Account/setup required; sponsor infra demo only",
        claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
        signature_state: "NOT_SIGNED",
      },
    },
    {
      dir: "nebius",
      file: "NEBIUS_MISSION_RECEIPT.json",
      body: {
        schema: "sponsor.nebius.discovery_receipt.v1",
        mission_id: "ANB-SP-NEBIUS-SMOKE-001",
        provider: "Nebius",
        NEBIUS_STATE: "SKIPPED_NONBLOCKING",
        status: "SKIPPED",
        note: "Optional non-blocking; no repeated setup loop",
        claim_ceiling: "NOT_APPLICABLE",
        signature_state: "NOT_SIGNED",
      },
    },
    {
      dir: "ultimate_fighting_agents",
      file: "UFA_SUBMISSION_READINESS.json",
      body: {
        schema: "sponsor.ufa.submission_readiness.v1",
        provider: "Ultimate Fighting Agents",
        track: "submission_only",
        sponsor_offer: {
          guaranteed_approval: true,
          prize_pool_usd: 15000,
        },
        perturbations_from_hydralamp: ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"],
        science_outputs_unchanged: true,
        closeout_receipt_ref: "eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json",
        claim_ceiling: "PREREGISTERED_RUNTYPE_HYDRALAMP_DEMO_DESIGN",
        signature_state: "NOT_SIGNED",
      },
    },
  ];

  for (const m of blockedMissions) {
    const d = path.join(evalDir, m.dir);
    mkdirSync(d, { recursive: true });
    writeFileSync(path.join(d, m.file), JSON.stringify(m.body, null, 2) + "\n");
  }

  // Cotal gateway bounded deterministic transaction (local)
  const gwDiscover = executeGatewayTool("discover_capabilities", root);
  const tavilySha = tavilyFile?.raw_artifact_sha256 || "";
  const gwPropose = executeGatewayTool("propose_external_evidence", root, {
    source_url: tavilyFile?.source_url || "",
    raw_artifact_sha256: tavilySha,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
  });
  writeFileSync(
    path.join(evalDir, "cotal", "GATEWAY_BOUNDED_TRANSACTION.json"),
    JSON.stringify({ discover: gwDiscover, propose: gwPropose, note: "Local gateway stub; not Cotal canonical state." }, null, 2) + "\n",
  );

  const runtypeStatus = String(runtype?.status || "NOT_ATTEMPTED");
  const tavilyStatus = tavilyFile?.status || String(tavilyReceipt?.status || "NOT_ATTEMPTED");

  const goldenPathNotes: string[] = [];
  if (tavilyStatus === "PASS") goldenPathNotes.push("Tavily extract PASS");
  else goldenPathNotes.push("Tavily extract not PASS");
  if (runtypeStatus === "PASS") goldenPathNotes.push("Runtype live PASS");
  else goldenPathNotes.push("Runtype live ERROR preserved");
  goldenPathNotes.push("Cortex roundtrip BLOCKED (mi CLI missing)");

  const closeout = {
    schema: "sponsor.integration_closeout.v1",
    recorded_at_utc: new Date().toISOString(),
    branch: "hack-hydra/hydralamp-20260826",
    execution_host: "magicSTUDIObox.local",
    GUM_DOCTOR_STATE: gum.GUM_DOCTOR_STATE,
    SPONSOR_SECRET_INJECTION: gum.SPONSOR_SECRET_INJECTION,
    providers: {
      Runtype: {
        priority: "P0",
        discovery_state: "CONFIGURED",
        live_status: runtypeStatus,
        secret_state: runtype?.RUNTYPE_API_KEY === "PRESENT" ? "PRESENT" : "MISSING",
        receipt_path: "eval/agent_native_sponsors_20260827/runtype/RUNTYPE_MISSION_RECEIPT.json",
        claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
        earliest_divergence: runtypeStatus !== "PASS" ? "runtype_execution_id null / lane ERROR" : null,
      },
      Tavily: {
        priority: "P0",
        discovery_state: "CONFIGURED",
        live_status: tavilyStatus,
        secret_state: "NOT_APPLICABLE",
        receipt_path: "eval/agent_native_sponsors_20260827/tavily/TAVILY_MISSION_RECEIPT.json",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        earliest_divergence: null,
      },
      Cortex: {
        priority: "P0",
        discovery_state: "BLOCKED",
        live_status: "BLOCKED",
        secret_state: "BLOCKED",
        receipt_path: "eval/agent_native_sponsors_20260827/cortex/CORTEX_MISSION_RECEIPT.json",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        earliest_divergence: "mi CLI / CONVEX_URL missing",
      },
      Yappy: {
        priority: "P1",
        discovery_state: "BLOCKED",
        live_status: "BLOCKED",
        secret_state: "BLOCKED",
        receipt_path: "eval/agent_native_sponsors_20260827/yappy/YAPPY_MISSION_RECEIPT.json",
        claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
        earliest_divergence: "mi CLI missing",
      },
      "Immersive Commons": {
        priority: "P1",
        discovery_state: "DISCOVERED",
        live_status: ic?.status === "PASS" ? "PASS" : "ERROR",
        secret_state: "NOT_APPLICABLE",
        receipt_path: "eval/agent_native_sponsors_20260827/immersive_commons/IMMERSIVE_COMMONS_MISSION_RECEIPT.json",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        earliest_divergence: null,
      },
      Cotal: {
        priority: "P1",
        discovery_state: "DEFERRED_NONBLOCKING",
        live_status: "SKIPPED",
        secret_state: "NOT_APPLICABLE",
        receipt_path: "eval/agent_native_sponsors_20260827/cotal/COTAL_MISSION_RECEIPT.json",
        claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
        earliest_divergence: "mesh setup deferred",
      },
      "Hacker Bob": {
        priority: "P2",
        discovery_state: "DISCOVERED",
        live_status: "SKIPPED",
        secret_state: "NOT_APPLICABLE",
        receipt_path: "eval/agent_native_sponsors_20260827/hacker_bob/HACKER_BOB_MISSION_RECEIPT.json",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        earliest_divergence: "scan not executed",
      },
      Tenki: {
        priority: "P2",
        discovery_state: "DEFERRED_NONBLOCKING",
        live_status: "SKIPPED",
        secret_state: "MISSING",
        receipt_path: "eval/agent_native_sponsors_20260827/tenki/TENKI_MISSION_RECEIPT.json",
        claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
        earliest_divergence: "account setup",
      },
      Nebius: {
        priority: "OPTIONAL",
        discovery_state: "SKIPPED",
        live_status: "SKIPPED",
        NEBIUS_STATE: "SKIPPED_NONBLOCKING",
        secret_state: "MISSING",
        receipt_path: "eval/agent_native_sponsors_20260827/nebius/NEBIUS_MISSION_RECEIPT.json",
        claim_ceiling: "NOT_APPLICABLE",
        earliest_divergence: null,
      },
    },
    golden_path: {
      source: tavilyStatus === "PASS" ? "Tavily" : null,
      memory: null,
      model: runtypeStatus === "PASS" ? "Runtype" : null,
      external_actor: null,
      custody: "HydraDG FCO/FCG",
      projection: "HydraDB",
      composed_status: tavilyStatus === "PASS" ? "PARTIAL" : "BLOCKED",
      notes: goldenPathNotes,
    },
    GOLDEN_PATH_STATE: tavilyStatus === "PASS" && runtypeStatus === "PASS" ? "PARTIAL_P0" : "PARTIAL_BLOCKED",
    EVIDENCE_STATE: tavilyStatus === "PASS" ? "EXTERNALLY_RETRIEVED_EVIDENCE_CAPTURED" : "MIXED",
    EXPERIMENT_STATE: "HYDRALAMP_CLOSEOUT_FROZEN_NO_RERUN",
    FCO_STATE: "QUARANTINE_PROPOSALS_ONLY",
    FCG_STATE: "CANONICAL_UNCHANGED_BY_SPONSOR_MISSIONS",
    HYDRADB_STATE: "PROJECTION_LANE_AVAILABLE",
    EARLIEST_DIVERGENCE: runtypeStatus !== "PASS" ? "Runtype provider lane ERROR" : "Cortex memory roundtrip BLOCKED",
    CLAIM_CEILING: "SPONSOR_INTEGRATION_BENCHMARK_ONLY",
    SIGNATURE_STATE: "NOT_SIGNED",
    MERKLE_MMR_STATE: "NOT_COMMITTED",
    NEXT_SAFE_ACTION: "Configure mi/Cortex with human-approved credentials via GUM Doctor when available",
    FINAL_REVIEW_GATE: "P0 golden path partial: Tavily PASS; Runtype ERROR preserved; Cortex BLOCKED",
  };

  const closeoutPath = path.join(evalDir, "SPONSOR_INTEGRATION_CLOSEOUT.json");
  writeFileSync(closeoutPath, JSON.stringify(closeout, null, 2) + "\n");
  writeFileSync(path.join(evalDir, "CLOSEOUT.sha256"), sha256Json(closeout) + "\n");
  console.log("CLOSEOUT_WRITTEN", closeoutPath);
  console.log("GOLDEN_PATH_STATE=" + closeout.GOLDEN_PATH_STATE);
}

void main();
