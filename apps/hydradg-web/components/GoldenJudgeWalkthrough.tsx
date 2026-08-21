import Link from "next/link";

const STEPS = [
  {
    number: "01",
    label: "REFERENCE",
    title: "Reference",
    relation: "CURRENT",
    body: "Start from the declared current fact and open its source, session, and custody path.",
  },
  {
    number: "02",
    label: "POISON",
    title: "Poison",
    relation: "CONTRADICTS / SUPERSEDED_BY",
    body: "Introduce a controlled conflicting state. HydraDG retains the predecessor and marks the first divergent relationship.",
  },
  {
    number: "03",
    label: "ANTIDOTE",
    title: "Antidote",
    relation: "RESTORES / CURRENT",
    body: "Restore the valid current state without deleting the poison, contradiction, provenance, or recovery history.",
  },
] as const;

export default function GoldenJudgeWalkthrough({ showCta = true }: { showCta?: boolean }) {
  return (
    <section
      id="golden-path"
      aria-label="Golden judge walkthrough"
      style={{
        margin: "22px 0 72px",
        padding: "clamp(22px, 4vw, 42px)",
        border: "1px solid rgba(226,195,117,0.72)",
        borderRadius: "8px",
        background:
          "linear-gradient(135deg, rgba(226,195,117,0.10), rgba(226,195,117,0.025) 45%, rgba(8,9,11,0.96) 78%)",
        boxShadow: "0 0 0 1px rgba(226,195,117,0.06) inset, 0 24px 80px rgba(0,0,0,0.26)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: "20px", alignItems: "flex-end", flexWrap: "wrap" }}>
        <div>
          <p
            style={{
              margin: 0,
              color: "#e2c375",
              font: "800 11px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace",
              letterSpacing: "0.18em",
              textTransform: "uppercase",
            }}
          >
            Judge Walkthrough · Golden Path
          </p>
          <h2
            style={{
              margin: "8px 0 8px",
              color: "#f2d995",
              fontFamily: "Georgia, 'Times New Roman', serif",
              fontWeight: 400,
              fontSize: "clamp(38px, 5vw, 72px)",
              lineHeight: 0.98,
              letterSpacing: "-0.045em",
            }}
          >
            Reference → Poison → Antidote
          </h2>
          <p style={{ margin: 0, maxWidth: "850px", color: "#d6c9a3", fontSize: "16px", lineHeight: 1.65 }}>
            This is the path to follow in the demo and the video. Change one governed fact, find the first divergence, then restore the valid state while the full contradictory history remains traversable.
          </p>
        </div>
        {showCta ? (
          <Link
            href="/judge#golden-path"
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "11px 16px",
              borderRadius: "999px",
              border: "1px solid #e2c375",
              color: "#17130a",
              background: "#e2c375",
              textDecoration: "none",
              fontWeight: 800,
              whiteSpace: "nowrap",
            }}
          >
            Start guided walkthrough →
          </Link>
        ) : null}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "12px", marginTop: "24px" }}>
        {STEPS.map((step) => (
          <article
            key={step.number}
            style={{
              minHeight: "220px",
              padding: "22px",
              border: "1px solid rgba(226,195,117,0.60)",
              borderRadius: "7px",
              background: "rgba(32,27,16,0.72)",
              boxShadow: "0 0 28px rgba(226,195,117,0.055) inset",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "baseline" }}>
              <span
                style={{
                  color: "#f2d995",
                  fontFamily: "Georgia, 'Times New Roman', serif",
                  fontSize: "38px",
                  lineHeight: 1,
                }}
              >
                {step.number}
              </span>
              <span
                style={{
                  color: "#e2c375",
                  font: "800 10px/1.3 ui-monospace, SFMono-Regular, Menlo, monospace",
                  letterSpacing: "0.12em",
                }}
              >
                {step.label}
              </span>
            </div>
            <h3
              style={{
                margin: "24px 0 6px",
                color: "#fff1c7",
                fontFamily: "Georgia, 'Times New Roman', serif",
                fontWeight: 400,
                fontSize: "34px",
              }}
            >
              {step.title}
            </h3>
            <p style={{ margin: "0 0 12px", color: "#e2c375", font: "700 10px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace" }}>
              {step.relation}
            </p>
            <p style={{ margin: 0, color: "#cfc7b2", lineHeight: 1.6 }}>{step.body}</p>
          </article>
        ))}
      </div>

      <p
        style={{
          margin: "18px 0 0",
          paddingTop: "14px",
          borderTop: "1px solid rgba(226,195,117,0.28)",
          color: "#bcae86",
          fontSize: "12px",
          lineHeight: 1.55,
        }}
      >
        Recording order: Reference → Poison → Antidote → running real-model matrix → evidence/custody → claim boundary. The walkthrough demonstrates governed state transitions; it does not fabricate hosted parity or experimental scores.
      </p>
    </section>
  );
}
