import { NextResponse } from "next/server";
import { CANONICAL_SEEDGRAPH_SNAPSHOT, canonicalSnapshotSha256 } from "@/lib/seedgraph/canonicalSnapshot";
import { detectSeedGraphGaps } from "@/lib/seedgraph/gap";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function payload() {
  const gaps = detectSeedGraphGaps();
  return {
    schema: "hydradg.seedgraph.gap.v1",
    canonical_snapshot: {
      identity: CANONICAL_SEEDGRAPH_SNAPSHOT.identity,
      graph_id: CANONICAL_SEEDGRAPH_SNAPSHOT.graph_id,
      sha256: canonicalSnapshotSha256(),
      node_count: CANONICAL_SEEDGRAPH_SNAPSHOT.nodes.length,
    },
    gaps,
    canonical_fcg_writes: 0,
    canonical_seedgraph_writes: 0,
    note: "Deterministic gap detection over a frozen snapshot. No Tavily call. No canonical mutation.",
  };
}

export async function POST() {
  return NextResponse.json(payload());
}

export async function GET() {
  return NextResponse.json(payload());
}
