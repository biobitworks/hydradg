"use client";

import { useEffect, useState } from "react";

type StatusPayload = {
  configured?: boolean;
  backend?: string;
  environment?: string;
  source_state?: string;
  hydradb_traceability_canary?: string;
  hosted_status?: {
    database?: string;
    collection?: string | null;
    base_url?: string;
    traceability?: { state?: string; source_id?: string };
  };
  error?: string;
};

type CollectionsPayload = {
  configured?: boolean;
  database?: string;
  configured_collection?: string | null;
  hydradb?: { data?: { collections?: string[]; sub_tenant_ids?: string[] } };
};

type TracePayload = {
  configured?: boolean;
  state?: string;
  database?: string;
  collection?: string | null;
  collection_source?: string;
  query_http?: number;
  query_apps?: boolean;
  graph_context?: boolean;
  result_payload_present?: boolean;
  claim_ceiling?: string;
  error?: string;
};

export default function PublicBackendStatus() {
  const [status, setStatus] = useState<StatusPayload | null>(null);
  const [collections, setCollections] = useState<CollectionsPayload | null>(null);
  const [traceability, setTraceability] = useState<TracePayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch("/api/graph/status", { cache: "no-store" }),
      fetch("/api/hydradb-v2/collections", { cache: "no-store" }),
      fetch("/api/hydradb-v2/traceability", { cache: "no-store" }),
    ])
      .then(async ([statusResponse, collectionsResponse, traceResponse]) => {
        const [statusPayload, collectionsPayload, tracePayload] = await Promise.all([
          statusResponse.json() as Promise<StatusPayload>,
          collectionsResponse.json() as Promise<CollectionsPayload>,
          traceResponse.json() as Promise<TracePayload>,
        ]);
        if (!active) return;
        setStatus(statusPayload);
        setCollections(collectionsPayload);
        setTraceability(tracePayload);
        const problems = [
          !statusResponse.ok ? statusPayload.error || "Hosted HydraDB connectivity failed." : "",
          !traceResponse.ok ? tracePayload.error || "Live HydraDB query traceability failed." : "",
        ].filter(Boolean);
        setError(problems.join(" "));
      })
      .catch((caught) => {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : String(caught));
      });
    return () => { active = false; };
  }, []);

  const connected = status?.configured === true;
  const discovered = collections?.hydradb?.data?.collections || collections?.hydradb?.data?.sub_tenant_ids || [];
  const database = traceability?.database || collections?.database || status?.hosted_status?.database || (connected ? "hydradg" : "NOT_CONFIGURED");
  const collection = traceability?.collection || collections?.configured_collection || discovered[0] || status?.hosted_status?.collection || (connected ? "DISCOVERY_REQUIRED" : "NOT_CONFIGURED");
  const trace = traceability?.state || status?.hydradb_traceability_canary || (connected ? "REQUEST_LEVEL_NOT_RUN" : "NOT_CONFIGURED");
  const traceGood = trace === "PASS_QUERY_LEVEL" || trace === "PASS_REQUEST_LEVEL";

  return (
    <section className="panel" aria-label="Public backend status">
      <div className="panelHead">
        <div>
          <p className="eyebrow">Public data plane</p>
          <h2>{connected ? "Hosted HydraDB connected" : "Hosted HydraDB not configured on this deployment"}</h2>
        </div>
        <div className="actions">
          <span className={connected ? "pill pillGood" : "pill pillWarn"}>{connected ? "PUBLIC LIVE" : "NO LIVE BACKEND"}</span>
          <span className={traceGood ? "pill pillGood" : "pill pillWarn"}>{traceGood ? "QUERY READBACK PASS" : "TRACEABILITY CHECK"}</span>
        </div>
      </div>
      <div className="metrics" style={{ gridTemplateColumns: "repeat(4,minmax(0,1fr))" }}>
        <div className="metric"><span className="metricLabel">Backend</span><strong>{status?.backend || "CHECKING"}</strong></div>
        <div className="metric"><span className="metricLabel">Database</span><strong>{database}</strong></div>
        <div className="metric"><span className="metricLabel">Collection</span><strong>{collection}</strong><span className="small muted">{traceability?.collection_source || (discovered.length ? "DISCOVERED" : "")}</span></div>
        <div className="metric"><span className="metricLabel">Traceability</span><strong>{trace}</strong><span className="small muted">{traceability?.query_http ? `query HTTP ${traceability.query_http}` : ""}</span></div>
      </div>
      <p className="small muted note">Connectivity, collection discovery and live query traceability are tested separately. Query-level PASS proves the production server can execute a read-only HydraDB query with graph/connector context; it does not by itself prove scientific correctness or source-specific semantic support. Credential values are never returned to the browser.</p>
      <div className="actions"><a className="secondary" href="/api/graph/status">Connectivity JSON</a><a className="secondary" href="/api/hydradb-v2/collections">Collection JSON</a><a className="secondary" href="/api/hydradb-v2/traceability">Traceability JSON</a></div>
      {error ? <p className="small" style={{ color: "var(--bad)" }}>{error}</p> : null}
    </section>
  );
}
