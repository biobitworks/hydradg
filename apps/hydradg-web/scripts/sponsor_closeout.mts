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
  const daytona = readJson(path.join(evalDir, "daytona", "DAYTONA_SMOKE_RECEIPT.json"));
  const cortexRoundtrip = readJson(
    path.join(evalDir, "cortex", "CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json"),
  );
  const cortexMission = readJson(path.join(evalDir, "cortex", "CORTEX_MISSION_RECEIPT.json"));
  const tavilyAiSdk = readJson(path.join(evalDir, "tavily", "TAVILY_AISDK_MISSION_RECEIPT.json"));
  const tenkiSandbox = readJson(
    path.join(evalDir, "tenki", "TENKI_SANDBOX_MISSION_RECEIPT.json"),
  );
  const tenkiMission = readJson(path.join(evalDir, "tenki", "TENKI_MISSION_RECEIPT.json"));
  const cotalLive = readJson(path.join(evalDir, "cotal", "COTAL_MISSION_RECEIPT.json"));
  const mitosisYappy = readJson(path.join(evalDir, "yappy", "YAPPY_MISSION_RECEIPT.json"));
  const yappyBiz = readJson(
    path.join(evalDir, "yappy_biz", "YAPPY_BIZ_API_MISSION_RECEIPT.json"),
  );

  // Write blocked/deferred mission stubs (do not overwrite live Cortex roundtrip)
  const blockedMissions = [
    ...(cortexRoundtrip
      ? []
      : [
          {
            dir: "cortex",
            file: "CORTEX_MISSION_RECEIPT.json",
            body: {
              schema: "sponsor.cortex.mission_receipt.v1",
              mission_id: "ANB-SP-CORTEX-ROUNDTRIP-001",
              provider: "Mitosis Cortex",
              operation: "memory_roundtrip",
              status: "BLOCKED",
              error_code: "MI_AUTH_MISSING",
              error_summary: "Cortex roundtrip not yet executed",
              offer_code_metadata: "FREECORTEX",
              offer_is_api_credential: false,
              architectural_boundary:
                "Cortex is external agent memory; FCG remains canonical HydraDG custody",
              roundtrip: {
                CORTEX_MEMORY_ROUNDTRIP: "NOT_ATTEMPTED",
                UNDERLYING_HYDRADG_RECEIPT_VERIFICATION: "NOT_ATTEMPTED",
              },
              underlying_receipt_ref:
                "eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json",
              claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
              secret_state: "BLOCKED",
              signature_state: "NOT_SIGNED",
              docs_ref: "https://mitosislabs.ai/developers/cli/overview",
            },
          },
        ]),
    ...(mitosisYappy ? [] : [
            {
              dir: "yappy",
              file: "YAPPY_MISSION_RECEIPT.json",
              body: {
                schema: "sponsor.yappy.mission_receipt.v1",
                mission_id: "ANB-SP-YAPPY-INTERACT-001",
                provider: "Mitosis Yappy",
                operation: "external_computer_use_interaction",
                status: "BLOCKED",
                error_code: "NOT_ATTEMPTED",
                claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
                signature_state: "NOT_SIGNED",
              },
            },
          ]),
    ...(cotalLive &&
    (cotalLive.operation === "cli_setup_and_gateway_bounded_transaction" ||
      cotalLive.mesh_up === "NOT_ATTEMPTED" ||
      cotalLive.status === "PASS")
      ? []
      : [
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
                claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
                signature_state: "NOT_SIGNED",
              },
            },
          ]),
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
    ...(tenkiSandbox
      ? []
      : [
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
        ]),
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
    const target = path.join(d, m.file);
    // Do not clobber restored/live mission receipts (final reconciliation restores from raw).
    if (existsSync(target)) {
      const existing = readJson(target);
      if (
        existing?.restoration_note ||
        existing?.status === "PASS" ||
        existing?.bounded_transaction === "BOUNDED_TX_PASS" ||
        existing?.error_code === "MI_NO_AGENTS"
      ) {
        continue;
      }
    }
    writeFileSync(target, JSON.stringify(m.body, null, 2) + "\n");
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
  const cortexRt = String(cortexRoundtrip?.CORTEX_MEMORY_ROUNDTRIP || "NOT_ATTEMPTED");
  const cortexHydra = String(
    cortexRoundtrip?.HYDRADG_RECEIPT_VERIFICATION || "NOT_ATTEMPTED",
  );
  const cortexStatus = String(
    cortexRoundtrip?.status || cortexMission?.status || "NOT_ATTEMPTED",
  );

  const goldenPathNotes: string[] = [];
  if (tavilyStatus === "PASS") goldenPathNotes.push("Tavily extract PASS");
  else goldenPathNotes.push("Tavily extract not PASS");
  if (runtypeStatus === "PASS") goldenPathNotes.push("Runtype live PASS");
  else goldenPathNotes.push("Runtype live ERROR preserved");
  goldenPathNotes.push(
    `Cortex roundtrip ${cortexRt}; HydraDG verify ${cortexHydra} (status=${cortexStatus})`,
  );

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
        ai_sdk_receipt_path:
          "eval/agent_native_sponsors_20260827/tavily/TAVILY_AISDK_MISSION_RECEIPT.json",
        ai_sdk_status: String(tavilyAiSdk?.status || "NOT_ATTEMPTED"),
        ai_sdk_package_import: String(tavilyAiSdk?.package_import || "NOT_ATTEMPTED"),
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        earliest_divergence: null,
      },
      Cortex: {
        priority: "P0",
        discovery_state:
          cortexRoundtrip?.auth_state === "PASS" ? "CONFIGURED" : "CLI_INSTALLED_AWAITING_AUTH",
        live_status: cortexStatus,
        secret_state: String(cortexRoundtrip?.secret_state || cortexMission?.secret_state || "BLOCKED"),
        receipt_path:
          "eval/agent_native_sponsors_20260827/cortex/CORTEX_MEMORY_ROUNDTRIP_RECEIPT.json",
        mission_receipt_path:
          "eval/agent_native_sponsors_20260827/cortex/CORTEX_MISSION_RECEIPT.json",
        CORTEX_MEMORY_ROUNDTRIP: cortexRt,
        HYDRADG_RECEIPT_VERIFICATION: cortexHydra,
        offer_code_metadata: "FREECORTEX",
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        earliest_divergence:
          cortexStatus === "PASS"
            ? null
            : String(cortexRoundtrip?.error_code || cortexMission?.error_code || "cortex_incomplete"),
      },
      Yappy: {
        priority: "P1",
        discovery_state: "CONFIGURED",
        live_status: String(mitosisYappy?.status || "BLOCKED"),
        secret_state: String(mitosisYappy?.secret_state || "BLOCKED"),
        receipt_path: "eval/agent_native_sponsors_20260827/yappy/YAPPY_MISSION_RECEIPT.json",
        agents_listed: mitosisYappy?.agents_listed ?? null,
        claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
        earliest_divergence: String(
          mitosisYappy?.error_code || "MI_NO_AGENTS",
        ),
        identity_note: "Mitosis Yappy — distinct from Yappy.biz",
      },
      "Yappy.biz": {
        priority: "P1",
        discovery_state: "CONFIGURED",
        live_status: String(yappyBiz?.status || "NOT_ATTEMPTED"),
        secret_state: "NOT_APPLICABLE",
        receipt_path:
          "eval/agent_native_sponsors_20260827/yappy_biz/YAPPY_BIZ_API_MISSION_RECEIPT.json",
        latest_release: yappyBiz?.latest_release_version || null,
        claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE",
        earliest_divergence: yappyBiz?.status === "PASS" ? null : String(yappyBiz?.error_code || "not_attempted"),
        identity_note: "yappy.biz public product API — distinct from Mitosis Yappy",
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
        discovery_state: "CONFIGURED",
        live_status: String(cotalLive?.status || "SKIPPED"),
        secret_state: "NOT_APPLICABLE",
        receipt_path: "eval/agent_native_sponsors_20260827/cotal/COTAL_MISSION_RECEIPT.json",
        mesh_up: cotalLive?.mesh_up || "NOT_ATTEMPTED",
        claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
        earliest_divergence:
          cotalLive?.status === "PASS" ? null : String(cotalLive?.error_code || "mesh setup deferred"),
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
        discovery_state: tenkiSandbox
          ? tenkiSandbox.status === "PASS"
            ? "CONFIGURED"
            : "CLI_INSTALLED_AWAITING_AUTH"
          : "DEFERRED_NONBLOCKING",
        live_status: String(tenkiSandbox?.status || tenkiMission?.status || "SKIPPED"),
        secret_state: String(tenkiSandbox?.TENKI_API_KEY || "MISSING"),
        receipt_path:
          "eval/agent_native_sponsors_20260827/tenki/TENKI_SANDBOX_MISSION_RECEIPT.json",
        mission_receipt_path:
          "eval/agent_native_sponsors_20260827/tenki/TENKI_MISSION_RECEIPT.json",
        claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
        earliest_divergence:
          tenkiSandbox?.status === "PASS"
            ? null
            : String(tenkiSandbox?.error_code || "TENKI_AUTH_MISSING"),
        scientific_execution_authority: "magicSTUDIObox.local",
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
    infrastructure: {
      Daytona: {
        lane: "INFRASTRUCTURE",
        anb_sponsor: false,
        discovery_state: daytona ? (daytona.status === "PASS" ? "CONFIGURED" : String(daytona.DAYTONA_STATE || "CONFIGURED")) : "CONFIGURED",
        live_status: daytona?.status === "PASS" ? "PASS" : String(daytona?.status || "NOT_ATTEMPTED"),
        secret_state: daytona?.secret_state || "PRESENT",
        receipt_path: "eval/agent_native_sponsors_20260827/daytona/DAYTONA_SMOKE_RECEIPT.json",
        claim_ceiling: "DETERMINISTIC_TOOL_OUTPUT",
        earliest_divergence: daytona?.status === "PASS" ? null : String(daytona?.error_code || "not_attempted"),
        scientific_execution_authority: "magicSTUDIObox.local",
      },
    },
    golden_path: {
      source: tavilyStatus === "PASS" ? "Tavily" : null,
      memory: cortexStatus === "PASS" ? "Mitosis Cortex" : null,
      model: runtypeStatus === "PASS" ? "Runtype" : null,
      external_actor: null,
      custody: "HydraDG FCO/FCG",
      projection: "HydraDB",
      composed_status:
        tavilyStatus === "PASS" || cortexStatus === "PASS" ? "PARTIAL" : "BLOCKED",
      notes: goldenPathNotes,
    },
    GOLDEN_PATH_STATE:
      tavilyStatus === "PASS" && cortexStatus === "PASS" && runtypeStatus === "PASS"
        ? "READY"
        : tavilyStatus === "PASS"
          ? "PARTIAL_P0"
          : "PARTIAL_BLOCKED",
    EVIDENCE_STATE: tavilyStatus === "PASS" ? "EXTERNALLY_RETRIEVED_EVIDENCE_CAPTURED" : "MIXED",
    EXPERIMENT_STATE: "HYDRALAMP_CLOSEOUT_FROZEN_NO_RERUN",
    FCO_STATE: "QUARANTINE_PROPOSALS_ONLY",
    FCG_STATE: "CANONICAL_UNCHANGED_BY_SPONSOR_MISSIONS",
    HYDRADB_STATE: "PROJECTION_LANE_AVAILABLE",
    EARLIEST_DIVERGENCE:
      cortexStatus !== "PASS"
        ? `Cortex ${cortexRt}/${cortexHydra}`
        : runtypeStatus !== "PASS"
          ? "Runtype provider lane ERROR"
          : null,
    CLAIM_CEILING: "SPONSOR_INTEGRATION_BENCHMARK_ONLY",
    SIGNATURE_STATE: "NOT_SIGNED",
    MERKLE_MMR_STATE: "NOT_COMMITTED",
    NEXT_SAFE_ACTION:
      cortexStatus !== "PASS"
        ? "Unlock Cortex office memory plan (trial_expired), then re-run npm run sponsor:mitosis"
        : "Continue P0 golden-path completion without rerunning HydraLamp overnight / Runtype",
    FINAL_REVIEW_GATE: `P0: Tavily=${tavilyStatus}; Cortex=${cortexStatus} (roundtrip=${cortexRt}, hydradg=${cortexHydra}); Runtype=${runtypeStatus} preserved`,
  };

  // v1 closeout is immutable historical evidence. Prefer V2 successor path.
  const v1Path = path.join(evalDir, "SPONSOR_INTEGRATION_CLOSEOUT.json");
  const v2Path = path.join(evalDir, "SPONSOR_INTEGRATION_CLOSEOUT_V2.json");
  if (existsSync(v1Path)) {
    console.log(
      "CLOSEOUT_V1_IMMUTABLE",
      v1Path,
      "— refusing overwrite; use npm run sponsor:final-reconciliation for V2",
    );
    if (!existsSync(v2Path)) {
      const v2 = {
        ...closeout,
        schema: "sponsor.integration_closeout.v2",
        predecessor: {
          path: "eval/agent_native_sponsors_20260827/SPONSOR_INTEGRATION_CLOSEOUT.json",
          immutable: true,
          note: "Generated by sponsor_closeout without recomputing full V2 divergence; prefer sponsor:final-reconciliation.",
        },
      };
      writeFileSync(v2Path, JSON.stringify(v2, null, 2) + "\n");
      writeFileSync(path.join(evalDir, "CLOSEOUT_V2.sha256"), sha256Json(v2) + "\n");
      console.log("CLOSEOUT_V2_WRITTEN", v2Path);
    }
  } else {
    writeFileSync(v1Path, JSON.stringify(closeout, null, 2) + "\n");
    writeFileSync(path.join(evalDir, "CLOSEOUT.sha256"), sha256Json(closeout) + "\n");
    console.log("CLOSEOUT_WRITTEN", v1Path);
  }
  console.log("GOLDEN_PATH_STATE=" + closeout.GOLDEN_PATH_STATE);
}

void main();
