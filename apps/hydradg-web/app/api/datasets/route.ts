import { RELEASE_STATUS } from "@/lib/releaseStatus";

export const dynamic = "force-dynamic";

export async function GET() {
  const rows = Object.entries(RELEASE_STATUS.datasets).map(([dataset_id, value]) => ({
    dataset_id,
    ...value,
  }));
  return Response.json({
    schema: "hydradg.public_dataset_registry.v1",
    read_only: true,
    evidence_basis: RELEASE_STATUS.evidence_basis,
    datasets: rows,
    claim_ceiling: "DATASET_ACQUISITION_AND_RELEASE_STATUS_ONLY",
    signature_state: RELEASE_STATUS.signature_state,
    merkle_state: RELEASE_STATUS.live_merkle_state,
  }, {
    headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" },
  });
}
