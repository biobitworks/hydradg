import Link from "next/link";

import { RELEASE_STATUS } from "@/lib/releaseStatus";

const evidence = [
  {
    label: "Live HydraDB structural conformance",
    status: "PASS",
    detail: "Pinned HydraDB executed the v2 typed-memory structural suite. Seven declared invariants passed across exact case membership, identity, supersession and contradiction construction/traversal.",
    ceiling: "SYNTHETIC_STRUCTURAL_CONFORMANCE_ONLY",
    href: "/track03",
  },
  {
    label: "LongMemEval full500 typed-memory ablation",
    status: "EXECUTED · NEGATIVE/NEUTRAL",
    detail: "500 cases were materialized into live pinned HydraDB; 470 cases had retrieval ground truth. B, C and D returned NO_POSITIVE_HIT_RATE_SIGNAL relative to A at the tested route.",
    ceiling: "LONGMEMEVAL_FULL500_RETRIEVAL_ABLATION_ONLY_NOT_END_TO_END_QA",
    href: "/track03",
  },
  {
    label: "Core Track 01/03 dataset acquisition",
    status: "DOWNLOADED · HASHED",
    detail: "EnterpriseRAG-Bench, HERB, LongMemEval cleaned, LongMemEval-V2 core and BEAM have local acquisition identities/manifests recorded. Download identity does not establish benchmark performance or full atomization.",
    ceiling: "LOCAL_DATASET_BYTE_IDENTITIES_AFTER_DOWNLOAD_ONLY",
    href: "/track01",
  },
  {
    label: "Total dataset atomization + FCO/FCG projection",
    status: "IMPLEMENTED · CORPUS EXECUTION PENDING",
    detail: "The release branch contains record-level atomization, SeedGraph bundle admission and full FCO/FCG-to-HydraDB projection tooling. Do not call the downloaded corpora FULL_STRUCTURAL_ATOMIZATION until the completeness/projection receipts execute.",
    ceiling: "IMPLEMENTATION_STATE_ONLY_NOT_FULL_CORPUS_ATOMIZATION",
    href: "/track01",
  },
  {
    label: "Track 03 live poison → antidote release path",
    status: "IMPLEMENTED · FRESH EXECUTION RECEIPT PENDING",
    detail: "The release server resolves original and injected live Facts so the judge sequence can preserve SUPERSEDED_BY history through poison and antidote. A fresh release receipt remains required before PASS.",
    ceiling: "LIVE_HYDRADB_FCG_GOLDEN_PATH_STATE_TRANSITION_ONLY_NOT_RETRIEVAL_SUPERIORITY",
    href: "/judge",
  },
  {
    label: "Track 02 HydraBlast",
    status: RELEASE_STATUS.tracks.track02.synthetic_canary,
    detail: "Fresh Hack Hydra code compares deterministic Python reverse dependency closure with HydraDB across reference, poison, partial-repair and full-repair states. Public PASS remains receipt-gated.",
    ceiling: "SYNTHETIC_TRACK02_STRUCTURAL_CANARY_ONLY_NOT_REAL_NPM_EXPOSURE",
    href: "/track02",
  },
  {
    label: "Track 01 HydraOntology",
    status: RELEASE_STATUS.tracks.track01.synthetic_canary,
    detail: "Track 01 source datasets are downloaded and hash-identified. The synthetic identity canary exists, while public PASS and real EnterpriseRAG/HERB claims remain receipt/evaluation gated.",
    ceiling: "SYNTHETIC_TRACK01_STRUCTURAL_CANARY_ONLY_NOT_ENTERPRISERAG_OR_HERB_PERFORMANCE",
    href: "/track01",
  },
  {
    label: "Release hosting",
    status: "BACKUP IMPLEMENTED · RELEASE VERCEL PENDING",
    detail: "The connected Vercel project has a READY production deployment from an older branch. The current release branch is not yet the live production surface. A standalone static fallback artifact now preserves the judge story without requiring Vercel or a live backend.",
    ceiling: "ARTIFACT_DELIVERY_STATE_ONLY",
    href: "/demo",
  },
];

const hashes = [
  ["LongMemEval source", "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"],
  ["full500 result", "bdecb4b62cf90040c7f346d283efe78459825b427557cec8d4998f3499ee0324"],
  ["full500 statistics", "8dcf57f5ac60418d16d3c945ad678b4d17b557b9425fededbd6684add7cff7cc"],
  ["full500 receipt", "21a29046de961e252372d06fd85d98db767b900982f90421cc720dfb85069365"],
] as const;

export default function EvidencePage() {
  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Hack Hydra 2026 · evidence ledger</p>
          <h1>Results without claim inflation.</h1>
          <p className="lede">Positive, negative, failed, blocked and pending executions remain separate custody objects. Follow any result downward from the public statement to its source identity, transformation, receipt and claim ceiling.</p>
        </div>
        <div className="heroStatus"><span className="pill pillGood">FULL500 RECEIPT RETAINED</span><span className="pill pillMuted">NOT SIGNED</span><span className="pill pillMuted">NOT LIVE-MERKLE-COMMITTED</span></div>
      </header>

      <section className="metrics" aria-label="Submission evidence status">
        <article className="metric"><span className="metricLabel">Structural gate</span><strong>7/7</strong><span className="small muted">declared live HydraDB invariants</span></article>
        <article className="metric"><span className="metricLabel">Primary real dataset</span><strong>500 cases</strong><span className="small muted">LongMemEval-S full500</span></article>
        <article className="metric"><span className="metricLabel">Core datasets</span><strong>5 acquired</strong><span className="small muted">hash-identified local bytes</span></article>
        <article className="metric"><span className="metricLabel">Decision</span><strong>No positive signal</strong><span className="small muted">B/C/D hit-rate comparison</span></article>
      </section>

      <section className="computeSection"><span className="sectionNumber">01 / EVIDENCE OBJECTS</span><h2 className="displayTitle">Every state stays visible.</h2><div className="grid twoCol">{evidence.map((item) => <article className="panel" key={item.label}><p className="eyebrow">{item.status}</p><h2>{item.label}</h2><p className="muted">{item.detail}</p><p className="mono small compact">claim_ceiling={item.ceiling}</p><div className="actions"><Link className="secondary" href={item.href}>Follow evidence path</Link></div></article>)}</div></section>

      <section className="computeSection"><span className="sectionNumber">02 / FULL500 IDENTITIES</span><h2 className="displayTitle">Hashes link retained result objects.</h2><div className="stack">{hashes.map(([label, hash]) => <div className="panel" key={label}><p className="eyebrow">{label}</p><p className="mono compact">{hash}</p></div>)}</div><p className="small muted note">A SHA-256 value establishes byte/object identity for the retained artifact. It does not establish correctness or independent verification.</p></section>

      <section className="computeSection"><span className="sectionNumber">03 / PROJECT FCG</span><h2 className="displayTitle">Source → transformation → evidence → claim → artifact.</h2><div className="flow mono"><span>source bytes</span><b>→</b><span>SeedGraph / transform</span><b>→</b><span>FCO/FCG</span><b>→</b><span>HydraDB / evaluation</span><b>→</b><span>website artifact</span></div><div className="actions"><a className="secondary" href="/api/site-fcg">Open site FCG JSON</a><a className="secondary" href="/backup/hydradg.html">Open offline artifact</a></div></section>
    </main>
  );
}
