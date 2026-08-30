import { NextResponse } from "next/server";
import { buildProviderStatus } from "@/lib/providers/status";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Factual provider status. CONFIGURED is never PASS. */
export async function GET() {
  const status = await buildProviderStatus();
  return NextResponse.json(status);
}
