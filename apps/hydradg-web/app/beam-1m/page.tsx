import Link from "next/link";

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
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#d97706", fontWeight: 800, fontSize: "0.78rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Future benchmark lane · official rows not yet materialized
        </p>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", margin: "0.5rem 0", lineHeight: 1.02 }}>
          BEAM 1M Hybrid Architecture + Multi-Agent Custody
        </h1>
        <p style={{ maxWidth: "880px", lineHeight: 1.7 }}>
          The public BEAM 1M target scope is 35 conversations and 700 probes. HydraDG has prepared the A–H architecture contract, but the official rows have not yet been materialized, revision-pinned, or row-hashed in this repository. No HydraDG BEAM score is claimed.
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
          HydraDB reports <strong>82% overall on BEAM 1M</strong>, compared with <strong>74% for Hindsight</strong>. These are external benchmark references, not HydraDG measurements and not route-by-route scores.
        </p>
        <p style={{ marginBottom: 0, opacity: 0.8 }}>
          HydraDG remains <strong>PREPARED_UNEXECUTED</strong> until official BEAM rows, revisions, hashes, model outputs, and evaluator receipts exist.
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
                <th style={{ padding: "0.8rem" }}>HydraDG state</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((route) => (
                <tr key={route.id} style={{ borderBottom: "1px solid rgba(127,127,127,0.25)" }}>
                  <td style={{ padding: "0.8rem", fontWeight: 800 }}>{route.id}</td>
                  <td style={{ padding: "0.8rem" }}>{route.name}</td>
                  <td style={{ padding: "0.8rem", color: "#d97706", fontWeight: 800 }}>{route.state}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={{ marginBottom: "2rem", padding: "1.25rem", border: "1px solid rgba(212,175,55,0.5)", borderRadius: "8px" }}>
        <p style={{ color: "#d4af37", fontWeight: 800, fontSize: "0.78rem", letterSpacing: "0.08em", textTransform: "uppercase", marginTop: 0 }}>
          Future preregistered multi-agent hypothesis
        </p>
        <h2>Preserve where the error entered — and what inherited it.</h2>
        <p style={{ lineHeight: 1.7 }}>
          Future work will represent every retrieval, extraction, reasoning, decision, and answer agent as part of the FCG. Wrong decisions remain perturbation evidence, so HydraDG can test where an error first entered, which downstream agents inherited it, and which correction restored a valid state.
        </p>
        <p style={{ lineHeight: 1.7, marginBottom: 0 }}>
          Primary future hypothesis: explicit FCO supersession, validity, provenance, claim-state, and agent-decision lineage can improve BEAM knowledge-update, contradiction-resolution, and multi-session reasoning without degrading temporal reasoning, event ordering, or multi-session guardrails.
        </p>
      </section>

      <section style={{ padding: "1.25rem", border: "1px solid rgba(127,127,127,0.35)", borderRadius: "8px" }}>
        <h2 style={{ marginTop: 0 }}>Future quality + economics measurements</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {futureMetrics.map((metric) => (
            <span key={metric} style={{ border: "1px solid rgba(127,127,127,0.35)", borderRadius: "999px", padding: "0.35rem 0.6rem", fontSize: "0.82rem" }}>
              {metric}
            </span>
          ))}
        </div>
        <p style={{ lineHeight: 1.7, marginBottom: 0, marginTop: "1rem" }}>
          Anticube classification is preregistered as a governance/classification signal, not an assumed ranking boost. Storage savings, token savings, avoided model calls, and cost-per-correct-governed-answer remain <strong>NOT MEASURED</strong>; no cost-saving claim is made until serialized bytes, context tokens, and inference calls are actually counted.
        </p>
      </section>
    </main>
  );
}
