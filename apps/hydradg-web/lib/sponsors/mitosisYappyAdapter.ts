/**
 * Mitosis Yappy lane — computer-use / office agents via `mi`.
 * Distinct from yappy.biz public API.
 */
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { resolveMitosisOfficeId, mitosisAuthState, miCliStatus } from "./cortexAdapter";

export type MitosisYappyMissionReceipt = {
  schema: "sponsor.yappy.mission_receipt.v1";
  mission_id: "ANB-SP-YAPPY-INTERACT-001";
  provider: "Mitosis Yappy";
  operation: "external_computer_use_interaction";
  identity_note: string;
  docs_ref: string;
  auth_state: "PASS" | "FAIL";
  office_id: string | null;
  agents_listed: number;
  agent_names: string[];
  bounded_interaction: "NOT_ATTEMPTED" | "PASS" | "ERROR" | "BLOCKED";
  offer_code_metadata: "FREEYAPPY";
  offer_is_api_credential: false;
  fcg_append: "NOT_APPENDED";
  status: "PASS" | "ERROR" | "BLOCKED";
  error_code: string | null;
  error_summary: string | null;
  claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT";
  secret_state: "PRESENT" | "MISSING" | "BLOCKED";
  signature_state: "NOT_SIGNED";
  recorded_at_utc: string;
};

export function runMitosisYappyMission(params: {
  repoRoot: string;
}): MitosisYappyMissionReceipt {
  const recorded_at_utc = new Date().toISOString();
  const outDir = path.join(
    params.repoRoot,
    "eval",
    "agent_native_sponsors_20260827",
    "yappy",
  );
  mkdirSync(path.join(outDir, "raw"), { recursive: true });

  const auth = mitosisAuthState();
  const office = resolveMitosisOfficeId();
  let agents: Array<{ name?: string }> = [];
  let agents_listed = 0;

  if (miCliStatus() === "PRESENT" && auth === "PASS" && office) {
    const r = spawnSync("mi", ["agents", "list", "--office", office], {
      encoding: "utf8",
      timeout: 60_000,
      maxBuffer: 2 * 1024 * 1024,
    });
    writeFileSync(
      path.join(outDir, "raw", "MI_AGENTS_LIST_RAW.json"),
      JSON.stringify(
        { exit_code: r.status, stdout: r.stdout || "", stderr: r.stderr || "" },
        null,
        2,
      ) + "\n",
    );
    try {
      agents = JSON.parse(r.stdout || "[]");
      if (!Array.isArray(agents)) agents = [];
    } catch {
      agents = [];
    }
    agents_listed = agents.length;
  }

  const names = agents
    .map((a) => (typeof a.name === "string" ? a.name : ""))
    .filter(Boolean);

  let status: MitosisYappyMissionReceipt["status"] = "BLOCKED";
  let error_code: string | null = "MI_NO_AGENTS";
  let error_summary: string | null =
    "Office has zero agents; cannot demonstrate computer-use interaction. Hire/spawn via Mitosis dashboard or mi agents hire, then re-run.";
  let bounded: MitosisYappyMissionReceipt["bounded_interaction"] = "BLOCKED";

  if (auth !== "PASS") {
    error_code = "MI_AUTH_MISSING";
    error_summary = "mi login required";
    bounded = "BLOCKED";
  } else if (!office) {
    error_code = "MI_OFFICE_MISSING";
    error_summary = "MITOSIS_OFFICE_ID / MI_OFFICE_ID required";
  } else if (agents_listed > 0) {
    // Do not auto-send messages without explicit agent target in this mission.
    status = "BLOCKED";
    error_code = "YAPPY_INTERACTION_NOT_AUTOMATED";
    error_summary =
      "Agents present but bounded computer-use interaction requires explicit operator-approved agent name; not auto-messaged.";
    bounded = "NOT_ATTEMPTED";
  }

  const receipt: MitosisYappyMissionReceipt = {
    schema: "sponsor.yappy.mission_receipt.v1",
    mission_id: "ANB-SP-YAPPY-INTERACT-001",
    provider: "Mitosis Yappy",
    operation: "external_computer_use_interaction",
    identity_note:
      "Mitosis office agents (mi). Not yappy.biz. See eval/.../yappy_biz/ for the public product API probe.",
    docs_ref: "https://mitosislabs.ai/developers/cli/overview",
    auth_state: auth,
    office_id: office,
    agents_listed,
    agent_names: names,
    bounded_interaction: bounded,
    offer_code_metadata: "FREEYAPPY",
    offer_is_api_credential: false,
    fcg_append: "NOT_APPENDED",
    status,
    error_code,
    error_summary,
    claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
    secret_state: auth === "PASS" ? "PRESENT" : "BLOCKED",
    signature_state: "NOT_SIGNED",
    recorded_at_utc,
  };

  writeFileSync(
    path.join(outDir, "YAPPY_MISSION_RECEIPT.json"),
    JSON.stringify(receipt, null, 2) + "\n",
  );
  return receipt;
}
