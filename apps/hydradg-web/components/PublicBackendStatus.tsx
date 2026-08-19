"use client";

import { useEffect, useState } from "react";

type StatusPayload = {
  configured?: boolean;
  backend?: string;
  environment?: string;
  source_state?: string;
  hydradb_traceability_canary?: string;
  hosted_status?: {
    tenant_id?: string;
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
        if (!response.ok) setError(payload.error || "Hosted HydraDB is not configured for this deployment.");
      })
      .catch((caught) => {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : String(caught));
      });
    return () => { active = false; };
  }, []);

  const connected = status?.configured === true;
  const trace = status?.hydradb_traceability_canary || "NOT_ESTABLISHED";

  return (
    <section className="panel" aria-label="Public backend status">
      <div className="panelHead">
        <div>
          <p className="eyebrow">Public data plane</p>
          <h2>{connected ? "Hosted HydraDB connected" : "Hosted HydraDB not yet connected"}</h2>
        </div>
        <span className={connected ? "pill pillGood" : "pill pillWarn"}>
          {connected ? "PUBLIC LIVE" : "PUBLIC FALLBACK"}
        </span>
      </div>
      <div className="metrics" style={{ gridTemplateColumns: "repeat(3,minmax(0,1fr))" }}>
        <div className="metric"><span className="metricLabel">Backend</span><strong>{status?.backend || "PENDING"}</strong></div>
        <div className="metric"><span className="metricLabel">Traceability</span><strong>{trace}</strong></div>
        <div className="metric"><span className="metricLabel">Tenant</span><strong>{status?.hosted_status?.tenant_id || "PENDING"}</strong></div>
      </div>
      <p className="small muted note">
        This status is a server-side connectivity/readback diagnostic. It does not validate the scientific result.
        HydraDB credentials are never returned to the browser.
      </p>
      {error ? <p className="small" style={{ color: "var(--bad)" }}>{error}</p> : null}
    </section>
  );
}
