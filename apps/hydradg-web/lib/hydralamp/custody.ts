import { writeFileSync, mkdirSync, existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { makeFcoNode, sha256Text, canonicalJson } from "../fco";
import type { ExperimentRun, LaneResult } from "./types";
import { repoRoot } from "./fixtures";

export function appendExperimentCustody(run: ExperimentRun, lanes: LaneResult[], verifier: Record<string, unknown>) {
  const rootBefore = run.fcg.root_before || sha256Text("hydralamp-empty-fcg-v1");
  const nodes = [];
  const edges: Array<{ from: string; to: string; type: string }> = [];

  const fixture = makeFcoNode("SyntheticFixtureFCO", {
    run_id: run.run_id,
    synthetic: true,
    security_incident: false,
    reference_root: run.reference_root,
    current_root: run.current_root,
    evidence_class: "SYNTHETIC_DEMO_FIXTURE",
  });
  nodes.push(fixture);

  const experiment = makeFcoNode("ExperimentFCO", {
    run_id: run.run_id,
    mode: run.mode,
    perturbation: run.perturbation,
    claim_ceiling: run.claim_ceiling,
  });
  nodes.push(experiment);
  edges.push({ from: fixture.id, to: experiment.id, type: "SUPPORTS" });

  const laneFcos = lanes.map((lane) => {
    const exec = makeFcoNode("AgentExecutionFCO", {
      lane: lane.lane,
      model_id: lane.model_id,
      runtype_execution_id: lane.runtype_execution_id,
      status: lane.status,
      tool_sequence: lane.tool_sequence,
      latency_ms: lane.latency_ms,
      evidence_class: "PROBABILISTIC_MODEL_OUTPUT",
    });
    const output = makeFcoNode("ProbabilisticOutputFCO", {
      lane: lane.lane,
      raw_output_sha256: lane.raw_output_sha256,
      structured: lane.structured,
      evidence_class: "PROBABILISTIC_MODEL_OUTPUT",
    });
    edges.push({ from: experiment.id, to: exec.id, type: "HAS_EXECUTION" });
    edges.push({ from: exec.id, to: output.id, type: "PRODUCED" });
    nodes.push(exec, output);
    return { exec, output };
  });

  const verification = makeFcoNode("DeterministicVerificationFCO", {
    verifier,
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
  });
  nodes.push(verification);
  for (const { output } of laneFcos) {
    edges.push({ from: output.id, to: verification.id, type: "VERIFIED_BY" });
  }

  const result = makeFcoNode("ResultFCO", {
    run_id: run.run_id,
    unauthorized_canonical_writes: (verifier as { unauthorized_canonical_writes?: number }).unauthorized_canonical_writes ?? 0,
    earliest_divergence: run.earliest_divergence_expected,
    decisions: lanes.map((l) => ({
      lane: l.lane,
      decision: l.structured?.decision ?? l.status,
    })),
  });
  nodes.push(result);
  edges.push({ from: verification.id, to: result.id, type: "YIELDS" });

  const hypothesis = makeFcoNode("HypothesisFCO", {
    statement: "Models propose. Custody decides.",
    claim_ceiling: run.claim_ceiling,
  });
  nodes.push(hypothesis);
  edges.push({ from: result.id, to: hypothesis.id, type: "SUPPORTS" });

  const graph = { nodes, edges, root_before: rootBefore };
  const root_after = sha256Text(canonicalJson(graph));

  const outDir = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "runs", run.run_id);
  mkdirSync(outDir, { recursive: true });
  const receipt = {
    schema: "hydralamp.runtype.fcg_receipt.v1",
    run_id: run.run_id,
    root_before: rootBefore,
    root_after,
    node_count: nodes.length,
    edge_count: edges.length,
    signature_state: "NOT_SIGNED",
    merkle_mmr_state: "NOT_COMMITTED",
    append_state: "PASS",
  };
  writeFileSync(path.join(outDir, "FCG_RECEIPT.json"), JSON.stringify(receipt, null, 2) + "\n");
  writeFileSync(path.join(outDir, "FCG_GRAPH.json"), JSON.stringify(graph, null, 2) + "\n");
  return receipt;
}

export function tryHydraDbProjection(runId: string, fcgReceipt: Record<string, unknown>) {
  // Projection is best-effort. Never roll back FCG. Do not claim PROJECTED without readback.
  const outDir = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "runs", runId);
  const hasKey = Boolean(process.env.HYDRADB_API_KEY);
  if (!hasKey) {
    const receipt = {
      schema: "hydralamp.runtype.hydradb_receipt.v1",
      state: "SKIPPED",
      reason: "HYDRADB_API_KEY_ABSENT_OR_NOT_USED_IN_THIS_PATH",
      readback: false,
      fcg_root_after: fcgReceipt.root_after,
    };
    writeFileSync(path.join(outDir, "HYDRADB_RECEIPT.json"), JSON.stringify(receipt, null, 2) + "\n");
    return receipt;
  }
  // Bounded: write a pending projection intent only; live cloud write is operator-gated.
  const receipt = {
    schema: "hydralamp.runtype.hydradb_receipt.v1",
    state: "PENDING",
    reason: "PROJECTION_INTENT_RECORDED_LIVE_WRITE_OPERATOR_GATED",
    readback: false,
    fcg_root_after: fcgReceipt.root_after,
    note: "HydraDB is projection/query substrate, not canonical custody.",
  };
  writeFileSync(path.join(outDir, "HYDRADB_RECEIPT.json"), JSON.stringify(receipt, null, 2) + "\n");
  return receipt;
}

export function persistRunArtifacts(run: ExperimentRun) {
  const outDir = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "runs", run.run_id);
  mkdirSync(outDir, { recursive: true });
  writeFileSync(path.join(outDir, "RUN_RECEIPT.json"), JSON.stringify(run, null, 2) + "\n");
  writeFileSync(
    path.join(outDir, "EVENTS.jsonl"),
    run.events.map((e) => JSON.stringify(e)).join("\n") + "\n",
  );
  const hashes = Object.fromEntries(
    run.lanes.map((l) => [l.lane, { model_id: l.model_id, raw_output_sha256: l.raw_output_sha256 }]),
  );
  writeFileSync(path.join(outDir, "MODEL_OUTPUT_HASHES.json"), JSON.stringify(hashes, null, 2) + "\n");
  if (run.verifier) {
    writeFileSync(path.join(outDir, "VERIFICATION.json"), JSON.stringify(run.verifier, null, 2) + "\n");
  }
  return outDir;
}

export function readRun(runId: string): ExperimentRun | null {
  const p = path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "runs", runId, "RUN_RECEIPT.json");
  if (!existsSync(p)) return null;
  return JSON.parse(readFileSync(p, "utf8")) as ExperimentRun;
}
