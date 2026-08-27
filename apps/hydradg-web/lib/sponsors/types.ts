/** Unified sponsor mission adapter contract — no provider bypasses custody. */

export type SponsorMissionStatus =
  | "PASS"
  | "NULL"
  | "NEGATIVE"
  | "ERROR"
  | "TIMEOUT"
  | "ABSTAIN"
  | "BLOCKED"
  | "SKIPPED";

export type SponsorDiscoveryState =
  | "DISCOVERED"
  | "CONFIGURED"
  | "BLOCKED"
  | "NOT_APPLICABLE"
  | "SKIPPED"
  | "DEFERRED_NONBLOCKING";

export type SponsorPanelState =
  | "DISCOVERED"
  | "CONFIGURED"
  | "LIVE_PASS"
  | "ERROR"
  | "BLOCKED"
  | "SKIPPED";

export type SponsorMissionResult = {
  mission_id: string;
  provider: string;
  operation: string;
  started_at: string;
  completed_at: string;
  evidence_class: string;
  source_identity: string | null;
  external_execution_id: string | null;
  raw_artifact_sha256: string | null;
  output_hash: string | null;
  status: SponsorMissionStatus;
  error_code: string | null;
  error_summary: string | null;
  claim_ceiling: string;
  secret_state: "PRESENT" | "MISSING" | "BLOCKED" | "INVALID_PLACEHOLDER" | "NOT_APPLICABLE";
  secret_ref: string | null;
  required_env_names: string[];
  discovery_state: SponsorDiscoveryState;
  connectivity_state: SponsorMissionStatus | "NOT_ATTEMPTED";
  empirical_state: SponsorMissionStatus | "NOT_ATTEMPTED";
  receipt_path: string;
};

export type SponsorProviderSummary = {
  provider: string;
  priority: "P0" | "P1" | "P2" | "OPTIONAL" | "SUBMISSION_ONLY" | "INFRASTRUCTURE";
  lane?: "SPONSOR" | "INFRASTRUCTURE";
  panel_state: SponsorPanelState;
  discovery_state: SponsorDiscoveryState;
  live_status: SponsorMissionStatus | "NOT_ATTEMPTED";
  claim_ceiling: string;
  receipt_path: string | null;
};

export type GoldenPathState = {
  source: string | null;
  memory: string | null;
  model: string | null;
  external_actor: string | null;
  custody: string;
  projection: string;
  composed_status: "PARTIAL" | "READY" | "BLOCKED";
  notes: string[];
};
