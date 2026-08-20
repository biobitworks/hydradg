import Link from "next/link";

import Breadcrumbs from "@/components/Breadcrumbs";
import { buildKnowledgeProjection } from "@/lib/knowledgeFcg";
import { RELEASE_TIMEPOINTS } from "@/lib/releaseTimepoints";

const RECEIPT_URL =
  "https://github.com/biobitworks/hydradg/blob/main/eval/hosted_migration_20260820/information_savings/INFORMATION_SAVINGS_RECEIPT_V2.json";

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
    label: "Canonical atom/key reuse accounting",
    status: "PASS · DETERMINISTIC ACCOUNTING",
    detail: "Retained word+sentence accounting gives 31,672,976 raw occurrences, 10,854,020 unique keys and 20,818,956 duplicate occurrences: 65.730975% combined identity reuse.",
    ceiling: "RETAINED_DEDUP_ACCOUNTING_INPUTS_AND_DETERMINISTIC_ARITHMETIC_ONLY",
    href: "/best-use#math",
  },
  {
    label: "Whole-corpus download-byte savings",
    status: "NOT_MEASURED",
    detail: "No complete frozen {path,size_bytes,sha256} manifest exists for all downloaded corpus objects. HydraDG does not translate atom reuse into an invented GB-saved claim.",
    ceiling: "NO_WHOLE_CORPUS_BYTE_SAVINGS_CLAIM_WITHOUT_HASHED_BYTE_MANIFEST",
    href: "/best-use#download-savings",
  },
  {
    label: "Information compute / energy scenario",
    status: "THEORETICAL_ONLY",
    detail: "A hypothetical dense 7B, 2 FLOPs/parameter/token, one-token-per-duplicate-atom scenario gives 2.91465384×10^17 theoretical FLOPs avoided and 0.809626 Wh theoretical equivalent at the declared efficiency assumption. Measured energy remains null.",
    ceiling: "THEORETICAL_COMPUTE_SCENARIO_ONLY_NOT_MEASURED_MODEL_OR_ENERGY_SAVINGS",
    href: "/best-use#math",
  },
  {
    label: "Historical hosted canonical FCG projection/readback",
    status: "PASS · HISTORICAL BOUNDED SCOPE",
    detail: "The retained T3 hosted-migration receipt covers database hydradg, 36 canonical FCOs and 24 canonical edges with matching bounded roots. It does not establish parity for the later expanded project/conversation graph.",
    ceiling: "HISTORICAL_36_FCO_24_EDGE_HOSTED_PROJECTION_SCOPE_ONLY",
    href: "/how-to#hosted-hydradb",
  },
  {
    label: "Actual SeedGraph admission",
    status: "NOT_ESTABLISHED",
    detail: "A generated accounting/admission receipt is not treated as proof that the governed SeedGraph operation executed. A real admission result/ledger receipt is required.",
    ceiling: "SEEDGRAPH_EXECUTION_NOT_ESTABLISHED",
    href: "/best-use#failure-is-evidence",
  },
  {
    label: "Full local HydraDB writeback/readback",
    status: "NOT_ESTABLISHED",
    detail: "Projected node/relation counts are not treated as a completed full network mutation plus readback. The operation remains open until actual write IDs and readback evidence exist.",
    ceiling: "FULL_LOCAL_HYDRADB_WRITE_AND_READBACK_NOT_ESTABLISHED",
    href: "/best-use#failure-is-evidence",
  },
  {
    label: "Expanded hosted HydraDB parity",
    status: "NOT_ESTABLISHED",
    detail: "The expanded graph must compare real hosted FCO IDs, edge IDs and hashes. It cannot inherit local expected counts or the earlier 36/24 historical green state.",
    ceiling: "EXPANDED_HOSTED_PARITY_REQUIRES_REAL_READBACK",
    href: "/best-use#failure-is-evidence",
  },
  {
    label: "Website FCO identity contract",
    status: "PASS · DETERMINISTIC",
    detail: "Website, Knowledge and release FCOs are content-addressed as fco:<object_sha256>. The deployed /api/release endpoint verifies one canonical 64-hex SHA-256 identity per FCO in its bounded catalog.",
    ceiling: "OBJECT_IDENTITY_NOT_SCIENTIFIC_CORRECTNESS",
    href: "/api/release",
  },
  {
    label: "Reference → poison → antidote visualization",
    status: "PASS · DECLARED SYNTHETIC FIXTURE",
    detail: "Violet reference/normal, orange poison/mutation and blue antidote/restoration are explicit state colors. G*, ΔG*, Cloud Drift, total-variation mutation distance and restoration gain remain separate calculations.",
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
  ["Information-savings input", "e32e89eaf2035a6ade0646d3f782b32e0b96e628c13f42cf23d095b911a931b5"],
  ["Information-savings calculation contract", "5ab14c2c3b24f1603795bb521b2747f0e475f3a2afd358b4dd19e72eea6b5846"],
  ["Information-savings receipt", "8d60ab68f989e88aec9446fc06739d2c52f4af911b673af058889c9f52afdf36"],
] as const;

export default function EvidencePage() {
  const knowledge = buildKnowledgeProjection();
  const gStarIndex = knowledge.nodes.findIndex((node) => node.payload.slug === "g-star");
  const jsdIndex = knowledge.nodes.findIndex((node) => node.payload.slug === "jensen-shannon-divergence");
  const gStar = gStarIndex >= 0 ? knowledge.nodes[gStarIndex] : null;
  const jsd = jsdIndex >= 0 ? knowledge.nodes[jsdIndex] : null;

  return (
    <main>
      <Breadcrumbs
        items={[{ label: "Home", href: "/" }, { label: "Why HydraDB", href: "/best-use" }, { label: "Evidence Ledger" }]}
        summaryText="Look for evidence classes: executed benchmark, deterministic accounting, theoretical scenarios, historical bounded parity, and operations that remain intentionally NOT_ESTABLISHED."
      />

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · evidence ledger</p>
          <h1>Executed evidence, bounded claims, no hidden nulls.</h1>
          <p className="lede">The judge ledger keeps executed results, retained negative/null evidence, deterministic accounting, theoretical scenarios, canonical identities and explicit N/A/NOT_ESTABLISHED states separate. It does not convert unexecuted work into a green badge.</p>
          <div className="actions"><Link className="primary" href="/judge">Judge walkthrough</Link><Link className="secondary" href="/best-use">Why HydraDB · math</Link><Link className="secondary" href="/how-to">How to use</Link><Link className="secondary" href="/knowledge">Knowledge Base</Link></div>
        </div>
        <div className="heroStatus"><span className="pill pillGood">FULL500 RETAINED</span><span className="pill pillGood">DEDUP ACCOUNTING PRESENT</span><span className="pill pillMuted">ENERGY THEORETICAL ONLY</span><span className="pill pillMuted">NOT_SIGNED</span><span className="pill pillMuted">NOT_MERKLE_COMMITTED</span></div>
      </header>

      <section className="metrics" aria-label="Submission evidence status">
        <article className="metric"><span className="metricLabel">Track 03</span><strong>500 cases</strong><span className="small muted">470 scored · 30 abstentions</span></article>
        <article className="metric"><span className="metricLabel">Context/Entropy</span><strong>99.9354%</strong><span className="small muted">18,555 / 18,567 classified</span></article>
        <article className="metric"><span className="metricLabel">Identity reuse</span><strong>65.730975%</strong><span className="small muted">20,818,956 duplicate word+sentence occurrences</span></article>
        <article className="metric"><span className="metricLabel">7B scenario</span><strong>0.809626 Wh</strong><span className="small muted">theoretical equivalent · measured energy null</span></article>
      </section>

      <section className="computeSection"><span className="sectionNumber">01 / EVIDENCE OBJECTS</span><h2 className="displayTitle">Every judge-facing state has a declared evidence class.</h2><div className="grid twoCol">{EVIDENCE.map((item) => <article className="panel" key={item.label}><p className="eyebrow">{item.status}</p><h2>{item.label}</h2><p className="muted">{item.detail}</p><p className="mono small compact">claim_ceiling={item.ceiling}</p><div className="actions"><Link className="secondary" href={item.href}>Follow evidence path</Link></div></article>)}</div></section>

      <section className="computeSection"><span className="sectionNumber">02 / RETAINED IDENTITIES</span><h2 className="displayTitle">Hashes link exact retained artifacts and calculations.</h2><div className="stack">{hashes.map(([label, hash]) => <div className="panel" key={label}><p className="eyebrow">{label}</p><p className="mono compact" style={{ overflowWrap: "anywhere" }}>{hash}</p></div>)}</div><div className="actions"><a className="secondary" href={RECEIPT_URL} target="_blank" rel="noreferrer">Open deterministic savings receipt ↗</a></div><p className="small muted note">A SHA-256 establishes byte/object identity for the retained artifact. It does not establish correctness, model execution, external-service execution, or a digital signature.</p></section>

      <section className="computeSection">
        <span className="sectionNumber">03 / GOVERNED THEORY + METRIC NAVIGATION</span>
        <h2 className="displayTitle">Academic source → internal Knowledge FCO → exact scorer contract.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">G* design rationale</p>
            <h3>Enßlin &amp; Weig (2010) → HydraDG G* Knowledge FCO</h3>
            <p className="small muted">The paper is design-rationale lineage for an information/free-energy analogy; it does not define HydraDG&apos;s exact synthetic-fixture equation.</p>
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

      <section className="computeSection" id="root-scopes">
        <span className="sectionNumber">05 / ROOT SCOPES</span>
        <h2 className="displayTitle">Historical parity stays historical; expanded parity must be re-earned.</h2>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">HISTORICAL BOUNDED MATCH</p><h3>T3 canonical FCO root</h3><p className="mono small compact" style={{ overflowWrap: "anywhere" }}>d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1</p><p className="muted">Retained for the historical 36-FCO hosted projection scope.</p></article>
          <article className="panel"><p className="eyebrow">HISTORICAL BOUNDED MATCH</p><h3>T3 canonical edge root</h3><p className="mono small compact" style={{ overflowWrap: "anywhere" }}>7297d87808a51bddcc4584387f10c79571bc66fe89a3339024890b5d77084fab</p><p className="muted">Retained for the historical 24-edge hosted projection scope.</p></article>
          <article className="panel"><p className="eyebrow">RECONCILIATION_REQUIRED</p><h3>Expanded project FCG computed root</h3><p className="mono small compact" style={{ overflowWrap: "anywhere" }}>bb0adb5a6453a6493e51363f33e7782b3d79dd82b27ceb8678173ce53f1ce72b</p><p className="muted">Retained experimental-branch scope recorded as 653 FCO nodes / 1,692 edges. This production release does not claim expanded hosted parity for that root.</p></article>
          <article className="panel"><p className="eyebrow">NOT_MERKLE_COMMITTED</p><h3>Computed root ≠ external commitment</h3><p className="muted">A deterministic root can identify a bounded set/order. It is not called a committed Merkle root unless an actual commitment operation and receipt exist.</p></article>
        </div>
      </section>

      <section className="computeSection"><span className="sectionNumber">06 / PROJECT FCG</span><h2 className="displayTitle">Source → transformation → evidence → claim → artifact.</h2><div className="flow mono"><span>source bytes</span><b>→</b><span>KnowledgeAtom</span><b>→</b><span>SeedOfTruth</span><b>→</b><span>FCO/FCG state</span><b>→</b><span>HydraDB projection</span><b>→</b><span>website artifact</span></div><p className="muted">The fractal design repeats identity, context, governance and provenance at source, atom, experiment, deployment and project scales. Lower-level roots can become evidence inside higher-level FCOs without erasing their original scope.</p><div className="actions"><a className="secondary" href="/api/site-fcg">Site FCG JSON</a><a className="secondary" href="/api/release">Release JSON</a><Link className="secondary" href="/graph?q=KnowledgeAtom">Atoms</Link><Link className="secondary" href="/graph?q=SeedOfTruth">Seeds</Link></div></section>
    </main>
  );
}
