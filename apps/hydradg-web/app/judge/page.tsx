import GoldenJudgeWalkthrough from "@/components/GoldenJudgeWalkthrough";
import PublicBackendStatus from "@/components/PublicBackendStatus";
import { TIMEPOINTS, TIMEPOINT_FCG_EDGES, getReleaseEvaluationFlags } from "@/lib/releaseTimepoints";

export default function JudgePage() {
  const flags = getReleaseEvaluationFlags();

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Judge Demo · public read-only walkthrough</p>
          <h1>Change state. Keep the history.</h1>
          <p className="lede">
            HydraDG models reference → poison → antidote as explicit graph state transitions. Timepoints T0–T2 use synthetic distributions ($G^*$, $\Delta G^*$, Cloud Drift); T3–T5 report empirical migration and release evidence without fabricating scores.
          </p>
        </div>
      </header>

      <GoldenJudgeWalkthrough showCta={false} />

      <PublicBackendStatus />

      <section className="computeSection">
        <span className="sectionNumber">02 / TIMEPOINT EVIDENCE LANES (T0–T5)</span>
        <h2 className="displayTitle">Scientific boundary &amp; multi-lane evaluation ledger.</h2>
        <p className="sectionLead">
          T0–T2 measure synthetic distribution perturbation ($G^*$, $\Delta G^*$, Cloud Drift). T3–T5 have no declared scoring distribution (`G_STAR_STATE = NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION`) and report exact measured migration, classification, and release identity deltas.
        </p>

        <div className="tableWrap" style={{ overflowX: "auto", margin: "1.5rem 0" }}>
          <table className="small" style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid rgba(255,255,255,0.15)", background: "rgba(255,255,255,0.02)" }}>
                <th style={{ padding: "10px" }}>Timepoint</th>
                <th style={{ padding: "10px" }}>State</th>
                <th style={{ padding: "10px" }}>Scientific Distribution Score</th>
                <th style={{ padding: "10px" }}>Migration / Experiment Measurement</th>
                <th style={{ padding: "10px" }}>Custody / Identity</th>
                <th style={{ padding: "10px" }}>Backend / Traceability</th>
                <th style={{ padding: "10px" }}>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {TIMEPOINTS.map((tp) => (
                <tr key={tp.timepoint} style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                  <td style={{ padding: "10px", fontWeight: "bold", whiteSpace: "nowrap" }}>
                    <span className="pill pillMuted" style={{ marginRight: "6px" }}>{tp.timepoint}</span>
                    {tp.label.replace(/^T\d\s*/, "")}
                  </td>
                  <td style={{ padding: "10px" }}>
                    <span className="mono small">{tp.state_type}</span>
                  </td>
                  <td style={{ padding: "10px" }}>
                    {tp.score_state.status === "DECLARED" ? (
                      <div>
                        <div><strong style={{ color: "#10b981" }}>G*: {tp.score_state.g_star.toFixed(6)}</strong></div>
                        <div className="small muted">ΔG*: {tp.score_state.delta_g_star > 0 ? "+" : ""}{tp.score_state.delta_g_star.toFixed(6)}</div>
                        <div className="small muted">Cloud Drift: {tp.score_state.cloud_drift.toFixed(4)}</div>
                      </div>
                    ) : (
                      <div>
                        <span className="pill pillMuted" style={{ fontSize: "11px" }}>N/A BY CONTRACT</span>
                        <div className="small muted" style={{ fontSize: "11px", marginTop: "4px" }}>
                          No declared distribution
                        </div>
                      </div>
                    )}
                  </td>
                  <td style={{ padding: "10px", maxWidth: "260px" }}>
                    {tp.measurement_summary}
                  </td>
                  <td style={{ padding: "10px", maxWidth: "220px" }}>
                    {tp.custody_identity}
                  </td>
                  <td style={{ padding: "10px", maxWidth: "220px" }}>
                    {tp.backend_traceability}
                  </td>
                  <td style={{ padding: "10px" }}>
                    <span className="mono small" style={{ color: "#60a5fa" }}>{tp.evidence}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="grid twoCol" style={{ marginTop: "1.5rem", gap: "1rem" }}>
          <div className="panel" style={{ padding: "1rem" }}>
            <p className="eyebrow" style={{ color: "#10b981" }}>Evaluation Summary Flags</p>
            <h3 style={{ margin: "0.25rem 0 0.75rem 0" }}>System Evaluation Results</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }} className="small mono">
              <div>T3 Canonical Parity: <span className="pill pillGood">{flags.T3_CANONICAL_PARITY}</span></div>
              <div>T3 FCO Delta: <span className="pill pillGood">{flags.T3_FCO_DELTA}</span></div>
              <div>T3 Edge Delta: <span className="pill pillGood">{flags.T3_EDGE_DELTA}</span></div>
              <div>T3 Hash Delta: <span className="pill pillGood">{flags.T3_HASH_DELTA}</span></div>
              <div>T3 Root Match: <span className="pill pillGood">{flags.T3_ROOT_MATCH}</span></div>
              <div>T3 Connectivity: <span className="pill pillGood">{flags.T3_BACKEND_CONNECTIVITY}</span></div>
              <div>T3 Collection: <span className="pill pillGood">{flags.T3_COLLECTION_DISCOVERY}</span></div>
              <div>T3 Traceability: <span className="pill pillGood">{flags.T3_TRACEABILITY}</span></div>
              <div>T4 Coverage: <span className="pill pillGood">{flags.T4_CLASSIFICATION_COVERAGE}</span></div>
              <div>T4 Abstention Rate: <span className="pill pillGood">{flags.T4_ABSTENTION_RATE}</span></div>
              <div>T4 Sum Invariant: <span className="pill pillGood">{flags.T4_CATEGORY_SUM_INVARIANT}</span></div>
              <div>T5 SHA Match: <span className="pill pillGood">{flags.T5_DEPLOYED_SHA_MATCH}</span></div>
              <div>T5 FCO Hash Match: <span className="pill pillGood">{flags.T5_RELEASE_FCO_HASH_MATCH}</span></div>
              <div>T5 FCO Validation: <span className="pill pillGood">{flags.T5_CANONICAL_FCO_IDENTITY_VALIDATION}</span></div>
            </div>
          </div>

          <div className="panel" style={{ padding: "1rem" }}>
            <p className="eyebrow" style={{ color: "#60a5fa" }}>FCG Graph Lineage</p>
            <h3 style={{ margin: "0.25rem 0 0.75rem 0" }}>Declared Evidence Edges</h3>
            <div className="stack" style={{ gap: "4px" }}>
              {TIMEPOINT_FCG_EDGES.map((edge, i) => (
                <div key={i} className="mono small compact" style={{ padding: "4px 8px", background: "rgba(255,255,255,0.03)", borderRadius: "4px" }}>
                  <span style={{ color: "#9ca3af" }}>{edge.src}</span>
                  <span style={{ color: "#f59e0b", margin: "0 6px" }}>--[{edge.rel}]--&gt;</span>
                  <span style={{ color: "#60a5fa" }}>{edge.dst}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / WHAT TO CLICK NEXT</span>
        <h2 className="displayTitle">Follow the evidence, not a sales claim.</h2>
        <div className="actions">
          <a className="primary" href="/real-local-matrix">See Running Real-Model Matrix</a>
          <a className="secondary" href="/track03">Historical Track 03 Baseline</a>
          <a className="secondary" href="/graph">Trace One Result</a>
          <a className="secondary" href="/knowledge">Need a term? Open Knowledge Base</a>
          <a className="secondary" href="/backup/hydradg.html">Open Static Fallback</a>
        </div>
        <p className="small muted note">
          This page demonstrates the state-transition contract and multi-lane timepoint evidence ledger. It does not claim that clicking presentation states mutates the public HydraDB tenant.
        </p>
      </section>
    </main>
  );
}
