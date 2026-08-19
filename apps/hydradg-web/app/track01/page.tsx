import Link from "next/link";

import { RELEASE_STATUS } from "@/lib/releaseStatus";

const datasets = [
  {
    name: "EnterpriseRAG-Bench",
    source: "onyx-dot-app/EnterpriseRAG-Bench",
    license: "MIT",
    role: "Primary Track 01 benchmark",
    state: RELEASE_STATUS.datasets.enterprise_rag_bench.state,
  },
  {
    name: "HERB",
    source: "Salesforce/HERB",
    license: "CC-BY-NC-4.0",
    role: "Independent heterogeneous enterprise stress lane",
    state: RELEASE_STATUS.datasets.herb.state,
  },
] as const;

export default function Track01Page() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Track 01 · Enterprise Context + Ontology</p>
          <h1>HydraOntology</h1>
          <p className="lede">
            Turn enterprise records into an explicit ontology where aliases, provenance, conflicting claims and current state are traversable instead of flattened into one similarity index.
          </p>
          <div className="actions">
            <Link className="primary" href="/knowledge">Open graph terminology</Link>
            <Link className="secondary" href="/graph">Open Graph Explorer</Link>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">CORE DATA DOWNLOADED + HASHED</span>
          <span className="pill pillWarn">REAL INGESTION / BENCHMARK PENDING</span>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber">01 / ONTOLOGY</span>
        <h2 className="displayTitle">Identity and current state are edges.</h2>
        <div className="fcgRail">
          {[["01", "Source"],["02", "EntityMention"],["03", "RESOLVES_TO"],["04", "Claim"],["05", "Current state"]].map(([n, label]) => <div className="fcgStep" key={label}><span className="sectionNumber">{n}</span><strong>{label}</strong></div>)}
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / DATASETS</span>
        <h2 className="displayTitle">Downloaded bytes are the source object, not the result.</h2>
        <div className="tableWrap">
          <table>
            <thead><tr><th>Dataset</th><th>HF repository</th><th>License</th><th>Role</th><th>State</th></tr></thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr key={dataset.name}><td>{dataset.name}</td><td className="mono small">{dataset.source}</td><td>{dataset.license}</td><td>{dataset.role}</td><td>{dataset.state}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small muted note">The local acquisition receipts establish the downloaded revision/manifest identities. They do not establish Track 01 ontology or retrieval performance. Full atomization, HydraDB projection and real-data evaluation remain separate gates.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / MECHANICAL TEST</span>
        <h2 className="displayTitle">Split an identity. Measure the damage. Merge it back.</h2>
        <div className="grid threeCol">
          <article className="panel"><p className="eyebrow">Reference</p><h2>One canonical entity.</h2><p className="muted">Multiple aliases resolve to one entity with traceable source evidence.</p></article>
          <article className="panel"><p className="eyebrow">Poison</p><h2>Alias split.</h2><p className="muted">Break one RESOLVES_TO relationship and measure downstream evidence-set change.</p></article>
          <article className="panel"><p className="eyebrow">Antidote</p><h2>Restore the merge.</h2><p className="muted">Reinstate the supported identity edge and test whether the expected evidence set returns.</p></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / TOTAL ATOMIZATION</span>
        <h2 className="displayTitle">Every record must remain traceable to the exact downloaded file.</h2>
        <div className="flow mono"><span>downloaded bytes</span><b>→</b><span>SeedGraph intake</span><b>→</b><span>record FCOs</span><b>→</b><span>FCG</span><b>→</b><span>HydraDB</span></div>
        <p className="small muted note">The adapter is implemented; the full EnterpriseRAG/HERB corpus atomization/projection receipt is still execution-gated.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">05 / RELEASE BOUNDARY</span>
        <h2 className="displayTitle">HERB remains license-bounded.</h2>
        <p className="sectionLead">HERB is recorded upstream as CC-BY-NC-4.0. Dataset bytes stay outside the public HydraDG repository by default. The release can expose source identifiers, manifests, adapters and bounded receipts rather than redistributing the dataset.</p>
      </section>
    </main>
  );
}
