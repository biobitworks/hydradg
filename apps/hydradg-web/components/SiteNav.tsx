import Link from "next/link";

const PRIMARY_NAV = [
  ["Overview", "/"],
  ["Judge", "/judge"],
  ["Context vs Entropy", "/results/context-vs-entropy"],
  ["Results", "/track03"],
  ["Graph", "/graph"],
  ["Why Graph?", "/track-fit"],
] as const;

const DEEP_NAV = [
  ["Knowledge", "/knowledge"],
  ["Evidence", "/evidence"],
  ["How to Use", "/how-to"],
  ["Track 01", "/track01"],
  ["Track 02", "/track02"],
  ["Track 03", "/track03"],
  ["Evolution", "/evolution"],
  ["Eligibility", "/eligibility"],
] as const;

export default function SiteNav() {
  return (
    <header className="siteNavShell">
      <nav className="siteNav" aria-label="HydraDG judge navigation">
        <Link className="siteBrand" href="/" aria-label="HydraDG home">
          <span className="siteBrandName">HydraDG</span>
          <span className="siteBrandMark">FCG</span>
        </Link>
        <div className="siteNavLinks" aria-label="Judge navigation">
          {PRIMARY_NAV.map(([label, href]) => (
            <Link key={href} href={href}>{label}</Link>
          ))}
          <details className="siteNavMore">
            <summary>Deep dive</summary>
            <div className="siteNavMoreMenu">
              {DEEP_NAV.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
              <a href="/backup/hydradg.html">Static fallback</a>
            </div>
          </details>
        </div>
        <Link className="siteNavCta" href="/track-fit">Final judge step</Link>
      </nav>
    </header>
  );
}
