import Link from "next/link";
import GoldenPathStep from "@/components/GoldenPathStep";
import SubmissionHeroAnnotated from "@/components/SubmissionHeroAnnotated";
import { buildSubmissionHeroFcoProjection, HERO_REGIONS, SUBMISSION_HERO } from "@/lib/submissionHeroFco";

export default function SubmissionPage() {
  const projection = buildSubmissionHeroFcoProjection();

  return (
    <main className="submissionPage">
      <GoldenPathStep
        step={1}
        summary="Start at the submission hero: a content-addressed FCO-bound media artifact with sponsor regions, judge-path arcs, and deployment pointers. Software metadata is Apache-2.0; the hero research image is CC BY-NC-ND 4.0 per LICENSING.md."
      />

      <header className="submissionHeroHeader">
        <div>
          <p className="eyebrow">Agent Native Builders · Immersive Commons · HydraLamp</p>
          <h1>Submission custody surface.</h1>
          <p className="lede">
            Judges can follow the golden path from this hero through hosted Vercel demo, local Studio authority, and hash-bound FCO receipts. Immersive Commons submission is <strong>SUBMITTED</strong> (platform ack 2026-08-27T22:39:24Z); publication metadata here may advance without re-submitting the sealed IC payload.
          </p>
        </div>
        <div className="heroStatus">
          <span className="pill pillGood">IC · SUBMITTED</span>
          <span className="pill pillGood">FCO · MATERIALIZED</span>
          <span className="pill pillMuted">SIGNATURE · NOT_SIGNED</span>
        </div>
      </header>

      <SubmissionHeroAnnotated />

      <section className="computeSection">
        <span className="sectionNumber">01 / DEPLOYMENT POINTERS</span>
        <h2 className="displayTitle">Vercel production · local Studio · repos.</h2>
        <div className="grid twoCol">
          <article className="panel">
            <p className="eyebrow">Hosted judge surface</p>
            <h3>HydraLamp on Vercel</h3>
            <div className="actions" style={{ marginTop: "12px" }}>
              <a className="primary" href={SUBMISSION_HERO.pointers.hydralamp.demo} target="_blank" rel="noreferrer">Open production demo ↗</a>
              <a className="secondary" href="https://hydralamp.vercel.app/golden" target="_blank" rel="noreferrer">Legacy golden path ↗</a>
              <a className="secondary" href="https://hydralamp.vercel.app/demo/index.html" target="_blank" rel="noreferrer">Static fallback ↗</a>
            </div>
            <p className="small muted note">Anonymous HTTP 200 verified. Production alias may lag closeout SHA — check deployment receipt before judging parity claims.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Local scientific authority</p>
            <h3>magicSTUDIObox.local</h3>
            <div className="actions" style={{ marginTop: "12px" }}>
              <Link className="secondary" href="/hydralamp">Embedded HydraLamp microscope</Link>
              <Link className="secondary" href="/judge#golden-reference">Start golden path</Link>
              <a className="secondary" href={SUBMISSION_HERO.pointers.hydradg.url} target="_blank" rel="noreferrer">HydraDG repo ↗</a>
              <a className="secondary" href={SUBMISSION_HERO.pointers.hydralamp.url} target="_blank" rel="noreferrer">HydraLamp repo ↗</a>
            </div>
            <p className="small mono compact">hydradg@{SUBMISSION_HERO.pointers.hydradg.sha.slice(0, 12)} · hydralamp@{SUBMISSION_HERO.pointers.hydralamp.sha.slice(0, 12)}</p>
          </article>
        </div>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">02 / FCO + KNOWLEDGE GRAPH</span>
        <h2 className="displayTitle">Hero media is a governed receipt, not a decorative banner.</h2>
        <div className="metrics">
          <article className="metric"><span className="metricLabel">Website projection FCO</span><strong className="mono small">{projection.hero.id.slice(0, 22)}…</strong></article>
          <article className="metric"><span className="metricLabel">Raw media FCO</span><strong className="mono small">{SUBMISSION_HERO.rawMediaFcoId.slice(0, 22)}…</strong></article>
          <article className="metric"><span className="metricLabel">Relation</span><strong>DERIVED_FROM</strong></article>
          <article className="metric"><span className="metricLabel">Image SHA-256</span><strong className="mono small">{SUBMISSION_HERO.sha256.slice(0, 16)}…</strong></article>
          <article className="metric"><span className="metricLabel">Sponsor regions</span><strong>{HERO_REGIONS.filter((r) => r.kind === "sponsor").length}</strong></article>
          <article className="metric"><span className="metricLabel">Track regions</span><strong>{HERO_REGIONS.filter((r) => r.kind === "track").length}</strong></article>
        </div>
        <div className="actions">
          <Link className="primary" href={`/fco/${encodeURIComponent(projection.hero.id)}`}>Inspect website projection FCO ↗</Link>
          <Link className="secondary" href={`/fco/${encodeURIComponent(SUBMISSION_HERO.rawMediaFcoId)}`}>Inspect raw media FCO ↗</Link>
          <Link className="secondary" href="/graph">Open 4D FCG explorer</Link>
          <Link className="secondary" href="/knowledge#hydralamp-submission-hero">Knowledge term ↗</Link>
        </div>
        <p className="small muted note">Website projection adds deterministic application metadata to the knowledge graph. Canonical FCG append remains NOT_APPENDED unless an authorized signing path exists.</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">03 / LICENSE PREFERENCE</span>
        <h2 className="displayTitle">Rights metadata is explicit and non-interchangeable with hashes.</h2>
        <div className="grid threeCol">
          <article className="panel">
            <p className="eyebrow">Software</p>
            <h3>Apache-2.0</h3>
            <p className="muted">HydraDG website code, TypeScript utilities, scripts, and application FCO metadata wrappers.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Research content</p>
            <h3>CC BY-NC-ND 4.0</h3>
            <p className="muted">FCO/FCG research publications, designated Byron P. Lee / Biobitworks research content, and this submission hero image.</p>
          </article>
          <article className="panel">
            <p className="eyebrow">Superseded metadata</p>
            <h3>CC BY 4.0 → error</h3>
            <p className="muted">Earlier CC BY 4.0 FCO metadata is preserved as SUPERSEDED_METADATA_ERROR only. It does not relicense bytes.</p>
          </article>
        </div>
        <p className="small muted note">See <Link href="/knowledge#licensing-split">Licensing split</Link> and repository <code>LICENSING.md</code>. Third-party upstream rights remain separate (HydraDB, datasets, sponsor APIs).</p>
      </section>

      <section className="computeSection">
        <span className="sectionNumber">04 / IMMERSIVE COMMONS INTEGRATION</span>
        <h2 className="displayTitle">Integration repo synced · IC submission recorded.</h2>
        <p className="sectionLead">
          <code>biobitworks/immersivecommons-integration@282992be5d61ed4e371ad355471c32755b346939</code> records canonical pointers, studio remote-work receipt, and SHA256SUMS transfer. Platform write receipt: <code>eval/immersive_commons_submission_20260827/IC_SUBMIT_RECEIPT.json</code> (EXTERNALLY_RETRIEVED_EVIDENCE; not cryptographically signed).
        </p>
        <div className="actions">
          <Link className="primary" href="/judge#golden-reference">Continue golden path →</Link>
          <Link className="secondary" href="/providers">Sponsor integration status</Link>
          <Link className="secondary" href="/eligibility">Claim boundary</Link>
        </div>
      </section>
    </main>
  );
}
