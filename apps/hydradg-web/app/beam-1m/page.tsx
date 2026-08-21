import Link from "next/link";
import beamPrereg from "@/lib/beam-preregistration.json";

export default function Beam1mPage() {
  const routes = [
    { id: "Route A", name: "Dense Content Only", hydradb_published: "0.742", hydradg_measured: "QUEUED", status: "PREPARED" },
    { id: "Route B", name: "Dense + BM25 Hybrid", hydradb_published: "0.785", hydradg_measured: "QUEUED", status: "PREPARED" },
    { id: "Route C", name: "Route B + Sliding-Window Latent Context", hydradb_published: "0.812", hydradg_measured: "QUEUED", status: "PREPARED" },
    { id: "Route D", name: "Route C + Adaptive Query Expansion", hydradb_published: "0.834", hydradg_measured: "QUEUED", status: "PREPARED" },
    { id: "Route E", name: "Route D + FCG Bounded Graph Traversal", hydradb_published: "0.856", hydradg_measured: "QUEUED", status: "PREPARED" },
    { id: "Route F", name: "Route E + Valid-Time / Supersession Filter", hydradb_published: "0.871", hydradg_measured: "QUEUED", status: "PREPARED" },
    { id: "Route G", name: "Route F + Reciprocal Rank Fusion", hydradb_published: "0.880", hydradg_measured: "QUEUED", status: "PREPARED" },
    { id: "Route H", name: "Route G + Full FCO/FCG Custody & Claim-State", hydradb_published: "0.884", hydradg_measured: "QUEUED", status: "PREPARED" },
  ];

  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#d97706", fontWeight: "bold", fontSize: "0.875rem", letterSpacing: "0.05em", textTransform: "uppercase" }}>
          Parallel Architecture Preprocessing · BEAM 1M Benchmark Tier
        </p>
        <h1 style={{ fontSize: "2.25rem", fontWeight: "800", color: "#0f172a", marginTop: "0.5rem" }}>
          BEAM 1M + HydraDB Hybrid Architecture Preprocessing (35 Conversations, 700 Probes)
        </h1>
        <p style={{ color: "#475569", fontSize: "1.125rem", maxWidth: "800px", lineHeight: "1.6" }}>
          “BEAM 1M evaluates multi-session contextual memory across 1,000,000 token conversations.
          HydraDG's parallel preprocessing lane acquires official dataset manifests, implements architecture routes A–H,
          and preregisters evaluation metrics without running generative inference while local model matrix tasks are active.”
        </p>
        <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
          <Link href="/eligibility" style={{ background: "#0284c7", color: "#fff", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            ← Back to Eligibility Synthesis
          </Link>
          <Link href="/real-matrix" style={{ background: "#e2e8f0", color: "#0f172a", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            Real Local Model Matrix
          </Link>
        </div>
      </header>

      {/* Architecture Routes Table */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          Architecture Ablation Routes (Route A → Route H)
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", textAlign: "left", fontSize: "0.875rem" }}>
          <thead>
            <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
              <th style={{ padding: "0.75rem" }}>Route ID</th>
              <th style={{ padding: "0.75rem" }}>Architecture Description</th>
              <th style={{ padding: "0.75rem" }}>Published HydraDB Reference Accuracy</th>
              <th style={{ padding: "0.75rem" }}>HydraDG Measured Accuracy</th>
              <th style={{ padding: "0.75rem" }}>Pipeline State</th>
            </tr>
          </thead>
          <tbody>
            {routes.map((r, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.75rem", fontWeight: "bold" }}>{r.id}</td>
                <td style={{ padding: "0.75rem" }}>{r.name}</td>
                <td style={{ padding: "0.75rem", fontFamily: "monospace", color: "#64748b" }}>{r.hydradb_published} (Reference)</td>
                <td style={{ padding: "0.75rem", color: "#d97706", fontWeight: "bold" }}>{r.hydradg_measured}</td>
                <td style={{ padding: "0.75rem", color: "#0284c7", fontWeight: "bold" }}>{r.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
