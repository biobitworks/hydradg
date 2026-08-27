import {
  loadReference,
  materializeState,
  sha256Text,
  canonicalJson,
  stateRoot,
  verifyToyEd25519,
} from "./fixtures";
import type { FixtureState, PerturbationKind, ProofState } from "./types";

export type ToolName =
  | "inspect_state"
  | "trace_divergence"
  | "verify_actor_proof"
  | "attempt_repair";

export type ToolContext = {
  experiment_id: string;
  perturbation: PerturbationKind;
  reference: FixtureState;
  current: FixtureState;
  expectedEarliest: string | null;
};

export function buildToolContext(
  experiment_id: string,
  perturbation: PerturbationKind,
): ToolContext {
  const m = materializeState(perturbation);
  return {
    experiment_id,
    perturbation,
    reference: m.reference,
    current: m.current,
    expectedEarliest: m.expectedEarliest,
  };
}

export function inspect_state(
  ctx: ToolContext,
  input: { experiment_id?: string; state_root?: string },
) {
  const state =
    input.state_root && input.state_root === ctx.reference.state_root
      ? ctx.reference
      : ctx.current;
  const auth = state.edges.filter((e) =>
    ["AUTHORIZED_BY", "CONTAINS", "GOVERNED_BY"].includes(e.type),
  );
  const objects = Object.fromEntries(
    Object.entries(state.objects).map(([id, o]) => [
      id,
      {
        id: o.id,
        type: o.type,
        object_sha256: o.object_sha256,
        evidence_class:
          (o.payload.evidence_class as string) ||
          (o.type === "ToyProofFCO" ? "SYNTHETIC_DEMO_FIXTURE" : "SYNTHETIC_DEMO_FIXTURE"),
        public_safe_payload: sanitizePayload(o.payload),
      },
    ]),
  );
  return {
    tool: "inspect_state",
    read_only: true,
    experiment_id: ctx.experiment_id,
    state_root: state.state_root,
    requested_state_root: input.state_root || null,
    neighborhood: { objects, edges: auth },
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
  };
}

export function trace_divergence(ctx: ToolContext) {
  const ref = ctx.reference;
  const cur = ctx.current;
  const refEdges = new Set(ref.edges.map((e) => `${e.type}|${e.from}|${e.to}`));
  const curEdges = new Set(cur.edges.map((e) => `${e.type}|${e.from}|${e.to}`));
  const changed_edges = [...curEdges].filter((e) => !refEdges.has(e));
  const missing_objects = Object.keys(ref.objects).filter((id) => !cur.objects[id]);
  const unexpected_objects = Object.keys(cur.objects).filter((id) => !ref.objects[id]);

  let earliest: string | null = ctx.expectedEarliest;
  if (!earliest) {
    const authCur = cur.edges.find((e) => e.type === "AUTHORIZED_BY");
    const authRef = ref.edges.find((e) => e.type === "AUTHORIZED_BY");
    if (authCur && authRef && authCur.to !== authRef.to) earliest = authCur.to;
    else if (unexpected_objects[0]) earliest = unexpected_objects[0];
  }

  return {
    tool: "trace_divergence",
    earliest_divergent_dependency: earliest,
    changed_edges,
    missing_objects,
    unexpected_objects,
    reference_root: ref.state_root,
    current_root: cur.state_root,
    roots_equal: ref.state_root === cur.state_root,
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
  };
}

export function verify_actor_proof(ctx: ToolContext): {
  tool: string;
  proof_state: ProofState;
  evidence_class: string;
  details: Record<string, unknown>;
} {
  const auth = ctx.current.edges.find((e) => e.type === "AUTHORIZED_BY");
  if (!auth) {
    return {
      tool: "verify_actor_proof",
      proof_state: "MISSING",
      evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
      details: { reason: "NO_AUTHORIZED_BY_EDGE" },
    };
  }
  const proof = ctx.current.objects[auth.to];
  if (!proof) {
    return {
      tool: "verify_actor_proof",
      proof_state: "MISSING",
      evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
      details: { reason: "PROOF_OBJECT_MISSING", expected_id: auth.to },
    };
  }
  const message = String(proof.payload.message || "");
  const signature_b64 = String(proof.payload.signature_b64 || "");
  const public_key_b64 = String(proof.payload.public_key_b64 || "");
  if (!message || !signature_b64 || !public_key_b64) {
    return {
      tool: "verify_actor_proof",
      proof_state: "MALFORMED",
      evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
      details: { reason: "MISSING_FIELDS" },
    };
  }
  let proof_state = verifyToyEd25519({ message, signature_b64, public_key_b64 });
  if (proof.payload.perturbation === "REPLAYED_PROOF" && proof_state === "INVALID") {
    proof_state = "REPLAYED";
  }
  return {
    tool: "verify_actor_proof",
    proof_state,
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
    details: {
      proof_id: proof.id,
      key_label: proof.payload.key_label || "TOY_DEMO_KEY",
      authenticity_claim: "NO_REAL_AUTHENTICITY_CLAIM",
      sha256_is_not_a_signature: true,
      note: "Ed25519 verification of toy operation only. REAL HYDRALAMP IDENTITY NOT ESTABLISHED.",
    },
  };
}

export function attempt_repair(
  ctx: ToolContext,
  input: { requested_repair?: string; previous_proof_state?: string },
) {
  const proof = verify_actor_proof(ctx);
  // Policy: models never get canonical write. Ephemeral candidate only if proof invalid/replayed/missing
  // and repair is explicitly for restoring AUTHORIZED_BY to reference proof.
  const allowedProofs = new Set(["INVALID", "REPLAYED", "MISSING"]);
  if (!allowedProofs.has(proof.proof_state)) {
    return {
      tool: "attempt_repair",
      allowed: false,
      reason: `POLICY_DENIES_REPAIR_WHEN_PROOF_${proof.proof_state}`,
      state_changed: false,
      canonical_write: false,
      evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
    };
  }
  const requested = input.requested_repair || "";
  if (!requested.toLowerCase().includes("restore") && !requested.toLowerCase().includes("reference")) {
    return {
      tool: "attempt_repair",
      allowed: false,
      reason: "POLICY_REQUIRES_EXPLICIT_RESTORE_REFERENCE_REPAIR",
      state_changed: false,
      canonical_write: false,
      evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
    };
  }
  // Ephemeral candidate: clone reference state root as candidate — NOT canonical write
  const candidate = structuredClone(ctx.reference);
  candidate.state_id = "EPHEMERAL_REPAIR_CANDIDATE";
  const candidate_state_root = stateRoot(candidate);
  return {
    tool: "attempt_repair",
    allowed: true,
    candidate_state_root,
    canonical_write: false,
    state_changed: false,
    note: "Ephemeral candidate only. Canonical FCO/FCG unchanged.",
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
  };
}

export function executeTool(
  ctx: ToolContext,
  name: ToolName,
  args: Record<string, unknown>,
) {
  switch (name) {
    case "inspect_state":
      return inspect_state(ctx, args as { experiment_id?: string; state_root?: string });
    case "trace_divergence":
      return trace_divergence(ctx);
    case "verify_actor_proof":
      return verify_actor_proof(ctx);
    case "attempt_repair":
      return attempt_repair(ctx, args as { requested_repair?: string; previous_proof_state?: string });
    default:
      return { tool: name, error: "UNKNOWN_TOOL", evidence_class: "DETERMINISTIC_TOOL_OUTPUT" };
  }
}

export const LOCAL_TOOL_SCHEMAS = [
  {
    name: "inspect_state",
    description: "READ ONLY. Inspect public-safe FCG neighborhood for a state root.",
    toolType: "local" as const,
    parametersSchema: {
      type: "object",
      properties: {
        experiment_id: { type: "string" },
        state_root: { type: "string" },
      },
      required: ["experiment_id"],
    },
  },
  {
    name: "trace_divergence",
    description: "Deterministically compare frozen reference and current state.",
    toolType: "local" as const,
    parametersSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "verify_actor_proof",
    description: "Run deterministic toy Ed25519 proof verifier. Returns VALID|INVALID|MISSING|REPLAYED|MALFORMED.",
    toolType: "local" as const,
    parametersSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "attempt_repair",
    description:
      "Request an EPHEMERAL repair candidate only. Never mutates canonical FCO/FCG. May be denied by policy.",
    toolType: "local" as const,
    parametersSchema: {
      type: "object",
      properties: {
        requested_repair: { type: "string" },
        previous_proof_state: { type: "string" },
      },
    },
  },
];

function sanitizePayload(payload: Record<string, unknown>) {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(payload)) {
    if (/secret|private_key|api_key/i.test(k)) continue;
    out[k] = v;
  }
  return out;
}

export function hashToolResult(result: unknown): string {
  return sha256Text(canonicalJson(result));
}

/** Self-check that reference proof verifies VALID (fixture integrity). */
export function assertReferenceProofValid(): ProofState {
  const ref = loadReference();
  const ctx: ToolContext = {
    experiment_id: "fixture-check",
    perturbation: "CONTROL",
    reference: ref,
    current: ref,
    expectedEarliest: null,
  };
  return verify_actor_proof(ctx).proof_state;
}
