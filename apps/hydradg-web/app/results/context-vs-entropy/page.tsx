import Link from "next/link";
import PublicBackendStatus from "@/components/PublicBackendStatus";

export const metadata = {
  title: "Context vs Entropy Secret Classification | HydraDG",
  description: "Judge Experiment: HydraDB context-aware secret classification versus pattern/entropy detection.",
};

const CATEGORIES = [
  { name: "DETERMINISTIC_HASH", count: 18428, percentage: "99.25%", class: "pillGood", description: "Content-addressed SeedGraph SHA-256 cache identifiers in deterministic cache paths.", example: "HydraDG_DaisyTrain_v0.3.7/evidence/track03/.../seedgraph/cache/00049980b80...json" },
  { name: "TOY_NON_AUTHENTICATING_KEY", count: 126, percentage: "0.68%", class: "pillGood", description: "Intentionally public non-authenticating toy signature key fixtures declared in FCO package seals.", example: "archive/hydradg_video_final_reconciled_v3/fcg/TOY_SEAL_FCO_BUNDLE.jsonl" },
  { name: "REVOKED_HISTORICAL_CREDENTIAL", count: 1, percentage: "0.01%", class: "pillMuted", description: "Historical Modal token ID line in ECA retry log; user-attested revoked (USER_ATTESTED_REVOKED).", example: "HydraDG_DaisyTrain_v0.3.3/logs/20260817_081811_ECA_RETRY_2.log (Token: ak-REDACTED)" },
  { name: "UNEXPLAINED_SECRET_CANDIDATE", count: 12, percentage: "0.06%", class: "pillWarn", description: "Abstentions reserved for human/operator review; not silently allowlisted.", example: "apps/hydradg-web/.next/cache/.previewinfo" },
] as const;

export default function ContextVsEntropyPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Judge Experiment · Secret Classification Benchmark</p>
          <h1 style={{ fontSize: "clamp(36px, 5vw, 72px)" }}>Context vs. Entropy</h1>
          <p className="lede">Raw pattern/entropy detectors flag 18,567 candidates across repository history. HydraDB + FCO/FCG graph context classifies 18,555 of those raw findings (99.9354%) into reviewed provenance classes while retaining 12 unexplained candidates as abstentions.</p>
          <div className="actions"><Link className="primary" href="#flow">View Classification Flow</Link><Link className="secondary" href="#vithia-card">View Vithia Supplementary Card</Link><Link className="secondary" href="/evidence">Evidence ledger</Link></div>
        </div>
      </header>

      <PublicBackendStatus />

      <section className="computeSection" id="flow">
        <span className="sectionNumber">01 / CLASSIFICATION PIPELINE</span>
        <h2 className="displayTitle">Pattern Detector → HydraDB Context Graph → Deterministic Decision</h2>
        <div className="grid fourCol" style={{ marginTop: "2rem" }}>
          <article className="panel"><p className="eyebrow">STEP 01</p><h3>Raw Pattern Detector</h3><p className="small muted">Gitleaks built-in pattern/rule scanning provides the first-stage candidate stream.</p><div className="pill pillMuted" style={{ marginTop: "1rem" }}>Input Stream</div></article>
          <article className="panel"><p className="eyebrow">STEP 02</p><h3>18,567 Flags</h3><p className="small muted">Candidate matches retained across repository history.</p><div className="pill pillWarn" style={{ marginTop: "1rem" }}>Raw Findings</div></article>
          <article className="panel"><p className="eyebrow">STEP 03</p><h3>HydraDB Context Graph</h3><p className="small muted">Namespace: <code>hydradg-context-entropy-20260820</code></p><div className="pill pillGood" style={{ marginTop: "1rem" }}>FCO/FCG Provenance</div></article>
          <article className="panel"><p className="eyebrow">STEP 04</p><h3>99.9354% Classified</h3><p className="small muted">18,555 classified · 12 abstentions reserved for review.</p><div className="pill pillGood" style={{ marginTop: "1rem" }}>Context Decisions</div></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / EXPERIMENT RESULTS</span>
        <h2 className="displayTitle">Summary Metrics &amp; Category Breakdown</h2>
        <div className="grid fourCol" style={{ margin: "2rem 0" }}>
          <div className="panel"><p className="eyebrow">RAW FINDINGS</p><h2 style={{ fontSize: "36px", margin: "0.5rem 0" }}>18,567</h2><p className="small muted">Total raw detector matches</p></div>
          <div className="panel"><p className="eyebrow">CONTEXT CLASSIFIED</p><h2 style={{ fontSize: "36px", margin: "0.5rem 0", color: "var(--color-good, #10b981)" }}>18,555</h2><p className="small muted">99.9354% coverage</p></div>
          <div className="panel"><p className="eyebrow">ABSTENTIONS</p><h2 style={{ fontSize: "36px", margin: "0.5rem 0", color: "var(--color-warn, #f59e0b)" }}>12</h2><p className="small muted">Unexplained secret candidates</p></div>
          <div className="panel"><p className="eyebrow">REVOKED CREDENTIALS</p><h2 style={{ fontSize: "36px", margin: "0.5rem 0" }}>1</h2><p className="small muted">User-attested revoked historical item</p></div>
        </div>
        <div className="grid twoCol">{CATEGORIES.map((cat) => <article className="panel" key={cat.name}><div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><span className={`pill ${cat.class}`}>{cat.name}</span><strong style={{ fontSize: "20px" }}>{cat.count.toLocaleString()} ({cat.percentage})</strong></div><p style={{ marginTop: "1rem" }}>{cat.description}</p><p className="small muted" style={{ marginTop: "0.5rem", wordBreak: "break-all" }}><strong>Public-Safe Example:</strong> <code>{cat.example}</code></p></article>)}</div>
        <p className="small muted note">This second-stage contextual classification does not replace Gitleaks and does not establish that no secret can exist under every detector or context.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / MODAL TOKEN PRESERVATION</span>
        <h2 className="displayTitle">User-Attested Revoked Credential Record</h2>
        <div className="panel" style={{ borderLeft: "4px solid var(--color-warn, #f59e0b)" }}>
          <p className="eyebrow">REVOKED_HISTORICAL_CREDENTIAL · USER_ATTESTED_REVOKED</p>
          <h3>Historical Modal Token Identifier</h3>
          <p>The historical Modal token-ID line is classified as <strong>REVOKED_HISTORICAL_CREDENTIAL</strong> based on user attestation.</p>
          <p className="small muted" style={{ marginTop: "0.5rem" }}><strong>Evidence Basis:</strong> <code>USER_ATTESTED_REVOKED</code> · <strong>Provider Verified:</strong> <code>false</code>. Credential values are not reproduced here.</p>
        </div>
      </section>

      <section className="computeSection" id="vithia-card">
        <span className="sectionNumber">04 / SUPPLEMENTARY CARD</span>
        <h2 className="displayTitle">Vithia / Pythia-14m Training Baseline Repair</h2>
        <div className="panel" style={{ background: "rgba(255, 255, 255, 0.03)", borderRadius: "12px", padding: "2rem" }}>
          <p className="eyebrow">PRESERVED FAILURE CONTROL → REPAIRED BASELINE → REFERENCE BASIN</p>
          <div className="grid fourCol" style={{ margin: "1.5rem 0" }}>
            <div><p className="small muted">01. Failure Control</p><strong>VITHIA-OVERNIGHT-01</strong><p className="small" style={{ color: "var(--color-bad, #ef4444)" }}>Step 0 Divergence (AdamW eps=1e-8)</p></div>
            <div><p className="small muted">02. Repaired Config</p><strong>AdamW lr=1e-4, eps=1e-5</strong><p className="small" style={{ color: "var(--color-good, #10b981)" }}>grad_clip_norm=1.0 · 100% finite reference runs</p></div>
            <div><p className="small muted">03. Reference Basin</p><strong>5-Seed Baseline Suite</strong><p className="small">Loss: 10.8424 ± 0.0020</p></div>
            <div><p className="small muted">04. FCO Admission</p><strong>Turn 1 Admitted</strong><p className="small">fco:0f63d48a... (PASS)</p></div>
          </div>
          <div className="panel" style={{ background: "rgba(0,0,0,0.2)", marginTop: "1rem" }}><p className="small muted"><strong>Explicit Claim Ceiling Notice:</strong> This supplementary card documents a reproducible, numerically stable Pythia-14m reference baseline process. It does NOT claim improved LM accuracy, convergence superiority, LongMemEval superiority, or end-to-end QA improvement.</p></div>
        </div>
      </section>
    </main>
  );
}
