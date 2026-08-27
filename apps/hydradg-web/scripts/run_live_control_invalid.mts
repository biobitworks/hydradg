/**
 * Live CONTROL + INVALID_PROOF runner (R1; optional R2/R3 via env).
 * Requires RUNTYPE_API_KEY and frozen MODEL_INVENTORY with selected_models.
 * Never falls back to synthetic inside LIVE_RUNTYPE.
 */
import { writeFileSync, mkdirSync, readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { loadHydraLampServerEnv, runtypeApiKeyStatus } from "../lib/hydralamp/env.ts";
import { startHydraLampExperiment } from "../lib/hydralamp/coordinator.ts";
import { getRun, subscribe } from "../lib/hydralamp/store.ts";
import { repoRoot } from "../lib/hydralamp/fixtures.ts";
import type { PerturbationKind } from "../lib/hydralamp/types.ts";

async function waitDone(runId: string, timeoutMs = 120_000) {
  return new Promise<void>((resolve, reject) => {
    const unsub = subscribe(runId, () => {});
    const t = setInterval(() => {
      const r = getRun(runId);
      if (r?.done) {
        clearInterval(t);
        unsub();
        resolve();
      }
    }, 100);
    setTimeout(() => {
      clearInterval(t);
      unsub();
      reject(new Error("WAIT_TIMEOUT"));
    }, timeoutMs);
  });
}

async function runOnce(perturbation: PerturbationKind, replicate: string) {
  const run = await startHydraLampExperiment({
    perturbation,
    demo_20s: false,
    allow_synthetic_ui_fixture: false,
  });
  if (run.mode !== "LIVE_RUNTYPE") {
    throw new Error(`EXPECTED_LIVE_GOT_${run.mode}`);
  }
  await waitDone(run.run_id);
  const final = getRun(run.run_id)!;
  const summary = {
    replicate,
    perturbation,
    run_id: final.run_id,
    mode: final.mode,
    lanes: final.lanes.map((l) => ({
      lane: l.lane,
      model_id: l.model_id,
      runtype_execution_id: l.runtype_execution_id,
      status: l.status,
      decision: l.structured?.decision ?? null,
      proof_state: l.structured?.proof_state ?? null,
      prompt_hash: l.prompt_hash ?? null,
      model_output_hash: l.raw_output_sha256,
      tool_calls: l.tool_sequence,
      tool_results_hashes: l.tool_results_hashes ?? [],
      latency_ms: l.latency_ms,
      fallback_used: l.fallback_used === true ? true : false,
      final_model_status: l.final_model_status ?? l.status,
    })),
    earliest_divergence: final.earliest_divergence_expected,
    verifier: final.verifier,
    fcg: final.fcg,
    hydradb: final.hydradb,
    unauthorized_canonical_writes:
      (final.verifier as { unauthorized_canonical_writes?: number })?.unauthorized_canonical_writes ?? null,
  };
  return summary;
}

async function main() {
  loadHydraLampServerEnv();
  if (runtypeApiKeyStatus() !== "PRESENT") {
    console.log("RUNTYPE_API_KEY=MISSING");
    console.log("LIVE_RUN=BLOCKED");
    process.exit(2);
  }
  const invPath = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "MODEL_INVENTORY.json");
  if (!existsSync(invPath)) {
    console.log("MODEL_INVENTORY=MISSING — run discover_runtype_inventory.mts first");
    process.exit(3);
  }
  const inv = JSON.parse(readFileSync(invPath, "utf8"));
  if (!inv.selected_models?.length) {
    console.log("MODEL_INVENTORY_EMPTY");
    process.exit(3);
  }
  console.log("RUNTYPE_API_KEY=PRESENT");
  console.log(
    "MODELS",
    inv.selected_models.map((m: { model_id: string }) => m.model_id).join(","),
  );

  const replicates = (process.env.HYDRALAMP_REPLICATES || "R1").split(",").map((s) => s.trim());
  const outDir = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "live");
  mkdirSync(outDir, { recursive: true });

  const results: Record<string, unknown> = {
    schema: "hydralamp.runtype.live_batch.v1",
    recorded_at_utc: new Date().toISOString(),
    inventory_path: "eval/hydralamp_runtype_20260826/MODEL_INVENTORY.json",
    replicates,
    control: {},
    invalid_proof: {},
  };

  for (const rep of replicates) {
    console.log("START", rep, "CONTROL");
    results.control = {
      ...(results.control as object),
      [rep]: await runOnce("CONTROL", rep),
    };
    console.log("START", rep, "INVALID_PROOF");
    results.invalid_proof = {
      ...(results.invalid_proof as object),
      [rep]: await runOnce("INVALID_PROOF", rep),
    };
  }

  const out = path.join(outDir, `LIVE_BATCH_${Date.now()}.json`);
  writeFileSync(out, JSON.stringify(results, null, 2) + "\n");
  writeFileSync(path.join(outDir, "LATEST.json"), JSON.stringify(results, null, 2) + "\n");
  console.log("LIVE_BATCH_WRITTEN", out);
}

void main().catch((e) => {
  console.log("LIVE_RUN_ERROR", String((e as Error).message || e).slice(0, 200));
  process.exit(1);
});
