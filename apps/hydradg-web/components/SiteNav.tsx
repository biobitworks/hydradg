import Link from "next/link";

const NAV = [
  ["Judge", "/judge"],
  ["4D FCG", "/graph"],
  ["Knowledge", "/knowledge"],
  ["Evidence", "/evidence"],
  ["Track 01", "/track01"],
  ["Track 02", "/track02"],
  ["Track 03", "/track03"],
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
        <div className="siteNavLinks">
          {NAV.map(([label, href]) => (
            <Link key={href} href={href}>{label}</Link>
          ))}
        </div>
        <Link className="siteNavCta" href="/judge">Run judge path</Link>
      </nav>
    </header>
  );
}
