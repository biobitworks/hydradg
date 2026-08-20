import { NextResponse } from "next/server";

import { buildReleaseManifest } from "@/lib/releaseMeta";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const release = buildReleaseManifest();
  return NextResponse.json(release, {
    headers: {
      "Cache-Control": "no-store, max-age=0",
      "X-HydraDG-Read-Only": "true",
    },
  });
}
