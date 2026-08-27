/**
 * Stepped HydraLamp golden-path machine:
 * UNLOCK → REFERENCE → POISON → AGENT → VERIFY → ANTIDOTE → RESTORATION → RECEIPT
 *
 * Session FCG only — never silently mutates canonical scientific custody.
 */
import { readFileSync, existsSync, mkdirSync, appendFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import {
  appendSessionFcgRoot,
  createJudgeSession,
  getJudgeSession,
  type JudgeSession,
} from "./judgeSession";
import { materializeLongMemEvalIncident } from "./goldenPathIncident";
import { sha256Text, canonicalJson, repoRoot } from "./fixtures";
import { projectRunState } from "./cloudflareProjection";

export type GoldenPhase =
  | "LOCKED"
  | "UNLOCK"
  | "REFERENCE"
  | "POISON"
  | "AGENT"
  | "VERIFY"
  | "ANTIDOTE"
  | "RESTORATION"
  | "RECEIPT";

export type TransitionStatus =
  | "PASS"
  | "FAIL"
  | "NULL"
  | "NEGATIVE"
  | "TIMEOUT"
  | "ABSTAIN"
  | "ERROR"
  | "BLOCKED";

export type ModelSlot = {
  tag: string;
  params_b: number;
  digest_abbrev: string;
  status: "AVAILABLE" | "RUNNING" | "PASS" | "NULL" | "NEGATIVE" | "FAIL" | "TIMEOUT" | "ABSTAIN";
  diameter_px: number;
};

export type FcgTransition = {
  seq: number;
  phase: GoldenPhase;
  action: string;
  actor: string;
  tool_provider: string | null;
  model: ModelSlot | null;
  input_fco: string | null;
  output_fco: string | null;
  fcg_root_before: string;
  fcg_root_after: string;
  evidence_class: string;
  claim_ceiling: string;
  status: TransitionStatus;
  summary: string;
  timestamp: string;
  sha256: string;
};

export type GoldenPathRun = {
  schema: "hydralamp.golden_path_run.v1";
  run_id: string;
  session_id: string;
  namespace: string;
  phase: GoldenPhase;
  paused: boolean;
  follow_current: boolean;
  focus_target: "current" | "poison" | "divergence" | "restoration" | "centroid";
  task_prompt: string;
  transitions: FcgTransition[];
  fcg_root_initial: string;
  fcg_root_current: string;
  fco_lineage: { A?: string; B?: string; C?: string; auth?: string };
  earliest_divergence: string | null;
  model_ladder: ModelSlot[];
  active_model_index: number;
  escalation_reason: string | null;
  providers: {
    cloudflare: string;
    runtype: string;
    mitosis: string;
    mistral: string;
  };
  result_panel: Record<string, unknown> | null;
  claim_ceiling: string;
  signature_state: "NOT_SIGNED";
  merkle_mmr_state: "NOT_COMMITTED";
  hydradb_state: string;
  done: boolean;
  created_at: string;
};

const PHASE_ORDER: GoldenPhase[] = [
  "UNLOCK",
  "REFERENCE",
  "POISON",
  "AGENT",
  "VERIFY",
  "ANTIDOTE",
  "RESTORATION",
  "RECEIPT",
];

const runs = new Map<string, GoldenPathRun>();

function modelDiameter(params_b: number): number {
  // log scale so 14B doesn't erase 0.5B
  return Math.round(18 + 14 * Math.log2(1 + params_b));
}

function buildLadder(): ModelSlot[] {
  const specs: Array<[string, number, string]> = [
    ["qwen2.5:0.5b", 0.5, "a8b0c5157701"],
    ["qwen2.5:1.5b", 1.5, "65ec06548149"],
    ["qwen3:1.7b", 1.7, "8f68893c685c"],
    ["llama3.2:3b", 3, "a80c4f17acd5"],
    ["qwen2.5-coder:7b", 7, "dae161e27b0e"],
    ["deepseek-r1:14b", 14, "c333b7232bdb"],
  ];
  return specs.map(([tag, params_b, dig]) => ({
    tag,
    params_b,
    digest_abbrev: dig,
    status: "AVAILABLE" as const,
    diameter_px: modelDiameter(params_b),
  }));
}

function evalDir(): string {
  const d = path.join(repoRoot(), "eval", "hydralamp_golden_path_20260827");
  mkdirSync(d, { recursive: true });
  return d;
}

function persistTransition(run: GoldenPathRun, t: FcgTransition) {
  const p = path.join(evalDir(), "FCG_TRANSITION_RECEIPTS.jsonl");
  appendFileSync(p, JSON.stringify({ run_id: run.run_id, session_id: run.session_id, ...t }) + "\n");
}

function emitTransition(
  run: GoldenPathRun,
  partial: Omit<FcgTransition, "seq" | "fcg_root_before" | "fcg_root_after" | "sha256" | "timestamp"> & {
    fcg_root_after?: string;
  },
): FcgTransition {
  const before = run.fcg_root_current;
  const after =
    partial.fcg_root_after ||
    appendSessionFcgRoot(before, partial.action, {
      phase: partial.phase,
      output_fco: partial.output_fco,
      status: partial.status,
    });
  const t: FcgTransition = {
    seq: run.transitions.length + 1,
    phase: partial.phase,
    action: partial.action,
    actor: partial.actor,
    tool_provider: partial.tool_provider,
    model: partial.model,
    input_fco: partial.input_fco,
    output_fco: partial.output_fco,
    fcg_root_before: before,
    fcg_root_after: after,
    evidence_class: partial.evidence_class,
    claim_ceiling: partial.claim_ceiling,
    status: partial.status,
    summary: partial.summary,
    timestamp: new Date().toISOString(),
    sha256: "",
  };
  t.sha256 = sha256Text(canonicalJson({ ...t, sha256: undefined }));
  run.transitions.push(t);
  run.fcg_root_current = after;
  run.phase = partial.phase;
  persistTransition(run, t);
  void projectRunState({
    run_id: run.run_id,
    lifecycle:
      partial.phase === "REFERENCE"
        ? "NORMAL"
        : partial.phase === "POISON"
          ? "POISON"
          : partial.phase === "VERIFY"
            ? "QUARANTINED"
            : partial.phase === "ANTIDOTE"
              ? "ANTIDOTE"
              : partial.phase === "RESTORATION" || partial.phase === "RECEIPT"
                ? "RESTORED"
                : "NORMAL",
    custody_state: "CUSTODY_VERIFIED",
    event_count: run.transitions.length,
    last_event_hash: t.sha256,
    fcg_root: after,
    provider_badge: "BOUNDED",
  });
  return t;
}

export function getGoldenRun(runId: string): GoldenPathRun | undefined {
  return runs.get(runId);
}

export function unlockGoldenPath(params: {
  judge_key: string;
  task_prompt?: string;
}): { ok: true; run: GoldenPathRun; session: JudgeSession } | { ok: false; error: string; code: string } {
  const unlocked = createJudgeSession({
    judge_key: params.judge_key,
    task_prompt: params.task_prompt,
  });
  if (!unlocked.ok) return unlocked;

  const session = unlocked.session;
  const run_id = `gp_${Date.now().toString(36)}_${session.session_id.slice(-8)}`;
  const ladder = buildLadder();
  const run: GoldenPathRun = {
    schema: "hydralamp.golden_path_run.v1",
    run_id,
    session_id: session.session_id,
    namespace: session.namespace,
    phase: "UNLOCK",
    paused: true,
    follow_current: true,
    focus_target: "current",
    task_prompt: session.task_prompt,
    transitions: [],
    fcg_root_initial: session.fcg_root,
    fcg_root_current: session.fcg_root,
    fco_lineage: { auth: session.authorization_fco_id },
    earliest_divergence: null,
    model_ladder: ladder,
    active_model_index: 0,
    escalation_reason: null,
    providers: {
      cloudflare: process.env.HYDRALAMP_CF_WORKER_URL?.trim()
        ? "CLOUDFLARE INTEGRATION READY / LIVE URL SET"
        : "CLOUDFLARE INTEGRATION READY / NOT LIVE",
      runtype: process.env.RUNTYPE_API_KEY?.trim() ? "RUNTYPE KEY PRESENT — LIVE PATH ERROR-PRONE" : "RUNTYPE NOT CONFIGURED",
      mitosis: "CORTEX_MEMORY=BLOCKED_TRIAL_EXPIRED",
      mistral: "FUTURE_OPTIONAL",
    },
    result_panel: null,
    claim_ceiling: "DEMO_SESSION_MECHANISM_CANARY_NOT_EMPIRICAL_CLAIM",
    signature_state: "NOT_SIGNED",
    merkle_mmr_state: "NOT_COMMITTED",
    hydradb_state: "PENDING_READBACK",
    done: false,
    created_at: new Date().toISOString(),
  };
  runs.set(run_id, run);
  emitTransition(run, {
    phase: "UNLOCK",
    action: "JUDGE_SESSION_AUTHORIZE",
    actor: "judge",
    tool_provider: null,
    model: null,
    input_fco: null,
    output_fco: session.authorization_fco_id,
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
    claim_ceiling: session.claim_ceiling,
    status: "PASS",
    summary: "JUDGE SESSION — AUTHORIZED (demo capability, not cryptographic signature)",
  });
  writeFileSync(path.join(evalDir(), `${run_id}.json`), JSON.stringify(run, null, 2) + "\n");
  return { ok: true, run, session };
}

export function stepGoldenPath(runId: string): GoldenPathRun {
  const run = runs.get(runId);
  if (!run) throw new Error("RUN_NOT_FOUND");
  if (run.done) return run;

  const idx = PHASE_ORDER.indexOf(run.phase);
  const next = PHASE_ORDER[Math.min(idx + 1, PHASE_ORDER.length - 1)];
  if (next === run.phase && run.phase === "RECEIPT") {
    run.done = true;
    return run;
  }

  const incident = materializeLongMemEvalIncident();

  switch (next) {
    case "REFERENCE": {
      run.fco_lineage.A = incident.fco_A;
      emitTransition(run, {
        phase: "REFERENCE",
        action: "MATERIALIZE_REFERENCE",
        actor: "hydradg",
        tool_provider: "HYDRADG",
        model: null,
        input_fco: run.fco_lineage.auth || null,
        output_fco: incident.fco_A,
        evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
        claim_ceiling: incident.packet.claim_ceiling,
        status: "PASS",
        summary: "REFERENCE: accepted evidence-bounded LongMemEval state A",
      });
      run.focus_target = "current";
      break;
    }
    case "POISON": {
      run.fco_lineage.B = incident.fco_B;
      run.earliest_divergence = incident.fco_B;
      emitTransition(run, {
        phase: "POISON",
        action: "INJECT_UNTRUSTED_OVERCLAIM",
        actor: "untrusted_candidate",
        tool_provider: null,
        model: null,
        input_fco: incident.fco_A,
        output_fco: incident.fco_B,
        evidence_class: "INFERENCE_HYPOTHESIS",
        claim_ceiling: "UNTRUSTED_OVERCLAIM_CANDIDATE",
        status: "NEGATIVE",
        summary: "POISON: untrusted overclaim B contradicts A (retained, not erased)",
      });
      run.focus_target = "poison";
      break;
    }
    case "AGENT": {
      const model = { ...run.model_ladder[run.active_model_index]! };
      model.status = "RUNNING";
      run.model_ladder[run.active_model_index] = model;
      // Deterministic agent over poisoned state — smallest model first
      const insufficient = false; // demo: smallest model completes structured refusal of poison as authority
      let used = model;
      if (insufficient && run.active_model_index < run.model_ladder.length - 1) {
        run.escalation_reason = "EVIDENCE INSUFFICIENT — ESCALATING MODEL";
        run.active_model_index += 1;
        used = { ...run.model_ladder[run.active_model_index]!, status: "RUNNING" };
        run.model_ladder[run.active_model_index] = used;
      }
      used = { ...used, status: "PASS" };
      run.model_ladder[run.active_model_index] = used;
      emitTransition(run, {
        phase: "AGENT",
        action: "RESOLVE_CUSTOMER_REQUEST_OVER_CURRENT_EVIDENCE",
        actor: "agent",
        tool_provider: run.providers.runtype.includes("NOT CONFIGURED")
          ? "DETERMINISTIC_LOCAL_AGENT"
          : "RUNTYPE_OR_LOCAL_FALLBACK",
        model: used,
        input_fco: incident.fco_B,
        output_fco: `fco:agent_decision_${sha256Text(run.run_id + used.tag).slice(0, 16)}`,
        evidence_class: "PROBABILISTIC_MODEL_OUTPUT",
        claim_ceiling: "PROBABILISTIC_MODEL_OUTPUT",
        status: "PASS",
        summary: `AGENT (${used.tag} · ${used.params_b}B): task over poisoned state; model opinion not canonical`,
      });
      run.focus_target = "current";
      break;
    }
    case "VERIFY": {
      run.focus_target = "divergence";
      emitTransition(run, {
        phase: "VERIFY",
        action: "DETECT_EARLIEST_DIVERGENCE",
        actor: "deterministic_verifier",
        tool_provider: "HYDRALAMP_VERIFIER",
        model: null,
        input_fco: incident.fco_B,
        output_fco: incident.fco_B,
        evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
        claim_ceiling: incident.packet.claim_ceiling,
        status: "PASS",
        summary: `VERIFY: earliest divergent dependency = ${incident.fco_B.slice(0, 18)}…; poison quarantined`,
      });
      break;
    }
    case "ANTIDOTE": {
      emitTransition(run, {
        phase: "ANTIDOTE",
        action: "APPLY_EVIDENCE_BOUNDED_ANTIDOTE",
        actor: "custody",
        tool_provider: "HYDRADG",
        model: null,
        input_fco: incident.packet_sha256,
        output_fco: incident.fco_C,
        evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
        claim_ceiling: incident.packet.claim_ceiling,
        status: "PASS",
        summary: "ANTIDOTE: retrieve frozen K5/K10 evidence; reject maximize-context overclaim",
      });
      run.fco_lineage.C = incident.fco_C;
      run.focus_target = "restoration";
      break;
    }
    case "RESTORATION": {
      emitTransition(run, {
        phase: "RESTORATION",
        action: "RESTORE_CORRECTED_SUCCESSOR",
        actor: "custody",
        tool_provider: "HYDRADG",
        model: null,
        input_fco: incident.fco_A,
        output_fco: incident.fco_C,
        evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
        claim_ceiling: incident.packet.claim_ceiling,
        status: "PASS",
        summary: "RESTORATION: C current; A and B remain visible as superseded/quarantined lineage",
      });
      run.focus_target = "restoration";
      break;
    }
    case "RECEIPT": {
      const first = run.transitions[0];
      run.result_panel = {
        STATUS: "RESTORED",
        POISON: run.fco_lineage.B,
        EARLIEST_DIVERGENCE: run.earliest_divergence,
        AGENT: run.model_ladder[run.active_model_index]
          ? `${run.model_ladder[run.active_model_index]!.tag} · ${run.model_ladder[run.active_model_index]!.params_b}B`
          : null,
        EXECUTION: `${run.providers.cloudflare} | ${run.providers.runtype}`,
        "MEMORY/VERIFY": run.providers.mitosis,
        FCG: `${run.fcg_root_initial.slice(0, 12)}… → ${run.fcg_root_current.slice(0, 12)}…`,
        CUSTODY: "HASHED",
        SIGNATURE: "NOT_SIGNED",
        "MERKLE/MMR": "NOT_COMMITTED",
        NOTE: "Demo/session FCG only — not canonical science promotion",
      };
      emitTransition(run, {
        phase: "RECEIPT",
        action: "EMIT_SESSION_RECEIPT",
        actor: "hydralamp",
        tool_provider: "HYDRALAMP",
        model: null,
        input_fco: first?.output_fco || null,
        output_fco: run.fco_lineage.C || null,
        evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
        claim_ceiling: run.claim_ceiling,
        status: "PASS",
        summary: "RECEIPT: session complete; TRACE THE REPAIR available",
      });
      run.done = true;
      run.paused = true;
      break;
    }
    default:
      break;
  }

  writeFileSync(path.join(evalDir(), `${run.run_id}.json`), JSON.stringify(run, null, 2) + "\n");
  return run;
}

export function runUntilPausedOrDone(runId: string, maxSteps = 8): GoldenPathRun {
  let run = getGoldenRun(runId);
  if (!run) throw new Error("RUN_NOT_FOUND");
  run.paused = false;
  for (let i = 0; i < maxSteps; i++) {
    if (run.done || run.paused) break;
    run = stepGoldenPath(runId);
    // Auto-run continues unless operator paused mid-flight
    if (getGoldenRun(runId)?.paused) break;
  }
  return getGoldenRun(runId)!;
}

export function pauseGoldenPath(runId: string): GoldenPathRun {
  const run = runs.get(runId);
  if (!run) throw new Error("RUN_NOT_FOUND");
  run.paused = true;
  return run;
}

export function setFollowCurrent(runId: string, on: boolean): GoldenPathRun {
  const run = runs.get(runId);
  if (!run) throw new Error("RUN_NOT_FOUND");
  run.follow_current = on;
  return run;
}

export function setFocus(
  runId: string,
  target: GoldenPathRun["focus_target"],
): GoldenPathRun {
  const run = runs.get(runId);
  if (!run) throw new Error("RUN_NOT_FOUND");
  run.focus_target = target;
  run.follow_current = false;
  return run;
}

export function resetGoldenPath(params: {
  judge_key: string;
  task_prompt?: string;
}): ReturnType<typeof unlockGoldenPath> {
  // New session — prior sessions retained on disk / in map
  return unlockGoldenPath(params);
}

export function publicRunView(run: GoldenPathRun) {
  const session = getJudgeSession(run.session_id);
  return {
    ...run,
    judge_label: session?.label || "JUDGE SESSION — AUTHORIZED",
    cryptographic_signed: false,
    phase_rail: PHASE_ORDER,
  };
}
