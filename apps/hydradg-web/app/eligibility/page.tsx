import { eligibilityClaimCeiling, hackHydraEligibility } from "@/lib/eligibility";

export default function EligibilityPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · Submission custody</p>
          <h1>Eligibility evidence</h1>
          <p className="lede">
            HydraDG exposes the evidence supporting the team&apos;s submission confirmations while
            keeping human attestations distinct from machine-verifiable custody.
          </p>
        </div>
      </header>

      <section className="panel">
        <div className="panelHead">
          <div>
            <p className="eyebrow">Claim ceiling</p>
            <h2 className="mono compact">{eligibilityClaimCeiling}</h2>
          </div>
        </div>
        <p className="muted">
          Hashes, Git history, FCO/FCG receipts, experiment records, and host/runtime manifests can
          support an auditable chronology. They do not independently prove first authorship,
          wall-clock truth, another participant&apos;s submission status, or agreement to rules.
        </p>
      </section>

      <section className="grid twoCol">
        {hackHydraEligibility.map((item) => (
          <article className="panel" key={item.key}>
            <div className="panelHead">
              <div>
                <p className="eyebrow">{item.key.replaceAll("_", " ")}</p>
                <h2>{item.label}</h2>
              </div>
              <span className="pill pillMuted">{item.state}</span>
            </div>
            <h3>Evidence target</h3>
            <ul>
              {item.evidence.map((evidence) => (
                <li key={evidence}>{evidence}</li>
              ))}
            </ul>
            <p className="small muted note">{item.limitation}</p>
          </article>
        ))}
      </section>

      <section className="panel architecture">
        <div>
          <p className="eyebrow">Submission evidence path</p>
          <h2>Requirement → work → execution → artifact → submission</h2>
        </div>
        <div className="flow mono">
          <span>form requirement</span><b>→</b><span>Git/FCO requirement</span><b>→</b>
          <span>implementation</span><b>→</b><span>experiment receipt</span><b>→</b>
          <span>tested commit</span><b>→</b><span>submission manifest</span>
        </div>
      </section>
    </main>
  );
}
