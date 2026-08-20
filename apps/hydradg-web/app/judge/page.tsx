import PublicBackendStatus from "@/components/PublicBackendStatus";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

const WALKTHROUGH = RELEASE_TIMEPOINTS.slice(0, 3);
const RELEASE_STATES = RELEASE_TIMEPOINTS.slice(3);

function scalar(point: (typeof RELEASE_TIMEPOINTS)[number]) {
  if (point.score_state !== "MEASURED") return "N/A — no declared distribution";
  return `G* ${point.g_star?.toFixed(6)} · ΔG* ${point.delta_g_star?.toFixed(6)} · Cloud Drift ${point.cloud_drift?.toFixed(4)}`;
}

export default function JudgePage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Judge Demo · public read-only walkthrough</p>
          <h1>Change state. Keep the history.</h1>
          <p className="lede">
            HydraDG models reference → poison → antidote as explicit graph state transitions, then records hosted migration,
            the Context-vs-Entropy experiment and the final release as separate FCG timepoints rather than copying one score forward.
          </p>
          <div className="actions">
            <a className="primary" href="/graph">Open 4D FCG</a>
            <a className="secondary" href="/how-to">How to use</a>
            <a className="secondary" href="/knowledge">Knowledge Base</a>
          </div>
        </div>
      </header>

      <PublicBackendStatus />

      <section className="computeSection">
        <span className="sectionNumber">01 / GOLDEN PATH TABLE</span>
        <h2 className="displayTitle">Reference → poison → antidote with the exact declared calculations.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr><th align="left">State</th><th align="left">Color</th><th align="left">Distribution</th><th>U*</th><th>G*</th><th>ΔG*</th><th>Cloud Drift</th><th align="left">What to inspect</th></tr>
            </thead>
            <tbody>
              {WALKTHROUGH.map((point) => (
                <tr key={point.id}>
                  <td><strong>{point.id} · {point.label}</strong></td>
                  <td><span aria-hidden="true" style={{ color: point.color, fontSize: 22 }}>●</span> {point.color}</td>
                  <td className="mono small">[{point.distribution?.join(", ")}]</td>
                  <td align="center">{point.burden?.toFixed(2)}</td>
                  <td align="center">{point.g_star?.toFixed(6)}</td>
                  <td align="center">{point.delta_g_star && point.delta_g_star > 0 ? "+" : ""}{point.delta_g_star?.toFixed(6)}</td>
                  <td align="center">{point.cloud_drift?.toFixed(4)}</td>
                  <td className="small">{point.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small muted note">Violet = reference/normal, orange = poison/mutation, blue = antidote/restoration. Color identifies state; it does not encode correctness or retrieval accuracy.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / FCO WALKTHROUGH</span>
        <h2 className="displayTitle">Source → Evidence → KnowledgeAtom → SeedOfTruth → StateSnapshot.</h2>
        <div className="actions">
          <a className="secondary" href="/graph?q=Source">Source FCOs</a>
          <a className="secondary" href="/graph?q=Evidence">Evidence FCOs</a>
          <a className="secondary" href="/graph?q=KnowledgeAtom">KnowledgeAtom</a>
          <a className="secondary" href="/graph?q=SeedOfTruth">SeedOfTruth</a>
          <a className="secondary" href="/graph?q=StateSnapshot">StateSnapshot</a>
          <a className="secondary" href="/knowledge#knowledge-atom">KB: KnowledgeAtom</a>
          <a className="secondary" href="/knowledge#seed-of-truth">KB: SeedOfTruth</a>
        </div>
        <p className="small muted note">Every canonical FCO inspector exposes one FCO ID and one matching object SHA-256. A hash establishes object identity, not scientific truth.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / PROJECT + RELEASE TIMEPOINTS</span>
        <h2 className="displayTitle">T3–T5 are real transitions without fabricated scalar context scores.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Timepoint</th><th align="left">Classification</th><th align="left">Scalar score state</th><th align="left">Evidence</th></tr></thead>
            <tbody>
              {RELEASE_STATES.map((point) => (
                <tr key={point.id}>
                  <td><strong style={{ color: point.color }}>{point.id} · {point.label}</strong></td>
                  <td>{point.classification}</td>
                  <td>{scalar(point)}</td>
                  <td className="small">{point.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / WHAT TO CLICK NEXT</span>
        <h2 className="displayTitle">Follow the evidence, not a sales claim.</h2>
        <div className="actions">
          <a className="primary" href="/track03">Executed Track 03 Result</a>
          <a className="secondary" href="/results/context-vs-entropy">Context vs Entropy</a>
          <a className="secondary" href="/evidence">Evidence Ledger</a>
          <a className="secondary" href="/evolution">Version + FCG history</a>
          <a className="secondary" href="/eligibility">Eligibility proof</a>
          <a className="secondary" href="/api/release">Release JSON</a>
        </div>
        <p className="small muted note">The public walkthrough is read-only. It demonstrates the declared state-transition and custody contract; it does not mutate a judge-visible HydraDB tenant.</p>
      </section>
    </main>
  );
}
