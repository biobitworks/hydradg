"use client";

import { useEffect, useState } from "react";

type StatusPayload = {
  configured?: boolean;
  backend?: string;
  database?: string;
  collection?: string;
  historical_migration_collection?: string;
  current_discovered_collection?: string;
  collection_scope_changed?: boolean;
  environment?: string;
  source_state?: string;
  backend_connectivity?: string;
  database_binding?: string;
  collection_discovery?: string;
  canonical_parity_receipt?: string;
  live_source_traceability?: string;
  hydradb_traceability_canary?: string;
  hosted_status?: {
    tenant_id?: string;
    database?: string;
    collection?: string;
    base_url?: string;
    traceability?: { state?: string; source_id?: string };
  };
  error?: string;
};

export default function PublicBackendStatus() {
  const [status, setStatus] = useState<StatusPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetch("/api/graph/status", { cache: "no-store" })
      .then(async (response) => {
        const payload = (await response.json()) as StatusPayload;
        if (!active) return;
        setStatus(payload);
        if (!response.ok) setError(payload.error || "Live hosted HydraDB readback is not configured for this Vercel deployment.");
      })
      .catch((caught) => {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : String(caught));
      });
    return () => { active = false; };
  }, []);

  const connected = status?.configured === true;
  const trace = status?.live_source_traceability || status?.hydradb_traceability_canary || "PENDING_CANARY_READBACK";
  const databaseName = status?.database || status?.hosted_status?.database || "hydradg";
  const discoveredCollection = status?.current_discovered_collection || status?.collection || "hydradg-judge-demo";
  const historicalCollection = status?.historical_migration_collection || "default";
  const parity = status?.canonical_parity_receipt || "NOT_ESTABLISHED";

  return (
    <section className="panel" aria-label="HydraDB execution and hosted connectivity status">
      <div className="panelHead">
        <div>
          <p className="eyebrow">HydraDB evidence plane · local use + hosted upload + Vercel readback</p>
          <h2>{connected ? "Hosted HydraDB live readback connected" : "HydraDB used; Vercel live readback not yet wired"}</h2>
        </div>
        <span className={connected ? "pill pillGood" : "pill pillWarn"}>
          {connected ? "PUBLIC LIVE" : "PUBLIC FALLBACK"}
        </span>
      </div>

      <p className="small muted note" style={{ marginTop: 0 }}>
        HydraDG has used HydraDB in the local/research pipeline and uploaded hosted data. The public Vercel application currently relies on repository-backed artifacts/connectors rather than a live HydraDB API readback. A hosted upload receipt is not the same as live parity or traceability proof.
      </p>

      <div className="metrics" style={{ gridTemplateColumns: "repeat(5,minmax(0,1fr))" }}>
        <div className="metric"><span className="metricLabel">Vercel Live Readback</span><strong>{status?.backend_connectivity || (connected ? "PASS" : "NOT_WIRED")}</strong></div>
        <div className="metric"><span className="metricLabel">Database</span><strong>{databaseName}</strong></div>
        <div className="metric"><span className="metricLabel">Collection Scope</span><strong>{discoveredCollection}</strong></div>
        <div className="metric"><span className="metricLabel">Hosted Parity</span><strong>{parity}</strong></div>
        <div className="metric"><span className="metricLabel">Traceability</span><strong>{trace}</strong></div>
      </div>

      <p className="small muted note">
        Historical receipt recorded collection <code>{historicalCollection}</code>. Current intended hosted scope is <code>{discoveredCollection}</code>. Live parity remains <code>NOT_ESTABLISHED</code> unless a scoped canary readback proves source identity, missing/extra accounting, and root comparison from the deployed application.
      </p>
      {error ? <p className="small" style={{ color: "var(--bad)" }}>{error}</p> : null}
    </section>
  );
}
