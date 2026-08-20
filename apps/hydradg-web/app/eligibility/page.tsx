import Link from "next/link";
import {
  eligibilityClaimCeiling,
  eligibilityProofDoc,
  hackHydraEligibility,
} from "@/lib/eligibility";

const GOVERNED_CHAIN = [
  ["1. Atom of Knowledge", "RAW CONTEXT UNIT", "Basic textual or structural context fragment prior to governance classification.", "RAW_INPUT"],
  ["2. Seed of Truth", "BOUNDED PROVENANCE ANCHOR", "Content-addressed initial factual reference bundle for deterministic lineage.", "ANCHORED"],
  ["3. First-Class Object (FCO)", "GOVERNED CUSTODY OBJECT", "Canonical content identity with immutable SHA-256 hash and rich provenance.", "IDENTITY_REUSE_65.73%"],
  ["4. First-Class Graph (FCG)", "TYPED DEPENDENCY GRAPH", "Explicit directed relationships (PRECEDES, DERIVED_FROM, CONTRADICTS) among FCOs.", "1,692_EDGES"],
  ["5. Hyper-FCG / Time Layer", "TIME-INDEXED GRAPH VIEW", "Versioned temporal snapshots tracking Context Drift (JSD), Hnorm, and G* movement over time.", "ESTABLISHED_MATH"],
  ["6. CFMO / MMR", "PLANNED SCALABLE PROOF", "Context-Free Model Optimization & Merkle Mountain Range commitment structures.", "PLANNED / NOT_ESTABLISHED"],
  ["7. HydraDB BYOG Projection", "OPERATIONAL QUERY LAYER", "Canonical FCG graph_payload projected into hosted HydraDB database `hydradg` collection `hydradg-judge-demo`.", "1,692/1,692_BYOG_PARITY"],
  ["8. K=5 / K=10 / K=100 Matrix", "RETRIEVAL DEPTH EXPERIMENTS", "Cross-track retrieval ablation testing whether model extractors improve performance over heuristic control.", "EXECUTED_R1_R2_R3_PASS"],
  ["9. Final Claim Ceiling", "STRICT NULL-PRESERVING CEILING", "All 9 Holm-Bonferroni co-primary tests retained null (p > 0.05); graph depth helps, model extractions do not.", "NO_MODEL_BENEFIT_OBSERVED"],
] as const;

const DAISY_MATRIX = [
  ["Track 01 · Enterprise RAG", "EnterpriseRAG-Bench (N=300)", "Heuristic (0.865) vs Models (0.858–0.863)", "0 / 3 Sig", "TRACK01_NO_GRAPH_ADVANTAGE_OBSERVED"],
  ["Track 02 · Dependency Graph", "HydraBlast-Real-Deps (N=250)", "Heuristic (0.932) vs Models (0.926–0.931)", "0 / 3 Sig", "TRACK02_REAL_DEPENDENCY_BENCHMARK_EXECUTED"],
  ["Track 03 · Context Memory", "LongMemEval-S (N=470)", "Heuristic (0.941) vs Models (0.931–0.938)", "0 / 3 Sig", "TRACK03_DEPTH_EFFECT_REPLICATED"],
] as const;

const K_DEPTH_ABLATION = [
  ["K=5", "0.942 (Control)", "0.938 (Qwen)", "0.936 (Qwen-Coder)", "0.940 (DeepSeek-R1)", "Baseline depth"],
  ["K=10 (Co-Primary)", "0.978 (Control)", "0.974 (Qwen)", "0.972 (Qwen-Coder)", "0.976 (DeepSeek-R1)", "+0.036 depth gain"],
  ["K=100 (Saturation)", "0.982 (Control)", "0.978 (Qwen)", "0.975 (Qwen-Coder)", "0.980 (DeepSeek-R1)", "+0.004 gain / 0.042 dilution"],
] as const;

const SUPERSEDED_PANEL = [
  ["20.82M Cloud Node Writeback", "SUPERSEDED_HISTORICAL_FAILURE_EVIDENCE", "The 20.8M count represents local spatiotemporal occurrences from Parquet dictionaries, not individually streamed cloud objects.", "RECLASSIFIED"],
  ["HTTP 400 Batch Upload Path", "HISTORICAL_FAILURE_EVIDENCE", "HTTP 400 response path is preserved intact for historical audit verification.", "RETAINED_FAILURE"],
  ["Vercel Production Deploy", "HELD LOCAL / NOT DEPLOYED", "Target branch `hack-hydra/final-hosted-fcg-20260820` is held 100% local for human review.", "NOT_DEPLOYED"],
] as const;

export default function EligibilityPage() {
  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#d97706", fontWeight: "bold", fontSize: "0.875rem", letterSpacing: "0.05em", textTransform: "uppercase" }}>
          Golden Path · Final Step · Governed Context Synthesis
        </p>
        <h1 style={{ fontSize: "2.25rem", fontWeight: "800", color: "#0f172a", marginTop: "0.5rem" }}>
          HydraDG Pre-Production Synthesis: Governed Chain & Matrix Evidence
        </h1>
        <p style={{ color: "#475569", fontSize: "1.125rem", maxWidth: "800px", lineHeight: "1.6" }}>
          “FCO/FCG reduces repeated identity; HydraDB makes the resulting governed graph operational;
          Context Drift measures how the information state moves through time; retrieval experiments determine
          whether those paths actually help models.”
        </p>
        <p style={{ color: "#334155", fontSize: "1rem", maxWidth: "800px", lineHeight: "1.6", background: "#f8fafc", padding: "1rem", borderRadius: "8px", borderLeft: "4px solid #0284c7" }}>
          “HydraDG demonstrates a governed context graph where 31.67M contextual occurrences collapse to
          10.85M canonical identities with 65.73% identity reuse, while provenance and temporal relationships
          remain explicit. The canonical FCG is projected into HydraDB through BYOG with exact 1,692-edge hosted parity.
          K=5/10/100 experiments then test how much graph context different models actually need, rather than assuming
          bigger context or bigger models are better.”
        </p>
        <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
          <Link href="/best-use" style={{ background: "#0284c7", color: "#fff", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            Why HydraDB + Math
          </Link>
          <Link href="/atom-heatmap" style={{ background: "#e2e8f0", color: "#0f172a", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            Atom Heat Map
          </Link>
        </div>
      </header>

      {/* 1. Governed Chain */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          1. The Governed Context Chain (Atom → Seed → FCO → FCG → HydraDB → Null Ceiling)
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
          {GOVERNED_CHAIN.map(([step, tag, desc, badge], i) => (
            <div key={i} style={{ background: "#fff", border: "1px solid #e2e8f0", padding: "1rem", borderRadius: "8px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: "bold", color: "#64748b" }}>{tag}</span>
                <span style={{ fontSize: "0.75rem", background: "#f1f5f9", padding: "0.125rem 0.5rem", borderRadius: "4px", fontWeight: "600" }}>{badge}</span>
              </div>
              <h3 style={{ fontSize: "1.125rem", fontWeight: "700", marginTop: "0.5rem", color: "#0f172a" }}>{step}</h3>
              <p style={{ fontSize: "0.875rem", color: "#475569", marginTop: "0.25rem" }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 2. Cross-Track Daisy Matrix */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          2. Daisy Train — Cross-Track Model × Dataset × K Matrix (9 Co-Primary Tests)
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", textAlign: "left", fontSize: "0.875rem" }}>
          <thead>
            <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
              <th style={{ padding: "0.75rem" }}>Track & Name</th>
              <th style={{ padding: "0.75rem" }}>Benchmark Dataset</th>
              <th style={{ padding: "0.75rem" }}>Primary K=10 Score Range</th>
              <th style={{ padding: "0.75rem" }}>Holm-Bonferroni Sig</th>
              <th style={{ padding: "0.75rem" }}>Track Claim Ceiling</th>
            </tr>
          </thead>
          <tbody>
            {DAISY_MATRIX.map(([t, d, s, sig, c], i) => (
              <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.75rem", fontWeight: "600" }}>{t}</td>
                <td style={{ padding: "0.75rem" }}>{d}</td>
                <td style={{ padding: "0.75rem" }}>{s}</td>
                <td style={{ padding: "0.75rem", color: "#dc2626", fontWeight: "bold" }}>{sig}</td>
                <td style={{ padding: "0.75rem", fontFamily: "monospace", fontSize: "0.75rem" }}>{c}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* 3. Retrieval Depth Ablation */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          3. Retrieval Depth Ablation (K=5 → K=10 → K=100 Saturation & Dilution)
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", textAlign: "left", fontSize: "0.875rem" }}>
          <thead>
            <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
              <th style={{ padding: "0.75rem" }}>Depth K</th>
              <th style={{ padding: "0.75rem" }}>Control (Heuristic)</th>
              <th style={{ padding: "0.75rem" }}>Qwen 2.5 7B</th>
              <th style={{ padding: "0.75rem" }}>Qwen2.5-Coder 7B</th>
              <th style={{ padding: "0.75rem" }}>DeepSeek-R1 14B</th>
              <th style={{ padding: "0.75rem" }}>Depth Analysis</th>
            </tr>
          </thead>
          <tbody>
            {K_DEPTH_ABLATION.map(([k, ctrl, qw, qwc, ds, notes], i) => (
              <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.75rem", fontWeight: "bold" }}>{k}</td>
                <td style={{ padding: "0.75rem" }}>{ctrl}</td>
                <td style={{ padding: "0.75rem" }}>{qw}</td>
                <td style={{ padding: "0.75rem" }}>{qwc}</td>
                <td style={{ padding: "0.75rem" }}>{ds}</td>
                <td style={{ padding: "0.75rem", color: "#475569" }}>{notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* 4. Superseded Historical Panel */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#991b1b", borderBottom: "2px solid #fecaca", paddingBottom: "0.5rem" }}>
          4. Historical Audit & Superseded Claim Reclassification
        </h2>
        <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>
          {SUPERSEDED_PANEL.map(([claim, status, reason, badge], i) => (
            <div key={i} style={{ background: "#fef2f2", border: "1px solid #fca5a5", padding: "1rem", borderRadius: "8px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.875rem", fontWeight: "bold", color: "#991b1b" }}>{claim}</span>
                <span style={{ fontSize: "0.75rem", background: "#fee2e2", color: "#991b1b", padding: "0.125rem 0.5rem", borderRadius: "4px", fontWeight: "600" }}>{badge}</span>
              </div>
              <p style={{ fontSize: "0.875rem", color: "#7f1d1d", marginTop: "0.25rem" }}>{reason}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
