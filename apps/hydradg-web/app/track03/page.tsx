import Link from "next/link";

const EDGES = [
  ["ABOUT", 7012], ["ASSERTS", 3506], ["CONTAINS", 23867], ["CONTRADICTS", 4914], ["DERIVED_FROM", 3506],
  ["HAS_CASE", 500], ["MENTIONS", 6935], ["NEXT", 23367], ["PREV", 23367], ["SUPERSEDED_BY", 2457],
] as const;

const ROUTES = [
  ["A · reference / flat", 0.9638297872, 0.9065957447, "reference"],
  ["B · temporal", 0.9468085106, 0.8538297872, "no positive Hit@5 signal"],
  ["C · temporal + entity/provenance", 0.9468085106, 0.85258865, "no positive Hit@5 signal"],
  ["D · current/supersession + contradiction", 0.94468085, 0.84602837, "no positive Hit@5 signal"],
] as const;

export default function Track03Page() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Track 03 · Memory + Context Retrieval</p>
          <h1>HydraMemory</h1>
          <p className="lede">A real LongMemEval-S full500 run materialized temporal sessions, facts, entities, supersession and contradiction in pinned HydraDB, then compared A/B/C/D retrieval.</p>
          <div className="actions"><Link className="primary" href="/judge">Judge walkthrough</Link><Link className="secondary" href="/graph">Inspect 4D FCG</Link><Link className="secondary" href="/how-to">How to use</Link></div>
        </div>
        <div className="heroStatus"><span className="pill pillGood">FULL500 COMPLETE</span><span className="pill pillWarn">NO POSITIVE B/C/D HIT-RATE SIGNAL</span></div>
      </header>

      <section className="metrics">
        <article className="metric"><span className="metricLabel">Cases</span><strong>500</strong><span className="small muted">470 retrieval-scored · 30 abstentions</span></article>
        <article className="metric"><span className="metricLabel">Sessions</span><strong>23,867</strong><span className="small muted">occurrence-scoped identity</span></article>
        <article className="metric"><span className="metricLabel">Facts</span><strong>3,506</strong><span className="small muted">heuristic extraction</span></article>
        <article className="metric"><span className="metricLabel">Entities</span><strong>4,776</strong><span className="small muted">context-scoped</span></article>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / RETRIEVAL RESULT</span>
        <h2 className="displayTitle">The graph worked. The tested retrieval advantage did not appear.</h2>
        <p className="sectionLead">B, C and D did not establish a positive Hit@5 advantage over route A at the tested K=5 configuration. Evidence-path coverage can increase while top-k recall declines; HydraDG retains that null/negative result.</p>
        <div style={{ overflowX: "auto" }}><table style={{ width: "100%", borderCollapse: "collapse" }}><thead><tr><th align="left">Route</th><th>Hit@5</th><th>Recall@5</th><th align="left">Interpretation</th></tr></thead><tbody>{ROUTES.map(([route, hit, recall, interpretation]) => <tr key={route}><td>{route}</td><td align="center">{hit.toFixed(10)}</td><td align="center">{recall.toFixed(10)}</td><td>{interpretation}</td></tr>)}</tbody></table></div>
        <div className="grid twoCol" style={{ marginTop: 28 }}>
          <article className="panel"><p className="eyebrow">Evidence class</p><h2>RECOMPUTED_LIVE_HYDRADB_RETRIEVAL_ABLATION</h2><p className="small muted">Claim ceiling: LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA</p></article>
          <article className="panel"><p className="eyebrow">Custody state</p><h2>Hashed, not signed.</h2><p className="small muted">Signature: NOT_SIGNED · Merkle: NOT_MERKLE_COMMITTED · independent replication: NOT_ESTABLISHED</p></article>
        </div>
      </section>

      <section className="computeSection"><span className="sectionNumber">02 / GRAPH</span><h2 className="displayTitle">What was actually written.</h2><div className="tableWrap"><table><thead><tr><th>Relation</th><th>Count</th><th>Role</th></tr></thead><tbody>{EDGES.map(([name, count]) => <tr key={name}><td className="mono">{name}</td><td>{count.toLocaleString()}</td><td>{name === "SUPERSEDED_BY" ? "temporal replacement" : name === "CONTRADICTS" ? "incompatible fact state" : "typed graph structure"}</td></tr>)}</tbody></table></div></section>

      <section className="computeSection"><span className="sectionNumber">03 / HASHES</span><h2 className="displayTitle">Executed result identities.</h2><div className="stack"><div className="panel"><p className="eyebrow">LongMemEval source</p><p className="mono compact">d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442</p></div><div className="panel"><p className="eyebrow">Result</p><p className="mono compact">bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324</p></div><div className="panel"><p className="eyebrow">Statistics</p><p className="mono compact">8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc</p></div><div className="panel"><p className="eyebrow">Receipt</p><p className="mono compact">21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365</p></div></div><p className="small muted note">These digests establish retained byte/object identity under the recorded run; they do not establish correctness by themselves.</p></section>

      <section className="computeSection">
        <span className="sectionNumber">04 / FALSIFICATION WALKTHROUGH</span>
        <h2 className="displayTitle">Inspect the causal state contract without mutating the public backend.</h2>
        <div className="flow mono"><span>reference</span><b>→</b><span>poison</span><b>→</b><span>SUPERSEDED_BY / CONTRADICTS</span><b>→</b><span>antidote</span><b>→</b><span>restoration check</span></div>
        <div className="actions"><Link className="primary" href="/judge">Open read-only walkthrough table</Link><Link className="secondary" href="/graph?q=SeedOfTruth">Trace SeedOfTruth</Link><Link className="secondary" href="/knowledge">Relationship contract</Link></div>
      </section>
    </main>
  );
}
