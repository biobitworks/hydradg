import Link from "next/link";
import auditGate from "@/lib/final-audit-gate.json";

export default function RealLocalMatrixPage() {
  const cellStates = [
    { cell: "Deterministic IR Scorers", state: "EXECUTED", badgeClass: "badgeExecuted", details: "Hit@K, Recall@K, Precision@K, MRR, MAP@K, nDCG@K computed from per-case ranked IDs" },
    { cell: "Ollama Local Text Models (10 Models)", state: "EXECUTED", badgeClass: "badgeExecuted", details: "10 text models dynamically discovered from runtime (ollama list)" },
    { cell: "Vithia Pythia-14m Training Evidence", state: "NOT_ESTABLISHED", badgeClass: "badgeBlocked", details: "NOT_ESTABLISHED_FROM_EXECUTION_RECEIPT (No raw training log found)" },
    { cell: "DeepEval Suite", state: "BLOCKED_PACKAGE_NOT_INSTALLED", badgeClass: "badgeBlocked", details: "deepeval package not installed in runtime environment" },
    { cell: "Ragas Suite", state: "BLOCKED_PACKAGE_NOT_INSTALLED", badgeClass: "badgeBlocked", details: "ragas package not installed in runtime environment" },
    { cell: "Inspect AI Harness", state: "BLOCKED_PACKAGE_NOT_INSTALLED", badgeClass: "badgeBlocked", details: "inspect_ai package not installed in runtime environment" },
    { cell: "BEIR Benchmarks", state: "BLOCKED_PACKAGE_NOT_INSTALLED", badgeClass: "badgeBlocked", details: "beir package not installed in runtime environment" },
    { cell: "MTEB Control", state: "BLOCKED_PACKAGE_NOT_INSTALLED", badgeClass: "badgeBlocked", details: "mteb package not installed in runtime environment" },
    { cell: "LM-Eval Capability Control", state: "BLOCKED_PACKAGE_NOT_INSTALLED", badgeClass: "badgeBlocked", details: "lm_eval package not installed in runtime environment" },
    { cell: "Historical 9efee94f Constant Values", state: "RECLASSIFIED_DEVELOPMENT_ARTIFACT", badgeClass: "badgeReclassified", details: "Reclassified as development lineage; NOT primary empirical evidence" },
  ];

  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1rem", fontFamily: "sans-serif" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#d97706", fontWeight: "bold", fontSize: "0.875rem", letterSpacing: "0.05em", textTransform: "uppercase" }}>
          Forensic Execution Audit · Real Receipt Repair
        </p>
        <h1 style={{ fontSize: "2.25rem", fontWeight: "800", color: "#0f172a", marginTop: "0.5rem" }}>
          Forensic Execution Audit v2 & Real Receipt Repair
        </h1>
        <p style={{ color: "#475569", fontSize: "1.125rem", maxWidth: "800px", lineHeight: "1.6" }}>
          “Every claimed numerical score is verified against actual case-level execution receipts.
          Literal metric dictionaries and constant math are explicitly reclassified as development lineage rather than primary evidence.”
        </p>
        <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
          <Link href="/eligibility" style={{ background: "#0284c7", color: "#fff", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            ← Back to Eligibility Synthesis
          </Link>
          <Link href="/beam-1m" style={{ background: "#e2e8f0", color: "#0f172a", padding: "0.625rem 1.25rem", borderRadius: "6px", textDecoration: "none", fontWeight: "600" }}>
            BEAM 1M Preprocessing
          </Link>
        </div>
      </header>

      {/* Audit Gate Summary */}
      <section style={{ marginBottom: "3rem", background: "#f8fafc", padding: "1.5rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <h2 style={{ fontSize: "1.25rem", fontWeight: "700", color: "#0f172a", marginBottom: "0.5rem" }}>
          Final Audit Gate Verification: {auditGate.evidence_audit_gate}
        </h2>
        <p style={{ fontSize: "0.875rem", color: "#475569", margin: "0.25rem 0" }}>
          <strong>Start SHA:</strong> {auditGate.starting_sha} | <strong>Models Discovered:</strong> {auditGate.models_discovered} | <strong>Cases Executed:</strong> {auditGate.dataset_cases_actually_executed}
        </p>
        <p style={{ fontSize: "0.875rem", color: "#0284c7", fontWeight: "bold", margin: "0.25rem 0" }}>
          <strong>Primary Claim Ceiling:</strong> {auditGate.primary_claim_ceiling}
        </p>
      </section>

      {/* Matrix Cell Provenance Table */}
      <section style={{ marginBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", borderBottom: "2px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          Forensic Cell Audit & Evidence Classification
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", textAlign: "left", fontSize: "0.875rem" }}>
          <thead>
            <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0" }}>
              <th style={{ padding: "0.75rem" }}>Evaluation Cell / Metric</th>
              <th style={{ padding: "0.75rem" }}>Audited Execution State</th>
              <th style={{ padding: "0.75rem" }}>Provenance & Forensic Audit Notes</th>
            </tr>
          </thead>
          <tbody>
            {cellStates.map((c, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.75rem", fontWeight: "bold" }}>{c.cell}</td>
                <td style={{ padding: "0.75rem", fontWeight: "bold" }}>
                  {c.state === "EXECUTED" && <span style={{ background: "#dcfce7", color: "#15803d", padding: "0.25rem 0.5rem", borderRadius: "4px" }}>EXECUTED</span>}
                  {c.state.startsWith("BLOCKED") && <span style={{ background: "#fee2e2", color: "#991b1b", padding: "0.25rem 0.5rem", borderRadius: "4px" }}>{c.state}</span>}
                  {c.state === "NOT_ESTABLISHED" && <span style={{ background: "#fef3c7", color: "#92400e", padding: "0.25rem 0.5rem", borderRadius: "4px" }}>NOT_ESTABLISHED</span>}
                  {c.state === "RECLASSIFIED_DEVELOPMENT_ARTIFACT" && <span style={{ background: "#f1f5f9", color: "#475569", padding: "0.25rem 0.5rem", borderRadius: "4px" }}>RECLASSIFIED</span>}
                </td>
                <td style={{ padding: "0.75rem", color: "#475569" }}>{c.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}