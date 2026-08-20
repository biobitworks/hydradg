import Link from "next/link";

import ContextIcebergHeroV2 from "@/components/ContextIcebergHeroV2";
import KnowledgeTermLink from "@/components/KnowledgeTermLink";
import PublicBackendStatus from "@/components/PublicBackendStatus";
import { buildReleaseManifest } from "@/lib/releaseMeta";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

export default function Home() {
  const release = buildReleaseManifest();
  const canonicalFcos = release.fco_identity_validation.unique_fco_count;

  return (
    <main>
      <header className="hero curatedHero" id="top">
        <div className="curatedHeroCopy">
          <p className="eyebrow">Hack Hydra 2026 · Track 03 · HydraDG</p>
          <h1>See the context move.</h1>
          <p className="lede">
            HydraDG keeps changing memory as a traversable <KnowledgeTermLink slug="fcg">custody graph</KnowledgeTermLink>: <KnowledgeTermLink slug="current-state">current state</KnowledgeTermLink>, prior state, <KnowledgeTermLink slug="contradicts">contradiction</KnowledgeTermLink>, <KnowledgeTermLink slug="superseded-by">supersession</KnowledgeTermLink>, source, and <KnowledgeTermLink slug="claim-ceiling">claim ceiling</KnowledgeTermLink> remain linked instead of collapsing into one answer.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Start judge walkthrough</Link>
            <Link className="secondary" href="/graph">Open 4D FCG</Link>
            <Link className="secondary" href="/track-fit">Why Graph? + math</Link>
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

      <section className="metrics curatedMetrics" aria-label="Newest recorded project measurements">
        <article className="metric"><span className="metricLabel">Hosted FCG</span><strong>36 FCOs</strong><span className="small muted">24 edges · canonical parity PASS</span></article>
        <article className="metric"><span className="metricLabel">Context classified</span><strong>18,555 / 18,567</strong><span className="small muted">99.9354% · 12 abstentions</span></article>
        <article className="metric"><span className="metricLabel">Track 03</span><strong>500 cases</strong><span className="small muted">23,867 temporal sessions</span></article>
        <article className="metric"><span className="metricLabel">Release identity</span><strong>{canonicalFcos} FCOs</strong><span className="small muted">one canonical SHA-256 each · PASS</span></article>
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
          <article className="panel"><p className="eyebrow">Scientific ceiling</p><h2>Retrieval ablation only.</h2><p className="muted">Not an end-to-end LongMemEval QA improvement claim. <KnowledgeTermLink slug="fco">Hash identity</KnowledgeTermLink> is not correctness.</p></article>
          <article className="panel"><p className="eyebrow">Custody boundary</p><h2>History stays visible.</h2><p className="muted">Negative, null, superseded and restored states remain first-class graph objects rather than being deleted.</p></article>
        </div>
        <div className="actions"><Link className="secondary" href="/track03">Open Track 03 result</Link><Link className="secondary" href="/results/context-vs-entropy">Context vs Entropy</Link><Link className="secondary" href="/evidence">Evidence ledger</Link><Link className="secondary" href="/track-fit">Show the math</Link></div>
      </section>

      <section className="computeSection curatedSection" id="time-space">
        <span className="sectionNumber">03 / TIME + SPACE FCG</span>
        <h2 className="displayTitle">Scientific distribution scores and production measurements are separate lanes.</h2>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Timepoint</th><th align="left">Class</th><th align="left">Scientific distribution score</th><th align="left">Measured state evidence</th></tr></thead>
            <tbody>
              {RELEASE_TIMEPOINTS.map((point) => (
                <tr key={point.id} style={{ borderLeft: `3px solid ${point.color}` }}>
                  <td><strong style={{ color: point.color }}>{point.id} · {point.label}</strong></td>
                  <td>{point.classification}</td>
                  <td>{point.score_state === "MEASURED" ? `G* ${point.g_star?.toFixed(6)} · ΔG* ${point.delta_g_star?.toFixed(6)} · Drift ${point.cloud_drift?.toFixed(4)}` : "N/A by contract"}</td>
                  <td className="small">{point.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small muted note">T3–T5 do not borrow the T2 G*/Cloud Drift scalar. Their real migration, experiment, release, parity and identity calculations are shown on <Link href="/track-fit">Why Graph? + math</Link> and Evolution.</p>
      </section>

      <section className="computeSection curatedSection" id="explore">
        <span className="sectionNumber">04 / EXPLORE</span>
        <h2 className="displayTitle">One custody spine. Three graph problems.</h2>
        <p className="sectionLead">The final judge path emphasizes Track 03 while preserving the shared custody spine used by the broader HydraDG track experiments.</p>
        <div className="routeGrid curatedRouteGrid">
          <Link href="/judge" className="routeCard"><div><p className="eyebrow">Guided</p><h3>Judge demo</h3><p>Reference → poison → antidote with exact calculations.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/track03" className="routeCard"><div><p className="eyebrow">Executed</p><h3>Results</h3><p>Full500 graph, retrieval result, hashes and claim ceiling.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/graph" className="routeCard"><div><p className="eyebrow">Interactive</p><h3>4D FCG</h3><p>Click a node for classification-colored state math, FCO hash and Anticube consideration.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/track-fit" className="routeCard"><div><p className="eyebrow">Final judge step</p><h3>Why Graph?</h3><p>Track 01/02/03 fit, real project math, worked examples and graph-native claim boundary.</p></div><span className="routeArrow">↗</span></Link>
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
