/**
 * Structural context delta — NOT hash Hamming distance.
 */
import { jensenShannonDivergence } from "../contextIceberg";
import type { FixtureState } from "./types";

export type ContextDelta = {
  nodes_added: number;
  nodes_removed: number;
  edges_added: number;
  edges_removed: number;
  claims_added: number;
  claims_removed: number;
  claims_contested: number;
  contradictions_delta: number;
  quarantine_delta: number;
  canonical_delta: number;
  evidence_class_counts_before: Record<string, number>;
  evidence_class_counts_after: Record<string, number>;
  model_context_token_delta: number | null;
  cloud_drift_0_100: number | "NOT_COMPUTED";
  cloud_drift_source: string | null;
};

function edgeKey(e: { type: string; from: string; to: string }) {
  return `${e.type}|${e.from}|${e.to}`;
}

function evidenceCounts(state: FixtureState): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const o of Object.values(state.objects)) {
    const cls = String(o.payload.evidence_class || o.type || "UNKNOWN");
    counts[cls] = (counts[cls] || 0) + 1;
  }
  return counts;
}

function distFromCounts(counts: Record<string, number>): number[] {
  const keys = Object.keys(counts).sort();
  if (!keys.length) return [1];
  return keys.map((k) => counts[k]);
}

export function computeContextDelta(
  before: FixtureState,
  after: FixtureState,
  opts?: {
    quarantine_delta?: number;
    canonical_delta?: number;
    contradictions_delta?: number;
    claims_contested?: number;
    token_before?: number | null;
    token_after?: number | null;
  },
): ContextDelta {
  const beforeNodes = new Set(Object.keys(before.objects));
  const afterNodes = new Set(Object.keys(after.objects));
  const beforeEdges = new Set(before.edges.map(edgeKey));
  const afterEdges = new Set(after.edges.map(edgeKey));

  const nodes_added = [...afterNodes].filter((id) => !beforeNodes.has(id)).length;
  const nodes_removed = [...beforeNodes].filter((id) => !afterNodes.has(id)).length;
  const edges_added = [...afterEdges].filter((id) => !beforeEdges.has(id)).length;
  const edges_removed = [...beforeEdges].filter((id) => !afterEdges.has(id)).length;

  const evidence_class_counts_before = evidenceCounts(before);
  const evidence_class_counts_after = evidenceCounts(after);

  let cloud_drift_0_100: number | "NOT_COMPUTED" = "NOT_COMPUTED";
  let cloud_drift_source: string | null = null;
  try {
    const left = distFromCounts(evidence_class_counts_before);
    const right = distFromCounts(evidence_class_counts_after);
    // Align lengths for JSD
    const width = Math.max(left.length, right.length);
    const L = Array.from({ length: width }, (_, i) => left[i] ?? 0);
    const R = Array.from({ length: width }, (_, i) => right[i] ?? 0);
    // Ensure positive mass
    if (L.some((x) => x > 0) && R.some((x) => x > 0)) {
      const js = jensenShannonDivergence(L, R);
      cloud_drift_0_100 = Math.round(js * 10000) / 100;
      cloud_drift_source = "apps/hydradg-web/lib/contextIceberg.ts#jensenShannonDivergence";
    }
  } catch {
    cloud_drift_0_100 = "NOT_COMPUTED";
    cloud_drift_source = null;
  }

  const token_before = opts?.token_before ?? null;
  const token_after = opts?.token_after ?? null;

  return {
    nodes_added,
    nodes_removed,
    edges_added,
    edges_removed,
    claims_added: nodes_added,
    claims_removed: nodes_removed,
    claims_contested: opts?.claims_contested ?? 0,
    contradictions_delta: opts?.contradictions_delta ?? 0,
    quarantine_delta: opts?.quarantine_delta ?? 0,
    canonical_delta: opts?.canonical_delta ?? (before.state_root === after.state_root ? 0 : 1),
    evidence_class_counts_before,
    evidence_class_counts_after,
    model_context_token_delta:
      token_before != null && token_after != null ? token_after - token_before : null,
    cloud_drift_0_100,
    cloud_drift_source,
  };
}
