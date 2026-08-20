import Link from "next/link";

const PRIMARY_NAV = [
  ["Judge", "/judge"],
  ["Results", "/track03"],
  ["Graph", "/graph"],
  ["Models", "/models"],
  ["Custody", "/custody"],
] as const;

const DEEP_NAV = [
  ["Why HydraDB", "/best-use"],
  ["Track 01 · Ontology", "/track01"],
  ["Track 02 · Code Graphs", "/track02"],
  ["Track 03 · Memory", "/track03"],
  ["Context vs Entropy", "/results/context-vs-entropy"],
  ["Knowledge", "/knowledge"],
  ["Evidence", "/evidence"],
  ["How to Use", "/how-to"],
  ["Evolution", "/evolution"],
  ["Eligibility", "/eligibility"],
] as const;

export default function SiteNav() {
  return (
    <>
      <a className="skipLink" href="#main-content">Skip to main content</a>
      <header className="siteNavShell">
        <nav className="siteNav" aria-label="HydraDG primary navigation">
          <Link className="siteBrand" href="/" aria-label="HydraDG home MVP">
            <span className="siteBrandName">HydraDG</span>
            <span className="siteBrandMark">FCO / FCG</span>
          </Link>

          <div className="siteNavLinks siteNavPrimary" aria-label="Judge navigation">
            {PRIMARY_NAV.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
          </div>

          <details className="siteNavMore siteNavMenu">
            <summary aria-label="Open all HydraDG pages">All pages</summary>
            <div className="siteNavMoreMenu">
              <Link href="/">Home MVP</Link>
              {PRIMARY_NAV.map(([label, href]) => <Link key={`p-${href}`} href={href}>{label}</Link>)}
              {DEEP_NAV.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
              <a href="/backup/hydradg.html">Static fallback</a>
            </div>
          </details>

          <Link className="siteNavCta goldenCta" href="/judge">Start golden path</Link>
        </nav>
      </header>
    </>
  );
}
