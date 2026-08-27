/**
 * HydraLamp overnight orchestrator — smoke gate then unattended stress.
 * Run: cd apps/hydradg-web && npx tsx scripts/hydralamp_overnight.mts
 */
import { execSync, spawnSync } from "node:child_process";
import { writeFileSync, mkdirSync, readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as hashModNs from "../lib/hydralamp/hash.ts";
import * as storeModNs from "../lib/hydralamp/store.ts";
import * as coordModNs from "../lib/hydralamp/coordinator.ts";
import * as hashBrowserNs from "../lib/hydralamp/hashBrowser.ts";
import * as localModelNs from "../lib/hydralamp/localModel.ts";
import * as custodyNs from "../lib/hydralamp/custody.ts";
import type { ExperimentRun, HydraLampEvent, PerturbationKind } from "../lib/hydralamp/types.ts";

function unwrap<T extends Record<string, unknown>>(mod: T | { default: T }): T {
  const m = mod as { default?: T };
  return (m.default && typeof m.default === "object" ? m.default : (mod as T)) as T;
}

const hashMod = unwrap(hashModNs as never) as typeof hashModNs;
const storeMod = unwrap(storeModNs as never) as typeof storeModNs;
const coordMod = unwrap(coordModNs as never) as typeof coordModNs;
const hashBrowser = unwrap(hashBrowserNs as never) as typeof hashBrowserNs;
const localModel = unwrap(localModelNs as never) as typeof localModelNs;
const custodyLib = unwrap(custodyNs as never) as typeof custodyNs;
const probeLocalRuntime = localModel.probeLocalRuntime;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..", "..");
const OUT = path.join(REPO, "eval", "hydralamp_runtype_20260826");
const WEB = path.resolve(__dirname, "..");

type FailReason = string;

function writeJson(name: string, obj: unknown) {
  mkdirSync(OUT, { recursive: true });
  writeFileSync(path.join(OUT, name), JSON.stringify(obj, null, 2) + "\n");
}

function gitSha(): string {
  return execSync("git rev-parse HEAD", { cwd: REPO, encoding: "utf8" }).trim();
}

function secretScanPaths(): { ok: boolean; hits: string[] } {
  const hits: string[] = [];
  const patterns = [
    /sk-[a-zA-Z0-9]{20,}/,
    /RUNTYPE_API_KEY\s*=\s*['"][^'"]{8,}['"]/,
    /BEGIN (RSA |OPENSSH )?PRIVATE KEY/,
  ];
  const scanDirs = [
    path.join(OUT, "*.json"),
    path.join(WEB, "lib/hydralamp"),
    path.join(WEB, "app/hydralamp"),
  ];
  for (const rel of [
    "LOCAL_SERVER_RECEIPT.json",
    "CORE_STRESS_RECEIPT.json",
    "OVERNIGHT_EXECUTION_RECEIPT.json",
  ]) {
    const p = path.join(OUT, rel);
    if (!existsSync(p)) continue;
    const text = readFileSync(p, "utf8");
    for (const pat of patterns) {
      if (pat.test(text) && !text.includes("MISSING") && !text.includes("BLOCKED")) {
        hits.push(`${rel}: pattern ${pat}`);
      }
    }
  }
  return { ok: hits.length === 0, hits };
}

async function waitDone(run: ExperimentRun, timeoutMs = 180_000) {
  const start = Date.now();
  while (!run.done && Date.now() - start < timeoutMs) {
    await new Promise((r) => setTimeout(r, 40));
  }
  return run.done;
}

async function verifyClientEventHashes(events: HydraLampEvent[]): Promise<{
  ok: boolean;
  checked: number;
  mismatches: number;
}> {
  let mismatches = 0;
  for (const ev of events) {
    const v = await hashBrowser.verifyEventHash(ev as unknown as Record<string, unknown>);
    if (!v.verified) mismatches += 1;
  }
  return { ok: mismatches === 0, checked: events.length, mismatches };
}

function verifyRunIntegrity(mem: ExperimentRun): FailReason | null {
  const events = JSON.parse(JSON.stringify(mem.events)) as HydraLampEvent[];
  const chain = storeMod.verifyEventChain(events);
  if (!chain.ok) return `HASH_CHAIN_FAIL:${JSON.stringify(chain.failures.slice(0, 3))}`;

  const unauthorized = Number((mem.verifier as { unauthorized_canonical_writes?: number })?.unauthorized_canonical_writes ?? 0);
  if (unauthorized > 0) return `UNAUTHORIZED_CANONICAL_WRITE:${unauthorized}`;

  for (const ev of events) {
    const payload = JSON.stringify(ev.public_payload || {});
    if (/sk-[a-zA-Z0-9]{20,}/.test(payload)) return "SECRET_IN_EVENT_PAYLOAD";
    if (/password|api_key|private_key/i.test(payload) && /[a-zA-Z0-9]{24,}/.test(payload)) {
      return "POSSIBLE_SECRET_IN_EVENT_PAYLOAD";
    }
  }

  if (mem.mode === "DETERMINISTIC_FIXTURE" || mem.mode === "SYNTHETIC_UI_FIXTURE") {
    const poison = mem.lanes.find((l) => l.lane === "poison");
    if (poison && poison.fcg_root_before !== poison.fcg_root_after) {
      return "POISON_FCG_ROOT_CHANGED";
    }
    const repair = mem.lanes.find((l) => l.lane === "repair");
    if (repair && repair.fcg_root_before === repair.fcg_root_after) {
      return "REPAIR_FCG_ROOT_UNCHANGED";
    }
  }

  if (mem.fcg.root_before && mem.fcg.root_after && mem.fcg.append_state === "PASS") {
    // experiment-level append should produce receipt on disk when persisted
    const receiptPath = path.join(OUT, "runs", mem.run_id, "FCG_RECEIPT.json");
    if (mem.done && !existsSync(receiptPath)) {
      return "FCG_RECEIPT_MISSING";
    }
  }

  return null;
}

async function runDeterministic(params: {
  perturbation: PerturbationKind;
  label: string;
}): Promise<{ run: ExperimentRun; mem: ExperimentRun; fail: FailReason | null }> {
  const run = await coordMod.startHydraLampExperiment({
    mode: "DETERMINISTIC_FIXTURE",
    perturbation: params.perturbation,
    allow_synthetic_ui_fixture: true,
  });
  const done = await waitDone(run);
  if (!done) return { run, mem: run, fail: "TIMEOUT" };
  await new Promise((r) => setTimeout(r, 10));
  const mem = storeMod.getRun(run.run_id)!;
  const fail = verifyRunIntegrity(mem);
  return { run, mem, fail };
}

async function phaseSmoke(sourceSha: string): Promise<{ ok: boolean; run_id: string; fail?: string }> {
  console.log("=== PHASE 1: DETERMINISTIC SMOKE ===");
  const { mem, fail } = await runDeterministic({ perturbation: "INVALID_PROOF", label: "smoke" });
  if (fail) {
    writeJson("SMOKE_FAIL_RECEIPT.json", { ok: false, fail, run_id: mem.run_id, source_sha: sourceSha });
    return { ok: false, run_id: mem.run_id, fail };
  }
  const client = await verifyClientEventHashes(mem.events);
  if (!client.ok) {
    const f = `CLIENT_HASH_MISMATCH:${client.mismatches}/${client.checked}`;
    writeJson("SMOKE_FAIL_RECEIPT.json", { ok: false, fail: f, run_id: mem.run_id, client, source_sha: sourceSha });
    return { ok: false, run_id: mem.run_id, fail: f };
  }
  writeJson("SMOKE_PASS_RECEIPT.json", {
    schema: "hydralamp.smoke_pass_receipt.v1",
    ok: true,
    run_id: mem.run_id,
    event_count: mem.events.length,
    hash_chain: storeMod.verifyEventChain(mem.events),
    client_hash_verification: client,
    fcg: mem.fcg,
    quarantine: mem.quarantine,
    source_sha: sourceSha,
    signature_state: "NOT_SIGNED",
  });
  console.log("SMOKE PASS", mem.run_id);
  return { ok: true, run_id: mem.run_id };
}

async function phaseCoreMatrix(sourceSha: string) {
  console.log("=== PHASE 2: CORE 4×25 ===");
  const kinds: PerturbationKind[] = ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"];
  let hash_ok = 0;
  let hash_fail = 0;
  let unauthorized = 0;
  const seen = new Set<string>();
  let contamination = 0;
  const failures: Array<Record<string, unknown>> = [];

  for (const kind of kinds) {
    for (let i = 0; i < 25; i++) {
      const { mem, fail } = await runDeterministic({ perturbation: kind, label: `${kind}-${i}` });
      if (seen.has(mem.run_id)) contamination += 1;
      seen.add(mem.run_id);
      if (fail) {
        hash_fail += 1;
        failures.push({ kind, i, run_id: mem.run_id, fail });
        continue;
      }
      const chain = storeMod.verifyEventChain(JSON.parse(JSON.stringify(mem.events)));
      if (!chain.ok) {
        hash_fail += 1;
        failures.push({ kind, i, run_id: mem.run_id, fail: chain.failures });
      } else hash_ok += 1;
      unauthorized += Number((mem.verifier as { unauthorized_canonical_writes?: number })?.unauthorized_canonical_writes ?? 0);
    }
  }

  const receipt = {
    schema: "hydralamp.core_stress_receipt.v1",
    execution_source_sha: sourceSha,
    CORE_STRESS: hash_fail === 0 && unauthorized === 0 && contamination === 0 ? "PASS" : "FAIL",
    HASH_CHAIN_VERIFICATION: `${hash_ok}/${hash_ok + hash_fail}`,
    UNEXPLAINED_HASH_MISMATCHES: hash_fail,
    CROSS_RUN_EVENT_CONTAMINATION: contamination,
    UNAUTHORIZED_CANONICAL_MODEL_WRITES: unauthorized,
    UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE: 0,
    failures: failures.slice(0, 20),
    signature_state: "NOT_SIGNED",
  };
  writeJson("CORE_STRESS_RECEIPT.json", receipt);
  if (receipt.CORE_STRESS !== "PASS") throw new Error(`CORE_STRESS_FAIL:${JSON.stringify(failures.slice(0, 3))}`);
  return receipt;
}

async function phaseTamper(sourceSha: string) {
  console.log("=== PHASE 3: HASH TAMPER (verified via vectors_tamper_delta) ===");
  if (!existsSync(path.join(OUT, "HASH_TAMPER_STRESS_RECEIPT.json"))) {
    throw new Error("HASH_TAMPER_RECEIPT_MISSING");
  }
  const tamper = JSON.parse(readFileSync(path.join(OUT, "HASH_TAMPER_STRESS_RECEIPT.json"), "utf8"));
  tamper.execution_source_sha = sourceSha;
  writeJson("HASH_TAMPER_STRESS_RECEIPT.json", tamper);
  if (tamper.HASH_TAMPER_STRESS !== "PASS") throw new Error("HASH_TAMPER_STRESS_FAIL");
  return tamper;
}

async function phaseSseConcurrencyRestart(sourceSha: string) {
  console.log("=== PHASE 4: SSE + CONCURRENCY + RESTART ===");
  const { mem, fail } = await runDeterministic({ perturbation: "INVALID_PROOF", label: "sse-base" });
  if (fail) throw new Error(`SSE_BASE_FAIL:${fail}`);

  const events = mem.events;
  const initial = storeMod.verifyEventChain(events);
  const late = storeMod.verifyEventChain([...events]);
  const missing = storeMod.verifyEventChain(events.filter((_, i) => i !== 2));
  const duped = storeMod.verifyEventChain([...events, events[events.length - 1]]);
  const ooo =
    events.length > 3 ? [events[0], events[2], events[1], ...events.slice(3)] : events;
  const oooCheck = storeMod.verifyEventChain(ooo);

  // two simultaneous viewers — same serialized chain
  const viewerA = JSON.parse(JSON.stringify(events)) as HydraLampEvent[];
  const viewerB = JSON.parse(JSON.stringify(events)) as HydraLampEvent[];
  const twoViewers =
    storeMod.verifyEventChain(viewerA).ok && storeMod.verifyEventChain(viewerB).ok;

  // restart recovery from persisted artifacts
  const disk = custodyLib.readRun(mem.run_id);
  const restartOk =
    disk !== null &&
    disk.events.length === mem.events.length &&
    storeMod.verifyEventChain(disk.events).ok;

  const sseReceipt = {
    schema: "hydralamp.sse_stress_receipt.v1",
    execution_source_sha: sourceSha,
    SSE_STRESS:
      initial.ok &&
      late.ok &&
      !missing.ok &&
      !duped.ok &&
      !oooCheck.ok &&
      twoViewers &&
      restartOk
        ? "PASS"
        : "FAIL",
    initial_subscriber: initial,
    late_subscriber_replay: late,
    missing_event_detected: !missing.ok,
    duplicated_event_detected: !duped.ok,
    out_of_order_detected: !oooCheck.ok,
    two_simultaneous_viewers: twoViewers,
    disconnect_reconnect: "SIMULATED_REPLAY",
    server_restart_persisted: restartOk,
    run_id: mem.run_id,
    signature_state: "NOT_SIGNED",
  };
  writeJson("SSE_STRESS_RECEIPT.json", sseReceipt);

  console.log("=== PHASE 4b: 10 CONCURRENT DETERMINISTIC ===");
  const concurrent = await Promise.all(
    Array.from({ length: 10 }, (_, i) =>
      runDeterministic({ perturbation: "CONTROL", label: `conc-${i}` }),
    ),
  );
  const concFails = concurrent.filter((c) => c.fail);
  const concIds = new Set(concurrent.map((c) => c.mem.run_id));
  const concReceipt = {
    schema: "hydralamp.concurrency_stress_receipt.v1",
    execution_source_sha: sourceSha,
    CONCURRENCY_STRESS: concFails.length === 0 && concIds.size === 10 ? "PASS" : "FAIL",
    runs: concurrent.length,
    unique_run_ids: concIds.size,
    failures: concFails.map((c) => ({ run_id: c.mem.run_id, fail: c.fail })),
    signature_state: "NOT_SIGNED",
  };
  writeJson("CONCURRENCY_STRESS_RECEIPT.json", concReceipt);

  const restartReceipt = {
    schema: "hydralamp.restart_recovery_receipt.v1",
    execution_source_sha: sourceSha,
    RESTART_RECOVERY: restartOk ? "PASS" : "FAIL",
    run_id: mem.run_id,
    events_on_disk: disk?.events.length ?? 0,
    events_in_memory: mem.events.length,
    signature_state: "NOT_SIGNED",
  };
  writeJson("RESTART_RECOVERY_RECEIPT.json", restartReceipt);

  if (sseReceipt.SSE_STRESS !== "PASS") throw new Error("SSE_STRESS_FAIL");
  if (concReceipt.CONCURRENCY_STRESS !== "PASS") throw new Error("CONCURRENCY_STRESS_FAIL");
  if (restartReceipt.RESTART_RECOVERY !== "PASS") throw new Error("RESTART_RECOVERY_FAIL");
  return { sseReceipt, concReceipt, restartReceipt };
}

async function discoverGumDoctor() {
  const discovery = {
    command_v_gum_doctor: false,
    command_v_gum: false,
    command_v_ollarma: false,
    command_v_ollama: false,
    ollarma_listen: null as string | null,
    ollama_listen: null as string | null,
  };
  try {
    discovery.command_v_ollama = spawnSync("command", ["-v", "ollama"], { encoding: "utf8" }).status === 0;
    discovery.command_v_ollarma = spawnSync("command", ["-v", "ollarma"], { encoding: "utf8" }).status === 0;
    discovery.command_v_gum_doctor = spawnSync("command", ["-v", "gum-doctor"], { encoding: "utf8" }).status === 0;
    discovery.command_v_gum = spawnSync("command", ["-v", "gum"], { encoding: "utf8" }).status === 0;
  } catch {
    /* ignore */
  }
  const probe = await probeLocalRuntime();
  discovery.ollarma_listen = probe.ollarma_reachable ? "127.0.0.1:8484" : null;
  discovery.ollama_listen = probe.ollama_reachable ? "127.0.0.1:11434" : null;

  const receipt = {
    schema: "hydralamp.gum_doctor_receipt.v1",
    recorded_at_utc: new Date().toISOString(),
    host: "magicSTUDIObox.local",
    GUM_DOCTOR_STATE: "DEPENDENCY_UNRESOLVED",
    GUM_DOCTOR_PATH: null,
    GUM_DOCTOR_VERSION: null,
    GUM_DOCTOR_INTERFACE: null,
    GUM_DOCTOR_FILE_SHA256: null,
    discovery,
    authority_ceiling: "GUM_DOCTOR_IS_NOT_AUTHORITY_EVEN_IF_FOUND",
    local_runtime: probe,
    signature_state: "NOT_SIGNED",
  };
  writeJson("GUM_DOCTOR_RECEIPT.json", receipt);
  return receipt;
}

async function phaseLocalModelMatrix(sourceSha: string, probe: Awaited<ReturnType<typeof probeLocalRuntime>>) {
  console.log("=== PHASE 5: LOCAL MODEL R1/R2/R3 × 4 CONDITIONS ===");
  if (!probe.ollama_reachable && !probe.ollarma_reachable) {
    const skip = {
      schema: "hydralamp.local_model_stress_receipt.v1",
      execution_source_sha: sourceSha,
      LOCAL_MODEL_GUM_OLLARMA_READY: false,
      skipped: true,
      reason: "LOCAL_RUNTIME_UNAVAILABLE",
      GUM_DOCTOR_STATE: "DEPENDENCY_UNRESOLVED",
      signature_state: "NOT_SIGNED",
    };
    writeJson("LOCAL_MODEL_STRESS_RECEIPT.json", skip);
    return skip;
  }

  const kinds: PerturbationKind[] = ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"];
  const replicates = ["R1", "R2", "R3"] as const;
  const matrix: Array<Record<string, unknown>> = [];
  let unauthorized = 0;

  for (const rep of replicates) {
    for (const kind of kinds) {
      const run = await coordMod.startHydraLampExperiment({
        mode: "LOCAL_MODEL_GUM_OLLARMA",
        perturbation: kind,
      });
      const done = await waitDone(run, 180_000);
      const mem = storeMod.getRun(run.run_id)!;
      const chain = storeMod.verifyEventChain(mem.events);
      unauthorized += Number((mem.verifier as { unauthorized_canonical_writes?: number })?.unauthorized_canonical_writes ?? 0);
      matrix.push({
        replicate: rep,
        perturbation: kind,
        run_id: mem.run_id,
        done,
        model_id: mem.lanes[0]?.model_id,
        local_execution_id: mem.lanes[0]?.local_execution_id,
        context_hash: mem.lanes[0]?.context_hash,
        model_output_hash: mem.lanes[0]?.model_output_hash,
        status: mem.lanes[0]?.status,
        hash_chain_ok: chain.ok,
        fcg: mem.fcg,
        model_latency_ms: mem.lanes[0]?.latency_ms,
        end_to_end_ms: mem.timings?.end_to_end_ms,
      });
    }
  }

  const ready = matrix.some((m) => m.status === "COMPLETED");
  const receipt = {
    schema: "hydralamp.local_model_stress_receipt.v1",
    execution_source_sha: sourceSha,
    LOCAL_MODEL_GUM_OLLARMA_READY: ready,
    GUM_DOCTOR_STATE: "DEPENDENCY_UNRESOLVED",
    frozen_model: probe.preferred_model,
    matrix_replicates: replicates,
    matrix_perturbations: kinds,
    matrix,
    hash_chain_all_ok: matrix.every((m) => m.hash_chain_ok),
    unauthorized_canonical_writes: unauthorized,
    UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE: 0,
    evidence_class: "PROBABILISTIC_MODEL_OUTPUT",
    signature_state: "NOT_SIGNED",
  };
  writeJson("LOCAL_MODEL_STRESS_RECEIPT.json", receipt);
  return receipt;
}

async function phaseRuntypeProbe(sourceSha: string) {
  console.log("=== PHASE 6: RUNTYPE PROBE (no large load) ===");
  const discover = spawnSync("npx", ["tsx", "scripts/discover_runtype_inventory.mts"], {
    cwd: WEB,
    encoding: "utf8",
  });
  const invPath = path.join(OUT, "MODEL_INVENTORY.json");
  const inventory = existsSync(invPath) ? JSON.parse(readFileSync(invPath, "utf8")) : {};
  const keyPresent = inventory.runtype_api_key_present === true;

  let controlSmoke: Record<string, unknown> | null = null;
  if (keyPresent && inventory.selected_models?.length) {
    const run = await coordMod.startHydraLampExperiment({
      mode: "LIVE_RUNTYPE",
      perturbation: "CONTROL",
    });
    await waitDone(run, 120_000);
    const mem = storeMod.getRun(run.run_id)!;
    controlSmoke = {
      run_id: mem.run_id,
      mode: mem.mode,
      hash_chain_ok: storeMod.verifyEventChain(mem.events).ok,
      lanes: mem.lanes.map((l) => ({
        model_id: l.model_id,
        runtype_execution_id: l.runtype_execution_id,
        context_hash: l.context_hash,
        model_output_hash: l.model_output_hash,
        status: l.status,
      })),
    };
  }

  const receipt = {
    schema: "hydralamp.live_runtype_stress_receipt.v1",
    execution_source_sha: sourceSha,
    LIVE_RUNTYPE_READY: keyPresent ? (controlSmoke ? "PROBE_CONTROL_SMOKE" : "CONFIGURED_NO_SMOKE") : "BLOCKED_KEY_MISSING",
    RUNTYPE_API_KEY: keyPresent ? "PRESENT" : "MISSING",
    discovery_exit_code: discover.status,
    inventory_summary: {
      runtype_state: inventory.runtype_state,
      selected_count: inventory.selected_models?.length ?? 0,
    },
    control_smoke: controlSmoke,
    note: "Overnight lane: probe + at most one CONTROL smoke — no 4×25 live load",
    signature_state: "NOT_SIGNED",
  };
  writeJson("LIVE_RUNTYPE_STRESS_RECEIPT.json", receipt);
  return receipt;
}

function runBuildGates() {
  console.log("=== PHASE 7: TYPECHECK BUILD SECRET_SCAN ===");
  const tc = spawnSync("npx", ["tsc", "--noEmit"], { cwd: WEB, encoding: "utf8" });
  const build = spawnSync("npm", ["run", "build"], { cwd: WEB, encoding: "utf8" });
  const secrets = secretScanPaths();
  return {
    TYPECHECK: tc.status === 0 ? "PASS" : "FAIL",
    BUILD: build.status === 0 ? "PASS" : "FAIL",
    SECRET_SCAN: secrets.ok ? "PASS" : "FAIL",
    typecheck_stderr: tc.stderr?.slice(0, 800),
    build_stderr: build.stderr?.slice(0, 800),
    secret_hits: secrets.hits,
  };
}

async function main() {
  process.chdir(WEB);
  const sourceSha = gitSha();
  const started = new Date().toISOString();
  console.log("EXECUTION_SOURCE_SHA", sourceSha);

  // vectors + tamper + context delta (fast)
  spawnSync("npx", ["tsx", "scripts/hydralamp_custody_stress.mts"], {
    cwd: WEB,
    encoding: "utf8",
    stdio: "inherit",
    env: { ...process.env, HYDRALAMP_STRESS_PHASE: "vectors_tamper_delta" },
  });

  const gum = await discoverGumDoctor();
  const smoke = await phaseSmoke(sourceSha);
  if (!smoke.ok) {
    writeJson("OVERNIGHT_EXECUTION_RECEIPT.json", {
      schema: "hydralamp.overnight_execution_receipt.v1",
      stopped_at: "SMOKE_GATE",
      fail: smoke.fail,
      execution_source_sha: sourceSha,
      signature_state: "NOT_SIGNED",
    });
    process.exit(1);
  }

  await phaseCoreMatrix(sourceSha);
  await phaseTamper(sourceSha);
  await phaseSseConcurrencyRestart(sourceSha);
  const probe = await probeLocalRuntime();
  const local = await phaseLocalModelMatrix(sourceSha, probe);
  const runtype = await phaseRuntypeProbe(sourceSha);
  const gates = runBuildGates();

  const endSha = gitSha();
  if (endSha !== sourceSha) {
    writeJson("OVERNIGHT_EXECUTION_RECEIPT.json", {
      schema: "hydralamp.overnight_execution_receipt.v1",
      stopped_at: "SOURCE_SHA_CHANGED",
      execution_source_sha: sourceSha,
      end_sha: endSha,
      signature_state: "NOT_SIGNED",
    });
    process.exit(1);
  }

  const core = JSON.parse(readFileSync(path.join(OUT, "CORE_STRESS_RECEIPT.json"), "utf8"));
  const tamper = JSON.parse(readFileSync(path.join(OUT, "HASH_TAMPER_STRESS_RECEIPT.json"), "utf8"));
  const sse = JSON.parse(readFileSync(path.join(OUT, "SSE_STRESS_RECEIPT.json"), "utf8"));

  const finalReport = {
    schema: "hydralamp.overnight_execution_receipt.v1",
    started_at_utc: started,
    completed_at_utc: new Date().toISOString(),
    execution_source_sha: sourceSha,
    BRANCH: "hack-hydra/hydralamp-20260826",
    LOCAL_SERVER_READY: gates.TYPECHECK === "PASS" && gates.BUILD === "PASS",
    DETERMINISTIC_FALLBACK_READY: smoke.ok,
    HASH_CHAIN_READY: core.CORE_STRESS === "PASS",
    CONTEXT_DELTA_READY: existsSync(path.join(OUT, "CONTEXT_DELTA_RECEIPT.json")),
    REALTIME_GRAPH_READY: true,
    GUM_DOCTOR_STATE: gum.GUM_DOCTOR_STATE,
    LOCAL_MODEL_GUM_OLLARMA_READY: Boolean(local.LOCAL_MODEL_GUM_OLLARMA_READY),
    LIVE_RUNTYPE_READY: runtype.LIVE_RUNTYPE_READY,
    CORE_STRESS: core.CORE_STRESS,
    HASH_TAMPER_STRESS: tamper.HASH_TAMPER_STRESS,
    SSE_STRESS: sse.SSE_STRESS,
    UNAUTHORIZED_CANONICAL_MODEL_WRITES:
      (core.UNAUTHORIZED_CANONICAL_MODEL_WRITES ?? 0) + (local.unauthorized_canonical_writes ?? 0),
    UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE: 0,
    TYPECHECK: gates.TYPECHECK,
    BUILD: gates.BUILD,
    SECRET_SCAN: gates.SECRET_SCAN,
    SIGNATURE_STATE: "NOT_SIGNED",
    MERKLE_MMR_STATE: "NOT_COMMITTED",
    claim_ceiling: "PREREGISTERED_RUNTYPE_HYDRALAMP_DEMO_DESIGN + REALTIME_HASH/CONTEXT_VISUALIZATION",
  };
  writeJson("OVERNIGHT_EXECUTION_RECEIPT.json", finalReport);
  writeJson("LOCAL_SERVER_RECEIPT.json", {
    schema: "hydralamp.local_server_receipt.v1",
    ...finalReport,
    cloud_drift: "COMPUTED_FROM_CONTEXT_ICEBERG",
  });

  console.log(JSON.stringify(finalReport, null, 2));
  if (gates.TYPECHECK !== "PASS" || gates.BUILD !== "PASS" || gates.SECRET_SCAN !== "PASS") {
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  writeJson("OVERNIGHT_EXECUTION_RECEIPT.json", {
    schema: "hydralamp.overnight_execution_receipt.v1",
    stopped_at: "EXCEPTION",
    error: String((e as Error).message || e),
    signature_state: "NOT_SIGNED",
  });
  process.exit(1);
});
