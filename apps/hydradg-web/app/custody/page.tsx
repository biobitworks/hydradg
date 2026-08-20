import Link from "next/link";

import { CUSTODY_SEAL, PROJECT_SIGNING_FLOW } from "@/lib/custodySeal";

export default function CustodyPage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow goldText">Golden path · Verify custody</p>
          <h1>Hashing is present. Project signing is not yet complete.</h1>
          <p className="lede">HydraDG uses SHA-256 content identity for FCOs and FCG artifacts. The current project release does not have an admitted Ed25519 signature receipt sealing every current FCO/FCG, so the site must not call the project graph signed or sealed.</p>
          <div className="actions"><Link className="primary goldenCta" href="/evidence">Open evidence ledger</Link><a className="secondary" href="/api/site-fcg">Inspect Site FCG JSON</a></div>
        </div>
      </header>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">01 / CURRENT PROJECT STATE</span>
        <h2 className="displayTitle">Identity ≠ signature.</h2>
        <div className="statusGrid">
          <article className="statusCard gold"><p className="eyebrow">Object identity</p><strong>{CUSTODY_SEAL.object_identity.algorithm}</strong><p className="muted">{CUSTODY_SEAL.object_identity.rule}. {CUSTODY_SEAL.object_identity.meaning}</p></article>
          <article className="statusCard"><p className="eyebrow">Ed25519 project signature</p><strong>{CUSTODY_SEAL.hydradg_project.signature_state}</strong><p className="muted">No current project public-key + detached-signature verification receipt has been admitted for every current project object.</p></article>
          <article className="statusCard"><p className="eyebrow">Merkle / MMR</p><strong>{CUSTODY_SEAL.hydradg_project.merkle_state}</strong><p className="muted">A normal SHA-256 FCO identity is not promoted to a Merkle/MMR commitment.</p></article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">02 / PRIVATE KEY BOUNDARY</span>
        <h2 className="displayTitle">The private key belongs outside the website.</h2>
        <div className="panel goldenPanel">
          <p className="sectionLead">Policy: <span className="mono">{CUSTODY_SEAL.hydradg_project.private_key_policy}</span>.</p>
          <p>The website can render a public key or public-key fingerprint after it is admitted by a real signing receipt. It must never ship the authentic private key in JavaScript, HTML, CSS, image pixels, Git history, HydraDB records or public environment variables.</p>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">03 / PUBLICATION KEY</span>
        <h2 className="displayTitle">A real signed lineage exists—but its scope is the publication.</h2>
        <div className="panel">
          <p className="eyebrow">FCO publication v1 · Ed25519</p>
          <p><strong>DOI:</strong> <a className="goldLink" href={`https://doi.org/${CUSTODY_SEAL.fco_publication_v1.doi}`}>{CUSTODY_SEAL.fco_publication_v1.doi}</a></p>
          <p><strong>Public-key SHA-256 fingerprint:</strong></p>
          <p className="mono compact">{CUSTODY_SEAL.fco_publication_v1.public_key_sha256_fingerprint}</p>
          <p><strong>Signed FCG root prefix:</strong> <span className="mono">{CUSTODY_SEAL.fco_publication_v1.signed_fcg_root_prefix}…</span></p>
          <p className="small muted">Scope: {CUSTODY_SEAL.fco_publication_v1.signature_scope}. This signature cannot be inherited by later HydraDG project objects without a separate signing operation and receipt.</p>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber goldenSectionLabel">04 / REQUIRED PROJECT SIGNING FLOW</span>
        <h2 className="displayTitle">Seal only after the operation exists.</h2>
        <div className="fcgRail">{PROJECT_SIGNING_FLOW.map((step, i) => <div className="fcgStep" key={step}><span className="sectionNumber">{String(i + 1).padStart(2, "0")}</span><strong>{step}</strong></div>)}</div>
        <p className="small muted note">Required successor evidence: actual public key, detached signature, verified signature result and a SigningReceiptFCO linked into the project FCG. Until then, the claim ceiling remains <span className="mono">{CUSTODY_SEAL.hydradg_project.claim_ceiling}</span>.</p>
      </section>

      <section className="computeSection">
        <div className="actions"><Link className="primary goldenCta" href="/evidence">Verify evidence</Link><Link className="secondary" href="/models">Models used</Link><Link className="secondary" href="/">Home MVP</Link></div>
      </section>
    </main>
  );
}
