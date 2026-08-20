import Link from "next/link";

import Breadcrumbs from "@/components/Breadcrumbs";

const RECEIPT_URL =
  "https://github.com/biobitworks/hydradg/blob/hack-hydra/final-hosted-fcg-20260820/eval/hosted_migration_20260820/information_savings/INFORMATION_SAVINGS_RECEIPT_V2.json";
const CALCULATOR_URL =
  "https://github.com/biobitworks/hydradg/blob/hack-hydra/final-hosted-fcg-20260820/scripts/calculate_information_savings.py";

const evidenceStates = [
  ["Repository artifact chain", "PRESENT", "Hash-addressed artifacts and FCO/FCG lineage are retained in GitHub."],
  ["LongMemEval full500", "EXECUTED", "500 cases; 470 retrieval-scored; 30 abstentions; no positive B/C/D Hit@5 signal."],
  ["Atom/key dedup accounting", "PRESENT", "Deterministic arithmetic over the retained word + sentence accounting inputs."],
  ["Download-byte savings", "NOT_MEASURED", "A complete {path,size_bytes,sha256} acquisition manifest has not yet been frozen."],
  ["Energy savings", "THEORETICAL_ONLY", "FLOP and energy-equivalent scenario only; measured electrical energy is null."],
  ["SeedGraph admission", "NOT_ESTABLISHED", "A generated receipt is not treated as evidence of an executed SeedGraph admission."],
  ["Full local HydraDB write/read", "NOT_ESTABLISHED", "The existing accounting script does not prove a full network write plus readback."],
  ["Expanded hosted parity", "NOT_ESTABLISHED", "The retained 36-node/24-edge hosted receipt remains a historical bounded scope only."],
  ["Root scopes", "RECONCILIATION_REQUIRED", "Historical T3 roots and expanded conversation/project roots remain explicitly scoped."],
] as const;

const judgeFit = [
  {
    title: "A particularly strong graph data model",
    body: "Canonical FCO identities are reused while typed FCG edges preserve source, time, supersession, contradiction, membership and spatiotemporal context. One content identity can participate in many contexts without becoming many unrelated copies.",
    href: "/knowledge#fractal-custody-object-fco",
    link: "Open FCO terminology",
  },
  {
    title: "A novel retrieval or reasoning approach",
    body: "HydraDG treats similarity as only one candidate signal. Retrieval can carry graph context, custody state, source identity, time, contradiction, abstention and claim ceilings into the reasoning surface.",
    href: "/how-to",
    link: "Follow the retrieval walkthrough",
  },
  {
    title: "Interesting use of relationships, traversal or context",
    body: "A judge can move from source bytes to KnowledgeAtom to SeedOfTruth to evidence, state and release, or start from a reused hash and traverse every retained location/time where that identity appears.",
    href: "/graph",
    link: "Traverse the 4D FCG",
  },
  {
    title: "Harder to pull off with vector or relational approaches alone",
    body: "Vector similarity does not prove exact identity or provenance. Relational systems can encode these facts, but recursive content-addressed custody, supersession and multi-scale traversal require substantial application machinery. HydraDG uses the graph itself as the context/governance surface; this is a fit claim, not an impossibility claim about other databases.",
    href: "/evidence",
    link: "Inspect bounded evidence",
  },
] as const;

export default function BestUsePage() {
  return (
    <main>
      <Breadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Judge", href: "/judge" },
          { label: "Best Use of HydraDB" },
        ]}
        summaryText="Look for the separation between exact identity reuse, measured benchmark evidence, modeled scale accounting, and operations that remain intentionally NOT_ESTABLISHED."
      />

      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · Best Use of HydraDB · show the math</p>
          <h1>Store identity once. Traverse context many times.</h1>
          <p className="lede">
            HydraDG uses a content-addressed graph to separate canonical identity from the many places, times,
            models and claims that reference it. The scale-economics calculator is deterministic and fail-closed:
            input hash → calculation-contract hash → output receipt hash. A mismatch is evidence, not a value to hide.
          </p>
          <div className="actions">
            <Link className="primary" href="/graph">Open the graph</Link>
            <Link className="secondary" href="/evidence">Evidence ledger</Link>
            <Link className="secondary" href="/how-to">How to use</Link>
            <Link className="secondary" href="/knowledge">Terminology / KB</Link>
          </div>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">DETERMINISTIC ACCOUNTING</span>
          <span className="pill pillGood">FULL500 EXECUTED</span>
          <span className="pill pillMuted">ENERGY THEORETICAL ONLY</span>
          <span className="pill pillMuted">EXPANDED PARITY NOT ESTABLISHED</span>
        </div>
      </header>

      <section className="metrics" aria-label="Deterministic scale accounting">
        <article className="metric">
          <span className="metricLabel">Combined identity reuse</span>
          <strong>65.730975%</strong>
          <span className="small muted">31,672,976 raw occurrences → 10,854,020 unique keys</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Duplicate occurrences</span>
          <strong>20,818,956</strong>
          <span className="small muted">word + sentence retained accounting</span>
        </article>
        <article className="metric">
          <span className="metricLabel">Canonical Parquet footprint</span>
          <strong>1,101,473,790 B</strong>
          <span className="small muted">declared canonical output footprint · not download savings</span>
        </article>
        <article className="metric">
          <span className="metricLabel">7B scenario</span>
          <strong>2.91465384×10¹⁷ FLOPs</strong>
          <span className="small muted">0.809626 Wh theoretical equivalent · NOT measured energy</span>
        </article>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">01 / WHY HYDRADB</span>
        <h2 className="displayTitle">The judging criteria map directly to the graph contract.</h2>
        <div className="grid twoCol">
          {judgeFit.map((item) => (
            <article className="panel" key={item.title}>
              <h2>{item.title}</h2>
              <p className="muted">{item.body}</p>
              <div className="actions"><Link className="secondary" href={item.href}>{item.link}</Link></div>
            </article>
          ))}
        </div>
      </section>

      <section className="computeSection" id="math">
        <span className="sectionNumber">02 / DETERMINISTIC MATH</span>
        <h2 className="displayTitle">The arithmetic is reproducible from retained inputs.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">Word identity reuse</p>
            <h2>28,458,677 − 8,992,941 = 19,465,736</h2>
            <p className="mono small">100 × 19,465,736 / 28,458,677 = 68.400003%</p>
            <p className="muted">This is exact arithmetic over the retained accounting inputs. It is not a new claim that the entire third-party corpus was independently enumerated in this release.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Sentence identity reuse</p>
            <h2>3,214,299 − 1,861,079 = 1,353,220</h2>
            <p className="mono small">100 × 1,353,220 / 3,214,299 = 42.100004%</p>
            <p className="muted">The canonical key can be referenced by many contextual pointers instead of giving every occurrence a new content identity.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Combined retained accounting</p>
            <h2>31,672,976 → 10,854,020</h2>
            <p className="mono small">duplicates = 20,818,956 · identity reuse = 65.730975%</p>
            <p className="muted">This is the strongest current deterministic size/reuse statement because its units are explicit: word/sentence occurrence accounting, not tokenizer tokens or bytes.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Hypothetical 7B compute scenario</p>
            <h2>2 × 7,000,000,000 × 20,818,956</h2>
            <p className="mono small">= 291,465,384,000,000,000 theoretical FLOPs avoided</p>
            <p className="mono small">÷ 100,000,000,000,000 FLOP/s/W ÷ 3600 = 0.809626 Wh</p>
            <p className="muted">This assumes one model token per duplicate atom occurrence. It is a scenario, not a measured Ollama run or measured electrical energy.</p>
          </article>
        </div>
      </section>

      <section className="computeSection" id="download-savings">
        <span className="sectionNumber">03 / DOWNLOAD-BYTE SAVINGS</span>
        <h2 className="displayTitle">The valuable number we refuse to invent.</h2>
        <div className="panel">
          <p className="eyebrow">NOT_MEASURED</p>
          <h2>Whole-corpus duplicate download bytes require a hashed byte manifest.</h2>
          <p className="muted">
            HydraDG can deterministically calculate download/storage reuse once every acquired object contributes
            <code> path</code>, <code>size_bytes</code> and <code>sha256</code>. Until that manifest is frozen,
            the site does not convert atom reuse into a fabricated GB-saved claim.
          </p>
          <div className="flow mono">
            <span>raw bytes = Σ all sizes</span><b>→</b><span>unique bytes = Σ one size / SHA-256</span><b>→</b><span>duplicate bytes = raw − unique</span>
          </div>
          <p className="small muted note">Same SHA-256 + conflicting byte sizes is a hard calculator failure. Missing manifest means NOT_MEASURED.</p>
        </div>
      </section>

      <section className="computeSection" id="determinism">
        <span className="sectionNumber">04 / HASHED CALCULATION CHAIN</span>
        <h2 className="displayTitle">Input → deterministic analysis → output.</h2>
        <div className="stack">
          <article className="panel">
            <p className="eyebrow">Canonical input SHA-256</p>
            <p className="mono compact" style={{ overflowWrap: "anywhere" }}>e32e89eaf2035a6ade0646d3f782b32e0b96e628c13f42cf23d095b911a931b5</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Calculation contract SHA-256</p>
            <p className="mono compact" style={{ overflowWrap: "anywhere" }}>5ab14c2c3b24f1603795bb521b2747f0e475f3a2afd358b4dd19e72eea6b5846</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Deterministic receipt SHA-256</p>
            <p className="mono compact" style={{ overflowWrap: "anywhere" }}>8d60ab68f989e88aec9446fc06739d2c52f4af911b673af058889c9f52afdf36</p>
          </article>
        </div>
        <div className="actions">
          <a className="secondary" href={RECEIPT_URL} target="_blank" rel="noreferrer">Open receipt JSON ↗</a>
          <a className="secondary" href={CALCULATOR_URL} target="_blank" rel="noreferrer">Open calculator source ↗</a>
        </div>
      </section>

      <section className="computeSection" id="failure-is-evidence">
        <span className="sectionNumber">05 / FAILURE IS EVIDENCE</span>
        <h2 className="displayTitle">A red calculation is retained instead of normalized away.</h2>
        <div className="grid twoCol">
          <article className="panel"><p className="eyebrow">FAIL CLOSED</p><h3>Same content hash, different byte size</h3><p className="muted">The byte-manifest calculator rejects the input because one SHA-256 identity cannot truthfully name two different byte lengths in this contract.</p></article>
          <article className="panel"><p className="eyebrow">FAIL CLOSED</p><h3>Output receipt no longer recomputes</h3><p className="muted"><code>--verify</code> returns non-zero when the canonical input and contract do not reproduce the retained output receipt.</p></article>
          <article className="panel"><p className="eyebrow">NOT ESTABLISHED</p><h3>SeedGraph / local HydraDB operation absent</h3><p className="muted">Counting intended nodes does not establish an admission or database write. The operation stays red until a real request and readback exist.</p></article>
          <article className="panel"><p className="eyebrow">NOT ESTABLISHED</p><h3>Hosted readback unavailable</h3><p className="muted">A network failure cannot inherit local expected counts. Expanded parity must compare actual hosted IDs/hashes and fail closed on non-200 readback.</p></article>
        </div>
      </section>

      <section className="computeSection" id="evidence-state">
        <span className="sectionNumber">06 / CURRENT CLAIM STATE</span>
        <h2 className="displayTitle">Green, gray and red lanes are intentionally separate.</h2>
        <div className="stack">
          {evidenceStates.map(([label, state, detail]) => (
            <article className="panel" key={label}>
              <p className="eyebrow">{state}</p>
              <h3>{label}</h3>
              <p className="muted">{detail}</p>
            </article>
          ))}
        </div>
        <p className="mono small compact">
          claim_ceiling=REPOSITORY_ARTIFACT_CHAIN_AND_DEDUP_ACCOUNTING_PRESENT; LONGMEMEVAL_EXECUTED_EVIDENCE_RETAINED; ENERGY_SAVINGS_THEORETICAL_ONLY; ACTUAL_SEEDGRAPH_ADMISSION_FULL_LOCAL_HYDRADB_WRITEBACK_AND_EXPANDED_HOSTED_PARITY_NOT_YET_ESTABLISHED; ROOT_SCOPES_REQUIRE_RECONCILIATION
        </p>
      </section>

      <section className="computeSection" id="fractal-custody">
        <span className="sectionNumber">07 / FRACTAL CUSTODY</span>
        <h2 className="displayTitle">The same context/governance/provenance pattern recurs at every scale.</h2>
        <div className="flow mono">
          <span>source bytes</span><b>→</b><span>KnowledgeAtom</span><b>→</b><span>SeedOfTruth</span><b>→</b><span>experiment/state FCO</span><b>→</b><span>release/project root</span>
        </div>
        <p className="muted">
          A lower-level content-addressed root can become evidence inside a higher-level custody object. That recursive composition—not hashing alone—is the fractal design: identity plus context plus governance plus provenance at each layer.
        </p>
        <div className="actions">
          <Link className="secondary" href="/knowledge">Resolve terms in the KB</Link>
          <Link className="secondary" href="/graph?q=KnowledgeAtom">KnowledgeAtom graph</Link>
          <Link className="secondary" href="/graph?q=SeedOfTruth">SeedOfTruth graph</Link>
          <Link className="primary" href="/judge">Return to judge walkthrough</Link>
        </div>
      </section>
    </main>
  );
}
