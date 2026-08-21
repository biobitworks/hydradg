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

const GOLDEN_BREADCRUMBS = [
  ["01 Reference", "/judge#golden-reference"],
  ["02 Poison", "/judge#golden-poison"],
  ["03 Antidote", "/judge#golden-antidote"],
  ["04 Matrix", "/real-local-matrix"],
  ["05 Evidence", "/evidence"],
  ["06 Claim", "/eligibility"],
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

      <nav
        aria-label="Golden path breadcrumbs"
        style={{
          pointerEvents: "auto",
          width: "min(1240px, 100%)",
          margin: "7px auto 0",
          padding: "8px 12px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          overflowX: "auto",
          border: "1px solid rgba(226,195,117,0.50)",
          borderRadius: "14px",
          background: "rgba(22,18,10,0.93)",
          backdropFilter: "blur(18px)",
          boxShadow: "0 12px 40px rgba(0,0,0,0.24)",
          scrollbarWidth: "none",
          whiteSpace: "nowrap",
        }}
      >
        <span
          style={{
            color: "#e2c375",
            font: "800 10px/1 ui-monospace, SFMono-Regular, Menlo, monospace",
            letterSpacing: "0.13em",
            textTransform: "uppercase",
            marginRight: "3px",
          }}
        >
          Golden path
        </span>
        {GOLDEN_BREADCRUMBS.map(([label, href], index) => (
          <span key={href} style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}>
            {index > 0 ? <span style={{ color: "#7f7048" }}>›</span> : null}
            <Link
              href={href}
              style={{
                color: index < 3 ? "#f2d995" : "#d6c9a3",
                textDecoration: "none",
                font: "700 11px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace",
                letterSpacing: "0.03em",
              }}
            >
              {label}
            </Link>
          </span>
        ))}
      </nav>

      <style>{`
        body main { padding-top: 154px; }
        @media (max-width: 820px) {
          body main { padding-top: 132px; }
        }
      `}</style>
    </header>
  );
}
