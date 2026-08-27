import { createHash } from "node:crypto";
import { canonicalJson } from "../fco";
import type { CanonicalSnapshot } from "./types";

/**
 * Frozen read-only SeedGraph snapshot for the Vercel control plane.
 * Canonical writes are forbidden. Repair emits successor-only artifacts.
 */
export const CANONICAL_SEEDGRAPH_SNAPSHOT: CanonicalSnapshot = {
  identity: "CANONICAL_FROZEN_SNAPSHOT",
  graph_id: "seedgraph.hydradg.vercel-control-plane.v1",
  nodes: [
    {
      id: "sg-tavily-vercel-docs",
      kind: "EXTERNAL_DOC",
      label: "Tavily Vercel AI SDK integration docs",
      source_url: null,
      source_sha256: null,
      provenance_edge: null,
      claim_ceiling: "C2",
    },
    {
      id: "sg-internal-policy",
      kind: "POLICY",
      label: "Quarantine-before-canonical policy",
      source_url: null,
      source_sha256: null,
      provenance_edge: "policy:quarantine-before-canonical",
      claim_ceiling: "C1",
    },
    {
      id: "sg-conflict-anchor",
      kind: "EXTERNAL_DOC",
      label: "Conflicting placeholder (must not repair into canonical)",
      source_url: "https://example.invalid/conflict-anchor",
      source_sha256: "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
      provenance_edge: "conflict:expected-sha-mismatch",
      claim_ceiling: "C2",
    },
  ],
};

export const TAVILY_VERCEL_DOCS_URL =
  "https://docs.tavily.com/documentation/integrations/vercel";

export function canonicalSnapshotSha256(): string {
  return createHash("sha256").update(canonicalJson(CANONICAL_SEEDGRAPH_SNAPSHOT)).digest("hex");
}
