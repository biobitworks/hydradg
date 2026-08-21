import Link from "next/link";

import GoldenPathStep from "@/components/GoldenPathStep";
import GraphHashComparison from "@/components/GraphHashComparison";

const evidence = [
  {
    label: "LongMemEval full500 retrieval ablation",
    status: "EXECUTED · NEGATIVE/NEUTRAL",
    detail: "500 cases; 470 retrieval-scored; 30 abstentions. B/C/D did not establish a positive Hit@5 advantage over A at the tested K=5 configuration.",
    ceiling: "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
  },
  {
    label: "Hosted HydraDB connectivity + canary",
    status: "CONNECTED · REQUEST-LEVEL TRACEABILITY",
    detail: "The configured database/collection is reachable and the canonical canary relation request succeeds. This is not the same claim as complete hosted graph parity.",
    ceiling: "REMOTE_HYDRADB_CONNECTIVITY_AND_REQUEST_LEVEL_TRACEABILITY_ONLY",
  },
  {
    label: "Expanded 653-FCO / 1,692-edge hosted parity",
    status: "NOT_ESTABLISHED",
    detail: "Full parity still requires scoped FCO/edge counts, missing/extra accounting, canonical identity mapping, and root comparison.",
    ceiling: "EXPANDED_HOSTED_PARITY_REQUIRES_REAL_SCOPED_READBACK",
  },
  {
    label: "Identity reuse accounting",
    status: "PRESENT · DETERMINISTIC",
    detail: "31,672,976 retained occurrences map to 10,854,020 unique keys, for 65.730975% identity reuse. This is not automatically byte, token, or dollar savings.",
    ceiling: "DETERMINISTIC_IDENTITY_REUSE_ACCOUNTING_ONLY",
  },
  {
    label: "Expanded local-model matrix",
    status: "AUDIT REQUIRED BEFORE PROMOTION",
    detail: "Runtime inventory/model-call evidence is retained, but only case-level results with real response receipts and non-synthetic metrics may become primary empirical evidence.",
    ceiling: "NO_EXPANDED_MODEL_CLAIM_WITHOUT_CASE_LEVEL_EXECUTION_RECEIPTS",
  },
  {
    label: "Cost / energy savings",
    status: "NOT MEASURED",
    detail: "Serialized bytes, retrieved context tokens, avoided inference calls, and measured energy remain future measurements rather than current savings claims.",
    ceiling: "NO_COST_SAVINGS_CLAIM_WITHOUT_MEASURED_BYTES_TOKENS_AND_CALLS",
  },
] as const;

const hashes = [
  ["LongMemEval source", "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"],
  ["full500 result", "bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324"],
  ["full500 statistics", "8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc"],
  ["full500 receipt", "21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365"],
] as const;

export default function EvidencePage() {
  return (
    <main>
      <GoldenPathStep
        step={6}
        summary="Trace each visible result back to its evidence class, custody identity, and claim ceiling. This is where a judge verifies that PASS, pending, failed, theoretical, and historical states are not collapsed together."
      />

      <header className="hero">
        <div>
          <p className="eyebrow">Step 06 of 08 · Evidence + FCG</p>
          <h1>Follow the evidence, not the headline.</h1>
          <p className="lede">Every result keeps a provenance path and a claim ceiling. Connectivity is not parity; a hash is not a signature; a development receipt is not automatically empirical execution.</p>
          <div className="actions">
            <Link className="primary" href="/beam-1m">Next · 07 Future Work →</Link>
            <Link className="secondary" href="/track03">← 05 Results</Link>
            <Link className="secondary" href="/knowledge">Open Knowledge Base</Link>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">FULL500 EXECUTED</span>
          <span className="pill pillGood">CANARY READBACK</span>
          <span className="pill pillWarn">PARITY NOT ESTABLISHED</span>
          <span className="pill pillMuted">NOT_SIGNED</span>
        </div>
      </header>

      <GraphHashComparison />

      <section className="computeSection">
        <span className="sectionNumber">06A / EVIDENCE CLASSES</span>
        <h2 className="displayTitle">Different evidence states keep different ceilings.</h2>
        <div className="grid twoCol">
          {evidence.map((item) => (
            <article className="panel" key={item.label}>
              <p className="eyebrow">{item.status}</p>
              <h2>{item.label}</h2>
              <p className="muted">{item.detail}</p>
              <p className="mono small compact">claim_ceiling={item.ceiling}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="computeSection" id="deterministic-identities">
        <span className="sectionNumber">06B / CUSTODY IDENTITIES</span>
        <h2 className="displayTitle">Retained objects are content-addressed.</h2>
        <div className="stack">
          {hashes.map(([label, hash]) => (
            <div className="panel" key={label}>
              <p className="eyebrow">{label}</p>
              <p className="mono compact" style={{ overflowWrap: "anywhere" }}>{hash}</p>
            </div>
          ))}
        </div>
        <p className="small muted note">SHA-256 establishes retained byte/object identity. It does not establish correctness, digital signature, or Merkle commitment by itself.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">06C / PROJECT FCG</span>
        <h2 className="displayTitle">Source → transformation → evidence → claim.</h2>
        <div className="flow mono"><span>source bytes</span><b>→</b><span>KnowledgeAtom</span><b>→</b><span>SeedOfTruth</span><b>→</b><span>FCO/FCG state</span><b>→</b><span>HydraDB projection</span><b>→</b><span>judge-visible claim</span></div>
        <p className="muted">Wrong, superseded, failed, timeout, and corrective states remain in the same graph so a judge can inspect where a perturbation entered and what later inherited or repaired it.</p>
        <div className="actions"><a className="secondary" href="/api/site-fcg">Open site FCG JSON</a><Link className="secondary" href="/graph">Open graph</Link></div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">06D / CONTINUE</span>
        <h2 className="displayTitle">Now show what comes next.</h2>
        <p className="sectionLead">The current submission stops at the established claim ceiling. Step 07 shows the preregistered BEAM and multi-agent program without presenting future work as completed evidence.</p>
        <div className="actions"><Link className="primary" href="/beam-1m">Continue · 07 Future Work →</Link><Link className="secondary" href="/track03">← 05 Results</Link></div>
      </section>
    </main>
  );
}
