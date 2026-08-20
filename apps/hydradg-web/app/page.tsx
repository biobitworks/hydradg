import Link from "next/link";

import ContextIcebergHero from "@/components/ContextIcebergHero";
import { CURRENT_PRESENTATION } from "@/lib/presentationLineage";
import { buildSiteFcg } from "@/lib/siteFcg";

export default function Home() {
  const site = buildSiteFcg();

  return (
    <main>
      <header className="hero curatedHero" id="top">
        <div className="curatedHeroCopy">
          <p className="eyebrow">Hack Hydra 2026 · Track 03 · HydraDG</p>
          <h1>See what changed. Trace why.</h1>
          <p className="lede">
            HydraDG keeps changing memory as a traversable custody graph: current state, prior state, contradiction,
            supersession, source, and claim ceiling remain linked instead of collapsing into one answer.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Start judge walkthrough</Link>
            <Link className="secondary" href="/graph">Open 4D FCG</Link>
          </div>
          <div className="curatedStatusRow">
            <span className="statusLine"><span className="statusDot good" />LongMemEval full500 executed</span>
            <span className="statusLine"><span className="statusDot good" />HydraDB graph path executed locally</span>
            <span className="statusLine"><span className="statusDot warn" />Hosted HydraDB readback requires deployment configuration</span>
          </div>
        </div>
        <div className="curatedHeroViz"><ContextIcebergHero /></div>
      </header>

      <section className="metrics curatedMetrics" aria-label="Recorded execution state">
        <article className="metric"><span className="metricLabel">Cases</span><strong>500</strong><span className="small muted">LongMemEval-S full500</span></article>
        <article className="metric"><span className="metricLabel">Sessions</span><strong>23,867</strong><span className="small muted">typed temporal state</span></article>
        <article className="metric"><span className="metricLabel">Result</span><strong>No positive signal</strong><span className="small muted">B/C/D hit-rate advantage not established</span></article>
        <article className="metric"><span className="metricLabel">Presentation</span><strong>Current</strong><span className="small muted">{CURRENT_PRESENTATION.label}</span></article>
      </section>

      <section className="computeSection curatedSection" id="demo">
        <div className="curatedSectionHead">
          <div>
            <span className="sectionNumber">01 / GOLDEN PATH</span>
            <h2 className="displayTitle">Reference → poison → antidote.</h2>
          </div>
          <Link className="secondary" href="/judge">Run it</Link>
        </div>
        <p className="sectionLead">
          One fact changes. HydraDG preserves the old state, records the relationship that diverged, and restores the declared current state without deleting the perturbation history.
        </p>
        <div className="storyStrip">
          <article><span className="storyIndex">01</span><div><strong>Reference</strong><p>Read the current fact and its source/session path.</p></div></article>
          <article><span className="storyIndex">02</span><div><strong>Poison</strong><p>Add a conflicting state and explicit supersession/contradiction edges.</p></div></article>
          <article><span className="storyIndex">03</span><div><strong>Antidote</strong><p>Restore the valid state while the divergent history remains inspectable.</p></div></article>
        </div>
      </section>

      <section className="computeSection curatedSection" id="result">
        <span className="sectionNumber">02 / EXECUTED EVIDENCE</span>
        <h2 className="displayTitle">The graph worked. The tested retrieval advantage did not appear.</h2>
        <p className="sectionLead">
          The completed full500 ablation constructed and queried the typed graph but did not establish a positive B/C/D hit-rate signal over the flat route at the tested configuration. HydraDG retains that null/negative evidence instead of optimizing it away.
        </p>
        <div className="curatedEvidenceGrid">
          <article className="panel">
            <p className="eyebrow">Scientific ceiling</p>
            <h2>Retrieval ablation only.</h2>
            <p className="muted">Not an end-to-end LongMemEval QA improvement claim. Hash identity is not correctness.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Custody boundary</p>
            <h2>History stays visible.</h2>
            <p className="muted">Negative, null, superseded and restored states remain first-class graph objects rather than being deleted.</p>
          </article>
        </div>
        <div className="actions">
          <Link className="secondary" href="/track03">Open Track 03 result</Link>
          <Link className="secondary" href="/evidence">Open evidence ledger</Link>
        </div>
      </section>

      <section className="computeSection curatedSection" id="evolution">
        <span className="sectionNumber">03 / PRESENTATION EVOLUTION</span>
        <h2 className="displayTitle">New views supersede. Old views stay in the graph.</h2>
        <p className="sectionLead">
          The Vercel-facing layout is intentionally quieter. Earlier web states remain linked to their exact Git commits and lose only default presentation priority. The Context Iceberg numbers can be scrubbed over time to inspect whether information-state and retrieval measurements changed; they are not retroactive quality scores for the UI.
        </p>
        <div className="curatedEvidenceGrid">
          <article className="panel"><p className="eyebrow">Less noise</p><h2>One story first.</h2><p className="muted">Judge path, executed result and 4D state field are primary; implementation detail moves to dedicated deep-dive routes.</p></article>
          <article className="panel"><p className="eyebrow">Visible semantics</p><h2>Color means direction.</h2><p className="muted">Warm/cool/violet encode signed ΔG* direction; Cloud Drift controls halo magnitude. Neither is an accuracy verdict.</p></article>
        </div>
        <div className="actions"><Link className="primary" href="/evolution">Open version + metric history</Link></div>
      </section>

      <section className="computeSection curatedSection" id="explore">
        <span className="sectionNumber">04 / EXPLORE</span>
        <h2 className="displayTitle">Three doors, then the deep dive.</h2>
        <div className="routeGrid curatedRouteGrid">
          <Link href="/judge" className="routeCard"><div><p className="eyebrow">Guided</p><h3>Judge demo</h3><p>Follow the reference → poison → antidote path with bounded claims.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/track03" className="routeCard"><div><p className="eyebrow">Executed</p><h3>Results</h3><p>Inspect the full500 graph, retrieval result, hashes and claim ceiling.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/graph" className="routeCard"><div><p className="eyebrow">Interactive</p><h3>4D FCG</h3><p>Rotate space, scrub time and inspect context envelopes on graph objects.</p></div><span className="routeArrow">↗</span></Link>
        </div>
        <div className="actions">
          <Link className="secondary" href="/knowledge">Knowledge</Link>
          <Link className="secondary" href="/how-to">How to use</Link>
          <Link className="secondary" href="/eligibility">Eligibility</Link>
          <a className="secondary" href="/backup/hydradg.html">Static fallback</a>
          <a className="secondary" href="/api/site-fcg">Site FCG JSON</a>
        </div>
      </section>

      <footer className="computeSection curatedFooter">
        <div><p className="eyebrow">Website custody</p><p className="small muted">{site.nodes.length} site FCOs · {site.edges.length} application-level FCG edges · presentation lineage retained in GitHub.</p></div>
        <p className="small muted">SHA-256 establishes retained byte/object identity only. Current project signature state remains NOT_SIGNED and live Merkle state remains NOT_MERKLE_COMMITTED unless later operations establish otherwise.</p>
      </footer>
    </main>
  );
}
