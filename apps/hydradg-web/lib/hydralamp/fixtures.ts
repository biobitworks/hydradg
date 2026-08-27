import { createHash, createPublicKey, verify as cryptoVerify } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import type { FixtureState, PerturbationKind, ProofState } from "./types";

export function repoRoot(): string {
  // apps/hydradg-web -> repo root
  return path.resolve(process.cwd(), "..", "..");
}

export function fixturesDir(): string {
  return path.join(repoRoot(), "eval", "hydralamp_runtype_20260826", "fixtures");
}

export function loadJson<T>(relOrAbs: string): T {
  const p = path.isAbsolute(relOrAbs) ? relOrAbs : path.join(fixturesDir(), relOrAbs);
  return JSON.parse(readFileSync(p, "utf8")) as T;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(normalize(value));
}

function normalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => [k, normalize(v)]),
    );
  }
  return value;
}

export function sha256Text(text: string): string {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

export function stateRoot(state: Pick<FixtureState, "objects" | "edges">): string {
  return sha256Text(canonicalJson({ objects: state.objects, edges: state.edges }));
}

export function loadReference(): FixtureState {
  return loadJson<FixtureState>("REFERENCE_STATE.json");
}

export function loadPerturbedInvalid(): FixtureState {
  return loadJson<FixtureState>("PERTURBED_STATE.json");
}

export function loadExpected() {
  return loadJson<{
    earliest_divergent_dependency: string;
    reference_root: string;
    perturbed_root: string;
    expected_proof_state: ProofState;
  }>("EXPECTED_DIVERGENCE.json");
}

export function loadFixtureHashes() {
  return loadJson<Record<string, string>>("FIXTURE_HASHES.json");
}

export function loadSystemPrompt(): string {
  return readFileSync(path.join(fixturesDir(), "SYSTEM_PROMPT.txt"), "utf8");
}

/** Build perturbation variants from the frozen reference without inventing new crypto. */
export function materializeState(kind: PerturbationKind): {
  reference: FixtureState;
  current: FixtureState;
  expectedEarliest: string | null;
  expectedProof: ProofState;
} {
  const reference = loadReference();
  if (kind === "CONTROL") {
    return {
      reference,
      current: structuredClone(reference),
      expectedEarliest: null,
      expectedProof: "VALID",
    };
  }
  if (kind === "INVALID_PROOF") {
    const current = loadPerturbedInvalid();
    const expected = loadExpected();
    return {
      reference,
      current,
      expectedEarliest: expected.earliest_divergent_dependency,
      expectedProof: "INVALID",
    };
  }

  // REPLAYED_PROOF: change message while keeping original signature bytes → INVALID under Ed25519; labeled REPLAYED
  if (kind === "REPLAYED_PROOF") {
    const current = structuredClone(reference);
    const authEdge = current.edges.find((e) => e.type === "AUTHORIZED_BY");
    if (!authEdge) throw new Error("missing AUTHORIZED_BY");
    const proof = structuredClone(current.objects[authEdge.to]);
    proof.payload = {
      ...proof.payload,
      message: "HYDRALAMP_TOY_ACTOR_PROOF_V1:REPLAYED_NONCE",
      perturbation: "REPLAYED_PROOF",
    };
    const body = { type: proof.type, payload: proof.payload };
    proof.object_sha256 = sha256Text(canonicalJson(body));
    proof.id = `fco:${proof.object_sha256}`;
    current.objects[proof.id] = proof;
    authEdge.to = proof.id;
    // also retarget GOVERENED_BY from old proof if present
    for (const e of current.edges) {
      if (e.type === "GOVERNED_BY" && e.from !== proof.id) {
        // leave policy edge from new proof
      }
    }
    const policyEdgeIdx = current.edges.findIndex((e) => e.type === "GOVERNED_BY");
    if (policyEdgeIdx >= 0) {
      const policyTo = current.edges[policyEdgeIdx].to;
      current.edges[policyEdgeIdx] = { from: proof.id, to: policyTo, type: "GOVERNED_BY" };
    }
    current.state_id = "PERTURBED_REPLAYED_PROOF";
    current.state_root = stateRoot(current);
    return {
      reference,
      current,
      expectedEarliest: proof.id,
      expectedProof: "REPLAYED",
    };
  }

  // BROKEN_AUTHORIZATION_EDGE: AUTHORIZED_BY points to missing object id
  const current = structuredClone(reference);
  const auth = current.edges.find((e) => e.type === "AUTHORIZED_BY");
  if (!auth) throw new Error("missing AUTHORIZED_BY");
  const missingId = "fco:" + "0".repeat(64);
  auth.to = missingId;
  current.state_id = "PERTURBED_BROKEN_AUTHORIZATION_EDGE";
  current.state_root = stateRoot(current);
  return {
    reference,
    current,
    expectedEarliest: missingId,
    expectedProof: "MISSING",
  };
}

export function b64urlToBuf(b64url: string): Buffer {
  const pad = "=".repeat((4 - (b64url.length % 4)) % 4);
  const b64 = (b64url + pad).replace(/-/g, "+").replace(/_/g, "/");
  return Buffer.from(b64, "base64");
}

export function verifyToyEd25519(params: {
  message: string;
  signature_b64: string;
  public_key_b64: string;
}): ProofState {
  try {
    const pub = createPublicKey({
      key: Buffer.concat([
        Buffer.from("302a300506032b6570032100", "hex"),
        b64urlToBuf(params.public_key_b64),
      ]),
      format: "der",
      type: "spki",
    });
    const ok = cryptoVerify(
      null,
      Buffer.from(params.message, "utf8"),
      pub,
      b64urlToBuf(params.signature_b64),
    );
    return ok ? "VALID" : "INVALID";
  } catch {
    return "MALFORMED";
  }
}
