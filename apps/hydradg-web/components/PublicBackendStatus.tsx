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
        setError(response.ok ? "" : payload.error || "Hosted HydraDB is not configured for this deployment.");
      })
      .catch((caught) => {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : String(caught));
      });
    return () => { active = false; };
  }, []);

  const connected = status?.configured === true;
  const trace = status?.hydradb_traceability_canary || (connected ? "REQUEST_LEVEL_NOT_RUN" : "NOT_CONFIGURED");
  const database = status?.hosted_status?.database || (connected ? "hydradg" : "NOT_CONFIGURED");
  const collection = status?.hosted_status?.collection || (connected ? "default / configured scope" : "NOT_CONFIGURED");

  return (
    <section className="panel" aria-label="Public backend status">
      <div className="panelHead">
        <div>
          <p className="eyebrow">Public data plane</p>
          <h2>{connected ? "Hosted HydraDB connected" : "Hosted HydraDB not configured on this deployment"}</h2>
        </div>
        <span className={connected ? "pill pillGood" : "pill pillWarn"}>{connected ? "PUBLIC LIVE" : "NO LIVE BACKEND"}</span>
      </div>
      <div className="metrics" style={{ gridTemplateColumns: "repeat(4,minmax(0,1fr))" }}>
        <div className="metric"><span className="metricLabel">Backend</span><strong>{status?.backend || "CHECKING"}</strong></div>
        <div className="metric"><span className="metricLabel">Database</span><strong>{database}</strong></div>
        <div className="metric"><span className="metricLabel">Collection</span><strong>{collection}</strong></div>
        <div className="metric"><span className="metricLabel">Traceability</span><strong>{trace}</strong></div>
      </div>
      <p className="small muted note">This is a live server-side connectivity/readback diagnostic, separate from the committed hosted-parity receipt and separate from scientific correctness. HydraDB credential values are never returned to the browser.</p>
      {error ? <p className="small" style={{ color: "var(--bad)" }}>{error}</p> : null}
    </section>
  );
}
