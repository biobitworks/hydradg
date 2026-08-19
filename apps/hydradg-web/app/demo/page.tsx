import Link from "next/link";

export default function DemoPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · submission overview</p>
          <h1>HydraDG in three minutes.</h1>
          <p className="lede">
            See what changed, trace the dependency that changed, and test whether a repair restores the declared current state while the divergent history remains visible.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Try the interactive demo</Link>
            <a className="secondary" href="/backup/hydradg.html">Open offline fallback</a>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">FULL500 RESULT RETAINED</span>
          <span className="pill pillWarn">FINAL VIDEO PENDING</span>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber">01 / WHAT IT DOES</span>
        <h2 className="displayTitle">Reference → poison → antidote.</h2>
        <div className="grid threeCol">
          <article className="panel"><p className="eyebrow">Reference</p><h2>Show current state.</h2><p className="muted">Read a fact with its source/session evidence path.</p></article>
          <article className="panel"><p className="eyebrow">Poison</p><h2>Change one dependency.</h2><p className="muted">Preserve the prior fact and create explicit supersession/contradiction history.</p></article>
          <article className="panel"><p className="eyebrow">Antidote</p><h2>Restore without erasing.</h2><p className="muted">Return to the declared reference state while retaining the perturbation as evidence.</p></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / EXECUTED EVIDENCE</span>
        <h2 className="displayTitle">A null result is still a result.</h2>
        <p className="sectionLead">The completed LongMemEval-S full500 retrieval ablation materialized the graph in pinned local HydraDB and returned no positive B/C/D hit-rate signal over the flat baseline at the tested configuration.</p>
        <div className="metrics">
          <article className="metric"><span className="metricLabel">Cases</span><strong>500</strong></article>
          <article className="metric"><span className="metricLabel">Sessions</span><strong>23,867</strong></article>
          <article className="metric"><span className="metricLabel">Facts</span><strong>3,506</strong></article>
          <article className="metric"><span className="metricLabel">Decision</span><strong>No positive signal</strong></article>
        </div>
        <div className="actions"><Link className="secondary" href="/evidence">Follow the evidence</Link><Link className="secondary" href="/track03">Open Track 03</Link></div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / VIDEO</span>
        <h2 className="displayTitle">Final recording slot.</h2>
        <div className="panel">
          <p className="eyebrow">Submission video</p>
          <h2>FINAL_YOUTUBE_URL_PENDING</h2>
          <p className="muted">Record only after the current release build, public-link audit and fresh golden-path receipt are green. The static fallback can be recorded if Vercel promotion remains blocked.</p>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / JUDGE PATH</span>
        <h2 className="displayTitle">Surface first. Evidence underneath.</h2>
        <div className="flow mono"><span>problem</span><b>→</b><span>golden path</span><b>→</b><span>executed result</span><b>→</b><span>graph explorer</span><b>→</b><span>FCO/FCG evidence</span></div>
      </section>
    </main>
  );
}
