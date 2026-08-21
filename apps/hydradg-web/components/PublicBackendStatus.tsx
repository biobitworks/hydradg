"use client";

import { useEffect, useState } from "react";

import GoldenPathStep from "@/components/GoldenPathStep";

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
        if (!response.ok) setError(payload.error || "Live hosted HydraDB readback is not configured for this deployment.");
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
    <section id="hydradb-status" style={{ scrollMarginTop: "155px" }} aria-label="HydraDB execution and hosted connectivity status">
      <GoldenPathStep
        step={4}
        compact
        summary="Verify that HydraDB is actually reachable and distinguish connectivity/readback from full canonical parity. Request-level traceability may pass while the 653-FCO / 1,692-edge parity gate remains separate."
      />

      <div className="panel">
        <div className="panelHead">
          <div>
            <p className="eyebrow">Step 04 of 08 · HydraDB evidence plane</p>
            <h2>{connected ? "Hosted HydraDB live readback connected" : "HydraDB used; live readback not yet wired"}</h2>
          </div>
          <span className={connected ? "pill pillGood" : "pill pillWarn"}>
            {connected ? "CONNECTED" : "FALLBACK"}
          </span>
        </div>

        <p className="small muted note" style={{ marginTop: 0 }}>
          This step answers one question: can the judge surface reach the intended HydraDB data plane? Connectivity, canary traceability, and full graph parity remain distinct evidence claims.
        </p>

        <div className="metrics" style={{ gridTemplateColumns: "repeat(5,minmax(0,1fr))" }}>
          <div className="metric"><span className="metricLabel">Live Readback</span><strong>{status?.backend_connectivity || (connected ? "PASS" : "NOT_WIRED")}</strong></div>
          <div className="metric"><span className="metricLabel">Database</span><strong>{databaseName}</strong></div>
          <div className="metric"><span className="metricLabel">Collection</span><strong>{discoveredCollection}</strong></div>
          <div className="metric"><span className="metricLabel">Canonical Parity</span><strong>{parity}</strong></div>
          <div className="metric"><span className="metricLabel">Canary Traceability</span><strong>{trace}</strong></div>
        </div>

        <p className="small muted note">
          Historical receipt scope: <code>{historicalCollection}</code>. Current intended hosted scope: <code>{discoveredCollection}</code>. A successful canary request proves request-level traceability; full parity requires scoped FCO/edge counts, missing/extra accounting, identity mapping, and root comparison.
        </p>
        {error ? <p className="small" style={{ color: "var(--bad)" }}>{error}</p> : null}
      </div>
    </section>
  );
}
