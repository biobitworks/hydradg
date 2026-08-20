"use client";

import Link from "next/link";

export type BreadcrumbItem = {
  label: string;
  href?: string;
};

type Props = {
  items: readonly BreadcrumbItem[];
  summaryText?: string;
};

export default function Breadcrumbs({ items, summaryText }: Props) {
  return (
    <div
      style={{
        background: "rgba(255, 255, 255, 0.03)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        borderRadius: "8px",
        padding: "0.75rem 1rem",
        marginBottom: "1.5rem",
      }}
    >
      <nav aria-label="Breadcrumb navigation" style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <span key={`${item.label}-${index}`} style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}>
              {index > 0 && <span style={{ color: "rgba(255,255,255,0.3)" }}>/</span>}
              {item.href && !isLast ? (
                <Link
                  href={item.href}
                  className="small mono"
                  style={{
                    color: "#60a5fa",
                    textDecoration: "none",
                    fontWeight: 600,
                    padding: "2px 6px",
                    borderRadius: "4px",
                    background: "rgba(96, 165, 250, 0.1)",
                  }}
                >
                  {item.label}
                </Link>
              ) : (
                <span
                  className="small mono"
                  style={{
                    color: isLast ? "#10b981" : "#e8edf2",
                    fontWeight: isLast ? 700 : 500,
                    padding: "2px 6px",
                    borderRadius: "4px",
                    background: isLast ? "rgba(16, 185, 129, 0.15)" : "transparent",
                    border: isLast ? "1px solid rgba(16, 185, 129, 0.3)" : "none",
                  }}
                >
                  {item.label}
                </span>
              )}
            </span>
          );
        })}
      </nav>
      {summaryText && (
        <p className="small muted" style={{ margin: "0.5rem 0 0 0", color: "#9ca3af" }}>
          <strong>What to look for:</strong> {summaryText}
        </p>
      )}
    </div>
  );
}
