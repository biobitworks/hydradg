import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { KNOWLEDGE_TERMS } from "@/lib/knowledgeLinks";
import { CONTEXT_SCORE_CONTRACT } from "@/lib/releaseTimepoints";

export default function KnowledgePage() {
  const knowledge = buildKnowledgeProjection();

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">HydraDG · linked terminology + custody</p>
          <h1>Every unfamiliar object resolves backward.</h1>
          <p className="lede">
            Project-specific terms are navigation objects, not decorative labels. Each declared term resolves to a definition,
            a deterministic website Knowledge FCO, a graph query, and an upstream source/receipt when one exists. The canonical
            project FCG has a hosted HydraDB readback receipt; website term FCOs remain an application metadata projection rather
            than a separate correctness claim.
          </p>
          <div className="actions">
            <a className="primary" href="/api/knowledge">Open knowledge API</a>
            <a className="secondary" href="/graph?q=KnowledgeAtom">Graph: KnowledgeAtom</a>
            <a className="secondary" href="/graph?q=SeedOfTruth">Graph: SeedOfTruth</a>
            <a className="secondary" href="/how-to">How to use</a>
          </div>
        </div>
      </header>

      <section className="metrics">
        <div className="metric"><span className="metricLabel">Knowledge terms</span><strong>{KNOWLEDGE_TERMS.length}</strong></div>
        <div className="metric"><span className="metricLabel">Knowledge root</span><strong className="mono small compact">{knowledge.root.object_sha256.slice(0, 18)}…</strong></div>
        <div className="metric"><span className="metricLabel">Hosted canonical FCG</span><strong className="small">READBACK VERIFIED</strong></div>
        <div className="metric"><span className="metricLabel">Claim boundary</span><strong className="small">navigation ≠ correctness</strong></div>
      </section>

      <section className="panel">
        <p className="eyebrow">Context scorer contract</p>
        <h2>Exact formulas used by the synthetic state fixture</h2>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr><th align="left">Quantity</th><th align="left">Declared contract</th></tr></thead>
          <tbody>
            {Object.entries(CONTEXT_SCORE_CONTRACT).map(([key, value]) => (
              <tr key={key}><td><strong>{key.replaceAll("_", " ")}</strong></td><td className="mono small">{value}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="small muted note">
          G* / ΔG* are application-defined dimensionless diagnostics. Enßlin &amp; Weig (2010) is design-rationale lineage for the information/free-energy analogy; HydraDG's exact formula is defined by the checked scorer above. Lin (1991) is the source lineage for Jensen-Shannon divergence / Cloud Drift.
        </p>
      </section>

      <section className="panel" style={{ background: "rgba(16, 185, 129, 0.05)", border: "2px solid #10b981" }}>
        <p className="eyebrow">Academic foundations</p>
        <div className="grid twoCol">
          <article>
            <h3>Enßlin &amp; Weig (2010)</h3>
            <p className="small muted"><em>Inference with minimal Gibbs free energy in information field theory.</em></p>
            <p className="small">Design-rationale lineage only; it does not define the exact HydraDG G* equation.</p>
            <div className="actions">
              <a className="secondary" href="https://doi.org/10.1103/PhysRevE.82.051112" target="_blank" rel="noreferrer">DOI ↗</a>
              <a className="secondary" href="/fco/fco:source:ensslin_weig_2010:3ed1f288ac8b3f48f4bf239f15a133fcdca36cd2ad8d3a9bb73a3f5a0be5349e">Source FCO</a>
            </div>
          </article>
          <article>
            <h3>Lin (1991)</h3>
            <p className="small muted"><em>Divergence measures based on the Shannon entropy.</em></p>
            <p className="small">Jensen-Shannon divergence source lineage for Cloud Drift = 100 × JSD.</p>
            <div className="actions"><a className="secondary" href="#jensen-shannon-divergence">Open JSD term</a></div>
          </article>
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
                    <a className="secondary" href={`/graph?q=${encodeURIComponent(item.graphQuery)}`}>Open in Graph</a>
                    <a className="secondary" href={`/fco/${encodeURIComponent(node.id)}`}>Knowledge FCO</a>
                    {item.external ? <a className="secondary" href={item.external} target="_blank" rel="noreferrer">Upstream source ↗</a> : null}
                  </div>
                </div>
                <p>{item.short}</p>
                <p className="small muted"><strong>How to:</strong> {item.howTo}</p>
                <p className="mono small compact">knowledge_fco={node.id}</p>
                <p className="mono small compact">object_sha256={node.object_sha256}</p>
                <p className="mono small compact">graph_query={item.graphQuery}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / RESOLUTION RULE</span>
        <h2 className="displayTitle">The UI is a projection, not custody truth.</h2>
        <div className="flow mono"><span>source / receipt</span><b>→</b><span>canonical custody</span><b>→</b><span>canonical FCG</span><b>→</b><span>hosted HydraDB readback</span><b>→</b><span>website Knowledge FCO</span></div>
        <p className="small muted note">Each website FCO has one canonical SHA-256 identity. A digest or graph path does not establish scientific correctness by itself.</p>
      </section>
    </main>
  );
}
