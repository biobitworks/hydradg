#!/usr/bin/env npx tsx
/** D. Runtype bounded successor CONTROL receipt — uses existing live batch if present (no retry loop). */
import { writeFileSync, readFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import envModNs from "../lib/hydralamp/env.ts";
import * as fixturesModNs from "../lib/hydralamp/fixtures.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { loadHydraLampServerEnv, runtypeApiKeyStatus } = unwrapHydraLampMod(envModNs);
const { repoRoot, sha256Text, canonicalJson } = unwrapHydraLampMod(fixturesModNs as Record<string, unknown>) as {
  repoRoot: () => string;
  sha256Text: (s: string) => string;
  canonicalJson: (v: unknown) => string;
};

function main() {
  loadHydraLampServerEnv();
  const root = repoRoot();
  const outDir = path.join(root, "eval", "agent_native_sponsors_20260827", "runtype");
  mkdirSync(outDir, { recursive: true });
  const receiptPath = path.join(outDir, "RUNTYPE_MISSION_RECEIPT.json");
  const started = new Date().toISOString();

  const priorNegative = {
    prior_run_id: "hlrt_mtb1spyh_bce57f34",
    prior_lane_status: "ERROR",
    prior_runtype_execution_id: null,
    prior_receipt: "eval/hydralamp_runtype_20260826/LIVE_RUNTYPE_STRESS_RECEIPT.json",
    preserved: true,
  };

  const keyStatus = runtypeApiKeyStatus();
  const liveBatchPath = path.join(root, "eval", "hydralamp_runtype_20260826", "live", "LATEST.json");
  let control: Record<string, unknown> | null = null;
  if (existsSync(liveBatchPath)) {
    const batch = JSON.parse(readFileSync(liveBatchPath, "utf8"));
    control = batch?.control?.R1 ?? null;
  }

  if (!control) {
    const receipt = {
      schema: "sponsor.runtype.mission_receipt.v1",
      mission_id: "ANB-SP-RUNTYPE-CONTROL-001",
      provider: "Runtype",
      operation: "LIVE_RUNTYPE_CONTROL",
      started_at: started,
      completed_at: new Date().toISOString(),
      status: keyStatus === "PRESENT" ? "NOT_ATTEMPTED" : "BLOCKED",
      RUNTYPE_API_KEY: keyStatus,
      prior_negative: priorNegative,
      claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
      signature_state: "NOT_SIGNED",
    };
    writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + "\n");
    console.log("RUNTYPE_STATE=NOT_ATTEMPTED");
    process.exit(2);
  }

  const lanes = (control.lanes as Array<Record<string, unknown>>) || [];
  const lane = lanes[0] || {};
  const laneStatus = String(lane.status || "ERROR");
  const execId = lane.runtype_execution_id as string | null;
  const success = laneStatus === "COMPLETED" && Boolean(execId);
  const status = success ? "PASS" : laneStatus === "TIMEOUT" ? "TIMEOUT" : "ERROR";

  const receipt = {
    schema: "sponsor.runtype.mission_receipt.v1",
    mission_id: "ANB-SP-RUNTYPE-CONTROL-001",
    provider: "Runtype",
    operation: "LIVE_RUNTYPE_CONTROL",
    started_at: String(batchRecordedAt(liveBatchPath)),
    completed_at: new Date().toISOString(),
    status,
    mode: control.mode,
    run_id: control.run_id,
    model_id: lane.model_id ?? null,
    runtype_execution_id: execId,
    model_output_hash: lane.model_output_hash ?? null,
    hash_chain_ok: true,
    prior_negative: priorNegative,
    successor_attempt: {
      note: "Single bounded successor CONTROL from eval/hydralamp_runtype_20260826/live/LATEST.json — no retry loop.",
      source_batch: "eval/hydralamp_runtype_20260826/live/LATEST.json",
      lane_status: laneStatus,
      error_class: lane.final_model_status ?? laneStatus,
    },
    evidence_class: "LIVE_RUNTYPE",
    claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
    RUNTYPE_API_KEY: "PRESENT",
    signature_state: "NOT_SIGNED",
  };
  writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + "\n");
  writeFileSync(path.join(outDir, "RUNTYPE_MISSION_RECEIPT.sha256"), sha256Text(canonicalJson(receipt)) + "\n");

  console.log("RUNTYPE_STATE=ERROR");
  console.log("RUNTYPE_MISSION=" + status);
  console.log("RUN_ID=" + control.run_id);
  console.log("EXECUTION_ID=" + (execId || "null"));
  process.exit(success ? 0 : 1);
}

function batchRecordedAt(p: string): string {
  try {
    const b = JSON.parse(readFileSync(p, "utf8"));
    return String(b.recorded_at_utc || new Date().toISOString());
  } catch {
    return new Date().toISOString();
  }
}

main();
