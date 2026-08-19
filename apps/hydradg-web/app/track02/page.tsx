import Link from "next/link";

export default function Track02Page() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Track 02A · Repos, dependencies + code as graphs</p>
          <h1>HydraBlast</h1>
          <p className="lede">
            Given a compromised package version, traverse the reverse dependency graph to identify exposed services, the exact dependency path, and whether a patch removes every vulnerable route.
          </p>
          <div className="actions">
            <a className="primary" href="https://github.com/biobitworks/hydradg/pull/16" target="_blank" rel="noreferrer">Open release PR ↗</a>
            <Link className="secondary" href="/evidence">Evidence index</Link>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillWarn">SYNTHETIC CANARY IN CI</span>
          <span className="pill pillMuted">REAL NPM SNAPSHOT PENDING</span>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber">01 / QUESTION</span>
        <h2 className="displayTitle">What is exposed at time T?</h2>
        <div className="fcgRail">
          {[
            ["01", "Advisory"],
            ["02", "PackageVersion"],
            ["03", "DEPENDS_ON*"],
            ["04", "Lockfile"],
            ["05", "Service"],
          ].map(([n, label]) => <div className="fcgStep" key={label}><span className="sectionNumber">{n}</span><strong>{label}</strong></div>)}
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / CANARY</span>
        <h2 className="displayTitle">Poison two paths. Repair one. Repair both.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">Expected state trajectory</p>
            <div className="flow mono">
              <span>reference · 0</span><b>→</b><span>poison · 2</span><b>→</b><span>partial repair · 1</span><b>→</b><span>full repair · 0</span>
            </div>
            <p className="small muted">Counts are exposed services in the synthetic structural canary, not real vulnerability counts.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Independent oracle</p>
            <h2>Python closure vs HydraDB.</h2>
            <p className="muted">Both consume the same frozen edge fixture. Exact exposed-service sets must match at every state before the canary is green.</p>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / ANTICUBE</span>
        <h2 className="displayTitle">Remove the load-bearing edge.</h2>
        <p className="sectionLead">
          The partial-repair state removes one vulnerable dependency path. The predicted affected set must shrink from two services to one. If it does not, the graph relationship is not behaving causally under the declared fixture.
        </p>
        <div className="panel" style={{ marginTop: 26 }}>
          <p className="eyebrow">Claim ceiling</p>
          <p className="mono compact">SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY_NOT_REAL_NPM_EXPOSURE</p>
          <p className="small muted">No real npm vulnerability, maintainer compromise, or production exposure claim is made until the real data lane executes.</p>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / REAL-DATA GATE</span>
        <h2 className="displayTitle">Then replace the fixture with evidence.</h2>
        <div className="grid threeCol">
          <article className="panel"><p className="eyebrow">Registry</p><h2>npm</h2><p className="muted">Exact package versions, dependencies, publication and package metadata.</p></article>
          <article className="panel"><p className="eyebrow">Resolved graph</p><h2>deps.dev</h2><p className="muted">Resolved dependency relationships independently sourced from the package graph.</p></article>
          <article className="panel"><p className="eyebrow">Advisories</p><h2>OSV / GHSA</h2><p className="muted">Affected and fixed version evidence; no advisory is treated as a runtime exploit claim.</p></article>
        </div>
      </section>
    </main>
  );
}
