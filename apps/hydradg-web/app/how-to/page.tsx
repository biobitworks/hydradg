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
          <p className="eyebrow">2 · HydraLamp golden path</p>
          <h2>Reference → poison → denial → repair → restoration</h2>
          <p className="muted">Open HydraLamp, scrub the 46-event lane, and confirm poison stays quarantined until governed repair restores authorized state.</p>
          <a className="secondary" href="/hydralamp">Open HydraLamp</a>
        </article>
        <article className="panel">
          <p className="eyebrow">2B · Judge walkthrough</p>
          <h2>Reference → poison → antidote</h2>
          <p className="muted">Alternate judge path on the custody microscope UI.</p>
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

      <section className="computeSection" id="hosted-hydradb">
        <p className="eyebrow">Hosted path · GitHub → HydraDB → Vercel</p>
        <h2 className="displayTitle">Connect once. Query the indexed graph from the judge site.</h2>
        <p className="sectionLead">
          The hosted demo uses HydraDB as a server-side context service. The API key never reaches the browser. The canonical FCO/FCG remains the custody source of truth; hosted HydraDB is a queryable projection and connector-backed source index.
        </p>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">A · Connect source</p>
            <h2>GitHub repository → database hydradg</h2>
            <p className="muted">In HydraDB, create or select the database <code>hydradg</code>, add the GitHub connector, authorize the repository, and let indexing reach a terminal ready state. Record whether the connector uses the default collection or an explicit collection.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">B · Configure Vercel</p>
            <h2>Server-side HydraDB credentials</h2>
            <p className="muted">Set <code>HYDRA_DB_API_KEY</code>, <code>HYDRADB_DATABASE=hydradg</code>, and <code>HYDRADB_API_URL=https://api.hydradb.com</code>. Set <code>HYDRADB_COLLECTION</code> only if the connector/import was explicitly scoped to that collection.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">C · Prove readback</p>
            <h2>Query with graph context</h2>
            <p className="muted">The server calls HydraDB v2 with <code>API-Version: 2</code>, the same database/collection scope used at ingestion, and <code>graph_context=true</code>. A successful readback establishes hosted connectivity and returned context only—not scientific correctness.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">D · Compare local → hosted</p>
            <h2>Separate custody parity from service drift</h2>
            <p className="muted">For the same canonical FCG, FCO/edge/root identity and backend-independent Context Iceberg inputs should remain unchanged. Retrieval ranking, latency, returned graph paths, Hit@K and Recall@K are measured separately as hosted-service deltas.</p>
          </article>
        </div>
        <div className="actions">
          <a className="secondary" href="/api/graph/status">Check hosted HydraDB status</a>
        </div>
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

      <section className="computeSection" id="reconciliation-delta">
        <p className="eyebrow">Inspecting a reconciliation delta</p>
        <h2 className="displayTitle">Source → recompute → difference → claim.</h2>
        <p className="sectionLead">
          Review B frozen 46 events (<code>44e9d3dc…1690d</code>) were recomputed deterministically. The reconciliation delta is derived evidence — not a model vote and not an empirical experiment.
        </p>
        <div className="flow mono"><span>frozen events</span><b>→</b><span>reconcile_measurements.py</span><b>→</b><span>delta JSON</span><b>→</b><span>claim ceiling</span></div>
        <div className="actions">
          <a className="secondary" href="/evidence#reconciliation-delta">Evidence delta card</a>
          <a className="secondary" href="/demo/reconciliation-delta-use-case.json">Projection JSON</a>
          <a className="secondary" href="/api/hydralamp/reconciliation-delta">API projection</a>
        </div>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Interpretation rules</p>
        <h2>Keep diagnostics, outcomes and custody separate</h2>
        <ul>
          <li>Cloud Drift measures context-distribution change for declared synthetic distributions (T0–T2); it is not accuracy.</li>
          <li>ΔG* is a dimensionless information-state diagnostic; it is not physical Gibbs free energy.</li>
          <li>Timepoints T3–T5 currently have no declared probability distribution (`G_STAR_STATE = NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION`, `CLOUD_DRIFT_STATE = NOT_APPLICABLE_NO_DECLARED_DISTRIBUTION`).</li>
          <li>For T3 hosted migration: Canonical custody identity was preserved across migration, but runtime/project context changed because deployment location, database indexing, timestamps, and query service changed.</li>
          <li>Hit@K is retrieval hit rate, not end-to-end QA accuracy.</li>
          <li>Recall@K is an empirical retrieval outcome.</li>
          <li>HydraDB is the queryable projection; FCO/FCG is the canonical custody/provenance layer.</li>
        </ul>
      </section>
    </main>
  );
}
