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
  | "ABSTAIN";

export type VerifierClass =
  | "PASS"
  | "FAIL"
  | "NULL"
  | "ABSTAIN"
  | "TIMEOUT"
  | "ERROR";

export type EventType =
  | "RUN_STARTED"
  | "MUTATION_INJECTED"
  | "MODEL_ACTIVE"
  | "TOOL_CALL"
  | "TOOL_RESULT"
  | "MODEL_FINAL"
  | "ERROR"
  | "TIMEOUT"
  | "VERIFIER_RESULT"
  | "FCG_APPEND"
  | "HYDRADB_PROJECTED"
  | "DONE";

export type HydraLampEvent = {
  run_id: string;
  seq: number;
  timestamp: string;
  lane: "reference" | "agent-a" | "agent-b" | "agent-c" | "verifier" | "custody";
  model_id?: string;
  runtype_execution_id?: string | null;
  type: EventType;
  tool?: string;
  summary: string;
  public_payload?: Record<string, unknown>;
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
  lane: "agent-a" | "agent-b" | "agent-c";
  model_id: string;
  runtype_execution_id: string | null;
  status: "COMPLETED" | "TIMEOUT" | "ERROR" | "NOT_CONFIGURED";
  tool_sequence: string[];
  tool_count: number;
  structured: StructuredAgentOutput | null;
  raw_output_sha256: string | null;
  latency_ms: number;
  error_class?: string;
  repair_requested: boolean;
  repair_allowed: boolean | null;
  candidate_root: string | null;
  unauthorized_canonical_writes: number;
  prompt_hash?: string | null;
  tool_results_hashes?: string[];
  fallback_used?: boolean;
  final_model_status?: string;
};

export type ExperimentRun = {
  run_id: string;
  created_at: string;
  mode: "LIVE_RUNTYPE" | "SYNTHETIC_UI_FIXTURE" | "NOT_CONFIGURED";
  perturbation: PerturbationKind;
  demo_20s: boolean;
  reference_root: string;
  current_root: string;
  earliest_divergence_expected: string | null;
  events: HydraLampEvent[];
  lanes: LaneResult[];
  verifier: Record<string, unknown> | null;
  fcg: {
    root_before: string | null;
    root_after: string | null;
    append_state: "PENDING" | "PASS" | "FAILED" | "SKIPPED";
  };
  hydradb: {
    state: "PENDING" | "PROJECTED" | "FAILED" | "SKIPPED";
    readback: boolean;
    receipt_path?: string;
  };
  claim_ceiling: string;
  signature_state: "NOT_SIGNED";
  merkle_mmr_state: "NOT_COMMITTED";
  done: boolean;
};
