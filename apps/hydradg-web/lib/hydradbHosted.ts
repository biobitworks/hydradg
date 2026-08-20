export type HostedHydraDBConfig = {
  apiKey: string;
  database: string;
  collection: string;
  baseUrl: string;
  canarySourceId: string;
};

export function hostedHydraDBConfig(): HostedHydraDBConfig {
  return {
    apiKey: process.env.HYDRA_DB_API_KEY || process.env.HYDRADB_API_KEY || "",
    database:
      process.env.HYDRADB_DATABASE ||
      process.env.HYDRA_DB_DATABASE ||
      process.env.HYDRADB_TENANT_ID ||
      process.env.HYDRA_DB_TENANT_ID ||
      "",
    collection:
      process.env.HYDRADB_COLLECTION ||
      process.env.HYDRA_DB_COLLECTION ||
      process.env.HYDRADB_SUB_TENANT_ID ||
      process.env.HYDRA_DB_SUB_TENANT_ID ||
      "",
    baseUrl: (process.env.HYDRADB_API_URL || "https://api.hydradb.com").replace(/\/$/, ""),
    canarySourceId: process.env.HYDRADG_PUBLIC_CANARY_SOURCE_ID || "",
  };
}

export async function hostedHydraDBRequest(path: string, method: "GET" | "POST" = "GET", body?: unknown) {
  const cfg = hostedHydraDBConfig();
  if (!cfg.apiKey) throw new Error("HYDRA_DB_API_KEY is not configured");

  let lastError: Error | null = null;
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const response = await fetch(`${cfg.baseUrl}${path}`, {
        method,
        headers: {
          Authorization: `Bearer ${cfg.apiKey}`,
          "API-Version": "2",
          ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
        },
        body: method === "POST" ? JSON.stringify(body || {}) : undefined,
        cache: "no-store",
        signal: AbortSignal.timeout(20_000),
      });
      const data = await response.json().catch(() => ({ status: response.status }));
      if (response.ok) return { status: response.status, data };

      const message = data?.error?.message || data?.detail?.message || data?.message || `HydraDB hosted API request failed (${response.status})`;
      if (![429, 500, 503].includes(response.status) || attempt === 3) throw new Error(message);
      await new Promise((resolve) => setTimeout(resolve, 2 ** attempt * 500));
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt === 3) break;
    }
  }
  throw lastError || new Error("HydraDB hosted API request failed");
}

export async function hostedHydraDBStatus() {
  const cfg = hostedHydraDBConfig();
  if (!cfg.apiKey) {
    return {
      configured: false as const,
      database_configured: Boolean(cfg.database),
      collection: cfg.collection || null,
      base_url: cfg.baseUrl,
      required: ["HYDRA_DB_API_KEY"],
      optional: ["HYDRADB_DATABASE", "HYDRADB_COLLECTION", "HYDRADB_API_URL", "HYDRADG_PUBLIC_CANARY_SOURCE_ID"],
      compatibility_aliases: ["HYDRADB_TENANT_ID", "HYDRADB_SUB_TENANT_ID"],
      key_value_disclosed: false,
    };
  }

  if (!cfg.database) {
    const databases = await hostedHydraDBRequest("/databases");
    const available = (databases.data as any)?.data?.databases;
    return {
      configured: true as const,
      database_configured: false,
      collection: cfg.collection || null,
      base_url: cfg.baseUrl,
      key_present: true,
      key_value_disclosed: false,
      databases_available: Array.isArray(available) ? available.length : null,
      claim_ceiling: "HYDRADB_HOSTED_KEY_AND_DATABASE_DISCOVERY_ONLY",
    };
  }

  const status = await hostedHydraDBRequest(`/databases/status?database=${encodeURIComponent(cfg.database)}`);
  let traceability: Record<string, unknown> = {
    state: "CANARY_SOURCE_NOT_CONFIGURED",
  };

  if (cfg.canarySourceId) {
    const params = new URLSearchParams({
      database: cfg.database,
      id: cfg.canarySourceId,
      limit: "500",
      type: "knowledge",
    });
    if (cfg.collection) params.set("collection", cfg.collection);
    const relations = await hostedHydraDBRequest(`/context/relations?${params.toString()}`);
    traceability = {
      state: "READBACK_REQUEST_SUCCEEDED",
      source_id: cfg.canarySourceId,
      response_status: relations.status,
      relation_payload_present: relations.data != null,
    };
  }

  return {
    configured: true as const,
    database_configured: true,
    database: cfg.database,
    collection: cfg.collection || null,
    base_url: cfg.baseUrl,
    key_present: true,
    key_value_disclosed: false,
    database_status_http: status.status,
    database_status: status.data,
    traceability,
    claim_ceiling: "REMOTE_HYDRADB_V2_CONNECTIVITY_AND_OPTIONAL_CANARY_READBACK_ONLY",
  };
}
