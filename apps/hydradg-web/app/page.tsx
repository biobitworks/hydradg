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
            <Link className="secondary" href="/best-use">Why HydraDB · show the math</Link>
            <Link className="secondary" href="/graph">Open 4D FCG</Link>
          </div>
          <div className="curatedStatusRow">
            <span className="statusLine"><span className="statusDot good" />LongMemEval full500 executed</span>
            <span className="statusLine"><span className="statusDot good" />Deterministic atom/key reuse accounting present</span>
            <span className="statusLine"><span className="statusDot" />Expanded SeedGraph/local/hosted parity not yet established</span>
          </div>
        </div>
        <div className="curatedHeroViz"><ContextIcebergHero /></div>
      </header>

      <section className="metrics curatedMetrics" aria-label="Recorded execution and accounting state">
        <article className="metric"><span className="metricLabel">Identity reuse</span><strong>65.730975%</strong><span className="small muted">31.67M word+sentence occurrences → 10.85M unique keys</span></article>
        <article className="metric"><span className="metricLabel">Duplicate occurrences</span><strong>20,818,956</strong><span className="small muted">deterministic retained accounting · not tokenizer tokens</span></article>
        <article className="metric"><span className="metricLabel">7B compute scenario</span><strong>2.9147×10¹⁷ FLOPs</strong><span className="small muted">0.809626 Wh theoretical equivalent · energy NOT measured</span></article>
        <article className="metric"><span className="metricLabel">Executed benchmark</span><strong>500 cases</strong><span className="small muted">LongMemEval full500 · 470 scored · 30 abstentions</span></article>
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
          <article className="panel">
            <p className="eyebrow">Deterministic custody</p>
            <h2>Input hash → contract hash → output hash.</h2>
            <p className="muted">The calculator recomputes the same receipt from the same canonical JSON. Hash or arithmetic mismatch is retained as failure evidence.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Graph-native economics</p>
            <h2>Reuse content identity; keep contextual edges.</h2>
            <p className="muted">Repeated occurrences can point to a canonical key while preserving distinct file, dataset, time and provenance relationships in the FCG.</p>
          </article>
        </div>
      </section>

      <section className="computeSection curatedSection" id="demo">
        <div className="curatedSectionHead">
          <div>
            <span className="sectionNumber">02 / GOLDEN PATH</span>
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
        <span className="sectionNumber">03 / EXECUTED EVIDENCE</span>
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
            <p className="eyebrow">Current infrastructure ceiling</p>
            <h2>Expanded parity remains open.</h2>
            <p className="muted">Historical hosted projection evidence remains retained, but actual SeedGraph admission, full local HydraDB write/readback and expanded hosted parity require real operation receipts.</p>
          </article>
        </div>
        <div className="actions">
          <Link className="secondary" href="/track03">Open Track 03 result</Link>
          <Link className="secondary" href="/evidence">Open evidence ledger</Link>
        </div>
      </section>

      <section className="computeSection curatedSection" id="evolution">
        <span className="sectionNumber">04 / PRESENTATION EVOLUTION</span>
        <h2 className="displayTitle">New views supersede. Old views stay in the graph.</h2>
        <p className="sectionLead">
          Earlier web and root scopes remain custody evidence rather than being rewritten as current state. The Context Iceberg numbers can be scrubbed over time to inspect information-state measurements; they are not retroactive quality scores for the UI or production migration.
        </p>
        <div className="curatedEvidenceGrid">
          <article className="panel"><p className="eyebrow">Fractal custody</p><h2>Roots become evidence upstream.</h2><p className="muted">Source, atom, seed, experiment and release objects recursively carry identity, context, governance and provenance.</p></article>
          <article className="panel"><p className="eyebrow">Visible semantics</p><h2>Measurement lanes stay separate.</h2><p className="muted">Synthetic G*/Cloud Drift, executed retrieval, dedup accounting, theoretical compute and infrastructure parity are never collapsed into one health score.</p></article>
        </div>
        <div className="actions"><Link className="primary" href="/evolution">Open version + metric history</Link></div>
      </section>

      <section className="computeSection curatedSection" id="explore">
        <span className="sectionNumber">05 / EXPLORE</span>
        <h2 className="displayTitle">Start with the judge path, then inspect the graph and math.</h2>
        <div className="routeGrid curatedRouteGrid">
          <Link href="/judge" className="routeCard"><div><p className="eyebrow">Guided</p><h3>Judge demo</h3><p>Follow the reference → poison → antidote path with bounded claims.</p></div><span className="routeArrow">↗</span></Link>
          <Link href="/best-use" className="routeCard"><div><p className="eyebrow">Deterministic</p><h3>Why HydraDB</h3><p>Inspect identity reuse, theoretical compute and fail-closed calculation hashes.</p></div><span className="routeArrow">↗</span></Link>
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
