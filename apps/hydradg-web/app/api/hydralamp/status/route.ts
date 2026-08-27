import { NextResponse } from "next/server";
import { getRun } from "@/lib/hydralamp/store";
import { readRun } from "@/lib/hydralamp/custody";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const runId = searchParams.get("run_id");
  if (!runId) return NextResponse.json({ error: "run_id required" }, { status: 400 });
  const run = getRun(runId) || readRun(runId);
  if (!run) return NextResponse.json({ error: "NOT_FOUND" }, { status: 404 });
  return NextResponse.json({
    run_id: run.run_id,
    mode: run.mode,
    done: run.done,
    perturbation: run.perturbation,
    reference_root: run.reference_root,
    current_root: run.current_root,
    earliest_divergence_expected: run.earliest_divergence_expected,
    lanes: run.lanes,
    verifier: run.verifier,
    fcg: run.fcg,
    hydradb: run.hydradb,
    claim_ceiling: run.claim_ceiling,
    event_count: run.events.length,
    final_frame: run.done
      ? {
          title: "HYDRALAMP",
          tagline: "Models propose. Custody decides.",
          decisions: run.lanes.map((l) => ({
            lane: l.lane,
            model_id: l.model_id,
            decision: l.structured?.decision || l.status,
          })),
          earliest_divergence: run.earliest_divergence_expected,
          fcg: run.fcg,
          hydradb: run.hydradb,
        }
      : null,
  });
}
