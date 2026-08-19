import Link from "next/link";

import { buildSiteFcg } from "@/lib/siteFcg";

const tracks = [
  {
    n: "01",
    href: "/track01",
    title: "HydraOntology",
    subtitle: "Enterprise context + ontology",
    body: "Resolve identities, conflicting evidence and current state across EnterpriseRAG-Bench and HERB.",
    status: "DATA PULL PENDING",
  },
  {
    n: "02",
    href: "/track02",
    title: "HydraBlast",
    subtitle: "Repos, dependencies + code as graphs",
    body: "Compute reverse dependency blast radius, first vulnerable path and poison → patch recovery in HydraDB.",
    status: "CANARY IN CI",
  },
  {
    n: "03",
    href: "/track03",
    title: "HydraMemory",
    subtitle: "Memory + context retrieval",
    body: "Preserve temporal state, supersession and contradiction while testing graph-aware retrieval on LongMemEval.",
    status: "FULL500 EXECUTED",
  },
] as const;

export default function Home() {
  const site = buildSiteFcg();

  return (
    <main>
      <header className="hero" id="top">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · built during the Aug 12–20 window</p>
          <h1>Memory that can show its work.</h1>
          <p className="lede">
            HydraDG turns graph state, transformations, perturbations and evidence paths into inspectable FCO/FCG objects.
            The interface does not hide the negative result: graph expansion did not improve the completed LongMemEval full500 hit-rate ablation.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Run the judge path</Link>
            <Link className="secondary" href="/graph">Open the 4D FCG</Link>
            <Link className="secondary" href="/evidence">Inspect evidence</Link>
          </div>
        </div>
        <div className="heroStatus" aria-label="Project status">
          <span className="pill pillGood">local HydraDB · executed</span>
          <span className="pill pillGood">LongMemEval · 500 cases</span>
          <span className="pill pillWarn">cloud API · non-blocking mismatch</span>
        </div>
      </header>

      <section className="metrics" aria-label="Recorded execution state">
        <article className="metric">
          <span className="metricLabel">HydraDB pin</span>
          <strong className="mono compact">6a2fbb192f37</strong>
          <span className="small muted">upstream source revision</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Track 03 graph</span>
          <strong>23,867 sessions</strong>
          <span className="small muted">500 cases · 3,506 facts · 4,776 entities</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Full500 decision</span>
          <strong>No positive signal</strong>
          <span className="small muted">B / C / D vs flat retrieval at the tested route</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Website custody</span>
          <strong>{site.nodes.length} FCO sections</strong>
          <span className="small muted">{site.edges.length} application-level FCG edges</span>
        </article>
      </section>

      <section className="computeSection" id="tracks">
        <span className="sectionNumber">01 / TRACKS</span>
        <h2 className="displayTitle">Three distinct graph problems.</h2>
        <p className="sectionLead">
          Shared custody primitives are allowed to repeat. The scientific question, dataset, graph schema, evaluation and judge story stay separate for each track.
        </p>
        <div className="routeGrid" style={{ marginTop: 30 }}>
          {tracks.map((track) => (
            <Link key={track.href} href={track.href} className="routeCard">
              <div>
                <p className="eyebrow">Track {track.n} · {track.status}</p>
                <h3>{track.title}</h3>
                <p className="small muted">{track.subtitle}</p>
                <p>{track.body}</p>
              </div>
              <span className="routeArrow" aria-hidden="true">↗</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="computeSection" id="fcg">
        <span className="sectionNumber">02 / WEBSITE FCG</span>
        <h2 className="displayTitle">The website is part of the custody graph.</h2>
        <p className="sectionLead">
          Every major route is represented as a hashed SiteSection FCO. Navigation and support relationships are explicit FCG edges.
          This establishes application object identity and lineage—not scientific correctness, signing, or a live HydraDB Merkle commitment.
        </p>
        <div className="fcgRail" style={{ marginTop: 30 }}>
          {[
            ["01", "Source"],
            ["02", "Evidence"],
            ["03", "Transformation"],
            ["04", "Claim"],
            ["05", "Artifact"],
          ].map(([n, label]) => (
            <div className="fcgStep" key={label}>
              <span className="sectionNumber">{n}</span>
              <strong>{label}</strong>
            </div>
          ))}
        </div>
        <div className="actions">
          <a className="secondary" href="/api/site-fcg">Open site FCG JSON</a>
          <Link className="secondary" href="/knowledge">Resolve terminology</Link>
        </div>
      </section>

      <section className="computeSection" id="judge">
        <span className="sectionNumber">03 / GOLDEN PATH</span>
        <h2 className="displayTitle">Reference → poison → antidote.</h2>
        <div className="grid threeCol">
          <article className="panel">
            <p className="eyebrow">Reference</p>
            <h2>Read the current graph.</h2>
            <p className="muted">Load a real LongMemEval case, run retrieval and inspect the supporting path before changing anything.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Perturbation</p>
            <h2>Change one fact.</h2>
            <p className="muted">Preserve the old fact, create SUPERSEDED_BY / CONTRADICTS, retain an FCG delta and inspect downstream behavior.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Recovery</p>
            <h2>Restore without erasing history.</h2>
            <p className="muted">Apply the antidote, resolve current state again and compare retrieval while the poison remains visible in history.</p>
          </article>
        </div>
        <div className="actions">
          <Link className="primary" href="/judge">Open Judge Lab</Link>
          <Link className="secondary" href="/knowledge#superseded-by">How SUPERSEDED_BY works</Link>
        </div>
      </section>

      <section className="computeSection" id="boundaries">
        <span className="sectionNumber">04 / CLAIM BOUNDARIES</span>
        <h2 className="displayTitle">Green means the stated gate passed. Nothing more.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">Established</p>
            <ul>
              <li>Local pinned HydraDB structural conformance passed.</li>
              <li>LongMemEval-S full500 retrieval ablation completed.</li>
              <li>Website SiteSection FCOs are content-addressed application metadata.</li>
            </ul>
          </article>
          <article className="panel">
            <p className="eyebrow">Not established</p>
            <ul>
              <li>Live HydraDB state is not Merkle-committed by this site.</li>
              <li>Project author signature is not claimed here.</li>
              <li>The full500 run does not establish graph retrieval superiority.</li>
              <li>Hosted HydraDB REST conformance remains unresolved.</li>
            </ul>
          </article>
        </div>
        <div className="actions">
          <Link className="secondary" href="/eligibility">Hackathon eligibility custody</Link>
          <Link className="secondary" href="/evidence">Evidence index</Link>
        </div>
      </section>

      <footer className="computeSection">
        <p className="eyebrow">Template attribution</p>
        <p className="small muted">
          Visual shell adapted during Hack Hydra from the user-supplied “COMPUTE — The Platform to Build & Ship AI Agents” template.
          HydraDG graph logic, evidence copy, routes and experiments are separate Hack Hydra implementation work.
        </p>
      </footer>
    </main>
  );
}
