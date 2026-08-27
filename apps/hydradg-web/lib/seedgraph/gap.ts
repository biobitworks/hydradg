import { CANONICAL_SEEDGRAPH_SNAPSHOT, TAVILY_VERCEL_DOCS_URL } from "./canonicalSnapshot";
import type { CanonicalNode, SeedGraphGap } from "./types";

function expectedUrlFor(node: CanonicalNode): string | null {
  if (node.id === "sg-tavily-vercel-docs") return TAVILY_VERCEL_DOCS_URL;
  if (node.id === "sg-conflict-anchor") return node.source_url;
  return null;
}

function detectNodeGaps(node: CanonicalNode): SeedGraphGap[] {
  const gaps: SeedGraphGap[] = [];
  const expectedUrl = expectedUrlFor(node);

  if (!node.source_url) {
    gaps.push({
      gap_id: `${node.id}:MISSING_SOURCE_URL`,
      kind: "MISSING_SOURCE_URL",
      node_id: node.id,
      expected_url: expectedUrl,
      expected_sha256: null,
      expected_provenance_edge: node.provenance_edge,
      repairable_by_tavily: Boolean(expectedUrl),
      notes: expectedUrl
        ? "Missing source URL; Tavily extract/search may retrieve external evidence."
        : "No expected URL; Tavily must not invent a source. Outcome is ABSTAIN.",
    });
  }

  if (!node.source_sha256) {
    gaps.push({
      gap_id: `${node.id}:MISSING_SOURCE_SHA256`,
      kind: "MISSING_SOURCE_SHA256",
      node_id: node.id,
      expected_url: expectedUrl ?? node.source_url,
      expected_sha256: null,
      expected_provenance_edge: node.provenance_edge,
      repairable_by_tavily: Boolean(expectedUrl ?? node.source_url),
      notes: "Missing raw-byte SHA-256 for the declared source.",
    });
  }

  if (!node.provenance_edge) {
    gaps.push({
      gap_id: `${node.id}:MISSING_PROVENANCE_EDGE`,
      kind: "MISSING_PROVENANCE_EDGE",
      node_id: node.id,
      expected_url: expectedUrl ?? node.source_url,
      expected_sha256: node.source_sha256,
      expected_provenance_edge: "retrieved:externally-retrieved-evidence",
      repairable_by_tavily: Boolean(expectedUrl ?? node.source_url),
      notes: "Missing provenance edge from node to source evidence.",
    });
  }

  if (node.kind === "EXTERNAL_DOC" && (!node.source_url || !node.source_sha256)) {
    gaps.push({
      gap_id: `${node.id}:UNRESOLVED_EXTERNAL_DOC`,
      kind: "UNRESOLVED_EXTERNAL_DOC",
      node_id: node.id,
      expected_url: expectedUrl ?? node.source_url,
      expected_sha256: node.source_sha256,
      expected_provenance_edge: node.provenance_edge,
      repairable_by_tavily: Boolean(expectedUrl ?? node.source_url),
      notes: "External document node is unresolved against a hashed source.",
    });
  }

  if (node.id === "sg-conflict-anchor") {
    gaps.push({
      gap_id: `${node.id}:UNRESOLVED_EXTERNAL_DOC`,
      kind: "UNRESOLVED_EXTERNAL_DOC",
      node_id: node.id,
      expected_url: expectedUrl ?? node.source_url,
      expected_sha256: node.source_sha256,
      expected_provenance_edge: node.provenance_edge,
      repairable_by_tavily: true,
      notes: "Frozen conflict SHA cannot be satisfied by retrieved bytes. Canonical mutation forbidden.",
    });
  }

  return gaps;
}

export function detectSeedGraphGaps(): SeedGraphGap[] {
  const gaps = CANONICAL_SEEDGRAPH_SNAPSHOT.nodes.flatMap(detectNodeGaps);
  return gaps.sort((a, b) => a.gap_id.localeCompare(b.gap_id));
}
