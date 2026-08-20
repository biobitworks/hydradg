import {
  eligibilityClaimCeiling,
  eligibilityProofDoc,
  hackHydraEligibility,
} from "@/lib/eligibility";

export default function EligibilityPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · Submission custody</p>
          <h1>Eligibility evidence</h1>
          <p className="lede">
            Each final-form confirmation is mapped to the custody evidence HydraDG can actually
            support. Machine-verifiable chronology, HydraDB execution, and public-release evidence
            stay separate from confirmations that only a human or team can truthfully make.
          </p>
        </div>
      </header>

      <section className="panel">
        <div className="panelHead">
          <div>
            <p className="eyebrow">Custody proof bundle</p>
            <h2>Requirement → work → receipt → FCO → FCG → release artifact</h2>
          </div>
          <span className="pill">FCO / FCG</span>
        </div>
        <div className="flow mono">
          <span>Hack Hydra requirement</span><b>→</b><span>participant work item</span><b>→</b>
          <span>Git / experiment receipt</span><b>→</b><span>FCO</span><b>→</b>
          <span>FCG provenance</span><b>→</b><span>judge artifact</span>
        </div>
        <p className="muted">
          Pre-existing research concepts, third-party datasets, and upstream software attach as
          source/dependency nodes. They are not relabeled as participant-authored Hack Hydra work.
        </p>
        <p>
          <a href={eligibilityProofDoc} target="_blank" rel="noreferrer">
            Open the complete eligibility custody evidence document ↗
          </a>
        </p>
      </section>

      <section className="panel">
        <div className="panelHead">
          <div>
            <p className="eyebrow">Claim ceiling</p>
            <h2 className="mono compact">{eligibilityClaimCeiling}</h2>
          </div>
        </div>
        <p className="muted">
          Hashes, Git history, FCO/FCG receipts, experiment records, HydraDB readbacks, and host
          manifests support an auditable chronology. They do not independently prove first
          authorship, wall-clock truth, another participant&apos;s submission status, or agreement to
          the rules/code of conduct.
        </p>
      </section>

      <section className="grid twoCol">
        {hackHydraEligibility.map((item) => (
          <article className="panel" key={item.key} id={item.key}>
            <div className="panelHead">
              <div>
                <p className="eyebrow">{item.key.replaceAll("_", " ")}</p>
                <h2>{item.label}</h2>
              </div>
              <span className="pill pillMuted">{item.state}</span>
            </div>

            <h3>Form confirmation</h3>
            <p className="note">“{item.formConfirmation}”</p>

            <h3>Custody evidence</h3>
            <ul>
              {item.evidence.map((evidence) => (
                <li key={evidence}>{evidence}</li>
              ))}
            </ul>

            <h3>FCG proof path</h3>
            <div className="flow mono">
              {item.graphPath.map((node, index) => (
                <span key={`${item.key}-${node}`}>
                  {index > 0 ? <b>→</b> : null}
                  <span>{node}</span>
                </span>
              ))}
            </div>

            <p className="small muted note">Boundary: {item.limitation}</p>
          </article>
        ))}
      </section>

      <section className="panel architecture">
        <div>
          <p className="eyebrow">Why this matters</p>
          <h2>The eligibility page is itself part of the release custody graph</h2>
        </div>
        <p className="muted">
          A judge can move from a confirmation to the implementation/evidence it depends on, then
          back to the release artifact that displayed it. A later correction supersedes this page
          through Git/FCG history rather than erasing the prior eligibility state.
        </p>
      </section>
    </main>
  );
}
