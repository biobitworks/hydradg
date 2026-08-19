import { KNOWLEDGE_TERMS } from "@/lib/knowledgeLinks";

export default function KnowledgePage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">HydraDG · linked terminology</p>
          <h1>Every unfamiliar object should resolve backward.</h1>
          <p className="lede">Project-specific terms are navigation objects, not decorative labels. Each declared term should resolve to a definition, operational meaning, graph search and upstream source/receipt when one exists.</p>
        </div>
      </header>

      <section className="metrics">
        <div className="metric"><span className="metricLabel">Knowledge terms</span><strong>{KNOWLEDGE_TERMS.length}</strong></div>
        <div className="metric"><span className="metricLabel">Resolution</span><strong className="small">term → FCG → source</strong></div>
        <div className="metric"><span className="metricLabel">Hash rule</span><strong className="small">identity ≠ correctness</strong></div>
        <div className="metric"><span className="metricLabel">Coverage</span><strong className="small">declared project-term gate</strong></div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / TERMINOLOGY MATRIX</span>
        <h2 className="displayTitle">Term → how to → FCG → source.</h2>
        <div className="stack">
          {KNOWLEDGE_TERMS.map((item, index) => (
            <article className="panel" id={item.slug} key={item.slug}>
              <div className="panelHead"><div><p className="eyebrow">{String(index + 1).padStart(2, "0")}</p><h3>{item.term}</h3></div><div className="actions"><a className="secondary" href={`/graph?q=${encodeURIComponent(item.graphQuery)}`}>Open in Graph Explorer</a>{item.external ? <a className="secondary" href={item.external} target="_blank" rel="noreferrer">Upstream source ↗</a> : null}</div></div>
              <p>{item.short}</p>
              <p className="small muted"><strong>How to:</strong> {item.howTo}</p>
              <p className="mono small compact">graph_query={item.graphQuery}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="computeSection"><span className="sectionNumber">02 / RESOLUTION RULE</span><h2 className="displayTitle">Hashes should be navigable, not isolated.</h2><div className="flow mono"><span>SHA-256 / term</span><b>→</b><span>knowledge object</span><b>→</b><span>FCO</span><b>→</b><span>FCG edge</span><b>→</b><span>source / receipt</span></div><p className="small muted note">The graph route supplies lineage and declared dependency context. Neither a digest nor a graph path establishes scientific correctness on its own.</p></section>
    </main>
  );
}
