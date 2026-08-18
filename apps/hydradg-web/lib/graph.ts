type GraphParameters = Record<string, unknown>;
export type GraphRow = Record<string, unknown>;

function decodeHydraValue(value: unknown): unknown {
  if (!value || typeof value !== "object") return value;
  const record = value as { type?: string; value?: unknown };
  if (!("type" in record)) return value;
  if (record.type === "list" && Array.isArray(record.value)) {
    return record.value.map(decodeHydraValue);
  }
  if (record.type === "null") return null;
  return record.value;
}

async function runHydraDbHttp(
  query: string,
  parameters: GraphParameters,
): Promise<GraphRow[]> {
  const baseUrl = process.env.HYDRADB_HTTP_URL?.replace(/\/$/, "");
  const token = process.env.HYDRADB_AUTH_TOKEN;
  const graphId = process.env.HYDRADB_GRAPH_ID || "default";
  const namespace = process.env.HYDRADB_GRAPH_NAMESPACE || "default";
  const cellId = process.env.HYDRADB_CELL_ID || "cell-0";

  if (!baseUrl || !token) throw new Error("HydraDB HTTP backend is not configured");

  const response = await fetch(`${baseUrl}/v1/graphs/${encodeURIComponent(graphId)}/query`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "X-Graph-Namespace": namespace,
    },
    body: JSON.stringify({ cell_id: cellId, query, parameters, page_size: 256 }),
    cache: "no-store",
  });

  const body = (await response.json()) as {
    columns?: string[];
    rows?: unknown[][];
    error?: { code?: string; message?: string };
  };
  if (!response.ok) throw new Error(body.error?.message || `HydraDB query failed (${response.status})`);

  const columns = body.columns || [];
  return (body.rows || []).map((row) =>
    Object.fromEntries(columns.map((column, index) => [column, decodeHydraValue(row[index])])),
  );
}

function normalizeNeo4j(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(normalizeNeo4j);
  if (value && typeof value === "object") {
    const maybeInteger = value as { toNumber?: () => number; toString?: () => string };
    if (typeof maybeInteger.toNumber === "function") {
      try {
        return maybeInteger.toNumber();
      } catch {
        return maybeInteger.toString?.() ?? String(value);
      }
    }
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, val]) => [key, normalizeNeo4j(val)]),
    );
  }
  return value;
}

async function runNeo4j(query: string, parameters: GraphParameters): Promise<GraphRow[]> {
  const uri = process.env.NEO4J_URI;
  const username = process.env.NEO4J_USERNAME;
  const password = process.env.NEO4J_PASSWORD;
  const database = process.env.NEO4J_DATABASE || undefined;
  if (!uri || !username || !password) throw new Error("Neo4j backend is not configured");

  const neo4j = await import("neo4j-driver");
  const driver = neo4j.default.driver(uri, neo4j.default.auth.basic(username, password));
  const session = driver.session({ database });
  try {
    const result = await session.run(query, parameters);
    return result.records.map((record) => normalizeNeo4j(record.toObject()) as GraphRow);
  } finally {
    await session.close();
    await driver.close();
  }
}

export function graphBackend(): "hydradb-http" | "neo4j" {
  return process.env.GRAPH_BACKEND === "neo4j" ? "neo4j" : "hydradb-http";
}

export function graphConfigured(): boolean {
  if (graphBackend() === "neo4j") {
    return Boolean(process.env.NEO4J_URI && process.env.NEO4J_USERNAME && process.env.NEO4J_PASSWORD);
  }
  return Boolean(process.env.HYDRADB_HTTP_URL && process.env.HYDRADB_AUTH_TOKEN);
}

export async function runGraph(query: string, parameters: GraphParameters = {}): Promise<GraphRow[]> {
  return graphBackend() === "neo4j" ? runNeo4j(query, parameters) : runHydraDbHttp(query, parameters);
}

export async function probeGraph(): Promise<{ ok: boolean; error?: string }> {
  if (!graphConfigured()) return { ok: false, error: "not configured" };
  try {
    if (graphBackend() === "hydradb-http") {
      // HydraDB requires a node-only MATCH to carry an id, label, or property
      // predicate. A labeled read is valid even when no such node exists.
      await runGraph("MATCH (n:HydraDGHealth) RETURN n.id AS id LIMIT 1");
    } else {
      await runGraph("RETURN 1 AS ok");
    }
    return { ok: true };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : String(error) };
  }
}
