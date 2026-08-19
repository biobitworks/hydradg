const evidence = [
  {
    label: "Live HydraDB structural conformance",
    status: "PASS",
    detail:
      "Pinned HydraDB built and executed the v2 typed-memory structural suite. Seven declared invariants passed: duplicate-session identity separation, exact case membership, context-scoped entity identity, supersession construction, contradiction construction, supersession traversal, and contradiction traversal.",
    ceiling: "SYNTHETIC_STRUCTURAL_CONFORMANCE_ONLY",
  },
  {
    label: "LongMemEval v1 lexical graph calibration",
    status: "NEGATIVE RESULT PRESERVED",
    detail:
      "At K=3, flat BM25 retrieved 75/77 non-abstention cases while naive graph expansion retrieved 68/77. Exact McNemar p=0.015625; the graph design was rejected rather than hidden.",
    ceiling: "REFERENCE_GRAPH_DESIGN_CALIBRATION_ONLY",
  },
  {
    label: "LongMemEval full500 typed-memory ablation",
    status: "DAISY RUN",
    detail:
      "A/B/C/D full500 is the submission-critical run: A flat BM25; B temporal traversal; C temporal + entity/provenance; D supersession/current-state + contradiction traversal. Ground-truth answer_session_ids remain evaluation-only.",
    ceiling: "PENDING_EXECUTED_RECEIPT",
  },
  {
    label: "ECA-EXT80 perturbation calibration",
    status: "RECOMPUTED COMPANION EVIDENCE",
    detail:
      "80 deterministic trajectories across Rules 30/90/110/184, five seeds, and four conditions. The fixture is used to calibrate first-divergence, downstream impact, and recovery semantics; it is not evidence about biology or LLM safety.",
    ceiling: "BOUNDED_DETERMINISTIC_CALIBRATION",
  },
];

export default function EvidencePage() {
  return (
    <main>
      <nav>
        <a href="/">MVP</a>
        <a href="/demo">Demo</a>
        <a href="/graph">4D FCG</a>
        <a href="/eligibility">Submission custody</a>
      </nav>

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · evidence ledger</p>
          <h1>Results without claim inflation</h1>
          <p className="lede">
            HydraDG preserves positive, negative, failed, and pending executions as separate custody
            objects. This page is the public judge-facing snapshot; the final full500 numbers are
            promoted only after the Daisy run emits an executed statistical receipt.
          </p>
        </div>
      </header>

      <section className="metrics" aria-label="Submission evidence status">
        <article className="metric">
          <span className="metricLabel">Structural gate</span>
          <strong>7/7 declared invariants</strong>
          <span className="small muted">live pinned HydraDB CI</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Primary real dataset</span>
          <strong>LongMemEval-S · 500 Q</strong>
          <span className="small muted">full500 Daisy train</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Negative result</span>
          <strong>Preserved</strong>
          <span className="small muted">v1 lexical expansion rejected</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Custody ceiling</span>
          <strong>Hash-linked</strong>
          <span className="small muted">not signed / not Merkle-committed unless separately executed</span>
        </article>
      </section>

      <section className="grid twoCol">
        {evidence.map((item) => (
          <article className="panel" key={item.label}>
            <p className="eyebrow">{item.status}</p>
            <h2>{item.label}</h2>
            <p className="muted">{item.detail}</p>
            <div className="result">
              claim_ceiling: {item.ceiling}
            </div>
          </article>
        ))}
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Mechanical Scientific Method</p>
        <h2>How a result becomes admissible</h2>
        <div className="flow mono">
          <span>freeze source</span><b>→</b><span>reference graph</span><b>→</b>
          <span>perturb / query</span><b>→</b><span>measure</span><b>→</b>
          <span>first divergence</span><b>→</b><span>recovery / ablation</span><b>→</b>
          <span>statistics</span><b>→</b><span>bounded claim</span>
        </div>
        <p className="small muted note">
          FCO/FCG preserves source → transformation → derived evidence → claim lineage. A hash proves
          byte identity, not scientific correctness. A graph path is evidence for a dependency route,
          not proof that the underlying claim is universally true.
        </p>
      </section>

      <section className="panel architecture">
        <p className="eyebrow">Best Use of HydraDB</p>
        <h2>The graph-native question</h2>
        <p className="lede">
          Given a changing memory state, return the current non-superseded evidence path, reconstruct
          the contradictory history that produced it, and show which upstream dependency changed.
        </p>
        <div className="flow mono">
          <span>Session</span><b>→</b><span>Fact</span><b>→</b><span>Entity</span><b>→</b>
          <span>SUPERSEDED_BY</span><b>→</b><span>current Fact</span><b>→</b><span>provenance path</span>
        </div>
      </section>
    </main>
  );
}
