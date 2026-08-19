import Link from "next/link";

const evidence = [
  {
    label: "Live HydraDB structural conformance",
    status: "PASS",
    detail:
      "Pinned HydraDB built and executed the v2 typed-memory structural suite. Seven declared invariants passed: duplicate-session identity separation, exact case membership, context-scoped entity identity, supersession construction, contradiction construction, supersession traversal, and contradiction traversal.",
    ceiling: "SYNTHETIC_STRUCTURAL_CONFORMANCE_ONLY",
    href: "/track03",
  },
  {
    label: "LongMemEval v1 lexical graph calibration",
    status: "NEGATIVE RESULT PRESERVED",
    detail:
      "At K=3, flat BM25 retrieved 75/77 non-abstention cases while naive graph expansion retrieved 68/77. Exact McNemar p=0.015625; the graph design was rejected rather than hidden.",
    ceiling: "REFERENCE_GRAPH_DESIGN_CALIBRATION_ONLY",
    href: "/track03",
  },
  {
    label: "LongMemEval full500 typed-memory ablation",
    status: "EXECUTED · NEGATIVE/NEUTRAL",
    detail:
      "500 cases were materialized into live pinned HydraDB; 470 cases had retrieval ground truth. The paired analysis returned NO_POSITIVE_HIT_RATE_SIGNAL for B, C, or D relative to A at the tested route. This is a retrieval ablation, not end-to-end QA.",
    ceiling: "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
    href: "/track03",
  },
  {
    label: "Track 02 HydraBlast",
    status: "CANARY EXECUTION IN PROGRESS",
    detail:
      "Fresh Hack Hydra code compares a deterministic Python reverse dependency closure against live HydraDB for reference, poison, partial-repair and full-repair states. The first CI attempt exposed an unsupported standalone MERGE+SET request shape and was retained as a failure before repair.",
    ceiling: "SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY_NOT_REAL_NPM_EXPOSURE",
    href: "/track02",
  },
  {
    label: "Track 01 HydraOntology",
    status: "CANARY EXECUTION IN PROGRESS",
    detail:
      "Fresh Hack Hydra code tests whether removing and restoring a RESOLVES_TO identity edge changes the evidence set exactly as a deterministic reference mapping predicts. EnterpriseRAG-Bench and HERB performance remains unclaimed until real dataset pull and benchmark receipts exist.",
    ceiling: "SYNTHETIC_TRACK01_STRUCTURAL_CANARY_ONLY_NOT_ENTERPRISERAG_OR_HERB_PERFORMANCE",
    href: "/track01",
  },
  {
    label: "ECA-EXT80 prior-work companion",
    status: "REFERENCE ONLY FOR HACKATHON ELIGIBILITY",
    detail:
      "Pre-hackathon perturbation/recovery work may inform the method or be cited as prior evidence, but participant-authored implementation written before August 12 is excluded from the Hack Hydra submission code under the official build-window rule.",
    ceiling: "PRIOR_WORK_REFERENCE_NOT_HACKATHON_IMPLEMENTATION",
    href: "/eligibility",
  },
];

const hashes = [
  ["LongMemEval source", "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"],
  ["full500 result", "bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324"],
  ["full500 statistics", "8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc"],
  ["full500 receipt", "21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365"],
] as const;

export default function EvidencePage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · evidence ledger</p>
          <h1>Results without claim inflation.</h1>
          <p className="lede">
            Positive, negative, failed and pending executions remain separate custody objects. The full500 run is now executed and its negative/neutral retrieval result is part of the judge-facing story rather than being overwritten.
          </p>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">FULL500 RECEIPT RETAINED</span>
          <span className="pill pillMuted">NOT SIGNED</span>
          <span className="pill pillMuted">NOT LIVE-MERKLE-COMMITTED</span>
        </div>
      </header>

      <section className="metrics" aria-label="Submission evidence status">
        <article className="metric">
          <span className="metricLabel">Structural gate</span>
          <strong>7/7</strong>
          <span className="small muted">declared live HydraDB invariants</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Primary real dataset</span>
          <strong>500 cases</strong>
          <span className="small muted">LongMemEval-S full500</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Scored retrieval cases</span>
          <strong>470</strong>
          <span className="small muted">ground truth used only for evaluation</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Decision</span>
          <strong>No positive signal</strong>
          <span className="small muted">B/C/D hit-rate comparison</span>
        </article>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / EVIDENCE OBJECTS</span>
        <h2 className="displayTitle">Every state stays visible.</h2>
        <div className="grid twoCol">
          {evidence.map((item) => (
            <article className="panel" key={item.label}>
              <p className="eyebrow">{item.status}</p>
              <h2>{item.label}</h2>
              <p className="muted">{item.detail}</p>
              <p className="mono small compact">claim_ceiling={item.ceiling}</p>
              <div className="actions"><Link className="secondary" href={item.href}>Follow evidence path</Link></div>
            </article>
          ))}
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / FULL500 IDENTITIES</span>
        <h2 className="displayTitle">Hashes link the retained result objects.</h2>
        <div className="stack">
          {hashes.map(([label, hash]) => (
            <div className="panel" key={label}>
              <p className="eyebrow">{label}</p>
              <p className="mono compact">{hash}</p>
            </div>
          ))}
        </div>
        <p className="small muted note">A SHA-256 value establishes byte/object identity for the retained artifact. It does not establish correctness or independent verification.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / MECHANICAL SCIENTIFIC METHOD</span>
        <h2 className="displayTitle">How a result becomes admissible.</h2>
        <div className="flow mono">
          <span>freeze source</span><b>→</b><span>reference graph</span><b>→</b>
          <span>perturb / query</span><b>→</b><span>measure</span><b>→</b>
          <span>first divergence</span><b>→</b><span>recovery / ablation</span><b>→</b>
          <span>statistics</span><b>→</b><span>bounded claim</span>
        </div>
        <p className="small muted note">
          FCO/FCG preserves source → transformation → derived evidence → claim lineage. A graph path establishes the declared dependency route under the executed system; it does not make the underlying claim universally true.
        </p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / BEST USE OF HYDRADB</span>
        <h2 className="displayTitle">The graph-native question.</h2>
        <p className="sectionLead">
          Given a changing memory state, return the current non-superseded evidence path, reconstruct the contradictory history that produced it, and show which upstream dependency changed.
        </p>
        <div className="flow mono">
          <span>Session</span><b>→</b><span>Fact</span><b>→</b><span>Entity</span><b>→</b>
          <span>SUPERSEDED_BY</span><b>→</b><span>current Fact</span><b>→</b><span>provenance path</span>
        </div>
      </section>
    </main>
  );
}
