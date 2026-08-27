import { makeFcoNode, sha256Text } from "../fco";
import { tavilyRetrieve, type TavilyRetrieveResult } from "../providers/tavily";
import type { QuarantineRecord } from "../providers/types";
import { canonicalSnapshotSha256 } from "./canonicalSnapshot";
import { detectSeedGraphGaps } from "./gap";
import { appendSuccessor, canonicalWriteCount } from "./store";
import type { RepairVerdict, SeedGraphGap } from "./types";
import { verifyCandidate } from "./verify";

export type RepairRequest = {
  gaps?: SeedGraphGap[];
  gap_ids?: string[];
};

function selectGaps(req: RepairRequest): SeedGraphGap[] {
  const detected = detectSeedGraphGaps();
  const incoming = req.gaps?.length ? req.gaps : detected;
  if (req.gap_ids?.length) {
    const wanted = new Set(req.gap_ids);
    return incoming.filter((g) => wanted.has(g.gap_id));
  }
  return incoming;
}

function candidateFco(gap: SeedGraphGap, quarantine: QuarantineRecord | null) {
  return makeFcoNode("seedgraph.gap_repair.candidate", {
    gap_id: gap.gap_id,
    node_id: gap.node_id,
    expected_url: gap.expected_url,
    quarantine_id: quarantine?.quarantine_id ?? null,
    raw_sha256: quarantine?.raw_sha256 ?? null,
    evidence_class: "EXTERNALLY_RETRIEVED_EVIDENCE",
    custody_state: "QUARANTINED",
    canonical_mutation: false,
  });
}

async function retrieveCached(
  cache: Map<string, TavilyRetrieveResult>,
  url: string,
): Promise<TavilyRetrieveResult> {
  const hit = cache.get(url);
  if (hit) return hit;
  const retrieved = await tavilyRetrieve({
    operation: "extract",
    urls: [url],
    query: url,
  });
  cache.set(url, retrieved);
  return retrieved;
}

export async function repairSeedGraphGaps(req: RepairRequest = {}) {
  const gaps = selectGaps(req);
  const verdicts: RepairVerdict[] = [];
  const retrievals: QuarantineRecord[] = [];
  const cache = new Map<string, TavilyRetrieveResult>();
  let successorAppends = 0;

  for (const gap of gaps) {
    let quarantine: QuarantineRecord | null = null;
    let retrieveStatus: TavilyRetrieveResult["status"] | null = null;

    if (gap.expected_url && (gap.repairable_by_tavily || gap.node_id === "sg-conflict-anchor")) {
      const retrieved = await retrieveCached(cache, gap.expected_url);
      retrieveStatus = retrieved.status;
      if (retrieved.quarantine) {
        quarantine = retrieved.quarantine;
        if (!retrievals.some((q) => q.quarantine_id === quarantine!.quarantine_id)) {
          retrievals.push(quarantine);
        }
      }
    }

    const verification = verifyCandidate(gap, quarantine, retrieveStatus);
    const fco = candidateFco(gap, quarantine);
    let successorNodeId: string | null = null;
    let successorAppended = false;

    if (verification.outcome === "PASS" && quarantine && gap.expected_url) {
      successorNodeId = `successor:${gap.node_id}:${quarantine.raw_sha256.slice(0, 12)}`;
      appendSuccessor(
        {
          id: successorNodeId,
          parent_canonical_node_id: gap.node_id,
          source_url: gap.expected_url,
          source_sha256: quarantine.raw_sha256,
          provenance_edge: "retrieved:externally-retrieved-evidence",
          identity: "SUCCESSOR_NOT_CANONICAL",
        },
        {
          identity: "SUCCESSOR_NOT_CANONICAL",
          fcg_id: `fcg-successor-${sha256Text(successorNodeId).slice(0, 16)}`,
          parent_canonical_graph_id: "seedgraph.hydradg.vercel-control-plane.v1",
          appended_at: new Date().toISOString(),
          node_id: successorNodeId,
          evidence_sha256: quarantine.raw_sha256,
        },
      );
      successorAppended = true;
      successorAppends += 1;
    }

    verdicts.push({
      gap_id: gap.gap_id,
      outcome: verification.outcome,
      reasons: verification.reasons,
      candidate_fco_id: fco.id,
      candidate_fco_sha256: fco.object_sha256,
      successor_node_id: successorNodeId,
      successor_fcg_appended: successorAppended,
    });
  }

  return {
    schema: "hydradg.seedgraph.repair.v1",
    canonical_snapshot_sha256: canonicalSnapshotSha256(),
    canonical_fcg_writes: canonicalWriteCount(),
    canonical_seedgraph_writes: 0,
    unauthorized_canonical_writes: 0,
    successor_fcg_appends: successorAppends,
    fcg: { identity: "SUCCESSOR_NOT_CANONICAL" as const },
    gaps_considered: gaps.map((g) => g.gap_id),
    retrievals: retrievals.map((q) => ({
      quarantine_id: q.quarantine_id,
      operation: q.operation,
      evidence_class: q.evidence_class,
      custody_state: q.custody_state,
      raw_sha256: q.raw_sha256,
      result_count: q.result_count,
    })),
    verdicts,
    signature_state: "NOT_SIGNED" as const,
  };
}
