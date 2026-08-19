import Link from "next/link";
import { notFound } from "next/navigation";

import { buildDemoFixture } from "@/lib/demoFixture";
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

export default async function FcoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const decoded = decodeURIComponent(id);
  const { nodes, edges } = catalog();
  const node = nodes.find((candidate) => candidate.id === decoded);
  if (!node) notFound();

  const incoming = edges.filter((edge) => edge.target === node.id);
  const outgoing = edges.filter((edge) => edge.source === node.id);
  const byId = new Map(nodes.map((candidate) => [candidate.id, candidate]));

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">FCO inspector · content-addressed application object</p>
          <h1>{node.type}</h1>
          <p className="lede">Follow the incoming and outgoing FCG edges to reconstruct what this object depends on and what depends on it.</p>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">HASHED</span>
          <span className="pill pillMuted">IDENTITY ≠ CORRECTNESS</span>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber">01 / IDENTITY</span>
        <h2 className="displayTitle">The hash is the address.</h2>
        <div className="panel">
          <p className="eyebrow">FCO ID</p>
          <p className="mono compact">{node.id}</p>
          <p className="eyebrow" style={{ marginTop: 24 }}>Object SHA-256</p>
          <p className="mono compact">{node.object_sha256}</p>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / PAYLOAD</span>
        <h2 className="displayTitle">Declared object state.</h2>
        <pre className="result">{JSON.stringify(node.payload, null, 2)}</pre>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / FCG EDGES</span>
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
        <span className="sectionNumber">04 / BOUNDARY</span>
        <h2 className="displayTitle">A navigable route is not a verification stamp.</h2>
        <p className="sectionLead">
          This page recomputes deterministic fixture/site/website-knowledge FCO identities from application metadata. Website knowledge remains an application projection until an isolated HydraDB write/read receipt exists. This page does not establish live HydraDB Merkle commitment, author signature, independent replication, or universal truth of the payload.
        </p>
        <div className="actions">
          <Link className="secondary" href="/graph">4D FCG</Link>
          <Link className="secondary" href="/evidence">Evidence index</Link>
          <Link className="secondary" href="/knowledge">Knowledge matrix</Link>
        </div>
      </section>
    </main>
  );
}
