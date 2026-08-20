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

const DEPTH_ROWS = [
  ["K=5", "Method A", "0.96383", "0.90660", "0.63787"],
  ["K=5", "Method D", "0.94468", "0.84603", "0.63787"],
  ["K=10", "Method A", "0.97872", "0.94535", "0.51511"],
  ["K=10", "Method D", "0.97021", "0.92273", "0.51511"],
] as const;

export default function Track03Page() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Track 03 · Memory + Context Retrieval</p>
          <h1>HydraMemory</h1>
          <p className="lede">A real LongMemEval-S full500 run materialized temporal sessions, facts, entities, supersession and contradiction in pinned HydraDB, then compared A/B/C/D retrieval. A later pre-registered K5/K10 matrix tested retrieval depth as a controlled perturbation.</p>
          <div className="actions"><Link className="primary" href="/judge">Judge walkthrough</Link><Link className="secondary" href="/best-use">Why HydraDB + math</Link><Link className="secondary" href="/graph">Inspect 4D FCG</Link><Link className="secondary" href="/how-to">How to use</Link></div>
        </div>
        <div className="heroStatus"><span className="pill pillGood">FULL500 COMPLETE</span><span className="pill pillWarn">MODEL BENEFIT NOT ESTABLISHED</span></div>
      </header>

      <section className="metrics">
        <article className="metric"><span className="metricLabel">Cases</span><strong>500</strong><span className="small muted">470 retrieval-scored · 30 abstentions</span></article>
        <article className="metric"><span className="metricLabel">Sessions</span><strong>23,867</strong><span className="small muted">occurrence-scoped identity</span></article>
        <article className="metric"><span className="metricLabel">Facts</span><strong>3,506</strong><span className="small muted">heuristic extraction in historical full500 lane</span></article>
        <article className="metric"><span className="metricLabel">Entities</span><strong>4,776</strong><span className="small muted">context-scoped</span></article>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / K=5 RETRIEVAL RESULT</span>
        <h2 className="displayTitle">The graph worked. The tested K=5 retrieval advantage did not appear.</h2>
        <p className="sectionLead">B, C and D did not establish a positive Hit@5 advantage over route A at the tested K=5 configuration. Evidence-path coverage can increase while top-k recall declines; HydraDG retains that null/negative result.</p>
        <div style={{ overflowX: "auto" }}><table style={{ width: "100%", borderCollapse: "collapse" }}><thead><tr><th align="left">Route</th><th>Hit@5</th><th>Recall@5</th><th align="left">Interpretation</th></tr></thead><tbody>{ROUTES.map(([route, hit, recall, interpretation]) => <tr key={route}><td>{route}</td><td align="center">{hit.toFixed(10)}</td><td align="center">{recall.toFixed(10)}</td><td>{interpretation}</td></tr>)}</tbody></table></div>
        <div className="grid twoCol" style={{ marginTop: 28 }}>
          <article className="panel"><p className="eyebrow">Evidence class</p><h2>RECOMPUTED_LIVE_HYDRADB_RETRIEVAL_ABLATION</h2><p className="small muted">Claim ceiling: LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA</p></article>
          <article className="panel"><p className="eyebrow">Custody state</p><h2>Hashed, not signed.</h2><p className="small muted">Signature: NOT_SIGNED · Merkle: NOT_MERKLE_COMMITTED · independent replication: NOT_ESTABLISHED</p></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">02 / K=5 → K=10 DEPTH ABLATION</span>
        <h2 className="displayTitle">K=10 improved retrieval depth without establishing a representation or model win.</h2>
        <p className="sectionLead">The pre-registered 2×2 matrix held the frozen dataset and retrieval logic fixed while comparing RAW vs SeedGraph at K=5 and K=10. RAW and SeedGraph were identical at the same K; increasing K improved Hit@K and Recall@K while evidence-path coverage density declined.</p>
        <div className="tableWrap"><table><thead><tr><th>Depth</th><th>Method</th><th>Hit@K</th><th>Recall@K</th><th>Evidence-path coverage</th></tr></thead><tbody>{DEPTH_ROWS.map(([k, method, hit, recall, coverage]) => <tr key={`${k}-${method}`}><td>{k}</td><td>{method}</td><td>{hit}</td><td>{recall}</td><td>{coverage}</td></tr>)}</tbody></table></div>
        <div className="grid twoCol" style={{ marginTop: 24 }}>
          <article className="panel"><p className="eyebrow">Method D depth effect</p><h2>+2.553 pp Hit · +7.670 pp Recall</h2><p className="small muted">K10 minus K5 in the retained local matrix. This supports a ranking-depth/cutoff effect under the tested implementation.</p></article>
          <article className="panel"><p className="eyebrow">Model involvement</p><h2>NONE IN PRIMARY MATRIX</h2><p className="small muted">The K10 result is not evidence that an LLM improved retrieval. Model-assisted extraction remains a separate future controlled axis.</p></article>
        </div>
        <div className="actions"><Link className="primary goldenCta" href="/best-use">Open Best Use of HydraDB analysis</Link><a className="secondary" href="https://github.com/biobitworks/hydradg/blob/main/PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json">Pre-registration</a><a className="secondary" href="https://github.com/biobitworks/hydradg/blob/main/eval/track03_k5_k10_20260819/RETAINED_MATRIX_SUMMARY.json">Retained summary</a></div>
      </section>

      <section className="computeSection"><span className="sectionNumber">03 / GRAPH</span><h2 className="displayTitle">What was actually written.</h2><div className="tableWrap"><table><thead><tr><th>Relation</th><th>Count</th><th>Role</th></tr></thead><tbody>{EDGES.map(([name, count]) => <tr key={name}><td className="mono">{name}</td><td>{count.toLocaleString()}</td><td>{name === "SUPERSEDED_BY" ? "temporal replacement" : name === "CONTRADICTS" ? "incompatible fact state" : "typed graph structure"}</td></tr>)}</tbody></table></div></section>

      <section className="computeSection"><span className="sectionNumber">04 / HASHES</span><h2 className="displayTitle">Executed result identities.</h2><div className="stack"><div className="panel"><p className="eyebrow">LongMemEval source</p><p className="mono compact">d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442</p></div><div className="panel"><p className="eyebrow">Result</p><p className="mono compact">bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324</p></div><div className="panel"><p className="eyebrow">Statistics</p><p className="mono compact">8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc</p></div><div className="panel"><p className="eyebrow">Receipt</p><p className="mono compact">21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365</p></div></div><p className="small muted note">These digests establish retained byte/object identity under the recorded run; they do not establish correctness by themselves.</p></section>

      <section className="computeSection">
        <span className="sectionNumber">05 / FALSIFICATION WALKTHROUGH</span>
        <h2 className="displayTitle">Inspect the causal state contract without mutating the public backend.</h2>
        <div className="flow mono"><span>reference</span><b>→</b><span>poison</span><b>→</b><span>SUPERSEDED_BY / CONTRADICTS</span><b>→</b><span>antidote</span><b>→</b><span>restoration check</span></div>
        <div className="actions"><Link className="primary" href="/judge">Open read-only walkthrough table</Link><Link className="secondary" href="/graph?q=SeedOfTruth">Trace SeedOfTruth</Link><Link className="secondary" href="/knowledge">Relationship contract</Link></div>
      </section>
    </main>
  );
}
