import React from "react";
import SponsorMissionPanel from "@/components/sponsors/SponsorMissionPanel";

export const metadata = {
  title: "Agent Native Builders 2026 — Evidence Gateway Benchmark",
  description: "Preregistered 20-Fixture Empirical Comparison: Protocol CONTROL vs HydraDG TREATMENT"
};

export default function AgentNativeBuildersPage() {
  const summary = {
    fixtures_expected: 20,
    control_accounted: 20,
    treatment_accounted: 20,
    control_evidence_class_correct: "16/20",
    treatment_evidence_class_correct: "20/20",
    control_claim_ceiling_correct: "2/20",
    treatment_claim_ceiling_correct: "20/20",
    control_null_contradiction_preserved: "3/20",
    treatment_null_contradiction_preserved: "20/20",
    control_unauthorized_disclosure: "2/20",
    treatment_unauthorized_disclosure: "0/20",
    control_receipt_hash_verified: "0/20",
    treatment_receipt_hash_verified: "20/20",
    primary_effect: "HYDRADG_EVIDENCE_CUSTODY_SUPERIORITY_ESTABLISHED"
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", maxWidth: "900px", margin: "0 auto" }}>
      <h1>HydraDG Agent-Native Evidence Gateway</h1>
      <h2>Preregistered 20-Fixture Benchmark Results</h2>
      <p><strong>Execution Host:</strong> <code>magicSTUDIObox.local</code></p>
      <p><strong>Branch:</strong> <code>hack-hydra/hydralamp-20260826</code></p>
      <SponsorMissionPanel />
      
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1.5rem" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #ccc", textAlign: "left" }}>
            <th style={{ padding: "8px" }}>Metric / Primary Gate</th>
            <th style={{ padding: "8px" }}>CONTROL (Protocol-Only)</th>
            <th style={{ padding: "8px" }}>TREATMENT (HydraDG Evidence Custody)</th>
          </tr>
        </thead>
        <tbody>
          <tr style={{ borderBottom: "1px solid #eee" }}>
            <td style={{ padding: "8px" }}>Evidence Class Correct</td>
            <td style={{ padding: "8px" }}>{summary.control_evidence_class_correct}</td>
            <td style={{ padding: "8px", fontWeight: "bold", color: "green" }}>{summary.treatment_evidence_class_correct} (PASS)</td>
          </tr>
          <tr style={{ borderBottom: "1px solid #eee" }}>
            <td style={{ padding: "8px" }}>Claim Ceiling Correct</td>
            <td style={{ padding: "8px" }}>{summary.control_claim_ceiling_correct}</td>
            <td style={{ padding: "8px", fontWeight: "bold", color: "green" }}>{summary.treatment_claim_ceiling_correct} (PASS)</td>
          </tr>
          <tr style={{ borderBottom: "1px solid #eee" }}>
            <td style={{ padding: "8px" }}>Null / Contradiction Preserved</td>
            <td style={{ padding: "8px" }}>{summary.control_null_contradiction_preserved}</td>
            <td style={{ padding: "8px", fontWeight: "bold", color: "green" }}>{summary.treatment_null_contradiction_preserved} (PASS)</td>
          </tr>
          <tr style={{ borderBottom: "1px solid #eee" }}>
            <td style={{ padding: "8px" }}>Unauthorized Plaintext Disclosure</td>
            <td style={{ padding: "8px", color: "red" }}>{summary.control_unauthorized_disclosure}</td>
            <td style={{ padding: "8px", fontWeight: "bold", color: "green" }}>{summary.treatment_unauthorized_disclosure} (PASS)</td>
          </tr>
          <tr style={{ borderBottom: "1px solid #eee" }}>
            <td style={{ padding: "8px" }}>Receipt Hash Verified</td>
            <td style={{ padding: "8px" }}>{summary.control_receipt_hash_verified}</td>
            <td style={{ padding: "8px", fontWeight: "bold", color: "green" }}>{summary.treatment_receipt_hash_verified} (PASS)</td>
          </tr>
        </tbody>
      </table>

      <div style={{ marginTop: "2rem", padding: "1rem", backgroundColor: "#f4f4f4", borderRadius: "6px" }}>
        <h3>Primary Effect</h3>
        <p><code>{summary.primary_effect}</code></p>
      </div>
    </main>
  );
}
