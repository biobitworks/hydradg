/**
 * Successor-only in-memory store. Canonical SeedGraph / FCG are never written.
 * Serverless instances do not share this store; repair remains request-scoped.
 */

export type SuccessorNode = {
  id: string;
  parent_canonical_node_id: string;
  source_url: string;
  source_sha256: string;
  provenance_edge: string;
  identity: "SUCCESSOR_NOT_CANONICAL";
};

export type SuccessorFcgAppend = {
  identity: "SUCCESSOR_NOT_CANONICAL";
  fcg_id: string;
  parent_canonical_graph_id: string;
  appended_at: string;
  node_id: string;
  evidence_sha256: string;
};

const successors: SuccessorNode[] = [];
const fcgAppends: SuccessorFcgAppend[] = [];

export function appendSuccessor(node: SuccessorNode, fcg: SuccessorFcgAppend): void {
  successors.push(node);
  fcgAppends.push(fcg);
}

export function successorCounts(): { successor_nodes: number; successor_fcg_appends: number } {
  return {
    successor_nodes: successors.length,
    successor_fcg_appends: fcgAppends.length,
  };
}

export function canonicalWriteCount(): 0 {
  return 0;
}
