import Link from "next/link";

import ContextIcebergHero from "@/components/ContextIcebergHero";

export default function Home() {
  return (
    <main>
      <header className="hero curatedHero" id="top">
        <div className="curatedHeroCopy">
          <p className="eyebrow goldText">Hack Hydra 2026 · Track 03 · HydraDG</p>
          <h1>See what changed. Trace why.</h1>
          <p className="lede">
            HydraDG keeps changing memory as a traversable custody graph: canonical identity, current state, prior state,
            contradiction, supersession, source and claim ceiling remain linked instead of collapsing into one answer.
          </p>
          <div className="actions">
            <Link className="primary goldenCta" href="/judge">Start judge walkthrough</Link>
            <Link className="secondary" href="/best-use">Why HydraDB · show the math</Link>
            <Link className="secondary" href="/graph">Open 4D FCG</Link>
          </div>
          <div className="curatedStatusRow">
            <span className="statusLine"><span className="statusDot good" />LongMemEval full500 executed</span>
            <span className="statusLine"><span className="statusDot good" />Deterministic atom/key reuse accounting present</span>
            <span className="statusLine"><span className="statusDot" />Expanded hosted FCG parity remains reconciliation-gated</span>
            <span className="statusLine"><span className="statusDot warn" />Project Ed25519 signing pending external private-key operation</span>
          </div>
        </div>
        <div className="curatedHeroViz"><ContextIcebergHero /></div>
      </header>

      <section className="computeSection curatedSection" id="judge-start">
        <span className="sectionNumber goldenSectionLabel">00 / JUDGE START</span>
        <h2 className="displayTitle">One golden path. Every word is a link.</h2>
        <div className="routeGrid curatedRouteGrid">
          <Link href="/judge" className="routeCard goldenPanel"><div><p className="eyebrow goldText">01 · Change state</p><h3>Reference → poison → antidote</h3><p>Inspect the explicit state transitions and T0–T5 evidence lanes.</p></div><span className="routeArrow">→</span></Link>
          <Link href="/track03" className="routeCard"><div><p className="eyebrow goldText">02 · Read result</p><h3>Executed Track 03 evidence</h3><p>Read the full500 null/negative retrieval result under its claim ceiling.</p></div><span className="routeArrow">→</span></Link>
          <Link href="/graph" className="routeCard"><div><p className="eyebrow goldText">03 · Trace FCO</p><h3>Follow provenance</h3><p>Open the 4D FCG and resolve one object backward to source and evidence.</p></div><span className="routeArrow">→</span></Link>
          <Link href="/models" className="routeCard"><div><p className="eyebrow goldText">04 · Models used</p><h3>Know when an LLM is in the loop</h3><p>Primary K=5: no model. Local Qwen models: separate probabilistic diagnostic lane.</p></div><span className="routeArrow">→</span></Link>
          <Link href="/custody" className="routeCard"><div><p className="eyebrow goldText">05 · Verify custody</p><h3>Hash ≠ signature</h3><p>Inspect SHA-256 identity, publication public-key fingerprint and current unsigned project state.</p></div><span className="routeArrow">→</span></Link>
          <Link href="/evidence" className="routeCard"><div><p className="eyebrow goldText">06 · Evidence</p><h3>Verify the receipts</h3><p>Inspect result, release, provenance and claim-boundary evidence.</p></div><span className="routeArrow">↗</span></Link>
        </div>
      </section>

      <section className="metrics curatedMetrics" aria-label="Recorded execution and accounting state">
        <article className="metric"><span className="metricLabel">Identity reuse</span><strong>65.730975%</strong><span className="small muted">31.67M word+sentence occurrences → 10.85M unique keys</span></article>
        <article className="metric"><span className="metricLabel">Duplicate occurrences</span><strong>20,818,956</strong><span className="small muted">deterministic retained accounting · not tokenizer tokens</span></article>
        <article className="metric"><span className="metricLabel">7B compute scenario</span><strong>2.9147×10¹⁷ FLOPs</strong><span className="small muted">0.809626 Wh theoretical equivalent · energy NOT measured</span></article>
        <article className="metric"><span className="metricLabel">Executed benchmark</span><strong>500 cases</strong><span className="small muted">LongMemEval full500 · 470 scored · 30 abstentions</span></article>
      </section>

      <section className="computeSection curatedSection" id="scale-economics">
        <div className="curatedSectionHead"><div><span className="sectionNumber">01 / BEST USE OF HYDRADB</span><h2 className="displayTitle">One identity. Many contexts. Math that fails closed.</h2></div><Link className="primary" href="/best-use">Show the math</Link></div>
        <p className="sectionLead">The strongest current scale result is identity reuse, not a fabricated storage or energy headline. Retained word/sentence accounting gives 31,672,976 occurrences, 10,854,020 unique keys and 20,818,956 duplicate occurrences. Whole-corpus download-byte savings remain NOT_MEASURED until a complete hashed byte manifest exists.</p>
        <div className="curatedEvidenceGrid">
          <article className="panel"><p className="eyebrow">Deterministic custody</p><h2>Input hash → contract hash → output hash.</h2><p className="muted">The calculator recomputes the same receipt from the same canonical JSON. Hash or arithmetic mismatch is retained as failure evidence.</p></article>
          <article className="panel"><p className="eyebrow">Graph-native economics</p><h2>Reuse content identity; keep contextual edges.</h2><p className="muted">Repeated occurrences can point to a canonical key while preserving distinct file, dataset, time and provenance relationships in the FCG.</p></article>
        </div>
      </section>

      <section className="computeSection curatedSection" id="demo">
        <div className="curatedSectionHead"><div><span className="sectionNumber goldenSectionLabel">02 / GOLDEN PATH</span><h2 className="displayTitle">Reference → poison → antidote.</h2></div><Link className="secondary" href="/judge">Run it</Link></div>
        <p className="sectionLead">One fact changes. HydraDG preserves the old state, records the relationship that diverged, and restores the declared current state without deleting the perturbation history.</p>
        <div className="storyStrip">
          <article><span className="storyIndex">01</span><div><strong><Link className="goldLink" href="/graph?q=T0_REFERENCE">Reference</Link></strong><p>Read the current fact and its source/session path.</p></div></article>
          <article><span className="storyIndex">02</span><div><strong><Link className="goldLink" href="/graph?q=T1_MUTATION">Poison</Link></strong><p>Add a conflicting state and explicit supersession/contradiction edges.</p></div></article>
          <article><span className="storyIndex">03</span><div><strong><Link className="goldLink" href="/graph?q=T2_RESTORATION">Antidote</Link></strong><p>Restore the valid state while the divergent history remains inspectable.</p></div></article>
        </div>
      </section>

      <section className="computeSection curatedSection" id="result">
        <span className="sectionNumber goldenSectionLabel">03 / EXECUTED EVIDENCE</span>
        <h2 className="displayTitle">The graph worked. The tested retrieval advantage did not appear.</h2>
        <p className="sectionLead">The completed full500 ablation constructed and queried the typed graph but did not establish a positive B/C/D Hit@5 signal over the flat route at the tested configuration. HydraDG retains that null/negative evidence instead of optimizing it away.</p>
        <div className="curatedEvidenceGrid">
          <article className="panel goldenPanel"><p className="eyebrow">Model used</p><h2>None for primary K=5.</h2><p className="mono small">extractor=heuristic · model=null · ollarma_url=null</p><p className="muted">Local Qwen models belong to a separate post-freeze probabilistic diagnostic lane.</p></article>
          <article className="panel"><p className="eyebrow">Scientific ceiling</p><h2>Retrieval ablation only.</h2><p className="muted">Not an end-to-end LongMemEval QA improvement claim. Hash identity is not correctness.</p></article>
          <article className="panel"><p className="eyebrow">Infrastructure ceiling</p><h2>Expanded parity remains open.</h2><p className="muted">Historical bounded hosted parity remains evidence for its own scope; expanded current FCG parity requires a fresh receipt.</p></article>
        </div>
        <div className="actions"><Link className="primary goldenCta" href="/track03">Open Track 03 result</Link><Link className="secondary" href="/models">Models used</Link><Link className="secondary" href="/evidence">Evidence ledger</Link></div>
      </section>

      <section className="computeSection curatedSection" id="tracks">
        <span className="sectionNumber">04 / THREE TRACK LENSES</span>
        <h2 className="displayTitle">One custody spine. Three graph problems.</h2>
        <div className="grid threeCol">
          <article className="panel"><p className="eyebrow">Track 01</p><h2><Link className="goldLink" href="/track01">Enterprise context + ontology</Link></h2><p className="muted">Identity, alias, provenance and current-state graph design. Real-data evaluation remains pending.</p></article>
          <article className="panel"><p className="eyebrow">Track 02</p><h2><Link className="goldLink" href="/track02">Repos + dependencies</Link></h2><p className="muted">Blast-radius traversal and patch reasoning. Synthetic structural canary remains bounded; real-data evaluation remains pending.</p></article>
          <article className="panel goldenPanel"><p className="eyebrow">Track 03 · primary submission</p><h2><Link className="goldLink" href="/track03">Memory + context retrieval</Link></h2><p className="muted">LongMemEval full500 executed; null/negative retrieval result retained.</p></article>
        </div>
      </section>

      <section className="computeSection curatedSection" id="custody-summary">
        <span className="sectionNumber goldenSectionLabel">05 / CRYPTOGRAPHIC BOUNDARY</span>
        <h2 className="displayTitle">Content-addressed now. Project signing next.</h2>
        <p className="sectionLead">Current project FCOs use SHA-256 identity. The site does not call the current HydraDG graph signed or sealed because no project Ed25519 detached-signature receipt has been admitted for every current object. A real publication signing key fingerprint is shown only under its publication scope.</p>
        <div className="actions"><Link className="primary goldenCta" href="/custody">Inspect custody state</Link><Link className="secondary" href="/models">Inspect model identities</Link></div>
      </section>

      <section className="computeSection curatedSection" id="explore">
        <span className="sectionNumber">06 / EXPLORE</span>
        <h2 className="displayTitle">No back button required.</h2>
        <div className="actions"><Link className="secondary" href="/judge">Judge</Link><Link className="secondary" href="/best-use">Why HydraDB</Link><Link className="secondary" href="/track01">Track 01</Link><Link className="secondary" href="/track02">Track 02</Link><Link className="secondary" href="/track03">Track 03</Link><Link className="secondary" href="/graph">Graph</Link><Link className="secondary" href="/models">Models</Link><Link className="secondary" href="/custody">Custody</Link><Link className="secondary" href="/knowledge">Knowledge</Link><Link className="secondary" href="/how-to">How to use</Link><Link className="secondary" href="/eligibility">Eligibility</Link><a className="secondary" href="/backup/hydradg.html">Static fallback</a></div>
      </section>
    </main>
  );
}
