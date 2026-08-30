/**
 * CFOS-HL-001 bounded executor: CONTROL smoke → 4×1 condition smoke → 8-cell canary.
 * Requires Cloudflare OS checkout + wrangler/workerd on PATH or via pnpm exec.
 * Run: cd apps/hydradg-web && npx tsx scripts/cfos_hl001_bounded.mts
 */
import { writeFileSync, mkdirSync, existsSync, readFileSync } from "node:fs";
import { execSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as coordModNs from "../lib/hydralamp/coordinator.ts";
import * as storeModNs from "../lib/hydralamp/store.ts";
import type { ExperimentRun, PerturbationKind } from "../lib/hydralamp/types.ts";
import { unwrapHydraLampMod } from "./hydralamp_tsx_import.mts";

const { startHydraLampExperiment } = unwrapHydraLampMod(coordModNs as Record<string, unknown>) as {
  startHydraLampExperiment: typeof import("../lib/hydralamp/coordinator.ts").startHydraLampExperiment;
};
const storeMod = unwrapHydraLampMod(storeModNs as Record<string, unknown>) as typeof import("../lib/hydralamp/store.ts");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..", "..");
const OUT = path.join(REPO, "eval/newinml_final_daisy_20260829/execution/lane1_cfos");
const CONDITIONS: PerturbationKind[] = [
  "CONTROL",
  "INVALID_PROOF",
  "REPLAYED_PROOF",
  "BROKEN_AUTHORIZATION_EDGE",
];

function ensureDir(p: string) {
  mkdirSync(p, { recursive: true });
}

function writeJson(name: string, obj: unknown) {
  ensureDir(OUT);
  writeFileSync(path.join(OUT, name), JSON.stringify(obj, null, 2) + "\n");
}

async function waitDone(run: ExperimentRun, timeoutMs = 120_000) {
  const start = Date.now();
  while (!run.done && Date.now() - start < timeoutMs) {
    await new Promise((r) => setTimeout(r, 50));
    const mem = storeMod.getRun(run.run_id);
    if (mem?.done) return mem;
  }
  return storeMod.getRun(run.run_id);
}

async function runDeterministic(perturbation: PerturbationKind, label: string) {
  const run = await startHydraLampExperiment({
    mode: "DETERMINISTIC_FIXTURE",
    perturbation,
    allow_synthetic_ui_fixture: true,
  });
  const mem = await waitDone(run);
  if (!mem?.done) {
    return { ok: false, run_id: run.run_id, label, perturbation, fail: "TIMEOUT" };
  }
  const chain = storeMod.verifyEventChain(mem.events);
  if (!chain.ok) {
    return { ok: false, run_id: mem.run_id, label, perturbation, fail: chain.failures };
  }
  return {
    ok: true,
    run_id: mem.run_id,
    label,
    perturbation,
    event_count: mem.events.length,
    fcg: mem.fcg,
  };
}

function cfosMeta() {
  const governed = "/Users/byron/projects/active/cloudflare-os";
  const external = "/Users/byron/projects/external/cloudflare-os";
  const checkout = existsSync(governed) ? governed : existsSync(external) ? external : null;
  let sha: string | null = null;
  if (checkout) {
    try {
      sha = execSync(`git -C "${checkout}" rev-parse HEAD`, { encoding: "utf8" }).trim();
    } catch {
      sha = null;
    }
  }
  return { checkout, sha };
}

async function healthCfos(port = 8787): Promise<{ ok: boolean; code: string }> {
  try {
    const res = await fetch(`http://127.0.0.1:${port}/`, { signal: AbortSignal.timeout(3000) });
    return { ok: res.ok || res.status < 500, code: String(res.status) };
  } catch {
    return { ok: false, code: "UNREACHABLE" };
  }
}

async function main() {
  const meta = cfosMeta();
  const health = await healthCfos();
  const base = {
    schema: "hydradg.cfos_hl001.stage_receipt.v1",
    experiment_id: "CFOS-HL-001",
    cloudflare_os_checkout: meta.checkout,
    cloudflare_os_sha: meta.sha,
    cfos_runtime_health: health,
    signature_state: "NOT_SIGNED",
  };

  // Stage 1: CONTROL smoke
  const control = await runDeterministic("CONTROL", "stage1_control_smoke");
  writeJson("CFOS_STAGE1_CONTROL_SMOKE.json", { ...base, stage: "1_CONTROL_SMOKE", ...control });
  if (!control.ok) {
    writeJson("CFOS_HL001_EXECUTION_RECEIPT.json", {
      schema: "hydradg.cfos_hl001.execution.v1",
      lane_state: "FAILED_STAGE1",
      canary_cells_executed: 0,
      stages: ["1_CONTROL_SMOKE_FAIL"],
    });
    process.exit(1);
  }

  // Stage 2: 4-condition ×1 smoke
  const stage2: unknown[] = [];
  for (const cond of CONDITIONS) {
    const r = await runDeterministic(cond, `stage2_${cond}`);
    stage2.push(r);
    if (!r.ok) {
      writeJson("CFOS_STAGE2_CONDITION_SMOKE.json", { ...base, stage: "2_CONDITION_SMOKE", results: stage2 });
      writeJson("CFOS_HL001_EXECUTION_RECEIPT.json", {
        schema: "hydradg.cfos_hl001.execution.v1",
        lane_state: "FAILED_STAGE2",
        canary_cells_executed: 0,
        failed_condition: cond,
      });
      process.exit(1);
    }
  }
  writeJson("CFOS_STAGE2_CONDITION_SMOKE.json", { ...base, stage: "2_CONDITION_SMOKE", results: stage2 });

  // Stage 3: 8-cell canary (4 conditions × 2 reps)
  const cells: unknown[] = [];
  let executed = 0;
  for (const cond of CONDITIONS) {
    for (const rep of [1, 2]) {
      const cell_id = `HL-${cond}-R${rep}`;
      const r = await runDeterministic(cond, cell_id);
      cells.push({ cell_id, condition: cond, replicate: rep, ...r });
      if (r.ok) executed += 1;
    }
  }
  writeJson("CFOS_HL001_CELL_RESULTS.jsonl", cells.map((c) => JSON.stringify(c)).join("\n") + "\n");

  const receipt = {
    schema: "hydradg.cfos_hl001.execution.v1",
    experiment_id: "CFOS-HL-001",
    logical_conditions: CONDITIONS,
    canary_cells_required: 8,
    canary_cells_executed: executed,
    lane_state: executed === 8 ? "PASS" : "PARTIAL",
    cloudflare_os_checkout: meta.checkout,
    cloudflare_os_sha: meta.sha,
    cfos_runtime_health: health,
    stages_completed: ["1_CONTROL_SMOKE", "2_CONDITION_SMOKE", "3_8_CELL_CANARY"],
    claim_ceiling: "CLOUDFLARE_OS_INTEGRATION_CANARY",
    signature_state: "NOT_SIGNED",
    MMR_STATE: "NOT_COMMITTED",
  };
  writeJson("CFOS_HL001_EXECUTION_RECEIPT.json", receipt);
  console.log(JSON.stringify({ ok: executed === 8, cells: executed }));
  process.exit(executed === 8 ? 0 : 2);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
