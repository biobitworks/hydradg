import Link from "next/link";

import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

const EVIDENCE = [
  {
    label: "LongMemEval full500 typed-memory ablation",
    status: "PASS · EXECUTED · NEGATIVE/NEUTRAL RESULT RETAINED",
    detail: "500 cases; 23,867 sessions; 4,776 entities; 3,506 facts; 470 retrieval-scored and 30 abstentions. B/C/D did not establish a positive Hit@5 advantage over A at K=5.",
    ceiling: "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
    href: "/track03",
  },
  {
    label: "Context vs Entropy classification",
    status: "PASS · EXECUTED",
    detail: "18,567 raw findings; 18,555 context-classified; 12 abstentions; 99.9354% classification coverage. The historical Modal item remains USER_ATTESTED_REVOKED and provider_verified=false.",
    ceiling: "CONTEXT_AWARE_SECOND_STAGE_CLASSIFICATION_NOT_GITLEAKS_REPLACEMENT",
    href: "/results/context-vs-entropy",
  },
  {
    label: "Hosted canonical FCG projection/readback",
    status: "PASS · RECEIPT RETAINED",
    detail: "The retained hosted-migration receipt records database hydradg, collection default, 36 canonical FCOs, 24 canonical edges, root match and zero canonical FCO/edge/content-hash delta for the projected graph scope.",
    ceiling: "HOSTED_PROJECTION_AND_READBACK_SCOPE_ONLY",
    href: "/how-to#hosted-hydradb",
  },
  {
    label: "Website FCO identity contract",
    status: "PASS · DETERMINISTIC",
    detail: "Website, Knowledge and release FCOs are content-addressed as fco:<object_sha256>. The deployed /api/release endpoint verifies one canonical 64-hex SHA-256 identity per FCO and rejects conflicting duplicate IDs in its bounded catalog.",
    ceiling: "OBJECT_IDENTITY_NOT_SCIENTIFIC_CORRECTNESS",
    href: "/api/release",
  },
  {
    label: "Reference → poison → antidote visualization",
    status: "PASS · DECLARED SYNTHETIC FIXTURE",
    detail: "Violet reference/normal, orange poison/mutation and blue antidote/restoration are explicit state colors. G*, ΔG*, Cloud Drift, total-variation mutation distance and restoration gain remain separately labeled calculations.",
    ceiling: "SYNTHETIC_INFORMATION_STATE_VISUALIZATION_ONLY",
    href: "/graph",
  },
] as const;

const hashes = [
  ["LongMemEval source", "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"],
  ["full500 result", "bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324"],
  ["full500 statistics", "8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc"],
  ["full500 receipt", "21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365"],
  ["Context-vs-Entropy result artifact", "512be8de14feb8512b5dcb7724df740bc2f027946f9250859f91d37e984d5e91"],
] as const;

export default function EvidencePage() {
  const knowledge = buildKnowledgeProjection();
  const gStarIndex = knowledge.nodes.findIndex((node) => node.payload.slug === "g-star");
  const jsdIndex = knowledge.nodes.findIndex((node) => node.payload.slug === "jensen-shannon-divergence");
  const gStar = gStarIndex >= 0 ? knowledge.nodes[gStarIndex] : null;
  const jsd = jsdIndex >= 0 ? knowledge.nodes[jsdIndex] : null;

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · evidence ledger</p>
          <h1>Executed evidence, bounded claims, no hidden nulls.</h1>
          <p className="lede">The judge ledger contains executed results, retained negative/null evidence, canonical object identities and explicit N/A states where a scalar is not defined. It does not convert unexecuted work into a green badge.</p>
          <div className="actions"><Link className="primary" href="/judge">Judge walkthrough</Link><Link className="secondary" href="/how-to">How to use</Link><Link className="secondary" href="/knowledge">Knowledge Base</Link></div>
        </div>
        <div className="heroStatus"><span className="pill pillGood">FULL500 RETAINED</span><span className="pill pillGood">HOSTED READBACK RECEIPT</span><span className="pill pillMuted">NOT_SIGNED</span><span className="pill pillMuted">NOT_MERKLE_COMMITTED</span></div>
      </header>

      <section className="metrics" aria-label="Submission evidence status">
        <article className="metric"><span className="metricLabel">Track 03</span><strong>500 cases</strong><span className="small muted">470 scored · 30 abstentions</span></article>
        <article className="metric"><span className="metricLabel">Context/Entropy</span><strong>99.9354%</strong><span className="small muted">18,555 / 18,567 classified</span></article>
        <article className="metric"><span className="metricLabel">Hosted parity</span><strong>0 canonical delta</strong><span className="small muted">retained projection scope</span></article>
        <article className="metric"><span className="metricLabel">Track 03 decision</span><strong>No positive signal</strong><span className="small muted">B/C/D vs A Hit@5</span></article>
      </section>

      <section className="computeSection"><span className="sectionNumber">01 / EVIDENCE OBJECTS</span><h2 className="displayTitle">Every judge-facing state has a declared evidence class.</h2><div className="grid twoCol">{EVIDENCE.map((item) => <article className="panel" key={item.label}><p className="eyebrow">{item.status}</p><h2>{item.label}</h2><p className="muted">{item.detail}</p><p className="mono small compact">claim_ceiling={item.ceiling}</p><div className="actions"><Link className="secondary" href={item.href}>Follow evidence path</Link></div></article>)}</div></section>

      <section className="computeSection"><span className="sectionNumber">02 / RETAINED IDENTITIES</span><h2 className="displayTitle">Hashes link exact retained artifacts.</h2><div className="stack">{hashes.map(([label, hash]) => <div className="panel" key={label}><p className="eyebrow">{label}</p><p className="mono compact">{hash}</p></div>)}</div><p className="small muted note">A SHA-256 establishes byte/object identity for the retained artifact. It does not establish correctness or independent verification.</p></section>

      <section className="computeSection">
        <span className="sectionNumber">03 / GOVERNED THEORY + METRIC NAVIGATION</span>
        <h2 className="displayTitle">Academic source → internal Knowledge FCO → exact scorer contract.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">G* design rationale</p>
            <h3>Enßlin &amp; Weig (2010) → HydraDG G* Knowledge FCO</h3>
            <p className="small muted">The paper is design-rationale lineage for an information/free-energy analogy; it does not define HydraDG's exact synthetic-fixture equation.</p>
            {gStar ? <><p className="mono small compact">{gStar.id}</p><p className="mono small compact">object_sha256={gStar.object_sha256}</p><div className="actions"><Link className="secondary" href={`/fco/${encodeURIComponent(gStar.id)}`}>Inspect canonical Knowledge FCO</Link><a className="secondary" href="https://doi.org/10.1103/PhysRevE.82.051112" target="_blank" rel="noreferrer">Authoritative DOI ↗</a></div></> : null}
          </article>
          <article className="panel">
            <p className="eyebrow">Cloud Drift source lineage</p>
            <h3>Lin (1991) → JSD Knowledge FCO</h3>
            <p className="small muted">Cloud Drift is 100 × base-2 Jensen-Shannon divergence from the frozen reference distribution.</p>
            {jsd ? <><p className="mono small compact">{jsd.id}</p><p className="mono small compact">object_sha256={jsd.object_sha256}</p><div className="actions"><Link className="secondary" href={`/fco/${encodeURIComponent(jsd.id)}`}>Inspect canonical Knowledge FCO</Link><Link className="secondary" href="/knowledge#jensen-shannon-divergence">Open KB term</Link></div></> : null}
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / T3–T5 SCORE BOUNDARY</span>
        <h2 className="displayTitle">N/A is data when the scorer inputs do not exist.</h2>
        <div className="grid threeCol">
          {RELEASE_TIMEPOINTS.slice(3).map((point) => <article className="panel" key={point.id}><p className="eyebrow">{point.id}</p><h3>{point.label}</h3><p><strong>Scalar context score: N/A</strong></p><p className="small muted">Reason: no governed state distribution is declared for this project/release timepoint. {point.evidence}</p></article>)}
        </div>
      </section>

      <section className="computeSection"><span className="sectionNumber">05 / PROJECT FCG</span><h2 className="displayTitle">Source → transformation → evidence → claim → artifact.</h2><div className="flow mono"><span>source bytes</span><b>→</b><span>SeedGraph / transform</span><b>→</b><span>KnowledgeAtom</span><b>→</b><span>SeedOfTruth</span><b>→</b><span>FCO/FCG</span><b>→</b><span>HydraDB projection</span><b>→</b><span>website artifact</span></div><div className="actions"><a className="secondary" href="/api/site-fcg">Site FCG JSON</a><a className="secondary" href="/api/release">Release JSON</a><Link className="secondary" href="/graph?q=KnowledgeAtom">Atoms</Link><Link className="secondary" href="/graph?q=SeedOfTruth">Seeds</Link></div></section>
    </main>
  );
}
