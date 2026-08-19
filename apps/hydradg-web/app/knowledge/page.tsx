import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { KNOWLEDGE_TERMS } from "@/lib/knowledgeLinks";

export default function KnowledgePage() {
  const knowledge = buildKnowledgeProjection();

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">HydraDG · linked terminology + custody</p>
          <h1>Every unfamiliar object should resolve backward.</h1>
          <p className="lede">
            Project-specific terms are navigation objects, not decorative labels. Each declared term resolves to a
            definition, operational meaning, graph search, content-addressed website knowledge FCO and upstream
            source/receipt when one exists. HydraDB projection remains explicitly gated until a stable release handoff.
          </p>
          <div className="actions">
            <a className="primary" href="/api/knowledge">Open knowledge API</a>
            <a className="secondary" href="/graph">Open Context Iceberg graph</a>
          </div>
        </div>
      </header>

      <section className="metrics">
        <div className="metric"><span className="metricLabel">Knowledge terms</span><strong>{KNOWLEDGE_TERMS.length}</strong></div>
        <div className="metric"><span className="metricLabel">Knowledge root</span><strong className="mono small compact">{knowledge.root.object_sha256.slice(0, 18)}…</strong></div>
        <div className="metric"><span className="metricLabel">HydraDB KB projection</span><strong className="small">PENDING STABLE HANDOFF</strong></div>
        <div className="metric"><span className="metricLabel">Claim ceiling</span><strong className="small">navigation ≠ correctness</strong></div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / TERMINOLOGY MATRIX</span>
        <h2 className="displayTitle">Term → knowledge FCO → FCG query → source.</h2>
        <div className="stack">
          {KNOWLEDGE_TERMS.map((item, index) => {
            const node = knowledge.nodes[index];
            return (
              <article className="panel" id={item.slug} key={item.slug}>
                <div className="panelHead">
                  <div><p className="eyebrow">{String(index + 1).padStart(2, "0")}</p><h3>{item.term}</h3></div>
                  <div className="actions">
                    <a className="secondary" href={`/graph?q=${encodeURIComponent(item.graphQuery)}`}>Open in Context Iceberg</a>
                    <a className="secondary" href={`/fco/${encodeURIComponent(node.id)}`}>Knowledge FCO</a>
                    {item.external ? <a className="secondary" href={item.external} target="_blank" rel="noreferrer">Upstream source ↗</a> : null}
                  </div>
                </div>
                <p>{item.short}</p>
                <p className="small muted"><strong>How to:</strong> {item.howTo}</p>
                <p className="mono small compact">knowledge_fco={node.id}</p>
                <p className="mono small compact">graph_query={item.graphQuery}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / RESOLUTION RULE</span>
        <h2 className="displayTitle">The UI is a projection, not the source of truth.</h2>
        <div className="flow mono">
          <span>source / receipt</span><b>→</b><span>canonical custody</span><b>→</b><span>canonical FCG</span><b>→</b><span>HydraDB projection</span><b>→</b><span>website knowledge FCO</span>
        </div>
        <p className="small muted note">
          Current website term FCOs are deterministic application-level projections. The API records HydraDB KB projection as PENDING until the stable scientific/release handoff permits an isolated projection. A digest or graph path does not establish scientific correctness by itself.
        </p>
      </section>
    </main>
  );
}
