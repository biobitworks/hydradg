import { NextResponse } from "next/server";

import { hostedHydraDBConfig, hostedHydraDBRequest } from "@/lib/hydradbHosted";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const cfg = hostedHydraDBConfig();
  if (!cfg.apiKey || !cfg.database) {
    return NextResponse.json(
      {
        configured: false,
        database: cfg.database || null,
        required: ["HYDRA_DB_API_KEY", "HYDRADB_DATABASE"],
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
      },
      { status: 503 },
    );
  }

  try {
    const response = await hostedHydraDBRequest(`/databases/collections?database=${encodeURIComponent(cfg.database)}`);
    return NextResponse.json({
      configured: true,
      database: cfg.database,
      configured_collection: cfg.collection || null,
      hydradb: response.data,
      secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
      claim_ceiling: "HYDRADB_V2_COLLECTION_DISCOVERY_ONLY",
    });
  } catch (error) {
    return NextResponse.json(
      {
        configured: true,
        database: cfg.database,
        error: error instanceof Error ? error.message : String(error),
        secret_disclosure: "HYDRADB_CREDENTIAL_VALUES_NEVER_RETURNED",
      },
      { status: 503 },
    );
  }
}
