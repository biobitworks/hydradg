import { NextResponse } from "next/server";
import { buildProviderHealth } from "@/lib/providers/health";
import { DOCUMENTED_SERVER_ENV } from "@/lib/providers/secrets";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

export async function GET(req: Request) {
  const url = new URL(req.url);
  const probe = url.searchParams.get("probe") === "1" || url.searchParams.get("probe") === "true";
  const health = await buildProviderHealth({ probe });
  return NextResponse.json({
    ...health,
    documented_server_env: [...DOCUMENTED_SERVER_ENV],
    note: "CONFIGURED means a key or public endpoint is present. It is never PASS.",
  });
}
