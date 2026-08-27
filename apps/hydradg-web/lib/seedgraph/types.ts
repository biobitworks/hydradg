export const GAP_KINDS = [
  "MISSING_SOURCE_URL",
  "MISSING_SOURCE_SHA256",
  "MISSING_PROVENANCE_EDGE",
  "UNRESOLVED_EXTERNAL_DOC",
] as const;

export type GapKind = (typeof GAP_KINDS)[number];

export const REPAIR_OUTCOMES = ["PASS", "NULL", "NEGATIVE", "ABSTAIN"] as const;
export type RepairOutcome = (typeof REPAIR_OUTCOMES)[number];

export type CanonicalNode = {
  id: string;
  kind: string;
  label: string;
  source_url: string | null;
  source_sha256: string | null;
  provenance_edge: string | null;
  claim_ceiling: string;
};

export type CanonicalSnapshot = {
  identity: "CANONICAL_FROZEN_SNAPSHOT";
  graph_id: string;
  nodes: CanonicalNode[];
};

export type SeedGraphGap = {
  gap_id: string;
  kind: GapKind;
  node_id: string;
  expected_url: string | null;
  expected_sha256: string | null;
  expected_provenance_edge: string | null;
  repairable_by_tavily: boolean;
  notes: string;
};

export type RepairVerdict = {
  gap_id: string;
  outcome: RepairOutcome;
  reasons: string[];
  candidate_fco_id: string | null;
  candidate_fco_sha256: string | null;
  successor_node_id: string | null;
  successor_fcg_appended: boolean;
};
