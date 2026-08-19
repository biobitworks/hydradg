import { RELEASE_STATUS } from "@/lib/releaseStatus";

export const dynamic = "force-dynamic";

export async function GET() {
  const rows = Object.entries(RELEASE_STATUS.tracks).map(([track_id, value]) => ({
    track_id,
    ...value,
  }));
  return Response.json({
    schema: "hydradg.public_track_registry.v1",
    read_only: true,
    tracks: rows,
    claim_ceiling: "TRACK_IMPLEMENTATION_AND_EXECUTION_STATUS_ONLY",
    signature_state: RELEASE_STATUS.signature_state,
    merkle_state: RELEASE_STATUS.live_merkle_state,
  }, {
    headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" },
  });
}
