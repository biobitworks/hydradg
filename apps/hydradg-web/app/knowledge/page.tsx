import { KNOWLEDGE_TERMS } from "@/lib/knowledgeLinks";

export default function KnowledgePage() {
  return (
    <main>
      <nav>
        <a href="/">MVP</a>
        <a href="/judge">Judge Lab</a>
        <a href="/graph">4D FCG</a>
        <a href="/knowledge">Knowledge</a>
        <a href="/evidence">Evidence</a>
      </nav>

      <header className="hero">
        <div>
          <p className="eyebrow">HydraDG · linked terminology</p>
          <h1>Everything resolves back to the graph.</h1>
          <p className="lede">
            Terms are not decorative labels. Each term links to a how-to definition, a graph search, and an
            upstream source when one exists. FCO IDs and hashes remain identifiers rather than truth claims.
          </p>
        </div>
      </header>

      <section className="metrics">
        <div className="metric"><span className="metricLabel">Terms</span><strong>{KNOWLEDGE_TERMS.length}</strong></div>
        <div className="metric"><span className="metricLabel">Graph surface</span><strong>4D + time</strong></div>
        <div className="metric"><span className="metricLabel">Source rule</span><strong className="small">hash → object → dependency → source</strong></div>
        <div className="metric"><span className="metricLabel">Claim rule</span><strong className="small">identity ≠ correctness</strong></div>
      </section>

      <section className="panel">
        <p className="eyebrow">Terminology matrix</p>
        <h2>Term → how to → FCG → source</h2>
        <div className="stack">
          {KNOWLEDGE_TERMS.map((item, index) => (
            <article className="panel" id={item.slug} key={item.slug}>
              <div className="panelHead">
                <div>
                  <p className="eyebrow">{String(index + 1).padStart(2, "0")}</p>
                  <h3>{item.term}</h3>
                </div>
                <div className="actions">
                  <a className="secondary" href={`/graph?q=${encodeURIComponent(item.graphQuery)}`}>Open in 4D FCG</a>
                  {item.external ? <a className="secondary" href={item.external} target="_blank" rel="noreferrer">Upstream source ↗</a> : null}
                </div>
              </div>
              <p>{item.short}</p>
              <p className="small muted"><strong>How to:</strong> {item.howTo}</p>
              <p className="mono small compact">graph_query={item.graphQuery}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">FCG resolution rule</p>
        <h2>Hashes should be navigable, not isolated.</h2>
        <div className="flow mono">
          <span>SHA-256</span><b>→</b><span>FCO</span><b>→</b><span>FCG edge</span><b>→</b><span>source/version</span><b>→</b><span>derived claim/artifact</span>
        </div>
        <p className="muted">
          A digest establishes byte/object identity only. The graph supplies the route to the source, transformation,
          evidence class, claim ceiling, and later artifact that depends on it.
        </p>
      </section>
    </main>
  );
}
