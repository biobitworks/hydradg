"use client";

import { useEffect, useState } from "react";
import SiteNav from "@/components/SiteNav";

type Preserved = {
  receipt_path: string;
  receipt_present: boolean;
  live_status: string;
  error_code: string | null;
  lane: string;
  note: string;
};

type ProviderRow = {
  provider: string;
  lane: string;
  secret_state: string;
  config_state: string;
  runtime_state: string;
  panel_state: string;
  hosted_on_vercel: boolean;
  claim_ceiling: string;
  note: string;
};

type StatusPayload = {
  schema: string;
  scientific_execution_authority: string;
  vercel_runtime: boolean;
  invariant: string;
  preserved_studio_receipts: Record<string, Preserved>;
  preserved_invariants: Record<string, string>;
  providers: ProviderRow[];
  note: string;
};

const COLOR: Record<string, string> = {
  PASS: "#4ade80",
  LIVE_PASS: "#4ade80",
  CONFIGURED: "#93c5fd",
  ERROR: "#f87171",
  BLOCKED: "#fb923c",
  SKIPPED: "#a8a29e",
  NOT_PROBED: "#cbd5e1",
};

function Badge({ state }: { state: string }) {
  return (
    <code
      style={{
        color: COLOR[state] || "#e8e5dc",
        background: "#111",
        padding: "0.1rem 0.4rem",
        borderRadius: 4,
        fontSize: "0.85rem",
      }}
    >
      {state}
    </code>
  );
}

export default function ProvidersPage() {
  const [data, setData] = useState<StatusPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/providers/status")
      .then(async (r) => {
        if (!r.ok) throw new Error(`HTTP_${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  return (
    <main style={{ minHeight: "100vh", background: "#0b0c0f", color: "#e8e5dc" }}>
      <SiteNav />
      <div style={{ maxWidth: 960, margin: "0 auto", padding: "2rem 1.25rem 4rem" }}>
        <header style={{ marginBottom: "1.5rem" }}>
          <p style={{ opacity: 0.7, letterSpacing: "0.08em", textTransform: "uppercase", fontSize: "0.75rem" }}>
            Vercel control plane
          </p>
          <h1 style={{ margin: "0.25rem 0 0.5rem", fontSize: "1.75rem" }}>Provider health</h1>
          <p style={{ margin: 0, maxWidth: 640, lineHeight: 1.5, opacity: 0.9 }}>
            Factual status only. Key presence is <Badge state="CONFIGURED" />, never PASS. Studio receipts remain
            authoritative for Tavily PASS, Runtype ERROR, Cortex ERROR / CORTEX_TRIAL_EXPIRED, and Daytona
            INFRASTRUCTURE / LIVE_PASS.
          </p>
        </header>

        {err && (
          <p style={{ color: "#f87171" }}>Status unavailable: {err}</p>
        )}

        {!data && !err && <p>Loading…</p>}

        {data && (
          <>
            <section
              style={{
                marginBottom: "1.5rem",
                padding: "1rem",
                border: "1px solid #2a2d33",
                borderRadius: 8,
              }}
            >
              <p style={{ margin: "0 0 0.5rem" }}>
                Authority: <code>{data.scientific_execution_authority}</code>
              </p>
              <p style={{ margin: "0 0 0.5rem" }}>
                Invariant: <Badge state={data.invariant} /> · Vercel runtime:{" "}
                <code>{String(data.vercel_runtime)}</code>
              </p>
              <p style={{ margin: 0, opacity: 0.85, fontSize: "0.9rem" }}>{data.note}</p>
            </section>

            <section style={{ marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.1rem" }}>Preserved Studio receipts</h2>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                <thead>
                  <tr style={{ textAlign: "left", borderBottom: "1px solid #2a2d33" }}>
                    <th style={{ padding: "0.5rem" }}>Provider</th>
                    <th style={{ padding: "0.5rem" }}>Lane</th>
                    <th style={{ padding: "0.5rem" }}>Live status</th>
                    <th style={{ padding: "0.5rem" }}>Error</th>
                    <th style={{ padding: "0.5rem" }}>Receipt</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.preserved_studio_receipts).map(([name, row]) => (
                    <tr key={name} style={{ borderBottom: "1px solid #1c1f24" }}>
                      <td style={{ padding: "0.55rem" }}>{name}</td>
                      <td style={{ padding: "0.55rem" }}>{row.lane}</td>
                      <td style={{ padding: "0.55rem" }}>
                        <Badge state={row.live_status} />
                      </td>
                      <td style={{ padding: "0.55rem" }}>
                        {row.error_code ? <code>{row.error_code}</code> : "—"}
                      </td>
                      <td style={{ padding: "0.55rem", fontSize: "0.75rem", opacity: 0.8 }}>
                        {row.receipt_present ? row.receipt_path : "MISSING"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <ul style={{ fontSize: "0.85rem", opacity: 0.85 }}>
                {Object.entries(data.preserved_invariants).map(([k, v]) => (
                  <li key={k}>
                    <strong>{k}</strong>: {v}
                  </li>
                ))}
              </ul>
            </section>

            <section>
              <h2 style={{ fontSize: "1.1rem" }}>Vercel runtime config</h2>
              <p style={{ fontSize: "0.85rem", opacity: 0.8 }}>
                Panel state reflects this deployment only. CONFIGURED means a key or public endpoint is present.
              </p>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                <thead>
                  <tr style={{ textAlign: "left", borderBottom: "1px solid #2a2d33" }}>
                    <th style={{ padding: "0.5rem" }}>Provider</th>
                    <th style={{ padding: "0.5rem" }}>Panel</th>
                    <th style={{ padding: "0.5rem" }}>Secret</th>
                    <th style={{ padding: "0.5rem" }}>Hosted</th>
                    <th style={{ padding: "0.5rem" }}>Note</th>
                  </tr>
                </thead>
                <tbody>
                  {data.providers.map((p) => (
                    <tr key={p.provider} style={{ borderBottom: "1px solid #1c1f24", verticalAlign: "top" }}>
                      <td style={{ padding: "0.55rem" }}>
                        {p.provider}
                        <div style={{ fontSize: "0.75rem", opacity: 0.65 }}>{p.lane}</div>
                      </td>
                      <td style={{ padding: "0.55rem" }}>
                        <Badge state={p.panel_state} />
                      </td>
                      <td style={{ padding: "0.55rem" }}>{p.secret_state}</td>
                      <td style={{ padding: "0.55rem" }}>{p.hosted_on_vercel ? "yes" : "no"}</td>
                      <td style={{ padding: "0.55rem", fontSize: "0.8rem", opacity: 0.85 }}>{p.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          </>
        )}
      </div>
    </main>
  );
}
