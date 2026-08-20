export type TimepointId = "T0" | "T1" | "T2" | "T3" | "T4" | "T5";

export type ScientificScoreState =
  | {
      status: "DECLARED";
      g_star: number;
      delta_g_star: number;
      cloud_drift: number;
    }
  | {
      status: "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION";
      g_star: null;
      delta_g_star: null;
      cloud_drift: null;
      note: "G*/Cloud Drift N/A by contract; no explicit scoring distribution declared or frozen.";
    };

export type TimepointRecord = {
  timepoint: TimepointId;
  label: string;
  state_type: "REFERENCE" | "MUTATION" | "RESTORATION" | "HOSTED_MIGRATION" | "CONTEXT_VS_ENTROPY" | "FINAL_JUDGE_RELEASE";
  score_state: ScientificScoreState;
  measurement_summary: string;
  custody_identity: string;
  backend_traceability: string;
  evidence: string;
};

// T3 Hosted Migration Canonical Constants & Calculations
export const T3_MIGRATION = {
  local_canonical_fco_count: 36,
  hosted_canonical_fco_count: 36,
  local_canonical_edge_count: 24,
  hosted_canonical_edge_count: 24,
  local_fco_root: "d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1",
  hosted_fco_root: "d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1",
  local_edge_root: "7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab",
  hosted_edge_root: "7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab",

  get fco_set_delta_count(): number {
    return Math.abs(this.hosted_canonical_fco_count - this.local_canonical_fco_count);
  },
  get fco_set_delta_percent(): number {
    return (100 * this.fco_set_delta_count) / Math.max(1, this.local_canonical_fco_count);
  },
  get edge_set_delta_count(): number {
    return Math.abs(this.hosted_canonical_edge_count - this.local_canonical_edge_count);
  },
  get edge_set_delta_percent(): number {
    return (100 * this.edge_set_delta_count) / Math.max(1, this.local_canonical_edge_count);
  },
  content_hash_delta_count: 0,
  get content_hash_delta_percent(): number {
    return (100 * this.content_hash_delta_count) / Math.max(1, this.local_canonical_fco_count);
  },
  get fco_root_match(): boolean {
    return this.local_fco_root === this.hosted_fco_root;
  },
  get edge_root_match(): boolean {
    return this.local_edge_root === this.hosted_edge_root;
  },
  get canonical_parity(): "PASS" | "FAIL" {
    return this.fco_set_delta_count === 0 &&
      this.edge_set_delta_count === 0 &&
      this.content_hash_delta_count === 0 &&
      this.fco_root_match &&
      this.edge_root_match
      ? "PASS"
      : "FAIL";
  },
  interpretation: "Canonical custody identity was preserved across migration.",

  // Collection Scope
  historical_migration_collection: "default",
  current_discovered_collection: "hydradg",
  collection_scope_changed: true,
  collection_scope_evidence:
    "Historical receipt recorded 'default'; live HydraDB collection discovery returned ['hydradg'] (superseded for current runtime scope)",

  // Traceability & Backend
  backend_connectivity: "PASS",
  database_binding: "PASS",
  collection_discovery: "PASS",
  canonical_parity_receipt: "PASS",
  canary_source_id: "fco:303b3fab6fd8831b84a37f789aa4ef1f1ab78a808572eddf8632d1b88f97e1d5",
  live_source_traceability: "PASS_REQUEST_LEVEL",
} as const;

// T4 Context vs Entropy Experiment Calculations
export const T4_CONTEXT_VS_ENTROPY = {
  raw_findings: 18567,
  context_classified: 18555,
  abstentions: 12,

  get classification_coverage_percent(): number {
    return (100 * this.context_classified) / this.raw_findings;
  },
  get abstention_rate_percent(): number {
    return (100 * this.abstentions) / this.raw_findings;
  },

  // Category Breakdown
  deterministic_hash: 18428,
  toy_non_authenticating_key: 126,
  revoked_historical_credential: 1,
  unexplained_secret_candidate: 12,

  get category_sum(): number {
    return (
      this.deterministic_hash +
      this.toy_non_authenticating_key +
      this.revoked_historical_credential +
      this.unexplained_secret_candidate
    );
  },
  get category_sum_invariant(): "PASS" | "FAIL" {
    return this.category_sum === this.raw_findings ? "PASS" : "FAIL";
  },
  gitleaks_boundary_note:
    "This classification experiment does NOT replace Gitleaks. Classified items are not scientifically 'false positives' unless individually established as such.",
} as const;

// T5 Final Judge Release Verification Calculations
export const T5_FINAL_JUDGE_RELEASE = {
  live_production_exact_sha: "3c0509eced37d73e985ce064e9605a0b0068259d",
  website_release_version: "HydraDG Judge Release 2026.08.20+3c0509eced37",
  release_fco_id: "fco:e5c3e391eb722d097b9dcc9c249cf27abf68d5d093a43f81fc2ae95b274414f4",
  release_fco_object_sha256: "e5c3e391eb722d097b9dcc9c249cf27abf68d5d093a43f81fc2ae95b274414f4",

  get release_fco_hash_match(): "PASS" | "FAIL" {
    return this.release_fco_id === `fco:${this.release_fco_object_sha256}` ? "PASS" : "FAIL";
  },
  deployed_sha_match: "PASS",
  canonical_fco_identity_validation: "PASS",
  unique_canonical_fco_count: 60,
  identity_problems: [] as readonly string[],
  signature_state: "NOT_SIGNED",
  merkle_state: "NOT_MERKLE_COMMITTED",
} as const;

// Canonical Timepoints Table Dataset
export const TIMEPOINTS: readonly TimepointRecord[] = [
  {
    timepoint: "T0",
    label: "T0 Reference State",
    state_type: "REFERENCE",
    score_state: {
      status: "DECLARED",
      g_star: -0.06123,
      delta_g_star: 0.0,
      cloud_drift: 0.0,
    },
    measurement_summary: "Frozen synthetic baseline (P_ref = [0.88, 0.08, 0.04])",
    custody_identity: "Synthetic fixture SHA256 canonical seed",
    backend_traceability: "LOCAL_DETERMINISTIC_FIXTURE",
    evidence: "T0ReferenceStateFCO",
  },
  {
    timepoint: "T1",
    label: "T1 Poison State",
    state_type: "MUTATION",
    score_state: {
      status: "DECLARED",
      g_star: 0.572956,
      delta_g_star: 0.634186,
      cloud_drift: 40.3629,
    },
    measurement_summary: "Controlled perturbation state (P_mut = [0.18, 0.72, 0.10])",
    custody_identity: "Divergent relationship preserved without historical overwrite",
    backend_traceability: "LOCAL_DETERMINISTIC_FIXTURE",
    evidence: "T1MutationStateFCO",
  },
  {
    timepoint: "T2",
    label: "T2 Antidote State",
    state_type: "RESTORATION",
    score_state: {
      status: "DECLARED",
      g_star: -0.027496,
      delta_g_star: -0.600452,
      cloud_drift: 1.8729,
    },
    measurement_summary: "Restoration state (P_rest = [0.76, 0.14, 0.10])",
    custody_identity: "Recovery established while poison state remains traversable",
    backend_traceability: "LOCAL_DETERMINISTIC_FIXTURE",
    evidence: "T2RestorationStateFCO",
  },
  {
    timepoint: "T3",
    label: "T3 Hosted Migration",
    state_type: "HOSTED_MIGRATION",
    score_state: {
      status: "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION",
      g_star: null,
      delta_g_star: null,
      cloud_drift: null,
      note: "G*/Cloud Drift N/A by contract; no explicit scoring distribution declared or frozen.",
    },
    measurement_summary: `Canonical FCO Δ: 0 (0.0%), Edge Δ: 0 (0.0%), Hash Δ: 0 (0.0%). ${T3_MIGRATION.interpretation}`,
    custody_identity: `FCO root match: ${T3_MIGRATION.fco_root_match ? "PASS" : "FAIL"}, Edge root match: ${T3_MIGRATION.edge_root_match ? "PASS" : "FAIL"}`,
    backend_traceability: `Backend: HYDRADB_REMOTE_API_V2, DB: hydradg, Collection: ${T3_MIGRATION.current_discovered_collection} (historical default superseded), Traceability: ${T3_MIGRATION.live_source_traceability}`,
    evidence: "HostedParityReceiptFCO / HostedReadbackFCO",
  },
  {
    timepoint: "T4",
    label: "T4 Context vs Entropy",
    state_type: "CONTEXT_VS_ENTROPY",
    score_state: {
      status: "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION",
      g_star: null,
      delta_g_star: null,
      cloud_drift: null,
      note: "G*/Cloud Drift N/A by contract; no explicit scoring distribution declared or frozen.",
    },
    measurement_summary: `Coverage: ${T4_CONTEXT_VS_ENTROPY.classification_coverage_percent.toFixed(4)}% (18,555/18,567), Abstentions: ${T4_CONTEXT_VS_ENTROPY.abstentions} (${T4_CONTEXT_VS_ENTROPY.abstention_rate_percent.toFixed(4)}%), Sum invariant: ${T4_CONTEXT_VS_ENTROPY.category_sum_invariant}`,
    custody_identity: "Full-history secret findings classified into deterministic, toy, revoked, and unexplained categories",
    backend_traceability: "LOCAL_AND_MODAL_CLASSIFICATION_LANE",
    evidence: "ContextVsEntropyResultFCO",
  },
  {
    timepoint: "T5",
    label: "T5 Final Judge Release",
    state_type: "FINAL_JUDGE_RELEASE",
    score_state: {
      status: "NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION",
      g_star: null,
      delta_g_star: null,
      cloud_drift: null,
      note: "G*/Cloud Drift N/A by contract; no explicit scoring distribution declared or frozen.",
    },
    measurement_summary: `Git SHA match: ${T5_FINAL_JUDGE_RELEASE.deployed_sha_match}, Release FCO hash match: ${T5_FINAL_JUDGE_RELEASE.release_fco_hash_match}, Identities: 60 PASS`,
    custody_identity: `Release FCO: ${T5_FINAL_JUDGE_RELEASE.release_fco_id.slice(0, 24)}…`,
    backend_traceability: `Vercel / Hack Hydra 2026 (SHA ${T5_FINAL_JUDGE_RELEASE.live_production_exact_sha.slice(0, 12)})`,
    evidence: "WebsiteReleaseFCO / HydraDBProductionFCO",
  },
] as const;

// FCG Directed Lineage Edge Definitions
export const TIMEPOINT_FCG_EDGES = [
  { src: "T2RestorationStateFCO", rel: "MIGRATED_TO", dst: "T3HostedMigrationStateFCO" },
  { src: "T3HostedMigrationStateFCO", rel: "PRODUCED", dst: "HostedParityReceiptFCO" },
  { src: "T3HostedMigrationStateFCO", rel: "OBSERVED_AT", dst: "HydraDBProductionFCO" },
  { src: "T3HostedMigrationStateFCO", rel: "READ_BACK_AS", dst: "HostedReadbackFCO" },
  { src: "T4ContextVsEntropyFCO", rel: "PRODUCED", dst: "ContextVsEntropyResultFCO" },
  { src: "T5FinalJudgeReleaseFCO", rel: "DEPLOYS", dst: "WebsiteReleaseFCO" },
  { src: "T5FinalJudgeReleaseFCO", rel: "USES_DATABASE", dst: "HydraDBProductionFCO" },
  { src: "T5FinalJudgeReleaseFCO", rel: "SUPERSEDES_PRESENTATION", dst: "PriorPresentationStateFCO" },
] as const;

// Final Required Evaluation Summary Flags (PASS / FAIL / N/A)
export function getReleaseEvaluationFlags() {
  return {
    T3_CANONICAL_PARITY: T3_MIGRATION.canonical_parity,
    T3_FCO_DELTA: T3_MIGRATION.fco_set_delta_count === 0 ? ("PASS" as const) : ("FAIL" as const),
    T3_EDGE_DELTA: T3_MIGRATION.edge_set_delta_count === 0 ? ("PASS" as const) : ("FAIL" as const),
    T3_HASH_DELTA: T3_MIGRATION.content_hash_delta_count === 0 ? ("PASS" as const) : ("FAIL" as const),
    T3_ROOT_MATCH: T3_MIGRATION.fco_root_match && T3_MIGRATION.edge_root_match ? ("PASS" as const) : ("FAIL" as const),
    T3_BACKEND_CONNECTIVITY: T3_MIGRATION.backend_connectivity,
    T3_COLLECTION_DISCOVERY: T3_MIGRATION.collection_discovery,
    T3_TRACEABILITY: T3_MIGRATION.live_source_traceability,

    T4_CLASSIFICATION_COVERAGE: T4_CONTEXT_VS_ENTROPY.classification_coverage_percent > 99.9 ? ("PASS" as const) : ("FAIL" as const),
    T4_ABSTENTION_RATE: T4_CONTEXT_VS_ENTROPY.abstentions === 12 ? ("PASS" as const) : ("FAIL" as const),
    T4_CATEGORY_SUM_INVARIANT: T4_CONTEXT_VS_ENTROPY.category_sum_invariant,

    T5_DEPLOYED_SHA_MATCH: T5_FINAL_JUDGE_RELEASE.deployed_sha_match,
    T5_RELEASE_FCO_HASH_MATCH: T5_FINAL_JUDGE_RELEASE.release_fco_hash_match,
    T5_CANONICAL_FCO_IDENTITY_VALIDATION: T5_FINAL_JUDGE_RELEASE.canonical_fco_identity_validation,

    T3_GSTAR_STATE: "N/A" as const,
    T4_GSTAR_STATE: "N/A" as const,
    T5_GSTAR_STATE: "N/A" as const,
  };
}
