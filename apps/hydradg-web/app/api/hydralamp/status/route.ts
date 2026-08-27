import { NextResponse } from "next/server";
import { getRun, verifyEventChain } from "@/lib/hydralamp/store";
import { readRun } from "@/lib/hydralamp/custody";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const runId = searchParams.get("run_id");
  if (!runId) return NextResponse.json({ error: "run_id required" }, { status: 400 });
  const run = getRun(runId) || readRun(runId);
  if (!run) return NextResponse.json({ error: "NOT_FOUND" }, { status: 404 });
  const chain = verifyEventChain(run.events || []);
  return NextResponse.json({
    run_id: run.run_id,
    mode: run.mode,
    done: run.done,
    perturbation: run.perturbation,
    reference_root: run.reference_root,
    current_root: run.current_root,
    earliest_divergence_expected: run.earliest_divergence_expected,
    lifecycle_phase: run.lifecycle_phase || null,
    provider_badge: run.provider_badge || null,
    evidence_packet_sha256: run.evidence_packet_sha256 || null,
    fco_lineage: run.fco_lineage || null,
    mitosis_memory_state: run.mitosis_memory_state || null,
    cloudflare_projection: run.cloudflare_projection || null,
    lanes: run.lanes,
    verifier: run.verifier,
    fcg: run.fcg,
    quarantine: run.quarantine,
    graph_nodes: run.graph_nodes,
    graph_edges: run.graph_edges,
    hydradb: run.hydradb,
    claim_ceiling: run.claim_ceiling,
    event_count: run.events.length,
    last_event_hash: run.last_event_hash,
    hash_chain: chain,
    timings: run.timings,
    final_frame: run.done
      ? {
          title: "HYDRALAMP",
          tagline: "Models propose. Custody decides.",
          decisions: run.lanes.map((l) => ({
            lane: l.lane,
            model_id: l.model_id,
            decision: l.structured?.decision || l.status,
            context_hash: l.context_hash,
            model_output_hash: l.model_output_hash,
            proposal_hash: l.proposal_hash,
            verification_result: l.verification_result,
            fcg_before: l.fcg_root_before,
            fcg_after: l.fcg_root_after,
          })),
          earliest_divergence: run.earliest_divergence_expected,
          fcg: run.fcg,
          quarantine: run.quarantine,
          hydradb: run.hydradb,
          hash_chain_ok: chain.ok,
        }
      : null,
  });
}
