import { NextResponse } from "next/server";

import { buildSiteFcg } from "@/lib/siteFcg";

export const dynamic = "force-static";

export async function GET() {
  return NextResponse.json(buildSiteFcg(), {
    headers: {
      "Cache-Control": "public, max-age=0, s-maxage=3600",
    },
  });
}
