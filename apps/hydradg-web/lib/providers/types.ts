export type ProviderHealthState =
  | "CONFIGURED"
  | "PASS"
  | "ERROR"
  | "BLOCKED"
  | "SKIPPED";

export type ProviderLane = "SPONSOR" | "INFRASTRUCTURE" | "SCAFFOLD" | "NOT_HOSTED";

export type ProviderHealthRow = {
  provider: string;
  lane: ProviderLane;
  secret_state: "PRESENT" | "MISSING" | "INVALID_PLACEHOLDER" | "NOT_APPLICABLE";
  /** Key/config present. Never equal to empirical PASS. */
  config_state: "CONFIGURED" | "NOT_CONFIGURED" | "NOT_APPLICABLE";
  /** Empirical / probe outcome. Absent probe stays NOT_PROBED, never auto-PASS. */
  runtime_state: ProviderHealthState | "NOT_PROBED";
  /** UI state: CONFIGURED is not rendered as PASS. */
  panel_state: ProviderHealthState;
  hosted_on_vercel: boolean;
  claim_ceiling: string;
  note: string;
};

export type QuarantineRecord = {
  quarantine_id: string;
  evidence_id: string;
  provider: string;
  operation: string;
  evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE";
  custody_state: "QUARANTINED";
  source_url: string | null;
  request_id: string | null;
  retrieved_at: string;
  raw_sha256: string;
  output_hash: string;
  result_count: number;
  /** Exact retrieved bytes as UTF-8 text. Never log, never ship to the browser. */
  raw_bytes: string;
  fcg_append: "NOT_APPENDED";
  claim_ceiling: "EXTERNALLY_RETRIEVED_EVIDENCE";
};

/** Public quarantine view: hashes and class only. No raw bytes, no secrets. */
export type PublicQuarantineRecord = Omit<QuarantineRecord, "raw_bytes">;

export function publicQuarantine(q: QuarantineRecord): PublicQuarantineRecord {
  const { raw_bytes: _raw, ...rest } = q;
  return rest;
}
