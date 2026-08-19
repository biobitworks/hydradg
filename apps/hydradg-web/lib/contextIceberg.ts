export type IcebergMetricSource =
  | "OBJECT_SPECIFIC"
  | "STATE_INHERITED"
  | "DEMO_CONTROL"
  | "PENDING";

export type ContextIcebergScopeMetric = {
  scope_id: string;
  scope_type: string;
  t?: number;
  delta_g_star: number | null;
  cloud_drift_0_100: number | null;
  burden_0_1?: number | null;
  metric_source: IcebergMetricSource;
};

export type ContextIcebergObservation = {
  schema: "hydradg.context_iceberg_projection.v1";
  state: "READY" | "PENDING" | "INCONCLUSIVE" | "ERROR";
  read_only: true;
  canonical_binding_state:
    | "BOUND"
    | "PENDING_CANONICAL_FCO_FCG_BINDING"
    | "NOT_APPLICABLE_DEMO_CONTROL";
  evidence_class: string;
  claim_ceiling: string;
  reference_state_root: string | null;
  current_state_root: string | null;
  distribution_schema_version: string | null;
  distribution_schema_sha256: string | null;
  scorer_version: string | null;
  scorer_code_sha256: string | null;
  config_sha256: string | null;
  artifact_sha256?: string | null;
  scores: {
    g_current: number | null;
    g_reference: number | null;
    delta_g_star: number | null;
    js_divergence: number | null;
    cloud_drift_0_100: number | null;
  };
  outcomes: {
    delta_hit_at_k: number | null;
    delta_recall_at_k: number | null;
    delta_evidence_path_coverage: number | null;
    delta_provenance_completeness: number | null;
    mean_answer_rank_displacement: number | null;
  };
  governance: {
    provenance_completeness: number | null;
    orphan_fco_count: number | null;
    broken_fcg_edge_count: number | null;
    artifact_hash_mismatch_count: number | null;
    semantic_abstention_rate: number | null;
    unresolved_contradiction_rate: number | null;
    signature_state: string;
    merkle_state: string;
  };
  null_hypotheses: string[];
  scopes: ContextIcebergScopeMetric[];
  blocker?: string | null;
};

export const PENDING_CONTEXT_ICEBERG: ContextIcebergObservation = {
  schema: "hydradg.context_iceberg_projection.v1",
  state: "PENDING",
  read_only: true,
  canonical_binding_state: "PENDING_CANONICAL_FCO_FCG_BINDING",
  evidence_class: "DISPLAY_CONTRACT_ONLY_NO_SCIENTIFIC_SCORE_ESTABLISHED",
  claim_ceiling: "CONTEXT_ICEBERG_DISPLAY_CONTRACT_ONLY",
  reference_state_root: null,
  current_state_root: null,
  distribution_schema_version: null,
  distribution_schema_sha256: null,
  scorer_version: null,
  scorer_code_sha256: null,
  config_sha256: null,
  scores: {
    g_current: null,
    g_reference: null,
    delta_g_star: null,
    js_divergence: null,
    cloud_drift_0_100: null,
  },
  outcomes: {
    delta_hit_at_k: null,
    delta_recall_at_k: null,
    delta_evidence_path_coverage: null,
    delta_provenance_completeness: null,
    mean_answer_rank_displacement: null,
  },
  governance: {
    provenance_completeness: null,
    orphan_fco_count: null,
    broken_fcg_edge_count: null,
    artifact_hash_mismatch_count: null,
    semantic_abstention_rate: null,
    unresolved_contradiction_rate: null,
    signature_state: "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
    merkle_state: "NOT_MERKLE_COMMITTED",
  },
  null_hypotheses: [
    "H0-DISTRIBUTION: context distribution is not detectably different from the frozen reference beyond the preregistered criterion.",
    "H0-GIBBS: delta G* = 0.",
    "H0-ACCURACY-LINK: CloudDrift is not associated with a change in hit/recall.",
    "H0-GIBBS-ACCURACY-LINK: delta G* is not associated with a change in hit/recall.",
    "H0-PROVENANCE: context redistribution does not imply a custody/provenance break.",
  ],
  scopes: [],
  blocker: "NO_FROZEN_CONTEXT_ICEBERG_RECEIPT",
};

function assertFiniteNonNegative(value: number, label: string) {
  if (!Number.isFinite(value) || value < 0) {
    throw new Error(`${label} must be finite and non-negative`);
  }
}

export function cloudDriftFromFrozenVocabulary(
  vocabulary: readonly string[],
  referenceCounts: Readonly<Record<string, number>>,
  currentCounts: Readonly<Record<string, number>>,
) {
  if (!vocabulary.length) throw new Error("Frozen context-cloud vocabulary is empty");
  const allowed = new Set(vocabulary);
  for (const key of Object.keys(referenceCounts)) {
    if (!allowed.has(key)) throw new Error(`Reference contains undeclared bucket: ${key}`);
  }
  for (const key of Object.keys(currentCounts)) {
    if (!allowed.has(key)) throw new Error(`Current state contains undeclared bucket: ${key}`);
  }

  const ref = vocabulary.map((key) => Number(referenceCounts[key] ?? 0));
  const cur = vocabulary.map((key) => Number(currentCounts[key] ?? 0));
  ref.forEach((value, index) => assertFiniteNonNegative(value, `reference[${vocabulary[index]}]`));
  cur.forEach((value, index) => assertFiniteNonNegative(value, `current[${vocabulary[index]}]`));

  const refTotal = ref.reduce((sum, value) => sum + value, 0);
  const curTotal = cur.reduce((sum, value) => sum + value, 0);
  if (refTotal <= 0 || curTotal <= 0) throw new Error("Both context-cloud distributions must have positive mass");

  const p = ref.map((value) => value / refTotal);
  const q = cur.map((value) => value / curTotal);
  const m = p.map((value, index) => 0.5 * (value + q[index]));
  const kl = (a: number[], b: number[]) =>
    a.reduce((sum, value, index) => {
      if (value === 0) return sum;
      return sum + value * Math.log2(value / b[index]);
    }, 0);
  const jsd = 0.5 * kl(p, m) + 0.5 * kl(q, m);
  return {
    js_divergence: jsd,
    cloud_drift_0_100: Math.max(0, Math.min(100, jsd * 100)),
  };
}

export function deltaGDirection(deltaG: number | null | undefined) {
  if (deltaG == null || !Number.isFinite(deltaG)) return "PENDING" as const;
  if (Math.abs(deltaG) < 1e-12) return "STABLE" as const;
  return deltaG < 0 ? ("LOWER" as const) : ("HIGHER" as const);
}

export function contextCloudVisual(metric: {
  delta_g_star?: number | null;
  cloud_drift_0_100?: number | null;
  burden_0_1?: number | null;
}) {
  const drift = metric.cloud_drift_0_100 == null
    ? 0
    : Math.max(0, Math.min(100, metric.cloud_drift_0_100));
  const burden = metric.burden_0_1 == null
    ? 0
    : Math.max(0, Math.min(1, metric.burden_0_1));
  const direction = deltaGDirection(metric.delta_g_star);
  const fill = direction === "LOWER"
    ? "hsl(205 68% 67%)"
    : direction === "HIGHER"
      ? "hsl(34 78% 64%)"
      : "hsl(215 12% 72%)";
  return {
    direction,
    fill,
    radius_scale: 1 + burden * 0.45,
    halo_px: 3 + (drift / 100) * 22,
    halo_alpha: 0.08 + (drift / 100) * 0.34,
    halo_line_width: 1 + (drift / 100) * 6,
  };
}
