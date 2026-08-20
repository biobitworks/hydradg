import Link from "next/link";

const PRIMARY_NAV = [
  ["Overview", "/"],
  ["Judge", "/judge"],
  ["Why HydraDB", "/best-use"],
  ["Results", "/track03"],
  ["Graph", "/graph"],
] as const;

const DEEP_NAV = [
  ["Context vs Entropy", "/results/context-vs-entropy"],
  ["Knowledge", "/knowledge"],
  ["Evidence", "/evidence"],
  ["How to Use", "/how-to"],
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
        <Link className="siteNavCta" href="/best-use">Show the math</Link>
      </nav>
    </header>
  );
}
