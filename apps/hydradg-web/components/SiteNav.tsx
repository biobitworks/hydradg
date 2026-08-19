import Link from "next/link";

const NAV = [
  ["Overview", "/"],
  ["Judge Demo", "/judge"],
  ["Results", "/track03"],
  ["Graph", "/graph"],
  ["Knowledge", "/knowledge"],
  ["How to Use", "/how-to"],
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
          {NAV.map(([label, href]) => (
            <Link key={href} href={href}>{label}</Link>
          ))}
          <a href="/backup/hydradg.html">Static Fallback</a>
        </div>
        <Link className="siteNavCta" href="/judge">Start walkthrough</Link>
      </nav>
    </header>
  );
}
