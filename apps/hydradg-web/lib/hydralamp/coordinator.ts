import { randomUUID } from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import {
  buildToolContext,
  executeTool,
  LOCAL_TOOL_SCHEMAS,
  type ToolName,
} from "./tools";
import { loadSystemPrompt, materializeState, repoRoot, sha256Text, canonicalJson } from "./fixtures";
import { verifyLane, summarizeVerifier } from "./verifier";
import { appendExperimentCustody, tryHydraDbProjection, persistRunArtifacts } from "./custody";
import { putRun, pushEvent, markDone } from "./store";
import type {
  ExperimentRun,
  HydraLampEvent,
  LaneResult,
  PerturbationKind,
  StructuredAgentOutput,
} from "./types";

const DEADLINE_MS = 10_000;
const MAX_TOOL_CALLS = 6;

function now() {
  return new Date().toISOString();
}

function seqEvent(
  run: ExperimentRun,
  partial: Omit<HydraLampEvent, "run_id" | "seq" | "timestamp">,
): HydraLampEvent {
  return {
    run_id: run.run_id,
    seq: run.events.length + 1,
    timestamp: now(),
    ...partial,
  };
}

function emit(run: ExperimentRun, partial: Omit<HydraLampEvent, "run_id" | "seq" | "timestamp">) {
  const ev = seqEvent(run, partial);
  pushEvent(run.run_id, ev);
  return ev;
}

function parseStructured(text: string): StructuredAgentOutput | null {
  try {
    const start = text.indexOf("{");
    const end = text.lastIndexOf("}");
    if (start < 0 || end < 0) return null;
    const obj = JSON.parse(text.slice(start, end + 1));
    if (!obj || typeof obj !== "object") return null;
    return {
      decision: obj.decision,
      earliest_divergence: obj.earliest_divergence ?? null,
      proof_state: obj.proof_state ?? "UNKNOWN",
      requested_action: obj.requested_action ?? null,
      confidence: Number(obj.confidence ?? 0),
      evidence_refs: Array.isArray(obj.evidence_refs) ? obj.evidence_refs : [],
    };
  } catch {
    return null;
  }
}

export function runtypeKeyPresent(): boolean {
  return Boolean(process.env.RUNTYPE_API_KEY && process.env.RUNTYPE_API_KEY.trim());
}

export function loadModelInventory(): {
  runtype_state: string;
  selected_models: Array<{ lane: string; provider: string; model_id: string; config_id?: string }>;
} {
  const p = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "MODEL_INVENTORY.json");
  if (!existsSync(p)) {
    return { runtype_state: "NOT_CONFIGURED", selected_models: [] };
  }
  return JSON.parse(readFileSync(p, "utf8"));
}

async function runOneLaneLive(params: {
  run: ExperimentRun;
  lane: "agent-a" | "agent-b" | "agent-c";
  model_id: string;
  perturbation: PerturbationKind;
}): Promise<LaneResult> {
  const { run, lane, model_id, perturbation } = params;
  const started = Date.now();
  const ctx = buildToolContext(run.run_id, perturbation);
  emit(run, {
    lane,
    model_id,
    type: "MODEL_ACTIVE",
    summary: `Model active: ${model_id}`,
  });

  try {
    const { RuntypeClient } = await import("@runtypelabs/sdk");
    const client = new RuntypeClient({
      apiKey: process.env.RUNTYPE_API_KEY!,
      baseUrl: process.env.RUNTYPE_API_URL || "https://api.runtype.com",
    });

    const systemPrompt = loadSystemPrompt();
    const userPrompt = JSON.stringify({
      experiment_id: run.run_id,
      reference_root: ctx.reference.state_root,
      current_root: ctx.current.state_root,
      instruction:
        "Diagnose divergence using tools. Return only the required JSON object. No chain-of-thought.",
    });

    const localTools: Record<string, (args: unknown) => Promise<unknown>> = {};
    const tool_sequence: string[] = [];
    let repair_requested = false;
    let repair_allowed: boolean | null = null;
    let candidate_root: string | null = null;
    let tool_count = 0;

    for (const schema of LOCAL_TOOL_SCHEMAS) {
      localTools[schema.name] = async (args: unknown) => {
        const a = (args && typeof args === "object" ? args : {}) as Record<string, unknown>;
        if (tool_count >= MAX_TOOL_CALLS) {
          return { error: "MAX_TOOL_CALLS", max: MAX_TOOL_CALLS };
        }
        tool_count += 1;
        tool_sequence.push(schema.name);
        emit(run, {
          lane,
          model_id,
          type: "TOOL_CALL",
          tool: schema.name,
          summary: `Tool call: ${schema.name}`,
          public_payload: { args: publicSafeArgs(a) },
        });
        const result = executeTool(ctx, schema.name as ToolName, a);
        if (schema.name === "attempt_repair") {
          repair_requested = true;
          repair_allowed = Boolean((result as { allowed?: boolean }).allowed);
          candidate_root = ((result as { candidate_state_root?: string }).candidate_state_root as string) || null;
        }
        emit(run, {
          lane,
          model_id,
          type: "TOOL_RESULT",
          tool: schema.name,
          summary: `Tool result: ${schema.name}`,
          public_payload: result as Record<string, unknown>,
        });
        return result;
      };
    }

    const timeout = new Promise<never>((_, reject) =>
      setTimeout(() => reject(Object.assign(new Error("TIMEOUT"), { code: "TIMEOUT" })), DEADLINE_MS),
    );

    const execPromise = (async () => {
      // Official SDK: RuntypeClient.runWithLocalTools(request, localTools, options)
      // Do not call client.dispatch as a function — it is a DispatchEndpoint object.
      return await client.runWithLocalTools(
        {
          agent: {
            name: `HydraLamp-${lane}`,
            model: model_id,
            systemPrompt,
            temperature: 0,
            tools: {
              runtimeTools: LOCAL_TOOL_SCHEMAS,
              maxToolCalls: MAX_TOOL_CALLS,
            },
          },
          messages: [{ role: "user", content: userPrompt }],
          streamResponse: false,
        } as never,
        localTools as never,
        { cache: false } as never,
      );
    })();

    const result = (await Promise.race([execPromise, timeout])) as unknown as Record<string, unknown>;
    const executionId =
      (result?.executionId as string) ||
      (result?.id as string) ||
      (result?.execution_id as string) ||
      null;
    const text =
      (result?.output as string) ||
      (result?.content as string) ||
      (typeof result?.message === "string" ? result.message : "") ||
      JSON.stringify(result?.final || result?.data || result);
    const structured = parseStructured(text);
    emit(run, {
      lane,
      model_id,
      runtype_execution_id: executionId,
      type: "MODEL_FINAL",
      summary: `Model final: ${structured?.decision || "UNPARSED"}`,
      public_payload: structured || { parse: "FAILED" },
    });
    return {
      lane,
      model_id,
      runtype_execution_id: executionId,
      status: "COMPLETED",
      tool_sequence,
      tool_count,
      structured,
      raw_output_sha256: sha256Text(text),
      latency_ms: Date.now() - started,
      repair_requested,
      repair_allowed,
      candidate_root,
      unauthorized_canonical_writes: 0,
    };
  } catch (err) {
    const code = (err as { code?: string })?.code || (err as Error).message;
    const isTimeout = String(code).includes("TIMEOUT");
    emit(run, {
      lane,
      model_id,
      type: isTimeout ? "TIMEOUT" : "ERROR",
      summary: isTimeout ? "TIMEOUT" : `ERROR: ${String(code).slice(0, 120)}`,
    });
    return {
      lane,
      model_id,
      runtype_execution_id: null,
      status: isTimeout ? "TIMEOUT" : "ERROR",
      tool_sequence: [],
      tool_count: 0,
      structured: null,
      raw_output_sha256: null,
      latency_ms: Date.now() - started,
      error_class: isTimeout ? "TIMEOUT" : "PROVIDER_OR_SDK_ERROR",
      repair_requested: false,
      repair_allowed: null,
      candidate_root: null,
      unauthorized_canonical_writes: 0,
    };
  }
}

function publicSafeArgs(args: Record<string, unknown>) {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(args || {})) {
    if (/secret|key|token|password/i.test(k)) continue;
    out[k] = v;
  }
  return out;
}

/** Labeled synthetic UI fixture for layout — NEVER claimed as live Runtype. */
async function runSyntheticLabeledLanes(params: {
  run: ExperimentRun;
  perturbation: PerturbationKind;
}): Promise<LaneResult[]> {
  const { run, perturbation } = params;
  const ctx = buildToolContext(run.run_id, perturbation);
  const models = ["synthetic:layout-a", "synthetic:layout-b", "synthetic:layout-c"] as const;
  const lanes: Array<"agent-a" | "agent-b" | "agent-c"> = ["agent-a", "agent-b", "agent-c"];
  const results: LaneResult[] = [];

  for (let i = 0; i < 3; i++) {
    const lane = lanes[i];
    const model_id = models[i];
    const started = Date.now();
    emit(run, { lane, model_id, type: "MODEL_ACTIVE", summary: `SYNTHETIC FIXTURE lane ${lane}` });
    const seq = ["inspect_state", "trace_divergence", "verify_actor_proof"] as ToolName[];
    for (const tool of seq) {
      emit(run, { lane, model_id, type: "TOOL_CALL", tool, summary: `Tool call: ${tool}` });
      const result = executeTool(ctx, tool, { experiment_id: run.run_id });
      emit(run, {
        lane,
        model_id,
        type: "TOOL_RESULT",
        tool,
        summary: `Tool result: ${tool}`,
        public_payload: result as Record<string, unknown>,
      });
    }
    const proof = executeTool(ctx, "verify_actor_proof", {});
    const div = executeTool(ctx, "trace_divergence", {}) as {
      earliest_divergent_dependency: string | null;
    };
    const proof_state = (proof as { proof_state: string }).proof_state;
    const decision =
      perturbation === "CONTROL"
        ? "NO_ACTION"
        : proof_state === "VALID"
          ? "NO_ACTION"
          : "REJECT_ACTOR";
    const structured: StructuredAgentOutput = {
      decision,
      earliest_divergence: div.earliest_divergent_dependency,
      proof_state: proof_state as StructuredAgentOutput["proof_state"],
      requested_action: null,
      confidence: 1,
      evidence_refs: ["synthetic_ui_fixture"],
    };
    emit(run, {
      lane,
      model_id,
      type: "MODEL_FINAL",
      summary: `SYNTHETIC final: ${decision}`,
      public_payload: structured,
    });
    results.push({
      lane,
      model_id,
      runtype_execution_id: null,
      status: "COMPLETED",
      tool_sequence: seq,
      tool_count: seq.length,
      structured,
      raw_output_sha256: sha256Text(canonicalJson(structured)),
      latency_ms: Date.now() - started,
      repair_requested: false,
      repair_allowed: null,
      candidate_root: null,
      unauthorized_canonical_writes: 0,
    });
  }
  return results;
}

export async function startHydraLampExperiment(opts: {
  perturbation?: PerturbationKind;
  demo_20s?: boolean;
  allow_synthetic_ui_fixture?: boolean;
}): Promise<ExperimentRun> {
  const perturbation = opts.perturbation || "INVALID_PROOF";
  const demo_20s = Boolean(opts.demo_20s);
  const m = materializeState(perturbation);
  const run_id = `hlrt_${Date.now().toString(36)}_${randomUUID().slice(0, 8)}`;

  const keyPresent = runtypeKeyPresent();
  const inventory = loadModelInventory();
  const selected = inventory.selected_models || [];

  let mode: ExperimentRun["mode"] = "LIVE_RUNTYPE";
  if (!keyPresent || selected.length === 0) {
    mode = opts.allow_synthetic_ui_fixture ? "SYNTHETIC_UI_FIXTURE" : "NOT_CONFIGURED";
  }

  const run: ExperimentRun = {
    run_id,
    created_at: now(),
    mode,
    perturbation,
    demo_20s,
    reference_root: m.reference.state_root,
    current_root: m.reference.state_root,
    earliest_divergence_expected: m.expectedEarliest,
    events: [],
    lanes: [],
    verifier: null,
    fcg: { root_before: sha256Text("hydralamp-empty-fcg-v1"), root_after: null, append_state: "PENDING" },
    hydradb: { state: "PENDING", readback: false },
    claim_ceiling:
      mode === "LIVE_RUNTYPE"
        ? "REAL_RUNTYPE_AGENT_EXECUTION_WITH_DETERMINISTIC_CUSTODY_VERIFICATION_DEMO"
        : "PREREGISTERED_RUNTYPE_HYDRALAMP_DEMO_DESIGN",
    signature_state: "NOT_SIGNED",
    merkle_mmr_state: "NOT_COMMITTED",
    done: false,
  };
  putRun(run);

  // async execution
  void (async () => {
    try {
      emit(run, {
        lane: "reference",
        type: "RUN_STARTED",
        summary: `Run started mode=${mode} perturbation=${perturbation}`,
        public_payload: {
          reference_root: run.reference_root,
          mode,
          synthetic_label:
            mode === "SYNTHETIC_UI_FIXTURE" ? "SYNTHETIC FIXTURE ≠ LIVE RUNTYPE DEMO" : null,
        },
      });

      // mutation
      run.current_root = m.current.state_root;
      emit(run, {
        lane: "reference",
        type: "MUTATION_INJECTED",
        summary: `Mutation ${perturbation}: root ${run.reference_root.slice(0, 8)} → ${run.current_root.slice(0, 8)}`,
        public_payload: {
          reference_root: run.reference_root,
          current_root: run.current_root,
          earliest_divergence_expected: run.earliest_divergence_expected,
        },
      });

      let lanes: LaneResult[] = [];
      if (mode === "NOT_CONFIGURED") {
        emit(run, {
          lane: "custody",
          type: "ERROR",
          summary: "RUNTYPE_STATE=NOT_CONFIGURED — set RUNTYPE_API_KEY server-side",
        });
        lanes = ["agent-a", "agent-b", "agent-c"].map((lane, i) => ({
          lane: lane as "agent-a" | "agent-b" | "agent-c",
          model_id: `unconfigured-${i + 1}`,
          runtype_execution_id: null,
          status: "NOT_CONFIGURED" as const,
          tool_sequence: [],
          tool_count: 0,
          structured: null,
          raw_output_sha256: null,
          latency_ms: 0,
          error_class: "RUNTYPE_NOT_CONFIGURED",
          repair_requested: false,
          repair_allowed: null,
          candidate_root: null,
          unauthorized_canonical_writes: 0,
        }));
      } else if (mode === "SYNTHETIC_UI_FIXTURE") {
        lanes = await runSyntheticLabeledLanes({ run, perturbation });
      } else {
        const models = selected.slice(0, 3);
        while (models.length < 1) {
          // impossible if selected empty handled above
          break;
        }
        const laneIds: Array<"agent-a" | "agent-b" | "agent-c"> = ["agent-a", "agent-b", "agent-c"];
        const jobs = models.map((mdef, idx) =>
          runOneLaneLive({
            run,
            lane: laneIds[idx],
            model_id: mdef.model_id,
            perturbation,
          }),
        );
        // allSettled semantics
        const settled = await Promise.allSettled(jobs);
        lanes = settled.map((s, idx) => {
          if (s.status === "fulfilled") return s.value;
          return {
            lane: laneIds[idx],
            model_id: models[idx]?.model_id || `unknown-${idx}`,
            runtype_execution_id: null,
            status: "ERROR" as const,
            tool_sequence: [],
            tool_count: 0,
            structured: null,
            raw_output_sha256: null,
            latency_ms: 0,
            error_class: "LANE_REJECTED",
            repair_requested: false,
            repair_allowed: null,
            candidate_root: null,
            unauthorized_canonical_writes: 0,
          };
        });
      }

      run.lanes = lanes;

      const reports = lanes.map((lane) =>
        verifyLane({
          lane,
          expectedEarliest: m.expectedEarliest,
          expectedProof: m.expectedProof,
          control: perturbation === "CONTROL",
        }),
      );
      const summary = summarizeVerifier(reports);
      run.verifier = summary;
      emit(run, {
        lane: "verifier",
        type: "VERIFIER_RESULT",
        summary: `Verifier: unauthorized_writes=${summary.unauthorized_canonical_writes} pass=${summary.completed} timeout=${summary.timeout}`,
        public_payload: summary,
      });

      if (mode !== "NOT_CONFIGURED") {
        const fcg = appendExperimentCustody(run, lanes, summary);
        run.fcg.root_after = String(fcg.root_after);
        run.fcg.append_state = "PASS";
        emit(run, {
          lane: "custody",
          type: "FCG_APPEND",
          summary: `FCG ${String(fcg.root_before).slice(0, 8)} → ${String(fcg.root_after).slice(0, 8)}`,
          public_payload: fcg,
        });
        const hydra = tryHydraDbProjection(run.run_id, fcg);
        run.hydradb = {
          state: hydra.state as ExperimentRun["hydradb"]["state"],
          readback: Boolean(hydra.readback),
          receipt_path: `eval/hydralamp_runtype_20260826/runs/${run.run_id}/HYDRADB_RECEIPT.json`,
        };
        emit(run, {
          lane: "custody",
          type: "HYDRADB_PROJECTED",
          summary: `HydraDB ${run.hydradb.state}`,
          public_payload: hydra,
        });
      } else {
        run.fcg.append_state = "SKIPPED";
        run.hydradb = { state: "SKIPPED", readback: false };
      }

      emit(run, {
        lane: "custody",
        type: "DONE",
        summary: "Models propose. Custody decides.",
        public_payload: {
          mode: run.mode,
          decisions: lanes.map((l) => ({
            lane: l.lane,
            decision: l.structured?.decision || l.status,
          })),
          earliest_divergence: run.earliest_divergence_expected,
          fcg: run.fcg,
          hydradb: run.hydradb,
        },
      });
      persistRunArtifacts(run);
      // also write inventory snapshot note
      const modeDir = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "runs", run.run_id);
      mkdirSync(modeDir, { recursive: true });
      writeFileSync(
        path.join(modeDir, "MODE.json"),
        JSON.stringify({ mode: run.mode, runtype_key_present: keyPresent }, null, 2) + "\n",
      );
    } catch (e) {
      emit(run, {
        lane: "custody",
        type: "ERROR",
        summary: `COORDINATOR_ERROR: ${String((e as Error).message || e).slice(0, 160)}`,
      });
      persistRunArtifacts(run);
    } finally {
      markDone(run.run_id);
    }
  })();

  return run;
}
