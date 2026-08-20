import Link from "next/link";

const GOVERNED_CHAIN = [
  ["1. Atom of Knowledge", "RAW CONTEXT UNIT", "Basic textual or structural context fragment prior to governance classification.", "RAW_INPUT"],
  ["2. Seed of Truth", "BOUNDED PROVENANCE ANCHOR", "Content-addressed initial factual reference bundle for deterministic lineage.", "ANCHORED"],
  ["3. First-Class Object (FCO)", "GOVERNED CUSTODY OBJECT", "Canonical content identity with SHA-256 identity and explicit provenance.", "IDENTITY_REUSE_65.73%"],
  ["4. First-Class Graph (FCG)", "TYPED DEPENDENCY GRAPH", "Explicit directed relationships among sources, transformations, evidence, claims and artifacts.", "CANONICAL_GRAPH"],
  ["5. Hyper-FCG / Time Layer", "TIME-INDEXED GRAPH VIEW", "Versioned temporal snapshots tracking changing context and diagnostic state through time.", "TIME_INDEXED"],
  ["6. CFMO / MMR", "PLANNED SCALABLE PROOF", "Context-Free Model Optimization and Merkle Mountain Range structures remain separately bounded.", "PLANNED / NOT_COMMITTED"],
  ["7. HydraDB BYOG Projection", "OPERATIONAL QUERY LAYER", "Canonical FCG projection into hosted HydraDB; canonical readback remains pending.", "UPLOAD_ACCEPTED_INDEXING_PENDING"],
  ["8. Real Local Model Matrix", "EXECUTING EMPIRICAL FAMILY", "Ten local Ollama text-model lanes × three primary datasets × K=5/10/100, plus a separate Vithia perturbation family.", "CURRENTLY_RUNNING"],
  ["9. Final Claim Ceiling", "RESULT-DEPENDENT", "The expanded claim ceiling will be computed from stable execution and statistical receipts; it is not preselected.", "PENDING_REAL_MATRIX_RESULTS"],
] as const;

const DATASET_STATUS = [
  ["Track 01 · Enterprise RAG", "EnterpriseRAG-Bench", "N=300", "CURRENTLY_RUNNING", "K=5 / K=10 / K=100"],
  ["Track 02 · Dependency Graph", "HydraBlast-Real-Deps", "N=250", "CURRENTLY_RUNNING", "K=5 / K=10 / K=100"],
  ["Track 03 · Context Memory", "LongMemEval-S-full500", "N=500 total", "CURRENTLY_RUNNING", "K=5 / K=10 / K=100"],
] as const;

const DEPTH_STATUS = [
  ["K=5", "CURRENTLY_RUNNING", "SECONDARY_DEPTH_ANALYSIS"],
  ["K=10", "CURRENTLY_RUNNING", "CO_PRIMARY_MODEL_VS_CONTROL_FAMILY"],
  ["K=100", "CURRENTLY_RUNNING", "SECONDARY_SATURATION_DILUTION_ANALYSIS"],
] as const;

const HISTORICAL = [
  ["LongMemEval full500 K=5 ablation", "HISTORICAL_EXECUTED_BASELINE", "Typed graph constructed and queried; B/C/D did not establish a positive Hit@5 advantage over the flat reference route at that tested configuration.", "RETAINED"],
  ["Earlier 3-model K=5/10/100 development matrix", "RECLASSIFY_PENDING_REAL_RECEIPTS", "The current expanded experiment must not inherit hard-coded or simulated values as primary empirical evidence.", "NOT_CURRENT_HEADLINE"],
  ["Hosted 653-FCO / 1,692-edge canonical parity", "PENDING_READBACK", "Upload accepted; indexing/readback and canonical identity parity remain unestablished.", "FAIL_CLOSED"],
] as const;

const running = {
  display: "inline-block",
  padding: "0.18rem 0.5rem",
  borderRadius: "999px",
  border: "1px solid #fdba74",
  background: "#fff7ed",
  color: "#9a3412",
  fontWeight: 800,
  fontSize: "0.72rem",
} as const;

export default function EligibilityPage() {
  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#b45309", fontWeight: "bold", fontSize: "0.875rem", letterSpacing: "0.05em", textTransform: "uppercase" }}>Golden Path · Preview Staging · Real Experiment Running</p>
        <h1 style={{ fontSize: "2.25rem", fontWeight: "800", color: "#0f172a", marginTop: "0.5rem" }}>HydraDG Pre-Production Synthesis</h1>
        <p style={{ color: "#475569", fontSize: "1.125rem", maxWidth: "900px", lineHeight: "1.65" }}>
          HydraDG is now executing the broader real local-model program on <code>magicstudiobox</code>. The preview is structured for the arriving receipts, but numerical treatment results are intentionally withheld until the corresponding model execution, frozen FCO/FCG projection, deterministic K replay, and statistics exist.
        </p>
        <p style={{ color: "#334155", fontSize: "1rem", maxWidth: "900px", lineHeight: "1.6", background: "#fffbeb", padding: "1rem", borderRadius: "8px", borderLeft: "4px solid #d97706" }}>
          Null preservation does not mean foregrounding the oldest null forever. The historical full500 K=5 ablation remains evidence; the expanded ten-model × three-dataset × K=5/10/100 experiment will determine the new headline from actual outcomes, including positive, null, negative, failed, timeout, and abstaining cells.
        </p>
        <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem", flexWrap: "wrap" }}>
          <Link href="/real-local-matrix" style={{ background: "#0f172a", color: "#fff", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "700" }}>Open Running Matrix</Link>
          <Link href="/best-use" style={{ background: "#e2e8f0", color: "#0f172a", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>Why HydraDB + Math</Link>
          <Link href="/atom-heatmap" style={{ background: "#e2e8f0", color: "#0f172a", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>Atom Heat Map</Link>
        </div>
      </header>

      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>1. Governed Context Chain</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
          {GOVERNED_CHAIN.map(([step, tag, desc, badge], i) => (
            <div key={i} style={{ background: "#fff", border: "1px solid #e2e8f0", padding: "1rem", borderRadius: "8px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem", alignItems: "center" }}><span style={{ fontSize: "0.72rem", fontWeight: "bold", color: "#64748b" }}>{tag}</span><span style={{ fontSize: "0.7rem", background: "#f1f5f9", padding: "0.125rem 0.5rem", borderRadius: "4px", fontWeight: "600" }}>{badge}</span></div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: "700", marginTop: "0.5rem", color: "#0f172a" }}>{step}</h3><p style={{ fontSize: "0.875rem", color: "#475569", marginTop: "0.25rem" }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>2. Primary Dataset Families</h2>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", textAlign: "left", fontSize: "0.875rem" }}>
          <thead><tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}><th style={{ padding: "0.75rem" }}>Track</th><th style={{ padding: "0.75rem" }}>Dataset</th><th style={{ padding: "0.75rem" }}>Frozen scope</th><th style={{ padding: "0.75rem" }}>Result state</th><th style={{ padding: "0.75rem" }}>Depths</th></tr></thead>
          <tbody>{DATASET_STATUS.map(([t, d, n, status, k], i) => <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}><td style={{ padding: "0.75rem", fontWeight: "600" }}>{t}</td><td style={{ padding: "0.75rem" }}>{d}</td><td style={{ padding: "0.75rem" }}>{n}</td><td style={{ padding: "0.75rem" }}><span style={running}>{status}</span></td><td style={{ padding: "0.75rem", fontFamily: "monospace" }}>{k}</td></tr>)}</tbody>
        </table>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>3. Retrieval Depth Results</h2>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", textAlign: "left", fontSize: "0.875rem" }}><thead><tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}><th style={{ padding: "0.75rem" }}>Depth</th><th style={{ padding: "0.75rem" }}>Current result</th><th style={{ padding: "0.75rem" }}>Statistical role</th></tr></thead><tbody>{DEPTH_STATUS.map(([k, status, role], i) => <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}><td style={{ padding: "0.75rem", fontWeight: "700" }}>{k}</td><td style={{ padding: "0.75rem" }}><span style={running}>{status}</span></td><td style={{ padding: "0.75rem", fontFamily: "monospace", fontSize: "0.78rem" }}>{role}</td></tr>)}</tbody></table>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>4. Model Families</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
          <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1rem" }}><p style={{ color: "#64748b", fontWeight: 700 }}>OLLAMA TEXT FAMILY</p><h3>10 local model lanes</h3><span style={running}>CURRENTLY RUNNING</span><p style={{ color: "#475569" }}>Authoritative model names, digests, failures and completed cells will be read from the frozen execution receipt.</p></div>
          <div style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1rem" }}><p style={{ color: "#64748b", fontWeight: 700 }}>VITHIA / PYTHIA-14M FAMILY</p><h3>Reference basin + perturbation ablation</h3><span style={running}>CURRENTLY RUNNING</span><p style={{ color: "#475569" }}>Kept statistically and semantically separate from the Ollama retrieval family.</p></div>
        </div>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#991b1b", borderBottom: "2px solid #fecaca", paddingBottom: "0.5rem" }}>5. Historical / Superseded Evidence</h2>
        <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>{HISTORICAL.map(([claim, status, reason, badge], i) => <div key={i} style={{ background: "#fef2f2", border: "1px solid #fca5a5", padding: "1rem", borderRadius: "8px" }}><div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem", alignItems: "center" }}><span style={{ fontSize: "0.875rem", fontWeight: "bold", color: "#991b1b" }}>{claim}</span><span style={{ fontSize: "0.7rem", background: "#fee2e2", color: "#991b1b", padding: "0.125rem 0.5rem", borderRadius: "4px", fontWeight: "600" }}>{badge}</span></div><p style={{ fontSize: "0.75rem", fontFamily: "monospace", color: "#7f1d1d" }}>{status}</p><p style={{ fontSize: "0.875rem", color: "#7f1d1d", marginTop: "0.25rem" }}>{reason}</p></div>)}</div>
      </section>
    </main>
  );
}