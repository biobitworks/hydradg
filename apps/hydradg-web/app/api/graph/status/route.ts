import { NextResponse } from "next/server";

import { hostedHydraDBStatus } from "@/lib/hydradbHosted";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const status = await hostedHydraDBStatus();
    const traceability = (status as any).traceability?.state;
    const configured = status.configured === true && (status as any).tenant_configured === true;
    return NextResponse.json(
      {
        configured,
        backend: configured ? "HYDRADB_REMOTE_API" : "NOT_CONFIGURED",
        environment: "PUBLIC",
        source_state: configured ? "REMOTE_HYDRADB_PUBLIC_FCG" : "NO_REMOTE_HYDRADB_STATE",
        hydradb_traceability_canary:
          traceability === "READBACK_REQUEST_SUCCEEDED" ? "PASS_REQUEST_LEVEL" : "NOT_ESTABLISHED",
        hosted_status: status,
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
        claim_ceiling: "PUBLIC_REMOTE_HYDRADB_CONNECTIVITY_STATUS_ONLY",
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
        backend: "HYDRADB_REMOTE_API",
        environment: "PUBLIC",
        hydradb_traceability_canary: "FAIL",
        error: error instanceof Error ? error.message : String(error),
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
        claim_ceiling: "NO_REMOTE_HYDRADB_CONNECTIVITY_CLAIM",
      },
      { status: 503, headers: { "Cache-Control": "no-store, max-age=0", "X-HydraDG-Read-Only": "true" } },
    );
  }
}
