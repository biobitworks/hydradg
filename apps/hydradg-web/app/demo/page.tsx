import Link from "next/link";

const FINAL_VIDEO_URL = "https://youtu.be/7EDb6q-loPA";

export default function DemoPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · submission overview</p>
          <h1>HydraDG in three minutes.</h1>
          <p className="lede">See what changed, trace the dependency that changed, and test whether a repair restores the declared current state while the divergent history remains visible.</p>
          <div className="actions"><Link className="primary" href="/judge">Try the read-only walkthrough</Link><a className="secondary" href={FINAL_VIDEO_URL} target="_blank" rel="noreferrer">Watch final demo video ↗</a><a className="secondary" href="/backup/hydradg.html">Offline fallback</a></div>
        </div>
        <div className="heroStatus"><span className="pill pillGood">FULL500 RESULT RETAINED</span><span className="pill pillGood">FINAL VIDEO RECORDED</span></div>
      </header>

      <section className="computeSection"><span className="sectionNumber">01 / WHAT IT DOES</span><h2 className="displayTitle">Reference → poison → antidote.</h2><div className="grid threeCol"><article className="panel"><p className="eyebrow" style={{ color: "#b69cff" }}>Reference / normal</p><h2>Show current state.</h2><p className="muted">Read a fact with its source/session evidence path.</p></article><article className="panel"><p className="eyebrow" style={{ color: "#ff8a3d" }}>Poison / mutation</p><h2>Change one dependency.</h2><p className="muted">Preserve the prior fact and create explicit supersession/contradiction history.</p></article><article className="panel"><p className="eyebrow" style={{ color: "#5aa9ff" }}>Antidote / restoration</p><h2>Restore without erasing.</h2><p className="muted">Return toward the declared reference-compatible state while retaining the perturbation as evidence.</p></article></div></section>

      <section className="computeSection"><span className="sectionNumber">02 / EXECUTED EVIDENCE</span><h2 className="displayTitle">A null result is still a result.</h2><p className="sectionLead">The completed LongMemEval-S full500 retrieval ablation materialized the graph in pinned local HydraDB and returned no positive B/C/D hit-rate signal over the flat reference route at the tested configuration.</p><div className="metrics"><article className="metric"><span className="metricLabel">Cases</span><strong>500</strong></article><article className="metric"><span className="metricLabel">Sessions</span><strong>23,867</strong></article><article className="metric"><span className="metricLabel">Facts</span><strong>3,506</strong></article><article className="metric"><span className="metricLabel">Decision</span><strong>No positive signal</strong></article></div><div className="actions"><Link className="secondary" href="/evidence">Follow the evidence</Link><Link className="secondary" href="/track03">Open Track 03</Link></div></section>

      <section className="computeSection"><span className="sectionNumber">03 / VIDEO</span><h2 className="displayTitle">Final submission recording.</h2><div className="panel"><p className="eyebrow">Submission video</p><h2>Recorded and linked</h2><p className="muted">The final demo video is the human-submitted presentation artifact. Website/release state may continue to receive custody-bounded corrections without rewriting the executed scientific result.</p><div className="actions"><a className="primary" href={FINAL_VIDEO_URL} target="_blank" rel="noreferrer">Open final video ↗</a></div></div></section>

      <section className="computeSection"><span className="sectionNumber">04 / JUDGE PATH</span><h2 className="displayTitle">Surface first. Evidence underneath.</h2><div className="flow mono"><span>problem</span><b>→</b><span>golden path</span><b>→</b><span>executed result</span><b>→</b><span>4D graph</span><b>→</b><span>KnowledgeAtom / SeedOfTruth</span><b>→</b><span>FCO/FCG evidence</span></div><div className="actions"><Link className="secondary" href="/how-to">How to use</Link><Link className="secondary" href="/knowledge">Knowledge Base</Link></div></section>
    </main>
  );
}
