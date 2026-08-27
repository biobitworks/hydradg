/**
 * Morning golden-path incident: NORMAL → POISON → ANTIDOTE → RESTORED
 * Uses frozen LongMemEval K5/K10 evidence packet. Deterministic custody authority.
 */
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { sha256Text, canonicalJson, repoRoot, stateRoot } from "./fixtures";
import type { FixtureState, FcoLike } from "./types";

export type LifecyclePhase =
  | "NORMAL"
  | "POISON"
  | "QUARANTINED"
  | "ANTIDOTE"
  | "RESTORED";

export type EvidencePacket = {
  schema: string;
  packet_id: string;
  claim_ceiling: string;
  accepted_state_A: Record<string, unknown>;
  poison_candidate_B: Record<string, unknown>;
  corrected_state_C: Record<string, unknown>;
};

export function loadEvidencePacket(): EvidencePacket {
  const p = path.join(
    repoRoot(),
    "eval",
    "hydralamp_morning_20260827",
    "LONGMEMEVAL_EVIDENCE_PACKET.json",
  );
  if (!existsSync(p)) {
    throw new Error(`Evidence packet missing: ${p}`);
  }
  return JSON.parse(readFileSync(p, "utf8")) as EvidencePacket;
}

export function evidencePacketSha256(): string {
  const p = path.join(
    repoRoot(),
    "eval",
    "hydralamp_morning_20260827",
    "LONGMEMEVAL_EVIDENCE_PACKET.json",
  );
  return sha256Text(readFileSync(p, "utf8"));
}

function fco(type: string, payload: Record<string, unknown>): FcoLike {
  const body = { type, payload };
  const object_sha256 = sha256Text(canonicalJson(body));
  return {
    id: `fco:${object_sha256}`,
    object_sha256,
    type,
    payload,
  };
}

/** Build reference graph = accepted evidence-bounded state A. */
export function materializeLongMemEvalIncident(): {
  reference: FixtureState;
  poison: FixtureState;
  restored: FixtureState;
  packet: EvidencePacket;
  packet_sha256: string;
  fco_A: string;
  fco_B: string;
  fco_C: string;
  earliest_divergence: string;
} {
  const packet = loadEvidencePacket();
  const packet_sha256 = evidencePacketSha256();

  const A = fco("AcceptedEvidenceBoundedClaim", {
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
    role: "NORMAL_ACCEPTED_STATE_A",
    statement: packet.accepted_state_A.statement,
    packet_id: packet.packet_id,
    packet_sha256,
    claim_ceiling: packet.claim_ceiling,
    current: true,
  });

  const meta = fco("EvidencePacketPointer", {
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
    path: "eval/hydralamp_morning_20260827/LONGMEMEVAL_EVIDENCE_PACKET.json",
    packet_sha256,
    k5_A_hit: (packet.accepted_state_A.k5 as Record<string, unknown>).treatment_A_hit_at_5,
    k5_D_hit: (packet.accepted_state_A.k5 as Record<string, unknown>).treatment_D_hit_at_5,
    k10_primary: (packet.accepted_state_A.k10 as Record<string, unknown>).primary_result,
    n_scored: packet.accepted_state_A.n_scored,
    n_abstentions: packet.accepted_state_A.n_abstentions,
  });

  const reference: FixtureState = {
    schema: "hydralamp.fixture.v1",
    state_id: "LONGMEMEVAL_NORMAL_A",
    synthetic: false,
    security_incident: false,
    objects: { [A.id]: A, [meta.id]: meta },
    edges: [{ from: A.id, to: meta.id, type: "SUPPORTED_BY" }],
    state_root: "",
  };
  reference.state_root = stateRoot(reference);

  const B = fco("UntrustedOverclaimCandidate", {
    evidence_class: "INFERENCE_HYPOTHESIS",
    role: "POISON_CANDIDATE_B",
    statement: packet.poison_candidate_B.statement,
    classification: packet.poison_candidate_B.classification,
    malicious_intent: "NOT_ESTABLISHED",
    contradicts: A.id,
    current: false,
    quarantine: true,
  });

  const poison: FixtureState = {
    schema: "hydralamp.fixture.v1",
    state_id: "LONGMEMEVAL_POISON_B",
    synthetic: false,
    security_incident: false,
    objects: { ...reference.objects, [B.id]: B },
    edges: [
      ...reference.edges,
      { from: B.id, to: A.id, type: "CONTRADICTS" },
      { from: B.id, to: A.id, type: "OVERCLAIMS" },
    ],
    state_root: "",
  };
  poison.state_root = stateRoot(poison);

  const C = fco("CorrectedAcceptedSuccessor", {
    evidence_class: "DETERMINISTIC_TOOL_OUTPUT",
    role: "RESTORED_STATE_C",
    statement: packet.corrected_state_C.statement,
    packet_id: packet.packet_id,
    packet_sha256,
    claim_ceiling: packet.claim_ceiling,
    supersedes_current_of: [A.id, B.id],
    retains_visible: [A.id, B.id],
    current: true,
  });

  const restored: FixtureState = {
    schema: "hydralamp.fixture.v1",
    state_id: "LONGMEMEVAL_RESTORED_C",
    synthetic: false,
    security_incident: false,
    objects: {
      ...poison.objects,
      [A.id]: {
        ...A,
        payload: { ...A.payload, current: false, superseded_by: C.id },
      },
      [C.id]: C,
    },
    edges: [
      ...poison.edges,
      { from: C.id, to: A.id, type: "SUPERSEDES" },
      { from: C.id, to: B.id, type: "SUPERSEDES_AS_CURRENT" },
      { from: C.id, to: meta.id, type: "SUPPORTED_BY" },
      { from: B.id, to: C.id, type: "QUARANTINED_NOT_ERASED" },
    ],
    state_root: "",
  };
  restored.state_root = stateRoot(restored);

  return {
    reference,
    poison,
    restored,
    packet,
    packet_sha256,
    fco_A: A.id,
    fco_B: B.id,
    fco_C: C.id,
    earliest_divergence: B.id,
  };
}
