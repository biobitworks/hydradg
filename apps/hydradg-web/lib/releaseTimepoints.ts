export type ReleaseTimepoint = {
  id: string;
  label: string;
  classification: string;
  color: string;
  distribution?: readonly number[];
  burden?: number;
  g_star?: number;
  delta_g_star?: number;
  cloud_drift?: number;
  score_state: "MEASURED" | "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION";
  evidence: string;
};

export const RELEASE_TIMEPOINTS: readonly ReleaseTimepoint[] = [
  {
    id: "T0_REFERENCE",
    label: "Reference / normal",
    classification: "SYNTHETIC_FIXTURE",
    color: "#b69cff",
    distribution: [0.88, 0.08, 0.04],
    burden: 0.08,
    g_star: -0.06123,
    delta_g_star: 0,
    cloud_drift: 0,
    score_state: "MEASURED",
    evidence: "Declared deterministic fixture baseline.",
  },
  {
    id: "T1_MUTATION",
    label: "Poison / mutation",
    classification: "SYNTHETIC_FIXTURE",
    color: "#ff8a3d",
    distribution: [0.18, 0.72, 0.1],
    burden: 0.82,
    g_star: 0.572956,
    delta_g_star: 0.634186,
    cloud_drift: 40.3629,
    score_state: "MEASURED",
    evidence: "Declared controlled perturbation fixture.",
  },
  {
    id: "T2_RESTORATION",
    label: "Antidote / restoration",
    classification: "SYNTHETIC_FIXTURE",
    color: "#5aa9ff",
    distribution: [0.76, 0.14, 0.1],
    burden: 0.2,
    g_star: -0.027496,
    delta_g_star: -0.600452,
    cloud_drift: 1.8729,
    score_state: "MEASURED",
    evidence: "Declared restoration fixture; counterevidence remains in the graph.",
  },
  {
    id: "T3_HOSTED_MIGRATION",
    label: "Hosted HydraDB migration",
    classification: "PRODUCTION_RELEASE_STATE",
    color: "#7fd1b9",
    score_state: "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION",
    evidence: "Hosted parity receipt: 36 canonical FCOs, 24 edges, zero canonical set/edge/content-hash delta.",
  },
  {
    id: "T4_CONTEXT_VS_ENTROPY",
    label: "Context vs Entropy",
    classification: "PRODUCTION_EXPERIMENT_STATE",
    color: "#f6c85f",
    score_state: "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION",
    evidence: "18,567 raw findings; 18,555 context-classified; 12 abstentions; 99.9354% coverage.",
  },
  {
    id: "T5_FINAL_JUDGE_RELEASE",
    label: "Final judge release",
    classification: "PRODUCTION_JUDGE_RELEASE_STATE",
    color: "#d8e0e8",
    score_state: "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION",
    evidence: "Exact deployed Git SHA and WebsiteRelease FCO are resolved at build/runtime; no scalar G*/Cloud Drift is fabricated without a declared distribution.",
  },
] as const;

export const CONTEXT_SCORE_CONTRACT = {
  shannon: "H = -Σ p log2(p)",
  normalized_shannon: "Hnorm = H / log2(n)",
  g_star: "G* = U* - 0.35 × Hnorm",
  delta_g_star: "ΔG*(t) = G*(t) - G*(t-1)",
  cloud_drift: "Cloud Drift = 100 × JSD_base2(Pt || P_reference)",
  mutation_distance: "Mutation distance = total-variation distance from the reference distribution",
  restoration_gain: "Restoration gain = max(0, previous TV distance - current TV distance)",
} as const;
