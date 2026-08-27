"use client";

import { useEffect, useState } from "react";

type ProviderRow = {
  provider: string;
  priority: string;
  panel_state: string;
  discovery_state: string;
  live_status: string;
  claim_ceiling: string;
  receipt_path: string | null;
};

type GoldenPath = {
  source: string | null;
  memory: string | null;
  model: string | null;
  external_actor: string | null;
  custody: string;
  projection: string;
  composed_status: string;
  notes: string[];
};

type SponsorStatus = {
  GUM_DOCTOR_STATE: string;
  SPONSOR_SECRET_INJECTION: string;
  providers: ProviderRow[];
  golden_path: GoldenPath;
};

const STATE_COLOR: Record<string, string> = {
  LIVE_PASS: "#4ade80",
  PASS: "#4ade80",
  CONFIGURED: "#93c5fd",
  DISCOVERED: "#fde68a",
  ERROR: "#f87171",
  BLOCKED: "#fb923c",
  SKIPPED: "#a8a29e",
};

export default function SponsorMissionPanel() {
  const [data, setData] = useState<SponsorStatus | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/sponsors/status")
      .then((r) => r.json())
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  if (err) {
    return (
      <section style={{ marginTop: "1.5rem", padding: "1rem", background: "#2a1f1f", borderRadius: 8 }}>
        <h3>Sponsor Missions</h3>
        <p style={{ color: "#f87171" }}>Status unavailable: {err}</p>
      </section>
    );
  }

  if (!data) {
    return (
      <section style={{ marginTop: "1.5rem", padding: "1rem", background: "#1a1a1a", borderRadius: 8 }}>
        <h3>Sponsor Missions</h3>
        <p>Loading…</p>
      </section>
    );
  }

  const gp = data.golden_path;

  return (
    <section style={{ marginTop: "1.5rem", padding: "1rem", background: "#1a1a1a", borderRadius: 8, color: "#e8e5dc" }}>
      <h3 style={{ marginTop: 0 }}>Agent Natives Sponsor Missions</h3>
      <p style={{ fontSize: "0.9rem", opacity: 0.85 }}>
        GUM Doctor: <code>{data.GUM_DOCTOR_STATE}</code> · Secret injection:{" "}
        <code>{data.SPONSOR_SECRET_INJECTION}</code>
      </p>
      <p style={{ fontSize: "0.85rem", opacity: 0.75 }}>
        Configuration ≠ empirical success. Keys present are not shown here.
      </p>

      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.75rem", fontSize: "0.9rem" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #444", textAlign: "left" }}>
            <th style={{ padding: 6 }}>Provider</th>
            <th style={{ padding: 6 }}>Priority</th>
            <th style={{ padding: 6 }}>State</th>
            <th style={{ padding: 6 }}>Live</th>
          </tr>
        </thead>
        <tbody>
          {data.providers.map((p) => (
            <tr key={p.provider} style={{ borderBottom: "1px solid #333" }}>
              <td style={{ padding: 6 }}>{p.provider}</td>
              <td style={{ padding: 6 }}>{p.priority}</td>
              <td style={{ padding: 6, color: STATE_COLOR[p.panel_state] || "#ccc" }}>{p.panel_state}</td>
              <td style={{ padding: 6, color: STATE_COLOR[p.live_status] || "#ccc" }}>{p.live_status}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#252525", borderRadius: 6, fontSize: "0.85rem" }}>
        <strong>Golden path (factual)</strong>
        <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.2rem" }}>
          <li>SOURCE: {gp.source || "—"}</li>
          <li>MEMORY: {gp.memory || "—"}</li>
          <li>MODEL: {gp.model || "—"}</li>
          <li>EXTERNAL ACTOR: {gp.external_actor || "—"}</li>
          <li>CUSTODY: {gp.custody}</li>
          <li>PROJECTION: {gp.projection}</li>
        </ul>
        <p style={{ margin: "0.5rem 0 0", opacity: 0.8 }}>Composed: {gp.composed_status}</p>
        {gp.notes?.length > 0 && (
          <ul style={{ margin: "0.35rem 0 0", paddingLeft: "1.2rem", opacity: 0.75 }}>
            {gp.notes.map((n) => (
              <li key={n}>{n}</li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
