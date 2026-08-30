import Link from "next/link";

import GoldenPathStep from "@/components/GoldenPathStep";

export default function Beam1mPage() {
  const routes = [
    { id: "Route A", name: "Dense Content Only", state: "PREPARED_UNEXECUTED" },
    { id: "Route B", name: "Dense + BM25 Hybrid", state: "PREPARED_UNEXECUTED" },
    { id: "Route C", name: "Route B + Sliding-Window Latent Context", state: "PREPARED_UNEXECUTED" },
    { id: "Route D", name: "Route C + Adaptive Query Expansion", state: "PREPARED_UNEXECUTED" },
    { id: "Route E", name: "Route D + FCG Bounded Graph Traversal", state: "PREPARED_UNEXECUTED" },
    { id: "Route F", name: "Route E + Valid-Time / Supersession Filter", state: "PREPARED_UNEXECUTED" },
    { id: "Route G", name: "Route F + Reranking / Evidence Fusion", state: "PREPARED_UNEXECUTED" },
    { id: "Route H", name: "Route G + Full FCO/FCG Custody & Claim-State", state: "PREPARED_UNEXECUTED" },
  ];

  const futureMetrics = [
    "ErrorPropagationRate",
    "RecoveryRate",
    "FirstDivergenceAccuracy",
    "CurrentStateAccuracy",
    "HistoricalStateRetention",
    "CompleteEvidencePathRecovery",
    "SerializedByteReduction",
    "ContextTokenReduction",
    "AvoidedDownstreamInferenceCalls",
    "UsefulComputeRatio",
    "CostPerCorrectGovernedAnswer",
  ];

  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem" }}>
      <GoldenPathStep
        step={7}
        summary="Show the preregistered next experiment without presenting it as completed evidence: BEAM 1M hybrid retrieval, multi-session reasoning, multi-agent perturbation lineage, and measured economics."
      />

      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.78rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Step 07 of 08 · Future Work · PREPARED_UNEXECUTED
        </p>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", margin: "0.5rem 0", lineHeight: 1.02 }}>
          BEAM 1M + Multi-Agent Custody
        </h1>
        <p style={{ maxWidth: "880px", lineHeight: 1.7 }}>
          The public BEAM 1M target scope is 35 conversations and 700 probes. HydraDG has prepared the A–H architecture contract, but official rows have not yet been materialized, revision-pinned, or row-hashed in this repository. No HydraDG BEAM score is claimed.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginTop: "1.25rem" }}>
          <Link href="/eligibility" style={{ padding: "0.65rem 1rem", border: "1px solid #d4af37", borderRadius: "999px", background: "#d4af37", color: "#17130a", textDecoration: "none", fontWeight: 900 }}>
            Next · 08 Claim Boundary →
          </Link>
          <Link href="/evidence" style={{ padding: "0.65rem 1rem", border: "1px solid rgba(212,175,55,.55)", borderRadius: "999px", textDecoration: "none", color: "#d4af37", fontWeight: 800 }}>
            ← 06 Evidence
          </Link>
        </div>
      </header>

      <section style={{ marginBottom: "2rem", padding: "1.25rem", border: "1px solid rgba(127,127,127,0.35)", borderRadius: "8px" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 0 }}>07A / External reference</p>
        <h2 style={{ marginTop: 0 }}>Published HydraDB BEAM reference</h2>
        <p style={{ marginBottom: 0, lineHeight: 1.6 }}>
          HydraDB reports <strong>82% overall on BEAM 1M</strong>, compared with <strong>74% for Hindsight</strong>. These are external benchmark references, not HydraDG measurements and not Route A–H scores.
        </p>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>07B / Architecture ablation</p>
        <h2>Routes A → H</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
            <thead><tr style={{ borderBottom: "1px solid currentColor", textAlign: "left" }}><th style={{ padding: "0.8rem" }}>Route</th><th style={{ padding: "0.8rem" }}>Architecture</th><th style={{ padding: "0.8rem" }}>HydraDG state</th></tr></thead>
            <tbody>{routes.map((route) => <tr key={route.id} style={{ borderBottom: "1px solid rgba(127,127,127,0.25)" }}><td style={{ padding: "0.8rem", fontWeight: 800 }}>{route.id}</td><td style={{ padding: "0.8rem" }}>{route.name}</td><td style={{ padding: "0.8rem", color: "#d97706", fontWeight: 800 }}>{route.state}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section style={{ marginBottom: "2rem", padding: "1.25rem", border: "1px solid rgba(212,175,55,0.5)", borderRadius: "8px" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 0 }}>07C / Multi-agent perturbation hypothesis</p>
        <h2>Preserve where the error entered — and what inherited it.</h2>
        <p style={{ lineHeight: 1.7 }}>
          Future work will represent retrieval, extraction, reasoning, decision, and answer agents as FCG participants. Wrong decisions remain perturbation evidence, allowing HydraDG to measure first divergence, downstream inheritance, and recovery rather than deleting the bad state.
        </p>
        <p style={{ lineHeight: 1.7, marginBottom: 0 }}>
          Primary hypothesis: explicit FCO supersession, validity, provenance, claim-state, and agent-decision lineage can improve knowledge-update, contradiction-resolution, and multi-session reasoning without degrading HydraDB-style temporal reasoning and event ordering.
        </p>
      </section>

      <section style={{ padding: "1.25rem", border: "1px solid rgba(127,127,127,0.35)", borderRadius: "8px" }}>
        <p style={{ color: "#d4af37", fontWeight: 900, fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 0 }}>07D / Economics to measure</p>
        <h2 style={{ marginTop: 0 }}>Accuracy and cost stay separate until measured.</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>{futureMetrics.map((metric) => <span key={metric} style={{ border: "1px solid rgba(127,127,127,0.35)", borderRadius: "999px", padding: "0.35rem 0.6rem", fontSize: "0.82rem" }}>{metric}</span>)}</div>
        <p style={{ lineHeight: 1.7, marginBottom: 0, marginTop: "1rem" }}>
          Anticube classification is preregistered as a governance/classification signal, not an assumed ranking boost. Storage savings, token savings, avoided model calls, and cost-per-correct-governed-answer remain <strong>NOT MEASURED</strong> until bytes, context tokens, and inference calls are counted.
        </p>
        <div style={{ marginTop: "1.25rem" }}><Link href="/eligibility" style={{ display: "inline-flex", padding: "0.7rem 1.05rem", borderRadius: "999px", background: "#d4af37", color: "#17130a", textDecoration: "none", fontWeight: 900 }}>Finish Golden Path · 08 Claim Boundary →</Link></div>
      </section>
    </main>
  );
}
