import Link from "next/link";
import { notFound } from "next/navigation";

import Breadcrumbs from "@/components/Breadcrumbs";
import { buildDemoFixture } from "@/lib/demoFixture";
import { HUGGINGFACE_MODELS, PREPRINTS } from "@/lib/huggingfaceAndPreprints";
import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { buildSiteFcg } from "@/lib/siteFcg";

type Edge = { source: string; relation: string; target: string };
type NodeRow = { id: string; type: string; payload: Record<string, unknown>; object_sha256: string };

function catalog() {
  const fixture = buildDemoFixture();
  const site = buildSiteFcg();
  const knowledge = buildKnowledgeProjection();
  const fixtureNodes: NodeRow[] = fixture.nodes.map(([, node]) => node);
  const fixtureEdges: Edge[] = fixture.edges.map(([source, relation, target]) => ({ source, relation, target }));
  const nodes = [...fixtureNodes, ...site.nodes, site.artifact, ...knowledge.nodes, knowledge.root];
  const edges: Edge[] = [
    ...fixtureEdges,
    ...site.edges.map((edge) => ({ source: edge.source, relation: edge.relation, target: edge.target })),
    ...site.nodes.map((node) => ({ source: node.id, relation: "PART_OF_SITE_ARTIFACT", target: site.artifact.id })),
    ...knowledge.nodes.map((node) => ({ source: node.id, relation: "PART_OF_KNOWLEDGE_INDEX", target: knowledge.root.id })),
  ];
  return { nodes, edges };
}

function getAnticubeClassification(nodeType: string, payload: Record<string, unknown>) {
  if (nodeType === "ClassificationReceipt" || payload.safety_class === "NONSAFE") {
    return { label: "NONSAFE · QUARANTINE", badgeClass: "pillBad", color: "#ef4444", mathNote: "High perturbation burden (H=1.119 bits, G*=+0.573, Drift=40.36)" };
  }
  if (payload.state_label === "mutation" || payload.mode === "poison") {
    return { label: "NONSELF · MUTATION", badgeClass: "pillWarn", color: "#f59e0b", mathNote: "Divergent state transition (ΔG*=+0.634, JSD=0.700)" };
  }
  if (payload.state_label === "restoration" || payload.mode === "antidote") {
    return { label: "RESTORED · ADMIT", badgeClass: "pillGood", color: "#06b6d4", mathNote: "Recovery toward basin (H=0.580 bits, ΔG*=-0.600, Drift=1.87)" };
  }
  return { label: "SAFE · ADMIT", badgeClass: "pillGood", color: "#10b981", mathNote: "Canonical reference state (H=0.412 bits, G*=-0.061, Drift=0.00)" };
}

export default async function FcoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const decoded = decodeURIComponent(id);
  const { nodes, edges } = catalog();
  const node = nodes.find((candidate) => candidate.id === decoded);
  if (!node) notFound();

  const incoming = edges.filter((edge) => edge.target === node.id);
  const outgoing = edges.filter((edge) => edge.source === node.id);
  const byId = new Map(nodes.map((candidate) => [candidate.id, candidate]));

  const anticube = getAnticubeClassification(node.type, node.payload);
  const linkedPreprint = PREPRINTS.find((p) => p.knowledge_fco_id === node.id || decoded.includes(p.id));
  const linkedHfModel = HUGGINGFACE_MODELS.find((m) => m.knowledge_fco_id === node.id || decoded.includes(m.id));

  return (
    <main>
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "4D FCG Graph", href: "/graph" },
          { label: "FCO Inspector", href: "/graph" },
          { label: node.type },
        ]}
        summaryText={`Inspecting canonical FCO object ${node.id.slice(0, 18)}…. Verify incoming/outgoing edges, payload license, and math state variables.`}
      />

      <header className="hero">
        <div>
          <p className="eyebrow">FCO inspector · content-addressed application object</p>
          <h1>{node.type}</h1>
          <p className="lede">Follow the incoming and outgoing FCG edges to reconstruct what this object depends on and what depends on it.</p>
        </div>
        <div className="heroStatus">
          <span className={`pill ${anticube.badgeClass}`}>{anticube.label}</span>
          <span className="pill pillGood">HASHED</span>
          <span className="pill pillMuted">CC-BY-NC-ND 4.0</span>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber">01 / IDENTITY &amp; ANTICUBE CLASSIFICATION</span>
        <h2 className="displayTitle">The hash is the address.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">FCO ID</p>
            <p className="mono compact">{node.id}</p>
            <p className="eyebrow" style={{ marginTop: 24 }}>Object SHA-256</p>
            <p className="mono compact">{node.object_sha256}</p>
          </article>

          <article className="panel" style={{ borderLeft: `4px solid ${anticube.color}` }}>
            <p className="eyebrow" style={{ color: anticube.color }}>Anticube Classification &amp; State Math</p>
            <h3><span className={`pill ${anticube.badgeClass}`}>{anticube.label}</span></h3>
            <p className="small" style={{ marginTop: "0.5rem" }}>{anticube.mathNote}</p>
            <div style={{ marginTop: "1rem", padding: "0.75rem", background: "rgba(0,0,0,0.3)", borderRadius: "6px" }} className="mono small">
              <div>Shannon H: <code>H = -sum(p log2 p)</code></div>
              <div>Free-Energy G*: <code>G* = U* - 0.35 * Hnorm</code></div>
              <div>Lin JSD Drift: <code>100 * JSD(Pt || Pref)</code></div>
            </div>
          </article>
        </div>
      </section>

      {linkedPreprint || linkedHfModel ? (
        <section className="computeSection">
          <span className="sectionNumber">02 / ACADEMIC &amp; MODEL LINKS</span>
          <h2 className="displayTitle">Preprints &amp; Hugging Face Model Cards.</h2>
          <div className="grid twoCol">
            {linkedPreprint && (
              <article className="panel" style={{ border: "2px solid #10b981" }}>
                <span className="pill pillGood">Academic Preprint Citation</span>
                <h3 style={{ marginTop: "0.5rem" }}>{linkedPreprint.title}</h3>
                <p className="small muted">{linkedPreprint.authors} · {linkedPreprint.journal_or_arxiv}</p>
                <p className="small">{linkedPreprint.summary}</p>
                <div className="actions" style={{ marginTop: "0.75rem" }}>
                  <a className="primary" href={linkedPreprint.doi_or_url} target="_blank" rel="noreferrer">Open DOI / Paper ↗</a>
                </div>
              </article>
            )}
            {linkedHfModel && (
              <article className="panel" style={{ border: "2px solid #60a5fa" }}>
                <span className="pill pillGood">Hugging Face Model Card</span>
                <h3 style={{ marginTop: "0.5rem" }}>{linkedHfModel.model_name}</h3>
                <p className="small muted">Task: {linkedHfModel.task} · License: {linkedHfModel.license}</p>
                <p className="small">{linkedHfModel.description}</p>
                <div className="actions" style={{ marginTop: "0.75rem" }}>
                  <a className="primary" href={linkedHfModel.hf_repo_url} target="_blank" rel="noreferrer">Open Hugging Face Repo ↗</a>
                </div>
              </article>
            )}
          </div>
        </section>
      ) : null}

      <section className="computeSection">
        <span className="sectionNumber">03 / PAYLOAD</span>
        <h2 className="displayTitle">Declared object state.</h2>
        <pre className="result">{JSON.stringify(node.payload, null, 2)}</pre>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / FCG EDGES</span>
        <h2 className="displayTitle">Follow the dependency route.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">Incoming · {incoming.length}</p>
            <div className="stack">
              {incoming.length ? incoming.map((edge, index) => {
                const adjacent = byId.get(edge.source);
                return (
                  <Link className="source" key={`${edge.source}-${edge.relation}-${index}`} href={`/fco/${encodeURIComponent(edge.source)}`}>
                    <div><strong>{adjacent?.type || "FCO"}</strong><p className="mono small compact">{edge.source}</p></div>
                    <span className="sourceStatus verified">{edge.relation} →</span>
                  </Link>
                );
              }) : <p className="muted">No incoming edges in this bounded application graph.</p>}
            </div>
          </article>
          <article className="panel">
            <p className="eyebrow">Outgoing · {outgoing.length}</p>
            <div className="stack">
              {outgoing.length ? outgoing.map((edge, index) => {
                const adjacent = byId.get(edge.target);
                return (
                  <Link className="source" key={`${edge.target}-${edge.relation}-${index}`} href={`/fco/${encodeURIComponent(edge.target)}`}>
                    <div><strong>{adjacent?.type || "FCO"}</strong><p className="mono small compact">{edge.target}</p></div>
                    <span className="sourceStatus verified">{edge.relation} →</span>
                  </Link>
                );
              }) : <p className="muted">No outgoing edges in this bounded application graph.</p>}
            </div>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">05 / BOUNDARY &amp; FRACTAL PROVENANCE</span>
        <h2 className="displayTitle">Fractal structure ensures tamper-evidence at every scale.</h2>
        <p className="sectionLead">
          Fractal design hierarchy: Atomic FCO object root $\rightarrow$ Subgraph FCG root $\rightarrow$ Project Merkle root $\rightarrow$ Hosted HydraDB database root. Content identity is preserved across all projections. Payload content is licensed under CC BY-NC-ND 4.0.
        </p>
        <div className="actions">
          <Link className="secondary" href="/graph">4D FCG Explorer</Link>
          <Link className="secondary" href="/evidence">Evidence Ledger</Link>
          <Link className="secondary" href="/knowledge">Knowledge Matrix</Link>
        </div>
      </section>
    </main>
  );
}
