"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const PRIMARY_NAV = [
  ["Overview", "/"],
  ["Judge", "/judge"],
  ["Why HydraDB", "/best-use"],
  ["Results", "/track03"],
  ["Graph", "/graph"],
  ["HydraLamp", "/hydralamp"],
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
  ["04 HydraDB", "/judge#hydradb-status"],
  ["05 Results", "/track03"],
  ["06 Evidence", "/evidence"],
  ["07 Future", "/beam-1m"],
  ["08 Claim", "/eligibility"],
] as const;

function resolveStep(pathname: string, hash: string) {
  if (pathname === "/track03") return 4;
  if (pathname === "/evidence") return 5;
  if (pathname === "/beam-1m") return 6;
  if (pathname === "/eligibility") return 7;
  if (pathname === "/judge") {
    if (hash === "#golden-poison") return 1;
    if (hash === "#golden-antidote") return 2;
    if (hash === "#hydradb-status") return 3;
    return 0;
  }
  return -1;
}

export default function SiteNav() {
  const pathname = usePathname();
  const [hash, setHash] = useState("");

  useEffect(() => {
    const syncHash = () => setHash(window.location.hash);
    syncHash();
    window.addEventListener("hashchange", syncHash);
    return () => window.removeEventListener("hashchange", syncHash);
  }, [pathname]);

  const activeStep = resolveStep(pathname, hash);

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
        <Link className="siteNavCta" href="/judge#golden-reference">Start Golden Path</Link>
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
          gap: "7px",
          overflowX: "auto",
          border: "1px solid rgba(226,195,117,0.50)",
          borderRadius: "14px",
          background: "rgba(22,18,10,0.95)",
          backdropFilter: "blur(18px)",
          boxShadow: "0 12px 40px rgba(0,0,0,0.24)",
          scrollbarWidth: "none",
          whiteSpace: "nowrap",
        }}
      >
        <span
          style={{
            color: "#e2c375",
            font: "900 10px/1 ui-monospace, SFMono-Regular, Menlo, monospace",
            letterSpacing: "0.13em",
            textTransform: "uppercase",
            marginRight: "4px",
          }}
        >
          Golden path · 8 steps
        </span>
        {GOLDEN_BREADCRUMBS.map(([label, href], index) => {
          const current = index === activeStep;
          return (
            <span key={href} style={{ display: "inline-flex", alignItems: "center", gap: "7px" }}>
              {index > 0 ? <span style={{ color: "#7f7048" }}>›</span> : null}
              <Link
                href={href}
                aria-current={current ? "step" : undefined}
                style={{
                  color: current ? "#17130a" : index < 4 ? "#f2d995" : "#d6c9a3",
                  background: current ? "#e2c375" : "transparent",
                  border: current ? "1px solid #f2d995" : "1px solid transparent",
                  borderRadius: "999px",
                  textDecoration: "none",
                  font: "800 10.5px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace",
                  letterSpacing: "0.02em",
                  padding: current ? "5px 8px" : "5px 3px",
                }}
              >
                {current ? `CURRENT · ${label}` : label}
              </Link>
            </span>
          );
        })}
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
