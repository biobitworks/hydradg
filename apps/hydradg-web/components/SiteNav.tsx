import Link from "next/link";

const PRIMARY_NAV = [
  ["Overview", "/"],
  ["Demo", "/demo"],
  ["Results", "/evidence"],
  ["Experiments", "/#tracks"],
] as const;

const SECONDARY_NAV = [
  ["Graph Explorer", "/graph"],
  ["Knowledge", "/knowledge"],
  ["Eligibility", "/eligibility"],
] as const;

export default function SiteNav() {
  return (
    <header className="siteNavShell">
      <nav className="siteNav" aria-label="HydraDG primary navigation">
        <Link className="siteBrand" href="/" aria-label="HydraDG home">
          <span className="siteBrandName">HydraDG</span>
          <span className="siteBrandMark">FCG</span>
        </Link>
        <div className="siteNavLinks" aria-label="Primary navigation">
          {PRIMARY_NAV.map(([label, href]) => (
            <Link key={href} href={href}>{label}</Link>
          ))}
          <details className="siteNavMore">
            <summary>Deep dive</summary>
            <div className="siteNavMoreMenu">
              {SECONDARY_NAV.map(([label, href]) => (
                <Link key={href} href={href}>{label}</Link>
              ))}
            </div>
          </details>
        </div>
        <Link className="siteNavCta" href="/judge">Try the demo</Link>
      </nav>
    </header>
  );
}
