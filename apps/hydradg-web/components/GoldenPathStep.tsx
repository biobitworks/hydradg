"use client";

import Link from "next/link";

export const GOLDEN_PATH_STEPS = [
  { number: "01", short: "Reference", title: "Reference", href: "/judge#golden-reference" },
  { number: "02", short: "Poison", title: "Poison", href: "/judge#golden-poison" },
  { number: "03", short: "Antidote", title: "Antidote", href: "/judge#golden-antidote" },
  { number: "04", short: "HydraDB", title: "Hosted HydraDB", href: "/judge#hydradb-status" },
  { number: "05", short: "Results", title: "Historical Results", href: "/track03" },
  { number: "06", short: "Evidence", title: "Evidence + FCG", href: "/evidence" },
  { number: "07", short: "Future", title: "BEAM + Future Work", href: "/beam-1m" },
  { number: "08", short: "Claim", title: "Claim Boundary", href: "/eligibility" },
] as const;

export default function GoldenPathStep({
  step,
  summary,
  compact = false,
}: {
  step: number;
  summary: string;
  compact?: boolean;
}) {
  const index = Math.max(0, Math.min(GOLDEN_PATH_STEPS.length - 1, step - 1));
  const current = GOLDEN_PATH_STEPS[index];
  const previous = index > 0 ? GOLDEN_PATH_STEPS[index - 1] : null;
  const next = index < GOLDEN_PATH_STEPS.length - 1 ? GOLDEN_PATH_STEPS[index + 1] : null;

  return (
    <section
      aria-label={`Golden Path step ${current.number} of 08: ${current.title}`}
      style={{
        margin: compact ? "0 0 18px" : "0 0 28px",
        padding: compact ? "14px 16px" : "18px 20px",
        border: "1px solid rgba(226,195,117,0.62)",
        borderRadius: "12px",
        background: "linear-gradient(135deg, rgba(226,195,117,0.11), rgba(15,13,9,0.94) 72%)",
        boxShadow: "0 14px 44px rgba(0,0,0,0.18)",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "16px", flexWrap: "wrap" }}>
        <div style={{ minWidth: 0, flex: "1 1 520px" }}>
          <p style={{ margin: 0, color: "#e2c375", font: "800 10px/1.3 ui-monospace, SFMono-Regular, Menlo, monospace", letterSpacing: "0.14em", textTransform: "uppercase" }}>
            Golden Path · Step {current.number} of 08
          </p>
          <h2 style={{ margin: "5px 0 5px", color: "#f2d995", fontFamily: "Georgia, 'Times New Roman', serif", fontWeight: 400, fontSize: compact ? "25px" : "30px", lineHeight: 1.08 }}>
            {current.title}
          </h2>
          <p style={{ margin: 0, color: "#cfc7b2", lineHeight: 1.55, maxWidth: "780px", fontSize: compact ? "13px" : "14px" }}>
            {summary}
          </p>
        </div>

        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
          {previous ? (
            <Link href={previous.href} style={{ padding: "9px 12px", border: "1px solid rgba(226,195,117,0.50)", borderRadius: "999px", color: "#d6c9a3", textDecoration: "none", fontWeight: 800, fontSize: "12px", whiteSpace: "nowrap" }}>
              ← {previous.number} {previous.short}
            </Link>
          ) : null}
          {next ? (
            <Link href={next.href} style={{ padding: "9px 13px", border: "1px solid #e2c375", borderRadius: "999px", background: "#e2c375", color: "#17130a", textDecoration: "none", fontWeight: 900, fontSize: "12px", whiteSpace: "nowrap" }}>
              Next · {next.number} {next.short} →
            </Link>
          ) : (
            <Link href="/" style={{ padding: "9px 13px", border: "1px solid #e2c375", borderRadius: "999px", background: "#e2c375", color: "#17130a", textDecoration: "none", fontWeight: 900, fontSize: "12px", whiteSpace: "nowrap" }}>
              Finish · Overview →
            </Link>
          )}
        </div>
      </div>

      <div style={{ display: "flex", gap: "6px", overflowX: "auto", marginTop: "14px", paddingBottom: "2px", scrollbarWidth: "none" }}>
        {GOLDEN_PATH_STEPS.map((item, itemIndex) => {
          const isCurrent = itemIndex === index;
          const isPast = itemIndex < index;
          return (
            <Link
              key={item.number}
              href={item.href}
              aria-current={isCurrent ? "step" : undefined}
              title={`${item.number} · ${item.title}`}
              style={{
                flex: "0 0 auto",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 9px",
                borderRadius: "999px",
                border: isCurrent ? "1px solid #f2d995" : "1px solid rgba(226,195,117,0.24)",
                background: isCurrent ? "rgba(226,195,117,0.20)" : isPast ? "rgba(226,195,117,0.08)" : "rgba(255,255,255,0.025)",
                color: isCurrent ? "#fff1c7" : isPast ? "#d6c9a3" : "#8f866f",
                textDecoration: "none",
                font: "800 10px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace",
                letterSpacing: "0.02em",
              }}
            >
              <span>{item.number}</span>
              <span>{item.short}</span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
