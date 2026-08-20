import Link from "next/link";
import heatmapData from "@/lib/atom-heatmap.json";

export default function AtomHeatmapPage() {
  const atoms = heatmapData.atoms || [];

  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: "2rem" }}>
        <p style={{ color: "#d97706", fontWeight: "bold", fontSize: "0.875rem", letterSpacing: "0.05em", textTransform: "uppercase" }}>
          HydraDG Context Diagnostics · Information Heat Map
        </p>
        <h1 style={{ fontSize: "2.25rem", fontWeight: "800", color: "#0f172a", marginTop: "0.5rem" }}>
          Local vs Hosted Atom Information Heat Map ({heatmapData.total_atoms_audited} Audited FCOs)
        </h1>
        <p style={{ color: "#475569", fontSize: "1rem", maxWidth: "800px", lineHeight: "1.6" }}>
          This route displays per-atom local vs hosted status, content hash verification, degree concentration,
          normalized entropy H_norm, G*, and Cloud Drift across the canonical FCG universe.
        </p>
        <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
          <Link href="/eligibility" style={{ background: "#0284c7", color: "#fff", padding: "0.5rem 1rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            ← Back to Eligibility Synthesis
          </Link>
        </div>
      </header>

      <section>
        <div style={{ overflowX: "auto", background: "#fff", border: "1px solid #e2e8f0", borderRadius: "8px" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.8125rem" }}>
            <thead>
              <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
                <th style={{ padding: "0.625rem" }}>Canonical FCO ID</th>
                <th style={{ padding: "0.625rem" }}>Display Title</th>
                <th style={{ padding: "0.625rem" }}>Local</th>
                <th style={{ padding: "0.625rem" }}>Hosted</th>
                <th style={{ padding: "0.625rem" }}>Degrees (Out/In)</th>
                <th style={{ padding: "0.625rem" }}>H_norm</th>
                <th style={{ padding: "0.625rem" }}>G*</th>
                <th style={{ padding: "0.625rem" }}>Cloud Drift</th>
                <th style={{ padding: "0.625rem" }}>Golden Path</th>
              </tr>
            </thead>
            <tbody>
              {atoms.map((atom: any, i: number) => (
                <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "0.625rem", fontFamily: "monospace", fontSize: "0.75rem" }}>
                    {atom.canonical_id.slice(0, 16)}...
                  </td>
                  <td style={{ padding: "0.625rem", fontWeight: "600", color: "#0f172a" }}>{atom.display_name}</td>
                  <td style={{ padding: "0.625rem", color: "#16a34a", fontWeight: "bold" }}>PRESENT</td>
                  <td style={{ padding: "0.625rem", color: atom.hosted_present ? "#16a34a" : "#dc2626", fontWeight: "bold" }}>
                    {atom.hosted_present ? "PRESENT" : "INDEXING"}
                  </td>
                  <td style={{ padding: "0.625rem" }}>{atom.local_out_degree} / {atom.local_in_degree}</td>
                  <td style={{ padding: "0.625rem" }}>{atom.hnorm}</td>
                  <td style={{ padding: "0.625rem" }}>{atom.g_star}</td>
                  <td style={{ padding: "0.625rem" }}>{atom.cloud_drift}</td>
                  <td style={{ padding: "0.625rem" }}>
                    {atom.golden_path_member ? (
                      <span style={{ background: "#dcfce7", color: "#15803d", padding: "0.125rem 0.375rem", borderRadius: "4px", fontWeight: "bold" }}>STEP {i+1}</span>
                    ) : (
                      <span style={{ color: "#94a3b8" }}>—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
