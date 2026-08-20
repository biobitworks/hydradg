import Link from "next/link";

import Breadcrumbs from "@/components/Breadcrumbs";
import GraphHashComparison from "@/components/GraphHashComparison";

const RECEIPT_URL =
  "https://github.com/biobitworks/hydradg/blob/hack-hydra/final-hosted-fcg-20260820/eval/hosted_migration_20260820/information_savings/INFORMATION_SAVINGS_RECEIPT_V2.json";

const evidence = [
  {
    label: "LongMemEval full500 typed-memory ablation",
    status: "EXECUTED · NEGATIVE/NEUTRAL",
    detail: "500 cases; 23,867 sessions; 4,776 entities; 3,506 facts; 470 retrieval-scored and 30 abstentions. B/C/D did not establish a positive Hit@5 advantage over A at the tested K=5 route.",
    ceiling: "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
    href: "/track03",
  },
  {
    label: "Context vs Entropy classification",
    status: "EXECUTED",
    detail: "18,567 raw findings; 18,555 context-classified; 12 abstentions; 99.9354% classification coverage. This is a second-stage context classification result, not a replacement for Gitleaks.",
    ceiling: "CONTEXT_AWARE_SECOND_STAGE_CLASSIFICATION_NOT_GITLEAKS_REPLACEMENT",
    href: "/results/context-vs-entropy",
  },
  {
    label: "Canonical atom/key reuse accounting",
    status: "PRESENT · DETERMINISTIC",
    detail: "Retained word+sentence accounting gives 31,672,976 raw occurrences, 10,854,020 unique keys and 20,818,956 duplicate occurrences, for 65.730975% combined identity reuse.",
    ceiling: "RETAINED_DEDUP_ACCOUNTING_INPUTS_AND_DETERMINISTIC_ARITHMETIC_ONLY",
    href: "/best-use#math",
  },
  {
    label: "Whole-corpus download-byte savings",
    status: "NOT_MEASURED",
    detail: "No complete frozen {path,size_bytes,sha256} acquisition manifest exists for the whole corpus. HydraDG does not translate atom reuse into an invented GB-saved number.",
    ceiling: "NO_WHOLE_CORPUS_BYTE_SAVINGS_CLAIM_WITHOUT_HASHED_BYTE_MANIFEST",
    href: "/best-use#download-savings",
  },
  {
    label: "Information compute / energy scenario",
    status: "THEORETICAL_ONLY",
    detail: "A hypothetical dense 7B, 2 FLOPs/parameter/token, one-token-per-duplicate-atom scenario gives 2.91465384×10^17 theoretical FLOPs avoided and 0.809626 Wh theoretical equivalent under an assumed 100 TFLOP/s/W efficiency. Measured energy remains null.",
    ceiling: "THEORETICAL_COMPUTE_SCENARIO_ONLY_NOT_MEASURED_MODEL_OR_ENERGY_SAVINGS",
    href: "/best-use#math",
  },
  {
    label: "Historical hosted canonical projection/readback",
    status: "PASS · HISTORICAL BOUNDED SCOPE",
    detail: "The retained historical T3 receipt covers 36 canonical FCOs and 24 canonical edges with matching bounded roots. It does not establish parity for the later expanded conversation/project FCG.",
    ceiling: "HISTORICAL_36_FCO_24_EDGE_HOSTED_PROJECTION_SCOPE_ONLY",
    href: "/best-use#evidence-state",
  },
  {
    label: "Actual SeedGraph admission",
    status: "NOT_ESTABLISHED",
    detail: "Existing generated accounting/admission artifacts do not by themselves prove that a governed SeedGraph admission operation executed and returned an independently verifiable receipt.",
    ceiling: "SEEDGRAPH_EXECUTION_NOT_ESTABLISHED",
    href: "/best-use#failure-is-evidence",
  },
  {
    label: "Full local HydraDB writeback/readback",
    status: "NOT_ESTABLISHED",
    detail: "The existing full-scale accounting script calculates intended counts but does not prove the full network mutation plus readback. Projected counts are not labeled as written counts here.",
    ceiling: "FULL_LOCAL_HYDRADB_WRITE_AND_READBACK_NOT_ESTABLISHED",
    href: "/best-use#failure-is-evidence",
  },
  {
    label: "Expanded hosted HydraDB parity",
    status: "NOT_ESTABLISHED",
    detail: "The expanded project/conversation graph must compare real hosted FCO IDs, edge IDs and hashes. It cannot inherit the earlier 36/24 parity receipt or local expected counts after a network failure.",
    ceiling: "EXPANDED_HOSTED_PARITY_REQUIRES_REAL_READBACK",
    href: "/best-use#failure-is-evidence",
  },
  {
    label: "Expanded project root scopes",
    status: "RECONCILIATION_REQUIRED",
    detail: "Historical T3 roots remain historical custody evidence. The retained expanded computed root has its own 653-node/1,692-edge scope and must not be described as the same root as the historical 36/24 projection.",
    ceiling: "ROOT_IDENTITY_REQUIRES_EXPLICIT_SCOPE_AND_ALGORITHM",
    href: "/evolution",
  },
] as const;

const hashes = [
  ["LongMemEval source", "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"],
  ["full500 result", "bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324"],
  ["full500 statistics", "8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc"],
  ["full500 receipt", "21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365"],
  ["Information-savings input", "e32e89eaf2035a6ade0646d3f782b32e0b96e628c13f42cf23d095b911a931b5"],
  ["Information-savings calculator contract", "5ab14c2c3b24f1603795bb521b2747f0e475f3a2afd358b4dd19e72eea6b5846"],
  ["Information-savings receipt", "8d60ab68f989e88aec9446fc06739d2c52f4af911b673af058889c9f52afdf36"],
] as const;

export default function EvidencePage() {
  return (
    <main>
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Why HydraDB", href: "/best-use" },
          { label: "Evidence Ledger" },
        ]}
        summaryText="Separate executed benchmark evidence, deterministic accounting, theoretical scenarios, historical bounded parity, and operations that remain intentionally not established."
      />

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · evidence ledger</p>
          <h1>Results without claim inflation.</h1>
          <p className="lede">Positive, negative, failed, blocked, modeled and pending states remain separate custody objects. A generated receipt does not establish the underlying operation unless the operation actually executed and read back successfully.</p>
          <div className="actions">
            <Link className="primary" href="/best-use">Why HydraDB · show the math</Link>
            <Link className="secondary" href="/how-to">How to use</Link>
            <Link className="secondary" href="/knowledge">Knowledge Base</Link>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">FULL500 EXECUTED</span>
          <span className="pill pillGood">DEDUP ACCOUNTING PRESENT</span>
          <span className="pill pillMuted">ENERGY THEORETICAL ONLY</span>
          <span className="pill pillMuted">NOT_SIGNED</span>
          <span className="pill pillMuted">NOT_MERKLE_COMMITTED</span>
        </div>
      </header>

      <section className="metrics" aria-label="Current evidence state">
        <article className="metric"><span className="metricLabel">Combined identity reuse</span><strong>65.730975%</strong><span className="small muted">retained word+sentence accounting</span></article>
        <article className="metric"><span className="metricLabel">Duplicate occurrences</span><strong>20,818,956</strong><span className="small muted">not tokenizer tokens; not bytes</span></article>
        <article className="metric"><span className="metricLabel">7B scenario</span><strong>0.809626 Wh</strong><span className="small muted">theoretical equivalent · measured energy null</span></article>
        <article className="metric"><span className="metricLabel">Executed benchmark</span><strong>500 cases</strong><span className="small muted">LongMemEval-S full500</span></article>
      </section>

      <GraphHashComparison />

      <section className="computeSection">
        <span className="sectionNumber">01 / EVIDENCE OBJECTS</span>
        <h2 className="displayTitle">Every evidence class keeps its own ceiling.</h2>
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

      <section className="computeSection" id="deterministic-identities">
        <span className="sectionNumber">02 / RETAINED IDENTITIES</span>
        <h2 className="displayTitle">The calculation chain is content-addressed.</h2>
        <div className="stack">
          {hashes.map(([label, hash]) => (
            <div className="panel" key={label}>
              <p className="eyebrow">{label}</p>
              <p className="mono compact" style={{ overflowWrap: "anywhere" }}>{hash}</p>
            </div>
          ))}
        </div>
        <div className="actions"><a className="secondary" href={RECEIPT_URL} target="_blank" rel="noreferrer">Open deterministic receipt JSON ↗</a></div>
        <p className="small muted note">A SHA-256 establishes the identity of the canonical input, contract or receipt. It does not establish scientific correctness, execution of an external service, or a digital signature.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / GOVERNED THEORY + METRIC NAVIGATION</span>
        <h2 className="displayTitle">Academic source → Knowledge FCO → exact application contract.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">G* design rationale</p>
            <h3>Enßlin &amp; Weig (2010) → HydraDG G* Knowledge FCO</h3>
            <p className="small muted">Design-rationale lineage for an information/free-energy analogy; it does not define HydraDG&apos;s exact synthetic-fixture equation.</p>
            <p className="mono small compact" style={{ overflowWrap: "anywhere" }}>fco:92f319f1b3229895d587f6b4fb1b1f856104dd3fbb2624ce07821bd75686b56b</p>
            <div className="actions"><Link className="secondary" href="/fco/fco%3A92f319f1b3229895d587f6b4fb1b1f856104dd3fbb2624ce07821bd75686b56b">Inspect canonical Knowledge FCO</Link><a className="secondary" href="https://doi.org/10.1103/PhysRevE.82.051112" target="_blank" rel="noreferrer">Authoritative DOI ↗</a></div>
          </article>
          <article className="panel">
            <p className="eyebrow">Cloud Drift source lineage</p>
            <h3>Lin (1991) → Jensen-Shannon Knowledge FCO</h3>
            <p className="small muted">Cloud Drift is 100 × base-2 Jensen-Shannon divergence from the frozen reference distribution in the synthetic state lane.</p>
            <p className="mono small compact" style={{ overflowWrap: "anywhere" }}>fco:7fa58bb310fedd8a90a5214d9127fca7acc5d596f1dae4e105b3d28028d8c409</p>
            <div className="actions"><Link className="secondary" href="/fco/fco%3A7fa58bb310fedd8a90a5214d9127fca7acc5d596f1dae4e105b3d28028d8c409">Inspect canonical Knowledge FCO</Link><Link className="secondary" href="/knowledge#jensen-shannon-divergence">Open KB term</Link></div>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / PROJECT FCG</span>
        <h2 className="displayTitle">Source → atom → seed → state → release.</h2>
        <div className="flow mono"><span>source bytes</span><b>→</b><span>KnowledgeAtom</span><b>→</b><span>SeedOfTruth</span><b>→</b><span>FCO/FCG state</span><b>→</b><span>HydraDB projection</span><b>→</b><span>website evidence</span></div>
        <p className="muted">The fractal property is the repeated custody pattern—identity, context, governance and provenance—at source, atom, experiment, deployment and project scales. Lower-level roots can become evidence inside higher-level FCOs without erasing their original scope.</p>
        <div className="actions"><a className="secondary" href="/api/site-fcg">Open site FCG JSON</a><Link className="secondary" href="/graph?q=KnowledgeAtom">Knowledge Atoms</Link><Link className="secondary" href="/graph?q=SeedOfTruth">Seeds of Truth</Link></div>
      </section>
    </main>
  );
}
