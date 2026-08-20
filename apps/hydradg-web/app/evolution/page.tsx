import Link from "next/link";

import PresentationEvolution from "@/components/PresentationEvolution";
import { PRESENTATION_CLAIM_BOUNDARY, PRESENTATION_HISTORY } from "@/lib/presentationLineage";

export default function EvolutionPage() {
  return (
    <main>
      <header className="hero curatedTextHero">
        <div>
          <p className="eyebrow">FCG presentation lineage</p>
          <h1>Keep every version. Change the default view.</h1>
          <p className="lede">
            HydraDG treats the website itself as a custody-bearing projection. New presentation states can supersede older ones without deleting them, while measured context-state numbers remain separate from visual preference.
          </p>
          <div className="actions">
            <Link className="primary" href="/judge">Open current judge view</Link>
            <Link className="secondary" href="/graph">Inspect the FCG</Link>
          </div>
        </div>
      </header>

      <section className="computeSection" style={{ marginTop: 42 }}>
        <span className="sectionNumber">01 / EVOLUTION</span>
        <h2 className="displayTitle">Supersession is lineage, not erasure.</h2>
        <p className="sectionLead">
          The current interface gets primary presentation priority because it is the latest intended judge surface. Historical interfaces remain linked to immutable Git commits and may still carry evidence that matters to later interpretation.
        </p>
        <PresentationEvolution history={PRESENTATION_HISTORY} />
      </section>

      <footer className="computeSection">
        <p className="eyebrow">Claim boundary</p>
        <p className="small muted">{PRESENTATION_CLAIM_BOUNDARY}</p>
      </footer>
    </main>
  );
}
