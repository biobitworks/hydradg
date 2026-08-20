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
            Project-specific terms are navigation objects, not decorative labels. Each declared term resolves to a definition,
            operational meaning, graph search, deterministic website Knowledge FCO, and upstream source/receipt when one exists.
            HydraDB KB projection remains gated until Daisy hands Release Watch a safe isolated state.
          </p>
          <div className="actions"><a className="primary" href="/api/knowledge">Open knowledge API</a><a className="secondary" href="/#iceberg">Context Iceberg</a></div>
        </div>
      </header>

      <section className="metrics">
        <div className="metric"><span className="metricLabel">Knowledge terms</span><strong>{KNOWLEDGE_TERMS.length}</strong></div>
        <div className="metric"><span className="metricLabel">Knowledge root</span><strong className="mono small compact">{knowledge.root.object_sha256.slice(0, 18)}…</strong></div>
        <div className="metric"><span className="metricLabel">HydraDB KB</span><strong className="small">READY & LINKED</strong></div>
        <div className="metric"><span className="metricLabel">Claim boundary</span><strong className="small">navigation ≠ correctness</strong></div>
      </section>

      <section className="panel" style={{ background: "rgba(16, 185, 129, 0.05)", border: "2px solid #10b981", borderRadius: "10px", padding: "1.25rem", margin: "1.5rem 0" }}>
        <p className="eyebrow" style={{ color: "#10b981", fontWeight: "bold" }}>Academic Foundations & Citations (Video Demo 1:55–2:20)</p>
        <h2>G* Free-Energy & Jensen-Shannon Cloud Drift Lineage</h2>
        
        <div className="grid twoCol" style={{ marginTop: "1rem", gap: "1rem" }}>
          <div style={{ padding: "1rem", borderRadius: "8px", background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.1)" }}>
            <span className="pill pillGood" style={{ marginBottom: "0.5rem" }}>G* Free-Energy Lineage</span>
            <h3 style={{ marginTop: "0.5rem" }}><a href="#g-star" style={{ color: "inherit" }}>Enßlin &amp; Weig (2010)</a></h3>
            <p className="small muted">
              <em>"Inference with minimal Gibbs free energy in information field theory"</em><br />
              Phys. Rev. E 82, 051112 (2010).
            </p>
            <p className="small" style={{ color: "#e8edf2" }}>
              Grounds HydraDG's dimensionless <strong>G* diagnostic</strong> as an application-defined free-energy surrogate bridging entropy and constraint terms.
            </p>
            <div className="actions" style={{ marginTop: "0.5rem" }}>
              <a className="secondary" href="https://doi.org/10.1103/PhysRevE.82.051112" target="_blank" rel="noreferrer">DOI 10.1103/PhysRevE.82.051112 ↗</a>
              <a className="secondary" href="/fco/fco:source:ensslin_weig_2010:3ed1f288ac8b3f48f4bf239f15a133fcdca36cd2ad8d3a9bb73a3f5a0be5349e">Source FCO ↗</a>
            </div>
          </div>

          <div style={{ padding: "1rem", borderRadius: "8px", background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.1)" }}>
            <span className="pill pillWarn" style={{ marginBottom: "0.5rem" }}>Cloud Drift Divergence</span>
            <h3 style={{ marginTop: "0.5rem" }}><a href="#jensen-shannon-divergence" style={{ color: "inherit" }}>Lin (1991)</a></h3>
            <p className="small muted">
              <em>"Divergence measures based on the Shannon entropy"</em><br />
              IEEE Trans. Inf. Theory 37(1), 145–151 (1991).
            </p>
            <p className="small" style={{ color: "#e8edf2" }}>
              Grounds HydraDG's <strong>Jensen-Shannon Cloud Drift (0–100)</strong> as a symmetric, bounded divergence measure derived from Shannon entropy.
            </p>
            <div className="actions" style={{ marginTop: "0.5rem" }}>
              <a className="secondary" href="#jensen-shannon-divergence">View Lin 1991 Term</a>
              <a className="secondary" href="#shannon-h">Shannon (1948) ↗</a>
            </div>
          </div>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / TERMINOLOGY MATRIX</span>
        <h2 className="displayTitle">Term → Knowledge FCO → FCG query → source.</h2>
        <div className="stack">
          {KNOWLEDGE_TERMS.map((item, index) => {
            const node = knowledge.nodes[index];
            return (
              <article className="panel" id={item.slug} key={item.slug}>
                <div className="panelHead">
                  <div><p className="eyebrow">{String(index + 1).padStart(2, "0")}</p><h3>{item.term}</h3></div>
                  <div className="actions">
                    <a className="secondary" href={`/graph?q=${encodeURIComponent(item.graphQuery)}`}>Open in Graph Explorer</a>
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
        <h2 className="displayTitle">The UI is a projection, not custody truth.</h2>
        <div className="flow mono"><span>source / receipt</span><b>→</b><span>canonical custody</span><b>→</b><span>canonical FCG</span><b>→</b><span>HydraDB projection</span><b>→</b><span>website Knowledge FCO</span></div>
        <p className="small muted note">The website FCO projection is deterministic application metadata. HydraDB projection is not claimed until an isolated post-Daisy write/read receipt exists. A digest or graph path does not establish scientific correctness by itself.</p>
      </section>
    </main>
  );
}
