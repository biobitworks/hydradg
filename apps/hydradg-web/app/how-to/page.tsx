export default function HowToPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">How to use HydraDG</p>
          <h1>One path from context change to custody.</h1>
          <p className="lede">
            This page is the judge/operator guide. Follow the numbered path; every step is read-only against the public scientific state.
          </p>
        </div>
      </header>

      <section className="grid twoCol">
        <article className="panel">
          <p className="eyebrow">1 · Overview</p>
          <h2>Interact with the Context Iceberg</h2>
          <p className="muted">Rotate x/y/z, zoom, scrub time, and select an FCO. Read ΔG* and Cloud Drift separately from Hit@K and Recall@K.</p>
          <a className="secondary" href="/">Open Overview</a>
        </article>
        <article className="panel">
          <p className="eyebrow">2 · Judge Demo</p>
          <h2>Reference → poison → antidote</h2>
          <p className="muted">Move through the controlled state sequence and confirm that prior state is retained rather than overwritten.</p>
          <a className="secondary" href="/judge">Start Judge Walkthrough</a>
        </article>
        <article className="panel">
          <p className="eyebrow">3 · Results</p>
          <h2>Read the empirical outcome</h2>
          <p className="muted">Inspect cases, graph scale, Hit@K, Recall@K and the retained null/negative result under its declared claim ceiling.</p>
          <a className="secondary" href="/track03">Open Track 03 Results</a>
        </article>
        <article className="panel">
          <p className="eyebrow">4 · Graph</p>
          <h2>Trace one FCO</h2>
          <p className="muted">Select a node and follow its identity, relations, source/provenance, claim ceiling and HydraDB projection/readback state.</p>
          <a className="secondary" href="/graph">Open 4D Graph</a>
        </article>
        <article className="panel">
          <p className="eyebrow">5 · Knowledge</p>
          <h2>Resolve project terminology</h2>
          <p className="muted">Use the governed Knowledge Base for FCO, FCG, HydraDB, Context Iceberg, Cloud Drift, ΔG*, Hit@K and Recall@K.</p>
          <a className="secondary" href="/knowledge">Open Knowledge Base</a>
        </article>
        <article className="panel">
          <p className="eyebrow">6 · Eligibility</p>
          <h2>Check release and custody state</h2>
          <p className="muted">Inspect hashes, roots, signature/Merkle status and publication boundaries before treating an artifact as released.</p>
          <a className="secondary" href="/eligibility">Check Eligibility</a>
        </article>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Fallback</p>
        <h2>Live → static → live</h2>
        <p className="muted">
          The static artifact is an offline presentation fallback. It is not a live HydraDB control surface.
        </p>
        <div className="actions">
          <a className="secondary" href="/backup/hydradg.html">Open Static Fallback</a>
          <a className="secondary" href="/">Return to Live Demo</a>
        </div>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Interpretation rules</p>
        <h2>Keep diagnostics, outcomes and custody separate</h2>
        <ul>
          <li>Cloud Drift measures context-distribution change; it is not accuracy.</li>
          <li>ΔG* is a dimensionless information-state abstraction; it is not physical Gibbs free energy.</li>
          <li>Hit@K is retrieval hit rate, not end-to-end QA accuracy.</li>
          <li>Recall@K is an empirical retrieval outcome.</li>
          <li>HydraDB is the queryable projection; FCO/FCG is the canonical custody/provenance layer.</li>
        </ul>
      </section>
    </main>
  );
}
