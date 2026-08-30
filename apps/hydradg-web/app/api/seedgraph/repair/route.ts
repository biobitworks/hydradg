import { NextResponse } from "next/server";
import { redactSecrets } from "@/lib/providers/secrets";
import { repairSeedGraphGaps, type RepairRequest } from "@/lib/seedgraph/repair";
import type { SeedGraphGap } from "@/lib/seedgraph/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

export async function POST(req: Request) {
  let body: RepairRequest = {};
  try {
    body = (await req.json()) as RepairRequest;
  } catch {
    body = {};
  }

  const gaps = Array.isArray(body.gaps) ? (body.gaps as SeedGraphGap[]) : undefined;
  const gap_ids = Array.isArray(body.gap_ids)
    ? body.gap_ids.filter((id): id is string => typeof id === "string")
    : undefined;

  try {
    const result = await repairSeedGraphGaps({ gaps, gap_ids });
    return NextResponse.json(result);
  } catch (e) {
    return NextResponse.json(
      {
        error: "SEEDGRAPH_REPAIR_FAILED",
        message: redactSecrets(String((e as Error).message || e)).slice(0, 240),
        canonical_fcg_writes: 0,
        canonical_seedgraph_writes: 0,
        unauthorized_canonical_writes: 0,
      },
      { status: 500 },
    );
  }
}
