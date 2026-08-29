import React from "react";
import SponsorMissionPanel from "@/components/sponsors/SponsorMissionPanel";

export const metadata = {
  title: "Agent Native Builders 2026 — Evidence Gateway Audit & Conformance",
  description: "Preregistered 20-Fixture Conformance Test Suite & Real Agent Experiment Status"
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
    deterministic_conformance_status: "DETERMINISTIC CONFORMANCE TEST — PASS",
    real_agent_experiment_status: "REAL AGENT CONTROL/TREATMENT EXPERIMENT — NOT YET ESTABLISHED"
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", maxWidth: "900px", margin: "0 auto" }}>
      <h1>HydraDG Agent-Native Evidence Gateway</h1>
      <h2>20-Fixture Deterministic Conformance Suite</h2>
      <p><strong>Execution Host:</strong> <code>magicSTUDIObox.local</code></p>
      <p><strong>Branch:</strong> <code>hack-hydra/agent-native-builders-20260826</code></p>
      <p><strong>Provenances:</strong> 5 Real Benchmark Cases, 14 Synthetic Conformance Fixtures, 1 Development Fixture</p>
      <SponsorMissionPanel />

      <div style={{ marginTop: "1rem", padding: "1rem", backgroundColor: "#eef9ff", borderLeft: "4px solid #0070f3", borderRadius: "4px" }}>
        <p><strong>Suite Status:</strong> <code>{summary.deterministic_conformance_status}</code></p>
        <p><strong>Empirical Comparison:</strong> <code>{summary.real_agent_experiment_status}</code></p>
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1.5rem" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #ccc", textAlign: "left" }}>
            <th style={{ padding: "8px" }}>Metric / Conformance Gate</th>
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
        <h3>Governance Audit & Reclassification Note</h3>
        <p style={{ fontSize: "0.9rem", color: "#555" }}>
          Forensic audit of <code>scripts/agent_native_builders_runner.py</code> verified that the 20-fixture suite evaluates deterministic conformance logic without live LLM calls (<code>zero_model_calls=true</code>). The empirical claim of superiority has been reclassified to a deterministic conformance test pass. A live 2-case Ollama model comparison canary (using <code>qwen3:8b</code>) is preregistered as the next experimental gate.
        </p>
      </div>
    </main>
  );
}
