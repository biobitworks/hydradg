import Breadcrumbs from "@/components/Breadcrumbs";
import { AUTHOR_AUTHORITY, HACKATHON_AND_COMMUNITY_PROJECTS, HUGGINGFACE_MODELS, PREPRINTS } from "@/lib/huggingfaceAndPreprints";
import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { KNOWLEDGE_TERMS } from "@/lib/knowledgeLinks";

export default function KnowledgePage() {
  const knowledge = buildKnowledgeProjection();

  return (
    <main>
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Knowledge Base" },
        ]}
        summaryText="Resolve unfamiliar terms, academic preprints, versioned DOIs, Hugging Face models, and hackathon demos backward to their underlying Knowledge Atom FCOs."
      />

      <header className="hero">
        <div>
          <p className="eyebrow">HydraDG · linked terminology + custody</p>
          <h1>Every unfamiliar object should resolve backward.</h1>
          <p className="lede">
            Project-specific terms are navigation objects, not decorative labels. Each declared term resolves to a definition,
            operational meaning, graph search, deterministic website Knowledge FCO, and upstream source/receipt when one exists.
          </p>
          <div className="actions">
            <a className="primary" href="/api/knowledge">Open Knowledge API</a>
            <a className="secondary" href="https://huggingface.co/biobitworks" target="_blank" rel="noreferrer">Hugging Face Org ↗</a>
            <a className="secondary" href={AUTHOR_AUTHORITY.orcid} target="_blank" rel="noreferrer">ORCID ↗</a>
          </div>
        </div>
      </header>

      <section className="metrics">
        <div className="metric"><span className="metricLabel">Word / Token Atoms</span><strong>28,458,677</strong><span className="small muted">Level 0 field leaf hashes</span></div>
        <div className="metric"><span className="metricLabel">Sentence / Record Atoms</span><strong>3,214,299</strong><span className="small muted">Level 1 Merkle roots</span></div>
        <div className="metric"><span className="metricLabel">Preprints &amp; DOIs</span><strong>{PREPRINTS.length}</strong><span className="small muted">Versioned publications</span></div>
        <div className="metric"><span className="metricLabel">Container FCOs</span><strong>503</strong><span className="small muted">Top-level FCG wrappers</span></div>
      </section>

      {/* Preprints & Hugging Face Models Section */}
      <section className="computeSection">
        <span className="sectionNumber">01 / PREPRINTS, DOIS &amp; HUGGING FACE MODELS</span>
        <h2 className="displayTitle">Canonical publication DOIs (with versions) &amp; Hugging Face weights.</h2>
        <div className="grid twoCol">
          {PREPRINTS.map((paper) => (
            <article className="panel" key={paper.id} style={{ border: "1px solid rgba(255,255,255,0.1)" }}>
              <div className="panelHead">
                <div>
                  <span className="pill pillGood" style={{ marginBottom: "0.25rem" }}>Publication Preprint</span>
                  {paper.version_note && <span className="pill pillMuted" style={{ marginLeft: "0.5rem" }}>{paper.version_note}</span>}
                  <h3 style={{ marginTop: "0.25rem" }}>{paper.title}</h3>
                </div>
              </div>
              <p className="small muted">{paper.authors} · {paper.journal_or_arxiv}</p>
              <p className="small">{paper.summary}</p>
              <p className="mono small compact" style={{ overflowWrap: "anywhere" }}>knowledge_fco={paper.knowledge_fco_id}</p>
              <div className="actions" style={{ marginTop: "0.75rem" }}>
                <a className="primary" href={paper.doi_or_url} target="_blank" rel="noreferrer">Open DOI ({paper.doi_or_url.replace("https://doi.org/", "")}) ↗</a>
                <a className="secondary" href={`/fco/${encodeURIComponent(paper.knowledge_fco_id)}`}>Inspect Knowledge Atom FCO ↗</a>
              </div>
            </article>
          ))}

          {HUGGINGFACE_MODELS.map((model) => (
            <article className="panel" key={model.id} style={{ border: "1px solid rgba(96, 165, 250, 0.3)", background: "rgba(96, 165, 250, 0.03)" }}>
              <div className="panelHead">
                <div>
                  <span className="pill pillGood" style={{ marginBottom: "0.25rem" }}>Hugging Face Model</span>
                  <h3 style={{ marginTop: "0.25rem" }}>{model.model_name}</h3>
                </div>
              </div>
              <p className="small muted">Task: {model.task} · License: {model.license}</p>
              <p className="small">{model.description}</p>
              <p className="mono small compact" style={{ overflowWrap: "anywhere" }}>knowledge_fco={model.knowledge_fco_id}</p>
              <div className="actions" style={{ marginTop: "0.75rem" }}>
                <a className="primary" href={model.hf_repo_url} target="_blank" rel="noreferrer">Open Hugging Face Repo ↗</a>
                <a className="secondary" href={`/fco/${encodeURIComponent(model.knowledge_fco_id)}`}>Inspect Knowledge Atom FCO ↗</a>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Hackathon Demos & Community Projects Section */}
      <section className="computeSection">
        <span className="sectionNumber">02 / HACKATHON DEMOS &amp; COMMUNITY PROJECTS</span>
        <h2 className="displayTitle">Live demo surfaces &amp; project links.</h2>
        <div className="grid twoCol">
          {HACKATHON_AND_COMMUNITY_PROJECTS.map((proj) => (
            <article className="panel" key={proj.url} style={{ border: "1px solid rgba(255,255,255,0.08)" }}>
              <span className="pill pillMuted">{proj.category}</span>
              <h3 style={{ marginTop: "0.5rem" }}>{proj.name}</h3>
              <p className="small muted">{proj.description}</p>
              <div className="actions" style={{ marginTop: "0.75rem" }}>
                <a className="secondary" href={proj.url} target="_blank" rel="noreferrer">Open Site ↗</a>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="panel" style={{ background: "rgba(16, 185, 129, 0.05)", border: "2px solid #10b981", borderRadius: "10px", padding: "1.25rem", margin: "1.5rem 0" }}>
        <p className="eyebrow" style={{ color: "#10b981", fontWeight: "bold" }}>Academic Foundations &amp; Citations (Video Demo 1:55–2:20)</p>
        <h2>G* Free-Energy &amp; Jensen-Shannon Cloud Drift Lineage</h2>
        
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
        <span className="sectionNumber">03 / TERMINOLOGY MATRIX</span>
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
        <span className="sectionNumber">04 / RESOLUTION RULE</span>
        <h2 className="displayTitle">The UI is a projection, not custody truth.</h2>
        <div className="flow mono"><span>source / receipt</span><b>→</b><span>canonical custody</span><b>→</b><span>canonical FCG</span><b>→</b><span>HydraDB projection</span><b>→</b><span>website Knowledge FCO</span></div>
        <p className="small muted note">The website FCO projection is deterministic application metadata. HydraDB projection is not claimed until an isolated post-Daisy write/read receipt exists. A digest or graph path does not establish scientific correctness by itself.</p>
      </section>
    </main>
  );
}
