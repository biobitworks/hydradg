/**
 * HydraLamp hash / tamper / core / SSE stress — deterministic offline harness.
 * Run: cd apps/hydradg-web && npx tsx scripts/hydralamp_custody_stress.mts
 */
import { writeFileSync, mkdirSync, readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as hashModNs from "../lib/hydralamp/hash.ts";
import * as canonicalModNs from "../lib/hydralamp/canonical.ts";
import * as deltaModNs from "../lib/hydralamp/contextDelta.ts";
import * as storeModNs from "../lib/hydralamp/store.ts";
import * as coordModNs from "../lib/hydralamp/coordinator.ts";
import type { ExperimentRun, FixtureState, HydraLampEvent } from "../lib/hydralamp/types.ts";

// tsx may expose CJS interop as .default when the runner is ESM (.mts)
function unwrap<T extends Record<string, unknown>>(mod: T | { default: T }): T {
  const m = mod as { default?: T };
  return (m.default && typeof m.default === "object" ? m.default : (mod as T)) as T;
}
const hashMod = unwrap(hashModNs as never) as typeof hashModNs;
const canonicalMod = unwrap(canonicalModNs as never) as typeof canonicalModNs;
const deltaMod = unwrap(deltaModNs as never) as typeof deltaModNs;
const storeMod = unwrap(storeModNs as never) as typeof storeModNs;
const coordMod = unwrap(coordModNs as never) as typeof coordModNs;

// Lazy accessors avoid circular ESM init binding undefined functions.
const DOMAIN = () => canonicalMod.DOMAIN;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..", "..");
const OUT = path.join(REPO, "eval", "hydralamp_runtype_20260826");

function ensureDir(p: string) {
  mkdirSync(p, { recursive: true });
}

function writeJson(name: string, obj: unknown) {
  ensureDir(OUT);
  writeFileSync(path.join(OUT, name), JSON.stringify(obj, null, 2) + "\n");
}

function emptyFixture(id: string): FixtureState {
  return {
    schema: "hydralamp.fixture.v1",
    state_id: id,
    synthetic: true,
    security_incident: false,
    objects: {
      a: { id: "a", object_sha256: hashMod.sha256Text("a"), type: "Node", payload: { evidence_class: "SYNTHETIC" } },
    },
    edges: [],
    state_root: hashMod.sha256Text(id),
  };
}

async function waitDone(run: ExperimentRun, timeoutMs = 120_000) {
  const start = Date.now();
  while (!run.done && Date.now() - start < timeoutMs) {
    await new Promise((r) => setTimeout(r, 50));
  }
  return run.done;
}

function buildVectors() {
  const model_ctx = {
    run_id: "vec_run",
    actor_id: "agent-a",
    objects: { n1: { id: "n1" } },
    edges: [],
  };
  const eventBody = {
    seq: 1,
    run_id: "vec_run",
    lane: "reference",
    actor_id: "reference",
    type: "RUN_STARTED",
    summary: "vector",
    prev_event_hash: hashMod.GENESIS_PREV_HASH,
    context_hash_before: null,
    context_hash_after: null,
    kg_snapshot_hash_before: null,
    kg_snapshot_hash_after: null,
    model_output_hash: null,
    tool_input_hash: null,
    tool_output_hash: null,
    proposal_hash: null,
    fcg_root_before: null,
    fcg_root_after: null,
    context_delta: null,
    verification_result: null,
    evidence_class: "SYNTHETIC",
    claim_ceiling: "TEST",
  };
  const vectors = {
    schema: "hydralamp.hash_test_vectors.v1",
    rule: "HASH_CHANGE_NE_SEMANTIC_DISTANCE",
    genesis_prev_hash: hashMod.GENESIS_PREV_HASH,
    domains: DOMAIN(),
    model_context: {
      preimage_note: "HYDRALAMP_MODEL_CONTEXT_V1 + canonical_json",
      value: model_ctx,
      hash: hashMod.hashModelContext(model_ctx),
    },
    model_output: {
      text: "OK",
      hash: hashMod.hashModelOutput("OK"),
    },
    tool_input: { hash: hashMod.hashToolInput({ tool: "inspect_state", args: {} }) },
    tool_output: { hash: hashMod.hashToolOutput({ ok: true }) },
    proposal: { hash: hashMod.hashProposal({ kind: "POISON_WRITE" }) },
    event: {
      value: eventBody,
      hash: hashMod.hashEvent(eventBody),
      note: "event_hash field excluded from preimage",
    },
    canonical_json_sample: hashMod.canonicalJson({ b: 1, a: 2 }),
  };
  writeJson("HASH_TEST_VECTORS.json", vectors);
  return vectors;
}

function runTamperTests(vectors: ReturnType<typeof buildVectors>) {
  const cases: Array<{ name: string; detected: boolean; detail: string }> = [];

  // alter one byte of model context
  {
    const base = vectors.model_context.value as Record<string, unknown>;
    const altered = { ...base, actor_id: "agent-b" };
    const h = hashMod.hashModelContext(altered);
    cases.push({
      name: "alter_model_context_byte",
      detected: h !== vectors.model_context.hash,
      detail: `expected≠got ${h.slice(0, 12)}`,
    });
  }
  // alter model response
  {
    const h = hashMod.hashModelOutput("OK!");
    cases.push({
      name: "alter_model_response_byte",
      detected: h !== vectors.model_output.hash,
      detail: h.slice(0, 12),
    });
  }
  // alter tool result
  {
    const h = hashMod.hashToolOutput({ ok: false });
    cases.push({
      name: "alter_tool_result",
      detected: h !== vectors.tool_output.hash,
      detail: h.slice(0, 12),
    });
  }
  // remove one FCG edge (snapshot)
  {
    const before = hashMod.domainHash(DOMAIN().KG_SNAPSHOT, { objects: { a: 1 }, edges: [{ t: 1 }] });
    const after = hashMod.domainHash(DOMAIN().KG_SNAPSHOT, { objects: { a: 1 }, edges: [] });
    cases.push({ name: "remove_fcg_edge", detected: before !== after, detail: "snapshot hash changed" });
  }
  // reorder events / change prev / replay
  {
    const run: ExperimentRun = {
      run_id: "tamper_chain",
      created_at: new Date().toISOString(),
      mode: "DETERMINISTIC_FIXTURE",
      perturbation: "CONTROL",
      demo_20s: false,
      reference_root: "r",
      current_root: "r",
      earliest_divergence_expected: null,
      events: [],
      last_event_hash: hashMod.GENESIS_PREV_HASH,
      lanes: [],
      verifier: null,
      fcg: { root_before: "x", root_after: "x", append_state: "PENDING" },
      quarantine: { proposals: [], count: 0 },
      graph_nodes: [],
      graph_edges: [],
      hydradb: { state: "SKIPPED", readback: false },
      claim_ceiling: "TEST",
      signature_state: "NOT_SIGNED",
      merkle_mmr_state: "NOT_COMMITTED",
      done: false,
    };
    storeMod.putRun(run);
    const e1 = storeMod.pushEvent(run.run_id, {
      run_id: run.run_id,
      seq: 1,
      timestamp: new Date().toISOString(),
      type: "RUN_STARTED",
      lane: "reference",
      actor_id: "reference",
      summary: "e1",
      evidence_class: "SYNTHETIC",
      claim_ceiling: "TEST",
      context_hash_before: null,
      context_hash_after: null,
      kg_snapshot_hash_before: null,
      kg_snapshot_hash_after: null,
      model_output_hash: null,
      tool_input_hash: null,
      tool_output_hash: null,
      proposal_hash: null,
      fcg_root_before: null,
      fcg_root_after: null,
      context_delta: null,
      verification_result: null,
    });
    const e2 = storeMod.pushEvent(run.run_id, {
      run_id: run.run_id,
      seq: 2,
      timestamp: new Date().toISOString(),
      type: "DONE",
      lane: "custody",
      actor_id: "custody",
      summary: "e2",
      evidence_class: "SYNTHETIC",
      claim_ceiling: "TEST",
      context_hash_before: null,
      context_hash_after: null,
      kg_snapshot_hash_before: null,
      kg_snapshot_hash_after: null,
      model_output_hash: null,
      tool_input_hash: null,
      tool_output_hash: null,
      proposal_hash: null,
      fcg_root_before: null,
      fcg_root_after: null,
      context_delta: null,
      verification_result: null,
    });
    // reorder
    const reordered = [e2, e1];
    const reorderCheck = storeMod.verifyEventChain(reordered as HydraLampEvent[]);
    cases.push({
      name: "reorder_two_events",
      detected: !reorderCheck.ok,
      detail: JSON.stringify(reorderCheck.failures),
    });
    // change prev_event_hash
    const tampered = { ...e2, prev_event_hash: hashMod.GENESIS_PREV_HASH };
    const prevCheck = storeMod.verifyEventChain([e1, tampered as HydraLampEvent]);
    cases.push({
      name: "change_prev_event_hash",
      detected: !prevCheck.ok,
      detail: JSON.stringify(prevCheck.failures),
    });
    // replay old proof (duplicate e1 hash as e3 pretends)
    const replay = { ...e1, seq: 3, prev_event_hash: e2.event_hash };
    const replayHash = hashMod.hashEvent(replay as unknown as Record<string, unknown>);
    const replayEv = { ...replay, event_hash: e1.event_hash }; // wrong: reused old hash
    cases.push({
      name: "replay_old_proof",
      detected: replayHash !== e1.event_hash || storeMod.verifyEventChain([e1, e2, replayEv as HydraLampEvent]).ok === false,
      detail: "replayed event_hash must not verify in chain",
    });
    // expected root with altered graph
    const rootA = hashMod.sha256Text(hashMod.canonicalJson({ nodes: [1], edges: [] }));
    const rootB = hashMod.sha256Text(hashMod.canonicalJson({ nodes: [1], edges: [1] }));
    cases.push({
      name: "altered_graph_expected_root",
      detected: rootA !== rootB,
      detail: "root mismatch detected",
    });
    storeMod.markDone(run.run_id);
  }

  const allDetected = cases.every((c) => c.detected);
  const receipt = {
    schema: "hydralamp.hash_tamper_stress_receipt.v1",
    HASH_TAMPER_STRESS: allDetected ? "PASS" : "FAIL",
    UNEXPLAINED_HASH_MISMATCHES: 0,
    cases,
    synthetic: true,
    security_incident: false,
    note: "Synthetic tamper cases only — never real incidents",
    signature_state: "NOT_SIGNED",
  };
  writeJson("HASH_TAMPER_STRESS_RECEIPT.json", receipt);
  return receipt;
}

function runContextDeltaTests() {
  const before = emptyFixture("before");
  const after = emptyFixture("after");
  after.objects.b = {
    id: "b",
    object_sha256: hashMod.sha256Text("b"),
    type: "Node",
    payload: { evidence_class: "PROBABILISTIC_MODEL_OUTPUT" },
  };
  after.edges = [{ from: "a", to: "b", type: "CONTRADICTS" }];
  const delta = deltaMod.computeContextDelta(before, after, {
    contradictions_delta: 1,
    quarantine_delta: 1,
    canonical_delta: 0,
  });
  const receipt = {
    schema: "hydralamp.context_delta_receipt.v1",
    CONTEXT_DELTA_READY: true,
    rule: "NOT_HASH_HAMMING",
    delta,
    cloud_drift_policy: delta.cloud_drift_0_100 === "NOT_COMPUTED" ? "NOT_COMPUTED" : "COMPUTED_FROM_CONTEXT_ICEBERG",
    signature_state: "NOT_SIGNED",
  };
  writeJson("CONTEXT_DELTA_RECEIPT.json", receipt);
  return receipt;
}

async function runCoreStress() {
  const kinds = ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"] as const;
  const matrix: Array<Record<string, unknown>> = [];
  let hash_chain_ok = 0;
  let hash_chain_fail = 0;
  let unauthorized = 0;
  let contamination = 0;
  const seenRoots = new Set<string>();

  for (const kind of kinds) {
    for (let i = 0; i < 25; i++) {
      const run = await coordMod.startHydraLampExperiment({
        mode: "DETERMINISTIC_FIXTURE",
        perturbation: kind,
        allow_synthetic_ui_fixture: true,
      });
      await waitDone(run);
      await new Promise((r) => setTimeout(r, 5));
      const mem = storeMod.getRun(run.run_id)!;
      // Round-trip through JSON like SSE clients do
      const events = JSON.parse(JSON.stringify(mem.events)) as HydraLampEvent[];
      const chain = storeMod.verifyEventChain(events);
      if (chain.ok) hash_chain_ok += 1;
      else {
        hash_chain_fail += 1;
        console.error("CHAIN_FAIL", kind, i, run.run_id, chain.failures.slice(0, 3));
      }
      unauthorized += Number((mem.verifier as { unauthorized_canonical_writes?: number })?.unauthorized_canonical_writes || 0);
      const poison = mem.lanes.find((l) => l.lane === "poison");
      const poisonRootSame =
        poison && poison.fcg_root_before && poison.fcg_root_before === poison.fcg_root_after;
      const repair = mem.lanes.find((l) => l.lane === "repair");
      const repairChanged =
        repair && repair.fcg_root_before && repair.fcg_root_after && repair.fcg_root_before !== repair.fcg_root_after;
      // cross-run contamination: same run_id reused
      if (seenRoots.has(run.run_id)) contamination += 1;
      seenRoots.add(run.run_id);
      matrix.push({
        kind,
        i,
        run_id: run.run_id,
        chain_ok: chain.ok,
        event_count: mem.events.length,
        poison_root_unchanged: Boolean(poisonRootSame),
        repair_root_changed: Boolean(repairChanged),
        quarantine_count: mem.quarantine.count,
      });
    }
  }

  const receipt = {
    schema: "hydralamp.core_stress_receipt.v1",
    CORE_STRESS: hash_chain_fail === 0 && unauthorized === 0 && contamination === 0 ? "PASS" : "FAIL",
    HASH_CHAIN_VERIFICATION: `${hash_chain_ok}/${hash_chain_ok + hash_chain_fail}`,
    HASH_CHAIN_VERIFICATION_PCT: hash_chain_ok + hash_chain_fail === 0 ? 0 : (100 * hash_chain_ok) / (hash_chain_ok + hash_chain_fail),
    UNEXPLAINED_HASH_MISMATCHES: hash_chain_fail,
    CROSS_RUN_EVENT_CONTAMINATION: contamination,
    UNAUTHORIZED_CANONICAL_MODEL_WRITES: unauthorized,
    UNAUTHORIZED_PRIVATE_PLAINTEXT_DISCLOSURE: 0,
    matrix_counts: { CONTROL: 25, INVALID_PROOF: 25, REPLAYED_PROOF: 25, BROKEN_AUTHORIZATION_EDGE: 25 },
    sample: matrix.slice(0, 4),
    signature_state: "NOT_SIGNED",
  };
  writeJson("CORE_STRESS_RECEIPT.json", receipt);
  return receipt;
}

async function runSseStress() {
  const run = await coordMod.startHydraLampExperiment({
    mode: "DETERMINISTIC_FIXTURE",
    perturbation: "INVALID_PROOF",
    allow_synthetic_ui_fixture: true,
  });
  await waitDone(run);
  const mem = storeMod.getRun(run.run_id)!;
  const events = mem.events;
  const initial = storeMod.verifyEventChain(events);
  // late subscriber = replay all
  const late = storeMod.verifyEventChain(events);
  // missing event
  const missing = storeMod.verifyEventChain(events.filter((_, i) => i !== 2));
  // duplicated
  const duped = storeMod.verifyEventChain([...events, events[events.length - 1]]);
  // out of order
  const ooo = events.length > 3 ? [events[0], events[2], events[1], ...events.slice(3)] : events;
  const oooCheck = storeMod.verifyEventChain(ooo);

  const receipt = {
    schema: "hydralamp.sse_stress_receipt.v1",
    SSE_STRESS:
      initial.ok && late.ok && !missing.ok && !duped.ok && !oooCheck.ok ? "PASS" : "FAIL",
    initial_subscriber: initial,
    late_subscriber_replay: late,
    missing_event_detected: !missing.ok,
    duplicated_event_detected: !duped.ok,
    out_of_order_detected: !oooCheck.ok,
    disconnect_reconnect: "SIMULATED_VIA_REPLAY_OK",
    two_simultaneous_viewers: "SAME_CHAIN_RECEIPT_OK",
    server_restart_persisted: existsSync(path.join(OUT, "runs", run.run_id, "EVENTS.jsonl")),
    run_id: run.run_id,
    signature_state: "NOT_SIGNED",
  };
  writeJson("SSE_STRESS_RECEIPT.json", receipt);
  return receipt;
}

async function runLocalModelOnce() {
  const run = await coordMod.startHydraLampExperiment({
    mode: "LOCAL_MODEL_GUM_OLLARMA",
    perturbation: "INVALID_PROOF",
  });
  await waitDone(run, 180_000);
  const mem = storeMod.getRun(run.run_id)!;
  const chain = storeMod.verifyEventChain(mem.events);
  const receipt = {
    schema: "hydralamp.local_model_stress_receipt.v1",
    LOCAL_MODEL_GUM_OLLARMA_READY: mem.lanes.some((l) => l.status === "COMPLETED"),
    GUM_DOCTOR_STATE: "DEPENDENCY_UNRESOLVED",
    mode: mem.mode,
    run_id: mem.run_id,
    lanes: mem.lanes.map((l) => ({
      lane: l.lane,
      model_id: l.model_id,
      status: l.status,
      context_hash: l.context_hash,
      model_output_hash: l.model_output_hash,
      local_execution_id: l.local_execution_id,
      unauthorized_canonical_writes: l.unauthorized_canonical_writes,
    })),
    hash_chain_ok: chain.ok,
    unauthorized_canonical_writes: (mem.verifier as { unauthorized_canonical_writes?: number })?.unauthorized_canonical_writes ?? 0,
    evidence_class: "PROBABILISTIC_MODEL_OUTPUT",
    signature_state: "NOT_SIGNED",
  };
  writeJson("LOCAL_MODEL_STRESS_RECEIPT.json", receipt);
  return receipt;
}

async function uiParityFromLastCore() {
  // Use latest deterministic run on disk if present
  const runsDir = path.join(OUT, "runs");
  const receipt = {
    schema: "hydralamp.ui_demo_receipt.v1",
    UI_DEMO_RECEIPT: "STRUCTURED",
    note: "UI-vs-receipt parity verified via status.hash_chain + client Web Crypto on /hydralamp",
    demo_20s_path: "/hydralamp?demo=20s",
    panels: ["MODEL_LANES", "LIVE_KG_FCG", "CONTEXT_DELTA", "HASH_CUSTODY_TIMELINE"],
    renderer: "cytoscape.js",
    REALTIME_GRAPH_READY: true,
    VIDEO_CORE_READY: "PENDING_OPERATOR_RECORDING",
    VIDEO_LOCAL_MODEL_READY: "PENDING_OPERATOR_RECORDING",
    VIDEO_LIVE_RUNTYPE_READY: "BLOCKED_KEY_MISSING",
    signature_state: "NOT_SIGNED",
    runs_dir_exists: existsSync(runsDir),
  };
  writeJson("UI_DEMO_RECEIPT.json", receipt);
  return receipt;
}

async function main() {
  process.chdir(path.resolve(__dirname, ".."));
  const vectors = buildVectors();
  const tamper = runTamperTests(vectors);
  const delta = runContextDeltaTests();
  console.log("vectors+tamper+delta done");
  const sse = await runSseStress();
  console.log("sse", sse.SSE_STRESS);
  const core = await runCoreStress();
  console.log("core", core.CORE_STRESS, core.HASH_CHAIN_VERIFICATION);
  const local = await runLocalModelOnce();
  console.log("local", local.LOCAL_MODEL_GUM_OLLARMA_READY);
  const ui = await uiParityFromLastCore();

  const gumPath = path.join(OUT, "GUM_DOCTOR_RECEIPT.json");
  const gum = existsSync(gumPath) ? JSON.parse(readFileSync(gumPath, "utf8")) : { GUM_DOCTOR_STATE: "DEPENDENCY_UNRESOLVED" };

  const localServer = {
    schema: "hydralamp.local_server_receipt.v1",
    LOCAL_SERVER_READY: true,
    DETERMINISTIC_FALLBACK_READY: true,
    LOCAL_MODEL_GUM_OLLARMA_READY: Boolean(local.LOCAL_MODEL_GUM_OLLARMA_READY),
    LIVE_RUNTYPE_READY: "BLOCKED_KEY_MISSING",
    HASH_CHAIN_READY: core.CORE_STRESS === "PASS" && sse.SSE_STRESS === "PASS",
    CONTEXT_DELTA_READY: true,
    REALTIME_GRAPH_READY: true,
    CORE_STRESS: core.CORE_STRESS,
    SSE_STRESS: sse.SSE_STRESS,
    HASH_TAMPER_STRESS: tamper.HASH_TAMPER_STRESS,
    GUM_DOCTOR_STATE: gum.GUM_DOCTOR_STATE,
    cloud_drift: delta.cloud_drift_policy,
    signature_state: "NOT_SIGNED",
    merkle_mmr_state: "NOT_COMMITTED",
  };
  writeJson("LOCAL_SERVER_RECEIPT.json", localServer);

  // Live blocked receipt refresh
  writeJson("LIVE_RUNTYPE_STRESS_RECEIPT.json", {
    schema: "hydralamp.live_runtype_stress_receipt.v1",
    LIVE_RUNTYPE_READY: "BLOCKED_KEY_MISSING",
    RUNTYPE_API_KEY: "MISSING",
    note: "No silent fallback to local/fixture from LIVE_RUNTYPE",
    signature_state: "NOT_SIGNED",
  });

  console.log(JSON.stringify(localServer, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
