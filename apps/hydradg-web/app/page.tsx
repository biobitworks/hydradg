import Link from "next/link";

import ContextIcebergHeroV2 from "@/components/ContextIcebergHeroV2";
import PublicBackendStatus from "@/components/PublicBackendStatus";
import { CURRENT_PRESENTATION } from "@/lib/presentationLineage";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

export default function Home() {
  return (
    <main>
      <header className="hero curatedHero" id="top">
        <div className="curatedHeroCopy">
          <p className="eyebrow">Hack Hydra 2026 · Track 03 · HydraDG</p>
          <h1>See the context move.</h1>
          <p className="lede">
            HydraDG keeps changing memory as a traversable custody graph: current state, prior state, contradiction,
            supersession, source, and claim ceiling remain linked instead of collapsing into one answer.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Start judge walkthrough</Link>
            <Link className="secondary" href="/graph">Open 4D FCG</Link>
            <Link className="secondary" href="/how-to">How to use</Link>
          </div>
          <div className="curatedStatusRow">
            <span className="statusLine"><span className="statusDot good" />LongMemEval full500 executed</span>
            <span className="statusLine"><span className="statusDot good" />Hosted canonical FCG readback receipt recorded</span>
            <span className="statusLine"><span className="statusDot good" />One SHA-256 identity per canonical FCO</span>
          </div>
        </div>
        <div className="curatedHeroViz"><ContextIcebergHeroV2 /></div>
      </header>

      <PublicBackendStatus />

      <section className="metrics curatedMetrics" aria-label="Recorded execution state">
        <article className="metric"><span className="metricLabel">Cases</span><strong>500</strong><span className="small muted">LongMemEval-S full500</span></article>
        <article className="metric"><span className="metricLabel">Sessions</span><strong>23,867</strong><span className="small muted">typed temporal state</span></article>
        <article className="metric"><span className="metricLabel">Result</span><strong>No positive signal</strong><span className="small muted">B/C/D hit-rate advantage not established</span></article>
        <article className="metric"><span className="metricLabel">Presentation</span><strong>Current</strong><span className="small muted">{CURRENT_PRESENTATION.label}</span></article>
      </section>

      <section className="computeSection curatedSection" id="demo">
        <div className="curatedSectionHead">
          <div><span className="sectionNumber">01 / GOLDEN PATH</span><h2 className="displayTitle">Reference → poison → antidote.</h2></div>
          <Link className="secondary" href="/judge">Open table walkthrough</Link>
        </div>
        <p className="sectionLead">One fact changes. HydraDG preserves the old state, records the relationship that diverged, and restores the declared current state without deleting the perturbation history.</p>
        <div className="storyStrip">
          <article><span className="storyIndex" style={{ color: "#b69cff" }}>01</span><div><strong>Reference / normal</strong><p>Violet · frozen comparison state.</p></div></article>
          <article><span className="storyIndex" style={{ color: "#ff8a3d" }}>02</span><div><strong>Poison / mutation</strong><p>Orange · controlled divergent state.</p></div></article>
          <article><span className="storyIndex" style={{ color: "#5aa9ff" }}>03</span><div><strong>Antidote / restoration</strong><p>Blue · recovery while poison history remains.</p></div></article>
        </div>
        <div className="actions">
          <Link className="secondary" href="/knowledge#knowledge-atom">KnowledgeAtom</Link>
          <Link className="secondary" href="/knowledge#seed-of-truth">SeedOfTruth</Link>
          <Link className="secondary" href="/graph?q=KnowledgeAtom">Atoms in graph</Link>
          <Link className="secondary" href="/graph?q=SeedOfTruth">Seeds in graph</Link>
        </div>
      </section>

      <section className="computeSection curatedSection" id="result">
        <span className="sectionNumber">02 / EXECUTED EVIDENCE</span>
        <h2 className="displayTitle">The graph worked. The tested retrieval advantage did not appear.</h2>
        <p className="sectionLead">The completed full500 ablation constructed and queried the typed graph but did not establish a positive B/C/D hit-rate signal over the flat route at the tested configuration. HydraDG retains that null/negative evidence instead of optimizing it away.</p>
        <div className="curatedEvidenceGrid">
          <article className="panel"><p className="eyebrow">Scientific ceiling</p><h2>Retrieval ablation only.</h2><p className="muted">Not an end-to-end LongMemEval QA improvement claim. Hash identity is not correctness.</p></article>
          <article className="panel"><p className="eyebrow">Custody boundary</p><h2>History stays visible.</h2><p className="muted">Negative, null, superseded and restored states remain first-class graph objects rather than being deleted.</p></article>
        </div>
        <div className="actions"><Link className="secondary" href="/track03">Open Track 03 result</Link><Link className="secondary" href="/results/context-vs-entropy">Context vs Entropy</Link><Link className="secondary" href="/evidence">Evidence ledger</Link></div>
      </section>

      <section className="computeSection curatedSection" id="time-space">
        <span className="sectionNumber">03 / TIME + SPACE FCG</span>
        <h2 className="displayTitle">Scientific state and release state are not collapsed into one score.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Timepoint</th><th align="left">Class</th><th align="left">Scalar context score</th><th align="left">Evidence</th></tr></thead>
            <tbody>
              {RELEASE_TIMEPOINTS.map((point) => (
                <tr key={point.id}>
                  <td><strong style={{ color: point.color }}>{point.id} · {point.label}</strong></td>
                  <td>{point.classification}</td>
                  <td>{point.score_state === "MEASURED" ? `G* ${point.g_star?.toFixed(6)} · ΔG* ${point.delta_g_star?.toFixed(6)} · Drift ${point.cloud_drift?.toFixed(4)}` : "N/A — no declared distribution"}</td>
                  <td className="small">{point.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small muted note">T3–T5 are real project/release transitions, but HydraDG does not fabricate a G*/Cloud Drift scalar when the required distribution is not declared.</p>
      </section>

      <section className="computeSection curatedSection" id="explore">
        <span className="sectionNumber">04 / EXPLORE</span>
        <h2 className="displayTitle">One custody spine. Three graph problems.</h2>
        <p className="sectionLead">The final judge path emphasizes Track 03 while preserving the shared custody spine used by the broader HydraDG track experiments.</p>
        <div className="routeGrid curatedRouteGrid">
          <Link href="/judge" className="routeCard"><div><p className="eyebrow">Guided</p><h3>Judge demo</h3><p>Reference → poison → antidote with exact calculations.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/track03" className="routeCard"><div><p className="eyebrow">Executed</p><h3>Results</h3><p>Full500 graph, retrieval result, hashes and claim ceiling.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/graph" className="routeCard"><div><p className="eyebrow">Interactive</p><h3>4D FCG</h3><p>Violet reference, orange poison, blue antidote; inspect one FCO hash.</p></div><span className="routeArrow">↗</span></Link>
        </div>
        <div className="actions">
          <Link className="secondary" href="/knowledge">Knowledge Base</Link>
          <Link className="secondary" href="/how-to">How to use</Link>
          <Link className="secondary" href="/evolution">Version history</Link>
          <Link className="secondary" href="/eligibility">Eligibility</Link>
          <a className="secondary" href="/api/release">Release JSON</a>
          <a className="secondary" href="/api/site-fcg">Site FCG JSON</a>
        </div>
      </section>
    </main>
  );
}
