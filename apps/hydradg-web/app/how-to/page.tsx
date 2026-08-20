import KnowledgeTermLink from "@/components/KnowledgeTermLink";

export default function HowToPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">How to use HydraDG</p>
          <h1>One path from context change to custody.</h1>
          <p className="lede">Follow the numbered path. Every public step is read-only against the judge release; each canonical <KnowledgeTermLink slug="fco">FCO</KnowledgeTermLink> resolves to one SHA-256 identity and every unfamiliar term can resolve through the terminology matrix.</p>
          <div className="actions"><a className="secondary" href="/api/release">Check deployed version + release FCO</a><a className="secondary" href="/knowledge">Terminology matrix</a><a className="secondary" href="/track-fit">Final: Why Graph?</a></div>
        </div>
      </header>

      <section className="grid twoCol">
        <article className="panel"><p className="eyebrow">1 · Overview</p><h2>Read the <KnowledgeTermLink slug="context-iceberg">Context Iceberg</KnowledgeTermLink></h2><p className="muted">Violet is reference/normal, orange is poison/mutation, blue is antidote/restoration. Read <KnowledgeTermLink slug="delta-g-star">ΔG*</KnowledgeTermLink> and <KnowledgeTermLink slug="cloud-drift">Cloud Drift</KnowledgeTermLink> separately from Hit@K and Recall@K.</p><a className="secondary" href="/">Open Overview</a></article>
        <article className="panel"><p className="eyebrow">2 · Judge Demo</p><h2>Reference → poison → antidote</h2><p className="muted">Use the walkthrough table to confirm exact distributions, G*, ΔG* and Cloud Drift for the synthetic T0–T2 fixture.</p><a className="secondary" href="/judge">Start Judge Walkthrough</a></article>
        <article className="panel"><p className="eyebrow">3 · Graph</p><h2>Click one canonical FCO</h2><p className="muted">The selected-node panel now shows distribution, H/Hnorm, U*, G*, ΔG*, Cloud Drift, TV mutation distance and restoration gain. The numbers inherit violet/orange/blue from their Reference/Poison/Antidote state classification.</p><a className="secondary" href="/graph">Open 4D Graph</a></article>
        <article className="panel"><p className="eyebrow">4 · Anticube</p><h2>Check classification without guessing</h2><p className="muted"><KnowledgeTermLink slug="anticube">Anticube</KnowledgeTermLink> is a separate receipt-based lane. If a ClassificationReceipt is not executed, the inspector displays UNKNOWN / NOT_EXECUTED; poison color is never automatically treated as NONSAFE.</p><div className="actions"><a className="secondary" href="/knowledge#anticube">KB: Anticube</a><a className="secondary" href="/graph?q=ClassificationReceipt">Classification receipts</a></div></article>
        <article className="panel"><p className="eyebrow">5 · Atom</p><h2>Resolve a <KnowledgeTermLink slug="knowledge-atom">KnowledgeAtom</KnowledgeTermLink></h2><p className="muted">Start from exact source/evidence, follow DERIVED_FROM into the atom, and keep semantic interpretation distinct from source bytes.</p><div className="actions"><a className="secondary" href="/knowledge#knowledge-atom">KB: KnowledgeAtom</a><a className="secondary" href="/graph?q=KnowledgeAtom">Graph atoms</a></div></article>
        <article className="panel"><p className="eyebrow">6 · Seed</p><h2>Resolve a <KnowledgeTermLink slug="seed-of-truth">SeedOfTruth</KnowledgeTermLink></h2><p className="muted">Follow SUPPORTED_BY edges back to admitted atoms/evidence and inspect the claim ceiling before reuse.</p><div className="actions"><a className="secondary" href="/knowledge#seed-of-truth">KB: SeedOfTruth</a><a className="secondary" href="/graph?q=SeedOfTruth">Graph seeds</a></div></article>
        <article className="panel"><p className="eyebrow">7 · Results</p><h2>Read the empirical outcome</h2><p className="muted">Inspect cases, graph scale, Hit@K, Recall@K and the retained null/negative result under its declared <KnowledgeTermLink slug="claim-ceiling">claim ceiling</KnowledgeTermLink>.</p><a className="secondary" href="/track03">Open Track 03 Results</a></article>
        <article className="panel"><p className="eyebrow">8 · Knowledge</p><h2>Resolve project terminology</h2><p className="muted">Use the governed Knowledge Base for FCO, FCG, Context Iceberg, G*, ΔG*, Cloud Drift, total-variation mutation distance, restoration gain and Anticube.</p><a className="secondary" href="/knowledge">Open Knowledge Base</a></article>
        <article className="panel"><p className="eyebrow">9 · Release</p><h2>Check version and custody state</h2><p className="muted">The global release stamp shows the deployed Git SHA and WebsiteRelease FCO hash. Signature and Merkle states remain separate.</p><div className="actions"><a className="secondary" href="/api/release">Release JSON</a><a className="secondary" href="/evolution">Version history</a><a className="secondary" href="/eligibility">Eligibility</a></div></article>
        <article className="panel" style={{ border: "2px solid rgba(246,200,95,0.45)" }}><p className="eyebrow">10 · Final judge step</p><h2>Why does this need a graph?</h2><p className="muted">Finish with the four HydraDB judging signals, Track 01/02/03 fit, real project calculations, worked graph examples and example code.</p><a className="primary" href="/track-fit">Open Why Graph? + math</a></article>
      </section>

      <section className="computeSection" id="hosted-hydradb">
        <p className="eyebrow">Hosted path · GitHub → HydraDB → Vercel</p>
        <h2 className="displayTitle">Connect once. Query the indexed graph from the judge site.</h2>
        <p className="sectionLead">The hosted demo uses <KnowledgeTermLink slug="hydradb">HydraDB</KnowledgeTermLink> as a server-side context service. Credentials never reach the browser. Canonical FCO/FCG identity remains backend-independent.</p>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">A · Source</p><h2>GitHub repository → database hydradg</h2><p className="muted">The GitHub connector indexes repository data in the hosted <code>hydradg</code> database. The historical migration receipt records collection <code>default</code>; current live collection discovery reports <code>hydradg</code>. Historical receipt metadata is retained rather than silently rewritten.</p></article>
          <article className="panel"><p className="eyebrow">B · Vercel</p><h2>Server-side configuration</h2><p className="muted">Production uses <code>HYDRA_DB_API_KEY</code>, <code>HYDRADB_DATABASE=hydradg</code>, and the official v2 API endpoint. Collection scope is discovered rather than guessed.</p></article>
          <article className="panel"><p className="eyebrow">C · Query</p><h2>Graph context + connector apps</h2><p className="muted">The v2 query route uses <code>graph_context=true</code> and <code>query_apps=true</code> by default so connector-backed GitHub context can be returned alongside graph context.</p></article>
          <article className="panel"><p className="eyebrow">D · Verify</p><h2>Separate parity from service drift</h2><p className="muted">Canonical FCO/edge/content roots are compared independently from retrieval ranking, latency, graph paths, Hit@K and Recall@K.</p></article>
        </div>
        <div className="actions"><a className="secondary" href="/api/graph/status">Live HydraDB status</a><a className="secondary" href="/api/hydradb-v2/collections">Collections readback</a><a className="secondary" href="/track-fit">Show migration math</a></div>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Interpretation rules</p>
        <ul>
          <li><a href="/knowledge#cloud-drift">Cloud Drift</a> = 100 × base-2 Jensen-Shannon divergence from the frozen reference distribution.</li>
          <li><a href="/knowledge#g-star">G*</a> = U* - 0.35 × normalized Shannon entropy for the declared synthetic fixture.</li>
          <li><a href="/knowledge#mutation-distance">Mutation distance</a> and <a href="/knowledge#restoration-gain">restoration gain</a> use the separate total-variation lane.</li>
          <li>G*/ΔG* are dimensionless information-state abstractions, not physical Gibbs free energy.</li>
          <li>T3–T5 do not receive fabricated T0–T2 scalars; their migration/experiment/release measurements are displayed separately.</li>
          <li><a href="/knowledge#anticube">Anticube</a> classification is independent of state color and remains UNKNOWN when no executed receipt supports a quadrant.</li>
          <li>HydraDB is a queryable projection/context substrate; <a href="/knowledge#fco">FCO</a>/<a href="/knowledge#fcg">FCG</a> is the canonical custody/provenance layer.</li>
        </ul>
      </section>
    </main>
  );
}
