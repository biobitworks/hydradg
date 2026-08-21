import { NextResponse } from "next/server";

import { hostedHydraDBStatus } from "@/lib/hydradbHosted";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const status = await hostedHydraDBStatus();
    const traceability = (status as any).traceability?.state;
    const configured = status.configured === true && (status as any).database_configured === true;
    return NextResponse.json(
      {
        configured,
        backend: configured ? "HYDRADB_REMOTE_API_V2" : "NOT_CONFIGURED",
        database: status.database || "hydradg",
        collection: status.collection || "hydradg-judge-demo",
        historical_migration_collection: "default",
        current_discovered_collection: status.collection || "hydradg-judge-demo",
        collection_scope_changed: true,
        collection_scope_evidence:
          "Historical receipt recorded a prior collection scope; current runtime uses the configured hydradg-judge-demo scope.",
        environment: "PUBLIC",
        source_state: configured ? "REMOTE_HYDRADB_PUBLIC_FCG" : "NO_REMOTE_HYDRADB_STATE",
        backend_connectivity: configured ? "PASS" : "FAIL",
        database_binding: configured ? "PASS" : "FAIL",
        collection_discovery: configured ? "PASS" : "FAIL",
        canonical_parity_receipt: (status as any).canonical_parity_receipt || "NOT_ESTABLISHED",
        live_source_traceability:
          (status as any).live_source_traceability ||
          (traceability === "READBACK_REQUEST_SUCCEEDED" ? "PASS_REQUEST_LEVEL" : "PENDING_CANARY_READBACK"),
        hydradb_traceability_canary:
          (status as any).live_source_traceability ||
          (traceability === "READBACK_REQUEST_SUCCEEDED" ? "PASS_REQUEST_LEVEL" : "PENDING_CANARY_READBACK"),
        hosted_status: status,
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
        claim_ceiling: "PUBLIC_REMOTE_HYDRADB_CONNECTIVITY_AND_REQUEST_LEVEL_TRACEABILITY_ONLY",
      },
      {
        status: configured ? 200 : 503,
        headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" },
      },
    );
  } catch (error) {
    return NextResponse.json(
      {
        configured: false,
        backend: "HYDRADB_REMOTE_API_V2",
        database: "hydradg",
        collection: "hydradg-judge-demo",
        historical_migration_collection: "default",
        current_discovered_collection: "hydradg-judge-demo",
        collection_scope_changed: true,
        environment: "PUBLIC",
        backend_connectivity: "FAIL",
        database_binding: "FAIL",
        collection_discovery: "FAIL",
        canonical_parity_receipt: "NOT_ESTABLISHED",
        live_source_traceability: "PENDING_CANARY_READBACK",
        hydradb_traceability_canary: "FAIL",
        error: error instanceof Error ? error.message : String(error),
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
        claim_ceiling: "NO_REMOTE_HYDRADB_CONNECTIVITY_CLAIM",
      },
      { status: 503, headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" } },
    );
  }
}
