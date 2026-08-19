import Link from "next/link";

import { buildSiteFcg } from "@/lib/siteFcg";

const tracks = [
  {
    n: "01",
    href: "/track01",
    title: "Identity",
    internal: "HydraOntology",
    subtitle: "Enterprise context + ontology",
    body: "When aliases or conflicting records resolve differently, what downstream evidence changes?",
    status: "DATA DOWNLOADED · REAL INGESTION PENDING",
  },
  {
    n: "02",
    href: "/track02",
    title: "Blast radius",
    internal: "HydraBlast",
    subtitle: "Repos, dependencies + code as graphs",
    body: "Given a vulnerable dependency, what services are exposed and does a patch remove every affected path?",
    status: "SYNTHETIC CANARY IMPLEMENTED",
  },
  {
    n: "03",
    href: "/track03",
    title: "Memory",
    internal: "HydraMemory",
    subtitle: "Memory + context retrieval",
    body: "After updates and contradictions, which fact is current and which source/session supports it?",
    status: "FULL500 EXECUTED",
  },
] as const;

export default function Home() {
  const site = buildSiteFcg();

  return (
    <main>
      <header className="hero" id="top">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · graph state with evidence paths</p>
          <h1>See what changed. Trace why. Test the repair.</h1>
          <p className="lede">
            HydraDG uses HydraDB to represent changing memory, identity and dependency state as typed graph relationships.
            FCO/FCG preserves the source and transformation route behind each derived state so a change can be inspected instead of silently overwritten.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Try the guided demo</Link>
            <Link className="secondary" href="/demo">Submission overview</Link>
            <Link className="secondary" href="/evidence">See the results</Link>
          </div>
        </div>
        <div className="heroStatus" aria-label="Project status">
          <span className="pill pillGood">local HydraDB · executed</span>
          <span className="pill pillGood">LongMemEval · 500 cases</span>
          <span className="pill pillMuted">release site · deployment pending</span>
        </div>
      </header>

      <section className="computeSection" id="demo">
        <span className="sectionNumber">01 / THE DEMO</span>
        <h2 className="displayTitle">Reference → poison → antidote.</h2>
        <p className="sectionLead">
          Start with one current fact. Change it. HydraDG preserves the prior state and the graph relationship that changed. Restore the valid state without deleting the perturbation history.
        </p>
        <div className="grid threeCol">
          <article className="panel">
            <p className="eyebrow">Reference</p>
            <h2>Read the current state.</h2>
            <p className="muted">Show the fact and the source/session path that supports it.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Poison</p>
            <h2>Change one fact.</h2>
            <p className="muted">Retain the old fact and add explicit SUPERSEDED_BY / CONTRADICTS relationships.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Antidote</p>
            <h2>Restore without erasing.</h2>
            <p className="muted">Recover the declared current state while the divergent history remains inspectable.</p>
          </article>
        </div>
        <div className="actions"><Link className="primary" href="/judge">Run Judge Lab</Link></div>
      </section>

      <section className="metrics" aria-label="Recorded execution state">
        <article className="metric"><span className="metricLabel">Cases</span><strong>500</strong><span className="small muted">LongMemEval-S full500</span></article>
        <article className="metric"><span className="metricLabel">Sessions</span><strong>23,867</strong><span className="small muted">typed temporal state</span></article>
        <article className="metric"><span className="metricLabel">Result</span><strong>No positive signal</strong><span className="small muted">B/C/D hit-rate advantage not established</span></article>
        <article className="metric"><span className="metricLabel">Website custody</span><strong>{site.nodes.length} FCO sections</strong><span className="small muted">{site.edges.length} application-level FCG edges</span></article>
      </section>

      <section className="computeSection" id="result">
        <span className="sectionNumber">02 / WHAT WE FOUND</span>
        <h2 className="displayTitle">The graph ran. The tested retrieval advantage did not appear.</h2>
        <p className="sectionLead">
          HydraDG constructed and queried the typed LongMemEval graph, but the completed full500 ablation did not establish a positive B/C/D hit-rate signal over the flat route at the tested configuration. That null/negative evidence is retained instead of optimized away.
        </p>
        <div className="actions"><Link className="secondary" href="/evidence">Open evidence ledger</Link><Link className="secondary" href="/track03">Open Track 03 result</Link></div>
      </section>

      <section className="computeSection" id="iceberg">
        <span className="sectionNumber">03 / TIP OF THE ICEBERG</span>
        <h2 className="displayTitle">Simple on the surface. Full custody underneath.</h2>
        <div className="grid threeCol">
          <article className="panel"><p className="eyebrow">Hot · now</p><h2>Current state</h2><p className="muted">The answer, recent change and recovery status are visible first.</p></article>
          <article className="panel"><p className="eyebrow">Warm · context</p><h2>Graph relationships</h2><p className="muted">Experiment, typed edges, perturbation path and result status appear when the visitor asks why.</p></article>
          <article className="panel"><p className="eyebrow">Cold · retained</p><h2>Evidence memory</h2><p className="muted">FCO identities, FCG edges, SeedGraph custody, HydraDB state, receipts and historical counterevidence remain addressable.</p></article>
        </div>
        <p className="small muted note">Hot/cold and iceberg language is a presentation metaphor. Application-defined ΔG* is analogous terminology only and is not physical Gibbs free energy.</p>
      </section>

      <section className="computeSection" id="tracks">
        <span className="sectionNumber">04 / EXPERIMENTS</span>
        <h2 className="displayTitle">One custody spine. Three graph problems.</h2>
        <div className="routeGrid" style={{ marginTop: 30 }}>
          {tracks.map((track) => (
            <Link key={track.href} href={track.href} className="routeCard">
              <div>
                <p className="eyebrow">Track {track.n} · {track.status}</p>
                <h3>{track.title}</h3>
                <p className="small muted">{track.internal} · {track.subtitle}</p>
                <p>{track.body}</p>
              </div>
              <span className="routeArrow" aria-hidden="true">↗</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="computeSection" id="fcg">
        <span className="sectionNumber">05 / DEEP DIVE</span>
        <h2 className="displayTitle">Every unfamiliar object should resolve backward.</h2>
        <p className="sectionLead">
          A term, entity, hash or result should not be an isolated label. It should link to a knowledge object, its FCO/FCG relationships, the source/version or executed receipt, and the claim ceiling that bounds what it means.
        </p>
        <div className="fcgRail" style={{ marginTop: 30 }}>
          {[["01", "Term / Hash"],["02", "FCO"],["03", "FCG edge"],["04", "Source"],["05", "Claim ceiling"]].map(([n, label]) => (
            <div className="fcgStep" key={label}><span className="sectionNumber">{n}</span><strong>{label}</strong></div>
          ))}
        </div>
        <div className="actions"><Link className="secondary" href="/graph">Open Graph Explorer</Link><Link className="secondary" href="/knowledge">Resolve terminology</Link><a className="secondary" href="/api/site-fcg">Open site FCG JSON</a></div>
      </section>

      <section className="computeSection" id="fallback">
        <span className="sectionNumber">06 / RELEASE CONTINUITY</span>
        <h2 className="displayTitle">The story survives a hosting failure.</h2>
        <p className="sectionLead">If the current release cannot be promoted to Vercel in time, the repository contains a self-contained static judge artifact with the same golden path, executed result and claim boundaries.</p>
        <div className="actions"><a className="secondary" href="/backup/hydradg.html">Open static fallback</a><Link className="secondary" href="/eligibility">Release custody</Link></div>
      </section>

      <footer className="computeSection"><p className="eyebrow">Claim boundary</p><p className="small muted">A SHA-256 digest establishes byte/object identity only. Website lineage does not establish scientific correctness. Current project signature state remains NOT_SIGNED and live HydraDB state remains NOT_MERKLE_COMMITTED unless explicit later operations establish otherwise.</p></footer>
    </main>
  );
}
