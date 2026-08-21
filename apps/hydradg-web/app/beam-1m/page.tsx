import Link from "next/link";

export default function Beam1mPage() {
  const routes = [
    { id: "Route A", name: "Dense Content Only", hydradgMeasured: "QUEUED", status: "PREPARED" },
    { id: "Route B", name: "Dense + BM25 Hybrid", hydradgMeasured: "QUEUED", status: "PREPARED" },
    { id: "Route C", name: "Route B + Sliding-Window Latent Context", hydradgMeasured: "QUEUED", status: "PREPARED" },
    { id: "Route D", name: "Route C + Adaptive Query Expansion", hydradgMeasured: "QUEUED", status: "PREPARED" },
    { id: "Route E", name: "Route D + FCG Bounded Graph Traversal", hydradgMeasured: "QUEUED", status: "PREPARED" },
    { id: "Route F", name: "Route E + Valid-Time / Supersession Filter", hydradgMeasured: "QUEUED", status: "PREPARED" },
    { id: "Route G", name: "Route F + Reranking / Fusion", hydradgMeasured: "QUEUED", status: "PREPARED" },
    { id: "Route H", name: "Route G + Full FCO/FCG Custody & Claim-State", hydradgMeasured: "QUEUED", status: "PREPARED" },
  ];

  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#d97706", fontWeight: 800, fontSize: "0.78rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Preregistered future experiment · no HydraDG BEAM score yet
        </p>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", margin: "0.5rem 0", lineHeight: 1.02 }}>
          BEAM 1M Hybrid Architecture Ablation
        </h1>
        <p style={{ maxWidth: "850px", lineHeight: 1.7 }}>
          HydraDG has frozen the BEAM 1M preprocessing scope at 35 conversations and 700 probes and prepared Routes A–H. Generative inference and HydraDG numerical scoring have not started. Every route remains QUEUED until real execution receipts exist.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginTop: "1.25rem" }}>
          <Link href="/judge#golden-path" style={{ padding: "0.65rem 1rem", border: "1px solid #d4af37", borderRadius: "999px", textDecoration: "none", color: "#d4af37", fontWeight: 800 }}>
            ← Golden judge path
          </Link>
          <Link href="/real-local-matrix" style={{ padding: "0.65rem 1rem", border: "1px solid currentColor", borderRadius: "999px", textDecoration: "none" }}>
            Expanded evidence state
          </Link>
        </div>
      </header>

      <section style={{ marginBottom: "2rem", padding: "1.25rem", border: "1px solid rgba(127,127,127,0.35)", borderRadius: "8px" }}>
        <h2 style={{ marginTop: 0 }}>Published HydraDB reference</h2>
        <p style={{ marginBottom: "0.5rem", lineHeight: 1.6 }}>
          HydraDB reports <strong>82% overall on BEAM 1M</strong>, compared with <strong>74% for Hindsight</strong>. This is an external benchmark reference, not a HydraDG measurement and not a route-by-route ablation result.
        </p>
        <p style={{ marginBottom: 0, opacity: 0.8 }}>
          HydraDG will compare its own measured Routes A–H only after the preregistered execution produces receipts.
        </p>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2>Architecture routes</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid currentColor", textAlign: "left" }}>
                <th style={{ padding: "0.8rem" }}>Route</th>
                <th style={{ padding: "0.8rem" }}>Architecture</th>
                <th style={{ padding: "0.8rem" }}>HydraDG measured result</th>
                <th style={{ padding: "0.8rem" }}>State</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((route) => (
                <tr key={route.id} style={{ borderBottom: "1px solid rgba(127,127,127,0.25)" }}>
                  <td style={{ padding: "0.8rem", fontWeight: 800 }}>{route.id}</td>
                  <td style={{ padding: "0.8rem" }}>{route.name}</td>
                  <td style={{ padding: "0.8rem", color: "#d97706", fontWeight: 800 }}>{route.hydradgMeasured}</td>
                  <td style={{ padding: "0.8rem" }}>{route.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={{ padding: "1.25rem", border: "1px solid rgba(212,175,55,0.5)", borderRadius: "8px" }}>
        <p style={{ color: "#d4af37", fontWeight: 800, fontSize: "0.78rem", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 0 }}>
          Future preregistered hypothesis
        </p>
        <h2>Can explicit custody improve difficult memory updates?</h2>
        <p style={{ lineHeight: 1.7, marginBottom: 0 }}>
          Future work will test whether explicit FCO supersession, validity, provenance and claim-state edges improve BEAM knowledge-update and contradiction-resolution performance without degrading HydraDB-style temporal reasoning, event ordering or multi-session performance. This hypothesis is future work and is not part of the current submission evidence.
        </p>
      </section>
    </main>
  );
}
