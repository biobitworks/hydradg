import { NextResponse } from "next/server";

import { RELEASE_STATUS } from "@/lib/releaseStatus";

export async function GET() {
  return NextResponse.json({
    schema: "hydradg.release_status.v1",
    ...RELEASE_STATUS,
    claim_ceiling: "RECORDED_RELEASE_STATE_ONLY",
  });
}
