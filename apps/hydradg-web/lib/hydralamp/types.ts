import type { ContextDelta } from "./contextDelta";

export type PerturbationKind =
  | "CONTROL"
  | "INVALID_PROOF"
  | "REPLAYED_PROOF"
  | "BROKEN_AUTHORIZATION_EDGE";

export type ProofState =
  | "VALID"
  | "INVALID"
  | "MISSING"
  | "REPLAYED"
  | "MALFORMED"
  | "UNKNOWN";

export type AgentDecision =
  | "NO_ACTION"
  | "REJECT_ACTOR"
  | "REQUEST_REPAIR"
  | "ABSTAIN"
  | "POISON_WRITE"
  | "AUTHORIZE_REPAIR";

export type VerifierClass =
  | "PASS"
  | "FAIL"
  | "NULL"
  | "ABSTAIN"
  | "TIMEOUT"
  | "ERROR"
  | "DENY"
  | "RETAIN";

export type ExecutionMode =
  | "DETERMINISTIC_FIXTURE"
  | "LOCAL_MODEL_GUM_OLLARMA"
  | "LIVE_RUNTYPE"
  | "NOT_CONFIGURED"
  /** @deprecated alias retained in receipts for prior runs */
  | "SYNTHETIC_UI_FIXTURE";

export type EventType =
  | "RUN_STARTED"
  | "MUTATION_INJECTED"
  | "MODEL_CONTEXT"
  | "MODEL_ACTIVE"
  | "TOOL_CALL"
  | "TOOL_RESULT"
  | "MODEL_OUTPUT"
  | "MODEL_FINAL"
  | "PROPOSAL"
  | "ERROR"
  | "TIMEOUT"
  | "VERIFIER_RESULT"
  | "QUARANTINE"
  | "FCG_APPEND"
  | "FCG_ROOT_UNCHANGED"
  | "HYDRADB_PROJECTED"
  | "PERF"
  | "DONE";

export type EvidenceClass =
  | "SYNTHETIC"
  | "SYNTHETIC_DEMO_FIXTURE"
  | "PROBABILISTIC_MODEL_OUTPUT"
  | "DETERMINISTIC_TOOL_OUTPUT"
  | "DETERMINISTIC_FIXTURE"
  | "LOCAL_MODEL_GUM_OLLARMA"
  | "LIVE_RUNTYPE"
  | "GUM_DOCTOR_DIAGNOSTIC"
  | "UNKNOWN";

export type NodeVisualClass =
  | "reference"
  | "probabilistic_proposal"
  | "quarantined"
  | "contradicted"
  | "verified"
  | "repaired"
  | "canonical";

export type HydraLampEvent = {
  run_id: string;
  seq: number;
  timestamp: string;
  type: EventType;
  lane: "reference" | "agent-a" | "agent-b" | "agent-c" | "poison" | "repair" | "verifier" | "custody";
  actor_id: string;
  model_id?: string | null;
  execution_id?: string | null;
  runtype_execution_id?: string | null;
  local_execution_id?: string | null;
  tool?: string;
  summary: string;
  public_payload?: Record<string, unknown>;

  // Hash / custody contract (nullable when N/A for event type)
  prev_event_hash: string;
  event_hash: string;
  context_hash_before: string | null;
  context_hash_after: string | null;
  kg_snapshot_hash_before: string | null;
  kg_snapshot_hash_after: string | null;
  model_output_hash: string | null;
  tool_input_hash: string | null;
  tool_output_hash: string | null;
  proposal_hash: string | null;
  fcg_root_before: string | null;
  fcg_root_after: string | null;
  context_delta: ContextDelta | null;
  verification_result: VerifierClass | null;
  evidence_class: EvidenceClass;
  claim_ceiling: string;

  // Performance (optional; never mixed into model latency claims incorrectly)
  hash_compute_ms?: number | null;
  context_delta_compute_ms?: number | null;
  graph_render_update_ms?: number | null;
  SSE_delivery_ms?: number | null;
  model_latency_ms?: number | null;
  end_to_end_ms?: number | null;
};

export type ModelContextReceipt = {
  context_id: string;
  context_hash: string;
  source_fco_ids: string[];
  source_edge_ids: string[];
  source_fcg_root: string;
  actor_capability_scope: string[];
  public_private: "public" | "private_redacted";
  token_count: number | null;
  model_visible_context: Record<string, unknown>;
};

export type FixtureState = {
  schema: string;
  state_id: string;
  synthetic: boolean;
  security_incident: boolean;
  objects: Record<string, FcoLike>;
  edges: Array<{ from: string; to: string; type: string }>;
  state_root: string;
};

export type FcoLike = {
  id: string;
  object_sha256: string;
  type: string;
  payload: Record<string, unknown>;
};

export type StructuredAgentOutput = {
  decision: AgentDecision;
  earliest_divergence: string | null;
  proof_state: ProofState;
  requested_action: string | null;
  confidence: number;
  evidence_refs: string[];
};

export type LaneResult = {
  lane: "agent-a" | "agent-b" | "agent-c" | "poison" | "repair";
  model_id: string;
  runtype_execution_id: string | null;
  local_execution_id?: string | null;
  status: "COMPLETED" | "TIMEOUT" | "ERROR" | "NOT_CONFIGURED" | "ABSTAIN";
  tool_sequence: string[];
  tool_count: number;
  structured: StructuredAgentOutput | null;
  raw_output_sha256: string | null;
  model_output_hash?: string | null;
  context_hash?: string | null;
  proposal_hash?: string | null;
  latency_ms: number;
  error_class?: string;
  error_name?: string | null;
  error_code?: string | null;
  error_message?: string | null;
  provider_error_code?: string | null;
  http_status?: number | null;
  provider_request_id?: string | null;
  sdk_version?: string | null;
  repair_requested: boolean;
  repair_allowed: boolean | null;
  candidate_root: string | null;
  unauthorized_canonical_writes: number;
  prompt_hash?: string | null;
  tool_results_hashes?: string[];
  fallback_used?: boolean;
  final_model_status?: string;
  verification_result?: VerifierClass | null;
  fcg_root_before?: string | null;
  fcg_root_after?: string | null;
  evidence_class?: EvidenceClass;
};

export type ExperimentRun = {
  run_id: string;
  created_at: string;
  mode: ExecutionMode;
  perturbation: PerturbationKind;
  demo_20s: boolean;
  reference_root: string;
  current_root: string;
  earliest_divergence_expected: string | null;
  events: HydraLampEvent[];
  last_event_hash: string;
  lanes: LaneResult[];
  verifier: Record<string, unknown> | null;
  fcg: {
    root_before: string | null;
    root_after: string | null;
    append_state: "PENDING" | "PASS" | "FAILED" | "SKIPPED" | "UNCHANGED_QUARANTINE";
  };
  quarantine: {
    proposals: Array<Record<string, unknown>>;
    count: number;
  };
  graph_nodes: Array<{
    id: string;
    label: string;
    visual_class: NodeVisualClass;
  }>;
  graph_edges: Array<{ id: string; source: string; target: string; label: string }>;
  hydradb: {
    state: "PENDING" | "PROJECTED" | "FAILED" | "SKIPPED";
    readback: boolean;
    receipt_path?: string;
  };
  claim_ceiling: string;
  signature_state: "NOT_SIGNED";
  merkle_mmr_state: "NOT_COMMITTED";
  done: boolean;
  timings?: {
    hash_compute_ms_total?: number;
    context_delta_compute_ms_total?: number;
    model_latency_ms_total?: number;
    end_to_end_ms?: number;
  };
};
