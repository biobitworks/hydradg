import KnowledgeTermLink from "@/components/KnowledgeTermLink";
import PublicBackendStatus from "@/components/PublicBackendStatus";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

const WALKTHROUGH = RELEASE_TIMEPOINTS.slice(0, 3);
const RELEASE_STATES = RELEASE_TIMEPOINTS.slice(3);

function scalar(point: (typeof RELEASE_TIMEPOINTS)[number]) {
  if (point.score_state !== "MEASURED") return "N/A by contract";
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
            HydraDG models reference → poison → antidote as explicit <KnowledgeTermLink slug="fcg">graph state transitions</KnowledgeTermLink>, then records hosted migration,
            the Context-vs-Entropy experiment and the final release as separate FCG timepoints rather than copying one score forward.
          </p>
          <div className="actions">
            <a className="primary" href="/graph">Open 4D FCG</a>
            <a className="secondary" href="/how-to">How to use</a>
            <a className="secondary" href="/knowledge">Terminology matrix</a>
            <a className="secondary" href="/track-fit">Final: Why Graph? + math</a>
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
              {WALKTHROUGH.map((point) => {
                const numberStyle = { color: point.color, background: `${point.color}12`, fontWeight: 700 } as const;
                return (
                  <tr key={point.id} style={{ borderLeft: `3px solid ${point.color}` }}>
                    <td><strong style={{ color: point.color }}>{point.id} · {point.label}</strong></td>
                    <td><span aria-hidden="true" style={{ color: point.color, fontSize: 22 }}>●</span> {point.color}</td>
                    <td className="mono small">[{point.distribution?.join(", ")}]</td>
                    <td align="center" style={numberStyle}>{point.burden?.toFixed(2)}</td>
                    <td align="center" style={numberStyle}>{point.g_star?.toFixed(6)}</td>
                    <td align="center" style={numberStyle}>{point.delta_g_star && point.delta_g_star > 0 ? "+" : ""}{point.delta_g_star?.toFixed(6)}</td>
                    <td align="center" style={numberStyle}>{point.cloud_drift?.toFixed(4)}</td>
                    <td className="small">{point.evidence}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="small muted note">Violet = reference/normal, orange = poison/mutation, blue = antidote/restoration. Color identifies the declared state classification; it does not encode correctness, retrieval accuracy, or <KnowledgeTermLink slug="anticube">Anticube</KnowledgeTermLink> safety classification.</p>
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
          <a className="secondary" href="/graph?q=ClassificationReceipt">Anticube receipts</a>
          <a className="secondary" href="/knowledge#knowledge-atom">KB: KnowledgeAtom</a>
          <a className="secondary" href="/knowledge#seed-of-truth">KB: SeedOfTruth</a>
        </div>
        <p className="small muted note">Click any node in the 4D graph to see its state math and Anticube consideration. Every canonical FCO inspector exposes one FCO ID and one matching object SHA-256. A hash establishes object identity, not scientific truth.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / PROJECT + RELEASE TIMEPOINTS</span>
        <h2 className="displayTitle">T3–T5 have real measurements even when G*/Cloud Drift is N/A by contract.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Timepoint</th><th align="left">Classification</th><th align="left">Scientific distribution score</th><th align="left">Measured project/release quantities</th><th align="left">Evidence</th></tr></thead>
            <tbody>
              {RELEASE_STATES.map((point) => (
                <tr key={point.id} style={{ borderLeft: `3px solid ${point.color}` }}>
                  <td><strong style={{ color: point.color }}>{point.id} · {point.label}</strong></td>
                  <td>{point.classification}</td>
                  <td>{scalar(point)}</td>
                  <td className="small">
                    <div className="stack">
                      {(point.project_measurements || []).map((measurement) => (
                        <div key={measurement.label} style={{ border: `1px solid ${point.color}55`, background: `${point.color}0d`, borderRadius: 8, padding: "7px 9px" }}>
                          <strong>{measurement.label}</strong><br />
                          <span className="mono small">{measurement.value}</span> <span className={measurement.state === "PASS" ? "pill pillGood" : "pill pillMuted"}>{measurement.state}</span>
                        </div>
                      ))}
                    </div>
                  </td>
                  <td className="small">{point.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small muted note">The production lane answers a different question from the synthetic G* lane: did custody identity survive migration, what did the experiment classify/abstain on, and does the deployed release resolve to its exact hash identity?</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / WHAT TO CLICK NEXT</span>
        <h2 className="displayTitle">Follow the evidence, then finish with the graph-fit argument.</h2>
        <div className="actions">
          <a className="primary" href="/track03">Executed Track 03 Result</a>
          <a className="secondary" href="/results/context-vs-entropy">Context vs Entropy</a>
          <a className="secondary" href="/evidence">Evidence Ledger</a>
          <a className="secondary" href="/evolution">Version + FCG history</a>
          <a className="secondary" href="/eligibility">Eligibility proof</a>
          <a className="secondary" href="/track-fit">Why Graph? + show the math</a>
          <a className="secondary" href="/api/release">Release JSON</a>
        </div>
        <p className="small muted note">The public walkthrough is read-only. It demonstrates the declared state-transition and custody contract; it does not mutate a judge-visible HydraDB database.</p>
      </section>
    </main>
  );
}
