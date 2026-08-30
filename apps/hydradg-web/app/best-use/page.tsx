import Link from "next/link";

const K_ROWS = [
  ["K=5", "Method A", "0.96383", "0.90660", "0.63787"],
  ["K=5", "Method D", "0.94468", "0.84603", "0.63787"],
  ["K=10", "Method A", "0.97872", "0.94535", "0.51511"],
  ["K=10", "Method D", "0.97021", "0.92273", "0.51511"],
] as const;

const SOURCE_LINKS = [
  ["Scale economics + fail-closed plan", "https://github.com/biobitworks/hydradg/blob/main/docs/BEST_USE_HYDRADB_SCALE_ECONOMICS_PLAN.md"],
  ["Deterministic calculator", "https://github.com/biobitworks/hydradg/blob/main/scripts/calculate_information_savings.py"],
  ["Calculator input", "https://github.com/biobitworks/hydradg/blob/main/eval/hosted_migration_20260820/information_savings/INPUT.json"],
  ["Deterministic receipt", "https://github.com/biobitworks/hydradg/blob/main/eval/hosted_migration_20260820/information_savings/INFORMATION_SAVINGS_RECEIPT_V2.json"],
  ["Legacy projection receipt", "https://github.com/biobitworks/hydradg/blob/main/eval/hosted_migration_20260820/DEDUPLICATION_PARQUET_RECEIPT.json"],
  ["K5/K10 pre-registration", "https://github.com/biobitworks/hydradg/blob/main/PRE_REGISTRATION_K5_K10_RAW_SEEDGRAPH.json"],
  ["Retained K5/K10 summary", "https://github.com/biobitworks/hydradg/blob/main/eval/track03_k5_k10_20260819/RETAINED_MATRIX_SUMMARY.json"],
] as const;

export default function BestUsePage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow goldText">Best Use of HydraDB</p>
          <h1>One canonical fact. Many relationships. Deterministic accounting.</h1>
          <p className="lede">HydraDG uses HydraDB as a graph-native context and custody layer: exact content identities become reusable nodes, while provenance, time, contradiction, supersession and evidence-path context remain typed relationships. A Vercel deployment can lack live HydraDB credentials without erasing the retained HydraDB execution evidence.</p>
          <div className="actions"><Link className="primary goldenCta" href="/track03">See executed retrieval</Link><Link className="secondary" href="/graph">Traverse the FCG</Link><Link className="secondary" href="/models">Model boundary</Link></div>
        </div>
        <div className="heroStatus"><span className="pill pillGood">GRAPH-NATIVE USE CASE</span><span className="pill pillWarn">LIVE HOSTED STATUS IS DEPLOYMENT-SPECIFIC</span></div>
      </header>

      <section className="metrics">
        <article className="metric"><span className="metricLabel">Raw word + sentence occurrences</span><strong>31,672,976</strong></article>
        <article className="metric"><span className="metricLabel">Canonical unique keys</span><strong>10,854,020</strong></article>
        <article className="metric"><span className="metricLabel">Reusable duplicate occurrences</span><strong>20,818,956</strong></article>
        <article className="metric"><span className="metricLabel">Occurrence reuse</span><strong>65.730975%</strong></article>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">01 / WHY HYDRADB</span>
        <h2 className="displayTitle">Similarity is not identity, and context is not a flat row.</h2>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">Canonical graph identity</p><h2>Hash once; reference many times.</h2><p>A content-addressed FCO can be reused across documents, releases, experiments and times without pretending each occurrence is new content. FCG edges preserve where, when and why that identity appears.</p></article>
          <article className="panel"><p className="eyebrow">Typed reasoning context</p><h2>Traverse provenance, contradiction and supersession.</h2><p>HydraDB relationships can carry <span className="mono">DERIVED_FROM</span>, <span className="mono">CONTRADICTS</span>, <span className="mono">SUPERSEDED_BY</span> and spatiotemporal context. Vector similarity can be a candidate signal, but it does not prove custody or exact equality.</p></article>
        </div>
        <p className="small muted note">HydraDG does not claim vector or relational systems are incapable of representing this information. The claim is narrower: a graph-native context layer makes recursive evidence relationships, exact identity and traversal first-class rather than application-side glue.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">02 / DETERMINISTIC REUSE MATH</span>
        <h2 className="displayTitle">The savings claim is split into measured, counted and theoretical lanes.</h2>
        <div className="panel goldenPanel">
          <p className="mono">31,672,976 raw occurrences = 10,854,020 unique keys + 20,818,956 duplicate occurrences</p>
          <p className="mono">reuse% = 100 × 20,818,956 / 31,672,976 = 65.730975%</p>
          <p className="mono">declared canonical Parquet footprint = 350,290,966 + 751,182,824 = 1,101,473,790 bytes</p>
        </div>
        <div className="grid twoCol" style={{ marginTop: 24 }}>
          <article className="panel"><p className="eyebrow">What is established</p><h2>Canonical atom/key reuse accounting</h2><p>The retained counts deterministically show 20,818,956 repeated word/sentence occurrences relative to unique keys. This supports the graph-economic idea of reusing canonical identities while preserving multiple contextual edges.</p></article>
          <article className="panel"><p className="eyebrow">What is not established</p><h2>Download-byte savings: NOT_MEASURED</h2><p>The calculator input currently has an empty full acquisition manifest. We therefore do not convert occurrence reuse into GB saved. The next byte-level gate requires one <span className="mono">path + size_bytes + sha256</span> record per acquired object.</p></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">03 / CALCULATOR CAUGHT A DISCREPANCY</span>
        <h2 className="displayTitle">Failure is evidence when the calculation is hash-bound.</h2>
        <div className="metrics">
          <article className="metric"><span className="metricLabel">Legacy projection</span><strong>809.63 Wh</strong><span className="small muted">projection-only receipt</span></article>
          <article className="metric"><span className="metricLabel">Deterministic recomputation</span><strong>0.809626 Wh</strong><span className="small muted">theoretical equivalent only</span></article>
          <article className="metric"><span className="metricLabel">Theoretical FLOPs</span><strong>2.91465384e17</strong><span className="small muted">not measured compute</span></article>
          <article className="metric"><span className="metricLabel">Measured energy</span><strong>NULL</strong><span className="small muted">not fabricated</span></article>
        </div>
        <div className="panel"><p className="mono">2 × 7,000,000,000 × 20,818,956 = 291,465,384,000,000,000 FLOPs</p><p className="mono">291,465,384,000,000,000 / 100,000,000,000,000 / 3600 = 0.809626 Wh</p><p>The roughly 1,000× legacy discrepancy is preserved instead of silently overwritten. The deterministic contract hashes canonical input, calculation rules and output receipt; <span className="mono">--verify</span> exits non-zero on mismatch.</p></div>
        <p className="small muted note">Energy remains theoretical. No measured watt-hour claim is promoted from this scenario.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">04 / WHY K=5 AND K=10</span>
        <h2 className="displayTitle">K is a context budget, not a model score.</h2>
        <p className="sectionLead">K=5 asks whether the correct memory survives a tight five-item retrieval budget. K=10 is the controlled falsification test for the hypothesis that useful memories are ranked below position five. The retained matrix changed K while preserving the frozen dataset and retrieval logic.</p>
        <div className="tableWrap"><table><thead><tr><th>Depth</th><th>Method</th><th>Hit@K</th><th>Recall@K</th><th>Evidence-path coverage</th></tr></thead><tbody>{K_ROWS.map(([k, method, hit, recall, coverage]) => <tr key={`${k}-${method}`}><td>{k}</td><td>{method}</td><td>{hit}</td><td>{recall}</td><td>{coverage}</td></tr>)}</tbody></table></div>
        <div className="grid twoCol" style={{ marginTop: 24 }}>
          <article className="panel"><p className="eyebrow">Depth result</p><h2>K=10 improved retrieval.</h2><p>Method A gained +1.489 percentage points Hit@K and +3.875 pp Recall@K. Method D gained +2.553 pp Hit@K and +7.670 pp Recall@K.</p></article>
          <article className="panel"><p className="eyebrow">Trade-off</p><h2>More depth did not mean denser evidence paths.</h2><p>Evidence-path coverage moved from 0.63787 at K=5 to 0.51511 at K=10, a -12.276 percentage-point change in this retained matrix.</p></article>
        </div>
        <p className="small muted note">RAW and SeedGraph had identical retrieval metrics at the same K under the tested parameters. That retains the representation null rather than calling K=10 a SeedGraph win.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">05 / DOES A MODEL IMPROVE IT?</span>
        <h2 className="displayTitle">Not established yet.</h2>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">Executed matrix</p><h2>Model = NONE</h2><p>The primary K5/K10 comparison intentionally kept probabilistic model output out of the deterministic retrieval matrix. The K=10 improvement is therefore a retrieval-depth effect, not evidence that Qwen, Ollama or Ollarma improved retrieval.</p></article>
          <article className="panel"><p className="eyebrow">Next controlled axis</p><h2>Heuristic vs Ollarma, K held fixed.</h2><p>Freeze the same input, K, graph logic and evaluation; bind the exact model tag/digest, tokenizer, prompt and extraction receipt; then compare model-assisted extraction against heuristic extraction. Model stochasticity must be measured or cached separately from retrieval determinism.</p></article>
        </div>
        <p className="mono small">MODEL_BENEFIT_NOT_ESTABLISHED · FUTURE_CONTROLLED_MODEL_EXTRACTION_ABLATION</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">06 / LIVE HOSTED STATUS VS PROJECT EVIDENCE</span>
        <h2 className="displayTitle">A missing deployment secret is not a missing HydraDB experiment.</h2>
        <p className="sectionLead">The public status card reports request-level connectivity for the current Vercel deployment. If it says Hosted HydraDB is not configured, that deployment cannot perform a live server-side HydraDB canary. The retained local HydraDB executions and bounded historical hosted receipts remain separate evidence objects.</p>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">Deployment lane</p><h2>Live credentials/configuration</h2><p>Server-only HydraDB configuration must be present in the Vercel environment for a live hosted canary. Credentials must never be exposed through <span className="mono">NEXT_PUBLIC_*</span> variables or browser code.</p></article>
          <article className="panel"><p className="eyebrow">Evidence lane</p><h2>Fail closed on parity scope</h2><p>Historical hosted parity remains bounded to its recorded graph scope. Expanded hosted parity, full local writeback/readback and root reconciliation must remain NOT_ESTABLISHED until their own receipts execute.</p></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">07 / SOURCE, MATH, IMPLEMENTATION</span>
        <h2 className="displayTitle">Every headline has a route to the artifact.</h2>
        <div className="grid twoCol">{SOURCE_LINKS.map(([label, href]) => <article className="panel" key={href}><h3><a className="goldLink" href={href}>{label}</a></h3><p className="small muted">Open the retained repository artifact.</p></article>)}</div>
        <div className="actions"><Link className="primary goldenCta" href="/track03">Back to Track 03</Link><Link className="secondary" href="/custody">Custody state</Link><Link className="secondary" href="/evidence">Evidence ledger</Link></div>
      </section>
    </main>
  );
}
