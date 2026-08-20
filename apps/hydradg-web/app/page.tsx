import Link from "next/link";

import ContextIcebergHero from "@/components/ContextIcebergHero";
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
            HydraDG keeps changing memory as a traversable custody graph: canonical identity, current state, prior state,
            contradiction, supersession, source and claim ceiling remain linked instead of collapsing into one answer.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Start judge walkthrough</Link>
            <Link className="secondary" href="/real-local-matrix">Real model matrix · running</Link>
            <Link className="secondary" href="/best-use">Why HydraDB · show the math</Link>
            <Link className="secondary" href="/graph">Open 4D FCG</Link>
          </div>
          <div className="curatedStatusRow">
            <span className="statusLine"><span className="statusDot good" />Historical LongMemEval full500 executed</span>
            <span className="statusLine"><span className="statusDot" />10-model × 3-dataset × K=5/10/100 matrix CURRENTLY RUNNING</span>
            <span className="statusLine"><span className="statusDot" />Vithia perturbation family CURRENTLY RUNNING</span>
            <span className="statusLine"><span className="statusDot" />Hosted canonical parity remains pending readback</span>
          </div>
        </div>
        <div className="curatedHeroViz"><ContextIcebergHero /></div>
      </header>

      <section className="metrics curatedMetrics" aria-label="Recorded execution and accounting state">
        <article className="metric"><span className="metricLabel">Identity reuse</span><strong>65.730975%</strong><span className="small muted">31.67M word+sentence occurrences → 10.85M unique keys</span></article>
        <article className="metric"><span className="metricLabel">Expanded experiment</span><strong>CURRENTLY RUNNING</strong><span className="small muted">10 local Ollama text lanes · 3 datasets · K=5/10/100 · plus separate Vithia family</span></article>
        <article className="metric"><span className="metricLabel">Result publication rule</span><strong>RECEIPT FIRST</strong><span className="small muted">No provisional numerical score is promoted before a stable execution receipt exists</span></article>
        <article className="metric"><span className="metricLabel">Historical baseline</span><strong>500 cases</strong><span className="small muted">LongMemEval full500 · 470 historical K=5 scored · 30 abstentions</span></article>
      </section>

      <section className="computeSection curatedSection" id="scale-economics">
        <div className="curatedSectionHead">
          <div>
            <span className="sectionNumber">01 / BEST USE OF HYDRADB</span>
            <h2 className="displayTitle">One identity. Many contexts. Math that fails closed.</h2>
          </div>
          <Link className="primary" href="/best-use">Show the math</Link>
        </div>
        <p className="sectionLead">
          The strongest current scale result is identity reuse, not a fabricated storage or energy headline. Retained word/sentence accounting gives 31,672,976 occurrences, 10,854,020 unique keys and 20,818,956 duplicate occurrences. Whole-corpus download-byte savings remain NOT_MEASURED until a complete hashed byte manifest exists.
        </p>
        <div className="curatedEvidenceGrid">
          <article className="panel"><p className="eyebrow">Deterministic custody</p><h2>Input hash → contract hash → output hash.</h2><p className="muted">The calculator recomputes the same receipt from the same canonical JSON. Hash or arithmetic mismatch is retained as failure evidence.</p></article>
          <article className="panel"><p className="eyebrow">Graph-native economics</p><h2>Reuse content identity; keep contextual edges.</h2><p className="muted">Repeated occurrences can point to a canonical key while preserving distinct file, dataset, time and provenance relationships in the FCG.</p></article>
        </div>
      </section>

      <section className="computeSection curatedSection" id="demo">
        <div className="curatedSectionHead">
          <div><span className="sectionNumber">02 / GOLDEN PATH</span><h2 className="displayTitle">Reference → poison → antidote.</h2></div>
          <Link className="secondary" href="/judge">Run it</Link>
        </div>
        <p className="sectionLead">One fact changes. HydraDG preserves the old state, records the relationship that diverged, and restores the declared current state without deleting the perturbation history.</p>
        <div className="storyStrip">
          <article><span className="storyIndex">01</span><div><strong>Reference</strong><p>Read the current fact and its source/session path.</p></div></article>
          <article><span className="storyIndex">02</span><div><strong>Poison</strong><p>Add a conflicting state and explicit supersession/contradiction edges.</p></div></article>
          <article><span className="storyIndex">03</span><div><strong>Antidote</strong><p>Restore the valid state while the divergent history remains inspectable.</p></div></article>
        </div>
      </section>

      <section className="computeSection curatedSection" id="result">
        <span className="sectionNumber">03 / REAL LOCAL MODEL EXPERIMENT</span>
        <h2 className="displayTitle">The expanded matrix is running now.</h2>
        <p className="sectionLead">
          HydraDG is executing the broader model × dataset × retrieval-depth experiment on magicstudiobox: ten local Ollama text-model lanes across EnterpriseRAG-Bench, HydraBlast-Real-Deps, and LongMemEval-S-full500 at K=5, K=10, and K=100, plus a separate Vithia/Pythia-14m perturbation family. Every result remains CURRENTLY_RUNNING until its model-output, FCO/FCG, deterministic replay, and statistical receipts are stable.
        </p>
        <div className="curatedEvidenceGrid">
          <article className="panel"><p className="eyebrow">Current result state</p><h2>CURRENTLY RUNNING.</h2><p className="muted">No expanded numerical headline is shown yet. Positive, null, negative, failed, timeout, and abstaining cells will all be retained.</p></article>
          <article className="panel"><p className="eyebrow">Historical baseline</p><h2>Full500 K=5 remains evidence, not the final headline.</h2><p className="muted">The earlier Track 03 ablation remains preserved as the first baseline. The expanded real-model matrix will determine whether that result generalizes, reverses, or becomes mixed.</p></article>
        </div>
        <div className="actions">
          <Link className="primary" href="/real-local-matrix">Open running matrix</Link>
          <Link className="secondary" href="/track03">Historical Track 03 baseline</Link>
          <Link className="secondary" href="/evidence">Open evidence ledger</Link>
        </div>
      </section>

      <section className="computeSection curatedSection" id="evolution">
        <span className="sectionNumber">04 / PRESENTATION EVOLUTION</span>
        <h2 className="displayTitle">New views supersede. Old views stay in the graph.</h2>
        <p className="sectionLead">Earlier web and root scopes remain custody evidence rather than being rewritten as current state. The Context Iceberg numbers can be scrubbed over time to inspect information-state measurements; they are not retroactive quality scores for the UI or production migration.</p>
        <div className="curatedEvidenceGrid">
          <article className="panel"><p className="eyebrow">Fractal custody</p><h2>Roots become evidence upstream.</h2><p className="muted">Source, atom, seed, experiment and release objects recursively carry identity, context, governance and provenance.</p></article>
          <article className="panel"><p className="eyebrow">Visible semantics</p><h2>Measurement lanes stay separate.</h2><p className="muted">Historical retrieval, running real-model evaluation, dedup accounting, theoretical compute and infrastructure parity are never collapsed into one health score.</p></article>
        </div>
        <div className="actions"><Link className="primary" href="/evolution">Open version + metric history</Link></div>
      </section>

      <section className="computeSection curatedSection" id="explore">
        <span className="sectionNumber">05 / EXPLORE</span>
        <h2 className="displayTitle">Start with the judge path, then inspect the running matrix, graph and math.</h2>
        <div className="routeGrid curatedRouteGrid">
          <Link href="/judge" className="routeCard"><div><p className="eyebrow">Guided</p><h3>Judge demo</h3><p>Follow the reference → poison → antidote path with bounded claims.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/real-local-matrix" className="routeCard"><div><p className="eyebrow">Running</p><h3>Real local model matrix</h3><p>See every planned model × dataset × K result as CURRENTLY_RUNNING until receipt-backed values land.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/best-use" className="routeCard"><div><p className="eyebrow">Deterministic</p><h3>Why HydraDB</h3><p>Inspect identity reuse, theoretical compute and fail-closed calculation hashes.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/graph" className="routeCard"><div><p className="eyebrow">Interactive</p><h3>4D FCG</h3><p>Rotate space, scrub time and inspect context envelopes on graph objects.</p></div><span className="routeArrow">↗</span></Link>
        </div>
        <div className="actions">
          <Link className="secondary" href="/knowledge">Knowledge</Link><Link className="secondary" href="/how-to">How to use</Link><Link className="secondary" href="/eligibility">Eligibility</Link><a className="secondary" href="/backup/hydradg.html">Static fallback</a><a className="secondary" href="/api/site-fcg">Site FCG JSON</a>
        </div>
      </section>

      <footer className="computeSection curatedFooter">
        <div><p className="eyebrow">Website custody</p><p className="small muted">{site.nodes.length} site FCOs · {site.edges.length} application-level FCG edges · presentation lineage retained in GitHub.</p></div>
        <p className="small muted">SHA-256 establishes retained byte/object identity only. Current project signature state remains NOT_SIGNED and live Merkle state remains NOT_MERKLE_COMMITTED unless later operations establish otherwise.</p>
      </footer>
    </main>
  );
}