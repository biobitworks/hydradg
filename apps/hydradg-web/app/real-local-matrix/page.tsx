import Link from "next/link";
import preview from "@/lib/real-local-matrix-preview.json";

const K_LEVELS = [
  ["K=5", "k5"],
  ["K=10 · co-primary", "k10"],
  ["K=100", "k100"],
] as const;

const runningBadge = {
  display: "inline-block",
  padding: "0.2rem 0.55rem",
  borderRadius: "999px",
  background: "#fff7ed",
  border: "1px solid #fdba74",
  color: "#9a3412",
  fontWeight: 700,
  fontSize: "0.72rem",
  letterSpacing: "0.04em",
} as const;

export default function RealLocalMatrixPage() {
  return (
    <main style={{ maxWidth: "1240px", margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#b45309", fontWeight: 800, fontSize: "0.8rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Preview staging · {preview.execution_host} · live experiment
        </p>
        <h1 style={{ fontSize: "2.5rem", margin: "0.5rem 0", color: "#0f172a" }}>Real Local Model × Dataset × K Matrix</h1>
        <p style={{ color: "#475569", lineHeight: 1.7, maxWidth: "900px", fontSize: "1.08rem" }}>
          HydraDG is executing the expanded experiment on <code>{preview.execution_host}</code>. The preview intentionally shows no
          provisional numerical scores. Every model/dataset/depth result remains <strong>CURRENTLY_RUNNING</strong> until a
          stable execution receipt, frozen model output, deterministic K replay, and statistical receipt exist.
        </p>
        <div style={{ background: "#fffbeb", border: "1px solid #f59e0b", padding: "1rem", borderRadius: "10px", marginTop: "1rem" }}>
          <strong>Claim boundary:</strong> the historical LongMemEval full500 K=5 ablation remains valid historical evidence,
          but it is not the headline for this expanded experiment. The final headline will be derived from the real multi-model
          matrix after completion, including positive, null, negative, failed, timeout, and abstaining cells.
        </div>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginTop: "1.25rem" }}>
          <Link href="/judge" style={{ padding: "0.6rem 1rem", background: "#0f172a", color: "white", borderRadius: "7px", textDecoration: "none", fontWeight: 700 }}>Judge golden path</Link>
          <Link href="/eligibility" style={{ padding: "0.6rem 1rem", background: "#e2e8f0", color: "#0f172a", borderRadius: "7px", textDecoration: "none", fontWeight: 700 }}>Eligibility / synthesis</Link>
          <Link href="/track03" style={{ padding: "0.6rem 1rem", background: "#e2e8f0", color: "#0f172a", borderRadius: "7px", textDecoration: "none", fontWeight: 700 }}>Historical Track 03 baseline</Link>
        </div>
      </header>

      <section style={{ marginBottom: "2.75rem" }}>
        <h2 style={{ fontSize: "1.5rem", color: "#0f172a" }}>Execution contract</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.8rem" }}>
          <article style={{ border: "1px solid #e2e8f0", borderRadius: "9px", padding: "1rem" }}><strong>{preview.models.length} Ollama text lanes</strong><p style={{ color: "#64748b" }}>Frozen local inventory expected; authoritative inventory comes from the run receipt.</p></article>
          <article style={{ border: "1px solid #e2e8f0", borderRadius: "9px", padding: "1rem" }}><strong>{preview.datasets.length} primary datasets</strong><p style={{ color: "#64748b" }}>EnterpriseRAG-Bench, HydraBlast-Real-Deps, LongMemEval-S-full500.</p></article>
          <article style={{ border: "1px solid #e2e8f0", borderRadius: "9px", padding: "1rem" }}><strong>K=5 / 10 / 100</strong><p style={{ color: "#64748b" }}>One frozen model extraction, then deterministic retrieval-depth replay.</p></article>
          <article style={{ border: "1px solid #e2e8f0", borderRadius: "9px", padding: "1rem" }}><strong>Vithia lane</strong><p style={{ color: "#64748b" }}>Separate Pythia-14m reference-basin / perturbation family; not conflated with Ollama retrieval.</p></article>
        </div>
      </section>

      {preview.datasets.map((dataset) => {
        const rows = preview.cells.filter((cell) => cell.dataset === dataset.name);
        return (
          <section key={dataset.name} style={{ marginBottom: "3rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "baseline", flexWrap: "wrap" }}>
              <div>
                <p style={{ color: "#b45309", fontWeight: 800, marginBottom: "0.25rem" }}>{dataset.track}</p>
                <h2 style={{ margin: 0, color: "#0f172a" }}>{dataset.name}</h2>
                <p style={{ color: "#64748b" }}>{dataset.scope}</p>
              </div>
              <span style={runningBadge}>DATASET FAMILY · CURRENTLY RUNNING</span>
            </div>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.84rem" }}>
                <thead>
                  <tr style={{ background: "#f8fafc", borderBottom: "2px solid #cbd5e1" }}>
                    <th style={{ textAlign: "left", padding: "0.7rem" }}>Model</th>
                    <th style={{ textAlign: "left", padding: "0.7rem" }}>Extraction</th>
                    {K_LEVELS.map(([label]) => <th key={label} style={{ textAlign: "left", padding: "0.7rem" }}>{label}</th>)}
                    <th style={{ textAlign: "left", padding: "0.7rem" }}>Receipt</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.model} style={{ borderBottom: "1px solid #e2e8f0" }}>
                      <td style={{ padding: "0.7rem", fontFamily: "monospace", fontWeight: 700 }}>{row.model}</td>
                      <td style={{ padding: "0.7rem" }}><span style={runningBadge}>{row.extraction_state}</span></td>
                      {K_LEVELS.map(([label, key]) => <td key={label} style={{ padding: "0.7rem" }}><span style={runningBadge}>{row[key]}</span></td>)}
                      <td style={{ padding: "0.7rem", color: "#64748b" }}>{row.receipt}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        );
      })}

      <section style={{ marginBottom: "3rem", border: "1px solid #cbd5e1", borderRadius: "10px", padding: "1.25rem" }}>
        <p style={{ color: "#b45309", fontWeight: 800, margin: 0 }}>VITHIA · SEPARATE EXPERIMENTAL FAMILY</p>
        <h2 style={{ color: "#0f172a" }}>Pythia-14m reference basin and perturbation ablation</h2>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <tbody>
            <tr style={{ borderBottom: "1px solid #e2e8f0" }}><td style={{ padding: "0.7rem", fontWeight: 700 }}>Historical repaired reference basin</td><td style={{ padding: "0.7rem" }}>{preview.vithia.historical_reference_basin}</td></tr>
            <tr style={{ borderBottom: "1px solid #e2e8f0" }}><td style={{ padding: "0.7rem", fontWeight: 700 }}>Seed / atom perturbation run</td><td style={{ padding: "0.7rem" }}><span style={runningBadge}>{preview.vithia.seed_atom_perturbation}</span></td></tr>
            <tr style={{ borderBottom: "1px solid #e2e8f0" }}><td style={{ padding: "0.7rem", fontWeight: 700 }}>First-divergence analysis</td><td style={{ padding: "0.7rem" }}><span style={runningBadge}>{preview.vithia.first_divergence_analysis}</span></td></tr>
            <tr><td style={{ padding: "0.7rem", fontWeight: 700 }}>Final Vithia claim ceiling</td><td style={{ padding: "0.7rem" }}>{preview.vithia.final_claim_ceiling}</td></tr>
          </tbody>
        </table>
      </section>

      <section style={{ marginBottom: "3rem", background: "#f8fafc", borderRadius: "10px", padding: "1.25rem" }}>
        <p style={{ fontWeight: 800, color: "#475569", margin: 0 }}>{preview.historical_baseline.label} · RETAINED</p>
        <h2 style={{ color: "#0f172a" }}>The first full500 graph ablation is baseline evidence, not the final program headline.</h2>
        <p style={{ color: "#475569", lineHeight: 1.6 }}>{preview.historical_baseline.claim} That result remains intact and will be compared against the expanded real-model matrix after the running experiment completes.</p>
      </section>

      <footer style={{ borderTop: "1px solid #e2e8f0", paddingTop: "1rem", color: "#64748b", lineHeight: 1.6 }}>
        Preview status only. Numerical cells are intentionally withheld until execution receipts exist. Authoritative result source:
        <code>{preview.authoritative_result_source}</code>. Signature state remains NOT_SIGNED and Merkle/MMR state remains
        NOT_MERKLE_COMMITTED unless a later authorized operation establishes otherwise.
      </footer>
    </main>
  );
}