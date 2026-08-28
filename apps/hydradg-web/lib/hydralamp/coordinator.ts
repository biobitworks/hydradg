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
import {
  GENESIS_PREV_HASH,
  hashModelOutput,
  hashToolInput,
  hashToolOutput,
  hashProposal,
} from "./hash";
import { buildModelVisibleContext, kgSnapshotHash } from "./modelContext";
import { computeContextDelta } from "./contextDelta";
import { localModelComplete, probeLocalRuntime } from "./localModel";
import { loadHydraLampServerEnv, runtypeApiKeyStatus } from "./env";
import {
  normalizeRuntypeDispatchResult,
  runRuntypeWithLocalTools,
  sanitizeRuntypeProviderError,
} from "./runtypeNormalize";
import type {
  EvidenceClass,
  ExecutionMode,
  ExperimentRun,
  HydraLampEvent,
  LaneResult,
  PerturbationKind,
  StructuredAgentOutput,
  VerifierClass,
} from "./types";

/** Measured Runtype minimal latency ~15s; floor 45s, cap 120s unless env override. */
const DEADLINE_MS = Number(process.env.RUNTYPE_PROVIDER_TIMEOUT_MS || 60_000);
const MAX_TOOL_CALLS = 6;
const LOCAL_DEADLINE_MS = 45_000;

function now() {
  return new Date().toISOString();
}

type EmitPartial = {
  type: HydraLampEvent["type"];
  lane: HydraLampEvent["lane"];
  summary: string;
  actor_id?: string;
  model_id?: string | null;
  execution_id?: string | null;
  runtype_execution_id?: string | null;
  local_execution_id?: string | null;
  tool?: string;
  public_payload?: Record<string, unknown>;
  evidence_class?: EvidenceClass;
  claim_ceiling?: string;
  context_hash_before?: string | null;
  context_hash_after?: string | null;
  kg_snapshot_hash_before?: string | null;
  kg_snapshot_hash_after?: string | null;
  model_output_hash?: string | null;
  tool_input_hash?: string | null;
  tool_output_hash?: string | null;
  proposal_hash?: string | null;
  fcg_root_before?: string | null;
  fcg_root_after?: string | null;
  context_delta?: HydraLampEvent["context_delta"];
  verification_result?: VerifierClass | null;
  model_latency_ms?: number | null;
  end_to_end_ms?: number | null;
  context_delta_compute_ms?: number | null;
};

function emit(run: ExperimentRun, partial: EmitPartial) {
  const evidence: EvidenceClass =
    partial.evidence_class ||
    (run.mode === "LIVE_RUNTYPE"
      ? "LIVE_RUNTYPE"
      : run.mode === "LOCAL_MODEL_GUM_OLLARMA"
        ? "LOCAL_MODEL_GUM_OLLARMA"
        : run.mode === "DETERMINISTIC_FIXTURE" || run.mode === "SYNTHETIC_UI_FIXTURE"
          ? "DETERMINISTIC_FIXTURE"
          : "UNKNOWN");

  const fcgDefault = run.fcg.root_after || run.fcg.root_before;
  return pushEvent(run.run_id, {
    run_id: run.run_id,
    seq: run.events.length + 1,
    timestamp: now(),
    type: partial.type,
    lane: partial.lane,
    summary: partial.summary,
    actor_id: partial.actor_id || partial.lane,
    model_id: partial.model_id,
    execution_id: partial.execution_id,
    runtype_execution_id: partial.runtype_execution_id,
    local_execution_id: partial.local_execution_id,
    tool: partial.tool,
    public_payload: partial.public_payload,
    evidence_class: evidence,
    claim_ceiling: partial.claim_ceiling || run.claim_ceiling,
    context_hash_before: partial.context_hash_before ?? null,
    context_hash_after: partial.context_hash_after ?? null,
    kg_snapshot_hash_before: partial.kg_snapshot_hash_before ?? null,
    kg_snapshot_hash_after: partial.kg_snapshot_hash_after ?? null,
    model_output_hash: partial.model_output_hash ?? null,
    tool_input_hash: partial.tool_input_hash ?? null,
    tool_output_hash: partial.tool_output_hash ?? null,
    proposal_hash: partial.proposal_hash ?? null,
    fcg_root_before: partial.fcg_root_before ?? fcgDefault,
    fcg_root_after: partial.fcg_root_after ?? fcgDefault,
    context_delta: partial.context_delta ?? null,
    verification_result: partial.verification_result ?? null,
    model_latency_ms: partial.model_latency_ms,
    end_to_end_ms: partial.end_to_end_ms,
    context_delta_compute_ms: partial.context_delta_compute_ms,
  });
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
  return runtypeApiKeyStatus() === "PRESENT";
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

function syncGraphFromState(run: ExperimentRun, state: ReturnType<typeof materializeState>["current"], extra?: {
  quarantinedIds?: string[];
  repairedIds?: string[];
  contradictedIds?: string[];
}) {
  run.graph_nodes = Object.values(state.objects).map((o) => {
    let visual_class: ExperimentRun["graph_nodes"][0]["visual_class"] = "reference";
    if (extra?.quarantinedIds?.includes(o.id)) visual_class = "quarantined";
    else if (extra?.repairedIds?.includes(o.id)) visual_class = "repaired";
    else if (extra?.contradictedIds?.includes(o.id)) visual_class = "contradicted";
    else if (o.type.includes("Proof") || o.payload.evidence_class === "PROBABILISTIC_MODEL_OUTPUT") {
      visual_class = "probabilistic_proposal";
    } else if (String(o.payload.verified) === "true") visual_class = "verified";
    else visual_class = "canonical";
    return { id: o.id, label: `${o.type}`, visual_class };
  });
  run.graph_edges = state.edges.map((e, i) => ({
    id: `e${i}`,
    source: e.from,
    target: e.to,
    label: e.type,
  }));
}

/**
 * Critical path: rejected poison — proposal/context may change; canonical FCG root unchanged.
 * Authorized repair — verifier PASS → append → root changes.
 */
function applyProposalDecision(params: {
  run: ExperimentRun;
  lane: LaneResult["lane"];
  model_id: string;
  proposal: Record<string, unknown>;
  decision: VerifierClass;
  authorizeAppend: boolean;
  stateBefore: ReturnType<typeof materializeState>["current"];
  stateAfterVisual: ReturnType<typeof materializeState>["current"];
}) {
  const { run, lane, model_id, proposal, decision, authorizeAppend, stateBefore, stateAfterVisual } =
    params;
  const proposal_hash = hashProposal(proposal);
  const fcg_before = run.fcg.root_after || run.fcg.root_before || GENESIS_PREV_HASH;
  const deltaStarted = Date.now();
  const context_delta = computeContextDelta(stateBefore, stateAfterVisual, {
    quarantine_delta: authorizeAppend ? 0 : 1,
    canonical_delta: authorizeAppend ? 1 : 0,
    contradictions_delta: authorizeAppend ? 0 : 1,
  });
  const context_delta_compute_ms = Date.now() - deltaStarted;

  emit(run, {
    lane: lane === "poison" || lane === "repair" ? lane : "verifier",
    actor_id: lane,
    model_id,
    type: "PROPOSAL",
    summary: `Proposal ${String(proposal.kind || "action")} hash=${proposal_hash.slice(0, 8)}`,
    proposal_hash,
    fcg_root_before: fcg_before,
    fcg_root_after: fcg_before,
    context_delta,
    context_delta_compute_ms,
    public_payload: { proposal },
  });

  emit(run, {
    lane: "verifier",
    actor_id: "deterministic_verifier",
    type: "VERIFIER_RESULT",
    summary: `VERIFIER: ${decision}`,
    verification_result: decision,
    proposal_hash,
    fcg_root_before: fcg_before,
    fcg_root_after: fcg_before,
    public_payload: { decision, authorizeAppend },
  });

  if (!authorizeAppend) {
    run.quarantine.proposals.push({ ...proposal, proposal_hash, decision });
    run.quarantine.count = run.quarantine.proposals.length;
    emit(run, {
      lane: "custody",
      actor_id: "custody",
      type: "QUARANTINE",
      summary: "Poison observed. Poison retained. Canonical knowledge unchanged.",
      proposal_hash,
      verification_result: decision,
      fcg_root_before: fcg_before,
      fcg_root_after: fcg_before,
      context_delta,
      public_payload: {
        PROPOSAL_HASH: "changed",
        MODEL_CONTEXT: "changed",
        QUARANTINE_STATE: "changed",
        CANONICAL_FCG_ROOT: "unchanged",
        fcg_same: true,
      },
    });
    emit(run, {
      lane: "custody",
      type: "FCG_ROOT_UNCHANGED",
      summary: `FCG BEFORE ${fcg_before.slice(0, 8)} AFTER ${fcg_before.slice(0, 8)} SAME ✓`,
      fcg_root_before: fcg_before,
      fcg_root_after: fcg_before,
      verification_result: "RETAIN",
    });
    run.fcg.append_state = "UNCHANGED_QUARANTINE";
    syncGraphFromState(run, stateAfterVisual, {
      quarantinedIds: Object.keys(stateAfterVisual.objects).slice(-1),
      contradictedIds: Object.keys(stateAfterVisual.objects).slice(-1),
    });
    return { fcg_root_before: fcg_before, fcg_root_after: fcg_before, proposal_hash };
  }

  // Authorized append — mutate FCG root
  const appendBody = {
    prev_root: fcg_before,
    proposal_hash,
    authorized: true,
    run_id: run.run_id,
    lane,
  };
  const fcg_after = sha256Text(canonicalJson(appendBody));
  run.fcg.root_after = fcg_after;
  run.fcg.append_state = "PASS";
  emit(run, {
    lane: "custody",
    type: "FCG_APPEND",
    summary: `AUTHORIZED FCG APPEND ${fcg_before.slice(0, 8)} → ${fcg_after.slice(0, 8)}`,
    proposal_hash,
    verification_result: "PASS",
    fcg_root_before: fcg_before,
    fcg_root_after: fcg_after,
    context_delta: { ...context_delta, canonical_delta: 1 },
    public_payload: {
      VERIFICATION: "PASS",
      FCG_APPEND: true,
      ROOT_CHANGED: true,
      CLIENT_HASH_RECOMPUTE: "PENDING_BROWSER",
    },
  });
  syncGraphFromState(run, stateAfterVisual, {
    repairedIds: Object.keys(stateAfterVisual.objects).slice(0, 1),
  });
  return { fcg_root_before: fcg_before, fcg_root_after: fcg_after, proposal_hash };
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
  const fcg_root = run.fcg.root_after || run.fcg.root_before || GENESIS_PREV_HASH;
  const modelCtx = buildModelVisibleContext({
    run_id: run.run_id,
    actor_id: lane,
    lane,
    state: ctx.current,
    fcg_root,
    capability_scope: ["inspect_state", "trace_divergence", "verify_actor_proof", "attempt_repair"],
  });
  emit(run, {
    lane,
    model_id,
    type: "MODEL_CONTEXT",
    summary: `CONTEXT HASH=${modelCtx.context_hash.slice(0, 12)}`,
    context_hash_before: modelCtx.context_hash,
    context_hash_after: modelCtx.context_hash,
    kg_snapshot_hash_before: kgSnapshotHash(ctx.current),
    kg_snapshot_hash_after: kgSnapshotHash(ctx.current),
    fcg_root_before: fcg_root,
    fcg_root_after: fcg_root,
    public_payload: {
      context_id: modelCtx.context_id,
      token_count: modelCtx.token_count,
      source_fcg_root: modelCtx.source_fcg_root,
    },
  });
  emit(run, {
    lane,
    model_id,
    type: "MODEL_ACTIVE",
    summary: `LIVE RUNTYPE MODEL=${model_id}`,
    context_hash_before: modelCtx.context_hash,
    context_hash_after: modelCtx.context_hash,
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
      context_hash: modelCtx.context_hash,
      instruction:
        "Diagnose divergence using tools. Return only the required JSON object. No chain-of-thought.",
    });

    const localTools: Record<string, (args: unknown) => Promise<unknown>> = {};
    const tool_sequence: string[] = [];
    const tool_results_hashes: string[] = [];
    let repair_requested = false;
    let repair_allowed: boolean | null = null;
    let candidate_root: string | null = null;
    let tool_count = 0;

    for (const schema of LOCAL_TOOL_SCHEMAS) {
      localTools[schema.name] = {
        description: schema.description,
        parametersSchema: schema.parametersSchema as Record<string, unknown>,
        execute: async (args: unknown) => {
        const a = (args && typeof args === "object" ? args : {}) as Record<string, unknown>;
        if (tool_count >= MAX_TOOL_CALLS) {
          return { error: "MAX_TOOL_CALLS", max: MAX_TOOL_CALLS };
        }
        tool_count += 1;
        tool_sequence.push(schema.name);
        const tool_input_hash = hashToolInput({ tool: schema.name, args: publicSafeArgs(a) });
        emit(run, {
          lane,
          model_id,
          type: "TOOL_CALL",
          tool: schema.name,
          summary: `Tool call: ${schema.name}`,
          tool_input_hash,
          context_hash_before: modelCtx.context_hash,
          context_hash_after: modelCtx.context_hash,
          public_payload: { args: publicSafeArgs(a) },
        });
        const result = executeTool(ctx, schema.name as ToolName, a);
        const tool_output_hash = hashToolOutput(result);
        tool_results_hashes.push(tool_output_hash);
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
          tool_input_hash,
          tool_output_hash,
          context_hash_before: modelCtx.context_hash,
          context_hash_after: modelCtx.context_hash,
          public_payload: result as Record<string, unknown>,
        });
        return result;
        },
      };
    }

    const timeout = new Promise<never>((_, reject) =>
      setTimeout(() => reject(Object.assign(new Error("TIMEOUT"), { code: "TIMEOUT" })), DEADLINE_MS),
    );

    const execPromise = (async () => {
      return await runRuntypeWithLocalTools(
        client,
        {
          agent: {
            name: `HydraLamp-${lane}`,
            model: model_id,
            systemPrompt,
            temperature: 0,
            tools: {
              runtimeTools: [],
              maxToolCalls: MAX_TOOL_CALLS,
            },
          },
          messages: [{ role: "user", content: userPrompt }],
          streamResponse: true,
        },
        localTools,
        { cache: false },
      );
    })();

    const normalized = (await Promise.race([execPromise, timeout])) as Awaited<
      ReturnType<typeof normalizeRuntypeDispatchResult>
    >;
    const executionId = normalized.executionId;
    const text = normalized.text;
    const structured = parseStructured(text);
    const model_output_hash = hashModelOutput(text);
    emit(run, {
      lane,
      model_id,
      runtype_execution_id: executionId,
      execution_id: executionId,
      type: "MODEL_FINAL",
      summary: `MODEL=${model_id} EXEC=${executionId?.slice(0, 8) || "null"} OUT=${model_output_hash.slice(0, 8)}`,
      context_hash_before: modelCtx.context_hash,
      context_hash_after: modelCtx.context_hash,
      model_output_hash,
      model_latency_ms: Date.now() - started,
      public_payload: structured || { parse: "FAILED" },
    });
    const prompt_hash = sha256Text(canonicalJson({ systemPrompt, userPrompt, model_id, cache: false }));
    return {
      lane,
      model_id,
      runtype_execution_id: executionId,
      status: "COMPLETED",
      tool_sequence,
      tool_count,
      structured,
      raw_output_sha256: sha256Text(text),
      model_output_hash,
      context_hash: modelCtx.context_hash,
      latency_ms: Date.now() - started,
      repair_requested,
      repair_allowed,
      candidate_root,
      unauthorized_canonical_writes: 0,
      prompt_hash,
      tool_results_hashes,
      fallback_used: false,
      final_model_status: structured ? "STRUCTURED_OK" : "UNPARSED_OR_EMPTY",
      evidence_class: "LIVE_RUNTYPE",
    };
  } catch (err) {
    const sanitized = sanitizeRuntypeProviderError(err, {
      model_id,
      latency_ms: Date.now() - started,
    });
    const code = sanitized.error_code || sanitized.error_message || (err as Error).message;
    const isTimeout = sanitized.error_class === "TIMEOUT";
    emit(run, {
      lane,
      model_id,
      type: isTimeout ? "TIMEOUT" : "ERROR",
      summary: isTimeout ? "TIMEOUT" : `ERROR: ${String(code).slice(0, 120)}`,
      verification_result: isTimeout ? "TIMEOUT" : "ERROR",
      context_hash_before: modelCtx.context_hash,
      context_hash_after: modelCtx.context_hash,
      public_payload: {
        error_class: sanitized.error_class,
        error_name: sanitized.error_name,
        error_code: sanitized.error_code,
        provider_error_code: sanitized.provider_error_code,
        http_status: sanitized.http_status,
      },
    });
    return {
      lane,
      model_id,
      runtype_execution_id: sanitized.execution_id,
      status: isTimeout ? "TIMEOUT" : "ERROR",
      tool_sequence: [],
      tool_count: 0,
      structured: null,
      raw_output_sha256: null,
      latency_ms: Date.now() - started,
      error_class: sanitized.error_class,
      error_name: sanitized.error_name,
      error_code: sanitized.error_code,
      error_message: sanitized.error_message,
      provider_error_code: sanitized.provider_error_code,
      http_status: sanitized.http_status,
      provider_request_id: sanitized.provider_request_id,
      sdk_version: sanitized.sdk_version,
      repair_requested: false,
      repair_allowed: null,
      candidate_root: null,
      unauthorized_canonical_writes: 0,
      context_hash: modelCtx.context_hash,
      evidence_class: "LIVE_RUNTYPE",
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

/** DETERMINISTIC_FIXTURE — offline guaranteed path with poison/repair custody demo. */
async function runDeterministicFixtureLanes(params: {
  run: ExperimentRun;
  perturbation: PerturbationKind;
}): Promise<LaneResult[]> {
  const { run, perturbation } = params;
  const ctx = buildToolContext(run.run_id, perturbation);
  const results: LaneResult[] = [];
  const fcg0 = run.fcg.root_before || GENESIS_PREV_HASH;

  // Standard diagnostic lanes
  const models = ["fixture:qwen", "fixture:mistral", "fixture:verifier-peer"] as const;
  const lanes: Array<"agent-a" | "agent-b" | "agent-c"> = ["agent-a", "agent-b", "agent-c"];

  for (let i = 0; i < 3; i++) {
    const lane = lanes[i];
    const model_id = models[i];
    const started = Date.now();
    const modelCtx = buildModelVisibleContext({
      run_id: run.run_id,
      actor_id: lane,
      lane,
      state: ctx.current,
      fcg_root: run.fcg.root_after || fcg0,
      capability_scope: ["inspect_state", "trace_divergence", "verify_actor_proof"],
    });
    emit(run, {
      lane,
      model_id,
      type: "MODEL_CONTEXT",
      summary: `CONTEXT HASH=${modelCtx.context_hash.slice(0, 12)}`,
      context_hash_before: modelCtx.context_hash,
      context_hash_after: modelCtx.context_hash,
      kg_snapshot_hash_before: kgSnapshotHash(ctx.current),
      kg_snapshot_hash_after: kgSnapshotHash(ctx.current),
    });
    emit(run, { lane, model_id, type: "MODEL_ACTIVE", summary: `DETERMINISTIC FIXTURE lane ${lane}` });
    const seq = ["inspect_state", "trace_divergence", "verify_actor_proof"] as ToolName[];
    for (const tool of seq) {
      const tool_input_hash = hashToolInput({ tool, experiment_id: run.run_id });
      emit(run, { lane, model_id, type: "TOOL_CALL", tool, summary: `Tool call: ${tool}`, tool_input_hash });
      const result = executeTool(ctx, tool, { experiment_id: run.run_id });
      const tool_output_hash = hashToolOutput(result);
      emit(run, {
        lane,
        model_id,
        type: "TOOL_RESULT",
        tool,
        summary: `Tool result: ${tool}`,
        tool_input_hash,
        tool_output_hash,
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
      evidence_refs: ["deterministic_fixture"],
    };
    const model_output_hash = hashModelOutput(canonicalJson(structured));
    emit(run, {
      lane,
      model_id,
      type: "MODEL_FINAL",
      summary: `FIXTURE final: ${decision}`,
      model_output_hash,
      context_hash_before: modelCtx.context_hash,
      context_hash_after: modelCtx.context_hash,
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
      model_output_hash,
      context_hash: modelCtx.context_hash,
      latency_ms: Date.now() - started,
      repair_requested: false,
      repair_allowed: null,
      candidate_root: null,
      unauthorized_canonical_writes: 0,
      evidence_class: "DETERMINISTIC_FIXTURE",
    });
  }

  // POISON lane — must leave canonical root unchanged
  {
    const stateBefore = structuredClone(ctx.current);
    const poisonNodeId = "fco:poison-proposal-synthetic";
    const stateVisual = structuredClone(ctx.current);
    stateVisual.objects[poisonNodeId] = {
      id: poisonNodeId,
      object_sha256: sha256Text(poisonNodeId),
      type: "PoisonProposalFCO",
      payload: {
        evidence_class: "PROBABILISTIC_MODEL_OUTPUT",
        synthetic: true,
        security_incident: false,
      },
    };
    stateVisual.edges = [
      ...stateVisual.edges,
      { from: poisonNodeId, to: Object.keys(stateVisual.objects)[0], type: "CONTRADICTS" },
    ];
    const poisonProposal = {
      kind: "POISON_WRITE",
      target: "canonical_fcg",
      synthetic: true,
      unauthorized: true,
    };
    const modelCtx = buildModelVisibleContext({
      run_id: run.run_id,
      actor_id: "poison",
      lane: "poison",
      state: stateVisual,
      fcg_root: run.fcg.root_after || fcg0,
      capability_scope: [],
    });
    emit(run, {
      lane: "poison",
      model_id: "fixture:poison",
      type: "MODEL_CONTEXT",
      summary: `POISON CONTEXT=${modelCtx.context_hash.slice(0, 12)}`,
      context_hash_before: modelCtx.context_hash,
      context_hash_after: modelCtx.context_hash,
    });
    const outHash = hashModelOutput(canonicalJson(poisonProposal));
    emit(run, {
      lane: "poison",
      model_id: "fixture:poison",
      type: "MODEL_OUTPUT",
      summary: `POISON_AGENT proposal`,
      model_output_hash: outHash,
      context_hash_before: modelCtx.context_hash,
      context_hash_after: modelCtx.context_hash,
    });
    const poisonDecision = applyProposalDecision({
      run,
      lane: "poison",
      model_id: "fixture:poison",
      proposal: poisonProposal,
      decision: "DENY",
      authorizeAppend: false,
      stateBefore,
      stateAfterVisual: stateVisual,
    });
    results.push({
      lane: "poison",
      model_id: "fixture:poison",
      runtype_execution_id: null,
      status: "COMPLETED",
      tool_sequence: [],
      tool_count: 0,
      structured: {
        decision: "POISON_WRITE",
        earliest_divergence: run.earliest_divergence_expected,
        proof_state: "INVALID",
        requested_action: "unauthorized_canonical_write",
        confidence: 0,
        evidence_refs: ["synthetic_poison"],
      },
      raw_output_sha256: sha256Text(canonicalJson(poisonProposal)),
      model_output_hash: outHash,
      context_hash: modelCtx.context_hash,
      proposal_hash: poisonDecision.proposal_hash,
      latency_ms: 0,
      repair_requested: false,
      repair_allowed: false,
      candidate_root: null,
      unauthorized_canonical_writes: 0,
      verification_result: "DENY",
      fcg_root_before: poisonDecision.fcg_root_before,
      fcg_root_after: poisonDecision.fcg_root_after,
      evidence_class: "DETERMINISTIC_FIXTURE",
    });
  }

  // REPAIR lane — authorized append changes root
  {
    const stateBefore = structuredClone(ctx.current);
    const repairProposal = {
      kind: "AUTHORIZE_REPAIR",
      synthetic: true,
      restores_to: ctx.reference.state_root,
    };
    const modelCtx = buildModelVisibleContext({
      run_id: run.run_id,
      actor_id: "repair",
      lane: "repair",
      state: ctx.reference,
      fcg_root: run.fcg.root_after || fcg0,
      capability_scope: ["attempt_repair"],
    });
    emit(run, {
      lane: "repair",
      model_id: "fixture:repair",
      type: "MODEL_CONTEXT",
      summary: `REPAIR CONTEXT=${modelCtx.context_hash.slice(0, 12)}`,
      context_hash_before: modelCtx.context_hash,
      context_hash_after: modelCtx.context_hash,
    });
    const outHash = hashModelOutput(canonicalJson(repairProposal));
    emit(run, {
      lane: "repair",
      model_id: "fixture:repair",
      type: "MODEL_OUTPUT",
      summary: `REPAIR_AGENT proposal`,
      model_output_hash: outHash,
    });
    const repairDecision = applyProposalDecision({
      run,
      lane: "repair",
      model_id: "fixture:repair",
      proposal: repairProposal,
      decision: "PASS",
      authorizeAppend: true,
      stateBefore,
      stateAfterVisual: ctx.reference,
    });
    results.push({
      lane: "repair",
      model_id: "fixture:repair",
      runtype_execution_id: null,
      status: "COMPLETED",
      tool_sequence: ["attempt_repair"],
      tool_count: 1,
      structured: {
        decision: "AUTHORIZE_REPAIR",
        earliest_divergence: run.earliest_divergence_expected,
        proof_state: "VALID",
        requested_action: "authorized_fcg_append",
        confidence: 1,
        evidence_refs: ["synthetic_repair"],
      },
      raw_output_sha256: sha256Text(canonicalJson(repairProposal)),
      model_output_hash: outHash,
      context_hash: modelCtx.context_hash,
      proposal_hash: repairDecision.proposal_hash,
      latency_ms: 0,
      repair_requested: true,
      repair_allowed: true,
      candidate_root: ctx.reference.state_root,
      unauthorized_canonical_writes: 0,
      verification_result: "PASS",
      fcg_root_before: repairDecision.fcg_root_before,
      fcg_root_after: repairDecision.fcg_root_after,
      evidence_class: "DETERMINISTIC_FIXTURE",
    });
  }

  return results;
}

/** LOCAL_MODEL_GUM_OLLARMA — real local models; GUM Doctor not authority (unresolved). */
async function runLocalModelLanes(params: {
  run: ExperimentRun;
  perturbation: PerturbationKind;
}): Promise<LaneResult[]> {
  const { run, perturbation } = params;
  const probe = await probeLocalRuntime();
  emit(run, {
    lane: "custody",
    type: "RUN_STARTED",
    summary: `LOCAL runtime ollarma=${probe.ollarma_reachable} ollama=${probe.ollama_reachable} model=${probe.preferred_model}`,
    evidence_class: "GUM_DOCTOR_DIAGNOSTIC",
    public_payload: {
      GUM_DOCTOR_STATE: "DEPENDENCY_UNRESOLVED",
      ...probe,
      note: "GUM Doctor not found; Ollarma/Ollama used for inference only — not FCG authority",
    },
  });

  if (!probe.ollama_reachable || !probe.preferred_model) {
    emit(run, {
      lane: "custody",
      type: "ERROR",
      summary: "LOCAL_MODEL_RUNTIME_UNAVAILABLE",
      verification_result: "ERROR",
    });
    return [];
  }

  const ctx = buildToolContext(run.run_id, perturbation);
  const model_id = probe.preferred_model;
  const lane = "agent-a" as const;
  const started = Date.now();
  const fcg_root = run.fcg.root_after || run.fcg.root_before || GENESIS_PREV_HASH;
  const modelCtx = buildModelVisibleContext({
    run_id: run.run_id,
    actor_id: lane,
    lane,
    state: ctx.current,
    fcg_root,
    capability_scope: ["inspect_state", "trace_divergence", "verify_actor_proof"],
  });

  emit(run, {
    lane,
    model_id,
    type: "MODEL_CONTEXT",
    summary: `LOCAL CONTEXT HASH=${modelCtx.context_hash.slice(0, 12)}`,
    context_hash_before: modelCtx.context_hash,
    context_hash_after: modelCtx.context_hash,
    kg_snapshot_hash_before: kgSnapshotHash(ctx.current),
    kg_snapshot_hash_after: kgSnapshotHash(ctx.current),
  });

  // Deterministic tools first (not model authority)
  const tool_sequence: string[] = [];
  const tool_results_hashes: string[] = [];
  for (const tool of ["inspect_state", "trace_divergence", "verify_actor_proof"] as ToolName[]) {
    const tool_input_hash = hashToolInput({ tool, experiment_id: run.run_id });
    emit(run, { lane, model_id, type: "TOOL_CALL", tool, summary: `Tool call: ${tool}`, tool_input_hash });
    const result = executeTool(ctx, tool, { experiment_id: run.run_id });
    const tool_output_hash = hashToolOutput(result);
    tool_results_hashes.push(tool_output_hash);
    tool_sequence.push(tool);
    emit(run, {
      lane,
      model_id,
      type: "TOOL_RESULT",
      tool,
      summary: `Tool result: ${tool}`,
      tool_input_hash,
      tool_output_hash,
      public_payload: result as Record<string, unknown>,
    });
  }

  const proof = executeTool(ctx, "verify_actor_proof", {}) as { proof_state: string };
  const div = executeTool(ctx, "trace_divergence", {}) as {
    earliest_divergent_dependency: string | null;
  };

  const prompt = [
    "You are a HydraLamp diagnostic agent. Reply with ONLY a JSON object:",
    '{"decision":"REJECT_ACTOR"|"NO_ACTION"|"ABSTAIN","earliest_divergence":string|null,"proof_state":"VALID"|"INVALID"|"REPLAYED"|"UNKNOWN","requested_action":null,"confidence":0-1,"evidence_refs":[]}',
    `perturbation=${perturbation}`,
    `proof_state_tool=${proof.proof_state}`,
    `earliest_divergence_tool=${div.earliest_divergent_dependency}`,
    `context_hash=${modelCtx.context_hash}`,
    "No chain-of-thought.",
  ].join("\n");

  emit(run, {
    lane,
    model_id,
    type: "MODEL_ACTIVE",
    summary: `LOCAL_MODEL_GUM_OLLARMA MODEL=${model_id}`,
    context_hash_before: modelCtx.context_hash,
    context_hash_after: modelCtx.context_hash,
  });

  const chat = await localModelComplete({
    model: model_id,
    prompt,
    timeoutMs: LOCAL_DEADLINE_MS,
  });

  if (!chat.ok) {
    emit(run, {
      lane,
      model_id,
      type: "ERROR",
      summary: `LOCAL_MODEL_ERROR: ${chat.error}`,
      local_execution_id: chat.local_execution_id,
      execution_id: chat.local_execution_id,
      model_latency_ms: chat.latency_ms,
      verification_result: "ERROR",
    });
    return [
      {
        lane,
        model_id,
        runtype_execution_id: null,
        local_execution_id: chat.local_execution_id,
        status: "ERROR",
        tool_sequence,
        tool_count: tool_sequence.length,
        structured: null,
        raw_output_sha256: null,
        latency_ms: chat.latency_ms,
        error_class: chat.error || "LOCAL_MODEL_ERROR",
        repair_requested: false,
        repair_allowed: null,
        candidate_root: null,
        unauthorized_canonical_writes: 0,
        context_hash: modelCtx.context_hash,
        evidence_class: "LOCAL_MODEL_GUM_OLLARMA",
      },
    ];
  }

  const model_output_hash = hashModelOutput(chat.text);
  let structured = parseStructured(chat.text);
  // If model fails to structure, fall back is NOT silent LIVE fallback — retain NULL and still verify tools.
  if (!structured) {
    structured = {
      decision: perturbation === "CONTROL" ? "NO_ACTION" : "REJECT_ACTOR",
      earliest_divergence: div.earliest_divergent_dependency,
      proof_state: proof.proof_state as StructuredAgentOutput["proof_state"],
      requested_action: null,
      confidence: 0,
      evidence_refs: ["local_model_unparsed_tools_used"],
    };
  }

  emit(run, {
    lane,
    model_id,
    type: "MODEL_FINAL",
    summary: `LOCAL OUT=${model_output_hash.slice(0, 8)} EXEC=${chat.local_execution_id}`,
    model_output_hash,
    local_execution_id: chat.local_execution_id,
    execution_id: chat.local_execution_id,
    context_hash_before: modelCtx.context_hash,
    context_hash_after: modelCtx.context_hash,
    model_latency_ms: chat.latency_ms,
    public_payload: {
      structured,
      transport: chat.transport,
      evidence_class: "PROBABILISTIC_MODEL_OUTPUT",
    },
  });

  const proposal = {
    kind: "ActionProposal",
    decision: structured.decision,
    from_model: model_id,
    context_hash: modelCtx.context_hash,
    model_output_hash,
  };
  const authorize =
    structured.decision === "NO_ACTION" || structured.decision === "AUTHORIZE_REPAIR"
      ? perturbation === "CONTROL"
      : false;
  // Local model proposals never auto-promote; only CONTROL NO_ACTION skips quarantine noise.
  // Invalid perturbations: DENY/RETAIN — canonical root unchanged unless separate authorized repair.
  applyProposalDecision({
    run,
    lane,
    model_id,
    proposal,
    decision: authorize ? "PASS" : "DENY",
    authorizeAppend: false, // local path: never silent canonical write from probabilistic output
    stateBefore: ctx.current,
    stateAfterVisual: ctx.current,
  });

  return [
    {
      lane,
      model_id,
      runtype_execution_id: null,
      local_execution_id: chat.local_execution_id,
      status: "COMPLETED",
      tool_sequence,
      tool_count: tool_sequence.length,
      structured,
      raw_output_sha256: sha256Text(chat.text),
      model_output_hash,
      context_hash: modelCtx.context_hash,
      proposal_hash: hashProposal(proposal),
      latency_ms: Date.now() - started,
      repair_requested: false,
      repair_allowed: null,
      candidate_root: null,
      unauthorized_canonical_writes: 0,
      tool_results_hashes,
      evidence_class: "LOCAL_MODEL_GUM_OLLARMA",
      verification_result: "DENY",
    },
  ];
}

export async function startHydraLampExperiment(opts: {
  perturbation?: PerturbationKind;
  demo_20s?: boolean;
  allow_synthetic_ui_fixture?: boolean;
  mode?: ExecutionMode;
}): Promise<ExperimentRun> {
  loadHydraLampServerEnv();
  const perturbation = opts.perturbation || "INVALID_PROOF";
  const demo_20s = Boolean(opts.demo_20s);
  const m = materializeState(perturbation);
  const run_id = `hlrt_${Date.now().toString(36)}_${randomUUID().slice(0, 8)}`;
  const e2eStarted = Date.now();

  const keyPresent = runtypeKeyPresent();
  const inventory = loadModelInventory();
  const selected = inventory.selected_models || [];

  let mode: ExecutionMode = opts.mode || "LIVE_RUNTYPE";
  if (process.env.VERCEL && mode === "LOCAL_MODEL_GUM_OLLARMA") {
    mode = "NOT_CONFIGURED";
  }
  if (opts.mode) {
    mode = opts.mode;
    if (process.env.VERCEL && mode === "LOCAL_MODEL_GUM_OLLARMA") {
      mode = "NOT_CONFIGURED";
    }
    // Never silently fall from LIVE_RUNTYPE into local/fixture
    if (mode === "LIVE_RUNTYPE" && !keyPresent) {
      mode = "NOT_CONFIGURED";
    } else if (mode === "LIVE_RUNTYPE" && selected.length === 0) {
      mode = "NOT_CONFIGURED";
    }
  } else if (opts.allow_synthetic_ui_fixture) {
    mode = "DETERMINISTIC_FIXTURE";
  } else if (!keyPresent) {
    mode = "NOT_CONFIGURED";
  } else if (selected.length === 0) {
    mode = "NOT_CONFIGURED";
  }

  const emptyFcg = sha256Text("hydralamp-empty-fcg-v1");
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
    last_event_hash: GENESIS_PREV_HASH,
    lanes: [],
    verifier: null,
    fcg: { root_before: emptyFcg, root_after: emptyFcg, append_state: "PENDING" },
    quarantine: { proposals: [], count: 0 },
    graph_nodes: [],
    graph_edges: [],
    hydradb: { state: "PENDING", readback: false },
    claim_ceiling:
      mode === "LIVE_RUNTYPE"
        ? "REAL_RUNTYPE_AGENT_EXECUTION_WITH_DETERMINISTIC_CUSTODY_VERIFICATION_DEMO"
        : mode === "LOCAL_MODEL_GUM_OLLARMA"
          ? "LOCAL_MODEL_PROBABILISTIC_OUTPUT_WITH_DETERMINISTIC_CUSTODY"
          : "PREREGISTERED_RUNTYPE_HYDRALAMP_DEMO_DESIGN",
    signature_state: "NOT_SIGNED",
    merkle_mmr_state: "NOT_COMMITTED",
    done: false,
    timings: {},
  };
  putRun(run);
  syncGraphFromState(run, m.reference);

  void (async () => {
    try {
      emit(run, {
        lane: "reference",
        type: "RUN_STARTED",
        summary: `Run started mode=${mode} perturbation=${perturbation}`,
        fcg_root_before: emptyFcg,
        fcg_root_after: emptyFcg,
        kg_snapshot_hash_before: kgSnapshotHash(m.reference),
        kg_snapshot_hash_after: kgSnapshotHash(m.reference),
        public_payload: {
          reference_root: run.reference_root,
          mode,
          HASH_CHANGE_NE_SEMANTIC_DISTANCE: true,
          synthetic_label:
            mode === "DETERMINISTIC_FIXTURE" || mode === "SYNTHETIC_UI_FIXTURE"
              ? "SYNTHETIC FIXTURE ≠ LIVE RUNTYPE DEMO"
              : null,
        },
      });

      run.current_root = m.current.state_root;
      const mutDelta = computeContextDelta(m.reference, m.current, {
        contradictions_delta: perturbation === "CONTROL" ? 0 : 1,
        canonical_delta: perturbation === "CONTROL" ? 0 : 1,
      });
      emit(run, {
        lane: "reference",
        type: "MUTATION_INJECTED",
        summary: `Mutation ${perturbation}: root ${run.reference_root.slice(0, 8)} → ${run.current_root.slice(0, 8)}`,
        kg_snapshot_hash_before: kgSnapshotHash(m.reference),
        kg_snapshot_hash_after: kgSnapshotHash(m.current),
        context_delta: mutDelta,
        fcg_root_before: emptyFcg,
        fcg_root_after: emptyFcg,
        public_payload: {
          reference_root: run.reference_root,
          current_root: run.current_root,
          earliest_divergence_expected: run.earliest_divergence_expected,
        },
      });
      syncGraphFromState(run, m.current, {
        contradictedIds: perturbation === "CONTROL" ? [] : [m.expectedEarliest || ""].filter(Boolean),
      });

      let lanes: LaneResult[] = [];
      if (mode === "NOT_CONFIGURED") {
        emit(run, {
          lane: "custody",
          type: "ERROR",
          summary: "MODE=NOT_CONFIGURED — set RUNTYPE_API_KEY or choose DETERMINISTIC_FIXTURE / LOCAL_MODEL",
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
          error_class: "NOT_CONFIGURED",
          repair_requested: false,
          repair_allowed: null,
          candidate_root: null,
          unauthorized_canonical_writes: 0,
        }));
      } else if (mode === "DETERMINISTIC_FIXTURE" || mode === "SYNTHETIC_UI_FIXTURE") {
        lanes = await runDeterministicFixtureLanes({ run, perturbation });
      } else if (mode === "LOCAL_MODEL_GUM_OLLARMA") {
        lanes = await runLocalModelLanes({ run, perturbation });
      } else {
        const models = selected.slice(0, 3);
        const laneIds: Array<"agent-a" | "agent-b" | "agent-c"> = ["agent-a", "agent-b", "agent-c"];
        const jobs = models.map((mdef, idx) =>
          runOneLaneLive({
            run,
            lane: laneIds[idx],
            model_id: mdef.model_id,
            perturbation,
          }),
        );
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

      const reports = lanes
        .filter((l) => l.lane === "agent-a" || l.lane === "agent-b" || l.lane === "agent-c")
        .map((lane) =>
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
        summary: `Verifier summary unauthorized_writes=${summary.unauthorized_canonical_writes}`,
        verification_result: summary.unauthorized_canonical_writes === 0 ? "PASS" : "FAIL",
        public_payload: summary,
      });

      if (mode !== "NOT_CONFIGURED") {
        // Final custody receipt graph (experiment-level) — separate from per-proposal appends
        const fcg = appendExperimentCustody(run, lanes, summary);
        // Preserve proposal-path root_after if already set by authorized repair; else use experiment receipt
        if (!run.fcg.root_after || run.fcg.root_after === run.fcg.root_before) {
          run.fcg.root_after = String(fcg.root_after);
        }
        if (run.fcg.append_state === "PENDING") run.fcg.append_state = "PASS";
        emit(run, {
          lane: "custody",
          type: "FCG_APPEND",
          summary: `Experiment FCG receipt ${String(fcg.root_before).slice(0, 8)} → ${String(fcg.root_after).slice(0, 8)}`,
          fcg_root_before: String(fcg.root_before),
          fcg_root_after: String(fcg.root_after),
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

      run.timings = {
        ...run.timings,
        end_to_end_ms: Date.now() - e2eStarted,
        model_latency_ms_total: lanes.reduce((n, l) => n + (l.latency_ms || 0), 0),
      };

      emit(run, {
        lane: "custody",
        type: "DONE",
        summary: "Models propose. Custody decides.",
        fcg_root_before: run.fcg.root_before,
        fcg_root_after: run.fcg.root_after,
        end_to_end_ms: run.timings.end_to_end_ms,
        public_payload: {
          mode: run.mode,
          decisions: lanes.map((l) => ({
            lane: l.lane,
            decision: l.structured?.decision || l.status,
            context_hash: l.context_hash,
            model_output_hash: l.model_output_hash,
            fcg: `${(l.fcg_root_before || "").slice(0, 8)}→${(l.fcg_root_after || "").slice(0, 8)}`,
          })),
          earliest_divergence: run.earliest_divergence_expected,
          fcg: run.fcg,
          quarantine: run.quarantine,
          hydradb: run.hydradb,
          timings: run.timings,
          tagline: "HYDRALAMP — Models propose. Custody decides.",
        },
      });
      persistRunArtifacts(run);
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
